# Standard library imports
import logging
import os
import traceback

# Third-party imports
import bentoml
import jwt
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

# Local imports
from src.auth.jwt_auth import JWTAuthMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security constants
# These are still needed for Login endpoint to generate token
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "insecure-default-key-do-not-use-in-production")
JWT_ALGORITHM = "HS256"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

# 1. Define Runners
# We use the BentoML Model Store to get the model and convert it to a Runner.
# This decouples inference from the API server.
xgboost_runner = bentoml.xgboost.get("rain_prediction_model:latest").to_runner()

# 2. Create Service
# We initialize the service with the runner.
svc = bentoml.Service("rain_prediction_service", runners=[xgboost_runner])

# 3. Add Middleware
# This handles authentication globally for all endpoints (except those excluded in middleware)
svc.add_asgi_middleware(JWTAuthMiddleware)


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


class LoginInput(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


@svc.api(input=bentoml.io.JSON(pydantic_model=LoginInput), output=bentoml.io.JSON())
def login(input_data: LoginInput, ctx: bentoml.Context) -> dict:
    """
    Login to get a JWT token.
    """
    if input_data.username == ADMIN_USERNAME and input_data.password == ADMIN_PASSWORD:
        token = jwt.encode(
            {"username": input_data.username}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )
        return {"token": token}
    else:
        ctx.response.status_code = 401
        return {"detail": "Invalid credentials"}


@svc.api(input=bentoml.io.JSON(pydantic_model=RainInput), output=bentoml.io.JSON())
async def predict(input_data: RainInput) -> dict:
    """
    Make a prediction using the XGBoost model runner.
    Authentication is handled by middleware.
    """
    try:
        # Convert Pydantic model to dictionary (including extra fields)
        data_dict = input_data.model_dump()

        # Convert to DataFrame
        df = pd.DataFrame([data_dict])

        # Predict using the Runner (Asynchronous call)
        # Note: Standard XGBoost runner exposes 'predict' method
        prediction = await xgboost_runner.predict.async_run(df)

        # Taking the first element since batch size is 1 here
        pred_value = int(prediction[0])

        return {
            "prediction": pred_value,
            "label": "Rain" if pred_value == 1 else "No Rain",
            # "probability": float(probability), # Removed for now as predict_proba might need extra config
        }

    except Exception:
        # Log the full error internally
        logger.error("Error during prediction:")
        logger.error(traceback.format_exc())

        # Return a generic error is handled by BentoML exceptions usually, but specific 500 here
        raise bentoml.exceptions.BentoMLException(
            message="An internal server error occurred.", error_code=500
        ) from None
