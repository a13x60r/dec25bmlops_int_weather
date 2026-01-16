pipeline {
  agent any

  options {
    skipDefaultCheckout(true)
  }

  parameters {
    string(name: 'GIT_REPO_URL', defaultValue: 'https://github.com/a13x60r/dec25bmlops_int_weather.git', description: 'Git repository HTTPS/SSH URL')
    string(name: 'GIT_BRANCH', defaultValue: 'master', description: 'Branch to build (e.g., main, develop)')
    // string(name: 'GIT_CREDENTIALS_ID', defaultValue: '', description: 'Optional Jenkins credentialsId for repo access')
  }

  environment {
    IMAGE_TAG = "weather-au-mlops:${BUILD_NUMBER}"
    DEV_IMAGE_TAG = "weather-au-mlops-dev:${BUILD_NUMBER}"
  }

  stages {
    
    stage('Checkout') {
        steps {
            script {
            def repo = 'https://github.com/a13x60r/dec25bmlops_int_weather.git'
            def preferred = (params.GIT_BRANCH?.trim()) ? params.GIT_BRANCH.trim() : 'master'

            def remoteHeads = sh(script: "git ls-remote --heads ${repo}", returnStdout: true).trim()
            def branchToBuild = remoteHeads.contains("refs/heads/${preferred}") ? preferred :
                                (remoteHeads.contains("refs/heads/main") ? 'main' : 'master')

            checkout([$class: 'GitSCM',
                branches: [[name: "*/${branchToBuild}"]],
                userRemoteConfigs: [[url: repo]],
                extensions: [[$class: 'CleanBeforeCheckout'], [$class: 'PruneStaleBranch']]
            ])
            echo "Checked out branch: ${branchToBuild}"
            }
        }
    }
}

    stage('Build DEV Image') {
      steps {
        sh "docker build -f Dockerfile.dev -t ${DEV_IMAGE_TAG} ."
      }
    }

    stage('Lint') {
      steps {
        sh "docker run --rm ${DEV_IMAGE_TAG} ruff check ."
      }
    }

    stage('Test') {
      steps {
        sh "docker run --rm ${DEV_IMAGE_TAG} pytest"
      }
    }

    stage('Cleanup') {
      steps {
        sh "docker rmi ${DEV_IMAGE_TAG} || true"
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }
}
