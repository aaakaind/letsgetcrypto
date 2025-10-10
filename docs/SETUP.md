# Quick Setup Guide for GitHub Pages

## One-Time Setup

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/aaakaind/letsgetcrypto`
2. Click on **Settings** (top menu)
3. Scroll down to **Pages** (in the left sidebar)
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions" from the dropdown
5. Save changes

### Step 2: Trigger Deployment

The deployment will automatically happen on the next push to `main` branch, or you can manually trigger it:

1. Go to **Actions** tab
2. Click on "Deploy to GitHub Pages" workflow
3. Click "Run workflow" button
4. Select `main` branch
5. Click "Run workflow"

### Step 3: Wait for Deployment

- The deployment typically takes 1-2 minutes
- Watch the workflow progress in the Actions tab
- Once complete, a green checkmark will appear

### Step 4: Access Your Dashboard

Your dashboard will be live at:
```
https://aaakaind.github.io/letsgetcrypto/
```

## Troubleshooting

### Workflow Fails

If the GitHub Actions workflow fails:

1. Check the error message in the Actions tab
2. Verify that GitHub Pages is enabled in Settings
3. Ensure the source is set to "GitHub Actions" (not "Deploy from branch")
4. Check that the `docs/` directory contains all required files

### Dashboard Not Loading

If the page loads but shows errors:

1. Open browser Developer Tools (F12)
2. Check the Console tab for errors
3. Verify that CoinGecko API is accessible
4. Try refreshing the page after a few seconds

### 404 Error

If you get a 404 error:

1. Wait a few minutes for GitHub Pages to update
2. Clear your browser cache
3. Try accessing the URL in an incognito/private window
4. Verify the deployment succeeded in the Actions tab

## Next Steps

Once your dashboard is live:

1. Test all features (market data, charts, etc.)
2. Customize the appearance (see [GITHUB_PAGES.md](../GITHUB_PAGES.md))
3. Share the URL with others
4. Monitor usage and API rate limits

## Custom Domain (Optional)

To use your own domain:

1. Create a file named `CNAME` in the `docs/` directory
2. Add your domain name to the file (e.g., `crypto.yourdomain.com`)
3. Configure DNS with your domain provider
4. Wait for DNS propagation (can take up to 48 hours)

## Support

For more detailed information, see:
- [GITHUB_PAGES.md](../GITHUB_PAGES.md) - Complete GitHub Pages guide
- [README.md](README.md) - Features and usage
- Main repository: https://github.com/aaakaind/letsgetcrypto
