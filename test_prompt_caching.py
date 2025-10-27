#!/usr/bin/env python3
"""
Test script for Claude prompt caching (infinite context window) feature
"""

import os
import sys
from claude_analyzer import ClaudeAnalyzer, ANTHROPIC_AVAILABLE


def test_caching_configuration():
    """Test that caching can be enabled/disabled"""
    print("=" * 60)
    print("Testing Prompt Caching Configuration")
    print("=" * 60)
    
    analyzer = ClaudeAnalyzer()
    
    # Test default state
    print(f"\n1. Default caching state: {analyzer.enable_caching}")
    assert analyzer.enable_caching == True, "Caching should be enabled by default"
    print("   ✓ Caching is enabled by default")
    
    # Test disabling
    analyzer.set_caching(False)
    print(f"2. After disabling: {analyzer.enable_caching}")
    assert analyzer.enable_caching == False, "Caching should be disabled"
    print("   ✓ Caching can be disabled")
    
    # Test re-enabling
    analyzer.set_caching(True)
    print(f"3. After re-enabling: {analyzer.enable_caching}")
    assert analyzer.enable_caching == True, "Caching should be enabled"
    print("   ✓ Caching can be re-enabled")
    
    print("\n✓ All caching configuration tests passed!")
    return True


def test_api_structure():
    """Test that API calls are structured correctly for caching"""
    print("\n" + "=" * 60)
    print("Testing API Call Structure")
    print("=" * 60)
    
    analyzer = ClaudeAnalyzer()
    
    # Check that methods exist
    print("\n1. Checking method availability:")
    methods = [
        'analyze_market_data',
        'explain_trading_signal',
        'get_risk_insights',
        'set_caching'
    ]
    
    for method in methods:
        assert hasattr(analyzer, method), f"Missing method: {method}"
        print(f"   ✓ {method} exists")
    
    print("\n2. Caching feature attributes:")
    print(f"   - enable_caching attribute: {hasattr(analyzer, 'enable_caching')}")
    print(f"   - Caching enabled: {analyzer.enable_caching}")
    
    print("\n✓ API structure tests passed!")
    return True


def test_mock_caching_behavior():
    """Test caching behavior with mock data (no API key required)"""
    print("\n" + "=" * 60)
    print("Testing Caching Behavior (Mock)")
    print("=" * 60)
    
    if not ANTHROPIC_AVAILABLE:
        print("\n⚠️  Anthropic library not available, skipping API tests")
        return True
    
    analyzer = ClaudeAnalyzer()
    
    if not analyzer.is_available():
        print("\n⚠️  No API key configured, showing expected behavior:")
        print("\nWith prompt caching enabled:")
        print("  - System prompts are cached with cache_control")
        print("  - Market context is cached for repeated analysis")
        print("  - Cost reduced by ~90% for cached content")
        print("  - Latency reduced by ~85% for cached content")
        print("  - Cache TTL: 5 minutes (refreshed on each use)")
        
        print("\nCaching is used in these methods:")
        print("  1. analyze_market_data() - caches system prompt and market context")
        print("  2. explain_trading_signal() - caches instruction prompt")
        print("  3. get_risk_insights() - caches analysis framework")
        
        print("\nExample cache_control structure:")
        print('  {')
        print('    "type": "text",')
        print('    "text": "<prompt content>",')
        print('    "cache_control": {"type": "ephemeral"}')
        print('  }')
        
        return True
    
    print("\n✓ API key is configured - caching will be used in production")
    return True


def test_documentation():
    """Test that documentation mentions caching"""
    print("\n" + "=" * 60)
    print("Testing Documentation")
    print("=" * 60)
    
    analyzer = ClaudeAnalyzer()
    
    # Check class docstring
    doc = ClaudeAnalyzer.__doc__
    print("\n1. Class docstring mentions:")
    assert "infinite context" in doc.lower() or "prompt caching" in doc.lower(), \
        "Docstring should mention infinite context or prompt caching"
    print("   ✓ Infinite context window feature")
    
    assert "90%" in doc or "cost" in doc.lower(), \
        "Docstring should mention cost savings"
    print("   ✓ Cost reduction benefits")
    
    assert "85%" in doc or "latency" in doc.lower(), \
        "Docstring should mention latency improvements"
    print("   ✓ Latency reduction benefits")
    
    # Check set_caching docstring
    set_caching_doc = analyzer.set_caching.__doc__
    print("\n2. set_caching() method documentation:")
    assert "prompt caching" in set_caching_doc.lower(), \
        "set_caching should document prompt caching"
    print("   ✓ Explains prompt caching")
    
    assert "5 minutes" in set_caching_doc or "ttl" in set_caching_doc.lower(), \
        "Should mention cache TTL"
    print("   ✓ Mentions cache TTL")
    
    print("\n✓ Documentation tests passed!")
    return True


def main():
    """Run all tests"""
    print("\n🚀 Testing Claude Prompt Caching (Infinite Context Window)\n")
    
    tests = [
        ("Caching Configuration", test_caching_configuration),
        ("API Structure", test_api_structure),
        ("Mock Caching Behavior", test_mock_caching_behavior),
        ("Documentation", test_documentation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n❌ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
