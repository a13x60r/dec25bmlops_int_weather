import logging
import os
import sys

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

DATA_PATH = "data/raw/weatherAUS.csv"
REQUIRED_COLUMNS = [
    "Date",
    "Location",
    "MinTemp",
    "MaxTemp",
    "Rainfall",
    "RainTomorrow",
]


def validate_data():
    """Validates the raw weather data file."""
    if not os.path.exists(DATA_PATH):
        logging.error(f"File not found: {DATA_PATH}")
        sys.exit(1)

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        logging.error(f"Failed to read CSV: {e}")
        sys.exit(1)

    if df.empty:
        logging.error("The dataset is empty.")
        sys.exit(1)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        logging.error(f"Missing required columns: {missing_cols}")
        sys.exit(1)

    # Basic Health Checks
    if len(df) < 100:
        logging.warning(f"Dataset is very small ({len(df)} rows). Is this expected?")

    # Null Check for critical columns
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    if null_counts.sum() > 0:
        logging.info(f"Null values found in critical columns:\n{null_counts}")
        # preventing total failure if nulls are expected, but good to log.
        # Strict validation:
        # if null_counts['Date'] > 0: logging.error("Dates missing"); sys.exit(1)

    logging.info(f"Validation successful. {len(df)} rows processed.")


if __name__ == "__main__":
    validate_data()
