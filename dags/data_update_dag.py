from datetime import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.bash import BashOperator

# Define the dataset
# This URI is a logical identifier. It doesn't have to perfectly match a physical path,
# but it's good practice. Use consistent URIs across DAGs.
weather_dataset = Dataset("file:///data/raw/weatherAUS.csv")

with DAG(
    dag_id="data_update_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",  # This DAG runs on a schedule (e.g., checks for new data daily)
    catchup=False,
    tags=["mlops", "data_eng"],
) as dag:
    # Task to simulate fetching new data
    # In a real scenario, this might run 'python src/data/fetch_new_data.py'
    # or 'dvc pull' if the data is updated externally.
    fetch_new_data = BashOperator(
        task_id="fetch_new_data",
        bash_command="echo 'Fetching new data...' && sleep 5 && echo 'Data updated!'",
        outlets=[weather_dataset],  # CRITICAL: This tells Airflow this task updates the dataset
    )
