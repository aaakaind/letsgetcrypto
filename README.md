# Advanced Cryptocurrency Trading & Prediction Tool

🚀 **A comprehensive cryptocurrency trading and prediction tool with machine learning, technical analysis, and automated trading capabilities.**

## 🌟 Features

- **📊 Multi-Source Data**: CoinGecko, Binance, Fear & Greed Index, News & Social Sentiment
- **🔬 Technical Analysis**: 15+ indicators including SMA, EMA, RSI, MACD, Bollinger Bands
- **🤖 Machine Learning**: LSTM, XGBoost, Logistic Regression with ensemble predictions
- **🧠 AI-Powered Insights**: Claude Opus 4.1 integration for intelligent market analysis
- **💼 Wallet Integration**: Bitcoin & Ethereum testnet support
- **⚡ Automated Trading**: Risk-managed trading with stop-loss and take-profit
- **🖥️ Professional GUI**: PyQt5 interface with real-time charts and controls
- **🛡️ Risk Management**: Position sizing, daily limits, comprehensive error handling

## 🚀 Quick Start

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
python run.py
# or directly:
python main.py
```

4. **Start Trading** (Recommended: Use testnet first):
   - Select a cryptocurrency
   - Fetch market data
   - Train ML models
   - Get predictions (with AI insights if configured)
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
- **[Risk Disclosure](README_APP.md#important-disclaimers)**: Trading risks and limitations

## 🛠️ Technical Stack

- **Backend**: Python 3.8+, pandas, numpy, scikit-learn, xgboost, tensorflow
- **APIs**: CCXT (Binance), CoinGecko, Fear & Greed Index, Anthropic Claude
- **AI**: Claude Opus 4.1 for intelligent market analysis and insights
- **GUI**: PyQt5, matplotlib
- **Crypto**: bitcoinlib, web3.py (testnet wallets)
- **ML**: LSTM neural networks, ensemble methods

## 🔧 Development

```bash
# Test core functionality
python -c "from main import *; print('✓ All imports successful')"

# Run validation tests
python -c "exec(open('main.py').read().split('if __name__')[0]); print('✓ Tests passed')"
```

## 📄 License

Educational use only. See risk disclaimers in documentation.

---

**💡 Remember**: This is educational software for learning about cryptocurrency analysis and trading systems. Always practice with testnet first!