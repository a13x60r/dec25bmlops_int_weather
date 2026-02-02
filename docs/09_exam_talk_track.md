# Exam Talk Track

## 7-10 minute oral script outline
1. Project purpose and target: RainTomorrow binary classification using Australian weather data, with full MLOps lifecycle.
2. Data versioning: DVC tracks raw/processed data and pipeline stages (`dvc.yaml`, `dvc.lock`).
3. Training flow: preprocess -> year-based splits -> XGBoost training with SMOTE and MLflow tracking/registry.
4. Orchestration: Airflow DAGs fetch daily data, validate, run DVC stages, and retrain.
5. Serving: BentoML service with JWT auth; FastAPI utility endpoints for training/testing.
6. Infra: Docker Compose ties Postgres + MinIO + MLflow + API + Streamlit + Airflow.
7. Observability: Prometheus + Grafana + Loki + Tempo + OTel, with drift metrics via Evidently.
8. CI/CD: GitHub Actions and Jenkins run lint/tests, DVC pull, and Bento build; release builds/pushes images.
9. Ops: model promotion via MLflow stages, Docker tags for rollback.
10. Gaps and next steps: alerting, formal data validation, thresholding.

Evidence (talk track anchors)
```text
# README.md
* **Primary Task:** RainTomorrow (binary classification)
```
```text
# dvc.yaml
stages:
  process:
  prepare_splits:
  train:
```
```text
# src/models/train_model.py
mlflow.log_metrics(metrics)
model_details = mlflow.register_model(model_uri, MODEL_NAME)
```
```text
# dags/retrain_dag.py
preprocess_data >> prepare_splits >> drift_check >> train_model
```
```text
# src/service.py
@bentoml.service(name="rain_prediction_service")
```

## 10 likely exam questions with crisp answers
1) Q: How is data versioned and reproduced?
   A: DVC tracks raw and processed data and defines the pipeline in `dvc.yaml` with hashes in `dvc.lock`.

2) Q: What triggers retraining?
   A: Airflow `weather_retrain_pipeline` is scheduled on the dataset update event and runs DVC stages plus drift check.

3) Q: Where are experiments tracked?
   A: MLflow runs are logged in `src/models/train_model.py` using `MLFLOW_TRACKING_URI` and `experiment_name` from `params.yaml`.

4) Q: How is the model promoted to production?
   A: The training script compares F1 to the current production model and transitions stages in the MLflow registry.

5) Q: What serving interface exists?
   A: BentoML service (`src/service.py`) exposes `/login` and `/predict` with JWT auth; FastAPI utility endpoints are in `src/api/main.py`.

6) Q: How do you deploy locally?
   A: Use `docker compose up -d` to run MLflow, MinIO, Postgres, API, and Streamlit per `docker-compose.yml`.

7) Q: What metrics are monitored?
   A: Prometheus scrapes BentoML `/metrics` and Pushgateway; training and drift metrics are pushed from scripts.

8) Q: How do you handle data drift?
   A: `src/monitoring/evidently_drift.py` creates reports and pushes drift metrics; Airflow runs it before training.

9) Q: What CI quality gates exist?
   A: GitHub Actions runs Ruff, pytest, DVC pull, and Bento build; pre-commit adds ruff/pytest/DVC hooks.

10) Q: How is rollback handled?
    A: MLflow stages allow reverting to archived model versions and Docker images are tagged with commit SHA for rollback.

Evidence (Q&A anchors)
```text
# .dvc/config
[remote "origin"]
    url = s3://dvc
```
```text
# src/models/train_model.py
if is_better:
    client.transition_model_version_stage(MODEL_NAME, model_details.version, "Production")
```
```text
# docker-compose.yml
api:
  ports:
    - "3000:3000"
```
```text
# prometheus.yml
  - job_name: bentoml_api
    metrics_path: /metrics
```
