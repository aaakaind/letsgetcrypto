# AWS Deployment Packaging Guide

This guide explains how to create and use deployment packages for AWS services.

## 🎯 Overview

The `package-for-aws.sh` script creates ready-to-deploy packages optimized for different AWS services. This eliminates the need to manually build Docker images or configure deployment files.

## 📦 Available Packages

### 1. CloudFormation/ECS Fargate Package
**File**: `letsgetcrypto-cloudformation-{version}-{timestamp}.zip`

**Best For**:
- Production deployments
- Applications requiring auto-scaling
- High availability requirements
- Full infrastructure control

**What's Included**:
- Pre-configured CloudFormation template
- ECS task definitions
- Dockerfile for containerization
- Automated deployment script
- Complete application code
- Documentation

**Deployment Method**:
1. Extract the package
2. Run `./deploy-aws.sh`
3. Wait 10-15 minutes
4. Application is live!

**AWS Services Used**:
- ECS Fargate (serverless containers)
- Application Load Balancer
- RDS PostgreSQL
- VPC with public/private subnets
- CloudWatch Logs
- Secrets Manager

**Estimated Monthly Cost**: $50-100

### 2. Elastic Beanstalk Package
**File**: `letsgetcrypto-beanstalk-{version}-{timestamp}.zip`

**Best For**:
- Quick deployments
- Testing environments
- Small to medium applications
- Teams preferring managed services

**What's Included**:
- Application code
- `.ebextensions/` configuration
- `.platform/` custom configuration
- Procfile for process management
- Requirements and dependencies
- Deployment documentation

**Deployment Method**:
- **Via Console**: Upload ZIP to AWS Elastic Beanstalk Console
- **Via CLI**: Use `eb create` command

**AWS Services Used**:
- Elastic Beanstalk (Python 3.11)
- EC2 instances (managed by Beanstalk)
- RDS PostgreSQL (optional)
- Load Balancer (auto-configured)

**Estimated Monthly Cost**: $30-50

### 3. Complete Source Package
**File**: `letsgetcrypto-source-{version}-{timestamp}.zip`

**Best For**:
- Custom deployment scenarios
- CI/CD pipelines
- Development environments
- Version control/backup

**What's Included**:
- Complete source code
- All configuration files
- Documentation
- Scripts and utilities

## 🚀 Quick Start

### Step 1: Create Packages

```bash
# Make the script executable (first time only)
chmod +x package-for-aws.sh

# Create packages with version number
./package-for-aws.sh 1.0.0

# Or create with default version
./package-for-aws.sh
```

Output:
```
📦 Creating AWS Deployment Packages
====================================
Version: 1.0.0
Timestamp: 20251008-003556

✅ CloudFormation package created
✅ Elastic Beanstalk package created
✅ Complete source package created

Packages created in: aws-packages/
```

### Step 2: Choose Your Deployment Method

#### For Easiest Deployment (Elastic Beanstalk)

**Console Method** (No command line needed):
1. Go to [AWS Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk)
2. Click "Create Application"
3. Upload `letsgetcrypto-beanstalk-*.zip`
4. Configure environment variables
5. Launch!

**CLI Method**:
```bash
# Extract package
unzip aws-packages/letsgetcrypto-beanstalk-*.zip -d deploy-eb
cd deploy-eb

# Install EB CLI if needed
pip install awsebcli

# Initialize and deploy
eb init -p python-3.11 letsgetcrypto --region us-east-1
eb create letsgetcrypto-env --database.engine postgres
eb open
```

#### For Production Deployment (CloudFormation/ECS)

```bash
# Extract package
unzip aws-packages/letsgetcrypto-cloudformation-*.zip -d deploy-cf
cd deploy-cf

# Deploy (requires Docker)
chmod +x deploy-aws.sh
./deploy-aws.sh
```

## 📋 Package Contents

### CloudFormation Package Structure
```
letsgetcrypto-cloudformation-*.zip
├── DEPLOYMENT_INSTRUCTIONS.md
├── README.md (AWS_DEPLOYMENT.md)
├── Dockerfile
├── deploy-aws.sh
├── requirements.txt
├── .dockerignore
├── aws/
│   ├── cloudformation-template.yaml
│   └── ecs-task-definition.json
└── app/
    ├── crypto_api/
    ├── letsgetcrypto_django/
    ├── manage.py
    └── requirements.txt
```

### Elastic Beanstalk Package Structure
```
letsgetcrypto-beanstalk-*.zip
├── BEANSTALK_DEPLOYMENT.md
├── Procfile
├── requirements.txt
├── manage.py
├── crypto_api/
├── letsgetcrypto_django/
├── .ebextensions/
│   ├── 01_django.config
│   └── 02_database.config
└── .platform/
    └── nginx/
        └── conf.d/
            └── proxy.conf
```

## 🔧 Configuration

### Environment Variables

Both packages support these environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_DEBUG` | Debug mode | `False` | No |
| `DJANGO_SECRET_KEY` | Secret key | - | Yes |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | `*` | No |
| `DATABASE_URL` | Database connection | Auto-generated | Yes |

### Setting Environment Variables

**Elastic Beanstalk**:
- Console: Configuration → Software → Environment properties
- CLI: `eb setenv VARIABLE=value`

**CloudFormation/ECS**:
- Stored in AWS Secrets Manager
- Auto-configured by deployment script

## 💰 Cost Comparison

| Package Type | Monthly Cost | Services | Best For |
|--------------|--------------|----------|----------|
| Elastic Beanstalk | $30-50 | EC2 t3.small + RDS t3.micro | Testing, small apps |
| ECS Fargate | $50-100 | Fargate tasks + RDS + ALB | Production, scaling |

**Cost factors**:
- Instance/container size
- Database size
- Data transfer
- Storage
- Backup retention

**Cost optimization tips**:
- Use smaller instance types for testing
- Delete resources when not in use
- Use RDS reserved instances for production
- Enable auto-scaling to match demand

## 🧪 Testing Packages Locally

Before deploying to AWS, test the packages locally:

### Test Elastic Beanstalk Package
```bash
# Extract package
unzip aws-packages/letsgetcrypto-beanstalk-*.zip -d test-eb
cd test-eb

# Install dependencies
pip install -r requirements.txt

# Run locally
python manage.py migrate
python manage.py runserver
```

### Test CloudFormation Package
```bash
# Extract package
unzip aws-packages/letsgetcrypto-cloudformation-*.zip -d test-cf
cd test-cf/app

# Use Docker Compose (if available in package)
docker-compose up
```

## 🔍 Troubleshooting

### Package Creation Fails

**Issue**: Script fails with "command not found"
**Solution**: Ensure `zip` and `rsync` are installed:
```bash
# Ubuntu/Debian
sudo apt-get install zip rsync

# macOS
brew install rsync
```

**Issue**: "No such file or directory" errors
**Solution**: Run the script from the repository root:
```bash
cd /path/to/letsgetcrypto
./package-for-aws.sh
```

### Deployment Issues

**Issue**: Elastic Beanstalk health check fails
**Solution**: Check that:
- `DJANGO_ALLOWED_HOSTS` includes the Beanstalk URL
- Database connection is configured
- Static files are collected

**Issue**: ECS task fails to start
**Solution**: Check CloudWatch logs:
```bash
aws logs tail /ecs/letsgetcrypto-api --follow
```

## 📚 Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)

## 🔐 Security Best Practices

1. **Always use secure passwords** for databases
2. **Generate a strong Django secret key**:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. **Set `DJANGO_DEBUG=False`** in production
4. **Restrict `DJANGO_ALLOWED_HOSTS`** to your domain
5. **Enable AWS CloudTrail** for audit logging
6. **Use IAM roles** with least privilege
7. **Enable encryption** for RDS and S3
8. **Review security groups** regularly

## 🤝 Support

For issues or questions:
1. Check the package's included documentation
2. Review AWS service documentation
3. Check CloudWatch logs for errors
4. Verify environment variables are set correctly

## 📝 Version History

- **v1.0.0**: Initial release with CloudFormation, Elastic Beanstalk, and source packages
