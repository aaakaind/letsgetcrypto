# CI/CD Pipeline Guide for LetsGetCrypto

This guide provides comprehensive documentation for setting up and using the AWS CodeBuild and CodePipeline CI/CD infrastructure for LetsGetCrypto.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Build Configuration](#build-configuration)
- [Deployment Strategies](#deployment-strategies)
- [Monitoring and Debugging](#monitoring-and-debugging)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The LetsGetCrypto CI/CD pipeline provides:

- ✅ **Automated builds** triggered by Git commits
- ✅ **Docker image creation** and versioning
- ✅ **ECR image registry** with automatic tagging
- ✅ **Optional testing** before deployment
- ✅ **ECS deployment** with zero-downtime rolling updates
- ✅ **Build caching** for faster execution
- ✅ **CloudWatch logging** for full visibility

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   GitHub    │─────▶│ CodePipeline │─────▶│  CodeBuild  │
│  (Source)   │      │ (Orchestrate)│      │   (Build)   │
└─────────────┘      └──────────────┘      └─────────────┘
                              │                     │
                              │                     ▼
                              │             ┌─────────────┐
                              │             │     ECR     │
                              │             │  (Images)   │
                              │             └─────────────┘
                              │                     │
                              ▼                     │
                       ┌─────────────┐            │
                       │     ECS     │◀───────────┘
                       │  (Deploy)   │
                       └─────────────┘
```

### Components

1. **GitHub Repository**: Source code and webhook trigger
2. **AWS CodePipeline**: Orchestrates the workflow (Source → Build → Deploy)
3. **AWS CodeBuild**: Executes build commands from `buildspec.yml`
4. **Amazon ECR**: Stores Docker images with version tags
5. **Amazon ECS**: Runs containerized application (optional)
6. **Amazon S3**: Stores pipeline artifacts
7. **AWS CloudWatch**: Collects logs and metrics
8. **IAM Roles**: Manages permissions between services

## 🚀 Quick Start

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** v2 installed and configured
3. **GitHub Personal Access Token** with scopes:
   - `repo` (Full control of private repositories)
   - `admin:repo_hook` (Full control of repository hooks)

### One-Command Setup

```bash
# Make script executable
chmod +x setup-cicd.sh

# Run setup
export GITHUB_TOKEN="your_github_token_here"
./setup-cicd.sh
```

The script will:
1. Prompt for configuration details
2. Create all AWS resources
3. Configure GitHub webhook
4. Display access URLs and commands

### Verify Setup

```bash
# Check pipeline status
aws codepipeline get-pipeline-state --name letsgetcrypto-cicd-pipeline

# View recent builds
aws codebuild list-builds-for-project --project-name letsgetcrypto-cicd-build

# Monitor logs
aws logs tail /aws/codebuild/letsgetcrypto-cicd --follow
```

## 🔧 Detailed Setup

### Step 1: Create GitHub Token

1. Navigate to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Set token name: `LetsGetCrypto-CI-CD`
4. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `admin:repo_hook` - Full control of repository hooks
5. Click "Generate token"
6. **Save the token securely** - you won't see it again

### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity
```

### Step 3: Deploy CI/CD Stack

#### Option A: Using setup script (Recommended)

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export AWS_REGION="us-east-1"

# Optional: Connect to existing ECS infrastructure
export ECS_CLUSTER_NAME="letsgetcrypto-cluster"
export ECS_SERVICE_NAME="letsgetcrypto-service"

./setup-cicd.sh
```

#### Option B: Manual CloudFormation deployment

```bash
aws cloudformation create-stack \
    --stack-name letsgetcrypto-cicd \
    --template-body file://aws/codebuild-pipeline.yaml \
    --parameters \
        ParameterKey=GitHubRepository,ParameterValue=aaakaind/letsgetcrypto \
        ParameterKey=GitHubBranch,ParameterValue=main \
        ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN \
        ParameterKey=ECSClusterName,ParameterValue=letsgetcrypto-cluster \
        ParameterKey=ECSServiceName,ParameterValue=letsgetcrypto-service \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1

# Wait for stack creation
aws cloudformation wait stack-create-complete \
    --stack-name letsgetcrypto-cicd
```

### Step 4: Verify Webhook

Check that the webhook was created in your GitHub repository:

1. Go to: `https://github.com/aaakaind/letsgetcrypto/settings/hooks`
2. You should see a webhook pointing to AWS CodePipeline
3. Recent deliveries should show successful pings

## 📝 Build Configuration

### buildspec.yml Structure

```yaml
version: 0.2

phases:
  pre_build:    # Setup and testing
  build:        # Docker image creation
  post_build:   # Push to ECR and deploy

artifacts:      # Files to pass to next stage
cache:          # Speed up builds
```

### Customizing Builds

#### Enable Testing

Uncomment these lines in `buildspec.yml`:

```yaml
pre_build:
  commands:
    # Uncomment to enable testing
    - pip install -r requirements.txt
    - python -m pytest test_integration.py -v
```

#### Add Linting

```yaml
pre_build:
  commands:
    - pip install flake8 black
    - flake8 crypto_api/ letsgetcrypto_django/
    - black --check .
```

#### Multi-stage Docker Builds

Optimize the `Dockerfile` for faster builds:

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
```

### Environment Variables

Configure these in CodeBuild project:

| Variable | Purpose | Example |
|----------|---------|---------|
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1` |
| `ECR_REPOSITORY` | ECR repo name | `letsgetcrypto` |
| `CLUSTER_NAME` | ECS cluster | `letsgetcrypto-cluster` |
| `SERVICE_NAME` | ECS service | `letsgetcrypto-service` |
| `DJANGO_DEBUG` | Debug mode | `False` |

Update via CLI:

```bash
aws codebuild update-project \
    --name letsgetcrypto-cicd-build \
    --environment type=LINUX_CONTAINER,\
computeType=BUILD_GENERAL1_SMALL,\
image=aws/codebuild/standard:7.0,\
privilegedMode=true,\
environmentVariables='[
  {name=CUSTOM_VAR,value=custom_value,type=PLAINTEXT}
]'
```

## 🚢 Deployment Strategies

### Blue/Green Deployment

For zero-downtime deployments:

```bash
# Update ECS service to use Blue/Green
aws ecs update-service \
    --cluster letsgetcrypto-cluster \
    --service letsgetcrypto-service \
    --deployment-configuration \
        maximumPercent=200,\
        minimumHealthyPercent=100
```

### Rolling Deployment (Default)

Default strategy - gradually replaces old tasks:

```bash
aws ecs update-service \
    --cluster letsgetcrypto-cluster \
    --service letsgetcrypto-service \
    --deployment-configuration \
        maximumPercent=150,\
        minimumHealthyPercent=50
```

### Canary Deployment

Deploy to subset of instances first:

```yaml
# Add to buildspec.yml post_build
- |
  aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME-canary \
    --force-new-deployment
  
  # Wait and verify metrics
  sleep 300
  
  # If successful, update main service
  aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment
```

## 📊 Monitoring and Debugging

### View Build Logs

```bash
# Real-time logs
aws logs tail /aws/codebuild/letsgetcrypto-cicd --follow

# Last hour
aws logs tail /aws/codebuild/letsgetcrypto-cicd --since 1h

# Filter by error
aws logs tail /aws/codebuild/letsgetcrypto-cicd \
    --filter-pattern "ERROR" --since 1h
```

### Check Pipeline Status

```bash
# Overall pipeline state
aws codepipeline get-pipeline-state \
    --name letsgetcrypto-cicd-pipeline

# Execution history
aws codepipeline list-pipeline-executions \
    --pipeline-name letsgetcrypto-cicd-pipeline \
    --max-results 5
```

### View Build Details

```bash
# List recent builds
aws codebuild list-builds-for-project \
    --project-name letsgetcrypto-cicd-build \
    --max-results 5

# Get build details
aws codebuild batch-get-builds \
    --ids <build-id>
```

### AWS Console Access

- **CodePipeline**: https://console.aws.amazon.com/codesuite/codepipeline/pipelines
- **CodeBuild**: https://console.aws.amazon.com/codesuite/codebuild/projects
- **ECR**: https://console.aws.amazon.com/ecr/repositories
- **CloudWatch**: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups

### Set Up Notifications

Create SNS topic for build notifications:

```bash
# Create SNS topic
aws sns create-topic --name letsgetcrypto-build-notifications

# Subscribe email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:letsgetcrypto-build-notifications \
    --protocol email \
    --notification-endpoint your-email@example.com

# Add notification rule to CodeBuild
aws codestar-notifications create-notification-rule \
    --name letsgetcrypto-build-notifications \
    --resource arn:aws:codebuild:us-east-1:ACCOUNT_ID:project/letsgetcrypto-cicd-build \
    --event-type-ids codebuild-project-build-state-failed codebuild-project-build-state-succeeded \
    --targets TargetType=SNS,TargetAddress=arn:aws:sns:us-east-1:ACCOUNT_ID:letsgetcrypto-build-notifications
```

## ✅ Best Practices

### 1. Use Semantic Versioning

Tag Docker images with version numbers:

```yaml
# In buildspec.yml
- IMAGE_TAG=${CODEBUILD_RESOLVED_SOURCE_VERSION}
- docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:v1.0.0
```

### 2. Implement Build Caching

Already configured in `buildspec.yml`:

```yaml
cache:
  paths:
    - '/root/.cache/pip/**/*'  # Python packages
```

Add more cache paths as needed:

```yaml
cache:
  paths:
    - '/root/.cache/pip/**/*'
    - 'node_modules/**/*'  # If using Node.js
    - '/root/.cache/go-build/**/*'  # If using Go
```

### 3. Run Tests in Pipeline

Always run tests before building images:

```yaml
pre_build:
  commands:
    - pip install -r requirements.txt
    - python -m pytest tests/ -v
    - |
      if [ $? -ne 0 ]; then
        echo "Tests failed! Aborting build."
        exit 1
      fi
```

### 4. Use Parameter Store for Secrets

Store sensitive values in AWS Systems Manager Parameter Store:

```bash
# Store secret
aws ssm put-parameter \
    --name /letsgetcrypto/api-key \
    --value "your-secret-key" \
    --type SecureString

# Reference in buildspec.yml
env:
  parameter-store:
    API_KEY: /letsgetcrypto/api-key
```

### 5. Implement Rollback Strategy

Configure ECS deployment circuit breaker:

```bash
aws ecs update-service \
    --cluster letsgetcrypto-cluster \
    --service letsgetcrypto-service \
    --deployment-configuration \
        deploymentCircuitBreaker="{enable=true,rollback=true}"
```

### 6. Monitor Build Metrics

Create CloudWatch dashboard:

```bash
aws cloudwatch put-dashboard \
    --dashboard-name LetsGetCrypto-CI-CD \
    --dashboard-body file://dashboard-config.json
```

## 🔍 Troubleshooting

### Issue: Build Fails with "Access Denied to ECR"

**Cause**: CodeBuild role lacks ECR permissions

**Solution**:
```bash
# Check role policy
aws iam get-role-policy \
    --role-name letsgetcrypto-cicd-codebuild-role \
    --policy-name CodeBuildPolicy

# Update if needed
aws iam put-role-policy \
    --role-name letsgetcrypto-cicd-codebuild-role \
    --policy-name ECRAccess \
    --policy-document file://aws/codebuild-policy.json
```

### Issue: Pipeline Not Triggering Automatically

**Cause**: GitHub webhook misconfigured

**Solution**:
1. Check webhook in GitHub: `https://github.com/aaakaind/letsgetcrypto/settings/hooks`
2. Test webhook delivery
3. Verify GitHub token has `admin:repo_hook` scope
4. Re-create webhook by updating stack

### Issue: Docker Build Timeout

**Cause**: Build takes too long with small instance

**Solution**:
```bash
# Update to larger instance
aws codebuild update-project \
    --name letsgetcrypto-cicd-build \
    --environment type=LINUX_CONTAINER,\
computeType=BUILD_GENERAL1_MEDIUM,\
image=aws/codebuild/standard:7.0,\
privilegedMode=true
```

### Issue: ECS Deployment Fails

**Cause**: Health check failures or insufficient resources

**Solution**:
```bash
# Check service events
aws ecs describe-services \
    --cluster letsgetcrypto-cluster \
    --services letsgetcrypto-service \
    --query 'services[0].events[0:10]'

# Check task logs
aws logs tail /ecs/letsgetcrypto-api --follow
```

### Issue: Build Succeeds but Old Image Still Running

**Cause**: ECS service not updating

**Solution**:
```bash
# Force new deployment
aws ecs update-service \
    --cluster letsgetcrypto-cluster \
    --service letsgetcrypto-service \
    --force-new-deployment

# Verify task definition
aws ecs describe-services \
    --cluster letsgetcrypto-cluster \
    --services letsgetcrypto-service \
    --query 'services[0].taskDefinition'
```

## 📈 Cost Optimization

### Estimated Monthly Costs

| Service | Usage | Cost |
|---------|-------|------|
| CodeBuild (on-demand) | 100 builds × 5 min | $1.00 |
| CodePipeline | 1 pipeline | $1.00 |
| S3 (artifacts) | 5 GB storage | $0.12 |
| CloudWatch Logs | 1 GB ingestion | $0.50 |
| Data Transfer | 10 GB out | $0.90 |
| **Total** | | **~$3.52/month** |

### Optimization Tips

1. **Use build caching** - Already enabled in buildspec.yml
2. **Optimize Docker builds** - Use multi-stage builds
3. **Clean up old images** - Set ECR lifecycle policy:

```bash
aws ecr put-lifecycle-policy \
    --repository-name letsgetcrypto \
    --lifecycle-policy-text '{
  "rules": [{
    "rulePriority": 1,
    "description": "Keep only 10 images",
    "selection": {
      "tagStatus": "any",
      "countType": "imageCountMoreThan",
      "countNumber": 10
    },
    "action": {
      "type": "expire"
    }
  }]
}'
```

4. **Use smaller instance** - BUILD_GENERAL1_SMALL for most builds
5. **Reduce pipeline polling** - Use webhooks instead (already configured)

## 🗑️ Cleanup

To remove all CI/CD resources:

```bash
# Get artifact bucket
BUCKET=$(aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-cicd \
    --query 'Stacks[0].Outputs[?OutputKey==`ArtifactBucketName`].OutputValue' \
    --output text)

# Empty bucket
aws s3 rm s3://$BUCKET --recursive

# Delete bucket
aws s3 rb s3://$BUCKET

# Delete stack (this removes all resources)
aws cloudformation delete-stack --stack-name letsgetcrypto-cicd

# Wait for deletion
aws cloudformation wait stack-delete-complete \
    --stack-name letsgetcrypto-cicd
```

## 📚 Additional Resources

- [AWS CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [AWS CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [Buildspec Reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [ECS Deployment Strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html)

## 🤝 Support

For issues or questions:
1. Check CloudWatch logs for error messages
2. Review GitHub webhook delivery status
3. Verify IAM role permissions
4. Check AWS service quotas
5. Open an issue in the repository
