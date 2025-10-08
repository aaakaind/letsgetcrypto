# 🚀 Quick Deploy to AWS

The fastest way to deploy LetsGetCrypto to AWS.

## Step 1: Create Deployment Packages

```bash
chmod +x package-for-aws.sh
./package-for-aws.sh 1.0.0
```

This creates packages in the `aws-packages/` directory.

## Step 2: Choose Your Deployment Method

### ⚡ Easiest: Elastic Beanstalk (5 minutes)

**No Docker or AWS CLI needed - just upload via web console!**

1. Go to [AWS Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk)
2. Click **Create Application**
3. Upload `aws-packages/letsgetcrypto-beanstalk-*.zip`
4. Select Platform: **Python 3.11**
5. Click **Create Environment**
6. Done! 🎉

**Cost**: ~$30-50/month

### 🔧 Production: ECS Fargate (10-15 minutes)

**Requires Docker and AWS CLI**

```bash
# Extract the package
unzip aws-packages/letsgetcrypto-cloudformation-*.zip -d deploy
cd deploy

# Deploy (requires Docker running)
chmod +x deploy-aws.sh
./deploy-aws.sh
```

**Cost**: ~$50-100/month

## Which Should I Choose?

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Testing, demo | Elastic Beanstalk | Easy to deploy via console |
| Small app, low traffic | Elastic Beanstalk | Lower cost, simpler management |
| Production, high traffic | ECS Fargate | Better scaling, more control |
| Need containers | ECS Fargate | Native container support |

## Need Help?

- **Elastic Beanstalk**: See `BEANSTALK_DEPLOYMENT.md` in the package
- **ECS Fargate**: See `AWS_DEPLOYMENT.md` in the package
- **Detailed Guide**: See [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)

## Security Checklist

Before deploying to production:

- [ ] Set `DJANGO_DEBUG=False`
- [ ] Generate strong `DJANGO_SECRET_KEY`
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with your domain
- [ ] Use strong database passwords
- [ ] Review security group settings
- [ ] Enable SSL/HTTPS (optional but recommended)

## Cleanup

To delete all AWS resources and stop charges:

**Elastic Beanstalk**:
```bash
eb terminate letsgetcrypto-env
```

**ECS Fargate**:
```bash
aws cloudformation delete-stack --stack-name letsgetcrypto-stack --region us-east-1
```

## Support

For detailed documentation, see:
- [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md) - Complete packaging guide
- [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - AWS deployment details
- [README.md](README.md) - Application documentation
