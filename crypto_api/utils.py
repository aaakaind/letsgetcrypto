"""
Utility functions for the crypto API including caching, rate limiting, and validation.
"""

import hashlib
import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


# ========== In-Memory Cache Implementation ==========

class InMemoryCache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            if time.time() < self._expiry.get(key, 0):
                logger.debug(f"Cache hit: {key}")
                return self._cache[key]
            else:
                # Expired, remove it
                self.delete(key)
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> None:
        """Set value in cache with timeout in seconds"""
        self._cache[key] = value
        self._expiry[key] = time.time() + timeout
        logger.debug(f"Cache set: {key} (expires in {timeout}s)")
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        current_time = time.time()
        active_entries = sum(1 for exp_time in self._expiry.values() if exp_time > current_time)
        return {
            'total_entries': len(self._cache),
            'active_entries': active_entries,
            'expired_entries': len(self._cache) - active_entries
        }


# Global cache instance
_memory_cache = InMemoryCache()


def cached(timeout: int = 300, key_prefix: str = "") -> Callable:
    """
    Decorator to cache function results in memory
    
    Args:
        timeout: Cache timeout in seconds (default: 300)
        key_prefix: Optional prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            
            # Add args to key (skip 'request' object)
            for arg in args:
                if hasattr(arg, 'method'):  # Skip request objects
                    continue
                key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Try to get from cache
            result = _memory_cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _memory_cache.set(cache_key, result, timeout)
            return result
        
        # Add cache management methods
        wrapper.clear_cache = _memory_cache.clear
        wrapper.cache_stats = _memory_cache.get_stats
        
        return wrapper
    return decorator


# ========== Rate Limiting ==========

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self) -> None:
        self._requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier for the client (IP, user ID, etc.)
            max_requests: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        cutoff = now - window_seconds
        
        # Remove old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > cutoff
        ]
        
        # Check if under limit
        if len(self._requests[key]) < max_requests:
            self._requests[key].append(now)
            return True
        
        return False
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests in current window"""
        now = time.time()
        cutoff = now - window_seconds
        
        # Count recent requests
        recent = sum(1 for req_time in self._requests.get(key, []) if req_time > cutoff)
        return max(0, max_requests - recent)
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key"""
        self._requests.pop(key, None)


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60) -> Callable:
    """
    Decorator to rate limit API endpoints
    
    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs) -> JsonResponse:
            # Use IP address as key
            client_ip = get_client_ip(request)
            
            if not _rate_limiter.is_allowed(client_ip, max_requests, window_seconds):
                remaining = _rate_limiter.get_remaining(client_ip, max_requests, window_seconds)
                logger.warning(f"Rate limit exceeded for {client_ip}")
                
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window_seconds} seconds',
                    'retry_after': window_seconds
                }, status=429)
                
                response['X-RateLimit-Limit'] = str(max_requests)
                response['X-RateLimit-Remaining'] = str(remaining)
                response['Retry-After'] = str(window_seconds)
                
                return response
            
            # Add rate limit headers to response
            response = func(request, *args, **kwargs)
            remaining = _rate_limiter.get_remaining(client_ip, max_requests, window_seconds)
            
            if isinstance(response, JsonResponse):
                response['X-RateLimit-Limit'] = str(max_requests)
                response['X-RateLimit-Remaining'] = str(remaining)
            
            return response
        
        return wrapper
    return decorator


# ========== Validation Utilities ==========

def validate_coin_id(coin_id: str) -> str:
    """
    Validate and sanitize cryptocurrency ID
    
    Args:
        coin_id: Cryptocurrency ID to validate
    
    Returns:
        Sanitized coin ID
    
    Raises:
        ValueError: If coin_id is invalid
    """
    if not coin_id or not isinstance(coin_id, str):
        raise ValueError("coin_id must be a non-empty string")
    
    # Remove whitespace
    coin_id = coin_id.strip()
    
    # Check length
    if len(coin_id) < 1 or len(coin_id) > 100:
        raise ValueError("coin_id must be between 1 and 100 characters")
    
    # Only allow alphanumeric, hyphens, and underscores
    if not all(c.isalnum() or c in '-_' for c in coin_id):
        raise ValueError("coin_id can only contain alphanumeric characters, hyphens, and underscores")
    
    return coin_id.lower()


def validate_symbol(symbol: str) -> str:
    """
    Validate and sanitize cryptocurrency symbol
    
    Args:
        symbol: Cryptocurrency symbol to validate
    
    Returns:
        Sanitized symbol (uppercase)
    
    Raises:
        ValueError: If symbol is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol must be a non-empty string")
    
    # Remove whitespace
    symbol = symbol.strip()
    
    # Check length
    if len(symbol) < 1 or len(symbol) > 20:
        raise ValueError("symbol must be between 1 and 20 characters")
    
    # Only allow letters and numbers
    if not symbol.replace('-', '').isalnum():
        raise ValueError("symbol can only contain alphanumeric characters and hyphens")
    
    return symbol.upper()


def validate_positive_integer(value: Any, name: str = "value", 
                              min_val: int = 1, max_val: Optional[int] = None) -> int:
    """
    Validate and convert to positive integer
    
    Args:
        value: Value to validate
        name: Name of the parameter for error messages
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Validated integer
    
    Raises:
        ValueError: If value is invalid
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a valid integer")
    
    if int_value < min_val:
        raise ValueError(f"{name} must be at least {min_val}")
    
    if max_val is not None and int_value > max_val:
        raise ValueError(f"{name} must be at most {max_val}")
    
    return int_value


def validate_decimal(value: Any, name: str = "value") -> Decimal:
    """
    Validate and convert to Decimal
    
    Args:
        value: Value to validate
        name: Name of the parameter for error messages
    
    Returns:
        Validated Decimal
    
    Raises:
        ValueError: If value is invalid
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    
    try:
        return Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError(f"{name} must be a valid decimal number")


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes and control characters
    sanitized = ''.join(c for c in value if c.isprintable() or c.isspace())
    
    # Trim to max length
    return sanitized[:max_length].strip()


# ========== Helper Functions ==========

def get_client_ip(request) -> str:
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def json_response_with_timestamp(data: Dict[str, Any], status: int = 200) -> JsonResponse:
    """Create a JSON response with timestamp"""
    data['timestamp'] = int(time.time())
    return JsonResponse(data, status=status)
