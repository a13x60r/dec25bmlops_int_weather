# API Documentation

This project contains two distinct API implementations:
1.  **BentoML Service** (`src/service.py`): The main inference service for the Rain Prediction model, intended for production deployment.
2.  **FastAPI Application** (`src/api/main.py`): A utility API for model training, testing, and dataset simulation.

---

## 1. BentoML Service (`src/service.py`)

This service is built using BentoML and focuses on serving the XGBoost model with JWT authentication.

### Authentication
The service uses JWT (JSON Web Tokens) for security.
- **Middleware**: `JWTAuthMiddleware` (`src/auth/jwt_auth.py`) protects endpoints.
- **Public Endpoints**: `/login`, `/docs`, `/metrics` are accessible without a token.

### Endpoints

#### `POST /login`
Authenticates a user and returns a JWT token.

*   **Input**: `LoginInput` (JSON)
    *   `username`: string
    *   `password`: string
*   **Output**: JSON
    *   `token`: string (JWT)
*   **Default Credentials**:
    *   Username: `admin` (or `ADMIN_USERNAME` env var)
    *   Password: `admin` (or `ADMIN_PASSWORD` env var)
    *   **Example Request**:
        ```bash
        curl -X POST "http://localhost:3000/login" \
             -H "Content-Type: application/json" \
             -d '{"username": "admin", "password": "admin"}'
        ```
        *Response*: `{"token": "YOUR_TOKEN"}`

#### `POST /predict`
Makes a prediction using the XGBoost runner. Requires `Authorization: Bearer <token>` header.

*   **Input**: `RainInput` (JSON) - Wrapped in `input_data` object
    *   `input_data` (object):
        *   `MinTemp` (float): Minimum temperature (C)
    *   `MaxTemp` (float): Maximum temperature (C)
    *   `Rainfall` (float): Rainfall (mm)
    *   `WindGustSpeed` (float): Peak wind gust speed (km/h)
    *   `WindSpeed9am` (float): Wind speed at 9am (km/h)
    *   `WindSpeed3pm` (float): Wind speed at 3pm (km/h)
    *   `Humidity9am` (float): Humidity at 9am (%)
    *   `Humidity3pm` (float): Humidity at 3pm (%)
    *   `Pressure9am` (float): Pressure at 9am (hPa)
    *   `Pressure3pm` (float): Pressure at 3pm (hPa)
    *   `Temp9am` (float): Temperature at 9am (C)
    *   `Temp3pm` (float): Temperature at 3pm (C)
    *   `RainToday` (int): 1 if it rained today, 0 otherwise
    *   `Year` (int): Year of observation
    *   *(Extra fields are allowed for location/wind One-Hot encoding)*
*   **Output**: JSON
    *   `prediction`: int (0 or 1)
    *   `label`: string ("Rain" or "No Rain")

---

## 2. FastAPI Application (`src/api/main.py`)

This is a standalone FastAPI app used for training workflows and simple testing.

### Endpoints

#### `POST /train`
Triggers the model training pipeline (`src/models/train_model.py`).
*   **Response**: Success/Failure message.

#### `POST /predict`
Make a prediction using the pickle-loaded model.
*   **Input**: JSON dictionary with model features (approx 110 features expected).
*   **Output**:
    *   `prediction`: int
    *   `label`: string
    *   `probability`: float

#### `POST /dataset/update`
Simulates the arrival of new data by incrementing the `split_id` in `params.yaml`.
*   **Response**: Details about the updated split.
*   **Usage**: Useful for testing MLOps pipelines (e.g., drift detection, re-training triggers).

#### `GET /health`
*   **Response**: `{"status": "healthy", "model_loaded": boolean}`
