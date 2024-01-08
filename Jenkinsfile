pipeline {
    agent any

    environment {
        GIT_REPO_URL = 'https://github.com/Stefen-Taime/investissement.git'
        GIT_CREDENTIALS = 'ops'
        MINIO_ALIAS = 'minio'
        MINIO_URL = 'http://minio:9000'
        MINIO_CREDENTIALS = 'minio'
        FEATURE_BRANCH = 'feature/01/buildRacineProject'
        ARTIFACT_NAME = "project-artifact-\${BRANCH_NAME}-\${BUILD_NUMBER}.tar.gz"
    }

    stages {
        stage('Initialization') {
            steps { echo 'Starting the Pipeline' }
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
    sh 'ls -la' // Pour lister les fichiers dans le répertoire courant
    def csvFiles = ['AAPL', 'AMZN', 'GOOG', 'MSFT', 'ORCL']
    csvFiles.each { file ->
        def command = "test -f infra/investment/pipelines/${file}.csv || { echo '${file}.csv missing in ' + pwd(); exit 1; }"
        sh command
    }
    echo "All CSV files are present."
}

    }
}



        stage('Prepare Artifact') {
            steps {
                sh "tar --exclude=\${ARTIFACT_NAME} -czvf \${ARTIFACT_NAME} ."
            }
        }

        stage('Upload to MinIO') {
            steps {
                withCredentials([usernamePassword(credentialsId: MINIO_CREDENTIALS, usernameVariable: 'MINIO_ACCESS_KEY', passwordVariable: 'MINIO_SECRET_KEY')]) {
                    sh "mc alias set \${MINIO_ALIAS} \${MINIO_URL} \${MINIO_ACCESS_KEY} \${MINIO_SECRET_KEY}"
                    sh "mc cp \${ARTIFACT_NAME} \${MINIO_ALIAS}/artifact/\${BRANCH_NAME}/"
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
                        git remote set-url origin https://\${GIT_USER}:\${GIT_PASS}@github.com/Stefen-Taime/investissement.git
                        echo "Pushing changes to remote..."
                        git push origin main
                    '''
                }
            }
        }

        stage('Deployment') {
            steps {
                echo "Deploying the application..."
                // Ajoutez ici vos étapes de déploiement spécifiques
            }
        }
    }

    post {
        always { echo 'Post-build cleanup' }
        success { echo 'Build Successful!' }
        failure { echo 'Build Failed!' }
    }
}
