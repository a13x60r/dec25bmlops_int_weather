# Standard library imports
import logging
import os
import pickle
import traceback
from pathlib import Path

# Third-party imports
import bentoml
import jwt
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security constants
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "insecure-default-key-do-not-use-in-production")
JWT_ALGORITHM = "HS256"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


# Define the input schema
class RainInput(BaseModel):
    # Key meteorological features
    MinTemp: float = Field(..., description="Minimum temperature in degrees Celsius")
    MaxTemp: float = Field(..., description="Maximum temperature in degrees Celsius")
    Rainfall: float = Field(..., description="Rainfall in mm")
    WindGustSpeed: float = Field(..., description="Peak wind gust speed in km/h")
    WindSpeed9am: float = Field(..., description="Wind speed at 9am in km/h")
    WindSpeed3pm: float = Field(..., description="Wind speed at 3pm in km/h")
    Humidity9am: float = Field(..., description="Humidity at 9am in percent")
    Humidity3pm: float = Field(..., description="Humidity at 3pm in percent")
    Pressure9am: float = Field(..., description="Atmospheric pressure at 9am in hPa")
    Pressure3pm: float = Field(..., description="Atmospheric pressure at 3pm in hPa")
    Temp9am: float = Field(..., description="Temperature at 9am in degrees Celsius")
    Temp3pm: float = Field(..., description="Temperature at 3pm in degrees Celsius")
    RainToday: int = Field(..., description="1 if it rained today, 0 otherwise")
    Year: int = Field(..., description="Year of the observation")

    # Allow extra fields for the 90+ One-Hot-Encoded location/wind columns
    model_config = ConfigDict(extra="allow")


@bentoml.service(name="rain_prediction_service")
class RainPredictionService:
    def __init__(self):
        model_path = Path("models/xgboost_model.pkl")
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    @bentoml.api
    def login(
        self,
        username: str = Field(..., description="Username"),
        password: str = Field(..., description="Password"),
    ) -> dict:
        """
        Login to get a JWT token.
        """
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            token = jwt.encode({"username": username}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return {"token": token}
        else:
            raise bentoml.exceptions.BentoMLException(message="Invalid credentials", error_code=401)

    @bentoml.api
    def predict(self, input_data: RainInput, ctx: bentoml.Context) -> dict:
        """
        Make a prediction using the XGBoost model.
        Requires 'Authorization: Bearer <token>' header.
        """
        # 1. Verify Authentication
        auth_header = ctx.request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise bentoml.exceptions.BentoMLException(
                message="Missing or invalid Authorization header", error_code=401
            )

        token = auth_header.split(" ")[1]
        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise bentoml.exceptions.BentoMLException(message="Token has expired", error_code=401)
        except jwt.InvalidTokenError:
            raise bentoml.exceptions.BentoMLException(message="Invalid token", error_code=401)

        try:
            # Convert Pydantic model to dictionary (including extra fields)
            data_dict = input_data.model_dump()

            # Convert to DataFrame
            df = pd.DataFrame([data_dict])

            # Ensure columns are in the correct order/set if necessary,
            # but XGBoost on DataFrame usually handles by column name if trained that way.
            # If trained on numpy array with no names, order matters strictly.
            # Assuming model was trained with feature names active.

            # Predict
            prediction = self.model.predict(df)[0]
            probability = self.model.predict_proba(df)[0][1]

            return {
                "prediction": int(prediction),
                "label": "Rain" if prediction == 1 else "No Rain",
                "probability": float(probability),
            }
        except Exception:
            # Log the full error internally
            logger.error("Error during prediction:")
            logger.error(traceback.format_exc())

            # Return a generic error to the client to avoid leaking internals
            raise bentoml.exceptions.BentoMLException(
                message="An internal server error occurred.", error_code=500
            )
