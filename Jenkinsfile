pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'                // Set your AWS region
        AWS_ACCESS_KEY_ID = credentials('aws_access_key_id')  // Set your AWS access key ID (Jenkins credentials)
        AWS_SECRET_ACCESS_KEY = credentials('aws_secret_access_key')  // Set your AWS secret key (Jenkins credentials)
        AWS_DEFAULT_REGION = 'us-east-1'         // AWS default region (can be overridden per stage)
        S3_BUCKET_NAME = 'my-bucket-name'        // Replace with your S3 bucket name
        VENV_DIR = '.venv'                       // Virtual environment directory
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checkout Code"
                // Checkout from your Git repository
                git 'https://github.com/your-repo/aws-python-project.git'  // Replace with your Git repository
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing dependencies"
                script {
                    // Create a virtual environment if it doesn't exist
                    if (!fileExists(VENV_DIR)) {
                        sh 'python3 -m venv ${VENV_DIR}'
                    }
                    // Install dependencies
                    sh 'source ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running Tests"
                script {
                    // Run tests using pytest or your preferred testing framework
                    sh 'source ${VENV_DIR}/bin/activate && pytest --maxfail=1 --disable-warnings -q'
                }
            }
        }

        stage('Deploy to AWS') {
            steps {
                echo "Deploying to AWS"
                script {
                    // Example: Deploy to S3 or trigger other AWS-related operations
                    // Upload code to an S3 bucket as an example
                    sh '''
                        source ${VENV_DIR}/bin/activate
                        aws s3 sync . s3://${S3_BUCKET_NAME}/ --exclude ".git/*" --exclude "*.pyc" --delete
                    '''
                }
            }
        }

        stage('Notify') {
            steps {
                echo "Sending Notification"
                // Example: Notify on successful deployment
                script {
                    // You can integrate an SNS or email notification here
                    // Example: send an email notification
                    mail to: 'devops@example.com', subject: 'Deployment Success', body: 'Deployment to AWS was successful.'
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up"
            // Cleanup any resources or environments
            sh 'deactivate || true'
        }

        success {
            echo "Pipeline succeeded!"
        }

        failure {
            echo "Pipeline failed!"
        }
    }
}
