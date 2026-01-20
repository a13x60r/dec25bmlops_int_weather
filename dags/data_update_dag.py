from datetime import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from utils.slack import send_slack_alert

weather_dataset = Dataset("file:///data/raw/weatherAUS.csv")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "on_failure_callback": send_slack_alert,
}

with DAG(
    dag_id="data_update_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["mlops", "data_eng"],
) as dag:
    # Run the fetch_weather_data.py script inside the container
    fetch_new_data = DockerOperator(
        task_id="fetch_weather_api",
        image="dec25bmlops_int_weather-trainer:latest",
        api_version="auto",
        auto_remove=True,
        # Re-installing requests just in case (though we added it to requirements, image rebuild might be pending in some contexts)
        # Actually we rebuilt the image in step 339, so requests should be there.
        command='bash -lc "python src/data/fetch_weather_data.py"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=[
            Mount(
                source="C:/Users/aboro/Documents/dataScientist/dec25bmlops_int_weather",
                target="/workspace",
                type="bind",
            ),
        ],
        environment={
            "OPENWEATHER_API_KEY": "{{ var.value.OPENWEATHER_API_KEY }}",
            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
        },
    )

    validate_data = DockerOperator(
        task_id="validate_data",
        image="dec25bmlops_int_weather-trainer:latest",
        api_version="auto",
        auto_remove=True,
        command='bash -lc "python src/data/validate_data.py"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=[
            Mount(
                source="C:/Users/aboro/Documents/dataScientist/dec25bmlops_int_weather",
                target="/workspace",
                type="bind",
            ),
        ],
        outlets=[weather_dataset],
    )

    fetch_new_data >> validate_data
