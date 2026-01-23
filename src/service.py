import pickle
from pathlib import Path

import bentoml
import pandas as pd


@bentoml.service(name="rain_prediction_service")
class RainPredictionService:
    def __init__(self):
        # Load model from local path relative to the service file (or project root when run)
        # When running centrally, paths might be sensitive.
        # using absolute path logic or relative to project root assuming run from root.

        # We need to handle path correctly for both local serve and built bento.
        # In built bento, files included are usually handling relative paths.

        model_path = Path("models/xgboost_model.pkl")
        if not model_path.exists():
            # Fallback for when running from src or different cwd?
            # Or strict check.
            pass

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    @bentoml.api
    def predict(self, input_data: dict) -> dict:
        """
        Make a prediction
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame([input_data])

            # Predict
            prediction = self.model.predict(df)[0]
            probability = self.model.predict_proba(df)[0][1]

            return {
                "prediction": int(prediction),
                "label": "Rain" if prediction == 1 else "No Rain",
                "probability": float(probability),
            }
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise e
