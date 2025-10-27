#!/usr/bin/env python3
"""
Example: Using Claude with Infinite Context Window (Prompt Caching)

This example demonstrates how prompt caching works with the ClaudeAnalyzer
to achieve 90% cost reduction and 85% faster responses for repeated analyses.
"""

import os
import sys

# Add parent directory to path to import claude_analyzer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from claude_analyzer import ClaudeAnalyzer


def main():
    """Demonstrate prompt caching usage"""
    
    print("=" * 70)
    print("Claude Infinite Context Window Example")
    print("=" * 70)
    
    # Check if API key is available
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n⚠️  No API key found. This is a demonstration of the structure.")
        print("   To run with actual API calls:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print()
    
    # Initialize analyzer with caching enabled (default)
    analyzer = ClaudeAnalyzer()
    
    print(f"\n✓ ClaudeAnalyzer initialized")
    print(f"  - Caching enabled: {analyzer.enable_caching}")
    print(f"  - Model: {analyzer.model}")
    print(f"  - API available: {analyzer.is_available()}")
    
    # Example 1: Market Analysis with Caching
    print("\n" + "=" * 70)
    print("Example 1: Market Analysis with Prompt Caching")
    print("=" * 70)
    
    print("\nScenario: Analyzing multiple cryptocurrencies")
    print("  First request: Full cost, ~2-3 seconds")
    print("  Subsequent requests: 10% cost, ~0.3-0.5 seconds (cached)")
    
    sample_analysis = {
        'coin': 'Bitcoin',
        'price': 45000.00,
        'change_24h': 3.5,
        'technical_indicators': {
            'rsi': 65.0,
            'macd': 0.0125,
            'sma_7': 44500.00,
            'sma_25': 43000.00,
            'volatility': 0.0234
        },
        'ml_predictions': {
            'signal': 'BUY',
            'confidence': 0.75
        },
        'fear_greed_index': 65
    }
    
    print(f"\nAnalyzing: {sample_analysis['coin']}")
    print(f"  Price: ${sample_analysis['price']:,.2f}")
    print(f"  24h Change: {sample_analysis['change_24h']:+.1f}%")
    
    if analyzer.is_available():
        # This would make an actual API call with caching
        result = analyzer.analyze_market_data(
            coin_name=sample_analysis['coin'],
            current_price=sample_analysis['price'],
            price_change_24h=sample_analysis['change_24h'],
            technical_indicators=sample_analysis['technical_indicators'],
            ml_predictions=sample_analysis['ml_predictions'],
            fear_greed_index=sample_analysis['fear_greed_index']
        )
        print("\n✓ Analysis complete!")
        print(f"  Analysis: {result['analysis'][:100]}...")
        print(f"  Recommendation: {result['recommendation'][:100]}...")
    else:
        print("\n  (API key not configured - showing structure only)")
        print("  With API key, this would:")
        print("    1. Cache the system prompt (analysis instructions)")
        print("    2. Cache the market context")
        print("    3. Return AI-powered analysis")
        print("    4. Reuse cached content for next 5 minutes")
    
    # Example 2: Trading Signal Explanations
    print("\n" + "=" * 70)
    print("Example 2: Trading Signal Explanations with Caching")
    print("=" * 70)
    
    print("\nScenario: Explaining multiple trading signals")
    print("  Cached: Instruction template for explanations")
    print("  Benefit: Fast explanations for multiple signals")
    
    signal_data = {
        'signal': 'BUY',
        'confidence': 0.82,
        'technical_reasons': [
            'RSI below 30 (oversold)',
            'MACD bullish crossover',
            'Price above 7-day SMA'
        ],
        'coin_name': 'Ethereum'
    }
    
    print(f"\nExplaining signal for: {signal_data['coin_name']}")
    print(f"  Signal: {signal_data['signal']}")
    print(f"  Confidence: {signal_data['confidence']:.0%}")
    
    if analyzer.is_available():
        explanation = analyzer.explain_trading_signal(
            signal=signal_data['signal'],
            confidence=signal_data['confidence'],
            technical_reasons=signal_data['technical_reasons'],
            coin_name=signal_data['coin_name']
        )
        print(f"\n✓ Explanation: {explanation}")
    else:
        print("\n  (API key not configured - showing structure only)")
        print("  With API key, cached instruction template would be reused")
    
    # Example 3: Disabling Caching
    print("\n" + "=" * 70)
    print("Example 3: Controlling Caching Behavior")
    print("=" * 70)
    
    print("\nCaching can be toggled on/off as needed:")
    
    # Disable caching
    analyzer.set_caching(False)
    print(f"  Caching disabled: {not analyzer.enable_caching}")
    
    # Re-enable caching
    analyzer.set_caching(True)
    print(f"  Caching re-enabled: {analyzer.enable_caching}")
    
    print("\nWhen to disable caching:")
    print("  - One-time queries")
    print("  - Testing different prompts")
    print("  - When requests are >5 minutes apart")
    
    # Summary
    print("\n" + "=" * 70)
    print("Caching Benefits Summary")
    print("=" * 70)
    
    print("\n✓ Cost Reduction (per Anthropic documentation):")
    print("  - Cache writes: +25% above standard rate")
    print("  - Cached reads: 10% of standard rate")
    print("  - Overall savings: ~90% for repeated analyses")
    
    print("\n✓ Performance Improvement:")
    print("  - First request: ~2-3 seconds")
    print("  - Cached requests: ~0.3-0.5 seconds")
    print("  - Latency reduction: ~85%")
    
    print("\n✓ Cache Behavior:")
    print("  - TTL: 5 minutes")
    print("  - Auto-refresh on each use")
    print("  - Transparent to user")
    
    print("\n" + "=" * 70)
    print("For more information, see PROMPT_CACHING.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
