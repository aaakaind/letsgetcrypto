# Production Deployment Checklist

Use this checklist before deploying LetsGetCrypto to production.

## Pre-Deployment Security Checklist

### Environment Variables
- [ ] `DJANGO_DEBUG=False` is set (NEVER use True in production)
- [ ] Strong `DJANGO_SECRET_KEY` generated (min 50 characters)
- [ ] `DJANGO_ALLOWED_HOSTS` configured with actual domain(s)
- [ ] `DATABASE_URL` points to production database
- [ ] API keys are stored in AWS Secrets Manager or environment variables
- [ ] No secrets committed to version control

### Database Configuration
- [ ] PostgreSQL instance is running and accessible
- [ ] Database backups are configured
- [ ] Database connection uses SSL/TLS
- [ ] Database credentials are stored securely
- [ ] Database migrations are up to date

### Security Settings
- [ ] SSL/HTTPS is enabled on load balancer
- [ ] `SECURE_SSL_REDIRECT=True` (if using HTTPS)
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] Security headers are configured
- [ ] CORS settings are properly configured
- [ ] Rate limiting is configured (if needed)

### Infrastructure
- [ ] Load balancer health checks are configured
- [ ] Auto-scaling policies are set
- [ ] CloudWatch logging is enabled
- [ ] CloudWatch alarms are configured
- [ ] VPC security groups are properly configured
- [ ] Only necessary ports are open (80, 443)

## Deployment Validation

### Pre-Deployment Tests
```bash
# Run all tests
python test_all.py

# Test Django configuration
python manage.py check --deploy

# Test database migrations
python manage.py migrate --check

# Collect static files
python manage.py collectstatic --noinput --dry-run
```

### Docker Build Test
```bash
# Test Docker build
docker build -t letsgetcrypto:test .

# Test Docker run locally
docker run -p 8000:8000 \
  -e DJANGO_DEBUG=False \
  -e DJANGO_SECRET_KEY=test-key \
  -e DJANGO_ALLOWED_HOSTS=localhost \
  letsgetcrypto:test
```

### AWS Deployment Steps
```bash
# 1. Package for deployment
./package-for-aws.sh $(cat VERSION)

# 2. Deploy to AWS
./deploy-aws.sh

# 3. Wait for deployment to complete
# Check ECS console or use AWS CLI
```

## Post-Deployment Validation

### Health Check Endpoints
Test all health check endpoints:
```bash
# Replace with your actual load balancer URL
LOAD_BALANCER_URL="http://your-load-balancer-url"

# Test liveness (should always return 200)
curl -f $LOAD_BALANCER_URL/api/liveness/ || echo "❌ Liveness check failed"

# Test readiness (checks database)
curl -f $LOAD_BALANCER_URL/api/readiness/ || echo "❌ Readiness check failed"

# Test health (comprehensive check)
curl -f $LOAD_BALANCER_URL/api/health/ || echo "❌ Health check failed"
```

### API Endpoint Tests
```bash
# Test market overview endpoint
curl -s $LOAD_BALANCER_URL/api/market/ | jq .

# Test price endpoint for Bitcoin
curl -s $LOAD_BALANCER_URL/api/price/bitcoin/ | jq .

# Test history endpoint
curl -s $LOAD_BALANCER_URL/api/history/bitcoin/?days=7 | jq .
```

### Dashboard Access
```bash
# Test dashboard loads
curl -f $LOAD_BALANCER_URL/api/dashboard/ || echo "❌ Dashboard failed"

# Or open in browser
xdg-open $LOAD_BALANCER_URL/api/dashboard/
```

### Performance Tests
```bash
# Test response time (should be < 2s)
time curl -s $LOAD_BALANCER_URL/api/health/ > /dev/null

# Test concurrent requests
ab -n 100 -c 10 $LOAD_BALANCER_URL/api/health/
```

## Monitoring Setup

### CloudWatch Metrics
- [ ] CPU utilization alerts configured
- [ ] Memory utilization alerts configured
- [ ] Request count metrics tracked
- [ ] Error rate alerts configured
- [ ] Database connection metrics monitored

### Logs
- [ ] Application logs flowing to CloudWatch
- [ ] Error logs are monitored
- [ ] Access logs are enabled
- [ ] Log retention policy configured

### Alarms
- [ ] High CPU alarm configured
- [ ] High memory alarm configured
- [ ] High error rate alarm configured
- [ ] Database connection failures alarm
- [ ] Health check failures alarm

## Rollback Plan

If deployment fails or issues are detected:

### Quick Rollback Steps
```bash
# 1. Identify previous task definition
aws ecs describe-services \
  --cluster letsgetcrypto-cluster \
  --services letsgetcrypto-service \
  --query 'services[0].deployments' \
  --region us-east-1

# 2. Rollback to previous task definition
aws ecs update-service \
  --cluster letsgetcrypto-cluster \
  --service letsgetcrypto-service \
  --task-definition letsgetcrypto-task:PREVIOUS_VERSION \
  --region us-east-1

# 3. Monitor rollback
watch aws ecs describe-services \
  --cluster letsgetcrypto-cluster \
  --services letsgetcrypto-service \
  --query 'services[0].deployments' \
  --region us-east-1
```

### Emergency Actions
1. Scale up to more instances if needed
2. Enable maintenance mode if available
3. Contact AWS support if infrastructure issues
4. Check CloudWatch logs for errors

## Post-Deployment Tasks

### Documentation
- [ ] Update deployment documentation with any changes
- [ ] Document any issues encountered and solutions
- [ ] Update runbooks if procedures changed
- [ ] Update API documentation if endpoints changed

### Team Communication
- [ ] Notify team of successful deployment
- [ ] Share deployment notes and any issues
- [ ] Schedule post-deployment review
- [ ] Update project status

### Clean Up
- [ ] Remove old Docker images from ECR (keep last 5)
- [ ] Archive old CloudWatch logs (after retention period)
- [ ] Update version tags in Git
- [ ] Create release notes in GitHub

## Version Information

Current Version: `cat VERSION`
Deployment Date: `date`
Deployed By: `whoami`

## Support Contacts

- AWS Support: https://console.aws.amazon.com/support/
- Project Documentation: See README.md
- Emergency Rollback: See section above

## Cost Monitoring

After deployment:
- [ ] Review AWS Cost Explorer for unexpected charges
- [ ] Verify RDS instance is right-sized
- [ ] Confirm ECS tasks are not over-provisioned
- [ ] Check for unused resources (old images, snapshots)

Expected monthly cost: $50-100/month for standard deployment

## Success Criteria

Deployment is considered successful when:
- ✅ All health check endpoints return 200 OK
- ✅ Dashboard loads and displays data
- ✅ API endpoints return valid responses
- ✅ Response times are < 2 seconds
- ✅ No errors in CloudWatch logs
- ✅ Database connections are working
- ✅ External API integrations are functioning
- ✅ Load balancer shows healthy targets

---

**Note**: This is a living document. Update it as deployment processes evolve.
