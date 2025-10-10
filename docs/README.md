# LetsGetCrypto - GitHub Pages Dashboard

This is a static version of the LetsGetCrypto dashboard hosted on GitHub Pages.

## Features

- 📊 Real-time cryptocurrency market data from CoinGecko API
- 📈 Interactive price charts with historical data
- 💹 Top cryptocurrencies ranked by market cap
- 🔄 Auto-refresh every 30 seconds
- 📱 Responsive design for mobile and desktop

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

## Running Locally

To test the static version locally:

```bash
# Using Python's built-in HTTP server
cd docs
python -m http.server 8080

# Then open: http://localhost:8080
```

## Deployment

This dashboard is automatically deployed to GitHub Pages via GitHub Actions whenever changes are pushed to the `main` branch.

See `.github/workflows/deploy-pages.yml` for the deployment configuration.

## Source Code

Full source code with Django backend available at: https://github.com/aaakaind/letsgetcrypto

## License

Educational use only. See main repository for full details.
