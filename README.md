# Advanced Cryptocurrency Trading & Prediction Tool

🚀 **A comprehensive cryptocurrency trading and prediction tool with machine learning, technical analysis, and automated trading capabilities.**

> **📖 New to the project?** Start here: **[GETTING_STARTED.md](GETTING_STARTED.md)** - Get from clone to running in minutes!

## 🎯 Version 1.0.0 - Deployment Ready

**This version is production-ready with comprehensive deployment documentation, health checks, and validation tools.**

## 🌟 Features

- **📊 Multi-Source Data**: CoinGecko, Binance, Fear & Greed Index, News & Social Sentiment
- **🔬 Technical Analysis**: 15+ indicators including SMA, EMA, RSI, MACD, Bollinger Bands
- **🤖 Machine Learning**: LSTM, XGBoost, Logistic Regression with ensemble predictions
- **🧠 AI-Powered Insights**: Claude Opus 4.1 integration for intelligent market analysis
- **♾️ Infinite Context Window**: Prompt caching for 90% cost reduction and 85% faster responses (NEW!)
- **🔄 Feedback Loop**: Automated continuous learning with tiered training system
- **💼 Wallet Integration**: Bitcoin & Ethereum testnet support
- **⚡ Automated Trading**: Risk-managed trading with stop-loss and take-profit
- **🖥️ Professional GUI**: PyQt5 desktop interface with real-time charts and controls
- **🌐 Web Dashboard**: Modern, responsive web interface accessible from any browser
- **📄 GitHub Pages**: Static dashboard deployment with free hosting
- **🛡️ Risk Management**: Position sizing, daily limits, comprehensive error handling
- **🔌 MCP Server**: Model Context Protocol server for AI assistant integration
- **☁️ Cloud Deployment**: Production-ready deployment to AWS (ECS/RDS) or GCP (Cloud Run/Cloud SQL)
- **🔄 CI/CD Pipeline**: Automated builds and deployments with AWS CodeBuild/CodePipeline or GCP Cloud Build

## 🚀 Quick Start

### ⚡ One-Command Setup (From Fresh GitHub Clone)

**The fastest way to get started:**

```bash
git clone https://github.com/aaakaind/letsgetcrypto.git
cd letsgetcrypto
./setup.sh
```

This automated setup script will:
- ✅ Check Python version (3.8+ required)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up configuration files
- ✅ Create ML model directories
- ✅ Run database migrations
- ✅ Optionally train initial ML models

Then run the application:

```bash
./run.sh
```

Choose from:
- 🌐 **Web Dashboard** - Modern browser interface at http://localhost:8000
- 🖥️ **Desktop GUI** - Full-featured PyQt5 application
- 📊 **Both** - Run web and desktop together

📖 **Detailed Guide**: See [GITHUB_CLONE_GUIDE.md](GITHUB_CLONE_GUIDE.md) for complete setup instructions

### 🎯 Interactive Deployment Menu

For deployment options, use the quick-start script:

```bash
./quick-start.sh
```

This script guides you through:
- 🐳 Docker Compose (local development)
- ☁️ AWS Elastic Beanstalk (simple cloud)
- 🚀 AWS ECS Fargate (production cloud)
- 📄 GitHub Pages (static demo)
- 🧪 Deployment validation
- 📚 Documentation access

### 🌐 Try the Live Demo (GitHub Pages)

**Want to try it instantly?** The dashboard is available as a static demo:

👉 **[View Live Demo](https://aaakaind.github.io/letsgetcrypto/)** (Once GitHub Pages is configured)

See [GITHUB_PAGES.md](GITHUB_PAGES.md) for setup instructions and [JEKYLL_SETUP.md](JEKYLL_SETUP.md) for Jekyll customization.

### 🧠 Initialize ML Learning Environment

Set up the machine learning environment with pre-trained models:

```bash
./init_ml_environment.sh
```

This creates:
- Model storage directories
- Sample training data
- Pre-trained models (Logistic Regression, XGBoost)
- Feature scalers and preprocessors

The ML environment supports:
- Automatic model training with real cryptocurrency data
- Feedback loop for continuous learning
- Multiple model types (LSTM, XGBoost, Logistic Regression)
- Ensemble predictions for better accuracy

### ☁️ Deploy to Cloud (Production)

**Want to run in the cloud?** Choose your preferred cloud provider:

**AWS Deployment:**
```bash
./package-for-aws.sh 1.0.0
# See AWS_DEPLOYMENT.md for details
```

**Google Cloud Deployment:**
```bash
cd gcp
./deploy-gcp.sh
# See GCP_DEPLOYMENT.md for details
```

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for the fastest way to deploy to AWS or [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) for Google Cloud Platform.

### Manual Setup (Advanced Users)

#### Option 1: Web Dashboard (Recommended for Local Development)

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

#### Option 2: Desktop GUI

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Claude AI** (Optional but recommended):
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. **Run the Application**:
```bash
python main.py
```

4. **Start Trading** (Recommended: Use testnet first):
   - Select a cryptocurrency
   - Fetch market data
   - Train ML models
   - Get predictions (with AI insights if configured)
   - Configure trading (optional)

## 🔄 Feedback Loop: Automated Continuous Learning

The application now includes an **intelligent feedback loop system** that automatically trains and improves ML models over time:

### Key Features
- **🎯 Tiered Training**: Three-tier system with hourly (basic), 6-hourly (intermediate), and daily (advanced) training
- **📊 Performance Tracking**: Monitors model accuracy and identifies performance trends
- **⚡ Smart Triggers**: Automatically retrains when performance drops or time intervals elapse
- **📝 Prediction Logging**: Tracks predictions vs actual outcomes for continuous learning
- **🔧 Configurable**: Adjust training intervals, thresholds, and evaluation windows

### Quick Usage
1. Enable automatic feedback loop in the GUI
2. The system runs in the background, checking for retraining needs every hour
3. View feedback loop status to see performance trends and training history
4. Manually trigger training cycles when needed

See **[FEEDBACK_LOOP.md](FEEDBACK_LOOP.md)** for detailed documentation.

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

### Quick Start & Setup
- **[⚡ GitHub Clone Guide](GITHUB_CLONE_GUIDE.md)**: **NEW!** Complete guide from clone to running app ⭐
- **[🚀 Deployment Guide](DEPLOYMENT_GUIDE.md)**: Complete production deployment guide
- **[✅ Release Checklist](RELEASE_CHECKLIST.md)**: Pre-deployment validation checklist
- **[GitHub Pages Setup](GITHUB_PAGES.md)**: Free static dashboard deployment
- **[Quick Deploy to AWS](QUICK_DEPLOY.md)**: Fastest way to deploy to AWS (5 minutes)

### Getting Started
- **[Web Dashboard Guide](DASHBOARD_GUIDE.md)**: Complete guide to using the web interface
- **[Complete User Guide](README_APP.md)**: Detailed features and usage for desktop GUI
- **[Claude AI Setup Guide](CLAUDE_SETUP.md)**: Configure AI-powered insights
- **[Prompt Caching Guide](PROMPT_CACHING.md)**: Infinite context window with 90% cost reduction
- **[Feedback Loop Guide](FEEDBACK_LOOP.md)**: Automated training and continuous learning

### Advanced Features
- **[MCP Server Guide](README_MCP.md)**: AI assistant integration with Model Context Protocol
- **[Integration Guide](INTEGRATION_GUIDE.md)**: Step-by-step setup for MCP clients
- **[Claude API Setup](CLAUDE_API_SETUP.md)**: Configure Anthropic Claude API key

### Production Deployment
- **[AWS Packaging Guide](PACKAGING_GUIDE.md)**: Create deployable packages for AWS
- **[AWS Deployment Guide](AWS_DEPLOYMENT.md)**: Production deployment to AWS
- **[CI/CD Pipeline Guide](CICD_GUIDE.md)**: Automated builds and deployments with AWS CodeBuild

### Reference
- **[Installation Guide](requirements.txt)**: All dependencies
- **[Testing Guide](TESTING.md)**: Running tests and validation
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

- **Backend**: Python 3.8+, pandas, numpy, scikit-learn, xgboost, tensorflow
- **APIs**: CCXT (Binance), CoinGecko, Fear & Greed Index, Anthropic Claude
- **AI**: Claude Opus 4.1 for intelligent market analysis and insights
- **GUI**: PyQt5, matplotlib
- **Backend**: Python 3.8+, Django, pandas, numpy, scikit-learn, xgboost, tensorflow
- **APIs**: CCXT (Binance), CoinGecko, Fear & Greed Index
- **GUI**: PyQt5 (desktop), HTML/CSS/JavaScript (web dashboard)
- **Web**: Django REST API, Chart.js for visualizations, jQuery for interactivity
- **Crypto**: bitcoinlib, web3.py (testnet wallets)
- **ML**: LSTM neural networks, ensemble methods

## 🔧 Development & Testing

### Running Tests

The project includes a comprehensive test suite with a unified test runner:

```bash
# Run all available tests
python test_all.py

# Run specific test suites
python test_all.py --tests integration claude

# List available test suites
python test_all.py --list

# Run individual test files
python test_integration.py      # Core integration tests
python test_mcp_server.py        # MCP server tests
python test_claude_integration.py # Claude AI tests
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

### Development Commands

```bash
# Test core functionality
python -c "from main import *; print('✓ All imports successful')"

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