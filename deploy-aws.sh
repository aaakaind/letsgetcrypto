#!/bin/bash

# LetsGetCrypto AWS Deployment Script
# This script deploys the application to AWS using CloudFormation and ECS

set -e

# Configuration
STACK_NAME="letsgetcrypto-stack"
REGION="us-east-1"
ECR_REPO_NAME="letsgetcrypto"
DB_PASSWORD="$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)"

echo "🚀 Starting LetsGetCrypto AWS Deployment"
echo "========================================"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install it first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $ACCOUNT_ID"

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $REGION || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $REGION

# Get ECR login
echo "🔑 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and tag Docker image
echo "🔨 Building Docker image..."
docker build -t $ECR_REPO_NAME:latest .

# Tag and push image to ECR
echo "📤 Pushing image to ECR..."
docker tag $ECR_REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Update CloudFormation template with account ID
sed "s/ACCOUNT_ID/$ACCOUNT_ID/g" aws/ecs-task-definition.json > aws/ecs-task-definition-updated.json

# Deploy CloudFormation stack
echo "☁️ Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file aws/cloudformation-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        ContainerImage=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME:latest \
        DBPassword=$DB_PASSWORD \
    --capabilities CAPABILITY_IAM \
    --region $REGION

# Get outputs
echo "📊 Getting deployment outputs..."
LOAD_BALANCER_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text \
    --region $REGION)

DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
    --output text \
    --region $REGION)

echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================="
echo "🌐 Application URL: $LOAD_BALANCER_URL"
echo "🗄️ Database Endpoint: $DB_ENDPOINT"
echo "🔍 Health Check: $LOAD_BALANCER_URL/api/health/"
echo "📊 Market Data: $LOAD_BALANCER_URL/api/market/"
echo ""
echo "⏰ Note: It may take a few minutes for the application to become available."
echo "📋 Database password has been stored in AWS Secrets Manager."

# Wait for application to be healthy
echo "⏳ Waiting for application to become healthy..."
for i in {1..30}; do
    if curl -s -f "$LOAD_BALANCER_URL/api/health/" > /dev/null 2>&1; then
        echo "✅ Application is healthy and ready!"
        break
    fi
    echo "⏳ Waiting... ($i/30)"
    sleep 10
done

echo ""
echo "🎯 Test the deployment:"
echo "curl $LOAD_BALANCER_URL/api/health/"
echo "curl $LOAD_BALANCER_URL/api/market/"
echo ""
echo "🛠️ To update the application:"
echo "1. Build and push a new image to ECR"
echo "2. Update the ECS service to use the new image"
echo ""
echo "🗑️ To cleanup resources:"
echo "aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"