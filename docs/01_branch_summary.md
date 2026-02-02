# Branch Summary

## Repo purpose (RainTomorrow binary classification)
- The README states the task is RainTomorrow binary classification on Australian weather data, and positions the project as an MLOps stack integration.

Evidence
```text
$ cat README.md (excerpt)
This project is an **MLOps-oriented weather forecasting system** based on Australian daily weather observations.
It extends the classic *cookiecutter data science* structure with **[data versioning](#mlops-stack), [experiment tracking](#mlops-stack), [CI/CD](#cicd), [deployment](#option-d-run-with-bentoml), and [monitoring](#key-metrics)**.

* **Primary Task:** RainTomorrow (binary classification)
* **Dataset:** [Kaggle - Weather Dataset Rattle Package]
```

## Branch + last commit
- Current branch is `docs-g` with last commit `b49fa5f docs: add quickstart section to README`.

Evidence
```text
$ git rev-parse --abbrev-ref HEAD
docs-g
```
```text
$ git log -1 --oneline
b49fa5f docs: add quickstart section to README
```

## Working tree status
- There are untracked files including `.devcontainer/` and several Markdown files.

Evidence
```text
$ git status --porcelain
?? .devcontainer/
?? C
?? auto_pilot.md
?? debrief_and_horizon.md
?? flight_plan.md
?? instrument_readings.md
?? package-lock.json
```

## Repo inventory (top-level + depth-3 file list)

Evidence
```text
$ ls -la
total 513
drwxr-xr-x 1 aboro 197609     0 Feb  2 13:22 .
drwxr-xr-x 1 aboro 197609     0 Feb  2 12:53 ..
drwxr-xr-x 1 aboro 197609     0 Feb  2 13:22 .devcontainer
drwxr-xr-x 1 aboro 197609     0 Jan 30 19:10 .dvc
-rw-r--r-- 1 aboro 197609   782 Feb  2 09:15 .env
-rw-r--r-- 1 aboro 197609   113 Jan 30 14:24 .env.example
drwxr-xr-x 1 aboro 197609     0 Jan 30 14:24 .github
-rw-r--r-- 1 aboro 197609  1629 Jan 30 14:24 .gitignore
-rw-r--r-- 1 aboro 197609   773 Jan 30 14:24 .pre-commit-config.yaml
-rw-r--r-- 1 aboro 197609  3458 Jan 30 14:24 API.md
-rw-r--r-- 1 aboro 197609   650 Feb  2 08:38 Dockerfile
-rw-r--r-- 1 aboro 197609   551 Jan 30 14:24 Dockerfile.dev
-rw-r--r-- 1 aboro 197609   124 Jan 30 14:24 Dockerfile.mlflow
-rw-r--r-- 1 aboro 197609   716 Jan 30 14:24 Makefile
-rw-r--r-- 1 aboro 197609 22333 Feb  2 12:34 README.md
```
```text
$ ls -la (continued)
drwxr-xr-x 1 aboro 197609     0 Jan 30 14:24 artifacts
-rw-r--r-- 1 aboro 197609   181 Jan 30 14:24 bentofile.yaml
drwxr-xr-x 1 aboro 197609     0 Feb  2 08:38 dags
drwxr-xr-x 1 aboro 197609     0 Jan 30 19:10 data
-rw-r--r-- 1 aboro 197609 12902 Feb  2 09:07 docker-compose.yml
-rw-r--r-- 1 aboro 197609  2017 Jan 30 14:24 dvc.lock
-rw-r--r-- 1 aboro 197609   717 Jan 30 14:24 dvc.yaml
drwxr-xr-x 1 aboro 197609     0 Feb  2 08:36 grafana
-rw-r--r-- 1 aboro 197609   986 Feb  2 08:36 prometheus.yml
-rw-r--r-- 1 aboro 197609   839 Feb  2 08:36 promtail-config.yml
-rw-r--r-- 1 aboro 197609   795 Feb  2 11:01 pyproject.toml
-rw-r--r-- 1 aboro 197609    43 Jan 30 14:24 pytest.ini
-rw-r--r-- 1 aboro 197609   563 Feb  2 11:01 requirements.txt
-rw-r--r-- 1 aboro 197609   171 Jan 30 14:24 ruff.toml
drwxr-xr-x 1 aboro 197609     0 Feb  2 11:01 src
drwxr-xr-x 1 aboro 197609     0 Feb  2 10:26 tests
```

Evidence (file inventory, trimmed)
```text
$ find . -maxdepth 3 -type f | sort
./.devcontainer/devcontainer.json
./.dvc/config
./.github/workflows/ci.yml
./.github/workflows/release.yml
./API.md
./Dockerfile
./Dockerfile.dev
./Dockerfile.mlflow
./Makefile
./README.md
./bentofile.yaml
./dags/data_update_dag.py
./dags/retrain_dag.py
./data/raw/weatherAUS.csv.dvc
./docker-compose.yml
./dvc.lock
./dvc.yaml
./grafana-dashboards.yml
./grafana-datasources.yml
./grafana/dashboards/mlops-overview.json
./nginx.conf
./otel-collector.yml
./prometheus.yml
./promtail-config.yml
./pyproject.toml
./requirements.txt
./src/service.py
./src/models/train_model.py
./tests/test_predict.py
```

Evidence (key directories)
```text
$ ls -la dags src tests models artifacts data || true
artifacts:
total 13
drwxr-xr-x 1 aboro 197609  0 Jan 30 14:24 .
drwxr-xr-x 1 aboro 197609  0 Feb  2 13:22 ..
-rw-r--r-- 1 aboro 197609 15 Jan 30 14:24 .gitignore

dags:
total 32
drwxr-xr-x 1 aboro 197609    0 Feb  2 08:38 .
drwxr-xr-x 1 aboro 197609    0 Feb  2 13:22 ..
-rw-r--r-- 1 aboro 197609 2412 Feb  2 08:38 data_update_dag.py
-rw-r--r-- 1 aboro 197609 4189 Feb  2 11:02 retrain_dag.py

data:
total 21
drwxr-xr-x 1 aboro 197609  0 Jan 30 19:10 .
drwxr-xr-x 1 aboro 197609  0 Feb  2 13:22 ..
-rw-r--r-- 1 aboro 197609 43 Jan 30 14:24 .gitignore
drwxr-xr-x 1 aboro 197609  0 Jan 30 19:10 interim
drwxr-xr-x 1 aboro 197609  0 Jan 30 19:10 processed
drwxr-xr-x 1 aboro 197609  0 Jan 30 19:10 raw
```
```text
$ ls -la dags src tests models artifacts data || true (continued)
models:
total 1416
drwxr-xr-x 1 aboro 197609       0 Feb  2 11:54 .
drwxr-xr-x 1 aboro 197609       0 Feb  2 13:22 ..
-rw-r--r-- 1 aboro 197609       0 Jan 30 14:24 .gitkeep
-rw-r--r-- 1 aboro 197609    4080 Jan 30 19:10 preprocessor.pkl
-rw-r--r-- 1 aboro 197609 1426334 Feb  2 12:31 xgboost_model.pkl

src:
total 40
drwxr-xr-x 1 aboro 197609    0 Feb  2 11:01 .
drwxr-xr-x 1 aboro 197609    0 Feb  2 13:22 ..
-rw-r--r-- 1 aboro 197609    0 Jan 30 14:24 __init__.py
drwxr-xr-x 1 aboro 197609    0 Feb  2 10:26 api
drwxr-xr-x 1 aboro 197609    0 Jan 30 14:24 auth
drwxr-xr-x 1 aboro 197609    0 Jan 30 14:24 data
drwxr-xr-x 1 aboro 197609    0 Jan 30 14:24 features
drwxr-xr-x 1 aboro 197609    0 Feb  2 08:36 models
drwxr-xr-x 1 aboro 197609    0 Feb  2 11:02 monitoring
drwxr-xr-x 1 aboro 197609    0 Feb  2 08:36 streamlit_app
drwxr-xr-x 1 aboro 197609    0 Jan 30 14:24 visualization
```
```text
$ ls -la dags src tests models artifacts data || true (continued)
tests:
total 33
drwxr-xr-x 1 aboro 197609    0 Feb  2 10:26 .
drwxr-xr-x 1 aboro 197609    0 Feb  2 13:22 ..
-rw-r--r-- 1 aboro 197609 1675 Jan 30 14:24 test_predict.py
-rw-r--r-- 1 aboro 197609 5060 Feb  2 10:40 test_security_verification.py
-rw-r--r-- 1 aboro 197609   50 Jan 30 14:24 test_smoke.py
```

Evidence (Grafana directory)
```text
$ ls -la grafana || true
total 16
drwxr-xr-x 1 aboro 197609 0 Feb  2 08:36 .
drwxr-xr-x 1 aboro 197609 0 Feb  2 13:22 ..
drwxr-xr-x 1 aboro 197609 0 Feb  2 11:23 dashboards
```

## What this branch implements vs baseline
- The only visible delta is the latest commit message: a docs update adding a Quickstart section in README; no code changes were inspected beyond that.

Evidence
```text
$ git log -1 --oneline
b49fa5f docs: add quickstart section to README
```

## Component map (paths)
- Data versioning and pipeline: `dvc.yaml`, `dvc.lock`, `.dvc/config`, `data/`
- Training + evaluation: `src/models/train_model.py`, `src/models/predict_model.py`
- Orchestration (Airflow): `dags/data_update_dag.py`, `dags/retrain_dag.py`
- Experiment tracking (MLflow): `Dockerfile.mlflow`, `src/models/train_model.py`
- Serving (BentoML): `bentofile.yaml`, `src/service.py`
- Observability: `prometheus.yml`, `grafana-dashboards.yml`, `grafana-datasources.yml`, `loki-config.yml`, `promtail-config.yml`, `tempo.yml`, `otel-collector.yml`
- CI/CD: `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `Jenkinsfile`
