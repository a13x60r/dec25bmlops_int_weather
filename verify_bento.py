from pathlib import Path

import pandas as pd
import requests


def verify():
    url = "http://127.0.0.1:3000/predict"

    # Load real sample data
    try:
        csv_path = Path("data/training_data_splits_by_year/split_01_2008/X_train.csv")
        if csv_path.exists():
            print(f"Loading sample from {csv_path}")
            df = pd.read_csv(csv_path, nrows=1)
            # Drop target if present? No, X_train usually doesn't have target.
            # Looking at file view, 'RainToday' is there?
            # View output showed: MinTemp...RainToday...Year
            # Wait, X_train usually implies features only. But typically 'RainTomorrow' is target. 'RainToday' is a feature.
            # Let's assume all columns in X_train are features.

            sample_data = df.iloc[0].to_dict()
            # Convert numpy types to native python for JSON serialization
            for k, v in sample_data.items():
                if hasattr(v, "item"):
                    sample_data[k] = v.item()

            data = {"input_data": sample_data}
        else:
            print("CSV not found, using dummy dict (may fail)")
            data = {"input_data": {f"feature_{i}": 0.5 for i in range(110)}}
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("Verification SUCCESS")
        else:
            print("Verification FAILED")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    verify()
