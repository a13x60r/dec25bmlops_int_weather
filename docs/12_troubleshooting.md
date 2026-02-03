# Troubleshooting Guide & Runbook

This guide covers common issues encountered during development, training, and deployment of the Rain Prediction service.

## 🚨 Critical System Failures

### 1. API Service 503 / Availability Issues

**Symptom**: `curl` requests return 503 or Connection Refused.
**Diagnosis**:

1. Check container status:

   ```bash
   docker compose ps
   ```

   Ensure `api` and `mlflow` containers are `Up`.

2. Inspect Service Logs:

   ```bash
   docker compose logs -f api
   ```

   Look for:
   - `FileNotFoundError`: Missing model files (`models/xgboost_model.pkl`).
   - `BentoMLException`: Service failed to bind port.

**Resolution**:

- If model missing: Run `dvc pull` inside the container or locally.
- If port busy: Check if port 3000 is occupied (`netstat -ano | findstr :3000`).

### 2. Airflow DAG Failure

**Symptom**: DAGs stuck in `queued` or marked `failed`.
**Diagnosis**:

- Access Airflow UI at [http://localhost:8081](http://localhost:8081).
- Click on the failed task instance -> **Logs**.

**Common Failures**:

- **DockerOperator Error**: The Airflow worker cannot talk to the Docker daemon.
  - *Fix*: Ensure `/var/run/docker.sock` is correctly mounted in `docker-compose.yml`.
- **API Rate Limit**: OpenWeatherMap API key invalid or quota exceeded.
  - *Fix*: Check `OPENWEATHER_API_KEY` in `.env`.

## 📉 Model Performance Issues

### 1. Data Drift Warnings

**Symptom**: `DataDriftDetected` alert fires (PSI > 0.1).
**Action**:

1. Run a manual drift report:

   ```bash
   python src/monitoring/evidently_drift.py --reference-split-id 1 --current-split-id 2
   ```

2. Open `reports/evidently/drift_*.html`.
3. If drift is confirmed on key features (`Pressure3pm`, `Humidity3pm`):
   - Trigger `weather_retrain_pipeline` in Airflow.
   - Or run manual retraining: `dvc repro train`.

### 2. High Prediction Latency (p95 > 200ms)

**Action**:

1. Check resource usage: `docker stats`.
2. Inspect Traces in Grafana Tempo ([http://localhost:3200](http://localhost:3200)).
   - Look for slow spans in `src.service.predict`.

## 🛠️ Development issues

### 1. DVC Pull Failed

**Error**: `ERROR: unexpected error - 403 Client Error` or `Authentication failed`.
**Fix**:

- Re-configure remote credentials:

  ```bash
  dvc remote modify --local origin user <DAGSHUB_USER>
  dvc remote modify --local origin password <DAGSHUB_TOKEN>
  ```

### 2. Docker Storage Full

**Symptom**: `No space left on device` during build.
**Fix**:
Prune old images and build cache:

```bash
docker system prune -a
```
