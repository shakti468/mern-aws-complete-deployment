import boto3
import json
import time
import base64
from botocore.exceptions import ClientError

# -------------------------------
# 🚨 Fill in your values
# -------------------------------
VPC_ID = "vpc-0056d809452f9f8ea"   # 👉 your VPC
SUBNET_IDS = ["subnet-0a08b704a1b1af340"]  # 👉 your subnet(s)
AWS_ACCOUNT_ID = "975050024946"    # 👉 your AWS Account ID
REGION = "ap-south-1"
KEY_NAME = "Shakti-b10"            # 👉 your EC2 key pair
SG_ID = "sg-0e03c3accc395a435"     # 👉 your existing SG
IAM_ROLE_NAME = "shakti-jenkins-ec2-iam"
INSTANCE_PROFILE_NAME = f"{IAM_ROLE_NAME}-profile"

# -------------------------------
# Clients
# -------------------------------
ec2 = boto3.client("ec2", region_name=REGION)
iam = boto3.client("iam", region_name=REGION)
autoscaling = boto3.client("autoscaling", region_name=REGION)

# -------------------------------
# 1. Ensure IAM Instance Profile exists
# -------------------------------
print("Checking IAM Instance Profile...")
try:
    iam.get_instance_profile(InstanceProfileName=INSTANCE_PROFILE_NAME)
    print(f"✅ Instance Profile already exists: {INSTANCE_PROFILE_NAME}")
except iam.exceptions.NoSuchEntityException:
    print("⚠️ Instance Profile not found, creating...")
    iam.create_instance_profile(InstanceProfileName=INSTANCE_PROFILE_NAME)
    time.sleep(5)  # give time
    iam.add_role_to_instance_profile(
        InstanceProfileName=INSTANCE_PROFILE_NAME,
        RoleName=IAM_ROLE_NAME
    )
    print(f"✅ Instance Profile created: {INSTANCE_PROFILE_NAME}")

print("⏳ Waiting 15s for IAM instance profile propagation...")
time.sleep(15)

# -------------------------------
# 2. Create / Reuse Launch Template
# -------------------------------
print("Creating Launch Template...")

USER_DATA = """#!/bin/bash
sudo apt update -y
sudo apt install -y docker.io awscli
sudo systemctl enable docker
sudo systemctl start docker

# Authenticate to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin {account}.dkr.ecr.ap-south-1.amazonaws.com

# Pull images
docker pull {account}.dkr.ecr.ap-south-1.amazonaws.com/hello-service:latest
docker pull {account}.dkr.ecr.ap-south-1.amazonaws.com/profile-service:latest
docker pull {account}.dkr.ecr.ap-south-1.amazonaws.com/mern-frontend:latest

# Run containers
docker run -d -p 3001:3001 {account}.dkr.ecr.ap-south-1.amazonaws.com/hello-service:latest
docker run -d -p 3002:3002 {account}.dkr.ecr.ap-south-1.amazonaws.com/profile-service:latest
docker run -d -p 3000:3000 {account}.dkr.ecr.ap-south-1.amazonaws.com/mern-frontend:latest
""".format(account=AWS_ACCOUNT_ID)

user_data_b64 = base64.b64encode(USER_DATA.encode("utf-8")).decode("utf-8")

try:
    lt = ec2.create_launch_template(
        LaunchTemplateName="MERNApp-LT",
        LaunchTemplateData={
            "ImageId": "ami-053b12d3152c0cc71",  # Ubuntu 22.04 in ap-south-1
            "InstanceType": "t3.micro",
            "KeyName": KEY_NAME,
            "SecurityGroupIds": [SG_ID],
            "IamInstanceProfile": {"Name": INSTANCE_PROFILE_NAME},
            "UserData": user_data_b64
        }
    )
    lt_id = lt["LaunchTemplate"]["LaunchTemplateId"]
    print(f"✅ Launch Template created: {lt_id}")

except ClientError as e:
    if "InvalidLaunchTemplateName.AlreadyExistsException" in str(e):
        print("⚠️ Launch Template already exists, using existing one...")
        existing_lt = ec2.describe_launch_templates(
            LaunchTemplateNames=["MERNApp-LT"]
        )
        lt_id = existing_lt["LaunchTemplates"][0]["LaunchTemplateId"]
        print(f"➡️ Using existing Launch Template: {lt_id}")
    else:
        raise

# -------------------------------
# 3. Create / Reuse Auto Scaling Group
# -------------------------------
print("Creating Auto Scaling Group...")

try:
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName="MERNApp-ASG",
        LaunchTemplate={"LaunchTemplateId": lt_id, "Version": "$Latest"},
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        VPCZoneIdentifier=",".join(SUBNET_IDS)
    )
    print("✅ Auto Scaling Group created successfully!")

except ClientError as e:
    if "AlreadyExists" in str(e):
        print("⚠️ Auto Scaling Group already exists, skipping creation.")
    else:
        raise
