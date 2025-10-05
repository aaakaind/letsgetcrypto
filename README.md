# Advanced Cryptocurrency Trading & Prediction Tool

🚀 **A comprehensive cryptocurrency trading and prediction tool with machine learning, technical analysis, and automated trading capabilities.**

## 🌟 Features

- **📊 Multi-Source Data**: CoinGecko, Binance, Fear & Greed Index, News & Social Sentiment
- **🔬 Technical Analysis**: 15+ indicators including SMA, EMA, RSI, MACD, Bollinger Bands
- **🤖 Machine Learning**: LSTM, XGBoost, Logistic Regression with ensemble predictions
- **💼 Wallet Integration**: Bitcoin & Ethereum testnet support
- **⚡ Automated Trading**: Risk-managed trading with stop-loss and take-profit
- **🖥️ Professional GUI**: PyQt5 interface with real-time charts and controls
- **🛡️ Risk Management**: Position sizing, daily limits, comprehensive error handling

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
- **[Installation Guide](requirements.txt)**: All dependencies
- **[Claude MCP Server](MCP_SERVER.md)**: Use with Claude AI via Model Context Protocol
- **[Risk Disclosure](README_APP.md#important-disclaimers)**: Trading risks and limitations

## 🛠️ Technical Stack

- **Backend**: Python 3.8+, pandas, numpy, scikit-learn, xgboost, tensorflow
- **APIs**: CCXT (Binance), CoinGecko, Fear & Greed Index
- **GUI**: PyQt5, matplotlib
- **Crypto**: bitcoinlib, web3.py (testnet wallets)
- **ML**: LSTM neural networks, ensemble methods

## 🤖 Claude AI Integration

Use LetsGetCrypto with Claude AI via the Model Context Protocol (MCP):

```bash
# Start the MCP server
python mcp_server.py
```

Once configured with Claude Desktop, you can ask Claude:
- "What's the current Bitcoin price?"
- "Analyze Ethereum's technical indicators"
- "Should I buy or sell Solana?"
- "Give me a market overview of top cryptocurrencies"

See **[MCP_SERVER.md](MCP_SERVER.md)** for complete setup instructions.

## 🔧 Development

```bash
# Test core functionality
python -c "from main import *; print('✓ All imports successful')"

# Run validation tests
python -c "exec(open('main.py').read().split('if __name__')[0]); print('✓ Tests passed')"

# Test MCP server
python test_mcp_server.py
```

## 📄 License

Educational use only. See risk disclaimers in documentation.

---

**💡 Remember**: This is educational software for learning about cryptocurrency analysis and trading systems. Always practice with testnet first!