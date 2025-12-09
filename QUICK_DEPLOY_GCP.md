# 🚀 Quick Deploy to Google Cloud Platform

**Deploy LetsGetCrypto to Google Cloud Platform in under 10 minutes!**

This guide gets you from zero to a live, production-ready deployment on GCP Cloud Run with minimal configuration.

## ⚡ Prerequisites (5 minutes)

### 1. Install Google Cloud SDK

```bash
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows
# Download from: https://cloud.google.com/sdk/docs/install
```

Verify installation:
```bash
gcloud --version
```

### 2. Authenticate and Set Up Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create letsgetcrypto-prod --name="LetsGetCrypto Production"

# Set as active project
gcloud config set project letsgetcrypto-prod

# Enable billing (required)
# Visit: https://console.cloud.google.com/billing
```

### 3. Install Docker

```bash
# macOS
brew install docker

# Ubuntu/Debian
sudo apt-get install docker.io

# Verify
docker --version
```

## 🚀 Deploy Now! (5 minutes)

### Option 1: One-Command Automated Deployment

```bash
cd gcp
export GCP_PROJECT_ID="your-project-id"
./deploy-gcp.sh
```

**That's it!** The script handles everything:
- ✅ Enables required GCP APIs
- ✅ Builds and pushes Docker image
- ✅ Creates Cloud SQL database
- ✅ Deploys Cloud Run service
- ✅ Sets up networking and security
- ✅ Configures secrets

**Time: ~10 minutes**

### Option 2: Manual Quick Deploy

If you prefer manual control:

```bash
# 1. Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 2. Enable APIs
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com

# 3. Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/letsgetcrypto

# 4. Deploy to Cloud Run
gcloud run deploy letsgetcrypto \
    --image gcr.io/$PROJECT_ID/letsgetcrypto:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars DJANGO_DEBUG=False,DJANGO_ALLOWED_HOSTS=*
```

**Time: ~5 minutes** (without database)

## ✅ Verify Deployment

```bash
# Get your service URL
gcloud run services describe letsgetcrypto \
    --region=us-central1 \
    --format='value(status.url)'

# Test it
curl https://YOUR_SERVICE_URL/api/health/
curl https://YOUR_SERVICE_URL/api/market/
```

## 📊 What You Get

After deployment, you have:

- **Live API**: Accessible at `https://letsgetcrypto-*.run.app`
- **Auto-scaling**: Scales from 0 to 10 instances automatically
- **HTTPS**: Automatic SSL/TLS certificate
- **Logging**: Integrated Cloud Logging
- **Monitoring**: Built-in metrics and dashboards

## 💰 Costs

Estimated monthly costs:

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 2M requests, 100 hours | $5-10 |
| Cloud SQL | db-f1-micro | $7-10 |
| VPC Connector | 1 connector | $7 |
| **Total** | | **$19-27/month** |

**Free Tier**: First 2M Cloud Run requests are free each month!

## 🔧 Common Configurations

### Add Custom Domain

```bash
# Map your domain
gcloud run domain-mappings create \
    --service=letsgetcrypto \
    --domain=api.yourdomain.com \
    --region=us-central1

# Follow DNS instructions provided
```

### Set Environment Variables

```bash
gcloud run services update letsgetcrypto \
    --region=us-central1 \
    --set-env-vars="COINGECKO_API_KEY=your-key,ANTHROPIC_API_KEY=your-key"
```

### Scale Configuration

```bash
# Set minimum instances (avoid cold starts)
gcloud run services update letsgetcrypto \
    --region=us-central1 \
    --min-instances=1 \
    --max-instances=20
```

### Enable Database

```bash
# Create Cloud SQL instance
gcloud sql instances create letsgetcrypto-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create letsgetcrypto \
    --instance=letsgetcrypto-db

# Update Cloud Run to connect
gcloud run services update letsgetcrypto \
    --region=us-central1 \
    --add-cloudsql-instances=PROJECT_ID:us-central1:letsgetcrypto-db \
    --set-env-vars="DATABASE_URL=postgres://..."
```

## 🔄 Updates

Deploy new version:

```bash
# Build new image
gcloud builds submit --tag gcr.io/$PROJECT_ID/letsgetcrypto:v2

# Deploy
gcloud run deploy letsgetcrypto \
    --image gcr.io/$PROJECT_ID/letsgetcrypto:v2 \
    --region=us-central1
```

## 🗑️ Cleanup

Remove everything:

```bash
# Delete Cloud Run service
gcloud run services delete letsgetcrypto --region=us-central1

# Delete Cloud SQL (if created)
gcloud sql instances delete letsgetcrypto-db

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/letsgetcrypto:latest
```

## 🆘 Troubleshooting

### Deployment fails with "Permission denied"

**Solution**: Enable required APIs
```bash
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    compute.googleapis.com \
    cloudbuild.googleapis.com
```

### Service won't start

**Check logs**:
```bash
gcloud run services logs read letsgetcrypto --region=us-central1 --limit=50
```

### Billing not enabled

Enable billing at: https://console.cloud.google.com/billing

## 📚 Next Steps

After successful deployment:

1. **Review GCP Console**: https://console.cloud.google.com/run
2. **Set up monitoring**: Create uptime checks and alerts
3. **Configure CI/CD**: Set up Cloud Build triggers
4. **Add database**: Follow database setup in [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)
5. **Custom domain**: Map your domain to the service

## 📖 Detailed Documentation

For complete deployment options and configurations:

- **[GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)**: Comprehensive GCP deployment guide
- **[gcp/README.md](gcp/README.md)**: GCP directory documentation
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Complete deployment guide (all platforms)

---

**Need help?** See the [troubleshooting section](#troubleshooting) above or open an issue on GitHub.

**Want more control?** See [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) for advanced configurations including:
- Terraform infrastructure as code
- Full Cloud SQL setup with VPC
- Secret Manager integration
- Cloud Build CI/CD pipeline
- Custom networking and security
