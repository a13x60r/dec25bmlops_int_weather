from datetime import datetime, timedelta

from airflow import DAG
from airflow.datasets import Dataset
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# Define the SAME dataset URI as the producer
weather_dataset = Dataset("file:///data/raw/weatherAUS.csv")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "weather_retrain_pipeline",
    default_args=default_args,
    description="Retrain model using DVC pipeline",
    schedule=[weather_dataset],  # Trigger when weather_dataset is updated
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["mlops", "training"],
) as dag:
    # Task: Run dvc repro inside a container
    # We use the same image as the 'trainer' service in docker-compose
    # Note: Ensure you have built the image locally with `docker compose build`
    retrain_model = DockerOperator(
        task_id="retrain_model",
        image="dec25bmlops_int_weather-trainer:latest",
        api_version="auto",
        auto_remove=True,
        command='bash -lc "dvc repro && dvc push"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=[
            # Host path must be exactly what the Docker Daemon sees (Windows format)
            Mount(
                source="C:/Users/aboro/Documents/dataScientist/dec25bmlops_int_weather",
                target="/workspace",
                type="bind",
            ),
        ],
        environment={
            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
            "MLFLOW_S3_ENDPOINT_URL": "http://minio:9000",
            "AWS_ACCESS_KEY_ID": "minio",
            "AWS_SECRET_ACCESS_KEY": "minio12345",
            "AWS_DEFAULT_REGION": "us-east-1",
            "DAGSHUB_USERNAME": "{{ var.value.DAGSHUB_USERNAME }}",
            "DAGSHUB_TOKEN": "{{ var.value.DAGSHUB_TOKEN }}",
        },
    )
