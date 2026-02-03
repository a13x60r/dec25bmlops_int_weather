# Monitoring and Ops

## Metrics collection (Prometheus + Pushgateway)

- Prometheus scrapes BentoML `/metrics`, Airflow statsd exporter, Postgres exporters, MinIO, node exporter, cAdvisor, and Pushgateway.
- Training and drift scripts push custom metrics to Pushgateway.

Evidence

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
# src/models/train_model.py
PUSHGATEWAY_URL = os.environ.get("PROMETHEUS_PUSHGATEWAY", "http://pushgateway:9091")
push_to_gateway(
    PUSHGATEWAY_URL,
    job="model_training",
    registry=registry,
)
```

```text
# src/monitoring/evidently_drift.py
DEFAULT_PUSHGATEWAY = "http://pushgateway:9091"
push_metrics(...)
```

## Logs and traces (Loki, Promtail, Tempo, OTel)

- Promtail tails Docker container logs and ships to Loki.
- OTel Collector exports traces to Tempo.
- API service sets OTel exporter env vars.

Evidence

```text
# promtail-config.yml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
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
# docker-compose.yml (excerpt)
api:
  environment:
    OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    OTEL_EXPORTER_OTLP_PROTOCOL: grpc
    OTEL_SERVICE_NAME: rain_prediction_service
```

## Dashboards and datasources

- Grafana is provisioned with Prometheus, Loki, and Tempo datasources and dashboard JSON files in `grafana/dashboards`.

Evidence

```text
# grafana-datasources.yml
datasources:
  - name: Prometheus
    url: http://prometheus:9090
  - name: Loki
    url: http://loki:3100
  - name: Tempo
    url: http://tempo:3200
```

```text
# grafana-dashboards.yml
providers:
  - name: mlops
    folder: MLOps
    options:
      path: /var/lib/grafana/dashboards
```

## Runbook (exam-ready)

- API down: check `docker compose ps`, ensure `api` and `mlflow` healthy; inspect BentoML logs; verify model files `models/xgboost_model.pkl` and `models/preprocessor.pkl` exist.
- Model drift detected: review `reports/evidently/*.html` and pushgateway metrics; trigger retrain via Airflow DAG `weather_retrain_pipeline`.
- Pipeline fails: use Airflow UI (port 8081), check task logs under `logs/`, and re-run failed task.

Evidence

```text
# dags/retrain_dag.py
preprocess_data >> prepare_splits >> drift_check >> train_model
```

## Rollback and versioning

- MLflow Model Registry stages are used to promote and archive model versions; BentoML stores models by tag; Docker images are tagged with `latest` and commit SHA.

Evidence

```text
# src/models/train_model.py
client.transition_model_version_stage(
    MODEL_NAME, current_model_version.version, "Archived"
)
client.transition_model_version_stage(
    MODEL_NAME, model_details.version, "Production"
)
```

```text
# .github/workflows/release.yml
tags:
  ${{ secrets.DOCKERHUB_USERNAME }}/weather-app:${{ github.sha }}
  ghcr.io/${{ github.repository_owner }}/weather-app:${{ github.sha }}
```

Status: Not present in repo

- Explicit alert rules (Alertmanager configs or Grafana alert policies) and SLO/SLA definitions.

Expected in mature setup

- Alerting for API error rate, model performance degradation, and data drift thresholds.

Actionable recommendations

- Add Alertmanager rules for `bentoml_service_request_total` 5xx rate and drift metrics.
- Define SLOs (p95 latency, error rate) and publish them in `docs/`.

## Service Level Objectives (SLOs)

| Metric | Target | Definition |
| :--- | :--- | :--- |
| **Availability** | 99.9% | Percentage of successful requests (2xx) over monthly window. |
| **Latency** | < 200ms | p95 latency for `/predict` endpoint. |
| **Data Drift** | < 0.05 | PSI score for `Rainfall` and `Pressure3pm`. |
| **Model Freshness** | < 24h | Time since last successful training run. |

## Alerting Rules

| Alert Name | Severity | Condition | Action |
| :--- | :--- | :--- | :--- |
| `APIHighErrorRate` | Critical | > 1% 5xx errors for 5m | Page On-Call, Check Logs |
| `APIHighLatency` | Warning | p95 > 300ms for 10m | Check Resource Usage |
| `DataDriftDetected` | Warning | PSI > 0.1 for critical features | Trigger Retraining |
| `PipelineFailure` | Error | Airflow DAG failure | Notify Slack Channel |
