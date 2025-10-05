# MCP Server for LetsGetCrypto

## Overview

The LetsGetCrypto MCP (Model Context Protocol) Server enables AI assistants to interact with cryptocurrency market data and trading tools. This allows AI-powered analysis, predictions, and trading recommendations.

## What is MCP?

Model Context Protocol (MCP) is a protocol that allows AI assistants (like Claude, GPT, etc.) to interact with external tools and data sources. The LetsGetCrypto MCP server exposes cryptocurrency data through this protocol.

## Installation

### Prerequisites

1. Python 3.8 or higher
2. MCP package installed:
```bash
pip install mcp
```

3. LetsGetCrypto API running (Django backend):
```bash
# Start the Django server
python manage.py runserver
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the MCP Server

### Standalone Mode

Run the MCP server directly:

```bash
python mcp_server.py
```

### With Custom API URL

Set the API URL via environment variable:

```bash
export CRYPTO_API_URL=http://localhost:8000
python mcp_server.py
```

Or for production/AWS deployment:

```bash
export CRYPTO_API_URL=https://your-loadbalancer-url.amazonaws.com
python mcp_server.py
```

## Configuration

The MCP server can be configured using:

1. **Environment Variables**:
   - `CRYPTO_API_URL`: Base URL for the crypto API (default: `http://localhost:8000`)

2. **Configuration File** (`mcp-config.json`):
   - Update the `env.CRYPTO_API_URL` value
   - Modify tool descriptions if needed

## Available Tools

The MCP server exposes the following tools to AI assistants:

### 1. get_crypto_price

Get current price and market data for a cryptocurrency.

**Parameters:**
- `symbol` (required): Cryptocurrency symbol (e.g., 'bitcoin', 'ethereum')

**Example Response:**
```json
{
  "symbol": "BITCOIN",
  "price_usd": 45000.50,
  "market_cap_usd": 850000000000,
  "volume_24h_usd": 25000000000,
  "price_change_24h_percent": 2.5,
  "timestamp": 1234567890
}
```

### 2. get_crypto_history

Get historical price data for a cryptocurrency.

**Parameters:**
- `symbol` (required): Cryptocurrency symbol
- `days` (optional): Number of days of historical data (1-365, default: 30)

**Example Response:**
```json
{
  "symbol": "BITCOIN",
  "days": 30,
  "data_points": 720,
  "prices": [
    {"timestamp": 1234567890, "price": 45000.50},
    {"timestamp": 1234567900, "price": 45010.20}
  ],
  "timestamp": 1234567890
}
```

### 3. get_market_overview

Get market overview with top cryptocurrencies by market cap.

**Parameters:**
- `limit` (optional): Number of cryptocurrencies to return (1-50, default: 10)

**Example Response:**
```json
{
  "market_overview": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "price_usd": 45000.50,
      "market_cap_usd": 850000000000,
      "volume_24h_usd": 25000000000,
      "price_change_24h_percent": 2.5,
      "market_cap_rank": 1
    }
  ],
  "total_cryptocurrencies": 10,
  "timestamp": 1234567890
}
```

### 4. check_api_health

Check the health status of the cryptocurrency API.

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "version": "1.0.0",
  "components": {
    "database": "ok",
    "external_apis": "ok"
  }
}
```

## Integration with AI Assistants

### Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "letsgetcrypto": {
      "command": "python",
      "args": ["/path/to/letsgetcrypto/mcp_server.py"],
      "env": {
        "CRYPTO_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Other AI Assistants

Follow your AI assistant's MCP integration documentation and use the `mcp-config.json` file as reference.

## Usage Examples

Once integrated with an AI assistant, you can ask questions like:

- "What's the current price of Bitcoin?"
- "Show me the price history of Ethereum for the last 7 days"
- "Give me an overview of the top 10 cryptocurrencies"
- "Is the crypto API healthy?"

The AI assistant will use the MCP server tools to fetch real-time data and provide informed responses.

## Troubleshooting

### MCP Package Not Found

If you see "MCP package not available", install it:
```bash
pip install mcp
```

### API Connection Issues

Ensure the Django API is running:
```bash
python manage.py runserver
```

Check the API health:
```bash
curl http://localhost:8000/api/health/
```

### Environment Variables

Verify your environment variables:
```bash
echo $CRYPTO_API_URL
```

## Production Deployment

For production use with AWS:

1. Deploy the Django API using the AWS deployment guide
2. Update `CRYPTO_API_URL` to point to your load balancer
3. Run the MCP server on a server that AI assistants can access

```bash
export CRYPTO_API_URL=https://your-loadbalancer-url.amazonaws.com
python mcp_server.py
```

## Security Considerations

- **API Access**: Ensure the crypto API is properly secured with authentication if needed
- **Rate Limiting**: Consider implementing rate limiting for production use
- **Environment Variables**: Never commit sensitive URLs or credentials to version control
- **Network Security**: Use HTTPS for production deployments

## Support

For issues or questions:
- Check the main [README.md](README.md) for general information
- Review the [AWS Deployment Guide](AWS_DEPLOYMENT.md) for production setup
- Ensure all dependencies are installed from [requirements.txt](requirements.txt)

---

**Note**: The MCP server requires the Django API backend to be running. It acts as a bridge between AI assistants and the cryptocurrency data API.
