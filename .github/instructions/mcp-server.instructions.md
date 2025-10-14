---
applyTo:
  - "crypto_mcp_server.py"
  - "mcp_server.py"
  - "examples/mcp_client_example.py"
  - "test_mcp_server.py"
---

# MCP Server Development Instructions

## Model Context Protocol Guidelines

### Tool Definition
- Each tool must have:
  - Unique name (lowercase with underscores)
  - Clear description explaining what it does
  - JSON schema defining input parameters
  - Proper return value specification
- Use descriptive names: `get_crypto_price`, `predict_price_trend`

### Input Validation
- Validate all tool inputs before processing
- Use JSON schema `required` field for mandatory parameters
- Provide default values for optional parameters
- Return clear error messages for invalid inputs

### Error Handling
- Catch and handle all exceptions within tool handlers
- Return structured error responses:
  ```python
  {
    "error": "Error type",
    "message": "Detailed error message",
    "details": {...}
  }
  ```
- Log errors for debugging
- Never let exceptions crash the MCP server

### Response Format
- Return consistent JSON structure
- Include relevant metadata (timestamp, source)
- Format numbers appropriately (2 decimal places for prices)
- Use clear field names (e.g., `current_price`, not just `price`)

### Protocol Compliance
- Support both stdio and SSE transport modes
- Implement proper initialize/shutdown lifecycle
- Handle ping/pong for connection health
- Follow MCP specification exactly

### Tool Categories
Organize tools by function:
- **Market Data**: Price fetching, historical data
- **Analysis**: Technical indicators, predictions
- **Trading**: Order execution, portfolio management
- **Information**: News, sentiment, market status

### Integration Testing
- Test each tool individually
- Verify input validation works correctly
- Test error scenarios
- Ensure proper JSON response format
- Test with actual MCP clients (Claude Desktop, VS Code)

### Documentation
- Document each tool with usage examples
- Include example requests and responses
- Explain parameter options clearly
- Note any API rate limits or restrictions

## Claude Desktop Integration

### Configuration
- Tools must be accessible via CLI invocation
- Use absolute paths in configuration
- Set proper environment variables (PYTHONPATH)
- Test configuration before recommending to users

### User Experience
- Provide clear, conversational responses
- Format data in human-readable way
- Include context (e.g., "Bitcoin is currently...")
- Explain technical terms when appropriate
