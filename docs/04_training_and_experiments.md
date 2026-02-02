# Training and Experiments

## Repro entrypoints (how to train)
- DVC pipeline: `dvc repro` runs preprocess -> splits -> train.
- Direct script: `python src/models/train_model.py --split_id <n>`.
- Docker Compose training profile: `docker compose --profile train up`.

Evidence
```text
# dvc.yaml
stages:
  process:
    cmd: python src/data/preprocess.py
  prepare_splits:
    cmd: python src/data/training_data_splits_by_year.py
  train:
    cmd: python src/models/train_model.py
```
```text
# README.md (excerpt)
Reproduce the full DVC pipeline (trains model, updates artifacts):

    dvc repro

Train directly (skip DVC)

    python src/models/train_model.py --split_id 1
```
```text
# docker-compose.yml (excerpt)
trainer:
  command: [ "bash", "-lc", "pip install -e . -r requirements.txt && python src/models/train_model.py" ]
  profiles: [ "train" ]
```

## Python entrypoints discovered
Evidence
```text
$ grep -R "if __name__ == \"__main__\"" -n src
src/api/main.py:179:if __name__ == "__main__":
src/data/fetch_weather_data.py:105:if __name__ == "__main__":
src/data/training_data_splits_by_year.py:184:if __name__ == "__main__":
src/data/validate_data.py:61:if __name__ == "__main__":
src/models/train_model.py:452:if __name__ == "__main__":
src/monitoring/evidently_drift.py:223:if __name__ == "__main__":
src/streamlit_app/app.py:144:if __name__ == "__main__":
src/weather_au_mlops/evaluate.py:5:if __name__ == "__main__":
src/weather_au_mlops/train.py:49:if __name__ == "__main__":
```

## Params/config sources
- Core params live in `params.yaml`, loaded via `src/config/__init__.py`.

Evidence
```text
$ cat params.yaml
data:
  test_size: 0.2
  random_state: 42
  split_id: 2
model:
  type: xgboost
  max_depth: 9
  learning_rate: 0.05
  n_estimators: 200
  colsample_bytree: 0.8
  subsample: 0.7
  gamma: 0.1
  min_child_weight: 3
  random_state: 42
mlflow:
  tracking_uri: http://mlflow:5000
  experiment_name: weather-au-rain
```
```text
# src/config/__init__.py
PARAMS = load_params()
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
```

## MLflow tracking and registry
- Tracking URI is set from config and environment; experiments are named `weather-au-rain`.
- Training logs metrics, artifacts, and registers models; production promotion is based on F1 improvement.

Evidence
```text
# src/models/train_model.py
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.log_metrics(metrics)
mlflow.xgboost.log_model(
    model, artifact_path="model", signature=signature, input_example=X_train.iloc[:5]
)
model_details = mlflow.register_model(model_uri, MODEL_NAME)
if is_better:
    client.transition_model_version_stage(MODEL_NAME, model_details.version, "Production")
```
```text
$ grep -R "mlflow" -n src dags . | head -n 50
src/models/train_model.py:23:import mlflow
src/models/train_model.py:55:    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
src/models/train_model.py:56:    mlflow.set_experiment(EXPERIMENT_NAME)
src/models/train_model.py:220:            mlflow.log_metrics(metrics)
src/models/train_model.py:268:            model_details = mlflow.register_model(model_uri, MODEL_NAME)
dags/data_update_dag.py:47:            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
```

## Determinism and reproducibility
- `random_state` is set in `params.yaml` and used in SMOTE and model training.
- Dependencies are pinned in `pyproject.toml` and `requirements.txt`; base images are pinned in Dockerfiles.

Evidence
```text
# src/models/train_model.py
smote = SMOTE(random_state=PARAMS["data"]["random_state"])
model_params = {
    "random_state": PARAMS["model"]["random_state"],
}
```
```text
$ cat pyproject.toml (excerpt)
dependencies = [
    "pandas==2.2.2",
    "scikit-learn==1.5.1",
    "xgboost==2.1.1",
    "mlflow==2.15.1",
    "dvc==3.53.2",
    "bentoml==1.4.33",
]
```
```text
# Dockerfile.dev
FROM python:3.11.7-slim
```

## Makefile availability
Status: Not present in repo
- A Makefile exists, but `make` is not available in this environment.

Evidence
```text
$ make help
bash: line 1: make: command not found
```

Expected in mature setup
- A documented `make help` target listing build/train/test commands.

Actionable recommendations
- Add a `help` target in `Makefile` and ensure CI images include GNU Make.
- Mirror the DVC and Docker training commands in Make targets.
