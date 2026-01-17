import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Add src to path to ensure we can import the app
sys.path.append(str(Path(__file__).parent.parent))

from src.api.main import app

client = TestClient(app)


@pytest.fixture
def sample_data():
    """Load real data if available, otherwise return dummy data."""
    data_path = Path("data/processed/X_test.csv")
    if data_path.exists():
        try:
            df = pd.read_csv(data_path)
            return df.iloc[0].to_dict()
        except Exception:
            pass

    # Fallback dummy data (110 features as mentioned in API doc)
    return {f"feature_{i}": 0.5 for i in range(110)}


@pytest.fixture
def mock_model_fns():
    """Mock the model prediction methods."""
    with patch("src.api.main.model") as mock_model:
        # Setup mock behavior
        mock_model.predict.return_value = [1]
        # predict_proba returns list of probabilities for classes [0, 1]
        mock_model.predict_proba.return_value = [[0.2, 0.8]]
        yield mock_model


def test_predict_endpoint(mock_model_fns, sample_data):
    """Test the predict endpoint with mocked model."""
    response = client.post("/predict", json=sample_data)

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "label" in data
    assert "probability" in data
    assert data["prediction"] == 1
    assert data["label"] == "Rain"
    # Probability is the second value in the proba array (for class 1)
    assert data["probability"] == 0.8
