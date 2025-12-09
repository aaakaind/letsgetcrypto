# Google Cloud Platform Deployment Files

This directory contains all necessary files for deploying LetsGetCrypto to Google Cloud Platform.

## 📁 Files Overview

### Infrastructure as Code (Terraform)

- **`main.tf`**: Complete Terraform configuration for GCP infrastructure
  - Cloud Run service for application hosting
  - Cloud SQL PostgreSQL database
  - VPC network and serverless VPC connector
  - Secret Manager for secure credential storage
  - IAM roles and permissions
  
- **`terraform.tfvars.example`**: Example variables file
  - Copy to `terraform.tfvars` and customize
  - Contains all configurable parameters

### Deployment Scripts

- **`deploy-gcp.sh`**: Automated deployment script
  - Validates prerequisites
  - Builds and pushes Docker image
  - Deploys infrastructure with Terraform
  - Displays deployment information
  - **Usage**: `./deploy-gcp.sh`

### CI/CD Configuration

- **`cloudbuild.yaml`**: Google Cloud Build configuration
  - Automated Docker image builds
  - Push to Google Container Registry
  - Deploy to Cloud Run
  - Triggered by Git commits

### Alternative Deployment Options

- **`app.yaml`**: Google App Engine configuration
  - Alternative to Cloud Run
  - Simpler deployment model
  - Integrated services
  - **Usage**: `gcloud app deploy app.yaml`

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Ensure prerequisites are installed (gcloud, docker, terraform)
# 2. Set your GCP project
export GCP_PROJECT_ID="your-project-id"

# 3. Run deployment script
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### Option 2: Manual Terraform Deployment

```bash
# 1. Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# 2. Build and push Docker image
gcloud builds submit --tag gcr.io/PROJECT_ID/letsgetcrypto ..

# 3. Initialize Terraform
terraform init

# 4. Plan and apply
terraform plan
terraform apply
```

### Option 3: App Engine Deployment

```bash
# 1. Edit app.yaml with your project settings
nano app.yaml

# 2. Deploy
gcloud app deploy app.yaml
```

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
   ```bash
   gcloud --version
   gcloud init
   ```
3. **Docker** installed and running
   ```bash
   docker --version
   ```
4. **Terraform** installed (for IaC deployment)
   ```bash
   terraform --version
   ```

## 🔧 Configuration

### Environment Variables

Set these before running deployment:

```bash
export GCP_PROJECT_ID="your-project-id"    # Required
export GCP_REGION="us-central1"            # Optional, default: us-central1
export DB_TIER="db-f1-micro"               # Optional, default: db-f1-micro
```

### Terraform Variables

Edit `terraform.tfvars` to customize:

- **project_id**: Your GCP project ID
- **region**: Deployment region (e.g., us-central1, europe-west1)
- **app_name**: Application name (default: letsgetcrypto)
- **db_tier**: Cloud SQL instance tier
  - `db-f1-micro`: Shared-core, development/testing
  - `db-n1-standard-1`: 1 vCPU, production
- **min_instances**: Minimum Cloud Run instances (0 for cost savings)
- **max_instances**: Maximum Cloud Run instances (for auto-scaling)

## 💰 Cost Estimates

### Cloud Run + Cloud SQL (Recommended)

| Component | Configuration | Estimated Cost/Month |
|-----------|--------------|---------------------|
| Cloud Run | 2M requests, 100 hours | $5-10 |
| Cloud SQL | db-f1-micro, 10GB | $7-10 |
| VPC Connector | 1 connector | $7 |
| Networking | Egress traffic | $1-5 |
| **Total** | | **$20-32/month** |

*Note: Cloud Run has a generous free tier (2M requests/month)*

### App Engine

| Component | Configuration | Estimated Cost/Month |
|-----------|--------------|---------------------|
| App Engine | F2 instance, 730 hours | $20-30 |
| Cloud SQL | db-f1-micro, 10GB | $7-10 |
| Networking | Egress traffic | $1-5 |
| **Total** | | **$28-45/month** |

## 🔍 Monitoring

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read letsgetcrypto --region=us-central1 --limit=50

# Tail logs in real-time
gcloud run services logs tail letsgetcrypto --region=us-central1

# Filter by severity
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=50
```

### View Service Status

```bash
# Cloud Run service details
gcloud run services describe letsgetcrypto --region=us-central1

# List revisions
gcloud run revisions list --service=letsgetcrypto --region=us-central1

# View metrics
gcloud monitoring dashboards list
```

## 🔄 Updates

### Deploy New Version

```bash
# Build new image
gcloud builds submit --tag gcr.io/PROJECT_ID/letsgetcrypto:v2 ..

# Deploy new revision
gcloud run deploy letsgetcrypto \
  --image gcr.io/PROJECT_ID/letsgetcrypto:v2 \
  --region us-central1
```

### Rollback to Previous Version

```bash
# List revisions
gcloud run revisions list --service=letsgetcrypto --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic letsgetcrypto \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```

## 🗑️ Cleanup

### Remove All Resources

```bash
# Using Terraform
terraform destroy

# Or manually
gcloud run services delete letsgetcrypto --region=us-central1
gcloud sql instances delete letsgetcrypto-db-instance
gcloud compute networks vpc-access connectors delete letsgetcrypto-connector --region=us-central1
```

## 📚 Documentation

- **[GCP_DEPLOYMENT.md](../GCP_DEPLOYMENT.md)**: Comprehensive deployment guide
- **[Cloud Run Documentation](https://cloud.google.com/run/docs)**
- **[Cloud SQL Documentation](https://cloud.google.com/sql/docs)**
- **[Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)**

## 🆘 Troubleshooting

### Common Issues

**Issue**: "Permission denied" errors
```bash
# Solution: Ensure you have required roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:YOUR_EMAIL" \
  --role="roles/run.admin"
```

**Issue**: Database connection fails
```bash
# Solution: Check Cloud SQL connection name
gcloud sql instances describe letsgetcrypto-db-instance \
  --format='value(connectionName)'
```

**Issue**: Build fails in Cloud Build
```bash
# Solution: View build logs
gcloud builds list --limit=10
gcloud builds log BUILD_ID
```

For more help, see [GCP_DEPLOYMENT.md](../GCP_DEPLOYMENT.md#troubleshooting).

## 🎯 Next Steps

After successful deployment:

1. **Test your deployment**: `curl https://YOUR_SERVICE_URL/api/health/`
2. **Set up custom domain**: Map your domain to Cloud Run
3. **Configure monitoring**: Set up uptime checks and alerts
4. **Enable Cloud Armor**: Add DDoS protection
5. **Review costs**: Monitor billing in GCP Console

---

**For detailed deployment instructions, see [GCP_DEPLOYMENT.md](../GCP_DEPLOYMENT.md)**
