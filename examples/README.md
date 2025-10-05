# LetsGetCrypto Examples

This directory contains example code and usage demonstrations for the LetsGetCrypto tools.

## Available Examples

### mcp_usage_example.py

Demonstrates how to use the MCP (Model Context Protocol) tools programmatically.

**Run the example:**
```bash
python mcp_usage_example.py
```

This example shows:
- How to list supported cryptocurrencies
- How to get price data for a specific coin
- How to get a market overview
- How to generate trading signals
- How to perform comprehensive technical analysis

## Usage with Claude AI

When the MCP server is configured with Claude Desktop, Claude can automatically call these same tools to provide real-time cryptocurrency analysis and market data.

See [../MCP_SERVER.md](../MCP_SERVER.md) for setup instructions.

## Note

The examples require an internet connection to fetch data from the CoinGecko API. If you encounter errors, it may be due to:
- Network connectivity issues
- API rate limiting
- The API being temporarily unavailable

This is normal for examples that depend on external APIs.
