# MCP Server Integration Guide

This guide explains how to integrate the Crypto MCP Server with various AI assistants and applications.

## Quick Start

### 1. Verify Installation

```bash
# Install dependencies
pip install pandas numpy requests retrying ta

# Test the server
python3 crypto_mcp_server.py
```

Press Ctrl+C after seeing the "Waiting for requests on stdin..." message.

### 2. Configure Your MCP Client

The server works with any MCP-compatible client. Here are configurations for popular options:

## Claude Desktop

### macOS
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux
Edit: `~/.config/Claude/claude_desktop_config.json`

### Configuration:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/full/path/to/letsgetcrypto/crypto_mcp_server.py"
      ]
    }
  }
}
```

**Important**: Replace `/full/path/to/letsgetcrypto/` with the actual path to your installation.

After saving, restart Claude Desktop. The crypto tools will appear in the tools menu.

## VS Code with Continue Extension

Edit your Continue configuration (`.continue/config.json`):

```json
{
  "mcpServers": [
    {
      "name": "crypto-data",
      "command": "python3",
      "args": [
        "/full/path/to/letsgetcrypto/crypto_mcp_server.py"
      ]
    }
  ]
}
```

## Custom MCP Client

See `examples/mcp_client_example.py` for a reference implementation.

```python
from examples.mcp_client_example import MCPClient

# Create client
client = MCPClient("/path/to/crypto_mcp_server.py")

# Initialize
client.initialize()

# Call a tool
response = client.call_tool("get_crypto_price", {
    "coin_id": "bitcoin"
})

# Clean up
client.close()
```

## Testing Your Integration

### Test 1: List Available Tools

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | \
  python3 crypto_mcp_server.py 2>/dev/null | \
  jq '.result.tools[].name'
```

Expected output:
```
"get_crypto_price"
"get_crypto_history"
"get_market_overview"
"analyze_cryptocurrency"
"get_supported_coins"
```

### Test 2: Get Supported Coins

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_supported_coins", "arguments": {}}}' | \
  python3 crypto_mcp_server.py 2>/dev/null | \
  jq -r '.result.content[0].text | fromjson | .supported_coins[]'
```

### Test 3: Run Example Client

```bash
cd examples
python3 mcp_client_example.py
```

## Using with AI Assistants

Once configured, you can interact naturally:

### Example Conversations

**User**: "What's the current price of Bitcoin?"

*AI uses `get_crypto_price` tool with `coin_id: "bitcoin"`*

**AI**: "Bitcoin is currently trading at $X,XXX.XX USD, with a 24-hour change of +X.XX%."

---

**User**: "Show me the top 5 cryptocurrencies by market cap"

*AI uses `get_market_overview` tool with `limit: 5`*

**AI**: "Here are the top 5 cryptocurrencies by market cap:
1. Bitcoin (BTC): $XX,XXX
2. Ethereum (ETH): $X,XXX
..."

---

**User**: "Analyze Ethereum's price trend over the last week"

*AI uses `analyze_cryptocurrency` tool with `coin_id: "ethereum", days: 7`*

**AI**: "Based on the technical analysis of Ethereum over the past 7 days..."

## Troubleshooting

### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Install dependencies
```bash
pip install pandas numpy requests retrying ta
```

### No Response from Tools

**Problem**: Server hangs or doesn't respond

**Solution**: Check that:
1. Python 3.8+ is installed: `python3 --version`
2. Internet connection is available (for CoinGecko API)
3. No firewall blocking outbound HTTPS

### Invalid Coin IDs

**Problem**: "Could not fetch data for [coin]"

**Solution**: Use `get_supported_coins` to see valid IDs:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_supported_coins", "arguments": {}}}' | \
  python3 crypto_mcp_server.py 2>/dev/null
```

Supported coins include:
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

### Rate Limiting

**Problem**: API errors or empty responses

**Solution**: The server caches data for 5 minutes. If you're hitting rate limits:
1. Wait a few minutes between requests
2. Use smaller `limit` values in `get_market_overview`
3. Request shorter time periods in `get_crypto_history`

## Advanced Configuration

### Custom Python Path

If your Python is not at `/usr/bin/python3`:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "/usr/local/bin/python3",
      "args": ["/path/to/crypto_mcp_server.py"]
    }
  }
}
```

### Environment Variables

Add custom environment variables:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": ["/path/to/crypto_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/letsgetcrypto",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Using the Launcher Script

For easier configuration, use the included launcher:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "/path/to/letsgetcrypto/run_mcp_server.sh"
    }
  }
}
```

## Security Considerations

The MCP server:
- ✅ Only provides read-only access to public data
- ✅ Does not require API keys or credentials
- ✅ Does not execute trades or manage wallets
- ✅ Runs locally on your machine
- ✅ Only communicates with public CoinGecko API

**Note**: The server does not have access to:
- Your private keys or wallets
- Your exchange accounts
- Your personal financial data

## Support

If you encounter issues:
1. Check the logs: Run server with `2>&1 | tee server.log`
2. Verify dependencies: `pip list | grep -E "(pandas|numpy|requests)"`
3. Test basic functionality: `python3 test_mcp_server.py`
4. Review the [main documentation](README_MCP.md)

## Next Steps

- Read the [full MCP documentation](README_MCP.md)
- Explore [example implementations](examples/)
- Review [API documentation](README_APP.md)
- Check out the [main project README](README.md)

---

**Educational Use Only**: This tool is for learning and research purposes. Cryptocurrency trading involves substantial risk. Always conduct your own research and consult financial advisors before making investment decisions.
