import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import jwt

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent))

# Set env vars before importing service
os.environ["ADMIN_USERNAME"] = "testuser"
os.environ["ADMIN_PASSWORD"] = "testpass"
os.environ["JWT_SECRET_KEY"] = "testsecret"

from src.service import RainPredictionService


class TestServiceSecurity(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Patch pickle.load to return a mock preprocessor and model
        self.pickle_patcher = patch("pickle.load")
        self.mock_pickle_load = self.pickle_patcher.start()

        # Patch bentoml.xgboost.load_model and save_model to avoid using real store
        # We patch it where it is used in src.service
        self.bento_load_patcher = patch("src.service.bentoml.xgboost.load_model")
        self.mock_load_model = self.bento_load_patcher.start()
        self.mock_load_model.side_effect = Exception("Not found in store")

        self.bento_save_patcher = patch("src.service.bentoml.xgboost.save_model")
        self.mock_save_model = self.bento_save_patcher.start()

        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = [0]
        self.mock_model.predict_proba.return_value = [[0.8, 0.2]]

        # Preprocessor dict mock
        self.mock_preprocessor = {
            "numeric_cols": ["MinTemp"],
            "categorical_cols": [],
            "categorical_cols_encoding": [],
            "feature_names": ["MinTemp"],
            "scaler": MagicMock(),
            "train_medians": {"MinTemp": 0.0},
            "train_modes": {},
        }
        self.mock_preprocessor["scaler"].transform.side_effect = lambda x: x

        # First call is for preprocessor, second for model (fallback)
        def mock_load(f):
            if "preprocessor" in str(f.name):
                return self.mock_preprocessor
            return self.mock_model

        self.mock_pickle_load.side_effect = mock_load

        # Initialize service
        self.service = RainPredictionService()

    def tearDown(self):
        self.pickle_patcher.stop()
        self.bento_load_patcher.stop()
        self.bento_save_patcher.stop()

    def test_login_success(self):
        result = self.service.login(username="testuser", password="testpass")
        self.assertIn("token", result)
        decoded = jwt.decode(result["token"], "testsecret", algorithms=["HS256"])
        self.assertEqual(decoded["username"], "testuser")

    def test_login_failure(self):
        result = self.service.login(username="testuser", password="wrongpass")
        self.assertEqual(result.get("status"), 401)
        self.assertEqual(result.get("detail"), "Invalid credentials")

    async def test_predict_no_token(self):
        ctx = MagicMock()
        ctx.request.headers = {}
        input_data = self._get_valid_input()

        result = await self.service.predict(
            ctx, **input_data
        )  # Should return error dict, not raise
        self.assertEqual(ctx.response.status_code, 401)
        self.assertIn("Missing or invalid Authorization header", result["detail"])

    async def test_predict_invalid_token(self):
        ctx = MagicMock()
        ctx.request.headers = {"Authorization": "Bearer invalidtoken"}
        input_data = self._get_valid_input()

        result = await self.service.predict(ctx, **input_data)
        self.assertEqual(ctx.response.status_code, 401)
        # Service catches 'Invalid token' and returns it in detail
        self.assertIn("Invalid token", result["detail"])

    async def test_predict_valid_token(self):
        # login first
        login_res = self.service.login(username="testuser", password="testpass")
        token = login_res["token"]

        ctx = MagicMock()
        ctx.request.headers = {"Authorization": f"Bearer {token}"}
        input_data = self._get_valid_input()

        # The service uses self.model.predict directly now.
        # We already mocked self.model in setUp and assigned it to self.service.model
        # because the RainPredictionService constructor loads it or errors.

        result = await self.service.predict(ctx, **input_data)
        self.assertIn("prediction", result)
        self.assertEqual(result["prediction"], 0)

    def _get_valid_input(self):
        # Create a valid input dict
        return {
            "MinTemp": 10.0,
            "MaxTemp": 20.0,
            "Rainfall": 0.0,
            "WindGustSpeed": 30.0,
            "WindSpeed9am": 10.0,
            "WindSpeed3pm": 15.0,
            "Humidity9am": 50.0,
            "Humidity3pm": 40.0,
            "Pressure9am": 1010.0,
            "Pressure3pm": 1008.0,
            "Temp9am": 12.0,
            "Temp3pm": 18.0,
            "RainToday": 0,
            "Year": 2021,
        }


if __name__ == "__main__":
    unittest.main()
