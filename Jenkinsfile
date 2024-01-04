pipeline {
    agent any  // Defines on which Jenkins agent/node the pipeline will run

    stages {
        stage('Initialization') {
            steps {
                // Commands to initialize your build
                echo 'Starting the Pipeline'
            }
        }
        stage('Clone Repo') {
            steps {
                git(credentialsId: 'github-access-buildracineproject', url: 'https://github.com/Stefen-Taime/investissement.git')
            }
        }

       
        stage('Tests') {
            steps {
                script {
                    // Vérifier l'existence des fichiers CSV
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
                // Commands to deploy your application
                script {
                    // Replace this with your deployment command
                    sh 'echo "Deployment command here"'
                }
            }
        }
    }
    post {
        always {
            // Actions to perform after executing the stages, regardless of the outcome
            echo 'Post-build cleanup'
        }
        success {
            // Specific actions to perform if the pipeline is successful
            echo 'Build Successful!'
        }
        failure {
            // Specific actions to perform in case of pipeline failure
            echo 'Build Failed!'
        }
    }
}
