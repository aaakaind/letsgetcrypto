#!/bin/bash

# LetsGetCrypto AWS Package Creation Script
# This script creates deployable packages for various AWS services

set -e

PACKAGE_VERSION=${1:-"1.0.0"}
OUTPUT_DIR="aws-packages"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "📦 Creating AWS Deployment Packages"
echo "===================================="
echo "Version: $PACKAGE_VERSION"
echo "Timestamp: $TIMESTAMP"
echo ""

# Clean and create output directory
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# =============================================================================
# Package 1: CloudFormation Deployment Package (Recommended for ECS Fargate)
# =============================================================================
echo "📦 Creating CloudFormation deployment package..."
CLOUDFORMATION_PACKAGE="$OUTPUT_DIR/letsgetcrypto-cloudformation-${PACKAGE_VERSION}-${TIMESTAMP}.zip"

# Create temporary directory for CloudFormation package
TEMP_CF_DIR=$(mktemp -d)

# Copy necessary files
cp -r aws $TEMP_CF_DIR/
cp Dockerfile $TEMP_CF_DIR/
cp requirements.txt $TEMP_CF_DIR/
cp deploy-aws.sh $TEMP_CF_DIR/
cp AWS_DEPLOYMENT.md $TEMP_CF_DIR/README.md
cp .dockerignore $TEMP_CF_DIR/ 2>/dev/null || true

# Copy application code (exclude unnecessary files)
mkdir -p $TEMP_CF_DIR/app
cp -r crypto_api $TEMP_CF_DIR/app/
cp -r letsgetcrypto_django $TEMP_CF_DIR/app/
cp manage.py $TEMP_CF_DIR/app/
cp requirements.txt $TEMP_CF_DIR/app/
cp -r static 2>/dev/null $TEMP_CF_DIR/app/ || mkdir -p $TEMP_CF_DIR/app/static

# Create deployment instructions
cat > $TEMP_CF_DIR/DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# CloudFormation/ECS Fargate Deployment Package

## Prerequisites
- AWS CLI v2 installed and configured
- Docker installed and running
- AWS account with appropriate permissions

## Quick Deployment

1. Extract this package:
   ```bash
   unzip letsgetcrypto-cloudformation-*.zip
   cd letsgetcrypto-cloudformation-*
   ```

2. Run the automated deployment script:
   ```bash
   chmod +x deploy-aws.sh
   ./deploy-aws.sh
   ```

## What Gets Deployed
- Amazon ECS Fargate cluster
- Application Load Balancer
- RDS PostgreSQL database
- VPC with public/private subnets
- CloudWatch logging
- AWS Secrets Manager for credentials

## Manual Deployment Steps
See README.md (AWS_DEPLOYMENT.md) for detailed manual deployment instructions.

## Estimated Cost
Approximately $50-100/month for small-scale usage with the default configuration.
EOF

# Create the CloudFormation package
CURRENT_DIR=$(pwd)
cd $TEMP_CF_DIR
zip -r $CURRENT_DIR/$CLOUDFORMATION_PACKAGE * >/dev/null
cd - >/dev/null

echo "✅ CloudFormation package created: $CLOUDFORMATION_PACKAGE"
echo ""

# =============================================================================
# Package 2: Elastic Beanstalk Package (Alternative simpler deployment)
# =============================================================================
echo "📦 Creating Elastic Beanstalk deployment package..."
BEANSTALK_PACKAGE="$OUTPUT_DIR/letsgetcrypto-beanstalk-${PACKAGE_VERSION}-${TIMESTAMP}.zip"

# Create temporary directory for Beanstalk package
TEMP_EB_DIR=$(mktemp -d)

# Copy application code
cp -r crypto_api $TEMP_EB_DIR/
cp -r letsgetcrypto_django $TEMP_EB_DIR/
cp manage.py $TEMP_EB_DIR/
cp requirements.txt $TEMP_EB_DIR/
mkdir -p $TEMP_EB_DIR/static

# Create .ebextensions directory for Elastic Beanstalk configuration
mkdir -p $TEMP_EB_DIR/.ebextensions

# Create Django configuration for Elastic Beanstalk
cat > $TEMP_EB_DIR/.ebextensions/01_django.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: "letsgetcrypto_django.settings"
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:container:python:
    WSGIPath: "letsgetcrypto_django.wsgi:application"

container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
    leader_only: true
EOF

# Create RDS configuration
cat > $TEMP_EB_DIR/.ebextensions/02_database.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:application:environment:
    DATABASE_URL: "postgresql://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT}/${RDS_DB_NAME}"
EOF

# Create Beanstalk platform configuration
mkdir -p $TEMP_EB_DIR/.platform/nginx/conf.d/
cat > $TEMP_EB_DIR/.platform/nginx/conf.d/proxy.conf << 'EOF'
client_max_body_size 20M;
EOF

# Create Procfile for Elastic Beanstalk
cat > $TEMP_EB_DIR/Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 60 letsgetcrypto_django.wsgi:application
EOF

# Create deployment instructions for Beanstalk
cat > $TEMP_EB_DIR/BEANSTALK_DEPLOYMENT.md << 'EOF'
# Elastic Beanstalk Deployment Package

## Prerequisites
- AWS CLI v2 installed and configured
- EB CLI installed: `pip install awsebcli`

## Quick Deployment

1. Extract this package:
   ```bash
   unzip letsgetcrypto-beanstalk-*.zip
   cd letsgetcrypto-beanstalk-*
   ```

2. Initialize Elastic Beanstalk:
   ```bash
   eb init -p python-3.11 letsgetcrypto --region us-east-1
   ```

3. Create an environment with RDS database:
   ```bash
   eb create letsgetcrypto-env \
     --database.engine postgres \
     --database.instance db.t3.micro \
     --instance-type t3.small \
     --envvars DJANGO_DEBUG=False,DJANGO_ALLOWED_HOSTS=*
   ```

4. Deploy the application:
   ```bash
   eb deploy
   ```

5. Open the application:
   ```bash
   eb open
   ```

## Alternative: Deploy via Console

1. Go to AWS Elastic Beanstalk Console
2. Click "Create Application"
3. Application name: "letsgetcrypto"
4. Platform: Python 3.11
5. Upload this ZIP file
6. Configure environment variables:
   - DJANGO_DEBUG=False
   - DJANGO_ALLOWED_HOSTS=*
7. Click "Create Environment"

## Configuration

Set these environment variables in the Elastic Beanstalk console:
- DJANGO_SECRET_KEY: (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
- DJANGO_ALLOWED_HOSTS: your-app-domain.elasticbeanstalk.com

## Estimated Cost
Approximately $30-50/month for small-scale usage with t3.small instance and db.t3.micro database.
EOF

# Create the Beanstalk package
cd $TEMP_EB_DIR
zip -r $CURRENT_DIR/$BEANSTALK_PACKAGE * .ebextensions .platform >/dev/null 2>&1
cd - >/dev/null

echo "✅ Elastic Beanstalk package created: $BEANSTALK_PACKAGE"
echo ""

# =============================================================================
# Package 3: Complete Source Package
# =============================================================================
echo "📦 Creating complete source package..."
SOURCE_PACKAGE="$OUTPUT_DIR/letsgetcrypto-source-${PACKAGE_VERSION}-${TIMESTAMP}.zip"

# Create temporary directory for source package
TEMP_SRC_DIR=$(mktemp -d)

# Copy all relevant files except build artifacts and dependencies
rsync -av --exclude='.git' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='venv' \
          --exclude='env' \
          --exclude='node_modules' \
          --exclude='.pytest_cache' \
          --exclude='*.egg-info' \
          --exclude='dist' \
          --exclude='build' \
          --exclude='aws-packages' \
          --exclude='*.log' \
          ./ $TEMP_SRC_DIR/ >/dev/null

# Create the source package
cd $TEMP_SRC_DIR
zip -r $CURRENT_DIR/$SOURCE_PACKAGE * .[^.]* >/dev/null 2>&1 || zip -r $CURRENT_DIR/$SOURCE_PACKAGE * >/dev/null
cd - >/dev/null

echo "✅ Complete source package created: $SOURCE_PACKAGE"
echo ""

# =============================================================================
# Create Package Summary
# =============================================================================
cat > $OUTPUT_DIR/PACKAGE_SUMMARY.md << EOF
# LetsGetCrypto AWS Deployment Packages

Generated: $(date)
Version: $PACKAGE_VERSION

## Available Packages

### 1. CloudFormation/ECS Fargate Package (Recommended)
**File**: \`$(basename $CLOUDFORMATION_PACKAGE)\`
**Size**: $(du -h $CLOUDFORMATION_PACKAGE | cut -f1)
**Best For**: Production deployments requiring scalability and full control

**Features**:
- Containerized deployment with ECS Fargate
- Auto-scaling capabilities
- Load balancer included
- Managed PostgreSQL database (RDS)
- Production-ready architecture

**To Deploy**:
\`\`\`bash
unzip $(basename $CLOUDFORMATION_PACKAGE)
chmod +x deploy-aws.sh
./deploy-aws.sh
\`\`\`

### 2. Elastic Beanstalk Package (Easiest)
**File**: \`$(basename $BEANSTALK_PACKAGE)\`
**Size**: $(du -h $BEANSTALK_PACKAGE | cut -f1)
**Best For**: Quick deployments and simpler management

**Features**:
- Simplified deployment process
- Automatic platform updates
- Integrated monitoring
- Lower cost for small applications
- Easy to deploy via console or CLI

**To Deploy**:
1. Go to AWS Elastic Beanstalk Console
2. Create new application
3. Upload ZIP file
4. Configure environment variables
5. Launch!

Or via CLI:
\`\`\`bash
unzip $(basename $BEANSTALK_PACKAGE)
eb init -p python-3.11 letsgetcrypto
eb create letsgetcrypto-env --database.engine postgres
\`\`\`

### 3. Complete Source Package
**File**: \`$(basename $SOURCE_PACKAGE)\`
**Size**: $(du -h $SOURCE_PACKAGE | cut -f1)
**Best For**: Custom deployments or development

**Features**:
- Complete application source code
- All configuration files
- Documentation
- Deploy to any platform

## Cost Estimates

| Package Type | Monthly Cost (Estimated) | Best For |
|--------------|-------------------------|----------|
| Elastic Beanstalk | \$30-50 | Small apps, testing |
| ECS Fargate | \$50-100 | Production, scaling |

## Next Steps

1. Choose the package that best fits your needs
2. Extract the package
3. Follow the included deployment instructions
4. Monitor your AWS costs in the AWS Cost Explorer

## Support

For detailed deployment instructions, see:
- CloudFormation: AWS_DEPLOYMENT.md in the package
- Elastic Beanstalk: BEANSTALK_DEPLOYMENT.md in the package
- Source: README.md

## Security Notes

- Always set strong passwords for databases
- Configure DJANGO_SECRET_KEY in production
- Set DJANGO_DEBUG=False in production
- Restrict DJANGO_ALLOWED_HOSTS to your domain
- Review AWS security group settings
- Enable AWS CloudTrail for audit logging
EOF

echo ""
echo "🎉 Package creation completed successfully!"
echo "=========================================="
echo ""
echo "📦 Packages created in: $OUTPUT_DIR/"
echo ""
ls -lh $OUTPUT_DIR/
echo ""
echo "📖 See $OUTPUT_DIR/PACKAGE_SUMMARY.md for detailed information"
echo ""
echo "🚀 Quick Start:"
echo "   For easiest deployment: Upload $(basename $BEANSTALK_PACKAGE) to Elastic Beanstalk"
echo "   For production deployment: Extract $(basename $CLOUDFORMATION_PACKAGE) and run deploy-aws.sh"
echo ""
