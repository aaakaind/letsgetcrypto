#!/usr/bin/env python3
"""
Test script for the Crypto MCP Server

This script tests the MCP server functionality by sending various requests
and verifying the responses.
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any

def send_request(process: subprocess.Popen, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a JSON-RPC request to the MCP server and get response.
    
    Args:
        process: The server process
        request: JSON-RPC request
        
    Returns:
        JSON-RPC response
    """
    request_line = json.dumps(request) + "\n"
    process.stdin.write(request_line.encode())
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline().decode().strip()
    return json.loads(response_line)


def test_mcp_server():
    """Test the MCP server with various requests."""
    print("=" * 60)
    print("Testing Crypto MCP Server")
    print("=" * 60)
    
    # Start the MCP server
    print("\n1. Starting MCP server...")
    process = subprocess.Popen(
        [sys.executable, "crypto_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    
    # Give server time to start
    time.sleep(1)
    
    try:
        # Test 1: Initialize
        print("\n2. Testing initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            }
        }
        response = send_request(process, init_request)
        print(f"   ✓ Initialize response: {json.dumps(response, indent=2)}")
        
        # Test 2: List tools
        print("\n3. Testing tools/list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = send_request(process, tools_request)
        print(f"   ✓ Found {len(response['result']['tools'])} tools:")
        for tool in response['result']['tools']:
            print(f"     - {tool['name']}: {tool['description']}")
        
        # Test 3: List resources
        print("\n4. Testing resources/list...")
        resources_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list"
        }
        response = send_request(process, resources_request)
        print(f"   ✓ Found {len(response['result']['resources'])} resources:")
        for resource in response['result']['resources']:
            print(f"     - {resource['name']}: {resource['uri']}")
        
        # Test 4: Call get_supported_coins tool
        print("\n5. Testing get_supported_coins tool...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_supported_coins",
                "arguments": {}
            }
        }
        response = send_request(process, call_request)
        result = json.loads(response['result']['content'][0]['text'])
        print(f"   ✓ Supported coins: {result['supported_coins'][:5]}... (showing first 5)")
        print(f"   ✓ Total: {result['count']} coins")
        
        # Test 5: Call get_market_overview tool
        print("\n6. Testing get_market_overview tool...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_market_overview",
                "arguments": {
                    "limit": 5
                }
            }
        }
        response = send_request(process, call_request)
        result = json.loads(response['result']['content'][0]['text'])
        print(f"   ✓ Market overview fetched: {result['total_cryptocurrencies']} coins")
        if result.get('market_overview'):
            for coin in result['market_overview'][:3]:
                print(f"     - {coin['symbol']}: ${coin['price_usd']:.2f} ({coin.get('price_change_24h_percent', 0):.2f}%)")
        
        # Test 6: Call get_crypto_price tool
        print("\n7. Testing get_crypto_price tool (Bitcoin)...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_crypto_price",
                "arguments": {
                    "coin_id": "bitcoin"
                }
            }
        }
        response = send_request(process, call_request)
        result = json.loads(response['result']['content'][0]['text'])
        if 'error' not in result:
            print(f"   ✓ Bitcoin price: ${result['price_usd']:.2f}")
            print(f"   ✓ 24h change: {result['price_change_24h_percent']:.2f}%")
            print(f"   ✓ Volume 24h: ${result['volume_24h_usd']:,.0f}")
        else:
            print(f"   ⚠ Error: {result['error']}")
        
        # Test 7: Read resource
        print("\n8. Testing resources/read...")
        read_request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "resources/read",
            "params": {
                "uri": "crypto://server-info"
            }
        }
        response = send_request(process, read_request)
        resource_content = json.loads(response['result']['contents'][0]['text'])
        print(f"   ✓ Server info: {json.dumps(resource_content, indent=6)}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        print("\n9. Shutting down server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("   ✓ Server stopped")
    
    return True


if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
