pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install dvc
                        """
                    } else {
                        bat """
                        python -m venv venv
                        call venv\\Scripts\\activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install dvc
                        """
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . venv/bin/activate
                        pytest
                        """
                    } else {
                        bat """
                        call venv\\Scripts\\activate
                        pytest
                        """
                    }
                }
            }
        }

        stage('Build Bento') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . venv/bin/activate
                        bentoml build
                        """
                    } else {
                        bat """
                        call venv\\Scripts\\activate
                        bentoml build
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
