import json

import joblib
import mlflow
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from weather_au_mlops.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, Paths


def main() -> None:
    paths = Paths()
    paths.artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Minimal synthetic run to validate tracking, packaging, and artifacts.
    rng = np.random.default_rng(42)
    X = rng.normal(size=(2000, 20))
    y = (X[:, 0] + 0.5 * X[:, 1] + rng.normal(scale=0.5, size=2000) > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=500, class_weight="balanced", n_jobs=1)
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, proba))

    model_path = paths.artifacts_dir / "model.joblib"
    metrics_path = paths.artifacts_dir / "metrics.json"
    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps({"roc_auc": auc}, indent=2))

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run(run_name="smoke-train"):
        mlflow.log_param("model", "LogisticRegression")
        mlflow.log_metric("roc_auc", auc)
        mlflow.log_artifact(str(model_path), artifact_path="model")
        mlflow.log_artifact(str(metrics_path), artifact_path="metrics")

    print(f"OK: roc_auc={auc:.4f} logged to MLflow at {MLFLOW_TRACKING_URI}")


if __name__ == "__main__":
    main()
