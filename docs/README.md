# LetsGetCrypto - GitHub Pages Dashboard

This is a Jekyll-powered static version of the LetsGetCrypto dashboard hosted on GitHub Pages.

## Features

- 📊 Real-time cryptocurrency market data from CoinGecko API
- 📈 Interactive price charts with historical data
- 💹 Top cryptocurrencies ranked by market cap
- 🔄 Auto-refresh every 30 seconds
- 📱 Responsive design for mobile and desktop
- 🔍 SEO optimized with automatic sitemaps and meta tags

## Usage

Visit the live dashboard at: `https://[username].github.io/letsgetcrypto/`

### Controls

- **Cryptocurrency Selection**: Choose from Bitcoin, Ethereum, Binance Coin, Cardano, or Solana
- **Days of Data**: Adjust historical data range (7-365 days)
- **Refresh Data**: Manually fetch latest market information
- **Train Models**: Simulated ML model training (demo mode)
- **Get Predictions**: Generate simulated trading signals (demo mode)

### Important Notes

⚠️ **Demo Mode**: The GitHub Pages version uses direct CoinGecko API calls. The ML training and trading features are simulated for demonstration purposes only.

⚠️ **API Rate Limits**: CoinGecko's free API has rate limits. If you see errors, wait a few moments before refreshing.

⚠️ **Educational Purpose**: This tool is for educational purposes only. Not financial advice.

## Jekyll Structure

This site uses Jekyll for better maintainability and SEO:

```
docs/
├── _config.yml          # Jekyll configuration
├── Gemfile              # Ruby dependencies
├── _layouts/            # Page layouts
│   └── default.html     # Main layout template
├── _includes/           # Reusable components
│   ├── header.html      # Site header
│   └── footer.html      # Site footer
├── index.html           # Main dashboard page
├── css/                 # Stylesheets
└── js/                  # JavaScript files
```

## Local Development

### Prerequisites
- Ruby 3.0+
- Bundler

### Setup and Run
```bash
# Install dependencies
bundle install

# Build the site
bundle exec jekyll build

# Serve locally
bundle exec jekyll serve --port 8080
# Visit: http://localhost:8080/letsgetcrypto/
```

## Customization

See [JEKYLL_SETUP.md](../JEKYLL_SETUP.md) in the root directory for detailed Jekyll customization instructions.

## Differences from Full Application

The GitHub Pages version is a static deployment and has some differences from the full Django application:

| Feature | GitHub Pages | Full Application |
|---------|--------------|------------------|
| Market Data | ✅ CoinGecko API | ✅ Multiple APIs |
| Price Charts | ✅ Real-time | ✅ Real-time |
| ML Training | ⚠️ Simulated | ✅ Actual ML models |
| Trading | ⚠️ Simulated | ✅ Testnet support |
| Backend API | ❌ N/A | ✅ Django REST API |
| Database | ❌ N/A | ✅ PostgreSQL/SQLite |

## Deployment

This dashboard is automatically deployed to GitHub Pages via GitHub Actions whenever changes are pushed to the `main` branch.

See `.github/workflows/deploy-pages.yml` for the deployment configuration.

## Resources

- [Main Repository](https://github.com/aaakaind/letsgetcrypto)
- [Jekyll Setup Guide](../JEKYLL_SETUP.md)
- [GitHub Pages Guide](../GITHUB_PAGES.md)

## License

Educational use only. See main repository for full details.
