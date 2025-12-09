# 🚀 Quick Deploy Guide

**Deploy LetsGetCrypto to production in under 15 minutes!**

Choose your preferred cloud platform and follow the quick start guide.

## 🎯 Platform Comparison

| Platform | Time | Cost/Month | Difficulty | Best For |
|----------|------|------------|------------|----------|
| **GCP Cloud Run** ⭐ | 10 min | $20-40 | Easy | Serverless, pay-per-use |
| **AWS ECS Fargate** | 15 min | $50-100 | Medium | Enterprise production |
| **AWS Beanstalk** | 10 min | $30-50 | Easy | Simple production |
| **Docker Compose** | 5 min | Free | Easy | Local development |

---

## ☁️ Cloud Deployments

### 🥇 Google Cloud Platform (Recommended for Most Users)

**Why choose GCP?**
- ✅ Lowest cost ($20-40/month)
- ✅ Serverless (no infrastructure to manage)
- ✅ Generous free tier (2M requests/month free)
- ✅ Automatic scaling from 0
- ✅ Pay only for actual usage
- ✅ Fastest deployment (10 minutes)

**Quick Deploy:**

```bash
# 1. Install gcloud CLI (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# 2. Set up your project
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy!
cd gcp
export GCP_PROJECT_ID="YOUR_PROJECT_ID"
./deploy-gcp.sh
```

**📖 Full Guide**: [QUICK_DEPLOY_GCP.md](QUICK_DEPLOY_GCP.md) | [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)

---

### 🏢 Amazon Web Services (Enterprise Production)

**Why choose AWS?**
- ✅ Enterprise-grade infrastructure
- ✅ More configuration options
- ✅ Existing AWS ecosystem
- ✅ Broader geographic regions
- ✅ Advanced networking features

**Quick Deploy - Option 1: Elastic Beanstalk (Easiest)**

```bash
# 1. Create package
./package-for-aws.sh 1.0.0

# 2. Upload to AWS Console
# - Go to AWS Elastic Beanstalk Console
# - Upload: aws-packages/letsgetcrypto-beanstalk-*.zip
# - Platform: Python 3.11
# - Deploy!
```

**Quick Deploy - Option 2: ECS Fargate (Production)**

```bash
# 1. Install AWS CLI (if not already installed)
# Visit: https://aws.amazon.com/cli/

# 2. Deploy
./deploy-aws.sh
```

**📖 Full Guide**: [QUICK_DEPLOY_AWS.md](QUICK_DEPLOY_AWS.md) | [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

---

## 📚 Additional Resources

- **[QUICK_DEPLOY_GCP.md](QUICK_DEPLOY_GCP.md)** - Google Cloud Platform quick deploy
- **[QUICK_DEPLOY_AWS.md](QUICK_DEPLOY_AWS.md)** - Amazon Web Services quick deploy
- **[GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)** - Complete GCP deployment guide
- **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - Complete AWS deployment guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - All deployment options

---

**Ready to deploy? Choose your platform above and get started! 🚀**
