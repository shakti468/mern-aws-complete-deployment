import boto3

# Clients
elbv2 = boto3.client("elbv2", region_name="ap-south-1")
autoscaling = boto3.client("autoscaling", region_name="ap-south-1")

# -------------------------------
# 🚨 Fill in your values
# -------------------------------
VPC_ID = "vpc-0056d809452f9f8ea"                # 👉 Fill here
SUBNET_IDS = ["subnet-0a08b704a1b1af340","subnet-0c1842aca7dc1b6b0"]       # 👉 Add at least 2 subnets in different AZs
SG_ID = "sg-03bc099f09edadb32"                  # 👉 From Step 5
ASG_NAME = "MERNApp-ASG"                        # From Step 5

# -------------------------------
# 1. Create Target Group
# -------------------------------
print("Creating Target Group...")
tg = elbv2.create_target_group(
    Name="MERNApp-TG",
    Protocol="HTTP",    # ✅ ALB uses HTTP/HTTPS
    Port=3001,          # 👈 backend port (HelloService). Create another TG for 3002 if needed
    VpcId=VPC_ID,
    HealthCheckProtocol="HTTP",
    HealthCheckPort="3001",
    HealthCheckPath="/",   # Adjust if your backend has a /health endpoint
    TargetType="instance"
)

tg_arn = tg["TargetGroups"][0]["TargetGroupArn"]
print(f"✅ Target Group created: {tg_arn}")

# -------------------------------
# 2. Create Application Load Balancer
# -------------------------------
print("Creating Application Load Balancer...")
alb = elbv2.create_load_balancer(
    Name="MERNApp-ALB",
    Subnets=SUBNET_IDS,
    SecurityGroups=[SG_ID],
    Scheme="internet-facing",
    Type="application",   # ✅ Key difference: ALB not NLB
    IpAddressType="ipv4"
)

alb_arn = alb["LoadBalancers"][0]["LoadBalancerArn"]
alb_dns = alb["LoadBalancers"][0]["DNSName"]

print(f"✅ ALB created: {alb_arn}")
print(f"🌍 ALB DNS: http://{alb_dns}")

# -------------------------------
# 3. Create Listener (port 80 → target group)
# -------------------------------
print("Creating Listener...")
elbv2.create_listener(
    LoadBalancerArn=alb_arn,
    Protocol="HTTP",
    Port=80,
    DefaultActions=[{"Type": "forward", "TargetGroupArn": tg_arn}]
)

print("✅ Listener created")

# -------------------------------
# 4. Attach Target Group to ASG
# -------------------------------
print("Attaching Target Group to Auto Scaling Group...")
autoscaling.attach_load_balancer_target_groups(
    AutoScalingGroupName=ASG_NAME,
    TargetGroupARNs=[tg_arn]
)

print("✅ Target Group attached to ASG")
