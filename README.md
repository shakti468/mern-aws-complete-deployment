
# Sample MERN with Microservices - Deployment Journey 🚀

This repository is a fork of [UnpredictablePrashant/SampleMERNwithMicroservices](https://github.com/UnpredictablePrashant/SampleMERNwithMicroservices).  
The goal is to deploy the MERN application (with microservices) on AWS using Docker, ECR, Jenkins, Boto3, and EKS.

---

## 📂 Repository Structure
```bash
SampleMERNwithMicroservices/
│
├── backend/
│ ├── helloService/ # Microservice 1 (PORT=3001)
│ └── profileService/ # Microservice 2 (PORT=3002 + MongoDB)
│
├── frontend/ # React frontend app
│
├── docker-compose.yml # To run full stack locally
├── README.md # Documentation (this file)
```
## Add upstream to pull future updates:
```bash
git remote add upstream https://github.com/UnpredictablePrashant/SampleMERNwithMicroservices.git
git fetch upstream
```
# AWS Environment Setup

## Install and verify AWS CLI
```bash
aws --version
```
## Configure IAM Credentials
```bash
aws configure
```

# Containerize the MERN Application

## Dockerfiles

### backend/helloService/Dockerfile
```bash
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```
### backend/profileService/Dockerfile
```bash
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3002
CMD ["npm", "start"]
```

### frontend/Dockerfile
```bash
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Build Docker Images
```bash
# helloService
docker build -t hello-service:latest ./backend/helloService

# profileService
docker build -t profile-service:latest ./backend/profileService

# frontend
docker build -t mern-frontend:latest ./frontend
```

## Run Containers Individually
```bash
# helloService
docker run -d -p 3001:3001 --name hello hello-service:latest

# profileService (with MongoDB URL)
docker run -d -p 3002:3002 \
  -e MONGO_URL="mongodb://host.docker.internal:27017/testdb" \
  --name profile profile-service:latest

# frontend
docker run -d -p 8080:80 --name frontend mern-frontend:latest
```

### Screenshot: docker ps output
<img width="1377" height="150" alt="image" src="https://github.com/user-attachments/assets/460fafe8-60c0-4345-9e3b-7234530ec61b" />

-----

### Screenshot: http://localhost:8080 running frontend
<img width="1505" height="602" alt="image" src="https://github.com/user-attachments/assets/3c47284e-3a2a-4949-ae56-ca4c2ed61a20" />

------


# Push Docker Images to Amazon ECR

## Create ECR Repositories

### Screenshots
<img width="1518" height="301" alt="image" src="https://github.com/user-attachments/assets/67aa2f2c-8976-4480-b72e-bf63b5e72cf6" />


-----

## Authenticate Docker with ECR
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.ap-south-1.amazonaws.com

```

## Tag and Push Docker Images
### hello-service
```bash
docker tag hello-service:latest 975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-hello-service:latest

docker push 975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-hello-service:latest
The push refers to repository [975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-hello-service]
```
### Verify Images in AWS Console

<img width="1061" height="593" alt="image" src="https://github.com/user-attachments/assets/ab155019-ad3f-4088-802e-c422b85e2d3d" />

---
### profile-service
```bash
docker tag profile-service:latest 975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-profile-service:latest
     
docker push 975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-profile-service:latest
The push refers to repository [975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-profile-service]
```

### Verify Images in AWS Console
<img width="1123" height="611" alt="image" src="https://github.com/user-attachments/assets/efd9ff09-bf53-4dea-bafc-ac33ba0712e7" />

----

### mern-frontend
```bash
docker tag mern-frontend:latest 975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-mern-frontend:latest

docker push 975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-mern-frontend:latest
The push refers to repository [975050024946.dkr.ecr.ap-south-1.amazonaws.com/shakti-mern-frontend]
```
### Verify Images in AWS Console
<img width="1172" height="613" alt="image" src="https://github.com/user-attachments/assets/96e574a5-41c2-4d18-a189-03b4becf43ce" />

------

# CI Pipeline with Jenkins for MERN Microservices

This explains how Jenkins is used to automate the build and push process
for the **Sample MERN with Microservices** project.

---

## 📌 Overview

Instead of manually building Docker images and pushing them to Amazon ECR, Jenkins
automates the entire workflow:

1. Clone the GitHub repository
2. Build Docker images for:
   - Hello Service
   - Profile Service
   - Frontend
3. Authenticate with Amazon ECR
4. Push Docker images to ECR repositories

This ensures **consistency, automation, and scalability** across all builds.

---

## 🛠 Setup Steps

### 1. Launch EC2 for Jenkins
- Use Ubuntu 22.04
- Install Jenkins + Java + Docker
- Open ports:
  - `8080` → Jenkins UI
  - `22` → SSH
 
  ### Screenshots
  <img width="1417" height="876" alt="image" src="https://github.com/user-attachments/assets/1f8236a6-6d5f-412a-80e2-5ed650f3904e" />


### 2. Configure Jenkins
- Install required plugins:
  - **GitHub**
  - **Pipeline**
  - **Docker Pipeline**
  - **Amazon ECR**
  - **AWS Credentials**
- Add AWS credentials under **Manage Jenkins → Credentials**

### 3. Jenkins Pipeline
A `Jenkinsfile` in the repo defines the pipeline:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') { ... }
        stage('Build Docker Images') { ... }
        stage('Login to ECR') { ... }
        stage('Tag & Push to ECR') { ... }
    }
}
```

# Run the Pipeline
<img width="1591" height="960" alt="image" src="https://github.com/user-attachments/assets/55894486-ee88-4a0d-b9c1-4c56b599309a" />

<img width="1238" height="751" alt="image" src="https://github.com/user-attachments/assets/3f5d82ee-4106-41bf-bcd4-3ba65970964d" />

------




