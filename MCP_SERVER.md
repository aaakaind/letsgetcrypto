# Claude MCP Server for LetsGetCrypto

## Overview

This MCP (Model Context Protocol) server exposes the LetsGetCrypto cryptocurrency analysis tools to Claude AI, enabling Claude to provide real-time cryptocurrency market data, technical analysis, and trading signals.

## Features

The MCP server provides the following tools to Claude:

### 1. `get_crypto_price`
Get historical price data for a cryptocurrency.

**Parameters:**
- `coin_id` (string): CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'cardano')
- `days` (integer): Number of days of historical data (default: 30)

**Returns:** JSON with current price, 24h change, volume, market cap, highs/lows

### 2. `analyze_cryptocurrency`
Perform comprehensive technical analysis on a cryptocurrency.

**Parameters:**
- `coin_id` (string): CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana')
- `days` (integer): Number of days to analyze (default: 30)

**Returns:** JSON with technical indicators (RSI, MACD, etc.), signals, and analysis

### 3. `get_market_overview`
Get market overview with top cryptocurrencies by market cap.

**Parameters:**
- `limit` (integer): Number of top coins to fetch (default: 10, max: 50)

**Returns:** JSON with market data for top cryptocurrencies

### 4. `get_trading_signals`
Generate trading signals based on technical analysis.

**Parameters:**
- `coin_id` (string): CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'dogecoin')
- `days` (integer): Number of days to analyze (default: 30)

**Returns:** JSON with BUY/SELL/HOLD signals, confidence levels, and reasons

### 5. `list_supported_coins`
List all pre-configured supported cryptocurrency IDs.

**Parameters:** None

**Returns:** JSON with list of supported coin IDs

## Quick Start

For the impatient:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test the server
python mcp_server.py --http

# 3. Add to Claude Desktop config (see Configuration section below)
```

## Installation

### Prerequisites

1. Python 3.8 or higher
2. Claude Desktop (or another MCP-compatible client)

### Setup Steps

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Test the MCP server:**
```bash
python mcp_server.py
```

This will start the server in HTTP mode for testing.

3. **Configure Claude Desktop:**

Add the following to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "letsgetcrypto": {
      "command": "python",
      "args": [
        "/absolute/path/to/letsgetcrypto/mcp_server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/letsgetcrypto/` with the actual path to your installation.

**Note:** The server runs in stdio mode by default, so the `--stdio` flag is optional.

4. **Restart Claude Desktop**

After restarting, Claude will have access to the cryptocurrency analysis tools.

## Usage Examples

Once configured, you can ask Claude questions like:

- "What's the current price of Bitcoin?"
- "Analyze Ethereum's technical indicators"
- "Give me a market overview of the top 10 cryptocurrencies"
- "Should I buy or sell Solana based on technical analysis?"
- "What are the trading signals for Cardano?"

Claude will use the MCP tools to fetch real-time data and provide analysis.

## Development

### Running in Stdio Mode (for MCP clients)

```bash
python mcp_server.py --stdio
```

### Running as HTTP Server (for testing)

```bash
python mcp_server.py
```

The server will start on `http://127.0.0.1:8000` with the following endpoints:
- `/sse` - Server-sent events endpoint
- `/messages/` - Message handling endpoint
- `/mcp` - Streamable HTTP endpoint

### Testing Tools

You can test individual tools using Python:

```python
from mcp_server import crypto_api

# Test price data
data = crypto_api.fetch_price_data('bitcoin', 7)
print(data)

# Test analysis
analysis = crypto_api.analyze_cryptocurrency('ethereum', 30)
print(analysis)

# Test market overview
market = crypto_api.get_market_overview(5)
print(market)
```

## Supported Cryptocurrencies

Pre-configured coins:
- bitcoin
- ethereum
- binancecoin
- cardano
- solana
- polkadot
- dogecoin
- avalanche-2
- polygon
- chainlink

**Note:** Any valid CoinGecko coin ID can be used, not just the pre-configured ones.

## Data Sources

- **CoinGecko API**: Historical price data, market cap, volume
- **Technical Analysis**: RSI, MACD, SMA, EMA, Bollinger Bands, and more

## Security Considerations

⚠️ **Important:**
- This tool is for educational purposes only
- The MCP server fetches public market data only
- No API keys or credentials are required for basic functionality
- Trading decisions should not be made solely based on automated signals
- Always do your own research before making investment decisions

## Troubleshooting

### Server won't start

1. Check Python version: `python --version` (must be 3.8+)
2. Verify dependencies: `pip install -r requirements.txt`
3. Check for port conflicts if running HTTP mode

### Claude can't connect

1. Verify the path in `claude_desktop_config.json` is absolute and correct
2. Ensure Python is in your PATH
3. Restart Claude Desktop after configuration changes
4. Check Claude Desktop logs for error messages

### Tools return errors

1. Check internet connectivity (required for CoinGecko API)
2. Verify coin IDs are correct (use `list_supported_coins`)
3. API rate limits may apply - wait a few minutes between requests

## API Rate Limits

The server uses the free CoinGecko API with the following limits:
- 10-50 calls per minute
- Data is cached for 5 minutes to reduce API calls

## Contributing

To add new tools to the MCP server:

1. Add a new function decorated with `@mcp.tool()` in `mcp_server.py`
2. Implement the functionality in `headless_crypto_api.py`
3. Update this documentation with the new tool details

## License

Educational use only. See main README for full disclaimers.

## Support

For issues and questions:
- GitHub Issues: https://github.com/aaakaind/letsgetcrypto
- Check existing documentation in README.md and README_APP.md
