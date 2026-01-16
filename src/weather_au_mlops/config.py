import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = project_root / "data"
    artifacts_dir: Path = project_root / "artifacts"


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


MLFLOW_TRACKING_URI = env("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MLFLOW_EXPERIMENT_NAME = env("MLFLOW_EXPERIMENT_NAME", "weather-au-rain")
