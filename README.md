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
| - [ ] **Weights & Biases** | Experiment comparison & dashboards |
| - [ ] **Docker** | Reproducible environments |
| - [ ] **Airflow** | Pipeline orchestration |
| - [ ] **BentoML** | Model serving |
| - [ ] **Jenkins** | CI/CD |
| - [ ] **Prometheus/Grafana** | Monitoring & drift |

---

## Configuration

**Crucial Step:** Before running the project (Locally or Docker), you must configure access to the data storage.

1.  **System Requirements**:
    *   Python 3.11+ (Local only)
    *   Docker Engine (Docker only)

2.  **DVC Credentials**:
    *   Navigate to `.dvc/` directory.
    *   Rename `!config.local` to `config.local`.
    *   Edit `config.local` with your credentials:
        ```ini
        user = <your-dagshub-username>
        password = <your-dagshub-token-or-password>
        ```
    *   *Note:* `config.local` is git-ignored to protect secrets.

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
