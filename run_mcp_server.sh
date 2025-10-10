#!/bin/bash
# Launcher script for Crypto MCP Server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to include the project directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the MCP server
exec python3 "$SCRIPT_DIR/crypto_mcp_server.py" "$@"
