# Architecture

## System overview
- Core pipeline: DVC stages build data and train an XGBoost model, tracked in MLflow and stored in MinIO, with promotion to Production based on F1.
- Serving: BentoML service with JWT auth; FastAPI utility API exists for training/testing endpoints.
- Orchestration: Airflow DAGs orchestrate daily data update and retraining via DockerOperator.
- Infra: Docker Compose coordinates Postgres, MinIO, MLflow, BentoML API, Streamlit, Airflow, and monitoring stack.
- Observability: Prometheus scrapes services, Grafana dashboards, Loki/Promtail for logs, Tempo/OTel for traces.

## Mermaid flow
```mermaid
flowchart LR
  A[Raw data in DVC] --> B[Preprocess stage]
  B --> C[Split by year]
  C --> D[Train XGBoost]
  D --> E[MLflow tracking + registry]
  E --> F[Model artifact store (MinIO/S3)]
  E --> G[BentoML service]
  G --> H[API + Streamlit UI]
  I[Airflow DAGs] --> B
  I --> C
  I --> D
  J[Prometheus + Grafana] --> G
  J --> D
  K[Loki + Promtail] --> G
  L[Tempo + OTel] --> G
```

## Infra placement (Postgres, MinIO, MLflow, API)
Evidence (Docker Compose excerpt)
```text
$ cat docker-compose.yml
services:
  postgres:
    image: postgres:16
    container_name: mlops_postgres
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
      POSTGRES_DB: mlflow
    ports:
      - "5432:5432"

  minio:
    image: minio/minio
    container_name: mlops_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio12345
    ports:
      - "9000:9000"
      - "9001:9001"

  mlflow:
    build:
      context: .
      dockerfile: Dockerfile.mlflow
    environment:
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minio
      AWS_SECRET_ACCESS_KEY: minio12345
    command: >
      mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri postgresql+psycopg2://mlflow:mlflow@postgres:5432/mlflow --artifacts-destination s3://mlflow/ --serve-artifacts
    ports:
      - "5000:5000"

  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: [ "bash", "-lc", "pip install -e . -r requirements.txt && bentoml serve src.service:RainPredictionService --host 0.0.0.0 --port 3000" ]
    ports:
      - "3000:3000"
```
```text
# Dockerfile.mlflow
FROM ghcr.io/mlflow/mlflow:v2.15.1
RUN pip install psycopg2-binary boto3
```

## Airflow orchestration
Evidence (Airflow DAGs)
```text
# dags/data_update_dag.py
with DAG(
    dag_id="data_update_pipeline",
    schedule="@daily",
):
    fetch_new_data = DockerOperator(
        task_id="fetch_weather_api",
        image="dec25bmlops_int_weather-trainer:latest",
        command='bash -lc "mkdir -p data/raw && python src/data/fetch_weather_data.py"',
    )
    validate_data = DockerOperator(
        task_id="validate_data",
        command='bash -lc "mkdir -p data/raw && python src/data/validate_data.py"',
        outlets=[weather_dataset],
    )
```
```text
# dags/retrain_dag.py
with DAG(
    "weather_retrain_pipeline",
    schedule=[weather_dataset],
):
    preprocess_data = DockerOperator(
        command='bash -lc "dvc repro process"',
    )
    prepare_splits = DockerOperator(
        command='bash -lc "dvc repro prepare_splits"',
    )
    drift_check = DockerOperator(
        command='bash -lc "python src/monitoring/evidently_drift.py --pushgateway-url http://pushgateway:9091"',
    )
    train_model = DockerOperator(
        command='bash -lc "dvc repro train && dvc push"',
    )
```

## Observability pipeline
Evidence (Prometheus + Grafana + Loki + Tempo + OTel configs)
```text
# prometheus.yml
scrape_configs:
  - job_name: bentoml_api
    metrics_path: /metrics
    static_configs:
      - targets: ["api:3000"]
  - job_name: pushgateway
    honor_labels: true
    static_configs:
      - targets: ["pushgateway:9091"]
```
```text
# grafana-datasources.yml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
  - name: Loki
    type: loki
    url: http://loki:3100
  - name: Tempo
    type: tempo
    url: http://tempo:3200
```
```text
# grafana-dashboards.yml
providers:
  - name: mlops
    folder: MLOps
    type: file
    options:
      path: /var/lib/grafana/dashboards
```
```text
# loki-config.yml
server:
  http_listen_port: 3100
common:
  storage:
    filesystem:
      chunks_directory: /loki/chunks
```
```text
# tempo.yml
distributor:
  receivers:
    otlp:
      protocols:
        grpc:
        http:
```
```text
# otel-collector.yml
receivers:
  otlp:
    protocols:
      grpc:
      http:
exporters:
  otlp:
    endpoint: tempo:4317
```
```text
# nginx.conf
server {
  listen 80;
  location / {
    proxy_pass http://mlflow:5000;
  }
}
```
