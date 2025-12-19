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
