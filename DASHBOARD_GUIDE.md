# Web Dashboard Guide

## Overview

The LetsGetCrypto web dashboard provides a modern, interactive interface for monitoring cryptocurrency markets, training ML models, viewing predictions, and executing trades.

## Starting the Dashboard

### Method 1: Django Development Server (Recommended for Local Testing)

```bash
# Set debug mode for development
export DJANGO_DEBUG=true

# Run the Django development server
python manage.py runserver

# Access the dashboard at:
# http://localhost:8000/
```

### Method 2: Production Deployment

For production deployments, use Gunicorn or another WSGI server:

```bash
# Install Gunicorn if not already installed
pip install gunicorn

# Run with Gunicorn
gunicorn letsgetcrypto_django.wsgi:application --bind 0.0.0.0:8000

# Or use the deployment scripts in the repository
```

## Dashboard Features

### Control Panel (Left Sidebar)

#### Cryptocurrency Selection
- Select from Bitcoin, Ethereum, Binance Coin, Cardano, or Solana
- Changes apply to all dashboard views

#### Data Controls
- **Days of Data**: Adjust historical data range (7-365 days)
- **Refresh Data**: Manually fetch latest market information
- **Train Models**: Train ML models on current data
- **Get Predictions**: Generate trading signals based on trained models

#### Trading Controls
- **Testnet Mode**: Toggle for safe testing (ALWAYS use for practice!)
- **Trade Amount**: Set the USD amount for trades
- **Buy/Sell Buttons**: Execute trades based on current settings

#### System Log
- Real-time activity logging
- Timestamped entries
- Color-coded messages (errors in red)

### Main Dashboard Area

#### Stats Cards
Display real-time metrics:
- **Current Price**: Latest price with 24h change percentage
- **Market Cap**: Total market capitalization
- **24h Volume**: 24-hour trading volume
- **ML Signal**: Latest model prediction (BUY/SELL/HOLD) with confidence

#### Charts
- **Price Chart**: Historical price visualization with interactive Chart.js
- **RSI Indicator**: Relative Strength Index technical indicator

#### Market Overview Table
- Top cryptocurrencies ranked by market cap
- Price, 24h change, market cap, and volume data
- Color-coded changes (green for gains, red for losses)

#### ML Predictions & Trading Signals
- Displays latest model predictions
- Shows signal type and confidence level
- Timestamp of when prediction was generated

#### Trading History
- Complete log of executed trades
- Includes timestamp, symbol, action, price, amount, and status
- Updates automatically as trades are executed

## Using the Dashboard

### Basic Workflow

1. **Monitor Markets**
   - Dashboard loads with default cryptocurrency (Bitcoin)
   - Market overview table shows top cryptocurrencies
   - Stats cards display current metrics

2. **Analyze Data**
   - Change the cryptocurrency using the dropdown
   - Adjust time range with "Days of Data"
   - Click "Refresh Data" to get latest information
   - Review price and RSI charts

3. **Train ML Models**
   - Ensure you have loaded data for your selected cryptocurrency
   - Click "Train Models" button
   - Wait for training to complete (status shown in system log)
   - Models are trained on the current data set

4. **Get Predictions**
   - After training, click "Get Predictions"
   - View signal in the ML Signal card (BUY/SELL/HOLD)
   - Check confidence level
   - Review detailed prediction in the predictions section

5. **Execute Trades** (Practice Mode)
   - Ensure "Testnet Mode" is enabled (checkbox should be checked)
   - Set trade amount in USD
   - Click "Buy" or "Sell" based on prediction or your analysis
   - Monitor execution in system log
   - View completed trade in trading history

### Auto-Refresh

The dashboard automatically refreshes market data every 30 seconds to keep information current. You can also manually refresh at any time using the "Refresh Data" button.

## API Endpoints

The dashboard uses these backend endpoints:

- `GET /api/dashboard/` - Dashboard page
- `GET /api/market/` - Market overview (top cryptocurrencies)
- `GET /api/price/{symbol}/` - Current price for a cryptocurrency
- `GET /api/history/{symbol}/?days={n}` - Historical price data
- `GET /api/health/` - System health check

## Safety Features

### Testnet Mode
- **ALWAYS** enabled by default
- Simulates trades without using real funds
- Safe for learning and testing strategies
- Uncheck only when you're ready for live trading (NOT recommended)

### Risk Warnings
- Dashboard displays prominent risk warning in footer
- System log shows trade mode (TESTNET or LIVE)
- Confirmation required for live trades

## Troubleshooting

### Dashboard Not Loading
1. Ensure Django server is running
2. Check that DEBUG=True for development
3. Verify static files are being served correctly

### API Errors
1. Check internet connectivity (external APIs required)
2. Review system log for error messages
3. Verify API rate limits haven't been exceeded

### Charts Not Displaying
1. Ensure external CDN resources can be loaded (Chart.js, jQuery)
2. Check browser console for JavaScript errors
3. Try refreshing the page

### No Market Data
1. External cryptocurrency APIs may be temporarily unavailable
2. Check /api/health/ endpoint for API status
3. Wait a moment and try refreshing

## Comparison with PyQt5 GUI

The repository includes both web and desktop interfaces:

### Web Dashboard (`/api/dashboard/`)
- **Pros**: 
  - Access from any device with a browser
  - No installation required on client
  - Better for remote access and monitoring
  - Easier to share with team members
  - Responsive design for mobile devices

### PyQt5 Desktop GUI (`main.py`)
- **Pros**: 
  - More advanced charting capabilities
  - Tighter integration with ML training
  - Wallet management features
  - Works offline for some features
  - Better performance for intensive operations

Both interfaces connect to the same backend data sources and can be used based on your preference and use case.

## Security Notes

⚠️ **IMPORTANT**: 
- Never share your API keys or credentials
- Always use testnet mode for practice
- This tool is for educational purposes only
- Cryptocurrency trading involves substantial risk
- Never invest more than you can afford to lose

## Contributing

To add new features to the dashboard:

1. Update `crypto_api/templates/dashboard.html` for UI changes
2. Modify `crypto_api/static/css/dashboard.css` for styling
3. Edit `crypto_api/static/js/dashboard.js` for interactive features
4. Add new API endpoints in `crypto_api/views.py` and `crypto_api/urls.py`

## Support

For issues or questions:
1. Check this documentation
2. Review the main README.md
3. Check application logs
4. Test with testnet mode first
5. Open an issue on GitHub

---

**Remember**: This dashboard is for educational purposes. Always conduct your own research and consult with financial advisors before making investment decisions.
