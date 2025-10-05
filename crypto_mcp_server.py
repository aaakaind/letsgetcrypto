#!/usr/bin/env python3
"""
Cryptocurrency Data MCP Server

This MCP (Model Context Protocol) server exposes cryptocurrency data
as tools and resources for AI assistants to use.

The server provides:
- Real-time cryptocurrency prices
- Historical price data
- Market overview with top cryptocurrencies
- Technical analysis and trading signals
- Cryptocurrency analysis with indicators

Based on the existing HeadlessCryptoAPI implementation.
"""

import sys
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import the existing crypto API
from headless_crypto_api import HeadlessCryptoAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


class CryptoMCPServer:
    """
    MCP Server for Cryptocurrency Data
    
    Implements the Model Context Protocol (MCP) to expose crypto data
    as tools that can be called by AI assistants.
    """
    
    def __init__(self):
        self.crypto_api = HeadlessCryptoAPI()
        self.server_info = {
            "name": "crypto-data-server",
            "version": "1.0.0",
            "description": "Cryptocurrency data and analysis server"
        }
        logger.info(f"Initialized {self.server_info['name']} v{self.server_info['version']}")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return list of available tools that the MCP server provides.
        
        Returns:
            List of tool definitions with name, description, and input schema
        """
        return [
            {
                "name": "get_crypto_price",
                "description": "Get current price and 24h data for a cryptocurrency",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "Cryptocurrency ID (e.g., 'bitcoin', 'ethereum')"
                        }
                    },
                    "required": ["coin_id"]
                }
            },
            {
                "name": "get_crypto_history",
                "description": "Get historical price data for a cryptocurrency",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "Cryptocurrency ID (e.g., 'bitcoin', 'ethereum')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of historical data (default: 30, max: 365)",
                            "default": 30
                        }
                    },
                    "required": ["coin_id"]
                }
            },
            {
                "name": "get_market_overview",
                "description": "Get market overview with top cryptocurrencies by market cap",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of cryptocurrencies to return (default: 10, max: 50)",
                            "default": 10
                        }
                    }
                }
            },
            {
                "name": "analyze_cryptocurrency",
                "description": "Perform comprehensive technical analysis on a cryptocurrency",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "Cryptocurrency ID (e.g., 'bitcoin', 'ethereum')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of data to analyze (default: 30)",
                            "default": 30
                        }
                    },
                    "required": ["coin_id"]
                }
            },
            {
                "name": "get_supported_coins",
                "description": "Get list of supported cryptocurrency IDs",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """
        Return list of available resources.
        
        Resources are static or dynamic data that can be read.
        """
        return [
            {
                "uri": "crypto://supported-coins",
                "name": "Supported Cryptocurrencies",
                "description": "List of supported cryptocurrency IDs",
                "mimeType": "application/json"
            },
            {
                "uri": "crypto://server-info",
                "name": "Server Information",
                "description": "Information about the crypto MCP server",
                "mimeType": "application/json"
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        try:
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            if tool_name == "get_crypto_price":
                return self._get_crypto_price(arguments)
            elif tool_name == "get_crypto_history":
                return self._get_crypto_history(arguments)
            elif tool_name == "get_market_overview":
                return self._get_market_overview(arguments)
            elif tool_name == "analyze_cryptocurrency":
                return self._analyze_cryptocurrency(arguments)
            elif tool_name == "get_supported_coins":
                return self._get_supported_coins()
            else:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": [t["name"] for t in self.get_tools()]
                }
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {
                "error": str(e),
                "tool": tool_name
            }
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        try:
            logger.info(f"Reading resource: {uri}")
            
            if uri == "crypto://supported-coins":
                return {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({
                        "supported_coins": self.crypto_api.supported_coins,
                        "count": len(self.crypto_api.supported_coins)
                    }, indent=2)
                }
            elif uri == "crypto://server-info":
                return {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(self.server_info, indent=2)
                }
            else:
                return {
                    "error": f"Unknown resource: {uri}",
                    "available_resources": [r["uri"] for r in self.get_resources()]
                }
                
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
            return {
                "error": str(e),
                "uri": uri
            }
    
    # Tool implementations
    
    def _get_crypto_price(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current price for a cryptocurrency."""
        coin_id = args.get("coin_id")
        if not coin_id:
            return {"error": "coin_id is required"}
        
        # Fetch price data (1 day to get latest)
        df = self.crypto_api.fetch_price_data(coin_id, days=1)
        if df is None:
            return {"error": f"Could not fetch data for {coin_id}"}
        
        latest_price = df['price'].iloc[-1]
        latest_volume = df['volume'].iloc[-1]
        latest_market_cap = df['market_cap'].iloc[-1]
        
        # Calculate 24h change if we have enough data
        price_change_24h = 0.0
        if len(df) > 1:
            price_change_24h = (latest_price - df['price'].iloc[0]) / df['price'].iloc[0] * 100
        
        return {
            "coin_id": coin_id,
            "price_usd": latest_price,
            "volume_24h_usd": latest_volume,
            "market_cap_usd": latest_market_cap,
            "price_change_24h_percent": price_change_24h,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_crypto_history(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical price data."""
        coin_id = args.get("coin_id")
        days = args.get("days", 30)
        
        if not coin_id:
            return {"error": "coin_id is required"}
        
        # Limit days to 365
        days = min(days, 365)
        
        df = self.crypto_api.fetch_price_data(coin_id, days)
        if df is None:
            return {"error": f"Could not fetch data for {coin_id}"}
        
        # Convert DataFrame to list of price points
        prices = []
        for idx, row in df.iterrows():
            prices.append({
                "timestamp": idx.isoformat(),
                "price": float(row['price']),
                "volume": float(row['volume']),
                "market_cap": float(row['market_cap'])
            })
        
        return {
            "coin_id": coin_id,
            "days": days,
            "data_points": len(prices),
            "prices": prices,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_market_overview(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get market overview."""
        limit = args.get("limit", 10)
        limit = min(limit, 50)  # Max 50
        
        market_data = self.crypto_api.get_market_overview(limit)
        
        return {
            "market_overview": market_data,
            "total_cryptocurrencies": len(market_data),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_cryptocurrency(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis."""
        coin_id = args.get("coin_id")
        days = args.get("days", 30)
        
        if not coin_id:
            return {"error": "coin_id is required"}
        
        return self.crypto_api.analyze_cryptocurrency(coin_id, days)
    
    def _get_supported_coins(self) -> Dict[str, Any]:
        """Get list of supported coins."""
        return {
            "supported_coins": self.crypto_api.supported_coins,
            "count": len(self.crypto_api.supported_coins),
            "timestamp": datetime.now().isoformat()
        }
    
    # MCP Protocol handlers
    
    def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": self.server_info
        }
    
    def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": self.get_tools()
        }
    
    def handle_list_resources(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {
            "resources": self.get_resources()
        }
    
    def handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        result = self.call_tool(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    def handle_read_resource(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request."""
        params = request.get("params", {})
        uri = params.get("uri")
        
        result = self.read_resource(uri)
        
        if "error" in result:
            return result
        
        return {
            "contents": [result]
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming MCP request.
        
        Args:
            request: MCP request object
            
        Returns:
            MCP response object
        """
        method = request.get("method")
        request_id = request.get("id")
        
        logger.info(f"Handling request: method={method}, id={request_id}")
        
        response = {"jsonrpc": "2.0", "id": request_id}
        
        try:
            if method == "initialize":
                response["result"] = self.handle_initialize(request)
            elif method == "tools/list":
                response["result"] = self.handle_list_tools(request)
            elif method == "resources/list":
                response["result"] = self.handle_list_resources(request)
            elif method == "tools/call":
                response["result"] = self.handle_call_tool(request)
            elif method == "resources/read":
                response["result"] = self.handle_read_resource(request)
            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            response["error"] = {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        
        return response


def run_stdio_server():
    """
    Run the MCP server using stdio transport.
    
    The server reads JSON-RPC requests from stdin and writes responses to stdout.
    """
    server = CryptoMCPServer()
    logger.info("Starting Crypto MCP Server in stdio mode")
    logger.info("Waiting for requests on stdin...")
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Cryptocurrency Data MCP Server")
    logger.info("=" * 60)
    
    # Run the stdio server
    run_stdio_server()


if __name__ == "__main__":
    main()
