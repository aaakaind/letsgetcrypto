# GitHub Pages Quick Start

> Deploy your LetsGetCrypto dashboard to GitHub Pages in 3 minutes!

## Prerequisites

- A GitHub account
- This repository forked or cloned
- Push access to the repository

## 3-Step Setup

### 1️⃣ Enable GitHub Pages

1. Go to **Settings** → **Pages** in your repository
2. Under "Build and deployment" → **Source**: Select **GitHub Actions**
3. Save changes

### 2️⃣ Deploy

**Option A - Automatic** (Recommended)
```bash
# Push any change to main branch
git push origin main
```

**Option B - Manual**
1. Go to **Actions** tab
2. Click "Deploy to GitHub Pages"
3. Click "Run workflow"

### 3️⃣ Access

Your dashboard will be live at:
```
https://[username].github.io/letsgetcrypto/
```

Replace `[username]` with your GitHub username.

## What You Get

✅ **Free Hosting**: Powered by GitHub Pages CDN
✅ **Auto HTTPS**: SSL certificate included
✅ **Real-time Data**: Live cryptocurrency prices
✅ **Interactive Charts**: Price history and RSI indicator
✅ **Auto-refresh**: Data updates every 30 seconds
✅ **Mobile Friendly**: Responsive design
✅ **Fast Load**: Global CDN distribution

## Features Available

| Feature | Status | Notes |
|---------|--------|-------|
| Market Data | ✅ Full | CoinGecko API |
| Price Charts | ✅ Full | Chart.js |
| ML Training | ⚠️ Demo | Simulated |
| Predictions | ⚠️ Demo | Simulated |
| Trading | ⚠️ Demo | Simulated |

## Quick Customization

### Change Colors
Edit `docs/css/dashboard.css`:
```css
/* Line 11 - Background gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change Refresh Interval
Edit `docs/js/dashboard.js`:
```javascript
// Line 68 - Currently 30 seconds (30000ms)
refreshInterval = setInterval(function() {
    loadMarketOverview();
    loadCryptoPrice();
}, 30000);
```

### Add Cryptocurrencies
Edit `docs/index.html`:
```html
<!-- Line 45 - Add new options -->
<option value="ripple">Ripple (XRP)</option>
```

## Common Issues & Fixes

### 404 Error
**Solution**: Wait 2-3 minutes after first deployment, then clear cache

### No Data Loading
**Solution**: Check browser console (F12) for API errors

### Deployment Failed
**Solution**: Check Actions tab for error details

### Rate Limit Error
**Solution**: Wait 60 seconds before refreshing

## Testing Locally

```bash
# Navigate to docs folder
cd docs

# Start local server
python -m http.server 8080

# Open browser
open http://localhost:8080
```

## Next Steps

- 📖 Read full guide: [GITHUB_PAGES.md](GITHUB_PAGES.md)
- 🔧 See deployment flow: [docs/DEPLOYMENT_FLOW.md](docs/DEPLOYMENT_FLOW.md)
- 🚀 Deploy full app: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
- 📱 Share your dashboard URL!

## Need Help?

- **Documentation**: See [GITHUB_PAGES.md](GITHUB_PAGES.md)
- **Issues**: Open an issue on GitHub
- **Full App**: See [README.md](README.md) for Django version

---

**⚠️ Disclaimer**: Educational purposes only. Not financial advice. Always use testnet mode for practice trading.

**Made with ❤️ for the crypto community**
