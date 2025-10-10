# Advanced Cryptocurrency Trading & Prediction Tool

🚀 **A comprehensive cryptocurrency trading and prediction tool with machine learning, technical analysis, and automated trading capabilities.**

## 🌟 Features

- **📊 Multi-Source Data**: CoinGecko, Binance, Fear & Greed Index, News & Social Sentiment
- **🔬 Technical Analysis**: 15+ indicators including SMA, EMA, RSI, MACD, Bollinger Bands
- **🤖 Machine Learning**: LSTM, XGBoost, Logistic Regression with ensemble predictions
- **💼 Wallet Integration**: Bitcoin & Ethereum testnet support
- **⚡ Automated Trading**: Risk-managed trading with stop-loss and take-profit
- **🖥️ Professional GUI**: PyQt5 desktop interface with real-time charts and controls
- **🌐 Web Dashboard**: Modern, responsive web interface accessible from any browser
- **📄 GitHub Pages**: Static dashboard deployment with free hosting
- **🛡️ Risk Management**: Position sizing, daily limits, comprehensive error handling
- **🔌 MCP Server**: Model Context Protocol server for AI assistant integration
- **☁️ AWS Deployment**: Production-ready deployment to AWS with ECS and RDS

## 🚀 Quick Start

### 🌐 Try the Live Demo (GitHub Pages)

**Want to try it instantly?** The dashboard is available as a static demo:

👉 **[View Live Demo](https://aaakaind.github.io/letsgetcrypto/)** (Once GitHub Pages is configured)

See [GITHUB_PAGES.md](GITHUB_PAGES.md) for setup instructions.

### ☁️ Deploy to AWS (Production)

**Want to run in the cloud?** See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for the fastest way to deploy to AWS.

```bash
./package-for-aws.sh 1.0.0
# Upload the generated package to AWS Elastic Beanstalk or ECS
```

### Option 1: Web Dashboard (Recommended for Local Development)

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start the Web Server**:
```bash
export DJANGO_DEBUG=true
python manage.py runserver
```

3. **Access Dashboard**:
   - Open browser to `http://localhost:8000/`
   - See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for detailed usage

### Option 2: Desktop GUI

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the Application**:
```bash
python run.py
# or directly:
python main.py
```

3. **Start Trading** (Recommended: Use testnet first):
   - Select a cryptocurrency
   - Fetch market data
   - Train ML models
   - Get predictions
   - Configure trading (optional)

## ⚠️ IMPORTANT DISCLAIMERS

**🎓 EDUCATIONAL PURPOSE ONLY**
- This tool is designed for learning and research
- Cryptocurrency trading involves substantial risk
- Never invest more than you can afford to lose
- Always use testnet/sandbox mode initially

**📈 NO INVESTMENT ADVICE**
- Predictions are NOT guaranteed
- Past performance does NOT predict future results
- Always conduct your own research
- Consult financial advisors before trading

## 📚 Documentation

### Getting Started
- **[GitHub Pages Setup](GITHUB_PAGES.md)**: Free static dashboard deployment ⭐ NEW
- **[Quick Deploy to AWS](QUICK_DEPLOY.md)**: Fastest way to deploy to AWS (5 minutes)
- **[Web Dashboard Guide](DASHBOARD_GUIDE.md)**: Complete guide to using the web interface
- **[Complete User Guide](README_APP.md)**: Detailed features and usage for desktop GUI

### Advanced Features
- **[MCP Server Guide](README_MCP.md)**: AI assistant integration with Model Context Protocol
- **[Integration Guide](INTEGRATION_GUIDE.md)**: Step-by-step setup for MCP clients
- **[Claude API Setup](CLAUDE_API_SETUP.md)**: Configure Anthropic Claude API key

### Deployment
- **[GitHub Pages Guide](GITHUB_PAGES.md)**: Free hosting with GitHub Pages ⭐ NEW
- **[AWS Packaging Guide](PACKAGING_GUIDE.md)**: Create deployable packages for AWS
- **[AWS Deployment Guide](AWS_DEPLOYMENT.md)**: Production deployment to AWS

### Reference
- **[Installation Guide](requirements.txt)**: All dependencies
- **[Risk Disclosure](README_APP.md#important-disclaimers)**: Trading risks and limitations

## 🖥️ User Interfaces

### Web Dashboard
Modern, responsive web interface accessible from any browser:
- **Real-time Updates**: Auto-refreshing market data every 30 seconds
- **Interactive Charts**: Price history and RSI indicator visualization
- **Control Panel**: Easy cryptocurrency selection, model training, and trading
- **Market Overview**: Top cryptocurrencies ranked by market cap
- **Trading Signals**: ML predictions with confidence levels
- **System Log**: Real-time activity monitoring

![Web Dashboard](https://github.com/user-attachments/assets/b0083e60-b572-4067-9dfb-26ddc2f4ca77)

### Desktop GUI (PyQt5)
Feature-rich desktop application with advanced capabilities:
- **Advanced Charting**: Multiple technical indicators
- **ML Model Training**: Direct access to model configuration
- **Wallet Management**: Bitcoin and Ethereum testnet wallets
- **Offline Features**: Some functionality works without internet
- **Performance**: Better for intensive ML operations

## 🛠️ Technical Stack

- **Backend**: Python 3.8+, Django, pandas, numpy, scikit-learn, xgboost, tensorflow
- **APIs**: CCXT (Binance), CoinGecko, Fear & Greed Index
- **GUI**: PyQt5 (desktop), HTML/CSS/JavaScript (web dashboard)
- **Web**: Django REST API, Chart.js for visualizations, jQuery for interactivity
- **Crypto**: bitcoinlib, web3.py (testnet wallets)
- **ML**: LSTM neural networks, ensemble methods

## 🔧 Development

```bash
# Test core functionality
python -c "from main import *; print('✓ All imports successful')"

# Run validation tests
python -c "exec(open('main.py').read().split('if __name__')[0]); print('✓ Tests passed')"

# Test MCP server
python3 crypto_mcp_server.py  # Run the MCP server
python3 test_mcp_server.py    # Test the MCP server
```

## 🔌 MCP Server Integration

The project includes a Model Context Protocol (MCP) server that exposes cryptocurrency data to AI assistants:

```bash
# Run the MCP server
python3 crypto_mcp_server.py

# Test the server
python3 test_mcp_server.py
```

For detailed MCP integration instructions, see [README_MCP.md](README_MCP.md).

## 📄 License

Educational use only. See risk disclaimers in documentation.

---

**💡 Remember**: This is educational software for learning about cryptocurrency analysis and trading systems. Always practice with testnet first!