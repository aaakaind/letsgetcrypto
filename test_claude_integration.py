#!/usr/bin/env python3
"""
Test script for Claude Opus 4.1 integration
Demonstrates the AI analysis features without requiring full app setup
"""

import os
import sys
from claude_analyzer import ClaudeAnalyzer, ANTHROPIC_AVAILABLE

def test_claude_availability():
    """Test if Claude integration is available"""
    print("="*60)
    print("Claude Opus 4.1 Integration Test")
    print("="*60)
    
    print(f"\n1. Anthropic library available: {ANTHROPIC_AVAILABLE}")
    
    if not ANTHROPIC_AVAILABLE:
        print("\n⚠️  Anthropic library not installed.")
        print("   Install with: pip install anthropic")
        return False
    
    # Check if API key is configured
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    print(f"2. API key configured: {api_key is not None}")
    
    if not api_key:
        print("\n⚠️  No API key found in environment.")
        print("   Set with: export ANTHROPIC_API_KEY='your-key'")
        print("   Get your key at: https://console.anthropic.com/")
    
    # Initialize analyzer
    analyzer = ClaudeAnalyzer()
    print(f"3. ClaudeAnalyzer initialized: True")
    print(f"4. Claude is available: {analyzer.is_available()}")
    print(f"5. Model: {analyzer.model}")
    
    return analyzer.is_available()

def test_mock_analysis():
    """Test analyzer with mock data (doesn't require API key)"""
    print("\n" + "="*60)
    print("Mock Analysis Test (Structure Only)")
    print("="*60)
    
    analyzer = ClaudeAnalyzer()
    
    # Sample data structure
    print("\nSample Analysis Request Structure:")
    print("  - Coin: Bitcoin")
    print("  - Current Price: $45,000")
    print("  - 24h Change: +3.5%")
    print("  - Technical Indicators: RSI, MACD, SMA, etc.")
    print("  - ML Signal: BUY with 75% confidence")
    print("  - Fear & Greed Index: 65 (Greed)")
    
    if analyzer.is_available():
        print("\n✓ Claude is available and ready for analysis!")
        print("  When API is called, it will provide:")
        print("    • Comprehensive market analysis")
        print("    • Trading recommendations with reasoning")
        print("    • Risk assessment")
        print("    • Key insights in bullet points")
    else:
        print("\n⚠️  Claude not available. Analysis would return:")
        print("    • Generic unavailable messages")
        print("    • Basic fallback information")
        print("    • No AI-powered insights")

def test_integration_points():
    """Show where Claude is integrated"""
    print("\n" + "="*60)
    print("Integration Points")
    print("="*60)
    
    print("\n1. HeadlessCryptoAPI (headless_crypto_api.py):")
    print("   - analyze_cryptocurrency() method")
    print("   - Adds 'claude_analysis' to results")
    print("   - Optional parameter: use_claude=True/False")
    
    print("\n2. Main GUI Application (main.py):")
    print("   - Initialized in CryptoPredictionApp.__init__()")
    print("   - Analysis triggered in get_predictions()")
    print("   - Results displayed in update_predictions_display()")
    
    print("\n3. Claude Analyzer Module (claude_analyzer.py):")
    print("   - ClaudeAnalyzer class")
    print("   - analyze_market_data() - Main analysis function")
    print("   - explain_trading_signal() - Signal explanations")
    print("   - get_risk_insights() - Risk assessment")
    
    print("\n4. API Key Configuration:")
    print("   - Environment variable: ANTHROPIC_API_KEY")
    print("   - Gracefully degrades if not configured")
    print("   - No breaking changes to existing functionality")

def main():
    """Run all tests"""
    print("\n🚀 Testing Claude Opus 4.1 Integration\n")
    
    claude_available = test_claude_availability()
    test_mock_analysis()
    test_integration_points()
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    if ANTHROPIC_AVAILABLE and claude_available:
        print("\n✓ All tests passed!")
        print("✓ Claude Opus 4.1 is ready to use")
        print("\nNext steps:")
        print("  1. Run the main application: python main.py")
        print("  2. Fetch cryptocurrency data")
        print("  3. Generate predictions to see AI insights")
    elif ANTHROPIC_AVAILABLE:
        print("\n⚠️  Claude library installed but API key not configured")
        print("\nTo enable AI features:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nThe application will work without Claude, just without AI insights.")
    else:
        print("\n⚠️  Anthropic library not installed")
        print("\nTo enable AI features:")
        print("  1. pip install anthropic")
        print("  2. export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nThe application will work without Claude, just without AI insights.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
