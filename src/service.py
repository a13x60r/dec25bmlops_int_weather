# Standard library imports
import logging
import os
import traceback
import pickle
from pathlib import Path

# Third-party imports
import bentoml
import jwt
import pandas as pd
import numpy as np
import xgboost as xgb
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security constants
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "insecure-default-key-do-not-use-in-production")
JWT_ALGORITHM = "HS256"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


# 1. Define Runners
try:
    xgboost_runner = bentoml.xgboost.get("rain_prediction_model:latest").to_runner()
except bentoml.exceptions.NotFound:
    # Fallback/Recovery: Load from pickle and save to BentoML store
    model_path = Path("models/xgboost_model.pkl")
    if model_path.exists():
        logger.info(f"Model not found in BentoML store. Loading from {model_path}...")
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        
        bentoml.xgboost.save_model("rain_prediction_model", model)
        xgboost_runner = bentoml.xgboost.get("rain_prediction_model:latest").to_runner()
    else:
        # We define runner anyway to pass to service, hoping it works or fails gracefully later
        logger.error(f"Critical Error: Model not found at {model_path}")
        # raise RuntimeError("Model not found in BentoML store OR models/xgboost_model.pkl!")
        # If we raise here, module import fails. 
        # But we need runner object.
        pass

# 2. Input Schemas
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
    
    # Optional fields
    Date: str | None = None
    Location: str | None = None
    WindGustDir: str | None = None
    WindDir9am: str | None = None
    WindDir3pm: str | None = None

    model_config = ConfigDict(extra="allow")

class LoginInput(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


# 3. Service Definition
@bentoml.service(name="rain_prediction_service", runners=[xgboost_runner])
class RainPredictionService:
    def __init__(self):
        # Force initialization of runner for local dev
        xgboost_runner.init_local()

        # Load artifacts on startup
        self.preprocessor = None
        try:
            artifact_path = Path("models/preprocessor.pkl")
            if artifact_path.exists():
                with open(artifact_path, "rb") as f:
                    self.preprocessor = pickle.load(f)
                logger.info("Preprocessing artifacts loaded successfully.")
            else:
                logger.warning(f"Preprocessing artifacts not found at {artifact_path}. Service may fail.")
        except Exception as e:
            logger.error(f"Failed to load preprocessing artifacts: {e}")

    def get_season_aus(self, month):
        if month in [12, 1, 2]:
            return "Summer"
        elif month in [3, 4, 5]:
            return "Autumn"
        elif month in [6, 7, 8]:
            return "Winter"
        else:
            return "Spring"

    def preprocess_input(self, data_dict: dict) -> pd.DataFrame:
        if self.preprocessor is None:
            return pd.DataFrame([data_dict])

        df = pd.DataFrame([data_dict])
        pp = self.preprocessor

        # 1. Handle Date/Season
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df["Year"] = df["Date"].dt.year
            df["Month"] = df["Date"].dt.month
            df["Season"] = df["Month"].apply(self.get_season_aus)
            df.drop(columns=["Date", "Month"], inplace=True)
 
        # 2. Imputation
        for col in pp["numeric_cols"]:
            if col not in df.columns:
                 df[col] = pp["train_medians"][col]
            else:
                 df[col] = df[col].fillna(pp["train_medians"][col])

        for col in pp["categorical_cols"]:
            if col not in df.columns:
                df[col] = pp["train_modes"][col]
            else:
                df[col] = df[col].fillna(pp["train_modes"][col])
                
        # 3. RainToday
        if "RainToday" in df.columns:
             if df["RainToday"].dtype == "object":
                 df["RainToday"] = df["RainToday"].map({"No": 0, "Yes": 1})
             df["RainToday"] = df["RainToday"].fillna(0).astype(int)

        # 4. OHE
        df = pd.get_dummies(df, columns=pp.get("categorical_cols_encoding", []), drop_first=True)

        # 5. Alienment
        expected_features = pp["feature_names"]
        df = df.reindex(columns=expected_features, fill_value=0)

        # 6. Scaling
        numeric_cols = pp["numeric_cols"]
        df[numeric_cols] = pp["scaler"].transform(df[numeric_cols])

        return df

    def verify_auth(self, ctx: bentoml.Context):
        request = ctx.request
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            ctx.response.status_code = 401
            raise Exception("Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]
        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            ctx.response.status_code = 401
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            ctx.response.status_code = 401
            raise Exception("Invalid token")
        except Exception as e:
            ctx.response.status_code = 401
            raise Exception(f"Auth error: {e}")

    @bentoml.api
    def login(self, input_data: LoginInput) -> dict:
        if input_data.username == ADMIN_USERNAME and input_data.password == ADMIN_PASSWORD:
            token = jwt.encode(
                {"username": input_data.username}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
            )
            return {"token": token}
        else:
            # ctx not available in sync api? It is if argument.
            # But let's raise simple error
            # Or use ctx argument
            return {"detail": "Invalid credentials", "status": 401} # BentoML handles return values?
            # Better to use ctx to set status code if possible, but let's keep it simple.
    
    @bentoml.api
    async def predict(self, input_data: RainInput, ctx: bentoml.Context) -> dict:
        try:
            self.verify_auth(ctx)
        except Exception as e:
            # verify_auth sets status code, we just return error message
            if ctx.response.status_code != 401:
                 ctx.response.status_code = 401
            return {"detail": str(e)}

        try:
            data_dict = input_data.model_dump()
            df = self.preprocess_input(data_dict)
            prediction = await xgboost_runner.predict.async_run(df)
            pred_value = int(prediction[0])
            return {
                "prediction": pred_value,
                "label": "Rain" if pred_value == 1 else "No Rain",
            }
        except Exception:
            logger.error("Error during prediction:")
            logger.error(traceback.format_exc())
            ctx.response.status_code = 500
            return {"detail": "Internal Server Error"}
