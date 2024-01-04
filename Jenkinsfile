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
                // Step to clone the Git repository
                git url: 'https://github.com/Stefen-Taime/investissement.git'
            }
        }
        stage('Build') {
            steps {
                // Commands to build your project
                // For example, for a Java project, you might use Maven or Gradle
                script {
                    // Replace this with your build command
                    sh 'echo "Build command here"'
                }
            }
        }
        stage('Tests') {
            steps {
                // Commands to run tests
                script {
                    // Replace this with your command to run tests
                    sh 'echo "Command to run tests here"'
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
