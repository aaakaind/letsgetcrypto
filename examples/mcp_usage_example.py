#!/usr/bin/env python3
"""
Example usage of the LetsGetCrypto MCP tools
This demonstrates how the tools can be called programmatically
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import (
    list_supported_coins,
    get_crypto_price,
    get_market_overview,
    get_trading_signals,
    analyze_cryptocurrency
)
import json


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def example_list_coins():
    """Example: List supported cryptocurrencies"""
    print_section("Example 1: List Supported Coins")
    
    result = json.loads(list_supported_coins())
    print(f"Total supported coins: {result['total']}")
    print("\nSupported coins:")
    for coin in result['supported_coins']:
        print(f"  • {coin}")
    print(f"\nNote: {result['note']}")


def example_get_price():
    """Example: Get Bitcoin price"""
    print_section("Example 2: Get Bitcoin Price (7 days)")
    
    result = json.loads(get_crypto_price('bitcoin', 7))
    
    if result['status'] == 'success':
        print(f"Coin: {result['coin']}")
        print(f"Current Price: ${result['current_price']:,.2f}")
        print(f"Price Change (7d): {result['price_change_percent']:.2f}%")
        print(f"24h Volume: ${result['volume_24h']:,.0f}")
        print(f"Market Cap: ${result['market_cap']:,.0f}")
        print(f"High (7d): ${result['high']:,.2f}")
        print(f"Low (7d): ${result['low']:,.2f}")
        print(f"Average (7d): ${result['average']:,.2f}")
    else:
        print(f"Error: {result['error']}")


def example_market_overview():
    """Example: Get market overview"""
    print_section("Example 3: Market Overview (Top 5)")
    
    result = json.loads(get_market_overview(5))
    
    if result['status'] == 'success':
        print(f"Showing top {result['limit']} cryptocurrencies:\n")
        for i, coin in enumerate(result['cryptocurrencies'], 1):
            print(f"{i}. {coin['name']} ({coin['symbol']})")
            print(f"   Price: ${coin['price_usd']:,.2f}")
            print(f"   24h Change: {coin['price_change_24h_percent']:.2f}%")
            print(f"   Market Cap: ${coin['market_cap_usd']:,.0f}")
            print(f"   Rank: #{coin['market_cap_rank']}\n")
    else:
        print(f"Error: {result['error']}")


def example_trading_signals():
    """Example: Get trading signals for Ethereum"""
    print_section("Example 4: Trading Signals for Ethereum")
    
    result = json.loads(get_trading_signals('ethereum', 30))
    
    if result['status'] == 'success':
        print(f"Coin: {result['coin']}")
        print(f"Signal: {result['signal']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Current Price: ${result['price']:,.2f}")
        print("\nReasons:")
        for reason in result['reasons']:
            print(f"  • {reason}")
    else:
        print(f"Error: {result['error']}")


def example_analyze():
    """Example: Comprehensive analysis"""
    print_section("Example 5: Comprehensive Analysis of Cardano")
    
    result = json.loads(analyze_cryptocurrency('cardano', 30))
    
    if result['status'] == 'success':
        print(f"Coin: {result['coin']}")
        print(f"Analysis Period: {result['days']} days")
        print(f"Data Points: {result['data_points']}")
        print(f"Current Price: ${result['price']:,.2f}")
        
        if 'signals' in result:
            signals = result['signals']
            print(f"\nSignals:")
            print(f"  Signal: {signals.get('signal', 'N/A')}")
            print(f"  Confidence: {signals.get('confidence', 0):.2f}")
            print(f"  Recommendation: {signals.get('recommendation', 'N/A')}")
        
        if 'indicators' in result:
            print(f"\nTechnical Indicators:")
            indicators = result['indicators']
            for key, value in indicators.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
    else:
        print(f"Error: {result['error']}")


def main():
    """Run all examples"""
    print("\n" + "🚀" * 30)
    print("  LetsGetCrypto MCP Tools - Usage Examples")
    print("🚀" * 30)
    
    print("\nThese examples demonstrate the MCP tools available to Claude AI.")
    print("When using Claude Desktop with MCP configured, Claude can call these")
    print("tools to provide cryptocurrency analysis and market data.\n")
    
    examples = [
        example_list_coins,
        example_get_price,
        example_market_overview,
        example_trading_signals,
        example_analyze
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError running example: {e}")
            print("(This may be due to API connectivity issues)")
    
    print("\n" + "=" * 60)
    print("  Examples completed!")
    print("=" * 60)
    print("\n⚠️  DISCLAIMER:")
    print("These tools are for educational purposes only.")
    print("Trading decisions should not be based solely on automated signals.")
    print("Always do your own research before making investment decisions.\n")


if __name__ == "__main__":
    main()
