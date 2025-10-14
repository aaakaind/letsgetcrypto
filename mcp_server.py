#!/usr/bin/env python3
"""
Claude MCP Server for LetsGetCrypto
Exposes cryptocurrency analysis tools to Claude AI via Model Context Protocol
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import FastMCP
from headless_crypto_api import HeadlessCryptoAPI

# Server configuration constants
SERVER_NAME = "letsgetcrypto"
SERVER_INSTRUCTIONS = "A cryptocurrency trading and analysis tool that provides real-time market data, technical analysis, and trading signals."
SERVER_WEBSITE_URL = "https://github.com/aaakaind/letsgetcrypto"

# Initialize FastMCP server
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=SERVER_INSTRUCTIONS,
    website_url=SERVER_WEBSITE_URL
)

# Initialize the crypto API
crypto_api = HeadlessCryptoAPI()


@mcp.tool()
def get_crypto_price(coin_id: str = "bitcoin", days: int = 30) -> str:
    """
    Get historical price data for a cryptocurrency.
    
    Args:
        coin_id: The CoinGecko ID of the cryptocurrency (e.g., 'bitcoin', 'ethereum', 'cardano')
        days: Number of days of historical data to fetch (default: 30)
    
    Returns:
        JSON string with price data including latest price, 24h change, and historical data summary
    """
    try:
        df = crypto_api.fetch_price_data(coin_id, days)
        if df is None or df.empty:
            return json.dumps({
                "error": f"Failed to fetch data for {coin_id}",
                "status": "error"
            })
        
        latest = df.iloc[-1]
        first = df.iloc[0]
        price_change = ((latest['price'] - first['price']) / first['price']) * 100
        
        result = {
            "coin": coin_id,
            "current_price": float(latest['price']),
            "price_change_percent": float(price_change),
            "days": days,
            "data_points": len(df),
            "volume_24h": float(latest['volume']),
            "market_cap": float(latest['market_cap']),
            "high": float(df['price'].max()),
            "low": float(df['price'].min()),
            "average": float(df['price'].mean()),
            "status": "success"
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })


@mcp.tool()
def analyze_cryptocurrency(coin_id: str = "bitcoin", days: int = 30) -> str:
    """
    Perform comprehensive technical analysis on a cryptocurrency.
    
    Args:
        coin_id: The CoinGecko ID of the cryptocurrency (e.g., 'bitcoin', 'ethereum', 'solana')
        days: Number of days of historical data to analyze (default: 30)
    
    Returns:
        JSON string with technical analysis including signals, indicators, and recommendations
    """
    try:
        analysis = crypto_api.analyze_cryptocurrency(coin_id, days)
        
        if analysis is None or 'error' in analysis:
            return json.dumps({
                "error": analysis.get('error', 'Analysis failed') if analysis else 'Analysis failed',
                "status": "error"
            })
        
        return json.dumps(analysis, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })


@mcp.tool()
def get_market_overview(limit: int = 10) -> str:
    """
    Get market overview with top cryptocurrencies by market cap.
    
    Args:
        limit: Number of top cryptocurrencies to fetch (default: 10, max: 50)
    
    Returns:
        JSON string with market overview data for top cryptocurrencies
    """
    try:
        # Ensure limit is within bounds
        limit = min(max(1, limit), 50)
        
        market_data = crypto_api.get_market_overview(limit)
        
        if not market_data:
            return json.dumps({
                "error": "Failed to fetch market overview",
                "status": "error"
            })
        
        result = {
            "total_coins": len(market_data),
            "limit": limit,
            "cryptocurrencies": market_data,
            "status": "success"
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })


@mcp.tool()
def get_trading_signals(coin_id: str = "bitcoin", days: int = 30) -> str:
    """
    Generate trading signals based on technical analysis.
    
    Args:
        coin_id: The CoinGecko ID of the cryptocurrency (e.g., 'bitcoin', 'ethereum', 'dogecoin')
        days: Number of days of historical data to analyze (default: 30)
    
    Returns:
        JSON string with trading signals (BUY/SELL/HOLD), confidence levels, and reasons
    """
    try:
        df = crypto_api.fetch_price_data(coin_id, days)
        if df is None or df.empty:
            return json.dumps({
                "error": f"Failed to fetch data for {coin_id}",
                "status": "error"
            })
        
        df = crypto_api.calculate_technical_indicators(df)
        signals = crypto_api.generate_signals(df)
        
        if signals is None or 'error' in signals:
            return json.dumps({
                "error": signals.get('error', 'Signal generation failed') if signals else 'Signal generation failed',
                "status": "error"
            })
        
        result = {
            "coin": coin_id,
            "signal": signals.get('signal', 'HOLD'),
            "confidence": signals.get('confidence', 0.0),
            "recommendation": signals.get('recommendation', 'HOLD'),
            "reasons": signals.get('reasons', []),
            "price": signals.get('price', 0.0),
            "status": "success"
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })


@mcp.tool()
def list_supported_coins() -> str:
    """
    List all supported cryptocurrency IDs.
    
    Returns:
        JSON string with list of supported cryptocurrency IDs
    """
    try:
        result = {
            "supported_coins": crypto_api.supported_coins,
            "total": len(crypto_api.supported_coins),
            "note": "These are CoinGecko IDs. You can also use any valid CoinGecko coin ID.",
            "status": "success"
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })


def main():
    """
    Run the MCP server
    """
    import sys
    
    # Check if running in stdio mode (for MCP client integration) or HTTP mode
    if "--http" in sys.argv:
        # Run as HTTP server for testing
        print("🚀 Starting LetsGetCrypto MCP Server (HTTP)")
        print("=" * 50)
        print("Available tools:")
        print("  - get_crypto_price")
        print("  - analyze_cryptocurrency")
        print("  - get_market_overview")
        print("  - get_trading_signals")
        print("  - list_supported_coins")
        print("=" * 50)
        print("Server running on http://127.0.0.1:8000")
        mcp.run(transport="http")
    else:
        # Run in stdio mode for MCP client (default)
        print("🚀 Starting LetsGetCrypto MCP Server (STDIO)", file=sys.stderr)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
