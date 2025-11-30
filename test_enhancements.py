#!/usr/bin/env python3
"""
Test script for enhanced crypto API features
"""

import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letsgetcrypto_django.settings')
django.setup()

from decimal import Decimal
from crypto_api.models import WatchlistItem
from crypto_api.utils import (
    validate_coin_id, validate_symbol, validate_positive_integer,
    validate_decimal, sanitize_string, InMemoryCache, RateLimiter
)
from crypto_api.config_validator import ConfigValidator, validate_crypto_api_settings
from crypto_api.model_manager import ModelManager, ModelVersion
from datetime import datetime


def test_model_enhancements():
    """Test enhanced WatchlistItem model"""
    print("\n=== Testing Model Enhancements ===")
    
    # Delete any existing test items
    WatchlistItem.objects.filter(coin_id='bitcoin-test').delete()
    
    # Create a test item
    item = WatchlistItem(
        coin_id='bitcoin-test',
        coin_name='Bitcoin',
        coin_symbol='BTC',
        last_price=Decimal('50000.00'),
        market_cap=Decimal('1000000000000'),
        volume_24h=Decimal('50000000000'),
        price_change_24h=Decimal('2.5'),
        is_favorite=True,
        alert_enabled=True
    )
    item.save()
    
    print(f"✓ Created WatchlistItem: {item}")
    print(f"✓ Price change percentage: {item.get_price_change_percentage()}%")
    
    # Test update method
    item.update_price_data(
        price=Decimal('51000.00'),
        market_cap=Decimal('1050000000000')
    )
    print(f"✓ Updated price data: ${item.last_price}")
    
    # Cleanup
    item.delete()
    
    return True


def test_validation():
    """Test input validation utilities"""
    print("\n=== Testing Input Validation ===")
    
    # Test coin_id validation
    try:
        valid_id = validate_coin_id('bitcoin')
        print(f"✓ Valid coin_id: {valid_id}")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Test invalid coin_id
    try:
        validate_coin_id('invalid@coin!')
        print("✗ Should have failed validation")
        return False
    except ValueError:
        print("✓ Invalid coin_id rejected correctly")
    
    # Test symbol validation
    try:
        valid_symbol = validate_symbol('btc')
        print(f"✓ Valid symbol: {valid_symbol}")
    except ValueError as e:
        print(f"✗ Symbol validation failed: {e}")
        return False
    
    # Test integer validation
    try:
        valid_int = validate_positive_integer(10, 'test', min_val=1, max_val=100)
        print(f"✓ Valid integer: {valid_int}")
    except ValueError as e:
        print(f"✗ Integer validation failed: {e}")
        return False
    
    # Test decimal validation
    try:
        valid_decimal = validate_decimal('123.45', 'price')
        print(f"✓ Valid decimal: {valid_decimal}")
    except ValueError as e:
        print(f"✗ Decimal validation failed: {e}")
        return False
    
    # Test string sanitization
    sanitized = sanitize_string('Hello <script>alert("xss")</script> World')
    print(f"✓ Sanitized string: {sanitized}")
    
    return True


def test_caching():
    """Test in-memory caching"""
    print("\n=== Testing In-Memory Cache ===")
    
    cache = InMemoryCache()
    
    # Set value
    cache.set('test_key', {'data': 'test_value'}, timeout=60)
    print("✓ Set cache value")
    
    # Get value
    value = cache.get('test_key')
    if value and value['data'] == 'test_value':
        print(f"✓ Retrieved cache value: {value}")
    else:
        print("✗ Failed to retrieve cache value")
        return False
    
    # Test cache stats
    stats = cache.get_stats()
    print(f"✓ Cache stats: {stats}")
    
    # Clear cache
    cache.clear()
    print("✓ Cache cleared")
    
    return True


def test_rate_limiting():
    """Test rate limiting"""
    print("\n=== Testing Rate Limiting ===")
    
    limiter = RateLimiter()
    
    # Test rate limit
    allowed_count = 0
    for i in range(15):
        if limiter.is_allowed('test_client', max_requests=10, window_seconds=60):
            allowed_count += 1
    
    if allowed_count == 10:
        print(f"✓ Rate limiter working: {allowed_count}/15 requests allowed")
    else:
        print(f"✗ Rate limiter failed: {allowed_count}/15 requests allowed (expected 10)")
        return False
    
    # Test remaining requests
    remaining = limiter.get_remaining('test_client', max_requests=10, window_seconds=60)
    print(f"✓ Remaining requests: {remaining}")
    
    # Reset
    limiter.reset('test_client')
    print("✓ Rate limit reset")
    
    return True


def test_config_validation():
    """Test configuration validation"""
    print("\n=== Testing Configuration Validation ===")
    
    validator = ConfigValidator()
    
    # Test URL validation
    validator.validate_url('https://api.example.com', 'Test API URL')
    
    # Test integer validation
    validator.validate_integer(30, 'timeout', min_val=1, max_val=120)
    
    # Test boolean validation
    validator.validate_boolean(True, 'debug_mode')
    
    if validator.has_errors():
        print(f"✗ Validation failed: {validator.get_errors()}")
        return False
    else:
        print("✓ Configuration validation passed")
    
    # Test crypto API settings validation
    settings = {
        'COINGECKO_API_URL': 'https://api.coingecko.com/api/v3',
        'BINANCE_API_URL': 'https://api.binance.com/api/v3',
        'REQUEST_TIMEOUT': 30,
        'CACHE_TIMEOUT': 300,
        'MAX_RETRIES': 3
    }
    
    api_validator = validate_crypto_api_settings(settings)
    if api_validator.has_errors():
        print(f"✗ API settings validation failed: {api_validator.get_errors()}")
        return False
    else:
        print("✓ API settings validation passed")
    
    return True


def test_model_manager():
    """Test ML model manager"""
    print("\n=== Testing Model Manager ===")
    
    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
    except ImportError as e:
        print(f"⚠ Skipping test: {e}")
        return True
    
    manager = ModelManager(models_dir='/tmp/test_models')
    
    # Create a simple test model
    X_train = np.random.rand(100, 10)
    y_train = np.random.randint(0, 2, 100)
    
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Save model
    version = manager.save_model(
        model=model,
        model_type='test_logistic_regression',
        metrics={'accuracy': 0.85, 'precision': 0.83},
        hyperparameters={'C': 1.0, 'max_iter': 100},
        training_data=X_train
    )
    print(f"✓ Saved model version: {version}")
    
    # Load model
    try:
        loaded_model, model_version = manager.load_model('test_logistic_regression', version)
        print(f"✓ Loaded model: {model_version.model_type} v{model_version.version}")
        print(f"  Metrics: {model_version.metrics}")
        print(f"  Hyperparameters: {model_version.hyperparameters}")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return False
    
    # List versions
    versions = manager.list_versions('test_logistic_regression')
    print(f"✓ Found {len(versions)} model version(s)")
    
    # Get model info
    info = manager.get_model_info('test_logistic_regression', version)
    if info:
        print(f"✓ Retrieved model info: {info.to_dict()}")
    else:
        print("✗ Failed to retrieve model info")
        return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("LetsGetCrypto Enhancement Tests")
    print("=" * 60)
    
    tests = [
        ("Model Enhancements", test_model_enhancements),
        ("Input Validation", test_validation),
        ("In-Memory Caching", test_caching),
        ("Rate Limiting", test_rate_limiting),
        ("Configuration Validation", test_config_validation),
        ("Model Manager", test_model_manager),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
