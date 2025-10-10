#!/usr/bin/env python3
"""
Example MCP Client

This script demonstrates how to interact with the Crypto MCP Server
using the JSON-RPC protocol over stdin/stdout.

This is a reference implementation showing how an MCP client would
communicate with the server.
"""

import json
import subprocess
import sys
from typing import Dict, Any


class MCPClient:
    """Simple MCP client for demonstration purposes."""
    
    def __init__(self, server_path: str):
        """Initialize the MCP client."""
        self.request_id = 0
        self.server_process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        if params:
            request["params"] = params
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_line.encode())
        self.server_process.stdin.flush()
        
        # Read response, skipping non-JSON lines (like log messages)
        max_attempts = 10
        for _ in range(max_attempts):
            response_line = self.server_process.stdout.readline().decode().strip()
            if not response_line:
                continue
            try:
                return json.loads(response_line)
            except json.JSONDecodeError:
                # Skip non-JSON lines (probably log messages)
                continue
        
        raise Exception("No valid JSON response received from server")
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session."""
        return self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {}
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return self.send_request("tools/list")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool."""
        if arguments is None:
            arguments = {}
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return self.send_request("resources/list")
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource."""
        return self.send_request("resources/read", {
            "uri": uri
        })
    
    def close(self):
        """Close the client connection."""
        self.server_process.terminate()
        try:
            self.server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server_process.kill()


def main():
    """Demonstrate MCP client usage."""
    print("=" * 60)
    print("Crypto MCP Client Example")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Initializing MCP client...")
    client = MCPClient("../crypto_mcp_server.py")
    
    try:
        # Initialize session
        print("\n2. Initializing MCP session...")
        init_response = client.initialize()
        server_info = init_response['result']['serverInfo']
        print(f"   Connected to: {server_info['name']} v{server_info['version']}")
        
        # List available tools
        print("\n3. Listing available tools...")
        tools_response = client.list_tools()
        tools = tools_response['result']['tools']
        print(f"   Available tools: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Example 1: Get supported coins
        print("\n4. Getting supported cryptocurrencies...")
        response = client.call_tool("get_supported_coins")
        result = json.loads(response['result']['content'][0]['text'])
        print(f"   Supported coins: {', '.join(result['supported_coins'])}")
        
        # Example 2: Get Bitcoin price
        print("\n5. Getting Bitcoin current price...")
        response = client.call_tool("get_crypto_price", {
            "coin_id": "bitcoin"
        })
        result = json.loads(response['result']['content'][0]['text'])
        if 'error' not in result:
            print(f"   Bitcoin Price: ${result['price_usd']:,.2f}")
            print(f"   24h Change: {result['price_change_24h_percent']:.2f}%")
        else:
            print(f"   Error: {result['error']}")
        
        # Example 3: Get market overview
        print("\n6. Getting market overview (top 5)...")
        response = client.call_tool("get_market_overview", {
            "limit": 5
        })
        result = json.loads(response['result']['content'][0]['text'])
        if result.get('market_overview'):
            print("   Top 5 Cryptocurrencies:")
            for i, coin in enumerate(result['market_overview'], 1):
                print(f"   {i}. {coin['symbol']:6s} ${coin['price_usd']:10,.2f} "
                      f"({coin.get('price_change_24h_percent', 0):6.2f}%)")
        
        # Example 4: Read a resource
        print("\n7. Reading server-info resource...")
        response = client.read_resource("crypto://server-info")
        resource_content = json.loads(response['result']['contents'][0]['text'])
        print(f"   Server: {json.dumps(resource_content, indent=6)}")
        
        print("\n" + "=" * 60)
        print("✅ Example completed successfully!")
        print("=" * 60)
        print("\nThis demonstrates how AI assistants can interact with")
        print("the Crypto MCP Server to fetch cryptocurrency data.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print("\n8. Closing connection...")
        client.close()
        print("   ✓ Disconnected")


if __name__ == "__main__":
    main()
