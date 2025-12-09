#!/bin/bash

# LetsGetCrypto Google Cloud Platform Deployment Script
# This script deploys the application to GCP using Cloud Run and Cloud SQL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="letsgetcrypto"
REGION="${GCP_REGION:-us-central1}"
DB_TIER="${DB_TIER:-db-f1-micro}"

echo "🚀 Starting LetsGetCrypto GCP Deployment"
echo "========================================"

# Check gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    echo "   Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${YELLOW}⚠️  Terraform is not installed. Installing...${NC}"
    echo "   Visit: https://www.terraform.io/downloads"
    echo "   Or run: brew install terraform  (on macOS)"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Get GCP project ID
if [ -z "$GCP_PROJECT_ID" ]; then
    GCP_PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo -e "${YELLOW}⚠️  GCP project not set. Please run:${NC}"
        echo "   gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

echo -e "${GREEN}📋 GCP Project ID: $GCP_PROJECT_ID${NC}"

# Enable required GCP APIs
echo "🔧 Enabling required GCP APIs..."
gcloud services enable \
    compute.googleapis.com \
    sqladmin.googleapis.com \
    run.googleapis.com \
    vpcaccess.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    --project=$GCP_PROJECT_ID \
    --quiet

# Configure Docker for GCR
echo "🔑 Configuring Docker for Google Container Registry..."
gcloud auth configure-docker --quiet

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t gcr.io/$GCP_PROJECT_ID/$APP_NAME:latest ..

# Push image to GCR
echo "📤 Pushing image to Google Container Registry..."
docker push gcr.io/$GCP_PROJECT_ID/$APP_NAME:latest

# Generate secure passwords if not set
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    echo -e "${YELLOW}📝 Generated database password${NC}"
fi

if [ -z "$DJANGO_SECRET_KEY" ]; then
    DJANGO_SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/")
    echo -e "${YELLOW}📝 Generated Django secret key${NC}"
fi

# Create terraform.tfvars if it doesn't exist
if [ ! -f terraform.tfvars ]; then
    echo "📝 Creating terraform.tfvars..."
    cat > terraform.tfvars <<EOF
project_id        = "$GCP_PROJECT_ID"
region            = "$REGION"
app_name          = "$APP_NAME"
db_tier           = "$DB_TIER"
db_password       = "$DB_PASSWORD"
django_secret_key = "$DJANGO_SECRET_KEY"
container_image   = "gcr.io/$GCP_PROJECT_ID/$APP_NAME:latest"
min_instances     = 0
max_instances     = 10
EOF
    echo -e "${GREEN}✅ Created terraform.tfvars${NC}"
fi

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning Terraform deployment..."
terraform plan

# Ask for confirmation
echo ""
read -p "Do you want to proceed with the deployment? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Apply Terraform configuration
echo "🚀 Deploying infrastructure..."
terraform apply -auto-approve

# Get the service URL
SERVICE_URL=$(terraform output -raw service_url 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo ""
    echo "========================================"
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo "========================================"
    echo ""
    echo "Your application is available at:"
    echo -e "${GREEN}$SERVICE_URL${NC}"
    echo ""
    echo "Test your deployment:"
    echo "  curl $SERVICE_URL/api/health/"
    echo "  curl $SERVICE_URL/api/market/"
    echo ""
    echo "View logs:"
    echo "  gcloud run services logs read $APP_NAME --region=$REGION"
    echo ""
    echo "To update your deployment:"
    echo "  1. Build new image: docker build -t gcr.io/$GCP_PROJECT_ID/$APP_NAME:latest .."
    echo "  2. Push to GCR: docker push gcr.io/$GCP_PROJECT_ID/$APP_NAME:latest"
    echo "  3. Deploy new revision: gcloud run deploy $APP_NAME --image gcr.io/$GCP_PROJECT_ID/$APP_NAME:latest --region=$REGION"
    echo ""
    echo "To cleanup all resources:"
    echo "  terraform destroy"
    echo ""
else
    echo -e "${RED}❌ Deployment may have failed. Check terraform output.${NC}"
    exit 1
fi
