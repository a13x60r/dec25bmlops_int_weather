Weather Forecast in Australia — MLOps
====================================

[![CI Pipeline](https://github.com/a13x60r/dec25bmlops_int_weather/actions/workflows/ci.yml/badge.svg)](https://github.com/a13x60r/dec25bmlops_int_weather/actions/workflows/ci.yml)
[![Release Pipeline](https://github.com/a13x60r/dec25bmlops_int_weather/actions/workflows/release.yml/badge.svg)](https://github.com/a13x60r/dec25bmlops_int_weather/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/a13x60r/dec25bmlops_int_weather)](https://github.com/a13x60r/dec25bmlops_int_weather/releases)
[![License: MIT](https://img.shields.io/github/license/a13x60r/dec25bmlops_int_weather)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-2e3138?logo=ruff)](https://github.com/astral-sh/ruff)
[![DVC](https://img.shields.io/badge/DVC-enabled-13ADC7?logo=dvc)](https://dagshub.com/a13x60r/dec25bmlops_int_weather)
[![DAGsHub](https://img.shields.io/badge/DAGsHub-connected-00AEEF)](https://dagshub.com/a13x60r/dec25bmlops_int_weather)
[![MLflow](https://img.shields.io/badge/MLflow-tracking-0194E2)](https://dagshub.com/a13x60r/dec25bmlops_int_weather.mlflow)
[![Airflow](https://img.shields.io/badge/Airflow-orchestration-017CEE?logo=apacheairflow)](https://airflow.apache.org/)
[![BentoML](https://img.shields.io/badge/BentoML-serving-FF6161)](https://www.bentoml.com/)
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker)](https://www.docker.com/)
[![MinIO](https://img.shields.io/badge/MinIO-artifacts-C72E49?logo=minio)](https://min.io/)
[![Postgres](https://img.shields.io/badge/Postgres-mlflow-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Docker Hub Pulls (API)](https://img.shields.io/docker/pulls/a13x60r/rain-prediction-service)](https://hub.docker.com/r/a13x60r/rain-prediction-service)
[![Docker Hub Pulls (App)](https://img.shields.io/docker/pulls/a13x60r/weather-app)](https://hub.docker.com/r/a13x60r/weather-app)
[![GHCR Image](https://img.shields.io/badge/GHCR-image-181717?logo=github)](https://github.com/a13x60r?tab=packages)
[![Last Commit](https://img.shields.io/github/last-commit/a13x60r/dec25bmlops_int_weather)](https://github.com/a13x60r/dec25bmlops_int_weather/commits/master)

[![Usage](https://img.shields.io/badge/Usage-Quickstart-0B5FFF)](#usage-guide)
[![Services](https://img.shields.io/badge/Services-Overview-0B5FFF)](#services--features)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Pipelines-0B5FFF)](#cicd)
[![API](https://img.shields.io/badge/API-Swagger-0B5FFF)](#option-b-run-with-docker)

This project is an **MLOps-oriented weather forecasting system** based on Australian daily weather observations.
It extends the classic *cookiecutter data science* structure with **[data versioning](#mlops-stack), [experiment tracking](#mlops-stack), [CI/CD](#cicd), [deployment](#option-d-run-with-bentoml), and [monitoring](#key-metrics)**.

* **Primary Task:** RainTomorrow (binary classification)
* **Dataset:** [Kaggle - Weather Dataset Rattle Package](https://www.kaggle.com/jsphyg/weather-dataset-rattle-package)

---

## Table of Contents

* [MLOps Stack](#mlops-stack)

* [Services & Features](#services--features)
* [Configuration](#configuration)
* [Usage Guide](#usage-guide)
  * [Option A: Run Locally](#option-a-run-locally)
  * [Option B: Run with Docker](#option-b-run-with-docker)
  * [Option C: Run with Airflow Orchestration](#option-c-run-with-airflow-orchestration)
  * [Option D: Run with BentoML](#option-d-run-with-bentoml)
  * [Using GHCR Images](#using-ghcr-images)
* [Development & Testing](#development--testing)
  * [Code Quality & Tests](#code-quality--tests)
  * [Manual Execution](#manual-execution)
* [Key Metrics](#key-metrics)
* [Project Organization](#project-organization)
* [CI/CD](#cicd)
* [References](#references)

---

## MLOps Stack

| Tool | Purpose |
| :--- | :--- |
| - [x] **DVC + DAGsHub** | Data & pipeline versioning |
| - [x] **MLflow** | Experiment tracking & model registry |
| - [x] **Docker** | Reproducible environments |
| - [x] **Airflow** | Pipeline orchestration |
| - [x] **BentoML** | Model serving |
| - [x] **Jenkins** | CI/CD |
| - [x] **GitHub Actions** | CI/CD |
| - [x] **Prometheus/Grafana** | Monitoring & drift |

---

## Services & Features

**Core services (Docker Compose)**

* **MLflow server**: Experiment tracking + model registry ([http://localhost:5000](http://localhost:5000))
* **Postgres**: MLflow backend store (`localhost:5432`)
* **MinIO + MinIO setup**: S3-compatible artifact storage ([http://localhost:9001](http://localhost:9001))
* **BentoML API**: Prediction service ([http://localhost:3000](http://localhost:3000))
* **Trainer**: Runs `src/models/train_model.py` with DVC/MLflow
* **Dev**: Interactive container for local development and DVC repro
* **Streamlit App**: Interactive UI for predictions ([http://localhost:8501](http://localhost:8501))

**Airflow services**

* **Airflow Webserver**: UI ([http://localhost:8081](http://localhost:8081), `airflow/airflow`)
* **Airflow Scheduler**: Orchestration
* **Airflow Postgres + Init**: Metadata DB + bootstrap
* **Failure alerts**: Slack notifications on task failure (optional)

**Monitoring services (Docker Compose profile: monitoring)**

> [!NOTE]
> These services are disabled by default. Start them with `docker compose --profile monitoring up -d`.

* **Prometheus**: Metrics ([http://localhost:9090](http://localhost:9090))
* **Grafana**: Dashboards ([http://localhost:3001](http://localhost:3001), `admin/admin`)
* **Loki**: Log aggregation ([http://localhost:3100](http://localhost:3100))
* **Tempo**: Traces ([http://localhost:3200](http://localhost:3200))
* **Pushgateway**: Training metrics ([http://localhost:9091](http://localhost:9091))
* **Exporters**: Airflow StatsD, Postgres, Node, cAdvisor

Grafana dashboards are provisioned under the **MLOps** folder from `grafana/dashboards`.

**Pipelines & orchestration**

* **DVC pipeline**: `dvc repro` for full training lifecycle
* **Airflow DAGs**:
  * `data_update_pipeline` (**Daily**): Fetches live OpenWeatherMap data, validates it, and appends to the raw dataset.
  * `weather_retrain_pipeline` (**Triggered**): Automatically runs when data updates. Executes DVC stages (`process` -> `prepare_splits` -> `train`) and pushes new artifacts to DAGsHub.
* **BentoML**: containerized prediction service and API endpoint (see [Option D](#option-d-run-with-bentoml))

---

## Configuration

**Crucial Step:** Before running the project ([Locally](#option-a-run-locally) or [Docker](#option-b-run-with-docker)), you must configure access to the data storage.

1. **System Requirements**:
    * Python 3.11+ (Local only)
    * Docker Engine (Docker only)

2. **DVC Credentials**:
    * **Local Development**:
        * **Option A (Pre-configured): Local MinIO**:
            * By default, DVC is configured to use the local MinIO service (`s3://dvc`) provided by Docker Compose.
            * No additional actions needed. This works out-of-the-box for local development.
        * **Option B: DAGsHub (Cloud)**:
            * To push/pull data to the shared DAGsHub storage (e.g. for collaboration), run:

            ```bash
            dvc remote modify --local origin url https://dagshub.com/a13x60r/dec25bmlops_int_weather.dvc
            dvc remote modify --local origin auth basic
            dvc remote modify --local origin user <YOUR_DAGSHUB_USERNAME>
            dvc remote modify --local origin password <YOUR_DAGSHUB_TOKEN>
            ```

            * This creates a `.dvc/config.local` file (ignored by git) to securely store your credentials.

3. **CI/CD Configuration (GitHub Actions)**:
    * **[CI & Release Pipelines](#cicd)**: Configure the DAGsHub DVC remote with basic auth for data access.
    * **Required Secrets**: To enable automatic releases and docker pushes, configure these **Repository Secrets**:
        * `DAGSHUB_USERNAME`, `DAGSHUB_TOKEN`: For DVC data access.
        * `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`: For pushing Docker images.
        * `GITHUB_TOKEN`: Automatically provided by GitHub (no action needed).

4. **Weather API (Optional)**:
    * The project uses OpenWeatherMap for live data.
    * Set `OPENWEATHER_API_KEY` in your `.env` (used by Airflow and the trainer service).

5. **Airflow Variables (Optional)**:
    * Slack alerts on task failure:
        * `SLACK_BOT_TOKEN`
        * `SLACK_CHANNEL`
    * These map to Airflow variables via `AIRFLOW_VAR_*` in `docker-compose.yml`.

6. **Docker Permissions (Airflow)**:
    * Airflow uses DockerOperator and mounts the Docker socket (`/var/run/docker.sock`).
    * Ensure your Docker host allows socket access from the Airflow containers.

---

## Usage Guide

### Option A: Run Locally

1. **Setup Environment**:

    ```powershell
    # Create and Activate Venv (Windows)
    python -m venv venv
    .\venv\Scripts\Activate

    # Create and Activate Venv (Linux/Mac)
    python3 -m venv venv
    source venv/bin/activate


    # Install Dependencies
    pip install -e .
    pip install -r requirements.txt
    ```

2. **Run Pipeline**:
    Reproduce the full DVC pipeline (trains model, updates artifacts):

    ```bash
    dvc repro
    ```

### Option B: Run with Docker

1. **Build & Start Services**:

    ```bash
    docker compose build
    docker compose up -d
    ```

    * **MLflow UI**: [http://localhost:5000](http://localhost:5000)
    * **MinIO Console**: [http://localhost:9001](http://localhost:9001)
    * **Postgres**: `localhost:5432`

    **Optional: Start monitoring stack**
    Start Grafana, Prometheus, and other monitoring tools:

    ```bash
    docker compose --profile monitoring up -d
    ```

    * **Grafana UI**: [http://localhost:3001](http://localhost:3001) (`admin`/`admin`)
    * **Prometheus**: [http://localhost:9090](http://localhost:9090)

2. **Run Training**:
    * **Via Service**: `docker compose --profile train up`
    * **Via Dev Container (Recommended)**:

        ```bash
        docker compose up -d dev
        docker compose exec dev dvc repro
        ```

3. **Run API**:
    Start the BentoML API service on port 3000:

    ```bash
    docker compose up -d api
    ```

    * **See [API.md](API.md) for full endpoint documentation.**
    * **Swagger UI**: [http://localhost:3000](http://localhost:3000)
    * **Authenticate**:
        Get your JWT token (default creds: `admin`/`admin`):

        ```bash
        curl -X POST "http://localhost:3000/login" \
             -H "Content-Type: application/json" \
             -d '{"username": "admin", "password": "admin"}'
        ```

        *Response*: `{"token": "YOUR_TOKEN"}`

    * **Example Request**:

        ```bash
        curl -X POST "http://localhost:3000/predict" \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer <YOUR_TOKEN>" \
             -d '{
                   "MinTemp": 10.5, "MaxTemp": 25.0, "Rainfall": 0.0, "WindGustSpeed": 30.0,
                   "WindSpeed9am": 10.0, "WindSpeed3pm": 15.0, "Humidity9am": 60.0, "Humidity3pm": 40.0,
                   "Pressure9am": 1015.0, "Pressure3pm": 1012.0, "Temp9am": 15.0, "Temp3pm": 22.0,
                   "RainToday": 0, "Year": 2023
                 }'
        ```

4. **Run Streamlit App**:
    Access the interactive UI to verify the model:

    ```bash
    docker compose up -d streamlit
    ```

    * **URL**: [http://localhost:8501](http://localhost:8501)
    * The app communicates with the API service automatically within the docker network.

### Option C: Run with Airflow Orchestration

1. **Access UI**: [http://localhost:8081](http://localhost:8081)
    * User/Pass: `airflow/airflow`
2. **Workflow**:
    * **`data_update_pipeline`**: Producer DAG. Runs **Daily**. Fetches live data from OpenWeatherMap API, validates schema, and updates the dataset.
    * **`weather_retrain_pipeline`**: Consumer DAG. **Triggered** by dataset updates. Runs the full training lifecycle (`preprocess` -> `splits` -> `train`) via DVC and pushes results to the remote storage.
3. **Key Directories**:
    * `dags/`: Your Python DAG files.
    * `logs/`: Airflow execution logs.

### Option D: Run with BentoML

1. **Serve Locally**:

    ```bash
    bentoml serve src.service:RainPredictionService
    ```

    * **Swagger UI**: [http://localhost:3000](http://localhost:3000)

2. **Build Bento**:

    ```bash
    bentoml build
    ```

3. **Container Registry**:
    The BentoML service is automatically built and pushed to Docker Hub and GHCR on every push to `master` (see [Using GHCR Images](#using-ghcr-images)).

    * **Docker Hub**: `docker.io/a13x60r/rain-prediction-service:latest`
    * **GHCR**: `ghcr.io/a13x60r/rain-prediction-service:latest`

    **Pull & Run**:

    ```bash
    docker run -it --rm -p 3000:3000 docker.io/a13x60r/rain-prediction-service:latest serve
    ```

### Available Docker Images

The project publishes two distinct images to GitHub Container Registry (GHCR):

| Image | Description | Use Case |
| :--- | :--- | :--- |
| **`rain-prediction-service`** | **The Product**. Production-ready AI API serving the prediction model. Includes Swagger UI (`/`) and JWT auth (`/login`). | **Deploying** the API for end-users to Kubernetes, Cloud Run, or servers. |
| **`weather-app`** | **The Factory**. Full development environment with Python 3.11, DVC, and training scripts. | **CI/CD**, testing, retraining models, or debugging pipelines. |

### Using GHCR Images

You can pull the pre-built images directly from the GitHub Container Registry (GHCR):

1. **Login to GHCR**:
    Create a Personal Access Token (classic) with `read:packages` scope.

    ```bash
    echo $CR_PAT | docker login ghcr.io -u a13x60r --password-stdin
    ```

2. **Pull Images**:

    ```bash
    # Main Application
    docker pull ghcr.io/a13x60r/weather-app:latest

    # BentoML Service
    docker pull ghcr.io/a13x60r/rain-prediction-service:latest
    ```

3. **Run Bento Service**:

    ```bash
    docker run -it --rm -p 3000:3000 ghcr.io/a13x60r/rain-prediction-service:latest serve
    ```

    Once the service is running, see the **[Run with Docker -> Run API](#run-api)** section for instructions on how to access the Swagger UI, authenticate, and make predictions.

---

## Train a New Model

**Reuse the pipeline (recommended)**

1. Update [`params.yaml`](params.yaml):
    * Point `data.raw_csv` to your dataset if needed.
    * Adjust model hyperparameters under `model`.
2. Run the full pipeline:

    ```bash
    dvc repro
    ```

**Train directly (skip DVC)**

```bash
python src/models/train_model.py --split_id 1
```

**Adding a different model type**

* Create a new training script (for example `src/models/train_lightgbm.py`) and add a new DVC stage in [`dvc.yaml`](dvc.yaml).
* Save the model under a new BentoML name to avoid overwriting the XGBoost model.

---

## Development & Testing

### Code Quality & Tests

Ensure your code is clean and stable before committing.

* **Run Tests**:

    ```bash
    pytest
    ```

* **Linting**:

    ```bash
    ruff check .
    ```

* **Pre-commit Hooks**:

    ```bash
    pre-commit install
    ```

### Manual Execution

If you need to run specific scripts without the full DVC pipeline:

**Local:**

```bash
# Train
python src/models/train_model.py

# Predict
python src/models/predict_model.py

# Verify BentoML Service
python verify_bento.py

```

**Docker:**
Execute the scripts inside the `dev` container:

```bash
# Train
docker compose exec dev python src/models/train_model.py

# Predict
docker compose exec dev python src/models/predict_model.py
```

---

## Key Metrics

The pipeline tracks the following metrics for model evaluation:

* **Classification:** ROC-AUC, F1, Precision, Recall, PR-AUC
* **MLOps:** Latency (p95), error rate, data drift (PSI / KS)

Training metrics are pushed to Prometheus via Pushgateway during `src/models/train_model.py` runs.

### Drift Monitoring (Evidently)

Drift checks run during the retrain workflow using the **training split of the current production model** as the
reference dataset. Reports are saved under `reports/evidently/` and summary drift metrics are pushed to Pushgateway.

**On-demand drift check**

```bash
python src/monitoring/evidently_drift.py
```

**Override splits or output directory**

```bash
python src/monitoring/evidently_drift.py --reference-split-id 2 --current-split-id 3 --output-dir reports/evidently
```

**Disable metrics push**

```bash
python src/monitoring/evidently_drift.py --no-push
```

---

## Project Organization

    ├── LICENSE
    ├── README.md              <- Project overview and instructions
    │
    ├── data                   <- Versioned with DVC
    │   ├── external           <- Third-party data sources
    │   ├── interim            <- Intermediate transformed data
    │   ├── processed          <- Final datasets for modeling
    │   └── raw                <- Original immutable data
    │
    ├── logs                   <- Training, inference, and pipeline logs
    ├── models                 <- Serialized models and predictions
    ├── notebooks              <- Jupyter notebooks (EDA, experiments)
    ├── references             <- Data dictionaries, BOM docs, specs
    ├── reports                <- Analysis reports
    ├── artifacts              <- MLflow/DVC outputs (metrics, artifacts)
    ├── docker                 <- Dockerfiles and compose configs
    │
    ├── dvc.yaml               <- Reproducible ML pipeline definition
    ├── params.yaml            <- Model and data parameters
    ├── requirements.txt       <- Pinned Python dependencies
    │
    ├── src                    <- Source code
    │   ├── data               <- Data ingestion and validation
    │   ├── features           <- Feature engineering
    │   ├── models             <- Training and inference
    │   ├── visualization      <- EDA and reporting plots
    │   └── config             <- Model, training, and infra configs
    │
    ├── tests                  <- Unit and pipeline smoke tests
    └── docker-compose.yml     <- Local MLflow / infra services

---

## CI/CD

Automatic quality assurance and deployment tracking are handled by GitHub Actions and Jenkins.

### 1. GitHub Actions: CI Pipeline ([`ci.yml`](.github/workflows/ci.yml))

**Trigger**: Pull requests to `master`.

Ensures that no broken code is merged into the main branch.

* **Dependencies**: Installs Python 3.11, pip, and required libraries (`requirements.txt`).
* **Data Integrity**: Runs `dvc pull` to ensure data versioning is configured and accessible.
* **Linting**: Enforces code style using `ruff`.
* **Testing**: Runs unit and integration tests with `pytest`.
* **Build Check**: Runs `bentoml build` to verify the model service can be packaged successfully.

### 2. GitHub Actions: Release Pipeline ([`release.yml`](.github/workflows/release.yml))

**Trigger**: Pushes to `master` and tags `v*.*.*`.

Deploys the application and service to container registries.

* **Pre-flight Checks**: Runs the full CI suite (Lint, Test, DVC Pull).
* **Docker Container**: Builds the main `weather-app` image containing the full environment.
  * **Pushes to**: DockerHub (`a13x60r/weather-app`) & GHCR (`ghcr.io/a13x60r/weather-app`).
  * **Tags**: `latest` and `commit-sha`.
* **BentoML Service**: Containerizes the API service.
  * **Pushes to**: DockerHub (`a13x60r/rain-prediction-service`) & GHCR (`ghcr.io/a13x60r/rain-prediction-service`).

### 3. Jenkins Pipeline ([`Jenkinsfile`](Jenkinsfile))

**Trigger**: Poll SCM / Webhook.

Provides a redundant, cross-platform CI environment.

* **Cross-Platform**: Designed to run checks on both **Windows** (Powershell) and **Linux** (Bash) agents.
* **Steps**:
  * Checkout Source
  * Create Virtual Environment (`venv`)
  * Install Dependencies (`pip install -r requirements.txt`)
  * Execute Tests (`pytest`)
  * Build Bento (`bentoml build`)

### Required Secrets

Set these in your GitHub Repository Secrets (`Settings -> Secrets and variables -> Actions`) to enable the pipelines:

| Secret | Purpose |
| :--- | :--- |
| `DAGSHUB_USERNAME` | Access to update/pull DVC data |
| `DAGSHUB_TOKEN` | Access token for DAGsHub |
| `DOCKERHUB_USERNAME` | Login for Docker Hub pushes |
| `DOCKERHUB_TOKEN` | Access token for Docker Hub |
| `GITHUB_TOKEN` | *(Auto-provided)* Access to GHCR and Issue commenting |

## References

* **Data Source**: [BOM Climate Data](http://www.bom.gov.au/climate/data)

* **Template**: [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
