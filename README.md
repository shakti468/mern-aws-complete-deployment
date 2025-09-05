
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

# Infrastructure as Code (IaC) with Boto3

In this step, we automated the **AWS infrastructure setup** for our MERN microservices project using **Python (Boto3)**.  
Instead of manually creating resources from the AWS Console, we wrote a script (`infra_setup.py`) to provision everything.

---

## 🔹 What This Script Does
1. **Checks / Creates IAM Instance Profile**
   - IAM Role already existed (`shakti-jenkins-ec2-iam`).
   - Attached it to an **Instance Profile** (`shakti-jenkins-ec2-iam-profile`).

2. **Launch Template**
   - Defines EC2 instance configuration:
     - Ubuntu AMI
     - Instance type: `t3.micro`
     - SSH Key: `Shakti-b10`
     - Security Group: `sg-0e03c3accc395a435`
     - IAM Instance Profile attached
     - User Data script to install Docker and run app containers

3. **Auto Scaling Group (ASG)**
   - Ensures highly available backend.
   - Launches EC2 instances in the given Subnet(s).
   - Configured with min=1, max=3, desired=1.

---

## 🔹 Commands Used

### Run the Python Script
```bash
python3 infra_setup.py
```
### Output screenshot
<img width="1287" height="243" alt="image" src="https://github.com/user-attachments/assets/3f94b2dc-c26d-4885-8c62-13c7b99e42ec" />

## running mern app with vpc id, subnet id, IAM Role, Asg ,  
<img width="1703" height="825" alt="image" src="https://github.com/user-attachments/assets/183a0563-3828-4fd3-824a-9e07ee2cf42d" />
<img width="966" height="265" alt="image" src="https://github.com/user-attachments/assets/41b376a8-5968-4975-8bc2-cdc36577b4de" />


---------

# Deploying Backend Services on EC2 with Auto Scaling Group (ASG)
## Launch Template
- Created a Launch Template with:

- Base Amazon Linux 2 AMI.

- User Data script that:

- Installs Docker.

- Authenticates with Amazon ECR.

- Pulls backend Docker images.

- Runs the containers:

## Auto Scaling Group (ASG)

- Attached the Launch Template to an ASG for high availability.

- Configured:

- Min capacity = 1

- Max capacity = 3

- Health checks via EC2 status.

# Networking with Load Balancer & DNS

- In this step, we expose the services to the internet using an Application Load Balancer (ALB).

## Target Group

- Created a Target Group for backend services.

- Registered EC2 instances from the ASG.

- Configured health checks:

- Protocol: HTTP

- Port: 3001 (hello-service) / 3002 (profile-service)

- Path: /

# Application Load Balancer (ALB)

Created an ALB with:

Internet-facing scheme

Subnets: <your-existing-subnets-here>

Security Group: allows inbound traffic on port 80.

Listener Configuration:

Port 80 → Forward to Target Group.

# DNS Configuration

## Obtained ALB DNS name: 
```bash
http://mernapp-alb-1600299037.ap-south-1.elb.amazonaws.com/
```
### Screenshots:
<img width="857" height="588" alt="image" src="https://github.com/user-attachments/assets/f205204f-c412-4ac7-ac35-266ee4e2d119" />


-----

# 🚀 MERN Application Deployment on AWS (EC2 + ALB + Lambda)

This guide explains how to deploy a **MERN microservices application** on AWS using:

- **EC2 (Auto Scaling Group + ALB)** → For backend & frontend  
- **Lambda + S3** → For automated MongoDB backups  

---

## 🛠 Prerequisites

- **AWS CLI v2** installed (`awscli2`)
- **Docker** installed on EC2
- An existing **VPC + Subnet IDs** (fill in your IDs where required)
- **ECR repositories** created for:
  - `hello-service`
  - `profile-service`
  - `mern-frontend`

---

## ⚙️ Step 1: Deploy Backend & Frontend on EC2 (with ALB)

We use an **Auto Scaling Group (ASG)** + **Application Load Balancer (ALB)**.  
Each EC2 instance runs both frontend and backend containers.

### `deploy.sh` (Run on EC2 instances)

```bash
#!/bin/bash

# Update & install docker + awscli2
sudo apt update -y
sudo apt install -y docker.io awscli2
sudo systemctl enable docker
sudo systemctl start docker

# Add ubuntu user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Authenticate to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.ap-south-1.amazonaws.com

# Stop & clean old containers
docker stop hello-service profile-service frontend || true
docker rm hello-service profile-service frontend || true

# Pull images
docker pull 975050024946.dkr.ecr.ap-south-1.amazonaws.com/hello-service:latest
docker pull 975050024946.dkr.ecr.ap-south-1.amazonaws.com/profile-service:latest
docker pull 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-frontend:latest

# Run backend services
docker run -d --name hello-service -p 3001:3001 975050024946.dkr.ecr.ap-south-1.amazonaws.com/hello-service:latest
docker run -d --name profile-service -p 3002:3002 -e MONGO_URL="your-mongo-uri-here" 975050024946.dkr.ecr.ap-south-1.amazonaws.com/profile-service:latest

# Run frontend service
docker run -d --name frontend -p 3000:3000 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-frontend:latest

```
## Access the app:
```bash
http://MERNApp-ALB-xyz.elb.ap-south-1.amazonaws.com
```
### Screenshots
<img width="1498" height="920" alt="image" src="https://github.com/user-attachments/assets/5a27c5aa-ed1c-4b8e-8d0d-5faf9554a218" />

