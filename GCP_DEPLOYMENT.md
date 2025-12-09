# Google Cloud Platform Deployment Guide for LetsGetCrypto

This comprehensive guide provides step-by-step instructions for deploying the LetsGetCrypto application to Google Cloud Platform using Cloud Run, App Engine, or Google Kubernetes Engine.

## 🏗️ Architecture Overview

The GCP deployment includes:

- **Cloud Run**: Serverless container platform with automatic scaling (Recommended)
- **Cloud SQL PostgreSQL**: Fully managed database with automated backups
- **Secret Manager**: Secure credential storage and rotation
- **Cloud Logging**: Centralized logging and monitoring
- **VPC Network**: Isolated network with serverless VPC access
- **Container Registry (GCR)**: Container image storage
- **Cloud Build**: CI/CD pipeline for automated deployments

## 🚀 Quick Deployment

### Prerequisites

Before deploying, ensure you have:

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured:
   ```bash
   gcloud --version  # Should show gcloud SDK version
   gcloud init       # Set up your credentials and project
   ```

3. **Docker** installed and running:
   ```bash
   docker --version  # Verify installation
   docker ps         # Check Docker is running
   ```

4. **Terraform** installed (for infrastructure as code):
   ```bash
   terraform --version  # Should show v1.0 or higher
   # Install: https://www.terraform.io/downloads
   ```

5. **GCP Project** with appropriate permissions:
   - Cloud Run Admin
   - Cloud SQL Admin
   - Compute Network Admin
   - Secret Manager Admin
   - Service Account User

### Automated Deployment (Recommended)

The automated script handles all deployment steps:

```bash
# Navigate to GCP directory
cd gcp

# Make the deployment script executable
chmod +x deploy-gcp.sh

# Set your GCP project (or script will use current project)
export GCP_PROJECT_ID="your-project-id"

# Run the deployment
./deploy-gcp.sh
```

**What the script does:**
1. ✅ Validates prerequisites (gcloud CLI, Docker, Terraform)
2. ✅ Enables required GCP APIs
3. ✅ Builds and pushes the Docker image to Google Container Registry
4. ✅ Generates secure database password and Django secret key
5. ✅ Creates Terraform configuration
6. ✅ Deploys infrastructure (VPC, Cloud SQL, Cloud Run)
7. ✅ Displays deployment information and testing commands

**Deployment time:** Approximately 10-15 minutes

## 📦 Deployment Options

### Option 1: Cloud Run (Recommended for Production)

**Best for:** Production deployments, automatic scaling, serverless

#### Using Terraform (Infrastructure as Code)

```bash
cd gcp

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

#### Using gcloud CLI (Quick Deploy)

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/letsgetcrypto

# Deploy to Cloud Run
gcloud run deploy letsgetcrypto \
  --image gcr.io/PROJECT_ID/letsgetcrypto:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars DJANGO_DEBUG=False,DJANGO_ALLOWED_HOSTS=* \
  --add-cloudsql-instances PROJECT_ID:us-central1:letsgetcrypto-db-instance \
  --min-instances 0 \
  --max-instances 10 \
  --cpu 1 \
  --memory 512Mi
```

**Cost:** ~$20-40/month (with generous free tier)

---

### Option 2: App Engine

**Best for:** Simple deployment, automatic SSL, integrated services

```bash
cd gcp

# Copy and edit app.yaml
cp app.yaml.example app.yaml
nano app.yaml  # Update PROJECT_ID and other settings

# Deploy to App Engine
gcloud app deploy app.yaml

# View your application
gcloud app browse
```

**Cost:** ~$25-50/month

---

### Option 3: Google Kubernetes Engine (GKE)

**Best for:** Complex applications, multi-service deployments, advanced orchestration

See [GKE_DEPLOYMENT.md](GKE_DEPLOYMENT.md) for detailed GKE instructions.

**Cost:** ~$70-150/month

---

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

### Google Secret Manager

Sensitive configuration is stored in Secret Manager:

- `letsgetcrypto-django-secret`: Django secret key
- `letsgetcrypto-db-password`: Database password

Access secrets:
```bash
# View secret
gcloud secrets versions access latest --secret="letsgetcrypto-django-secret"

# Create new secret
gcloud secrets create my-secret --data-file=./secret.txt
```

## 🔄 CI/CD Pipeline

### Setting Up Cloud Build

1. **Create Cloud Build trigger:**
```bash
gcloud builds triggers create github \
  --repo-name=letsgetcrypto \
  --repo-owner=aaakaind \
  --branch-pattern="^main$" \
  --build-config=gcp/cloudbuild.yaml
```

2. **Manual trigger:**
```bash
gcloud builds submit --config=gcp/cloudbuild.yaml
```

3. **Monitor builds:**
```bash
# List recent builds
gcloud builds list --limit=10

# View build logs
gcloud builds log BUILD_ID
```

### Cloud Build Configuration

The build process defined in `cloudbuild.yaml`:

- Automated Docker image builds
- Push to Google Container Registry
- Optional database migrations
- Deploy to Cloud Run
- Build caching for faster builds

## 🏥 Health Checks

The application provides multiple health check endpoints:

### Cloud Run Health Check
- **Endpoint**: `/api/health/`
- **Method**: GET
- **Success**: HTTP 200 with `{"status": "healthy"}`
- **Failure**: HTTP 503 with error details

### Readiness Check
- **Endpoint**: `/api/readiness/`
- **Method**: GET
- **Purpose**: Check if application is ready to serve traffic

### Liveness Check
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
Get current price for a specific cryptocurrency.

### Historical Data
```bash
GET /api/history/{symbol}/?days=30
```
Get historical price data for a cryptocurrency.

## 🔍 Monitoring and Logging

### Cloud Logging

View application logs:
```bash
# Tail logs from Cloud Run
gcloud run services logs read letsgetcrypto --region=us-central1 --limit=50

# Follow logs in real-time
gcloud run services logs tail letsgetcrypto --region=us-central1

# Filter logs by severity
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=50
```

### Cloud Monitoring

Set up monitoring dashboards and alerts:

```bash
# Create uptime check
gcloud monitoring uptime create https \
  --display-name="LetsGetCrypto Health Check" \
  --resource-type=uptime-url \
  --hostname=YOUR_SERVICE_URL \
  --path=/api/health/

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s
```

### Key Metrics to Monitor

1. **Request Count**: Monitor API request volume
2. **Response Times**: Track API latency
3. **Error Rates**: Monitor 4xx and 5xx responses
4. **Database Connections**: Monitor Cloud SQL connections
5. **Container Instances**: Monitor Cloud Run instance count

## 🔄 Updates and Maintenance

### Updating the Application

When you make code changes:

```bash
# 1. Build new image
gcloud builds submit --tag gcr.io/PROJECT_ID/letsgetcrypto:v2

# 2. Deploy new revision
gcloud run deploy letsgetcrypto \
  --image gcr.io/PROJECT_ID/letsgetcrypto:v2 \
  --region us-central1

# 3. Monitor deployment
gcloud run revisions list --service=letsgetcrypto --region=us-central1
```

**Note**: Cloud Run will perform a gradual rollout, routing traffic to the new revision.

### Database Migrations

For database schema changes:

```bash
# Option 1: Run migrations in Cloud Build (recommended)
# Add migration step to cloudbuild.yaml

# Option 2: Run migrations from local machine
gcloud run jobs create migrate-db \
  --image gcr.io/PROJECT_ID/letsgetcrypto:latest \
  --region us-central1 \
  --command python \
  --args manage.py,migrate

gcloud run jobs execute migrate-db --region us-central1
```

### Scaling

Cloud Run automatically scales based on traffic, but you can configure:

```bash
# Update scaling settings
gcloud run services update letsgetcrypto \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 20 \
  --concurrency 100
```

## 💰 Cost Optimization

### Estimated Monthly Costs (us-central1)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 2M requests, 100 hours | $5-10 |
| Cloud SQL (db-f1-micro) | 1 instance | $7-10 |
| VPC Connector | 1 connector | $7 |
| Cloud Storage (logs) | 5 GB | $0.10 |
| Cloud Build | 120 builds/month | Free tier |
| **Total** | | **$19-27/month** |

*Note: First 2M requests on Cloud Run are free per month*

### Cost Reduction Tips

1. **Use Free Tier**: Cloud Run has generous free tier (2M requests/month)
2. **Set min-instances to 0**: Avoid idle costs, accept cold starts
3. **Use Shared-core SQL**: db-f1-micro for development
4. **Schedule Scaling**: Use Cloud Scheduler to scale down during off-hours
5. **Optimize Images**: Smaller Docker images = faster starts, lower costs

## 🔐 Security Best Practices

### Implemented Security Features

1. **VPC Isolation**: Private communication between Cloud Run and Cloud SQL
2. **Secret Manager**: Encrypted credential storage
3. **IAM Roles**: Least-privilege access control
4. **HTTPS Only**: Automatic SSL/TLS on Cloud Run
5. **Database Encryption**: Cloud SQL encryption at rest
6. **Non-root Container**: Application runs as non-root user

### Additional Security Recommendations

1. **Enable Cloud Armor**: DDoS protection and WAF
2. **Use Identity-Aware Proxy**: Add authentication layer
3. **Enable VPC Service Controls**: Prevent data exfiltration
4. **Regular Security Scans**: Use Container Analysis
5. **Audit Logs**: Enable and monitor Cloud Audit Logs

## 🧪 Testing

### Local Testing with Docker

Test the production configuration locally:

```bash
# Build image
docker build -t letsgetcrypto:test .

# Run with test database
docker run -p 8000:8000 \
  -e DJANGO_DEBUG=False \
  -e DJANGO_SECRET_KEY=test-key \
  -e DJANGO_ALLOWED_HOSTS=* \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  letsgetcrypto:test

# Test endpoints
curl http://localhost:8000/api/health/
```

### Testing GCP Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe letsgetcrypto \
  --region=us-central1 \
  --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/api/health/

# Test market data
curl $SERVICE_URL/api/market/

# Test price endpoint
curl $SERVICE_URL/api/price/bitcoin/
```

## 🗑️ Cleanup

To remove all GCP resources:

### Using Terraform

```bash
cd gcp
terraform destroy
```

### Using gcloud CLI

```bash
# Delete Cloud Run service
gcloud run services delete letsgetcrypto --region=us-central1

# Delete Cloud SQL instance
gcloud sql instances delete letsgetcrypto-db-instance

# Delete VPC connector
gcloud compute networks vpc-access connectors delete letsgetcrypto-connector \
  --region=us-central1

# Delete container images
gcloud container images delete gcr.io/PROJECT_ID/letsgetcrypto:latest
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Cloud Run Service Won't Start

**Check deployment logs:**
```bash
gcloud run services logs read letsgetcrypto --region=us-central1 --limit=100
```

**Common causes:**
- Database connection issues
- Missing environment variables
- Image build errors
- Insufficient permissions

#### 2. Database Connection Errors

**Verify Cloud SQL configuration:**
```bash
gcloud sql instances describe letsgetcrypto-db-instance

# Check connection name
gcloud sql instances describe letsgetcrypto-db-instance \
  --format='value(connectionName)'
```

**Test connection from Cloud Shell:**
```bash
gcloud sql connect letsgetcrypto-db-instance --user=postgres
```

#### 3. Build Fails in Cloud Build

**View build logs:**
```bash
gcloud builds list --limit=10
gcloud builds log BUILD_ID
```

**Common issues:**
- Missing dependencies in requirements.txt
- Docker build context too large
- Insufficient build timeout

#### 4. High Response Times

**Monitor performance:**
```bash
# Check Cloud Run metrics
gcloud run services describe letsgetcrypto \
  --region=us-central1 \
  --format='value(status.latestCreatedRevisionName)'
```

**Solutions:**
- Increase min-instances to reduce cold starts
- Optimize database queries
- Add caching layer (Cloud Memorystore)
- Increase CPU/memory allocation

### Getting Help

**View service status:**
```bash
gcloud run services describe letsgetcrypto --region=us-central1
```

**Useful commands:**
```bash
# List all Cloud Run services
gcloud run services list

# View revisions
gcloud run revisions list --service=letsgetcrypto --region=us-central1

# Check IAM permissions
gcloud projects get-iam-policy PROJECT_ID

# View recent operations
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

## 🆕 What's Next?

After deployment, consider:

1. **Custom Domain**: Map your domain to Cloud Run
   ```bash
   gcloud run domain-mappings create --service=letsgetcrypto \
     --domain=api.yourdomain.com --region=us-central1
   ```

2. **Cloud CDN**: Enable CDN for static assets
3. **Cloud Armor**: Add DDoS protection
4. **Cloud Monitoring**: Set up custom dashboards
5. **Cloud Scheduler**: Schedule automated tasks

---

**Note**: This deployment guide assumes basic familiarity with Google Cloud Platform. For production deployments, consider implementing automated backups, monitoring, and disaster recovery procedures.
