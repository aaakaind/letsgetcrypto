#!/bin/bash

# LetsGetCrypto CI/CD Pipeline Setup Script
# This script sets up AWS CodeBuild and CodePipeline for automated deployments

set -e

# Configuration
STACK_NAME="letsgetcrypto-cicd"
REGION="${AWS_REGION:-us-east-1}"
GITHUB_REPO="${GITHUB_REPO:-aaakaind/letsgetcrypto}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"

echo "🚀 Setting up LetsGetCrypto CI/CD Pipeline"
echo "=========================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Get GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GitHub token not found in environment"
    echo "Please provide your GitHub personal access token:"
    echo "  (Create one at https://github.com/settings/tokens)"
    echo "  Required scopes: repo, admin:repo_hook"
    read -s -p "GitHub Token: " GITHUB_TOKEN
    echo ""
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GitHub token is required"
    exit 1
fi

# Optional ECS configuration
echo ""
echo "📋 ECS Configuration (optional - press Enter to skip)"
read -p "ECS Cluster Name (e.g., letsgetcrypto-cluster): " ECS_CLUSTER_NAME
read -p "ECS Service Name (e.g., letsgetcrypto-service): " ECS_SERVICE_NAME

# Build parameters
PARAMS="ParameterKey=GitHubRepository,ParameterValue=$GITHUB_REPO"
PARAMS="$PARAMS ParameterKey=GitHubBranch,ParameterValue=$GITHUB_BRANCH"
PARAMS="$PARAMS ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN"

if [ ! -z "$ECS_CLUSTER_NAME" ]; then
    PARAMS="$PARAMS ParameterKey=ECSClusterName,ParameterValue=$ECS_CLUSTER_NAME"
fi

if [ ! -z "$ECS_SERVICE_NAME" ]; then
    PARAMS="$PARAMS ParameterKey=ECSServiceName,ParameterValue=$ECS_SERVICE_NAME"
fi

# Deploy CloudFormation stack
echo ""
echo "☁️  Deploying CI/CD infrastructure..."
aws cloudformation deploy \
    --template-file aws/codebuild-pipeline.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides $PARAMS \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

# Get outputs
echo ""
echo "📊 Getting deployment outputs..."
PIPELINE_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`PipelineName`].OutputValue' \
    --output text \
    --region $REGION)

CODEBUILD_PROJECT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`CodeBuildProjectName`].OutputValue' \
    --output text \
    --region $REGION)

ARTIFACT_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ArtifactBucketName`].OutputValue' \
    --output text \
    --region $REGION)

PIPELINE_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`PipelineConsoleURL`].OutputValue' \
    --output text \
    --region $REGION)

CODEBUILD_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`CodeBuildConsoleURL`].OutputValue' \
    --output text \
    --region $REGION)

echo ""
echo "🎉 CI/CD Pipeline Setup Complete!"
echo "=================================="
echo ""
echo "📦 Resources Created:"
echo "  • Pipeline: $PIPELINE_NAME"
echo "  • CodeBuild Project: $CODEBUILD_PROJECT"
echo "  • Artifact Bucket: $ARTIFACT_BUCKET"
echo ""
echo "🌐 AWS Console Links:"
echo "  • Pipeline: $PIPELINE_URL"
echo "  • CodeBuild: $CODEBUILD_URL"
echo ""
echo "✅ Next Steps:"
echo "  1. The pipeline will automatically trigger on push to '$GITHUB_BRANCH' branch"
echo "  2. Monitor builds in the CodeBuild console"
echo "  3. View pipeline execution in the CodePipeline console"
echo ""
echo "🔄 Manual Trigger:"
echo "  aws codepipeline start-pipeline-execution --name $PIPELINE_NAME --region $REGION"
echo ""
echo "📝 Build Logs:"
echo "  aws logs tail /aws/codebuild/$STACK_NAME --follow --region $REGION"
echo ""
echo "🗑️  To cleanup:"
echo "  aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
echo "  aws s3 rm s3://$ARTIFACT_BUCKET --recursive"
echo "  aws s3 rb s3://$ARTIFACT_BUCKET"
