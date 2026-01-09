Weather Forecast in Australia — MLOps
====================================

This project is an **MLOps-oriented weather forecasting system** based on Australian daily weather observations.  
It extends the classic *cookiecutter data science* structure with **data versioning, experiment tracking, CI/CD, deployment, and monitoring**.

Primary ML task: **RainTomorrow (binary classification)**  
Secondary (optional): temperature, wind, and time-series forecasting.

Dataset:  
https://www.kaggle.com/jsphyg/weather-dataset-rattle-package

---

Project Organization
--------------------

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
    │
    ├── models                 <- Serialized models and predictions
    │
    ├── notebooks              <- Jupyter notebooks (EDA, experiments)
    │   └── 1.0-*-initial-eda.ipynb
    │
    ├── references             <- Data dictionaries, BOM docs, specs
    │
    ├── reports                <- Analysis reports
    │   └── figures            <- Generated plots and visual assets
    │
    ├── artifacts              <- MLflow/DVC outputs (metrics, artifacts)
    │
    ├── docker                 <- Dockerfiles and compose configs
    │
    ├── dvc.yaml               <- Reproducible ML pipeline definition
    ├── params.yaml            <- Model and data parameters
    │
    ├── requirements.txt       <- Pinned Python dependencies
    │
    ├── src                    <- Source code
    │   ├── __init__.py
    │   │
    │   ├── data               <- Data ingestion and validation
    │   │   └── make_dataset.py
    │   │
    │   ├── features           <- Feature engineering
    │   │   └── build_features.py
    │   │
    │   ├── models             <- Training and inference
    │   │   ├── train_model.py
    │   │   └── predict_model.py
    │   │
    │   ├── visualization      <- EDA and reporting plots
    │   │   └── visualize.py
    │   │
    │   └── config             <- Model, training, and infra configs
    │
    ├── tests                  <- Unit and pipeline smoke tests
    └── docker-compose.yml     <- Local MLflow / infra services

---

Run Locally (Virtual Environment)
---------------------------------

If you prefer to run the project without Docker, follow these steps:

### 1. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
Install the package in **editable mode** (crucial for local development) and all requirements:
```bash
pip install -e .
pip install -r requirements.txt
```

### 3. Run DVC Pipeline
Reproduce the pipeline to train the model and generate artifacts:
```bash
dvc repro
```
*Ensure you have configured your DVC credentials in `.dvc/config.local` as described below.*

### 4. Run Training Manually (Optional)
If you wish to run only the training script without checking the full DVC pipeline:
```bash
python -m weather_au_mlops.train
```

---

Run with Docker Compose
-----------------------

### 1. Configure DVC Credentials
To access data from version control, you must configure your DVC remote credentials:
1.  Navigate to the `.dvc` folder in the project root.
2.  Rename the file `!config.local` to `config.local` (remove the `!` exclamation mark).
    - *Note:* Do not commit `config.local` to version control as it contains secrets.
3.  Open `config.local` and enter your DagsHub credentials:
    ```ini
    user = <your-dagshub-username>
    password = <your-dagshub-token-or-password>
    ```

### 2. Run the Application
Start the entire infrastructure (MLflow, MinIO, PostgreSQL) and the development container:
```bash
docker compose up -d
```
You can access the services at:
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)

To run the training pipeline specifically:
```bash
docker compose --profile train up
```


### 3. Run DVC Pipeline in Docker
To run the full reproducible pipeline (which updates `dvc.lock` and ensures data consistency), use the `dev` service:
1.  Ensure the dev container is running:
    ```bash
    docker compose up -d dev
    ```
2.  Execute the reproduction command inside the container:
    ```bash
    docker compose exec dev dvc repro
    ```
    *Note: This mounts your local directory, so artifacts generated inside the container (like `models/`) will appear on your host machine.*

---

MLOps Stack
-----------
- **DVC + DAGsHub** — data & pipeline versioning  
- **MLflow** — experiment tracking & model registry  
- **Weights & Biases** — experiment comparison & dashboards  
- **Docker** — reproducible environments  
- **Airflow** — pipeline orchestration  
- **BentoML** — model serving  
- **Jenkins** — CI/CD  
- **Prometheus + Grafana** — monitoring & drift  
- **Kubernetes** — scalable deployment  

---

Key Metrics
-----------
- **Classification:** ROC-AUC, F1, Precision, Recall, PR-AUC  
- **Regression (optional):** RMSE, MAE  
- **MLOps:** latency (p95), error rate, data drift (PSI / KS)

---

References
----------
- Australian Bureau of Meteorology: http://www.bom.gov.au/climate/data  
- Example repo: https://github.com/DataScientest-Studio/dec25bmlops_int_weather  

---

Project based on the  
[cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/).
