# MCP Server Examples

This directory contains example scripts demonstrating how to interact with the Crypto MCP Server.

## Examples

### 1. MCP Client Example (`mcp_client_example.py`)

A reference implementation of an MCP client that demonstrates:
- Initializing an MCP session
- Listing available tools and resources
- Calling tools (get_supported_coins, get_crypto_price, get_market_overview)
- Reading resources

**Run it:**
```bash
cd examples
python3 mcp_client_example.py
```

This example shows how AI assistants and other MCP clients can interact with the Crypto MCP Server to fetch real-time cryptocurrency data.

## What You'll See

When you run the examples, you'll see:
1. Connection to the MCP server
2. List of available tools (5 crypto data tools)
3. Supported cryptocurrency IDs
4. Current Bitcoin price and 24h change
5. Market overview with top 5 cryptocurrencies
6. Server information from resources

## Requirements

- Python 3.8+
- Dependencies from main project (pandas, numpy, requests, etc.)
- Internet connection (for accessing CoinGecko API)

## Creating Your Own MCP Client

The example client provides a basic template. To create your own:

1. Start the server process
2. Send JSON-RPC requests over stdin
3. Read JSON-RPC responses from stdout
4. Follow the MCP protocol specification

See `mcp_client_example.py` for a complete implementation.

## Integration with AI Assistants

Instead of using a custom client, you can configure AI assistants like Claude Desktop to use the MCP server directly. See the main [README_MCP.md](../README_MCP.md) for configuration instructions.
