# Packaging and Deployment

## BentoML packaging
- Bento definition points to `src.service:RainPredictionService` and includes service + auth files.
- Service loads preprocessor/model from `models/` and falls back to BentoML model store.
- `models/` holds `xgboost_model.pkl` and `preprocessor.pkl`; `artifacts/` is reserved for run outputs.

Evidence
```text
# bentofile.yaml
service: "src.service:RainPredictionService"
include:
  - "src/service.py"
  - "src/auth/jwt_auth.py"
  - "requirements.txt"
```
```text
# ls -la models artifacts (excerpt)
models:
-rw-r--r-- 1 aboro 197609    4080 Jan 30 19:10 preprocessor.pkl
-rw-r--r-- 1 aboro 197609 1426334 Feb  2 12:31 xgboost_model.pkl

artifacts:
-rw-r--r-- 1 aboro 197609 15 Jan 30 14:24 .gitignore
```
```text
# src/service.py
@bentoml.service(name="rain_prediction_service")
class RainPredictionService:
    def __init__(self):
        artifact_path = Path("models/preprocessor.pkl")
        self.model = bentoml.xgboost.load_model(tag)
        pickle_path = Path("models/xgboost_model.pkl")
```
```text
$ grep -R "bentoml" -n . | head -n 50
./.github/workflows/ci.yml:52:        bentoml build
./.github/workflows/release.yml:81:        bentoml build
./docker-compose.yml:150:    command: [ "bash", "-lc", "pip install -e . -r requirements.txt && bentoml serve src.service:RainPredictionService --host 0.0.0.0 --port 3000" ]
./src/models/train_model.py:22:import bentoml
./src/service.py:26:@bentoml.service(name="rain_prediction_service")
./src/service.py:52:            self.model = bentoml.xgboost.load_model(tag)
```

## API contract (BentoML + FastAPI)
- BentoML endpoints: `/login`, `/predict` with JWT auth (public: `/login`, `/docs`, `/metrics`).
- FastAPI utility API includes `/train`, `/predict`, `/dataset/update`, `/health`.

Evidence
```text
# API.md
This project contains two distinct API implementations:
1.  **BentoML Service** (`src/service.py`)
2.  **FastAPI Application** (`src/api/main.py`)

Public Endpoints: `/login`, `/docs`, `/metrics`
```
```text
# src/service.py
@bentoml.api
def login(self, username: str = ADMIN_USERNAME, password: str = ADMIN_PASSWORD) -> dict:
@bentoml.api
async def predict(...):
```
```text
# src/api/main.py
@app.post("/train")
@app.post("/predict")
@app.post("/dataset/update")
@app.get("/health")
```

## Docker Compose deployment
- `api` runs BentoML on port 3000, `streamlit` on 8501, MLflow on 5000, Postgres on 5432, MinIO on 9000/9001, Airflow on 8081.

Evidence
```text
# docker-compose.yml (excerpt)
api:
  command: [ "bash", "-lc", "pip install -e . -r requirements.txt && bentoml serve src.service:RainPredictionService --host 0.0.0.0 --port 3000" ]
  ports:
    - "3000:3000"

streamlit:
  ports:
    - "8501:8501"

mlflow:
  ports:
    - "5000:5000"

postgres:
  ports:
    - "5432:5432"

minio:
  ports:
    - "9000:9000"
    - "9001:9001"

airflow-webserver:
  ports:
    - "8081:8080"
```

## Image sources
- Release workflow builds and pushes `weather-app` and `rain-prediction-service` images to Docker Hub + GHCR.

Evidence
```text
# .github/workflows/release.yml
tags:
  ${{ secrets.DOCKERHUB_USERNAME }}/weather-app:latest
  ghcr.io/${{ github.repository_owner }}/weather-app:latest

bentoml containerize rain_prediction_service:latest \
  --image-tag "$DOCKER_TAG" \
  --image-tag "$GHCR_TAG"
```
```text
# README.md (excerpt)
Docker Hub: docker.io/a13x60r/rain-prediction-service:latest
GHCR: ghcr.io/a13x60r/rain-prediction-service:latest
```

## Local verification
- Script `verify_bento.py` sends a request to the BentoML API for smoke validation.

Evidence
```text
# verify_bento.py
url = "http://127.0.0.1:3000/predict"
response = requests.post(url, json=data, timeout=10)
```
