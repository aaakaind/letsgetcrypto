# Cryptocurrency MCP Server

This directory contains a Model Context Protocol (MCP) server that exposes cryptocurrency data and analysis capabilities to AI assistants.

## Overview

The MCP server provides a standardized interface for AI assistants to access:
- Real-time cryptocurrency prices
- Historical price data
- Market overview and rankings
- Technical analysis and trading signals
- Supported cryptocurrency information

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables secure, controlled interactions between AI assistants and external data sources. This crypto MCP server allows AI assistants to fetch and analyze cryptocurrency data programmatically.

## Features

### Tools (Callable Functions)

1. **get_crypto_price** - Get current price and 24h data for a cryptocurrency
   - Parameters: `coin_id` (e.g., 'bitcoin', 'ethereum')
   - Returns: Current price, volume, market cap, 24h change

2. **get_crypto_history** - Get historical price data
   - Parameters: `coin_id`, `days` (default: 30, max: 365)
   - Returns: Time series of prices, volumes, market caps

3. **get_market_overview** - Get top cryptocurrencies by market cap
   - Parameters: `limit` (default: 10, max: 50)
   - Returns: List of top coins with prices and changes

4. **analyze_cryptocurrency** - Comprehensive technical analysis
   - Parameters: `coin_id`, `days` (default: 30)
   - Returns: Technical indicators, signals, recommendations

5. **get_supported_coins** - List all supported cryptocurrency IDs
   - Parameters: None
   - Returns: List of supported coin IDs

### Resources (Readable Data)

1. **crypto://supported-coins** - JSON list of supported cryptocurrencies
2. **crypto://server-info** - Server version and information

## Installation

The MCP server uses the existing project dependencies. Ensure you have installed:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

The MCP server runs in stdio mode, communicating via JSON-RPC over stdin/stdout:

```bash
python3 crypto_mcp_server.py
```

### Testing the Server

Run the test script to verify functionality:

```bash
python3 test_mcp_server.py
```

### Configuring for MCP Clients

Add the server to your MCP client configuration (e.g., Claude Desktop, VS Code):

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/path/to/crypto_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/letsgetcrypto"
      }
    }
  }
}
```

#### For Claude Desktop

On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Example configuration:
```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/home/runner/work/letsgetcrypto/letsgetcrypto/crypto_mcp_server.py"
      ]
    }
  }
}
```

## Example Usage with AI Assistants

Once configured, you can ask AI assistants to:

- "What's the current price of Bitcoin?"
- "Show me the market overview for the top 10 cryptocurrencies"
- "Analyze Ethereum's price trends over the last 30 days"
- "Get historical price data for Cardano"
- "What cryptocurrencies does the server support?"

The AI assistant will use the MCP tools to fetch and analyze the data.

## Architecture

```
crypto_mcp_server.py
├── CryptoMCPServer (Main server class)
│   ├── Tool handlers (get_crypto_price, etc.)
│   ├── Resource handlers (server-info, supported-coins)
│   └── MCP protocol handlers (initialize, tools/list, etc.)
└── HeadlessCryptoAPI (Data provider)
    └── CoinGecko API integration
```

## Data Sources

- **CoinGecko API**: Primary source for cryptocurrency data
- **Caching**: 5-minute cache to reduce API calls
- **Rate Limiting**: Respects API rate limits

## Error Handling

The server handles errors gracefully:
- Invalid coin IDs return error messages
- API failures are logged and reported
- Timeout protection for long-running requests

## Development

### Adding New Tools

1. Add tool definition to `get_tools()` method
2. Implement handler method (e.g., `_my_new_tool()`)
3. Add routing in `call_tool()` method
4. Update tests in `test_mcp_server.py`

### Adding New Resources

1. Add resource definition to `get_resources()` method
2. Implement handler in `read_resource()` method
3. Update documentation

## Logging

Logs are written to stderr to avoid interfering with the JSON-RPC protocol on stdout.

```python
# View logs when running
python3 crypto_mcp_server.py 2> server.log
```

## Security Considerations

- The server only provides read-only access to public cryptocurrency data
- No trading or wallet operations are exposed
- No API keys or credentials are required
- Rate limiting is handled automatically

## Troubleshooting

### Server won't start
- Check Python version (3.8+ required)
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check PYTHONPATH includes the project directory

### Tools return errors
- Verify internet connectivity
- Check CoinGecko API status
- Ensure coin IDs are valid (use `get_supported_coins`)

### Slow responses
- CoinGecko API may be rate-limited
- Try reducing request frequency
- Cache is used to speed up repeated requests

## Contributing

When adding new features:
1. Follow existing code patterns
2. Add comprehensive error handling
3. Update tool/resource lists
4. Add tests to verify functionality
5. Update this documentation

## License

Educational use only. See main project license for details.

## Support

For issues or questions:
- Check the logs for error messages
- Verify API connectivity
- Test with the included test script
- Review the main project documentation

---

**Note**: This is an educational tool. Cryptocurrency data and analysis should not be used as the sole basis for trading decisions. Always conduct your own research and consult with financial advisors.
