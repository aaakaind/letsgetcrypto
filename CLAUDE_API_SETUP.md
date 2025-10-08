# Anthropic Claude API Key Setup

This guide explains how to configure your Anthropic Claude API key for use with the LetsGetCrypto MCP server.

## Step 1: Get Your API Key

1. Visit the [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key or copy an existing one

## Step 2: Configure the API Key

### Option A: Using Environment Variables (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API key:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...your-actual-key-here
   ```

3. The `.env` file is already in `.gitignore` to prevent accidentally committing your key.

### Option B: Using Claude Desktop Configuration

For Claude Desktop integration with the MCP server, you can also set the API key in the configuration file:

#### macOS
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Windows
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

#### Linux
Edit: `~/.config/Claude/claude_desktop_config.json`

#### Configuration with API Key:

```json
{
  "mcpServers": {
    "crypto-data": {
      "command": "python3",
      "args": [
        "/full/path/to/letsgetcrypto/crypto_mcp_server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-...your-actual-key-here",
        "CRYPTO_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Important**: Replace `/full/path/to/letsgetcrypto/` with the actual path to your installation.

## Step 3: Verify Configuration

Test that your API key is properly configured:

```bash
# Load environment variables
source .env  # On Linux/macOS
# or
set -a; source .env; set +a  # Alternative for Linux/macOS

# Verify the key is loaded
echo $ANTHROPIC_API_KEY
```

## Step 4: Using with MCP Server

Once configured, restart your MCP client (Claude Desktop, VS Code, etc.) to apply the changes.

## Security Best Practices

1. **Never commit your API key** to version control
   - The `.env` file is already in `.gitignore`
   - Always use `.env.example` for templates

2. **Rotate keys regularly** if you suspect they've been compromised

3. **Use separate keys** for development and production

4. **Set usage limits** in the Anthropic Console to prevent unexpected charges

5. **Monitor usage** regularly through the Anthropic Console

## Troubleshooting

### API Key Not Found

If you get an error about missing API key:
- Verify the `.env` file exists and contains the key
- Check that the key format is correct (starts with `sk-ant-api03-`)
- Ensure you've restarted your MCP client after configuring

### Invalid API Key

If you get authentication errors:
- Verify the API key is active in the Anthropic Console
- Check for any typos when copying the key
- Ensure the key hasn't been revoked or expired

### Permission Denied

If you get permission errors:
- Check that your account has sufficient credits
- Verify the API key has the necessary permissions

## Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [MCP Server Documentation](MCP_SERVER.md)
- [Integration Guide](INTEGRATION_GUIDE.md)

## Support

For issues specific to:
- **API Key Management**: Contact [Anthropic Support](https://support.anthropic.com/)
- **MCP Server Integration**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **General Setup**: See [README.md](README.md)
