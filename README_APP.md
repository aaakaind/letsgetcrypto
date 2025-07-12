# Advanced Cryptocurrency Trading & Prediction Tool

## Overview

This is a comprehensive cryptocurrency trading and prediction tool that combines multiple data sources, machine learning models, and automated trading capabilities in a user-friendly PyQt5 GUI interface.

## Features

### 🔗 Data Sources
- **CoinGecko API**: Historical price data with hourly/daily intervals
- **Binance API (via CCXT)**: Real-time prices and order execution
- **Fear & Greed Index**: Market sentiment indicator
- **News Sentiment**: Simulated cryptocurrency news analysis
- **Social Sentiment**: Simulated social media sentiment tracking

### 📊 Technical Analysis
- **Moving Averages**: SMA (7, 25, 99 periods), EMA (12, 26 periods)
- **Momentum Indicators**: RSI, MACD with signal line
- **Volatility**: Bollinger Bands, rolling volatility
- **Volume Analysis**: Volume SMA, VWAP
- **Support/Resistance**: Dynamic level detection
- **Market Timing**: Quarter-end flags for institutional activity

### 🤖 Machine Learning Models
- **LSTM Neural Networks**: Deep learning for price regression (GPU-accelerated)
- **XGBoost**: Gradient boosting for classification (GPU when available)
- **Logistic Regression**: Baseline linear model
- **Ensemble Method**: Weighted combination of all models for final signals

### 💼 Wallet Integration
- **Bitcoin Testnet**: Wallet creation and balance tracking
- **Ethereum Testnet**: Account generation and management
- **Security**: Private key handling with encryption recommendations

### 🔄 Automated Trading
- **Exchange Integration**: Binance support via CCXT
- **Risk Management**: Position sizing, stop-loss, take-profit
- **Trade Limits**: Daily trade caps and portfolio allocation controls
- **Sandbox Mode**: Safe testing environment

### 🖥️ GUI Interface
- **Coin Selection**: Multiple cryptocurrency support
- **Real-time Charts**: Price, RSI, and volume visualization
- **Prediction Display**: ML model outputs and trading signals
- **Trading Controls**: Manual and automatic trade execution
- **Wallet Information**: Address and balance display
- **Live Status**: Real-time updates and logging

## Installation

1. **Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Additional Requirements**:
- Python 3.8+
- PyQt5 for GUI
- Optional: GPU for accelerated ML training

## Usage

### Starting the Application
```bash
python main.py
```

### Basic Workflow

1. **Select Cryptocurrency**: Choose from Bitcoin, Ethereum, etc.
2. **Fetch Data**: Click "Refresh Data" to get latest market information
3. **Train Models**: Click "Train Models" to prepare ML predictions
4. **Get Predictions**: Generate buy/sell/hold signals
5. **Set Up Trading** (Optional):
   - Enter Binance API credentials
   - Enable testnet mode for safety
   - Configure risk parameters
6. **Monitor Performance**: Track trades and portfolio metrics

### API Configuration

For live trading, you'll need:
- **Binance API Key**: For market data and trading
- **Binance Secret Key**: For authenticated operations
- **Testnet Mode**: Recommended for learning and testing

⚠️ **Always use testnet/sandbox mode initially**

## Risk Management

### Built-in Controls
- **Position Sizing**: Maximum 10% of portfolio per trade
- **Stop Loss**: 5% automatic loss protection
- **Take Profit**: 15% profit target
- **Daily Limits**: Maximum 5 trades per day

### Configurable Parameters
```python
risk_settings = {
    'max_position_size': 0.1,    # 10% max position
    'stop_loss_pct': 0.05,       # 5% stop loss
    'take_profit_pct': 0.15,     # 15% take profit
    'max_daily_trades': 5        # 5 trades/day max
}
```

## IMPORTANT DISCLAIMERS

### ⚠️ Educational Purpose Only
This tool is designed for educational and research purposes. It demonstrates:
- Cryptocurrency data analysis techniques
- Machine learning applications in finance
- Trading system architecture
- Risk management principles

### ⚠️ Trading Risks
**Cryptocurrency trading involves substantial risk:**
- **High Volatility**: Crypto prices can change rapidly
- **Market Risk**: External factors affect all cryptocurrencies
- **Technical Risk**: Software bugs or connectivity issues
- **Regulatory Risk**: Legal status may change
- **Liquidity Risk**: May be difficult to exit positions

### ⚠️ No Investment Advice
- Predictions are **NOT guaranteed**
- Past performance does **NOT predict future results**
- Always conduct your own research
- Consult financial advisors before trading
- Never invest more than you can afford to lose

### ⚠️ Model Limitations
- ML models are trained on historical data
- Market conditions constantly change
- Black swan events cannot be predicted
- Overfitting may occur with limited data

## Architecture

### Core Components

```
main.py
├── DataFetcher          # API data collection
├── TechnicalIndicators  # Technical analysis
├── MLModels            # Machine learning
├── CryptoWallet        # Wallet management
├── TradingEngine       # Trade execution
└── CryptoPredictionApp # GUI interface
```

### Data Flow
1. **Fetch** → Raw market data from APIs
2. **Process** → Technical indicators and features
3. **Predict** → ML model ensemble predictions
4. **Execute** → Trading decisions with risk controls
5. **Monitor** → Performance tracking and logging

## Development

### Adding New Features
- **New Indicators**: Extend `TechnicalIndicators` class
- **New Models**: Add to `MLModels` with ensemble integration
- **New Exchanges**: Extend `TradingEngine` with CCXT
- **New Data Sources**: Add to `DataFetcher` with error handling

### Testing
```bash
# Test core functionality
python -c "from main import *; print('All imports successful')"

# Test with sample data
python test_gui.py
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check internet connection
   - Verify API keys are correct
   - Ensure rate limits not exceeded

2. **GUI Not Starting**
   - Install PyQt5: `pip install PyQt5`
   - Check X11 forwarding if using SSH
   - Try different display backends

3. **Model Training Slow**
   - Reduce data size for testing
   - Check CPU/GPU utilization
   - Consider cloud computing for large datasets

4. **Trading Errors**
   - Verify exchange connectivity
   - Check account permissions
   - Ensure sufficient balance

### Logs and Debugging
- Application logs: `crypto_trading.log`
- Console output: Real-time status updates
- Error traces: Detailed exception information

## License

This project is for educational purposes. Use at your own risk.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with detailed description

## Support

For issues or questions:
1. Check this documentation
2. Review application logs
3. Test with sample data first
4. Use testnet before live trading

---

**Remember: This is educational software. Always do your own research and never invest more than you can afford to lose.**