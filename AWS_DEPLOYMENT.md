# AWS Deployment Guide for LetsGetCrypto

This comprehensive guide provides step-by-step instructions for deploying the LetsGetCrypto application to AWS using Amazon ECS with Fargate and RDS PostgreSQL.

## 🏗️ Architecture Overview

The AWS deployment includes:

- **Amazon ECS Fargate**: Serverless containerized application hosting (no EC2 management needed)
- **Application Load Balancer**: HTTP/HTTPS traffic distribution with health checks
- **Amazon RDS PostgreSQL**: Fully managed database with automated backups
- **AWS Secrets Manager**: Secure credential storage and rotation
- **Amazon CloudWatch**: Centralized logging and monitoring
- **Amazon VPC**: Isolated network with public and private subnets
- **Amazon ECR**: Container image registry

## 🔄 CI/CD Pipeline (Automated Deployments)

LetsGetCrypto includes a fully automated CI/CD pipeline using AWS CodeBuild and CodePipeline. This enables continuous delivery with automated builds and deployments triggered by Git commits.

### CI/CD Architecture

The CI/CD pipeline includes:

- **AWS CodePipeline**: Orchestrates the complete deployment workflow
- **AWS CodeBuild**: Builds Docker images and runs tests
- **Amazon ECR**: Stores versioned container images
- **GitHub Webhook**: Automatically triggers pipeline on code changes
- **Amazon ECS**: Automatic deployment of new versions to your cluster
- **Amazon S3**: Stores build artifacts and pipeline data
- **AWS CloudWatch**: Logs all build and deployment activities

### Quick Setup

Set up the complete CI/CD pipeline with a single command:

```bash
# Make the setup script executable
chmod +x setup-cicd.sh

# Run the setup (you'll be prompted for GitHub token)
./setup-cicd.sh
```

**What the script does:**
1. ✅ Creates an S3 bucket for pipeline artifacts
2. ✅ Sets up IAM roles with appropriate permissions
3. ✅ Creates a CodeBuild project for building Docker images
4. ✅ Creates a CodePipeline with Source → Build → Deploy stages
5. ✅ Configures GitHub webhook for automatic triggers
6. ✅ Optionally connects to your ECS cluster for automated deployments

**Setup time:** Approximately 2-3 minutes

### Manual CI/CD Setup

If you prefer manual setup or need customization:

#### 1. Create GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` and `admin:repo_hook`
4. Copy the generated token

#### 2. Deploy CI/CD Infrastructure

```bash
# Set environment variables
export GITHUB_TOKEN="your_github_token_here"
export AWS_REGION="us-east-1"

# Optional: Connect to existing ECS cluster
export ECS_CLUSTER_NAME="letsgetcrypto-cluster"
export ECS_SERVICE_NAME="letsgetcrypto-service"

# Deploy the CI/CD stack
aws cloudformation deploy \
    --template-file aws/codebuild-pipeline.yaml \
    --stack-name letsgetcrypto-cicd \
    --parameter-overrides \
        GitHubRepository=aaakaind/letsgetcrypto \
        GitHubBranch=main \
        GitHubToken=$GITHUB_TOKEN \
        ECSClusterName=$ECS_CLUSTER_NAME \
        ECSServiceName=$ECS_SERVICE_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION
```

#### 3. Monitor Pipeline

```bash
# Get pipeline name
PIPELINE_NAME=$(aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-cicd \
    --query 'Stacks[0].Outputs[?OutputKey==`PipelineName`].OutputValue' \
    --output text)

# View pipeline status
aws codepipeline get-pipeline-state --name $PIPELINE_NAME

# Manually trigger pipeline
aws codepipeline start-pipeline-execution --name $PIPELINE_NAME
```

### How It Works

1. **Developer pushes code** to the `main` branch (or configured branch)
2. **GitHub webhook** notifies CodePipeline
3. **Pipeline triggers** and enters Source stage
4. **CodeBuild starts** with the `buildspec.yml` configuration:
   - Installs dependencies
   - Runs tests (optional)
   - Builds Docker image
   - Pushes image to ECR with commit SHA tag
5. **Deploy stage** (if ECS is configured):
   - Updates ECS service with new image
   - Performs rolling deployment
   - Monitors health checks
6. **Notifications** are sent via CloudWatch logs

### Build Configuration

The build process is defined in `buildspec.yml`:

```yaml
# Key features:
- Automated Docker image builds
- ECR authentication and push
- Optional test execution
- ECS service updates
- Build caching for faster builds
- CloudWatch logging
```

#### Customizing the Build

Edit `buildspec.yml` to customize:

- **Enable tests**: Uncomment the test commands in the `pre_build` phase
- **Add linting**: Add linting tools in `pre_build`
- **Multi-stage builds**: Modify build commands for optimization
- **Environment variables**: Add to CodeBuild project configuration

### Environment Variables

Set these in the CodeBuild project (via CloudFormation or Console):

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_DEFAULT_REGION` | AWS region for deployment | `us-east-1` |
| `ECR_REPOSITORY` | ECR repository name | `letsgetcrypto` |
| `CLUSTER_NAME` | ECS cluster for deployment | (optional) |
| `SERVICE_NAME` | ECS service to update | (optional) |

### Monitoring and Logs

**View build logs:**
```bash
# Real-time logs
aws logs tail /aws/codebuild/letsgetcrypto-cicd --follow

# Recent logs
aws logs tail /aws/codebuild/letsgetcrypto-cicd --since 1h
```

**Check pipeline status:**
```bash
# Pipeline execution history
aws codepipeline list-pipeline-executions --pipeline-name letsgetcrypto-cicd-pipeline

# Latest execution details
aws codepipeline get-pipeline-execution \
    --pipeline-name letsgetcrypto-cicd-pipeline \
    --pipeline-execution-id <execution-id>
```

**AWS Console:**
- CodePipeline: https://console.aws.amazon.com/codesuite/codepipeline/pipelines
- CodeBuild: https://console.aws.amazon.com/codesuite/codebuild/projects
- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups

### Costs

Approximate monthly costs for CI/CD infrastructure:

| Service | Usage | Cost |
|---------|-------|------|
| CodeBuild | 100 builds @ 5 min each | ~$1.00 |
| CodePipeline | 1 active pipeline | $1.00 |
| S3 (artifacts) | ~5 GB storage | $0.12 |
| CloudWatch Logs | ~1 GB logs | $0.50 |
| **Total** | | **~$3/month** |

*Note: Actual costs may vary based on usage patterns*

### Troubleshooting CI/CD

#### Build Fails with "Access Denied"

**Issue**: CodeBuild can't access ECR or ECS

**Solution**: Verify IAM role permissions:
```bash
aws iam get-role-policy \
    --role-name letsgetcrypto-cicd-codebuild-role \
    --policy-name CodeBuildPolicy
```

#### Pipeline Not Triggering on Push

**Issue**: GitHub webhook not working

**Solution**: 
1. Check webhook in GitHub repository settings
2. Verify GitHub token has `admin:repo_hook` scope
3. Re-create webhook:
```bash
aws cloudformation update-stack \
    --stack-name letsgetcrypto-cicd \
    --use-previous-template \
    --parameters ParameterKey=GitHubToken,ParameterValue=<new-token> \
    --capabilities CAPABILITY_NAMED_IAM
```

#### Docker Build Fails

**Issue**: Out of memory or timeout

**Solution**: Increase CodeBuild compute size:
- Edit `aws/codebuild-pipeline.yaml`
- Change `ComputeType` from `BUILD_GENERAL1_SMALL` to `BUILD_GENERAL1_MEDIUM`
- Redeploy stack

### Cleanup CI/CD Resources

To remove the CI/CD pipeline:

```bash
# Get artifact bucket name
BUCKET=$(aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-cicd \
    --query 'Stacks[0].Outputs[?OutputKey==`ArtifactBucketName`].OutputValue' \
    --output text)

# Empty and delete bucket
aws s3 rm s3://$BUCKET --recursive
aws s3 rb s3://$BUCKET

# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name letsgetcrypto-cicd
```

## 📦 Deployment Packages

LetsGetCrypto provides ready-to-deploy packages for different AWS services. Choose the package that best fits your needs:

### Creating Deployment Packages

Run the packaging script to create deployment-ready packages:

```bash
# Make the script executable
chmod +x package-for-aws.sh

# Create packages (optionally specify version)
./package-for-aws.sh 1.0.0
```

This creates three packages in the `aws-packages/` directory:

1. **CloudFormation/ECS Fargate Package** (Recommended for production)
   - Best for: Scalable production deployments
   - Cost: ~$50-100/month
   - Features: Auto-scaling, load balancer, managed database
   
2. **Elastic Beanstalk Package** (Easiest deployment)
   - Best for: Quick deployments and testing
   - Cost: ~$30-50/month
   - Features: Simple management, automatic updates, lower cost

3. **Complete Source Package**
   - Best for: Custom deployments or development
   - Contains all source code and configuration

See `aws-packages/PACKAGE_SUMMARY.md` for detailed information on each package.

### Option 1: Elastic Beanstalk (Easiest) 🚀

**Perfect for**: Quick deployments, testing, small-scale applications

#### Via AWS Console (No Command Line Required)

1. Extract the Elastic Beanstalk package:
   ```bash
   unzip aws-packages/letsgetcrypto-beanstalk-*.zip
   ```

2. Go to [AWS Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk)

3. Click **Create Application**

4. Configure:
   - Application name: `letsgetcrypto`
   - Platform: Python 3.11
   - Upload the ZIP file created above

5. Configure environment variables:
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=*`
   - `DJANGO_SECRET_KEY=<generate-random-key>`

6. Click **Create Environment**

7. Wait 5-10 minutes for deployment

8. Access your application at the provided URL!

#### Via CLI

```bash
# Install EB CLI if not already installed
pip install awsebcli

# Extract and enter the package directory
unzip aws-packages/letsgetcrypto-beanstalk-*.zip -d letsgetcrypto-eb
cd letsgetcrypto-eb

# Initialize Elastic Beanstalk
eb init -p python-3.11 letsgetcrypto --region us-east-1

# Create environment with database
eb create letsgetcrypto-env \
  --database.engine postgres \
  --database.instance db.t3.micro \
  --instance-type t3.small \
  --envvars DJANGO_DEBUG=False,DJANGO_ALLOWED_HOSTS=*

# Open in browser
eb open
```

**Deployment time:** 5-10 minutes

### Option 2: CloudFormation/ECS Fargate (Production)

**Perfect for**: Production deployments requiring scalability

## 🚀 Quick Deployment

### Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions:
   - ECS (Elastic Container Service)
   - RDS (Relational Database Service)
   - VPC (Virtual Private Cloud)
   - Secrets Manager
   - CloudFormation
   - ECR (Elastic Container Registry)
   - CloudWatch
   - IAM (for creating roles)

2. **AWS CLI** v2 installed and configured:
   ```bash
   aws --version  # Should show v2.x.x
   aws configure  # Set your credentials
   ```

3. **Docker** installed and running:
   ```bash
   docker --version  # Verify installation
   docker ps         # Check Docker is running
   ```

4. **Sufficient AWS Service Limits**:
   - At least 2 Elastic IPs available
   - VPC limit not exceeded
   - ECS task limit available

### Automated Deployment (Recommended)

The automated script handles all deployment steps:

```bash
# Make the deployment script executable
chmod +x deploy-aws.sh

# Run the deployment
./deploy-aws.sh
```

**What the script does:**
1. ✅ Validates prerequisites (AWS CLI, Docker)
2. ✅ Creates an ECR repository for container images
3. ✅ Builds and pushes the Docker image to ECR
4. ✅ Generates a secure database password
5. ✅ Deploys the CloudFormation stack (infrastructure + application)
6. ✅ Waits for the application to become healthy
7. ✅ Displays deployment information and testing commands

**Deployment time:** Approximately 10-15 minutes

### Manual Deployment Steps

If you prefer manual deployment:

#### 1. Build and Push Docker Image

```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

# Create ECR repository
aws ecr create-repository --repository-name letsgetcrypto --region $REGION

# Build image
docker build -t letsgetcrypto:latest .

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Tag and push
docker tag letsgetcrypto:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:latest
```

#### 2. Deploy CloudFormation Stack

```bash
# Generate a secure database password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Deploy the stack
aws cloudformation deploy \
    --template-file aws/cloudformation-template.yaml \
    --stack-name letsgetcrypto-stack \
    --parameter-overrides \
        ContainerImage=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:latest \
        DBPassword=$DB_PASSWORD \
    --capabilities CAPABILITY_IAM \
    --region $REGION
```

#### 3. Get Application URL

```bash
# Get the load balancer URL
aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-stack \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text
```

## 🔧 Configuration

### Environment Variables

The application uses these environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_DEBUG` | Enable debug mode | `False` | No |
| `DJANGO_SECRET_KEY` | Django secret key | Generated | Yes |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | `*` | No |
| `DATABASE_URL` | PostgreSQL connection string | Generated | Yes |
| `DJANGO_LOG_LEVEL` | Logging level | `INFO` | No |

### AWS Secrets Manager

Sensitive configuration is stored in AWS Secrets Manager:

- `letsgetcrypto/django-secret-key`: Django secret key
- `letsgetcrypto/database-url`: Database connection string

## 🏥 Health Checks

The application provides multiple health check endpoints:

### Load Balancer Health Check
- **Endpoint**: `/api/health/`
- **Method**: GET
- **Success**: HTTP 200 with `{"status": "healthy"}`
- **Failure**: HTTP 503 with error details

### Kubernetes/ECS Readiness Check
- **Endpoint**: `/api/readiness/`
- **Method**: GET
- **Purpose**: Check if application is ready to serve traffic

### Kubernetes/ECS Liveness Check
- **Endpoint**: `/api/liveness/`
- **Method**: GET
- **Purpose**: Check if application is running

## 📊 API Endpoints

### Root Information
```bash
GET /
```
Returns API information and available endpoints.

### Market Overview
```bash
GET /api/market/?limit=10
```
Get top cryptocurrencies by market cap.

### Cryptocurrency Price
```bash
GET /api/price/{symbol}/
```
Get current price for a specific cryptocurrency (e.g., `bitcoin`, `ethereum`).

### Historical Data
```bash
GET /api/history/{symbol}/?days=30
```
Get historical price data for a cryptocurrency.

## 🔍 Monitoring and Logging

### CloudWatch Logs

Application logs are sent to CloudWatch:
- **Log Group**: `/ecs/letsgetcrypto-api`
- **Log Stream**: `ecs/{container-id}`

### Key Metrics to Monitor

1. **Health Check Success Rate**: Monitor `/api/health/` endpoint
2. **Response Times**: Track API response times
3. **Error Rates**: Monitor 4xx and 5xx responses
4. **Database Connections**: Monitor RDS connection count
5. **ECS Service Health**: Monitor task health and count

### Setting Up Alerts

```bash
# Create CloudWatch alarm for health checks
aws cloudwatch put-metric-alarm \
    --alarm-name "LetsGetCrypto-HealthCheck" \
    --alarm-description "Health check failures" \
    --metric-name TargetResponseTime \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 300 \
    --threshold 5.0 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

## 🔄 Updates and Maintenance

### Updating the Application

When you make code changes and want to deploy a new version:

1. **Build and push new image**:
   ```bash
   # Set your AWS account details
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   REGION="us-east-1"
   
   # Build new version
   docker build -t letsgetcrypto:v2.0 .
   
   # Login to ECR
   aws ecr get-login-password --region $REGION | \
       docker login --username AWS --password-stdin \
       $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
   
   # Tag and push
   docker tag letsgetcrypto:v2.0 \
       $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:v2.0
   docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:v2.0
   ```

2. **Update ECS service to use new image**:
   ```bash
   # Create new task definition revision with the new image
   # Then force a new deployment
   aws ecs update-service \
       --cluster letsgetcrypto-cluster \
       --service letsgetcrypto-service \
       --force-new-deployment \
       --region $REGION
   ```

3. **Monitor the deployment**:
   ```bash
   # Watch the service update
   aws ecs describe-services \
       --cluster letsgetcrypto-cluster \
       --services letsgetcrypto-service \
       --region $REGION \
       --query 'services[0].deployments'
   ```

**Note**: ECS will perform a rolling update, starting new tasks with the new image before stopping old ones.

### Database Migrations

For database schema changes:

```bash
# Connect to a running container
aws ecs execute-command \
    --cluster letsgetcrypto-cluster \
    --task TASK_ID \
    --container letsgetcrypto-api \
    --interactive \
    --command "/bin/bash"

# Run migrations inside the container
python manage.py migrate
```

### Scaling

```bash
# Scale the service
aws ecs update-service \
    --cluster letsgetcrypto-cluster \
    --service letsgetcrypto-service \
    --desired-count 4
```

## 🤖 MCP Server Integration

### What is MCP?

The Model Context Protocol (MCP) allows AI assistants to interact with your cryptocurrency data. After deploying to AWS, you can connect AI tools to your live data.

### Setting Up MCP Server with AWS Deployment

1. **Get your AWS Load Balancer URL**:
   ```bash
   aws cloudformation describe-stacks \
       --stack-name letsgetcrypto-stack \
       --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
       --output text
   ```

2. **Configure MCP server** to use your AWS deployment:
   ```bash
   export CRYPTO_API_URL=http://your-loadbalancer-url.amazonaws.com
   python mcp_server.py
   ```

3. **For Claude Desktop integration**, update your config:
   ```json
   {
     "mcpServers": {
       "letsgetcrypto": {
         "command": "python",
         "args": ["/path/to/letsgetcrypto/mcp_server.py"],
         "env": {
           "CRYPTO_API_URL": "http://your-loadbalancer-url.amazonaws.com"
         }
       }
     }
   }
   ```

See [MCP_SERVER.md](MCP_SERVER.md) for complete MCP server documentation.

## 🧪 Testing

### Local Testing with Docker Compose

Test the production configuration locally before AWS deployment:

```bash
# Start services
docker-compose up --build

# Test endpoints in another terminal
curl http://localhost/api/health/
curl http://localhost/api/market/
curl http://localhost/api/price/bitcoin/

# Stop services
docker-compose down
```

### Automated Testing

Test your AWS deployment with the automated test suite:

```bash
# Get your load balancer URL
LOAD_BALANCER_URL=$(aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-stack \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text)

# Run comprehensive tests
python test_aws_deployment.py --url $LOAD_BALANCER_URL
```

### Manual Testing

Test individual endpoints:

```bash
# Health check
curl $LOAD_BALANCER_URL/api/health/

# Market overview
curl $LOAD_BALANCER_URL/api/market/

# Bitcoin price
curl $LOAD_BALANCER_URL/api/price/bitcoin/

# Ethereum 7-day history
curl "$LOAD_BALANCER_URL/api/history/ethereum/?days=7"
```

## 💰 Cost Optimization

### Estimated Monthly Costs (us-east-1)

- **ECS Fargate** (2 tasks, 0.5 vCPU, 1GB): ~$20
- **Application Load Balancer**: ~$18
- **RDS db.t3.micro**: ~$12
- **NAT Gateway**: ~$33
- **CloudWatch Logs**: ~$2
- **Total**: ~$85/month

### Cost Reduction Tips

1. **Use Fargate Spot**: Save up to 70% on compute costs
2. **Right-size Resources**: Monitor and adjust CPU/memory
3. **Use Single AZ**: Remove NAT Gateway for dev environments
4. **Schedule Auto-scaling**: Scale down during off-hours

## 🔐 Security Best Practices

### Implemented Security Features

1. **VPC Isolation**: Private subnets for application and database
2. **Security Groups**: Restrictive firewall rules
3. **Secrets Management**: Credentials in AWS Secrets Manager
4. **HTTPS Ready**: SSL termination at load balancer
5. **Database Encryption**: RDS encryption at rest
6. **Non-root Container**: Application runs as non-root user

### Additional Security Recommendations

1. **Enable AWS Config**: Track configuration changes
2. **Set up AWS GuardDuty**: Threat detection
3. **Use AWS WAF**: Web application firewall
4. **Enable VPC Flow Logs**: Network traffic monitoring
5. **Regular Security Scans**: Container image scanning

## 🗑️ Cleanup

To remove all AWS resources:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack --stack-name letsgetcrypto-stack

# Delete ECR repository
aws ecr delete-repository --repository-name letsgetcrypto --force
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**:
   - Check CloudWatch logs
   - Verify database connectivity
   - Check secrets manager permissions

2. **Health checks failing**:
   - Verify security group rules
   - Check application logs
   - Test endpoints manually

3. **High response times**:
   - Check external API rate limits
   - Monitor database performance
   - Consider increasing task count

### Useful Commands

```bash
# View service status
aws ecs describe-services --cluster letsgetcrypto-cluster --services letsgetcrypto-service

# View task details
aws ecs describe-tasks --cluster letsgetcrypto-cluster --tasks TASK_ID

# View logs
aws logs tail /ecs/letsgetcrypto-api --follow

# Check load balancer health
aws elbv2 describe-target-health --target-group-arn TARGET_GROUP_ARN
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Deployment Fails with "CREATE_FAILED"

**Check CloudFormation events**:
```bash
aws cloudformation describe-stack-events \
    --stack-name letsgetcrypto-stack \
    --max-items 20 \
    --region us-east-1
```

**Common causes**:
- Insufficient permissions
- Service limits exceeded (check ECS, VPC limits)
- Invalid parameters

#### 2. Application Not Responding

**Check ECS task status**:
```bash
aws ecs list-tasks \
    --cluster letsgetcrypto-cluster \
    --region us-east-1

aws ecs describe-tasks \
    --cluster letsgetcrypto-cluster \
    --tasks <task-arn> \
    --region us-east-1
```

**Check CloudWatch logs**:
```bash
aws logs tail /ecs/letsgetcrypto-api --follow
```

#### 3. Health Check Failures

**Test health endpoint directly**:
```bash
curl -v http://your-loadbalancer-url/api/health/
```

**Common causes**:
- Database connection issues
- External API (CoinGecko) unavailable
- Application startup taking longer than health check interval

#### 4. Database Connection Issues

**Verify database endpoint**:
```bash
aws rds describe-db-instances \
    --db-instance-identifier <instance-id> \
    --query 'DBInstances[0].Endpoint'
```

**Check security groups**:
- Ensure ECS security group can access RDS security group on port 5432

#### 5. Docker Build Fails

**Check Dockerfile and dependencies**:
```bash
docker build -t letsgetcrypto:test .
```

**Common issues**:
- Missing requirements in requirements.txt
- Invalid Python version
- Build context too large (use .dockerignore)

### Getting Help

**View logs**:
```bash
# CloudWatch Logs
aws logs tail /ecs/letsgetcrypto-api --follow --format short

# ECS service events
aws ecs describe-services \
    --cluster letsgetcrypto-cluster \
    --services letsgetcrypto-service \
    --query 'services[0].events[0:10]'
```

**Useful AWS CLI commands**:
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name letsgetcrypto-stack

# List running tasks
aws ecs list-tasks --cluster letsgetcrypto-cluster

# View load balancer
aws elbv2 describe-load-balancers
```

## 🗑️ Cleanup

To delete all AWS resources and stop incurring charges:

```bash
# Delete the CloudFormation stack (removes all resources)
aws cloudformation delete-stack \
    --stack-name letsgetcrypto-stack \
    --region us-east-1

# Monitor deletion
aws cloudformation describe-stacks \
    --stack-name letsgetcrypto-stack \
    --region us-east-1 \
    --query 'Stacks[0].StackStatus'

# Delete ECR repository and images
aws ecr delete-repository \
    --repository-name letsgetcrypto \
    --force \
    --region us-east-1
```

**Note**: This will permanently delete:
- All ECS tasks and services
- The RDS database (and all data)
- The load balancer
- VPC and networking components
- CloudWatch logs (unless you've set longer retention)

## 📞 Support

For issues related to:
- **AWS Infrastructure**: Check CloudFormation events and CloudWatch logs
- **Application Code**: Review application logs in CloudWatch  
- **Database Issues**: Monitor RDS CloudWatch metrics
- **Network Issues**: Check VPC Flow Logs and security groups
- **MCP Server**: See [MCP_SERVER.md](MCP_SERVER.md) documentation

### Useful Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS RDS PostgreSQL Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [CloudFormation Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)
- [LetsGetCrypto README](README.md)

---

**Note**: This deployment guide assumes basic familiarity with AWS services. For production deployments, consider:
- Implementing automated backups
- Setting up CloudWatch alarms
- Configuring auto-scaling policies
- Adding a custom domain with Route 53
- Implementing AWS WAF for security
- Using AWS Certificate Manager for HTTPS