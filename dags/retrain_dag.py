from datetime import datetime, timedelta

from airflow import DAG
from airflow.datasets import Dataset
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# Import Slack helper
from utils.slack import send_slack_alert

# Define the SAME dataset URI as the producer
weather_dataset = Dataset("file:///data/raw/weatherAUS.csv")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": send_slack_alert,
}

# Common environment for all DVC tasks
DOCKER_ENV = {
    "MLFLOW_TRACKING_URI": "http://mlflow:5000",
    "MLFLOW_S3_ENDPOINT_URL": "http://minio:9000",
    "AWS_ACCESS_KEY_ID": "minio",
    "AWS_SECRET_ACCESS_KEY": "minio12345",
    "AWS_DEFAULT_REGION": "us-east-1",
    "DAGSHUB_USERNAME": "{{ var.value.DAGSHUB_USERNAME }}",
    "DAGSHUB_TOKEN": "{{ var.value.DAGSHUB_TOKEN }}",
}

# Common Mounts
DOCKER_MOUNTS = [
    Mount(
        source="C:/Users/aboro/Documents/dataScientist/dec25bmlops_int_weather",
        target="/workspace",
        type="bind",
    ),
]

with DAG(
    "weather_retrain_pipeline",
    default_args=default_args,
    description="Retrain model using DVC pipeline (Decomposed)",
    schedule=[weather_dataset],
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["mlops", "training"],
) as dag:
    # 1. Preprocess Data
    preprocess_data = DockerOperator(
        task_id="preprocess_data",
        image="dec25bmlops_int_weather-trainer:latest",
        api_version="auto",
        auto_remove=True,
        # Configure remote -> repro 'process' stage -> push local changes (if any)
        # Note: We must config remote every time because container is ephemeral/stateless
        command='bash -lc "dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc repro process"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=DOCKER_MOUNTS,
        environment=DOCKER_ENV,
    )

    # 2. Prepare Splits
    prepare_splits = DockerOperator(
        task_id="prepare_splits",
        image="dec25bmlops_int_weather-trainer:latest",
        api_version="auto",
        auto_remove=True,
        command='bash -lc "dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc repro prepare_splits"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=DOCKER_MOUNTS,
        environment=DOCKER_ENV,
    )

    # 3. Train Model
    train_model = DockerOperator(
        task_id="train_model",
        image="dec25bmlops_int_weather-trainer:latest",
        api_version="auto",
        auto_remove=True,
        # repro train -> push results to DagsHub
        command='bash -lc "dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc repro train && dvc push"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=DOCKER_MOUNTS,
        environment=DOCKER_ENV,
    )

    # Define Dependency Chain
    preprocess_data >> prepare_splits >> train_model
