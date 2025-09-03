pipeline {
    agent any

    environment {
        AWS_REGION = "ap-south-1"
        AWS_ACCOUNT_ID = "975050024946"   // replace with your AWS account ID
        IMAGE_HELLO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/hello-service"
        IMAGE_PROFILE = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/profile-service"
        IMAGE_FRONTEND = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/mern-frontend"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/shakti468/mern-aws-complete-deployment.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    sh 'docker build -t hello-service ./backend/helloService'
                    sh 'docker build -t profile-service ./backend/profileService'
                    sh 'docker build -t mern-frontend ./frontend'
                }
            }
        }

        stage('Login to ECR') {
            steps {
                    script {
                        sh """
                        aws ecr get-login-password --region ${AWS_REGION} \
                        | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                        """
                    }
            }
        }

        stage('Tag & Push to ECR') {
            steps {
                script {
                    sh """
                    docker tag hello-service:latest $IMAGE_HELLO:latest
                    docker push $IMAGE_HELLO:latest

                    docker tag profile-service:latest $IMAGE_PROFILE:latest
                    docker push $IMAGE_PROFILE:latest

                    docker tag mern-frontend:latest $IMAGE_FRONTEND:latest
                    docker push $IMAGE_FRONTEND:latest
                    """
                }
            }
        }
    }
}
