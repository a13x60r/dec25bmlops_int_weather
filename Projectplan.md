:bar_chart: Project Plan: MLOps Roadmap
Phase 0: Kick-off: Before November 14th 

* :bookmark_tabs: Kick-Off Slides: https://docs.google.com/presentation/d/1qIjvUaZMwHl6vvmQfJErMwcwCs4BbyHja6v9Lk4RBWQ/edit#slide=id.g31a2ff139c2_0_0

Phase 1: Foundations :date: Deadline: Jan 2

* Define project objectives and key metrics
* Set up a reproducible development environment
* Collect and preprocess data
    * Create a database (SQL or noSQL)
    * Store the data with a one-time run python script
* Build and evaluate a baseline ML model
    * Create 2 python scripts (training.py & predict.py)
* Implement a basic inference API
    * Create 2 endpoints (training/ & predict/)

Phase 2: Microservices, Tracking & Versioning :date: Deadline: Jan 10

* Set up experiment tracking with MLflow
    * Add MLFLow log code in the training script
* Implement data & model versioning with MLflow Registery
    * Compare performance after each retrain and flag the best model in MLflow
    * At the end of the training script (or later in Airflow, see chart n°1), load the previous version and compare to the new trained version

Phase 3: Orchestration & Deployment :date: Deadline: Jan 16

* Decompose the application into Docker microservices and design a simple orchestration with docker-compose
* Implement unit tests (it's enough to create a few example cases for CICD testing purposes)
* Create CI/CD pipeline with Github Actions:
    * ci.yaml → Linter + Unit Tests + Build Docker images
    * release.yaml →Linter + Unit Tests + Build Docker images + Deploy Docker images on DockerHub
* Optimize and secure the API
    * Basic Auth or OAuth2
* (OPTIONAL) Implement scalability with Kubernetes

Phase 4: Monitoring & Maintenance :date: Deadline: Jan 23

* Develop automated model and components updates with:
    *  Scheduled retraining: a cron script or Jenkins/Airlfow (more complex)
    * Triggered retraining: Graphana or Evidenlty webhook
* Implement drift detection with Evidently
* Set up performance monitoring using Prometheus/Grafana
* Finalize technical documentation in the repo

Phase 5: Frontend :date: Deadline: Jan 30

* Create a simple Streamlit application to interact with your API and make predictions

:microphone: Final Presentation (Defense):  February 6th

* Plan:
    * 15-minutes presentation
        * Explain the progress of your project
        * Explain the architecture chosen when organising the data
    * 5-minutes demonstration
        * Show that the application is functional
    * 10-minutes Q&A with the jury
* You can make the full presentation on the Streamlit application directly instead of slides.
* Every member must talk during the presentation.

