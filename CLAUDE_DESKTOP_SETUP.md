# Claude Desktop MCP Server Setup

This guide explains how to configure the LetsGetCrypto MCP server with Claude Desktop.

## Prerequisites

- Claude Desktop installed on your system
- Python 3.8 or higher installed
- LetsGetCrypto repository cloned locally

## Quick Setup

### 1. Locate Your Claude Desktop Configuration

The configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Copy the Template Configuration

A template configuration file is provided in this repository:

```bash
# View the template
cat claude_desktop_config.json.example

# Option 1: Copy directly to Claude Desktop config location (macOS example)
cp claude_desktop_config.json.example ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Option 2: Create/merge with existing config
cat claude_desktop_config.json.example >> ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 3. Update the Paths

Edit the configuration file and replace `/absolute/path/to/letsgetcrypto/` with the actual path to your installation:

```bash
# Find your installation path
pwd
# Example output: /home/username/projects/letsgetcrypto
```

Update the configuration:
```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/home/username/projects/letsgetcrypto/crypto_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/username/projects/letsgetcrypto",
        "CRYPTO_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 4. Verify the Configuration

Test that the MCP server runs correctly:

```bash
# Navigate to the repository
cd /path/to/letsgetcrypto

# Test the server
python3 crypto_mcp_server.py
```

You should see: "Waiting for requests on stdin..."

Press `Ctrl+C` to stop the test.

### 5. Restart Claude Desktop

Close and reopen Claude Desktop. The crypto tools should now be available.

## Using the MCP Server

Once configured, you can ask Claude to:

- "What's the current price of Bitcoin?"
- "Show me the market overview for the top 10 cryptocurrencies"
- "Analyze Ethereum's price trends over the last 30 days"
- "Get historical price data for Cardano"
- "What cryptocurrencies does the server support?"

Claude will use the MCP server to fetch real-time cryptocurrency data and perform analysis.

## Configuration Options

### Basic Configuration

Minimal setup with just the server path:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/path/to/crypto_mcp_server.py"
      ]
    }
  }
}
```

### Advanced Configuration

With environment variables and custom settings:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/path/to/crypto_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/letsgetcrypto",
        "CRYPTO_API_URL": "http://localhost:8000",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Multiple MCP Servers

If you have other MCP servers configured:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": ["/path/to/crypto_mcp_server.py"]
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other-server.js"]
    }
  }
}
```

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. **Check the configuration file path**: Ensure you edited the correct file for your OS
2. **Verify JSON syntax**: Use a JSON validator to check for syntax errors
3. **Check paths**: Ensure all paths are absolute and point to existing files
4. **Restart Claude Desktop**: Changes require a complete restart

### Python Not Found

If you see "python3: command not found":

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "/usr/bin/python3",  // Use full path to python
      "args": ["/path/to/crypto_mcp_server.py"]
    }
  }
}
```

Find your Python path:
```bash
which python3
```

### Missing Dependencies

If the server fails to start, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Testing the Configuration

Run the test script to verify functionality:

```bash
cd /path/to/letsgetcrypto
python3 test_mcp_server.py
```

## Additional Resources

- **[README_MCP.md](README_MCP.md)**: Complete MCP server documentation
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**: Integration with various clients
- **[CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)**: Configure Anthropic API key (optional)

## Support

For issues or questions:
- Check the [README_MCP.md](README_MCP.md) for detailed server documentation
- Review the [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for client setup
- Run `python3 test_mcp_server.py` to diagnose server issues
