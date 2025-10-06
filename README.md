# Advanced Cryptocurrency Trading & Prediction Tool

🚀 **A comprehensive cryptocurrency trading and prediction tool with machine learning, technical analysis, and automated trading capabilities.**

## 🌟 Features

- **📊 Multi-Source Data**: CoinGecko, Binance, Fear & Greed Index, News & Social Sentiment
- **🔬 Technical Analysis**: 15+ indicators including SMA, EMA, RSI, MACD, Bollinger Bands
- **🤖 Machine Learning**: LSTM, XGBoost, Logistic Regression with ensemble predictions
- **🔄 Feedback Loop**: Automated continuous learning with tiered training system (NEW!)
- **💼 Wallet Integration**: Bitcoin & Ethereum testnet support
- **⚡ Automated Trading**: Risk-managed trading with stop-loss and take-profit
- **🖥️ Professional GUI**: PyQt5 interface with real-time charts and controls
- **🛡️ Risk Management**: Position sizing, daily limits, comprehensive error handling
- **🔌 MCP Server**: Model Context Protocol server for AI assistant integration
- **☁️ AWS Deployment**: Production-ready deployment to AWS with ECS and RDS

## 🚀 Quick Start

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

- **[Complete User Guide](README_APP.md)**: Detailed features and usage
- **[Feedback Loop Guide](FEEDBACK_LOOP.md)**: Automated training and continuous learning (NEW!)
- **[MCP Server Guide](README_MCP.md)**: AI assistant integration with Model Context Protocol
- **[Integration Guide](INTEGRATION_GUIDE.md)**: Step-by-step setup for MCP clients
- **[AWS Deployment Guide](AWS_DEPLOYMENT.md)**: Production deployment to AWS
- **[Installation Guide](requirements.txt)**: All dependencies
- **[Risk Disclosure](README_APP.md#important-disclaimers)**: Trading risks and limitations

## 🛠️ Technical Stack

- **Backend**: Python 3.8+, pandas, numpy, scikit-learn, xgboost, tensorflow
- **APIs**: CCXT (Binance), CoinGecko, Fear & Greed Index
- **GUI**: PyQt5, matplotlib
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