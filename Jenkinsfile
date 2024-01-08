pipeline {
    agent any

    environment {
        GIT_REPO_URL = 'https://github.com/Stefen-Taime/investissement.git'
        GIT_CREDENTIALS = 'ops'
        MINIO_ALIAS = 'minio'
        MINIO_URL = 'http://minio:9000'
        MINIO_CREDENTIALS = 'minio'
        FEATURE_BRANCH = 'feature/01/buildRacineProject'
    }

    stages {
        stage('Initialization') {
            steps { 
                echo 'Starting the Pipeline' 
            }
        }

        stage('Clone Repo') {
            steps {
                git(credentialsId: GIT_CREDENTIALS, url: GIT_REPO_URL, branch: FEATURE_BRANCH)
            }
        }

        stage('Tests') {
            steps {
                script {
                    sh 'pwd'
                    sh 'ls -la' // List files in the current directory
                    def csvFiles = ['AAPL', 'AMZN', 'GOOG', 'MSFT', 'ORCL']
                    csvFiles.each { fileName ->
                        sh "if [ ! -f infra/investment/pipelines/${fileName}.csv ]; then echo '${fileName}.csv missing in ' \$(pwd); exit 1; fi"
                    }
                    echo "All CSV files are present."
                }
            }
        }

        stage('Prepare Artifact') {
            steps {
                script {
                    ARTIFACT_NAME = "project-artifact-${env.BRANCH_NAME}-${env.BUILD_NUMBER}.tar.gz"
                    sh "tar --exclude='.git' --exclude='some_other_directory' -czvf ${ARTIFACT_NAME} ."
                }
            }
        }

        stage('Upload to MinIO') {
            steps {
                withCredentials([usernamePassword(credentialsId: MINIO_CREDENTIALS, usernameVariable: 'MINIO_ACCESS_KEY', passwordVariable: 'MINIO_SECRET_KEY')]) {
                    script {
                        ARTIFACT_NAME = "project-artifact-${env.BRANCH_NAME}-${env.BUILD_NUMBER}.tar.gz"
                        sh "mc alias set ${MINIO_ALIAS} ${MINIO_URL} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}"
                        sh "mc cp ${ARTIFACT_NAME} ${MINIO_ALIAS}/artifact/${env.BRANCH_NAME}/"
                    }
                }
            }
        }

        stage('Checkout Main Branch') {
            steps {
                sh '''
                    echo "Checking out the main branch..."
                    git fetch --all
                    git checkout main
                    git pull origin main
                '''
            }
        }

        stage('Merge Feature into Main') {
    steps {
        withCredentials([usernamePassword(credentialsId: GIT_CREDENTIALS, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
            sh '''
                echo "Merging feature branch into main..."
                git merge \${FEATURE_BRANCH}
                echo "Configuring Git credentials..."
                git config --global user.email "stefentaime@gmail.com"
                git config --global user.name "Stefen-Taime"
                git remote set-url origin https://\${GIT_USER}:\${GIT_PASS}@github.com/Stefen-Taime/investissement.git
                git push origin main
            '''
        }
    }
}


        stage('Deployment') {
            steps {
                echo "Deploying the application..."
                // Add your specific deployment steps here
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
