Weather Forecast in Australia — MLOps
====================================

This project is an **MLOps-oriented weather forecasting system** based on Australian daily weather observations.
It extends the classic *cookiecutter data science* structure with **data versioning, experiment tracking, CI/CD, deployment, and monitoring**.

*   **Primary Task:** RainTomorrow (binary classification)
*   **Dataset:** [Kaggle - Weather Dataset Rattle Package](https://www.kaggle.com/jsphyg/weather-dataset-rattle-package)

---

## Table of Contents
- [MLOps Stack](#mlops-stack)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
  - [Option A: Run Locally](#option-a-run-locally)
  - [Option B: Run with Docker](#option-b-run-with-docker)
- [Development & Testing](#development--testing)
  - [Code Quality & Tests](#code-quality--tests)
  - [Manual Execution](#manual-execution)
- [Key Metrics](#key-metrics)
- [Project Organization](#project-organization)
- [References](#references)

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
| - [ ] **Prometheus/Grafana** | Monitoring & drift |

---

## Configuration

**Crucial Step:** Before running the project (Locally or Docker), you must configure access to the data storage.

1.  **System Requirements**:
    *   Python 3.11+ (Local only)
    *   Docker Engine (Docker only)

6.  **DVC Credentials**:
    *   **Local Development**:
        *   Ensure `DAGSHUB_USERNAME` and `DAGSHUB_TOKEN` are in your `.env` file.
        *   This allows you to push/pull data locally via the S3 remote.

6.  **CI/CD Configuration (GitHub Actions)**:
    *   **CI & Release Pipelines**: Configured to use public HTTPS access for reading data.
    *   **Required Secrets**: To enable automatic releases and docker pushes, configure these **Repository Secrets**:
        *   `DAGSHUB_USERNAME`, `DAGSHUB_TOKEN`: For DVC data access.
        *   `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`: For pushing Docker images.
        *   `GITHUB_TOKEN`: Automatically provided by GitHub (no action needed).

7.  **Weather API (Optional)**:
    *   The project uses OpenWeatherMap for live data.
    *   Key is pre-configured in `docker-compose.yml` (Free Tier).
    *   To use your own: Set `OPENWEATHER_API_KEY` in `docker-compose.yml` or `.env`.

---

## Usage Guide

### Option A: Run Locally

1.  **Setup Environment**:
    ```powershell
    # Create and Activate Venv (Windows)
    python -m venv venv
    .\venv\Scripts\Activate

    # Install Dependencies
    pip install -e .
    pip install -r requirements.txt
    ```

2.  **Run Pipeline**:
    Reproduce the full DVC pipeline (trains model, updates artifacts):
    ```bash
    dvc repro
    ```

### Option B: Run with Docker

1.  **Build & Start Services**:
    ```bash
    docker compose build
    docker compose up -d
    ```
    *   **MLflow UI**: [http://localhost:5000](http://localhost:5000)
    *   **MinIO Console**: [http://localhost:9001](http://localhost:9001)

2.  **Run Training**:
    *   **Via Service**: `docker compose --profile train up`
    *   **Via Dev Container (Recommended)**:
        ```bash
        docker compose up -d dev
        docker compose exec dev dvc repro
        ```

3.  **Run API**:
    Start the BentoML API service on port 3000:
    ```bash
    docker compose up -d api
    ```
    *   **See [API.md](API.md) for full endpoint documentation.**
    *   **Swagger UI**: [http://localhost:3000](http://localhost:3000)
    *   **Authenticate**:
        Get your JWT token (default creds: `admin`/`admin`):
        ```bash
        curl -X POST "http://localhost:3000/login" \
             -H "Content-Type: application/json" \
             -d '{"input_data": {"username": "admin", "password": "admin"}}'
        ```
        *Response*: `{"token": "YOUR_TOKEN"}`

    *   **Example Request**:
        ```bash
        curl -X POST "http://localhost:3000/predict" \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer <YOUR_TOKEN>" \
             -d '{
                   "input_data": {
                       "MinTemp": 10.5, "MaxTemp": 25.0, "Rainfall": 0.0, "WindGustSpeed": 30.0,
                       "WindSpeed9am": 10.0, "WindSpeed3pm": 15.0, "Humidity9am": 60.0, "Humidity3pm": 40.0,
                       "Pressure9am": 1015.0, "Pressure3pm": 1012.0, "Temp9am": 15.0, "Temp3pm": 22.0,
                       "RainToday": 0, "Year": 2023
                   }
                 }'
        ```

3.  **Run with Airflow Orchestration**:
    *   **Access UI**: [http://localhost:8081](http://localhost:8081)
        *   User/Pass: `airflow/airflow`
    *   **Workflow**:
        *   **`data_update_pipeline`**: Producer DAG. Fetches live data from OpenWeatherMap API (2.5/weather) and appends to dataset.
        *   **`weather_retrain_pipeline`**: Consumer DAG. Automatically triggers `dvc repro` when data updates.
    *   **Key Directories**:
        *   `dags/`: Your Python DAG files.
        *   `logs/`: Airflow execution logs.

### Option C: Run with BentoML

1.  **Serve Locally**:
    ```bash
    bentoml serve src.service:RainPredictionService
    ```
    *   **Swagger UI**: [http://localhost:3000](http://localhost:3000)

2.  **Build Bento**:
    ```bash
    bentoml build
    ```

3.  **Container Registry**:
    The BentoML service is automatically built and pushed to Docker Hub and GHCR on every push to `master`.

    *   **Docker Hub**: `docker.io/a13x60r/rain-prediction-service:latest`
    *   **GHCR**: `ghcr.io/a13x60r/rain-prediction-service:latest`

    **Pull & Run**:
    ```bash
    docker run -it --rm -p 3000:3000 docker.io/a13x60r/rain-prediction-service:latest serve
    ```

---

## Development & Testing

### Code Quality & Tests
Ensure your code is clean and stable before committing.

*   **Run Tests**:
    ```bash
    pytest
    ```
*   **Linting**:
    ```bash
    ruff check .
    ```
*   **Pre-commit Hooks**:
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
-   **Classification:** ROC-AUC, F1, Precision, Recall, PR-AUC
-   **MLOps:** Latency (p95), error rate, data drift (PSI / KS)

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

## References
-   **Data Source**: [BOM Climate Data](http://www.bom.gov.au/climate/data)
-   **Template**: [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
