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

        stage('Prepare Artifact') {
            steps {
                script {
                    sh 'echo "Zipping the project..."'
                    sh 'tar -czvf project-artifact.tar.gz .'
                }
            }
        }

      

        stage('Merge to Main/Master') {
    steps {
        script {
            sh 'echo "Fetching all branches..."'
            sh 'git fetch --all'
            
            sh 'echo "Checking out the main branch..."'
            sh 'git checkout main || git checkout master'

            sh 'echo "Merging feature branch into main/master..."'
            sh 'git merge ${BRANCH_NAME}'

            sh 'echo "Pushing to remote..."'
            sh 'git push origin main || git push origin master'
        }
    }
}


        stage('Deployment') {
            steps {
                script {
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
