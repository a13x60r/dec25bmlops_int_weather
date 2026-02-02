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
from pydantic import Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security constants
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "insecure-default-key-do-not-use-in-production")
JWT_ALGORITHM = "HS256"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


# 3. Service Definition
@bentoml.service(name="rain_prediction_service")
class RainPredictionService:
    def __init__(self):
        # Load artifacts on startup
        self.preprocessor = None
        self.model = None

        # 1. Load Preprocessor
        try:
            artifact_path = Path("models/preprocessor.pkl")
            if artifact_path.exists():
                with open(artifact_path, "rb") as f:
                    self.preprocessor = pickle.load(f)
                logger.info("Preprocessing artifacts loaded successfully.")
            else:
                logger.warning(
                    f"Preprocessing artifacts not found at {artifact_path}. Service may fail."
                )
        except Exception as e:
            logger.error(f"Failed to load preprocessing artifacts: {e}")

        # 2. Load XGBoost Model
        model_name = "rain_prediction_model"
        tag = f"{model_name}:latest"
        try:
            # Try loading from BentoML store
            self.model = bentoml.xgboost.load_model(tag)
            logger.info(f"Loaded model '{tag}' from BentoML store.")
        except Exception as e:
            logger.warning(f"Could not load model '{tag}' from BentoML store: {e}")
            # Fallback to pickle
            pickle_path = Path("models/xgboost_model.pkl")
            if pickle_path.exists():
                logger.info(f"Fallback: Loading model from {pickle_path}...")
                try:
                    with open(pickle_path, "rb") as f:
                        self.model = pickle.load(f)
                    # Save to BentoML store for future
                    bentoml.xgboost.save_model(model_name, self.model)
                    logger.info(f"Model saved to BentoML store as '{model_name}'")
                except Exception as load_error:
                    logger.error(f"Failed to load/save model from pickle: {load_error}")
                    raise
            else:
                logger.error(
                    f"Critical: Model not found in store AND pickle not found at {pickle_path}"
                )
                raise RuntimeError(f"Model {model_name} not found.") from None

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
            raise Exception("Token has expired") from None
        except jwt.InvalidTokenError:
            ctx.response.status_code = 401
            raise Exception("Invalid token") from None
        except Exception as e:
            ctx.response.status_code = 401
            raise Exception(f"Auth error: {e}") from e

    @bentoml.api
    def login(self, username: str = ADMIN_USERNAME, password: str = ADMIN_PASSWORD) -> dict:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            token = jwt.encode({"username": username}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return {"token": token}
        else:
            return {
                "detail": "Invalid credentials",
                "status": 401,
            }

    @bentoml.api
    async def predict(
        self,
        ctx: bentoml.Context,
        MinTemp: float = Field(..., description="Minimum temperature in degrees Celsius"),
        MaxTemp: float = Field(..., description="Maximum temperature in degrees Celsius"),
        Rainfall: float = Field(..., description="Rainfall in mm"),
        WindGustSpeed: float = Field(..., description="Peak wind gust speed in km/h"),
        WindSpeed9am: float = Field(..., description="Wind speed at 9am in km/h"),
        WindSpeed3pm: float = Field(..., description="Wind speed at 3pm in km/h"),
        Humidity9am: float = Field(..., description="Humidity at 9am in percent"),
        Humidity3pm: float = Field(..., description="Humidity at 3pm in percent"),
        Pressure9am: float = Field(..., description="Atmospheric pressure at 9am in hPa"),
        Pressure3pm: float = Field(..., description="Atmospheric pressure at 3pm in hPa"),
        Temp9am: float = Field(..., description="Temperature at 9am in degrees Celsius"),
        Temp3pm: float = Field(..., description="Temperature at 3pm in degrees Celsius"),
        RainToday: int = Field(..., description="1 if it rained today, 0 otherwise"),
        Year: int = Field(..., description="Year of the observation"),
        Date: str | None = None,
        Location: str | None = None,
        WindGustDir: str | None = None,
        WindDir9am: str | None = None,
        WindDir3pm: str | None = None,
    ) -> dict:
        try:
            self.verify_auth(ctx)
        except Exception as e:
            # verify_auth sets status code, we just return error message
            if ctx.response.status_code != 401:
                ctx.response.status_code = 401
            return {"detail": str(e)}

        try:
            data_dict = {
                "MinTemp": MinTemp,
                "MaxTemp": MaxTemp,
                "Rainfall": Rainfall,
                "WindGustSpeed": WindGustSpeed,
                "WindSpeed9am": WindSpeed9am,
                "WindSpeed3pm": WindSpeed3pm,
                "Humidity9am": Humidity9am,
                "Humidity3pm": Humidity3pm,
                "Pressure9am": Pressure9am,
                "Pressure3pm": Pressure3pm,
                "Temp9am": Temp9am,
                "Temp3pm": Temp3pm,
                "RainToday": RainToday,
                "Year": Year,
                "Date": Date,
                "Location": Location,
                "WindGustDir": WindGustDir,
                "WindDir9am": WindDir9am,
                "WindDir3pm": WindDir3pm,
            }

            df = self.preprocess_input(data_dict)

            # Use direct model prediction instead of runner
            prediction = self.model.predict(df)

            # Handle prediction output (might be numpy array)
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
