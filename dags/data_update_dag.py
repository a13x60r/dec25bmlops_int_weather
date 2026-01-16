from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.datasets import Dataset
from docker.types import Mount
import os

weather_dataset = Dataset("file:///data/raw/weatherAUS.csv")

with DAG(
    dag_id="data_update_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=['mlops', 'data_eng'],
) as dag:

    # Run the fetch_weather_data.py script inside the container
    fetch_new_data = DockerOperator(
        task_id="fetch_weather_api",
        image='dec25bmlops_int_weather-trainer:latest',
        api_version='auto',
        auto_remove=True,
        # Re-installing requests just in case (though we added it to requirements, image rebuild might be pending in some contexts)
        # Actually we rebuilt the image in step 339, so requests should be there.
        command='bash -lc "python src/data/fetch_weather_data.py"',
        docker_url="unix://var/run/docker.sock",
        network_mode="dec25bmlops_int_weather_default",
        mounts=[
            Mount(source='C:/Users/aboro/Documents/dataScientist/dec25bmlops_int_weather', target='/workspace', type='bind'),
        ],
        environment={
            'OPENWEATHER_API_KEY': os.getenv("OPENWEATHER_API_KEY", "2382ead9008d54d34ff156b1bbe44f6d"),
            'MLFLOW_TRACKING_URI': 'http://mlflow:5000',
        },
        outlets=[weather_dataset]
    )
