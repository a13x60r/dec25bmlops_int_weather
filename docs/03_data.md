# Data

## Dataset provenance and format
- Primary dataset is the Australian weather dataset (`weatherAUS.csv`) managed by DVC.
- Live updates can be fetched from OpenWeatherMap into `data/raw/weatherAUS.csv` via the ingestion script.

Evidence
```text
# data/raw/weatherAUS.csv.dvc
outs:
- md5: 88b31ee88a6309f992051db3dbecfc78
  size: 14098872
  path: weatherAUS.csv
```
```text
# src/data/fetch_weather_data.py
API_KEY = os.getenv("OPENWEATHER_API_KEY")
DATA_PATH = "data/raw/weatherAUS.csv"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
```

## Data versioning with DVC
- DVC is configured with an `origin` remote using S3/MinIO (`s3://dvc`).
- Pipeline stages are defined in `dvc.yaml` and locked in `dvc.lock`.
- Repo includes `.dvc/` metadata and `data.dvc.backup` for DVC state.

Evidence
```text
# .dvc/config
[core]
    autostage = true
    remote = origin
[remote "origin"]
    url = s3://dvc
```
```text
# ls -la (excerpt)
drwxr-xr-x 1 aboro 197609     0 Jan 30 19:10 .dvc
-rw-r--r-- 1 aboro 197609   110 Jan 30 14:24 data.dvc.backup
drwxr-xr-x 1 aboro 197609     0 Jan 30 19:10 data
```
```text
$ cat dvc.yaml
stages:
  process:
    cmd: python src/data/preprocess.py
    deps:
      - src/data/preprocess.py
      - data/raw/weatherAUS.csv
      - params.yaml
    outs:
      - data/processed
      - data/interim/df_preprocessed.csv
      - models/preprocessor.pkl

  prepare_splits:
    cmd: python src/data/training_data_splits_by_year.py
    deps:
      - src/data/training_data_splits_by_year.py
      - data/processed
      - params.yaml
    outs:
      - data/training_data_splits_by_year

  train:
    cmd: python src/models/train_model.py
    deps:
      - src/models/train_model.py
      - data/training_data_splits_by_year
      - params.yaml
    outs:
      - models/xgboost_model.pkl
```
```text
# dvc.lock (excerpt)
stages:
  process:
    deps:
    - path: data/raw/weatherAUS.csv
      md5: 88b31ee88a6309f992051db3dbecfc78
    outs:
    - path: data/interim/df_preprocessed.csv
      md5: 9e62f566c399452c7efac3ed4d92348a
    - path: data/processed
      md5: 1e1db19afe9bbaedd7698f560fb65866.dir
  prepare_splits:
    outs:
    - path: data/training_data_splits_by_year
      md5: b600b0f56bf44523a0dd09f6b7886e78.dir
  train:
    outs:
    - path: models/xgboost_model.pkl
      md5: b8736cefb8b0adb1fc74918f4c96a9c9
```

## Data splits and features
- Preprocessing engineers `Year` and `Season`, imputes missing values, one-hot encodes categorical fields, and scales numeric features.
- Training splits are cumulative by year (2008-2016) with a fixed test set.

Feature table (from preprocessing)
- Numeric: `MinTemp`, `MaxTemp`, `Rainfall`, `WindGustSpeed`, `WindSpeed9am`, `WindSpeed3pm`, `Humidity9am`, `Humidity3pm`, `Pressure9am`, `Pressure3pm`, `Temp9am`, `Temp3pm`
- Categorical (OHE): `Location`, `WindGustDir`, `WindDir9am`, `WindDir3pm`, `Season`
- Engineered: `Year`
- Target: `RainTomorrow`

Evidence
```text
# src/data/preprocess.py
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Season"] = df["Month"].apply(get_season_aus)
df = df.drop(["Date", "Month"], axis=1)
df["RainTomorrow"] = df["RainTomorrow"].map({"No": 0, "Yes": 1})
df["RainToday"] = df["RainToday"].map({"No": 0, "Yes": 1})
numeric_cols = [
    "MinTemp",
    "MaxTemp",
    "Rainfall",
    "WindGustSpeed",
    "WindSpeed9am",
    "WindSpeed3pm",
    "Humidity9am",
    "Humidity3pm",
    "Pressure9am",
    "Pressure3pm",
    "Temp9am",
    "Temp3pm",
]
categorical_cols_encoding = ["Location", "WindGustDir", "WindDir9am", "WindDir3pm", "Season"]
```
```text
# src/data/training_data_splits_by_year.py
metadata = {
    "split_method": "cumulative_by_year",
    "years_available": [int(y) for y in years_available],
}
for i, end_year in enumerate(years_available, 1):
    split_dir = splits_dir / f"split_{i:02d}_{split_name}"
    X_train_split.to_csv(split_dir / "X_train.csv", index=False)
    y_train_split.to_csv(split_dir / "y_train.csv", index=False)
    X_test_fixed.to_csv(split_dir / "X_test.csv", index=False)
    y_test_fixed.to_csv(split_dir / "y_test.csv", index=False)
```

## Data validation status
- A lightweight validation script checks required columns and basic dataset health.

Evidence
```text
# src/data/validate_data.py
REQUIRED_COLUMNS = [
    "Date",
    "Location",
    "MinTemp",
    "MaxTemp",
    "Rainfall",
    "RainTomorrow",
]
if df.empty:
    logging.error("The dataset is empty.")
if missing_cols:
    logging.error(f"Missing required columns: {missing_cols}")
```

Status: Not present in repo
- Formal schema validation or data quality checks (e.g., Great Expectations, pandera, or TensorFlow Data Validation).

Expected in mature setup
- Schema registry with type/range checks and automated report artifacts per DVC run.

Actionable recommendations
- Add a `data_validation` DVC stage and fail the pipeline on schema violations.
- Store validation reports under `reports/` and log them to MLflow as artifacts.
- Add unit tests that assert expected columns and distribution ranges for critical features.
