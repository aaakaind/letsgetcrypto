#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for LetsGetCrypto

This server exposes cryptocurrency data and trading tools to AI assistants
through the Model Context Protocol, enabling AI-powered trading analysis.
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import os

# Check if mcp package is available
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP package not available. Install with: pip install mcp")

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class CryptoAPIConfig:
    """Configuration for cryptocurrency API"""
    base_url: str = os.environ.get('CRYPTO_API_URL', 'http://localhost:8000')
    timeout: int = 30


class CryptoMCPServer:
    """MCP Server for cryptocurrency data and trading tools"""
    
    def __init__(self, config: Optional[CryptoAPIConfig] = None):
        self.config = config or CryptoAPIConfig()
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not installed. Install with: pip install mcp")
        self.server = Server("letsgetcrypto")
        self.setup_tools()
    
    def setup_tools(self):
        """Register all available tools with the MCP server"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available cryptocurrency tools"""
            return [
                Tool(
                    name="get_crypto_price",
                    description="Get current price and market data for a cryptocurrency",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Cryptocurrency symbol (e.g., 'bitcoin', 'ethereum')"
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="get_crypto_history",
                    description="Get historical price data for a cryptocurrency",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Cryptocurrency symbol (e.g., 'bitcoin', 'ethereum')"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days of historical data (1-365)",
                                "default": 30
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="get_market_overview",
                    description="Get market overview with top cryptocurrencies by market cap",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of cryptocurrencies to return (1-50)",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="check_api_health",
                    description="Check the health status of the cryptocurrency API",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a tool and return results"""
            try:
                if name == "get_crypto_price":
                    result = await self._get_crypto_price(arguments["symbol"])
                elif name == "get_crypto_history":
                    result = await self._get_crypto_history(
                        arguments["symbol"],
                        arguments.get("days", 30)
                    )
                elif name == "get_market_overview":
                    result = await self._get_market_overview(
                        arguments.get("limit", 10)
                    )
                elif name == "check_api_health":
                    result = await self._check_api_health()
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """Get current cryptocurrency price"""
        url = f"{self.config.base_url}/api/price/{symbol}/"
        response = requests.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()
    
    async def _get_crypto_history(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """Get historical cryptocurrency data"""
        url = f"{self.config.base_url}/api/history/{symbol}/"
        params = {"days": min(days, 365)}
        response = requests.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()
    
    async def _get_market_overview(self, limit: int = 10) -> Dict[str, Any]:
        """Get market overview"""
        url = f"{self.config.base_url}/api/market/"
        params = {"limit": min(limit, 50)}
        response = requests.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API health"""
        url = f"{self.config.base_url}/api/health/"
        response = requests.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP server"""
    if not MCP_AVAILABLE:
        print("Error: MCP package not installed.")
        print("Install with: pip install mcp")
        return 1
    
    config = CryptoAPIConfig()
    server = CryptoMCPServer(config)
    
    logger.info(f"Starting LetsGetCrypto MCP Server")
    logger.info(f"API Base URL: {config.base_url}")
    
    await server.run()
    return 0


if __name__ == "__main__":
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        print("Error: MCP package not installed.")
        print("Install with: pip install mcp")
        exit(1)
