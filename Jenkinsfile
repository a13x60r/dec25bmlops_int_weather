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

        stage('Update Dataset') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . venv/bin/activate
                        python -c "import yaml; params = yaml.safe_load(open('params.yaml')); params['data']['split_id'] = params['data'].get('split_id', 1) + 1; yaml.dump(params, open('params.yaml', 'w'))"
                        cat params.yaml
                        """
                    } else {
                        bat """
                        call venv\\Scripts\\activate
                        python -c "import yaml; params = yaml.safe_load(open('params.yaml')); params['data']['split_id'] = params['data'].get('split_id', 1) + 1; yaml.dump(params, open('params.yaml', 'w'))"
                        type params.yaml
                        """
                    }
                }
            }
        }

        stage('Reproduce Pipeline') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . venv/bin/activate
                        dvc repro
                        """
                    } else {
                        bat """
                        call venv\\Scripts\\activate
                        dvc repro
                        """
                    }
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'models/*.pkl, metrics.json, params.yaml', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
