# AWS Deployment Guide for LetsGetCrypto

This guide provides instructions for deploying the LetsGetCrypto application to AWS using Amazon ECS with Fargate and RDS PostgreSQL.

## 🏗️ Architecture Overview

The AWS deployment includes:

- **Amazon ECS Fargate**: Containerized application hosting
- **Application Load Balancer**: Traffic distribution and health checks
- **Amazon RDS PostgreSQL**: Managed database
- **AWS Secrets Manager**: Secure credential storage
- **CloudWatch**: Logging and monitoring
- **VPC**: Secure network isolation

## 🚀 Quick Deployment

### Prerequisites

1. **AWS CLI** installed and configured with appropriate permissions
2. **Docker** installed for building images
3. **AWS Account** with permissions for ECS, RDS, VPC, Secrets Manager, CloudFormation

### Automated Deployment

```bash
# Make the deployment script executable
chmod +x deploy-aws.sh

# Run the deployment
./deploy-aws.sh
```

The script will:
1. Create an ECR repository
2. Build and push the Docker image
3. Deploy the CloudFormation stack
4. Wait for the application to become healthy

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

1. **Build new image**:
   ```bash
   docker build -t letsgetcrypto:v2.0 .
   docker tag letsgetcrypto:v2.0 $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:v2.0
   docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/letsgetcrypto:v2.0
   ```

2. **Update ECS service**:
   ```bash
   # Update task definition with new image
   # Then update the service
   aws ecs update-service \
       --cluster letsgetcrypto-cluster \
       --service letsgetcrypto-service \
       --task-definition letsgetcrypto-api:2
   ```

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

## 🧪 Testing

### Local Testing with Docker Compose

Test the production configuration locally:

```bash
# Start services
docker-compose up --build

# Test endpoints
curl http://localhost/api/health/
curl http://localhost/api/market/

# Stop services
docker-compose down
```

### Automated Testing

```bash
# Run deployment readiness tests
python test_aws_deployment.py --url http://your-load-balancer-url
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

## 📞 Support

For issues related to:
- **AWS Infrastructure**: Check CloudFormation events and CloudWatch logs
- **Application Code**: Review application logs in CloudWatch
- **Database Issues**: Monitor RDS CloudWatch metrics
- **Network Issues**: Check VPC Flow Logs and security groups

---

**Note**: This deployment guide assumes basic familiarity with AWS services. For production deployments, consider additional monitoring, backup strategies, and security hardening based on your specific requirements.