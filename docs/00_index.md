# Doc Pack Index

## What I will say (6-10 bullets)

- This branch documents a RainTomorrow binary classification pipeline with DVC-driven data/version control and MLflow-backed training.
- Training is reproducible via `dvc repro` and Docker Compose services; Airflow orchestrates daily data updates and retraining triggers.
- Model artifacts are tracked in MLflow and promoted to Production based on F1 score improvement checks.
- Serving is provided by a BentoML service with JWT auth and a fallback FastAPI utility API for training/testing.
- The stack includes Postgres + MinIO for MLflow storage and an observability profile with Prometheus, Grafana, Loki, Tempo, and OpenTelemetry.
- CI gates run lint, tests, DVC pull, and Bento build; release workflows build and push Docker + Bento images.
- Drift monitoring uses Evidently reports and pushes metrics to Prometheus Pushgateway.
- OpenWeather API data ingestion is automated via Airflow, with basic data validation before retraining.

## Docs in this pack

- [01_branch_summary.md](01_branch_summary.md)
- [02_architecture.md](02_architecture.md)
- [03_data.md](03_data.md)
- [04_training_and_experiments.md](04_training_and_experiments.md)
- [05_evaluation.md](05_evaluation.md)
- [06_packaging_and_deployment.md](06_packaging_and_deployment.md)
- [07_ci_cd_quality.md](07_ci_cd_quality.md)
- [08_monitoring_and_ops.md](08_monitoring_and_ops.md)
- [09_exam_talk_track.md](09_exam_talk_track.md)
- [10_api_reference.md](10_api_reference.md)
- [11_project_roadmap.md](11_project_roadmap.md)
- [12_troubleshooting.md](12_troubleshooting.md)
