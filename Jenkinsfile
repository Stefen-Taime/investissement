pipeline {
    agent any

    stages {
        stage('Initialization') {
            steps {
                echo 'Starting the Pipeline'
            }
        }

        stage('Clone Repo') {
            steps {
               
                git(credentialsId: 'ops', url: 'https://github.com/Stefen-Taime/investissement.git', branch: 'feature/01/buildRacineProject')
            }
        }

        stage('Tests') {
            steps {
                script {
                    sh '''
                    set -e
                    [ -f infra/investment/pipelines/AAPL.csv ] || { echo "AAPL.csv missing"; exit 1; }
                    [ -f infra/investment/pipelines/AMZN.csv ] || { echo "AMZN.csv missing"; exit 1; }
                    [ -f infra/investment/pipelines/GOOG.csv ] || { echo "GOOG.csv missing"; exit 1; }
                    [ -f infra/investment/pipelines/MSFT.csv ] || { echo "MSFT.csv missing"; exit 1; }
                    [ -f infra/investment/pipelines/ORCL.csv ] || { echo "ORCL.csv missing"; exit 1; }
                    echo "All CSV files are present."
                    '''
                }
            }
        }

        stage('Deployment') {
            steps {
                script {
                    // Replace this with your actual deployment command
                    sh 'echo "Deployment command here"'
                }
            }
        }
    }

    post {
        always {
            echo 'Post-build cleanup'
        }
        success {
            echo 'Build Successful!'
        }
        failure {
            echo 'Build Failed!'
        }
    }
}
