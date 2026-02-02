import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

import mlflow
import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from mlflow.tracking import MlflowClient
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from src.config import MLFLOW_URI, PARAMS, PROJECT_ROOT

MODEL_NAME = "RainTomorrow_XGBoost"
DEFAULT_PUSHGATEWAY = "http://pushgateway:9091"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def find_split_dir(split_id: int) -> Path:
    splits_root = PROJECT_ROOT / "data" / "training_data_splits_by_year"
    matches = sorted(splits_root.glob(f"split_{split_id:02d}_*"))
    if not matches:
        raise FileNotFoundError(f"Split {split_id} not found in {splits_root}")
    return matches[0]


def load_split_features(split_id: int) -> pd.DataFrame:
    split_dir = find_split_dir(split_id)
    feature_path = split_dir / "X_train.csv"
    if not feature_path.exists():
        raise FileNotFoundError(f"Missing features at {feature_path}")
    return pd.read_csv(feature_path)


def get_production_split_id() -> int | None:
    mlflow.set_tracking_uri(MLFLOW_URI)
    client = MlflowClient()

    try:
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    except Exception as exc:
        logging.warning("Failed to query MLflow model registry: %s", exc)
        return None

    prod_versions = [v for v in versions if v.current_stage == "Production"]
    if not prod_versions:
        logging.warning("No production model found for %s", MODEL_NAME)
        return None

    latest_prod = max(prod_versions, key=lambda v: int(v.version))
    split_tag = latest_prod.tags.get("split_id") if latest_prod.tags else None
    if not split_tag:
        logging.warning("Production model missing split_id tag")
        return None

    try:
        return int(split_tag)
    except ValueError:
        logging.warning("Invalid split_id tag value: %s", split_tag)
        return None


def align_columns(
    reference: pd.DataFrame, current: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    common_cols = reference.columns.intersection(current.columns)
    missing_in_current = reference.columns.difference(current.columns)
    missing_in_reference = current.columns.difference(reference.columns)

    if len(missing_in_current) > 0:
        logging.warning("Missing %d reference columns in current data", len(missing_in_current))
    if len(missing_in_reference) > 0:
        logging.warning("Missing %d current columns in reference data", len(missing_in_reference))

    return reference[common_cols].copy(), current[common_cols].copy()


def build_report(reference: pd.DataFrame, current: pd.DataFrame) -> Report:
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)
    return report


def report_payload(report: Report) -> tuple[dict, str]:
    if hasattr(report, "json"):
        payload = report.json()
        if isinstance(payload, str):
            return json.loads(payload), payload
        return payload, json.dumps(payload, indent=2, default=str)
    if hasattr(report, "as_dict"):
        payload = report.as_dict()
        return payload, json.dumps(payload, indent=2, default=str)
    raise RuntimeError("Unsupported Evidently report serialization")


def extract_drift_metrics(report_payload: dict) -> dict:
    metrics = report_payload.get("metrics", [])
    for metric in metrics:
        result = metric.get("result")
        if not isinstance(result, dict):
            continue
        if "share_drifted_features" in result or "dataset_drift" in result:
            return {
                "dataset_drift": int(bool(result.get("dataset_drift"))),
                "share_drifted_features": float(result.get("share_drifted_features", 0.0)),
                "drifted_features": int(result.get("number_of_drifted_columns", 0)),
                "total_features": int(result.get("number_of_columns", 0)),
            }
    return {
        "dataset_drift": 0,
        "share_drifted_features": 0.0,
        "drifted_features": 0,
        "total_features": 0,
    }


def push_metrics(
    metrics: dict,
    model_name: str,
    reference_split: int,
    current_split: int,
    pushgateway_url: str,
) -> None:
    registry = CollectorRegistry()
    labels = [model_name, str(reference_split), str(current_split)]

    Gauge(
        "data_drift_dataset_detected",
        "1 if dataset drift detected",
        ["model_name", "reference_split", "current_split"],
        registry=registry,
    ).labels(*labels).set(metrics["dataset_drift"])

    Gauge(
        "data_drift_share",
        "Share of drifted features",
        ["model_name", "reference_split", "current_split"],
        registry=registry,
    ).labels(*labels).set(metrics["share_drifted_features"])

    Gauge(
        "data_drift_feature_count",
        "Number of drifted features",
        ["model_name", "reference_split", "current_split"],
        registry=registry,
    ).labels(*labels).set(metrics["drifted_features"])

    Gauge(
        "data_drift_total_feature_count",
        "Number of evaluated features",
        ["model_name", "reference_split", "current_split"],
        registry=registry,
    ).labels(*labels).set(metrics["total_features"])

    push_to_gateway(pushgateway_url, job="data_drift", registry=registry)


def main() -> None:
    configure_logging()

    parser = argparse.ArgumentParser(description="Run Evidently drift monitoring.")
    parser.add_argument("--reference-split-id", type=int, default=None)
    parser.add_argument("--current-split-id", type=int, default=None)
    parser.add_argument("--output-dir", type=str, default="reports/evidently")
    parser.add_argument("--pushgateway-url", type=str, default=None)
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()

    current_split = args.current_split_id or PARAMS["data"].get("split_id", 1)
    reference_split = args.reference_split_id or get_production_split_id() or current_split

    if reference_split == current_split:
        logging.warning("Reference split equals current split (%s)", current_split)

    logging.info("Reference split: %s", reference_split)
    logging.info("Current split: %s", current_split)

    reference_df = load_split_features(reference_split)
    current_df = load_split_features(current_split)
    reference_df, current_df = align_columns(reference_df, current_df)

    report = build_report(reference_df, current_df)

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base_name = f"drift_split_{reference_split:02d}_to_{current_split:02d}_{timestamp}"
    html_path = output_dir / f"{base_name}.html"
    json_path = output_dir / f"{base_name}.json"

    report.save_html(str(html_path))
    payload, payload_json = report_payload(report)
    json_path.write_text(payload_json, encoding="utf-8")

    drift_metrics = extract_drift_metrics(payload)
    logging.info("Dataset drift detected: %s", drift_metrics["dataset_drift"])
    logging.info("Drifted feature share: %.4f", drift_metrics["share_drifted_features"])

    if not args.no_push:
        pushgateway_url = args.pushgateway_url or DEFAULT_PUSHGATEWAY
        if pushgateway_url:
            try:
                push_metrics(
                    drift_metrics,
                    MODEL_NAME,
                    reference_split,
                    current_split,
                    pushgateway_url,
                )
                logging.info("Pushed drift metrics to %s", pushgateway_url)
            except Exception as exc:
                logging.warning("Failed to push drift metrics: %s", exc)


if __name__ == "__main__":
    main()
