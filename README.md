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

---

Quick Start
-----------
### Setup

```bash
# Clone repository
git clone https://github.com/a13x60r/dec25bmlops_int_weather.git
cd dec25bmlops_int_weather

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Data Pipeline
```bash
# Preprocess raw data
python src/data/preprocess.py
```

### Model training
```bash
# Train XGBoost model
python src/models/train_model.py
```

### Make predictions
```bash
# Run predictions on test data
python src/models/predict_model.py
```
---

API Usage
-----------
### Start API

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
python src/api/main.py
```

# API information
```bash
curl http://localhost:8000/
```

```
http://localhost:8000
```

```
http://localhost:8000/docs
```

# Health check
```bash
curl http://localhost:8000/health
```

```
http://localhost:8000/health
```

# Training endpoint
```bash
curl -X POST http://localhost:8000/train
```

# Test prediction with sample of X_test
```bash
python test_predict.py
```
---
