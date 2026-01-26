import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

import jwt

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent))

# Set env vars before importing service
os.environ["ADMIN_USERNAME"] = "testuser"
os.environ["ADMIN_PASSWORD"] = "testpass"
os.environ["JWT_SECRET_KEY"] = "testsecret"

from unittest.mock import patch

import bentoml

from src.service import RainInput, RainPredictionService


class TestServiceSecurity(unittest.TestCase):
    def setUp(self):
        # Patch pickle.load to return a mock model
        self.pickle_patcher = patch("pickle.load")
        self.mock_pickle_load = self.pickle_patcher.start()

        self.mock_model = MagicMock()
        # Setup mock model behavior
        self.mock_model.predict.return_value = [0]
        self.mock_model.predict_proba.return_value = [[0.8, 0.2]]
        self.mock_pickle_load.return_value = self.mock_model

        # Initialize service
        self.service = RainPredictionService()

    def tearDown(self):
        self.pickle_patcher.stop()

    def test_login_success(self):
        result = self.service.login("testuser", "testpass")
        self.assertIn("token", result)
        decoded = jwt.decode(result["token"], "testsecret", algorithms=["HS256"])
        self.assertEqual(decoded["username"], "testuser")

    def test_login_failure(self):
        with self.assertRaises(bentoml.exceptions.BentoMLException) as cm:
            self.service.login("testuser", "wrongpass")
        self.assertEqual(cm.exception.error_code, 401)

    def test_predict_no_token(self):
        ctx = MagicMock()
        ctx.request.headers = {}
        input_data = self._get_valid_input()

        with self.assertRaises(bentoml.exceptions.BentoMLException) as cm:
            self.service.predict(input_data, ctx)
        self.assertEqual(cm.exception.error_code, 401)

    def test_predict_invalid_token(self):
        ctx = MagicMock()
        ctx.request.headers = {"Authorization": "Bearer invalidtoken"}
        input_data = self._get_valid_input()

        with self.assertRaises(bentoml.exceptions.BentoMLException) as cm:
            self.service.predict(input_data, ctx)
        self.assertEqual(cm.exception.error_code, 401)

    def test_predict_valid_token(self):
        # login first
        login_res = self.service.login("testuser", "testpass")
        token = login_res["token"]

        ctx = MagicMock()
        ctx.request.headers = {"Authorization": f"Bearer {token}"}
        input_data = self._get_valid_input()

        # This will fail if model loading failed or prediction logic fails,
        # but we are mainly testing the security wrapper part here.
        # However, since the service loads the real model, this is an integration test.
        try:
            result = self.service.predict(input_data, ctx)
            self.assertIn("prediction", result)
        except Exception as e:
            self.fail(f"Predict raised exception with valid token: {e}")

    def _get_valid_input(self):
        # Create a valid input object
        return RainInput(
            MinTemp=10.0,
            MaxTemp=20.0,
            Rainfall=0.0,
            WindGustSpeed=30.0,
            WindSpeed9am=10.0,
            WindSpeed3pm=15.0,
            Humidity9am=50.0,
            Humidity3pm=40.0,
            Pressure9am=1010.0,
            Pressure3pm=1008.0,
            Temp9am=12.0,
            Temp3pm=18.0,
            RainToday=0,
            Year=2021,
        )


if __name__ == "__main__":
    unittest.main()
