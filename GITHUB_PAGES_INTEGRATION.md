# GitHub Pages Frontend Integration Guide

This guide explains how to integrate the GitHub Pages static frontend with the LetsGetCrypto backend API.

## Overview

The LetsGetCrypto application has two main components:
1. **Frontend**: Static HTML/CSS/JavaScript deployed on GitHub Pages
2. **Backend**: Django REST API with ML capabilities

This guide covers three deployment scenarios:

## Scenario 1: Local Development

### Setup

1. **Start the backend server:**
   ```bash
   cd letsgetcrypto
   source venv/bin/activate
   python manage.py runserver
   ```
   
   Backend API available at: `http://localhost:8000/api/`

2. **Configure frontend for local API:**
   
   Edit `docs/js/dashboard.js` and update the API endpoint:
   
   ```javascript
   // At the top of the file
   const API_BASE_URL = 'http://localhost:8000/api';
   
   // Example usage
   $.ajax({
       url: `${API_BASE_URL}/crypto/prices/`,
       // ... rest of configuration
   });
   ```

3. **Serve GitHub Pages locally:**
   
   ```bash
   cd docs
   python -m http.server 8080
   ```
   
   Or with Jekyll:
   ```bash
   cd docs
   bundle exec jekyll serve --port 8080
   ```
   
   Frontend available at: `http://localhost:8080/`

4. **Enable CORS in Django:**
   
   Install django-cors-headers:
   ```bash
   pip install django-cors-headers
   ```
   
   Update `letsgetcrypto_django/settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'corsheaders',
   ]
   
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',
       'django.middleware.common.CommonMiddleware',
       ...
   ]
   
   # For local development
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:8080",
       "http://127.0.0.1:8080",
   ]
   ```

## Scenario 2: GitHub Pages + Hosted Backend

### Backend Deployment

1. **Deploy backend to a hosting service:**
   - AWS ECS (see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md))
   - Heroku
   - DigitalOcean
   - Any cloud provider with Django support

2. **Get your backend URL:**
   ```
   https://your-app.herokuapp.com/api/
   https://your-domain.com/api/
   https://your-loadbalancer.aws.com/api/
   ```

### Frontend Configuration

1. **Update API endpoint in GitHub Pages:**
   
   Edit `docs/js/dashboard.js`:
   ```javascript
   const API_BASE_URL = 'https://your-backend-domain.com/api';
   ```

2. **Update CORS settings in Django:**
   
   In `letsgetcrypto_django/settings.py`:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://yourusername.github.io",
       "https://your-custom-domain.com",  # if using custom domain
   ]
   
   # Or for development, allow all (NOT for production!)
   # CORS_ALLOW_ALL_ORIGINS = True
   ```

3. **Commit and push to GitHub:**
   ```bash
   git add docs/js/dashboard.js
   git commit -m "Configure API endpoint for production"
   git push origin main
   ```
   
   GitHub Actions will automatically deploy to Pages.

## Scenario 3: Full Cloud Deployment (AWS)

### Architecture

```
┌─────────────────┐
│  GitHub Pages   │ ──────┐
│  (Frontend)     │       │
└─────────────────┘       │
                          ▼
                   ┌─────────────┐
                   │ AWS ALB     │ (Load Balancer)
                   │ + SSL/TLS   │
                   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  AWS ECS    │ (Django Backend)
                   │  Fargate    │
                   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  AWS RDS    │ (PostgreSQL)
                   └─────────────┘
```

### Setup Steps

1. **Deploy backend to AWS ECS:**
   ```bash
   ./deploy-aws.sh
   ```

2. **Get ALB URL from AWS Console:**
   - Go to EC2 → Load Balancers
   - Copy DNS name (e.g., `my-lb-123456789.us-east-1.elb.amazonaws.com`)

3. **Update frontend configuration:**
   ```javascript
   const API_BASE_URL = 'https://my-lb-123456789.us-east-1.elb.amazonaws.com/api';
   ```

4. **Configure CORS in AWS deployment:**
   
   Update `.env.production.template`:
   ```bash
   DJANGO_ALLOWED_HOSTS=my-lb-123456789.us-east-1.elb.amazonaws.com,yourusername.github.io
   CORS_ALLOWED_ORIGINS=https://yourusername.github.io
   ```

## API Endpoints Reference

The backend provides these key endpoints for the frontend:

### Market Data
```
GET /api/crypto/prices/
GET /api/crypto/prices/{coin_id}/
GET /api/crypto/history/{coin_id}/
```

### Predictions
```
POST /api/crypto/predict/
Body: { "coin_id": "bitcoin", "days": 30 }
```

### ML Training
```
POST /api/crypto/train/
Body: { "coin_id": "bitcoin", "model_type": "all" }
```

### Health Check
```
GET /api/health/
```

### Dashboard
```
GET /api/dashboard/
```

## Frontend API Integration Example

Update `docs/js/dashboard.js`:

```javascript
// Configuration
const API_BASE_URL = 'http://localhost:8000/api';  // Change for production

// Fetch cryptocurrency price
async function fetchCryptoPrice(coinId) {
    try {
        const response = await fetch(`${API_BASE_URL}/crypto/prices/${coinId}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching price:', error);
        // Fallback to CoinGecko API if backend unavailable
        return fetchFromCoinGecko(coinId);
    }
}

// Get ML predictions
async function getPredictions(coinId, days = 30) {
    try {
        const response = await fetch(`${API_BASE_URL}/crypto/predict/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ coin_id: coinId, days: days })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error getting predictions:', error);
        return null;
    }
}

// Train ML models
async function trainModels(coinId) {
    try {
        const response = await fetch(`${API_BASE_URL}/crypto/train/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ coin_id: coinId, model_type: 'all' })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error training models:', error);
        return null;
    }
}
```

## Environment-Specific Configuration

### Development (`.env`)
```bash
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### Production (`.env.production`)
```bash
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=your-secure-random-secret-key
DJANGO_ALLOWED_HOSTS=your-domain.com,your-lb.elb.amazonaws.com
CORS_ALLOWED_ORIGINS=https://yourusername.github.io,https://your-custom-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## Troubleshooting

### CORS Errors

**Problem**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution**:
1. Install django-cors-headers
2. Add to INSTALLED_APPS and MIDDLEWARE
3. Configure CORS_ALLOWED_ORIGINS with your GitHub Pages URL
4. Restart Django server

### API Not Responding

**Problem**: Frontend can't connect to API

**Solution**:
1. Check backend is running: `curl http://localhost:8000/api/health/`
2. Verify API_BASE_URL in frontend JavaScript
3. Check browser console for errors
4. Ensure CORS is properly configured

### 404 on API Endpoints

**Problem**: API endpoints return 404

**Solution**:
1. Check URL path includes `/api/`
2. Verify endpoint exists in Django: `python manage.py show_urls`
3. Check Django URL configuration in `crypto_api/urls.py`

### Mixed Content Error (HTTPS/HTTP)

**Problem**: "Mixed content" error when GitHub Pages (HTTPS) calls HTTP API

**Solution**:
1. Deploy backend with HTTPS/SSL
2. Use AWS ALB with SSL certificate
3. Or use a service like Cloudflare for SSL termination

## Testing the Integration

### Test Script

Create `test_integration.html` in docs:

```html
<!DOCTYPE html>
<html>
<head>
    <title>API Integration Test</title>
</head>
<body>
    <h1>API Integration Test</h1>
    <button onclick="testAPI()">Test API Connection</button>
    <pre id="results"></pre>
    
    <script>
        const API_BASE_URL = 'http://localhost:8000/api';
        
        async function testAPI() {
            const results = document.getElementById('results');
            results.textContent = 'Testing...';
            
            try {
                // Test health endpoint
                const health = await fetch(`${API_BASE_URL}/health/`);
                const healthData = await health.json();
                
                results.textContent = JSON.stringify(healthData, null, 2);
                
                if (health.ok) {
                    results.textContent += '\n\n✅ API Connection Successful!';
                }
            } catch (error) {
                results.textContent = `❌ Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

### Manual Testing

1. **Health Check:**
   ```bash
   curl http://localhost:8000/api/health/
   ```

2. **Get Prices:**
   ```bash
   curl http://localhost:8000/api/crypto/prices/bitcoin/
   ```

3. **Train Model:**
   ```bash
   curl -X POST http://localhost:8000/api/crypto/train/ \
     -H "Content-Type: application/json" \
     -d '{"coin_id": "bitcoin", "model_type": "logistic_regression"}'
   ```

## Best Practices

1. **Use Environment Variables:**
   - Don't hardcode API URLs
   - Use build-time configuration for different environments

2. **Handle Errors Gracefully:**
   - Implement fallback to CoinGecko API
   - Show user-friendly error messages
   - Retry failed requests with exponential backoff

3. **Optimize API Calls:**
   - Cache responses when appropriate
   - Batch requests when possible
   - Implement request throttling

4. **Security:**
   - Use HTTPS in production
   - Implement API rate limiting
   - Validate all inputs
   - Don't expose sensitive data in frontend

5. **Monitoring:**
   - Log API errors
   - Track response times
   - Monitor CORS issues
   - Set up alerts for API downtime

## Additional Resources

- [Django CORS Headers Documentation](https://github.com/adamchainz/django-cors-headers)
- [GitHub Pages Custom Domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [AWS ECS Deployment Guide](AWS_DEPLOYMENT.md)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**Need Help?** See the main [README.md](README.md) or [GITHUB_CLONE_GUIDE.md](GITHUB_CLONE_GUIDE.md) for more information.
