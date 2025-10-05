#!/usr/bin/env python3
"""
Test script for MCP server functionality
"""

import json
from mcp_server import (
    list_supported_coins,
    get_crypto_price,
    get_market_overview,
    get_trading_signals,
    analyze_cryptocurrency
)


def test_list_supported_coins():
    """Test listing supported coins"""
    print("Testing list_supported_coins...")
    result = json.loads(list_supported_coins())
    assert result['status'] == 'success'
    assert len(result['supported_coins']) > 0
    print(f"✓ Found {result['total']} supported coins")
    return True


def test_get_crypto_price():
    """Test getting crypto price"""
    print("\nTesting get_crypto_price...")
    result = json.loads(get_crypto_price('bitcoin', 7))
    
    if result.get('status') == 'error':
        print(f"⚠️  API error: {result.get('error')}")
        return False
    
    assert result['status'] == 'success'
    assert 'current_price' in result
    assert 'price_change_percent' in result
    print(f"✓ Bitcoin price: ${result['current_price']:.2f}")
    print(f"  7-day change: {result['price_change_percent']:.2f}%")
    return True


def test_get_market_overview():
    """Test getting market overview"""
    print("\nTesting get_market_overview...")
    result = json.loads(get_market_overview(5))
    
    if result.get('status') == 'error':
        print(f"⚠️  API error: {result.get('error')}")
        return False
    
    assert result['status'] == 'success'
    assert len(result['cryptocurrencies']) > 0
    print(f"✓ Retrieved {result['total_coins']} cryptocurrencies")
    for coin in result['cryptocurrencies'][:3]:
        print(f"  {coin['symbol']}: ${coin['price_usd']:.2f}")
    return True


def test_get_trading_signals():
    """Test getting trading signals"""
    print("\nTesting get_trading_signals...")
    result = json.loads(get_trading_signals('ethereum', 7))
    
    if result.get('status') == 'error':
        print(f"⚠️  API error: {result.get('error')}")
        return False
    
    assert result['status'] == 'success'
    assert 'signal' in result
    assert 'confidence' in result
    print(f"✓ Signal: {result['signal']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Recommendation: {result['recommendation']}")
    return True


def test_analyze_cryptocurrency():
    """Test cryptocurrency analysis"""
    print("\nTesting analyze_cryptocurrency...")
    result = json.loads(analyze_cryptocurrency('bitcoin', 7))
    
    if result.get('status') == 'error':
        print(f"⚠️  API error: {result.get('error')}")
        return False
    
    assert result['status'] == 'success'
    print(f"✓ Analysis completed for {result.get('coin', 'unknown')}")
    if 'signals' in result:
        print(f"  Signal: {result['signals'].get('signal', 'N/A')}")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Server Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("List Supported Coins", test_list_supported_coins),
        ("Get Crypto Price", test_get_crypto_price),
        ("Get Market Overview", test_get_market_overview),
        ("Get Trading Signals", test_get_trading_signals),
        ("Analyze Cryptocurrency", test_analyze_cryptocurrency),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("\n⚠️  Some tests failed - likely due to API rate limits or network issues")
        print("   This is normal for external API dependencies")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
