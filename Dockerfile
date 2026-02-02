FROM python:3.11.7-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src ./src
COPY pyproject.toml .
COPY params.yaml dvc.yaml dvc.lock ./
COPY .dvc ./.dvc
COPY data/raw/weatherAUS.csv.dvc data/raw/weatherAUS.csv.dvc
COPY tests ./tests

RUN mkdir -p /app/data/raw

CMD ["python", "-m", "weather_au_mlops.train"]
