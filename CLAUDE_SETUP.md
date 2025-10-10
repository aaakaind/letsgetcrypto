# Claude Opus 4.1 Integration Setup Guide

## Overview

This cryptocurrency trading tool now includes integration with **Claude Opus 4.1**, Anthropic's most advanced AI model, to provide intelligent market analysis and insights.

## What Claude Provides

When enabled, Claude Opus 4.1 enhances the tool with:

1. **Comprehensive Market Analysis**: Natural language analysis of market conditions, trends, and patterns
2. **Trading Recommendations**: AI-powered buy/sell/hold recommendations with detailed reasoning
3. **Risk Assessment**: Intelligent evaluation of risk factors and volatility
4. **Key Insights**: Bullet-point summaries of critical market factors
5. **Signal Explanations**: Easy-to-understand interpretations of technical trading signals

## Setup Instructions

### Step 1: Get an Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### Step 2: Configure Your Environment

#### Linux/Mac:

```bash
# Temporary (current session only)
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (Command Prompt):

```cmd
# Temporary
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Permanent
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
```

#### Windows (PowerShell):

```powershell
# Temporary
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Permanent
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-your-key-here', 'User')
```

### Step 3: Install Required Package

If you haven't already installed the anthropic library:

```bash
pip install anthropic>=0.39.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Step 4: Verify Setup

Run the test script to verify your setup:

```bash
python test_claude_integration.py
```

You should see:
```
✓ All tests passed!
✓ Claude Opus 4.1 is ready to use
```

## Usage

### In the GUI Application (main.py)

Once configured, Claude analysis is automatically included when you:

1. Select a cryptocurrency
2. Fetch market data
3. Train ML models
4. Click "Get Predictions"

The predictions panel will show:
- Standard ML predictions (Logistic Regression, XGBoost, LSTM)
- Ensemble prediction and trading signal
- **NEW: Claude AI Analysis section** with:
  - Market analysis
  - AI recommendation
  - Risk assessment
  - Key insights

### In the Headless API (headless_crypto_api.py)

```python
from headless_crypto_api import HeadlessCryptoAPI

# Initialize with Claude enabled (default)
api = HeadlessCryptoAPI(enable_claude=True)

# Analyze a cryptocurrency
result = api.analyze_cryptocurrency('bitcoin', days=30, use_claude=True)

# Access Claude analysis
if 'claude_analysis' in result:
    print(result['claude_analysis']['analysis'])
    print(result['claude_analysis']['recommendation'])
    print(result['claude_analysis']['risk_assessment'])
```

### Direct Use of ClaudeAnalyzer

```python
from claude_analyzer import ClaudeAnalyzer

analyzer = ClaudeAnalyzer()

if analyzer.is_available():
    # Analyze market data
    analysis = analyzer.analyze_market_data(
        coin_name="Bitcoin",
        current_price=45000.0,
        price_change_24h=3.5,
        technical_indicators={
            'rsi': 65.5,
            'macd': 0.0023,
            'sma_7': 44800,
            'sma_25': 44200,
            'volatility': 0.025
        },
        ml_predictions={
            'signal': 'BUY',
            'confidence': 0.75
        },
        fear_greed_index=65
    )
    
    print(analysis['analysis'])
    print(analysis['recommendation'])
```

## Graceful Degradation

The integration is designed to work gracefully without an API key:

- ✓ Application works normally without Claude
- ✓ No errors or crashes if API key is missing
- ✓ Clear warning messages when Claude is unavailable
- ✓ All other features (ML, technical analysis, trading) work independently

## Cost Considerations

**Important**: Claude Opus 4.1 API calls are **not free**. 

- API usage is billed by Anthropic based on tokens
- Each market analysis uses approximately 1000-1500 tokens
- Monitor your usage at: https://console.anthropic.com/
- Set usage limits in your Anthropic dashboard

Typical costs (as of 2024):
- Input: $15 per million tokens
- Output: $75 per million tokens
- Average analysis: ~$0.03 - $0.05 per request

**Recommendation**: 
- Start with a small budget and monitor usage
- Consider caching results for frequently analyzed coins
- Use `use_claude=False` in API calls when testing

## Troubleshooting

### "No Anthropic API key provided"
- Check that `ANTHROPIC_API_KEY` environment variable is set
- Restart your terminal/IDE after setting the variable
- Verify the key starts with `sk-ant-`

### "Claude analysis failed: Invalid API key"
- Double-check your API key is correct
- Ensure the key hasn't expired
- Verify your Anthropic account is active

### "Rate limit exceeded"
- You've made too many requests too quickly
- Wait a few seconds and try again
- Consider implementing rate limiting in your code

### Analysis returns generic messages
- API key might not be configured correctly
- Check the logs for specific error messages
- Run `test_claude_integration.py` to diagnose

## Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secure configuration files
   - Rotate keys periodically

2. **Usage Optimization**
   - Cache analysis results when appropriate
   - Don't fetch new analysis on every page refresh
   - Implement reasonable request delays

3. **Error Handling**
   - The tool handles Claude unavailability gracefully
   - Always check if `claude_analysis` exists in results
   - Provide fallback behavior in your code

4. **Production Use**
   - Monitor API costs and set alerts
   - Implement request queuing for high-volume scenarios
   - Consider using Claude 3.5 Sonnet for cost savings (modify `claude_analyzer.py`)

## Example Output

When Claude is enabled and working, you'll see output like:

```
CLAUDE OPUS 4.1 AI ANALYSIS
===========================================

MARKET ANALYSIS:
Bitcoin is currently showing bullish momentum with positive technical indicators. 
The RSI at 65.5 suggests strong buying pressure without being overbought. The MACD 
crossover indicates continued upward momentum. The 7-day SMA crossing above the 
25-day SMA confirms the bullish trend. Market sentiment is in the "Greed" zone, 
which can be both supportive and cautionary.

RECOMMENDATION:
MODERATE BUY - The technical indicators align well with the ML prediction, suggesting 
this is a reasonable entry point. However, the elevated Fear & Greed Index warrants 
caution on position sizing.

RISK ASSESSMENT:
Current volatility at 2.5% is moderate. The primary risk is potential profit-taking 
given recent gains. Consider implementing a stop-loss at $42,500 to protect gains.

KEY INSIGHTS:
1. Strong technical alignment across multiple indicators
2. Market sentiment approaching overheated levels
3. Volume trending higher, confirming price action
4. Potential resistance near $46,000 level
5. Overall trend remains bullish in short to medium term
```

## Support

For issues or questions:
1. Check this documentation
2. Review logs in `crypto_trading.log`
3. Run diagnostic script: `test_claude_integration.py`
4. Review Anthropic documentation: https://docs.anthropic.com/

---

**Remember**: This tool is for educational purposes only. AI analysis should complement, not replace, your own research and judgment. Always conduct thorough due diligence before making any trading decisions.
