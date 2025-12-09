# 🚀 LetsGetCrypto Deployment Guide

**Complete guide for deploying LetsGetCrypto to production.**

Version: `1.0.0`  
Last Updated: October 2025

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Options](#deployment-options)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Post-Deployment Validation](#post-deployment-validation)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## 🎯 Quick Start

**Choose your deployment method:**

| Method | Time | Difficulty | Cost/Month | Best For |
|--------|------|------------|------------|----------|
| **Docker Compose** | 5 min | Easy | $0 (local) | Development, testing |
| **AWS Elastic Beanstalk** | 10 min | Easy | $30-50 | Small production apps |
| **AWS ECS Fargate** | 15 min | Medium | $50-100 | Production apps |
| **GCP Cloud Run** | 10 min | Easy | $20-40 | Serverless production |
| **GCP App Engine** | 10 min | Easy | $25-50 | Simple production |
| **GitHub Pages** | 5 min | Easy | $0 | Static dashboard only |

### Fastest Path to Production

```bash
# 1. Validate your deployment
./validate-deployment.sh

# 2. Create deployment package
./package-for-aws.sh 1.0.0

# 3. Deploy to AWS
./deploy-aws.sh

# 4. Verify deployment
curl https://your-url.amazonaws.com/api/health/
```

---

## ✅ Pre-Deployment Checklist

Use the automated validation script:

```bash
./validate-deployment.sh
```

Or manually verify:

### Essential Requirements

- [ ] **Python 3.11+** installed
- [ ] **Docker** installed and running
- [ ] **AWS CLI v2** configured (for AWS deployments)
- [ ] **Git** repository is clean and up to date
- [ ] **Environment variables** configured (see `.env.production.template`)

### Security Checklist

- [ ] `DJANGO_DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY` (50+ characters)
- [ ] `DJANGO_ALLOWED_HOSTS` set to your domain
- [ ] Database credentials stored securely
- [ ] No API keys committed to repository
- [ ] SSL/HTTPS configured on load balancer

### Configuration Checklist

- [ ] Database is running and accessible
- [ ] Required environment variables set
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Health check endpoints working

**See [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for complete checklist.**

---

## 🎯 Deployment Options

### Option 1: Local Development with Docker Compose

**Best for:** Development, testing, demos

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your settings

# 2. Start services
docker-compose up -d

# 3. Access application
open http://localhost:8000/api/dashboard/
```

**Cleanup:**
```bash
docker-compose down -v
```

---

### Option 2: AWS Elastic Beanstalk

**Best for:** Simple production deployments, small apps

#### Prerequisites
- AWS account with appropriate permissions
- AWS CLI configured

#### Deployment Steps

```bash
# 1. Create deployment package
./package-for-aws.sh 1.0.0

# 2. Upload to Elastic Beanstalk
# - Go to AWS Elastic Beanstalk Console
# - Click "Create Application"
# - Upload: aws-packages/letsgetcrypto-beanstalk-*.zip
# - Platform: Python 3.11
# - Click "Create Environment"

# 3. Wait for deployment (5-10 minutes)
# 4. Get your application URL from the console
```

**Configuration:**
- Set environment variables in EB console
- Configure database (RDS recommended)
- Enable HTTPS with ACM certificate

**Cost:** ~$30-50/month

---

### Option 3: AWS ECS Fargate (Recommended for Production)

**Best for:** Production applications, high traffic, scalability

#### Prerequisites
- AWS account with appropriate permissions
- Docker installed and running
- AWS CLI v2 configured

#### Automated Deployment

```bash
# 1. Package application
./package-for-aws.sh 1.0.0

# 2. Extract and deploy
cd aws-packages
unzip letsgetcrypto-cloudformation-*.zip
cd letsgetcrypto-cloudformation-*

# 3. Deploy
chmod +x deploy-aws.sh
./deploy-aws.sh
```

The script will:
- ✅ Build Docker image
- ✅ Create ECR repository
- ✅ Push image to ECR
- ✅ Deploy CloudFormation stack
- ✅ Create VPC, subnets, security groups
- ✅ Create ECS cluster and service
- ✅ Create RDS PostgreSQL database
- ✅ Create Application Load Balancer
- ✅ Configure health checks
- ✅ Set up CloudWatch logging

**Deployment time:** 10-15 minutes

#### Manual Deployment

See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for detailed manual steps.

**Cost:** ~$50-100/month

---

### Option 4: Google Cloud Run (Serverless Production)

**Best for:** Serverless production, automatic scaling, pay-per-use

#### Prerequisites
- Google Cloud account with billing enabled
- gcloud CLI configured
- Docker installed

#### Automated Deployment

```bash
# Navigate to GCP directory
cd gcp

# Set your project
export GCP_PROJECT_ID="your-project-id"

# Run deployment script
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

The script will:
- ✅ Enable required GCP APIs
- ✅ Build and push Docker image to GCR
- ✅ Deploy Cloud Run service
- ✅ Create Cloud SQL database
- ✅ Set up VPC networking
- ✅ Configure secrets in Secret Manager

**Deployment time:** 10-15 minutes

See [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) for detailed instructions.

**Cost:** ~$20-40/month

---

### Option 5: GitHub Pages (Static Dashboard)

**Best for:** Static demo, documentation, marketing

```bash
# 1. Enable GitHub Pages
# - Go to repository Settings → Pages
# - Source: Deploy from branch
# - Branch: main, folder: /docs

# 2. Dashboard will be available at:
# https://yourusername.github.io/letsgetcrypto/
```

**Note:** This deploys only the static dashboard, not the full API.

See [GITHUB_PAGES.md](GITHUB_PAGES.md) for details.

---

## 📝 Step-by-Step Deployment

### Step 1: Prepare Your Environment

```bash
# Clone repository
git clone https://github.com/yourusername/letsgetcrypto.git
cd letsgetcrypto

# Create production configuration
cp .env.production.template .env
# Edit .env with production values

# Validate configuration
./validate-deployment.sh
```

### Step 2: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test server
python manage.py runserver

# Test in another terminal
curl http://localhost:8000/api/health/
```

### Step 3: Build and Test Docker Image

```bash
# Build image
docker build -t letsgetcrypto:test .

# Test image locally
docker run -d -p 8000:8000 \
  -e DJANGO_DEBUG=False \
  -e DJANGO_SECRET_KEY=test-key \
  -e DJANGO_ALLOWED_HOSTS=* \
  letsgetcrypto:test

# Test
curl http://localhost:8000/api/health/

# Stop container
docker stop $(docker ps -q --filter ancestor=letsgetcrypto:test)
```

### Step 4: Deploy to AWS

```bash
# Option A: Automated deployment
./deploy-aws.sh

# Option B: Package and deploy manually
./package-for-aws.sh 1.0.0
# Follow instructions in the package
```

### Step 5: Configure DNS (Optional)

```bash
# Get load balancer URL
aws cloudformation describe-stacks \
  --stack-name letsgetcrypto-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
  --output text

# Create CNAME record in your DNS
# api.yourdomain.com → load-balancer-url.elb.amazonaws.com
```

### Step 6: Enable HTTPS (Recommended)

```bash
# 1. Request ACM certificate
aws acm request-certificate \
  --domain-name api.yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# 2. Validate certificate via DNS

# 3. Attach to load balancer
# Update CloudFormation template or use AWS console
```

---

## ✅ Post-Deployment Validation

### Automated Validation

```bash
# Set your deployment URL
export DEPLOY_URL="https://your-url.amazonaws.com"

# Test health check
curl -f $DEPLOY_URL/api/health/ || echo "Health check failed"

# Test readiness
curl -f $DEPLOY_URL/api/readiness/ || echo "Readiness check failed"

# Test API endpoints
curl $DEPLOY_URL/api/market/ | jq .
curl $DEPLOY_URL/api/price/bitcoin/ | jq .
```

### Manual Testing

1. **Health Check**: Visit `https://your-url/api/health/`
   - Should return: `{"status": "healthy", "version": "1.0.0", ...}`

2. **Dashboard**: Visit `https://your-url/api/dashboard/`
   - Should load the web interface

3. **API Endpoints**: Test key endpoints
   ```bash
   # Market overview
   curl https://your-url/api/market/
   
   # Bitcoin price
   curl https://your-url/api/price/bitcoin/
   
   # Historical data
   curl https://your-url/api/history/bitcoin/?days=7
   ```

4. **Performance**: Check response times
   ```bash
   time curl -s https://your-url/api/health/ > /dev/null
   # Should be < 2 seconds
   ```

---

## 📊 Monitoring and Maintenance

### CloudWatch Monitoring

```bash
# View logs
aws logs tail /aws/ecs/letsgetcrypto --follow

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=letsgetcrypto-service \
  --statistics Average \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300
```

### Health Monitoring

Set up automated health checks:

```bash
# Create health check script
cat > check_health.sh << 'EOF'
#!/bin/bash
DEPLOY_URL="https://your-url.amazonaws.com"
if ! curl -f $DEPLOY_URL/api/health/ > /dev/null 2>&1; then
    echo "Health check failed at $(date)"
    # Send alert (email, Slack, etc.)
fi
EOF

# Add to crontab (check every 5 minutes)
*/5 * * * * /path/to/check_health.sh
```

### Database Backups

```bash
# Enable automated backups in RDS
aws rds modify-db-instance \
  --db-instance-identifier letsgetcrypto-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Health Check Failing

**Symptoms:** Load balancer shows unhealthy targets

**Solutions:**
```bash
# Check application logs
aws logs tail /aws/ecs/letsgetcrypto --follow

# Check database connection
aws rds describe-db-instances \
  --db-instance-identifier letsgetcrypto-db

# Verify environment variables
aws ecs describe-task-definition \
  --task-definition letsgetcrypto-task | jq '.taskDefinition.containerDefinitions[0].environment'
```

#### 2. Database Connection Errors

**Symptoms:** "Could not connect to database" errors

**Solutions:**
```bash
# Check security groups
aws ec2 describe-security-groups \
  --filters Name=group-name,Values=letsgetcrypto-*

# Test database connectivity
nc -zv your-db-endpoint.rds.amazonaws.com 5432

# Verify DATABASE_URL format
# postgres://username:password@host:5432/database
```

#### 3. Static Files Not Loading

**Symptoms:** 404 errors for CSS/JS files

**Solutions:**
```bash
# Collect static files
docker exec -it container-id python manage.py collectstatic --noinput

# Verify STATIC_ROOT setting
docker exec -it container-id python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)"
```

#### 4. High CPU/Memory Usage

**Solutions:**
```bash
# Scale up ECS service
aws ecs update-service \
  --cluster letsgetcrypto-cluster \
  --service letsgetcrypto-service \
  --desired-count 3

# Or increase task resources in task definition
```

### Getting Help

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Django Documentation**: https://docs.djangoproject.com/
- **Project Issues**: https://github.com/yourusername/letsgetcrypto/issues
- **AWS Support**: https://console.aws.amazon.com/support/

---

## 🔄 Rollback Procedures

### Quick Rollback

If deployment fails or issues are detected:

```bash
# 1. List previous task definitions
aws ecs list-task-definitions \
  --family-prefix letsgetcrypto-task \
  --sort DESC

# 2. Update service to use previous version
aws ecs update-service \
  --cluster letsgetcrypto-cluster \
  --service letsgetcrypto-service \
  --task-definition letsgetcrypto-task:PREVIOUS_VERSION

# 3. Monitor rollback
aws ecs describe-services \
  --cluster letsgetcrypto-cluster \
  --services letsgetcrypto-service \
  --query 'services[0].deployments'
```

### Complete Stack Rollback

```bash
# Rollback to previous CloudFormation stack
aws cloudformation update-stack \
  --stack-name letsgetcrypto-stack \
  --use-previous-template
```

### Emergency Shutdown

```bash
# Scale down to zero
aws ecs update-service \
  --cluster letsgetcrypto-cluster \
  --service letsgetcrypto-service \
  --desired-count 0
```

---

## 📊 Cost Management

### Estimated Costs

| Component | Cost/Month | Notes |
|-----------|------------|-------|
| ECS Fargate (2 tasks) | $30-40 | 0.25 vCPU, 0.5 GB each |
| RDS PostgreSQL (db.t3.micro) | $15-20 | Single-AZ, 20GB storage |
| Application Load Balancer | $16-20 | Standard pricing |
| Data Transfer | $5-10 | Depends on traffic |
| CloudWatch Logs | $5 | 5GB/month |
| **Total** | **$71-95/month** | Approximate |

### Cost Optimization

```bash
# 1. Use Savings Plans for ECS
# 2. Schedule tasks (stop during off-hours)
# 3. Use reserved RDS instances
# 4. Enable VPC endpoints (reduce data transfer)
# 5. Clean up old ECR images
aws ecr batch-delete-image \
  --repository-name letsgetcrypto \
  --image-ids "$(aws ecr list-images --repository-name letsgetcrypto --query 'imageIds[?imageTag!=`latest`]' --output json)"
```

---

## 🔐 Security Best Practices

1. **Secrets Management**
   - Use AWS Secrets Manager
   - Rotate credentials regularly
   - Never commit secrets to Git

2. **Network Security**
   - Use VPC with private subnets
   - Restrict security group rules
   - Enable WAF on load balancer

3. **Application Security**
   - Keep dependencies updated
   - Run security scans regularly
   - Enable HTTPS only
   - Use strong authentication

4. **Monitoring**
   - Enable CloudWatch alarms
   - Monitor failed login attempts
   - Track API rate limits
   - Review access logs

---

## 📚 Additional Resources

- **[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)** - Complete pre-deployment checklist
- **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - Detailed AWS deployment guide
- **[GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)** - Detailed Google Cloud deployment guide
- **[CICD_GUIDE.md](CICD_GUIDE.md)** - CI/CD pipeline setup for AWS
- **[README.md](README.md)** - Project overview and features
- **[TESTING.md](TESTING.md)** - Testing documentation

---

## 🆘 Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for detailed info
3. Open an issue on GitHub
4. Contact AWS Support for infrastructure issues

---

**Last Updated:** October 2025  
**Version:** 1.0.0  
**Maintained By:** LetsGetCrypto Team
