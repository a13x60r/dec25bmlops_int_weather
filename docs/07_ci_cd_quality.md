# CI/CD and Quality

## CI workflows
- CI pipeline runs on PRs to `master`, installs dependencies, configures DVC, runs Ruff, pulls data, runs pytest, and builds a Bento.

Evidence
```text
$ ls -la .github/workflows
total 12
drwxr-xr-x 1 aboro 197609    0 Jan 30 14:24 .
drwxr-xr-x 1 aboro 197609    0 Jan 30 14:24 ..
-rw-r--r-- 1 aboro 197609 2782 Feb  2 10:45 ci.yml
-rw-r--r-- 1 aboro 197609 4627 Jan 30 14:24 release.yml
```
```text
# .github/workflows/ci.yml (excerpt)
on:
  pull_request:
    branches: [ "master" ]

steps:
  - name: Install dependencies
    run: |
      pip install ruff pytest
      if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      pip install dvc dvc-s3
  - name: Configure DVC
    run: |
      dvc remote modify --local origin url https://dagshub.com/a13x60r/dec25bmlops_int_weather.dvc
  - name: Lint with Ruff
    run: |
      ruff check .
      ruff format --check .
  - name: Pull data
    run: |
      dvc pull
  - name: Test with pytest
    run: |
      pytest
  - name: Build Bento
    run: |
      bentoml build
```

## Release pipeline
- Release builds Docker images and containerizes Bento service, pushing to Docker Hub and GHCR.

Evidence
```text
# .github/workflows/release.yml (excerpt)
on:
  push:
    branches: [ "master" ]
    tags: [ 'v*.*.*' ]

steps:
  - name: Build and push Docker image
    uses: docker/build-push-action@v4
  - name: Build and Push BentoML Service
    run: |
      bentoml build
      bentoml containerize rain_prediction_service:latest \
        --image-tag "$DOCKER_TAG" \
        --image-tag "$GHCR_TAG"
```

## Linting, formatting, and tests
- Ruff is configured with a 100-char line length; pytest runs tests in `tests/`.
- Pre-commit enforces Ruff, formatting, and DVC hooks.

Evidence
```text
# ruff.toml
line-length = 100
[lint]
select = ["E", "F", "I", "B", "UP"]
```
```text
# pytest.ini
[pytest]
testpaths = tests
addopts = -q
```
```text
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format
  - repo: local
    hooks:
      - id: pytest
        entry: pytest
  - repo: https://github.com/iterative/dvc
    hooks:
      - id: dvc-pre-commit
      - id: dvc-pre-push
```

## Jenkins pipeline
- Jenkinsfile runs tests and builds Bento in a separate CI channel.

Evidence
```text
# Jenkinsfile (excerpt)
stage('Run Tests') {
  steps {
    sh """
    . venv/bin/activate
    pytest
    """
  }
}
stage('Build Bento') {
  steps {
    sh """
    . venv/bin/activate
    bentoml build
    """
  }
}
```
