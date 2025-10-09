# CI/CD Pipeline Summary

This document provides a quick overview of the CI/CD implementation for LetsGetCrypto.

## 📦 Files Added

### Core CI/CD Files
- **`buildspec.yml`** - AWS CodeBuild build specification
- **`setup-cicd.sh`** - Automated setup script for CI/CD infrastructure
- **`aws/codebuild-pipeline.yaml`** - CloudFormation template for CodeBuild and CodePipeline
- **`aws/codebuild-policy.json`** - IAM policy document for CodeBuild permissions

### Documentation
- **`CICD_GUIDE.md`** - Comprehensive CI/CD setup and usage guide (619 lines)
- **`AWS_DEPLOYMENT.md`** - Updated with CI/CD section (238 new lines)
- **`QUICK_DEPLOY.md`** - Updated with CI/CD quick start
- **`README.md`** - Updated to reference CI/CD capabilities

## 🏗️ Architecture

```
GitHub Repository
       ↓
   (Webhook)
       ↓
  CodePipeline ──→ Source Stage (GitHub)
       ↓
       ↓──────→ Build Stage (CodeBuild)
       ↓              │
       ↓              ├─ Build Docker Image
       ↓              ├─ Run Tests (optional)
       ↓              └─ Push to ECR
       ↓
       └────────→ Deploy Stage (ECS) [optional]
```

## ✨ Features

1. **Automated Builds**
   - Triggered by Git push to main branch
   - Builds Docker images with commit SHA tags
   - Pushes to Amazon ECR

2. **Testing Integration**
   - Optional test execution in pre-build phase
   - Configurable test commands
   - Fail build on test failures

3. **Build Caching**
   - Docker layer caching
   - Pip package caching
   - Faster subsequent builds

4. **Deployment Options**
   - Manual image deployment
   - Automatic ECS service updates
   - Rolling deployments with health checks

5. **Monitoring & Logging**
   - CloudWatch Logs integration
   - Build history tracking
   - Pipeline execution monitoring

## 🚀 Quick Usage

### Setup CI/CD Pipeline
```bash
chmod +x setup-cicd.sh
export GITHUB_TOKEN="your_token_here"
./setup-cicd.sh
```

### Manual Build Trigger
```bash
aws codepipeline start-pipeline-execution \
    --name letsgetcrypto-cicd-pipeline
```

### View Build Logs
```bash
aws logs tail /aws/codebuild/letsgetcrypto-cicd --follow
```

### Monitor Pipeline
```bash
aws codepipeline get-pipeline-state \
    --name letsgetcrypto-cicd-pipeline
```

## 📋 Configuration

### Environment Variables (CodeBuild)
- `AWS_DEFAULT_REGION` - AWS region (default: us-east-1)
- `ECR_REPOSITORY` - ECR repository name (default: letsgetcrypto)
- `CLUSTER_NAME` - ECS cluster for deployment (optional)
- `SERVICE_NAME` - ECS service to update (optional)

### GitHub Token Requirements
- Scope: `repo` (Full control of private repositories)
- Scope: `admin:repo_hook` (Full control of repository hooks)

### CloudFormation Parameters
- `GitHubRepository` - Repository (e.g., aaakaind/letsgetcrypto)
- `GitHubBranch` - Branch to track (default: main)
- `GitHubToken` - GitHub personal access token
- `ECSClusterName` - ECS cluster name (optional)
- `ECSServiceName` - ECS service name (optional)

## 💰 Cost Estimate

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| CodeBuild | 100 builds × 5 min | ~$1.00 |
| CodePipeline | 1 active pipeline | $1.00 |
| S3 (artifacts) | ~5 GB | $0.12 |
| CloudWatch Logs | ~1 GB | $0.50 |
| **Total** | | **~$2.62** |

## 🔧 Customization

### Enable Testing
Uncomment these lines in `buildspec.yml`:
```yaml
# - pip install -r requirements.txt
# - python -m pytest test_integration.py -v
```

### Add Linting
```yaml
pre_build:
  commands:
    - pip install flake8 black
    - flake8 crypto_api/
    - black --check .
```

### Increase Build Resources
Update `aws/codebuild-pipeline.yaml`:
```yaml
ComputeType: BUILD_GENERAL1_MEDIUM  # or BUILD_GENERAL1_LARGE
```

## 🔍 Troubleshooting

### Build Fails - Access Denied to ECR
**Fix**: Verify CodeBuild IAM role has ECR permissions
```bash
aws iam get-role-policy \
    --role-name letsgetcrypto-cicd-codebuild-role \
    --policy-name CodeBuildPolicy
```

### Pipeline Not Triggering
**Fix**: Check GitHub webhook status
1. Go to GitHub repo settings → Webhooks
2. Verify webhook exists and recent deliveries are successful
3. Check GitHub token scopes

### Docker Build Timeout
**Fix**: Increase build timeout or use larger instance type
```bash
aws codebuild update-project \
    --name letsgetcrypto-cicd-build \
    --timeout-in-minutes 30
```

## 📚 Documentation References

- **Detailed Setup**: [CICD_GUIDE.md](../CICD_GUIDE.md)
- **AWS Deployment**: [AWS_DEPLOYMENT.md](../AWS_DEPLOYMENT.md)
- **Quick Deploy**: [QUICK_DEPLOY.md](../QUICK_DEPLOY.md)

## 🗑️ Cleanup

```bash
# Get artifact bucket name
BUCKET=$(aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-cicd \
    --query 'Stacks[0].Outputs[?OutputKey==`ArtifactBucketName`].OutputValue' \
    --output text)

# Empty and delete bucket
aws s3 rm s3://$BUCKET --recursive
aws s3 rb s3://$BUCKET

# Delete stack
aws cloudformation delete-stack --stack-name letsgetcrypto-cicd
```

## ✅ Benefits

1. **Automation**: Eliminates manual build and deployment steps
2. **Consistency**: Same build process every time
3. **Speed**: Faster deployments with caching
4. **Visibility**: Full logs and monitoring
5. **Reliability**: Automated testing before deployment
6. **Scalability**: Easy to extend with additional stages

## 🎯 Next Steps

1. Set up the CI/CD pipeline using `setup-cicd.sh`
2. Make a test commit to trigger the pipeline
3. Monitor the build in CodeBuild console
4. Verify deployment in ECS (if configured)
5. Set up notifications for build failures
6. Add automated tests to pre-build phase
7. Configure deployment approvals for production
