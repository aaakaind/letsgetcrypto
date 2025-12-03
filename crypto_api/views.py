import json as json_lib
import logging
import time
from decimal import Decimal
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import connection, DatabaseError, IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from requests.exceptions import (
    RequestException, Timeout, ConnectionError, HTTPError, TooManyRedirects
)

from .models import WatchlistItem
from .utils import (
    cached, rate_limit, validate_coin_id, validate_symbol,
    validate_positive_integer, sanitize_string, json_response_with_timestamp
)

logger = logging.getLogger(__name__)


# ========== Custom Exceptions ==========

class CryptoAPIError(Exception):
    """Base exception for Crypto API errors"""
    pass


class ValidationError(CryptoAPIError):
    """Raised when input validation fails"""
    pass


class ExternalAPIError(CryptoAPIError):
    """Raised when external API call fails"""
    pass


class NotFoundError(CryptoAPIError):
    """Raised when resource is not found"""
    pass


# ========== Utility Functions ==========

def get_version() -> str:
    """Get the application version from VERSION file"""
    try:
        version_file = Path(settings.BASE_DIR) / 'VERSION'
        if version_file.exists():
            return version_file.read_text().strip()
        return '1.0.0'
    except Exception as e:
        logger.warning(f"Could not read VERSION file: {e}")
        return '1.0.0'


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle common API errors with specific exception types
    
    Provides comprehensive error handling with proper logging and user-friendly messages
    """
    @wraps(func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        try:
            return func(request, *args, **kwargs)
        
        # Handle validation errors
        except (ValidationError, ValueError) as e:
            logger.warning(f"Validation error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'validation',
                'client_ip': request.META.get('REMOTE_ADDR', 'unknown')
            })
            return JsonResponse({
                'error': 'Validation error',
                'message': str(e)
            }, status=400)
        
        # Handle database errors
        except IntegrityError as e:
            logger.error(f"Database integrity error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'database_integrity'
            })
            return JsonResponse({
                'error': 'Database error',
                'message': 'Resource already exists or constraint violation'
            }, status=409)
        
        except DatabaseError as e:
            logger.error(f"Database error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'database'
            })
            return JsonResponse({
                'error': 'Database error',
                'message': 'Failed to perform database operation'
            }, status=500)
        
        # Handle external API errors
        except Timeout as e:
            logger.error(f"API timeout in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'api_timeout'
            })
            return JsonResponse({
                'error': 'External API timeout',
                'message': 'Request to external service timed out'
            }, status=504)
        
        except ConnectionError as e:
            logger.error(f"API connection error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'api_connection'
            })
            return JsonResponse({
                'error': 'External API unavailable',
                'message': 'Could not connect to external service'
            }, status=503)
        
        except HTTPError as e:
            logger.error(f"API HTTP error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'api_http',
                'status_code': e.response.status_code if e.response else None
            })
            return JsonResponse({
                'error': 'External API error',
                'message': f'External service returned error: {e.response.status_code if e.response else "unknown"}'
            }, status=502)
        
        except TooManyRedirects as e:
            logger.error(f"API redirect error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'api_redirect'
            })
            return JsonResponse({
                'error': 'External API error',
                'message': 'Too many redirects from external service'
            }, status=502)
        
        except RequestException as e:
            logger.error(f"API request failed in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'api_request'
            })
            return JsonResponse({
                'error': 'External API error',
                'message': 'Failed to communicate with external service'
            }, status=503)
        
        # Handle not found errors
        except NotFoundError as e:
            logger.info(f"Resource not found in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'not_found'
            })
            return JsonResponse({
                'error': 'Not found',
                'message': str(e)
            }, status=404)
        
        # Handle JSON decode errors
        except json_lib.JSONDecodeError as e:
            logger.warning(f"JSON decode error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'json_decode'
            })
            return JsonResponse({
                'error': 'Invalid JSON',
                'message': 'Request body contains invalid JSON'
            }, status=400)
        
        # Catch-all for unexpected errors
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}", extra={
                'function': func.__name__,
                'error_type': 'unexpected'
            })
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred' if not settings.DEBUG else str(e)
            }, status=500)
    
    return wrapper


# ========== Health Check Endpoints ==========

def health_check(request: HttpRequest) -> JsonResponse:
    """
    Enhanced health check endpoint with detailed component status
    
    Provides comprehensive system health information for load balancers
    and monitoring systems
    """
    try:
        # Initialize status
        status = {
            'status': 'healthy',
            'version': get_version(),
            'timestamp': int(time.time()),
            'components': {}
        }
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            status['components']['database'] = {
                'status': 'ok',
                'vendor': connection.vendor,
                'response_time_ms': 0  # Could measure actual time
            }
        except DatabaseError as e:
            logger.error(f"Database health check failed: {e}")
            status['components']['database'] = {
                'status': 'error',
                'message': 'Database connection failed'
            }
            status['status'] = 'unhealthy'
        
        # Test external API connectivity
        try:
            start_time = time.time()
            response = requests.get(
                f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/ping",
                timeout=5
            )
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                status['components']['external_api'] = {
                    'status': 'ok',
                    'response_time_ms': response_time
                }
            else:
                status['components']['external_api'] = {
                    'status': 'degraded',
                    'response_time_ms': response_time,
                    'status_code': response.status_code
                }
        except RequestException as e:
            logger.warning(f"External API health check failed: {e}")
            status['components']['external_api'] = {
                'status': 'degraded',
                'message': 'External API unreachable'
            }
        
        # Add system metrics if psutil is available
        try:
            import psutil
            status['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'platform': platform.system()
            }
        except (ImportError, Exception) as e:
            logger.debug(f"Could not get system metrics: {e}")
        
        # Determine overall health status
        component_statuses = [
            comp.get('status') for comp in status['components'].values()
        ]
        if 'error' in component_statuses:
            status['status'] = 'unhealthy'
        elif 'degraded' in component_statuses:
            status['status'] = 'degraded'
        
        http_status = 200 if status['status'] == 'healthy' else 503
        return json_response_with_timestamp(status, http_status)
        
    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return json_response_with_timestamp({
            'status': 'unhealthy',
            'error': str(e) if settings.DEBUG else 'Health check failed',
            'timestamp': int(time.time())
        }, status=503)


def readiness_check(request: HttpRequest) -> JsonResponse:
    """
    Readiness check endpoint for Kubernetes/ECS
    
    Indicates if the application is ready to accept traffic
    """
    try:
        # Check database connection
        connection.ensure_connection()
        
        # Check critical components
        status = {
            'status': 'ready',
            'checks': {
                'database': 'ok'
            }
        }
        
        return json_response_with_timestamp(status)
        
    except DatabaseError as e:
        logger.error(f"Readiness check failed: {e}")
        return json_response_with_timestamp({
            'status': 'not_ready',
            'checks': {
                'database': 'error'
            },
            'error': 'Database not ready'
        }, status=503)
    except Exception as e:
        logger.exception(f"Readiness check failed: {e}")
        return json_response_with_timestamp({
            'status': 'not_ready',
            'error': str(e) if settings.DEBUG else 'Not ready'
        }, status=503)


def liveness_check(request: HttpRequest) -> JsonResponse:
    """
    Liveness check endpoint for Kubernetes/ECS
    
    Simple check to verify the application is running
    """
    return json_response_with_timestamp({
        'status': 'alive'
    })


# ========== API Endpoints ==========

@csrf_exempt
@require_http_methods(["GET"])
@rate_limit(max_requests=100, window_seconds=60)  # 100 requests per minute
@handle_api_errors
@cached(timeout=60, key_prefix="crypto_price")  # Cache for 1 minute
def get_crypto_price(request: HttpRequest, symbol: str) -> JsonResponse:
    """
    Get current price for a cryptocurrency
    
    Args:
        request: HTTP request
        symbol: Cryptocurrency symbol or ID
    
    Returns:
        JSON response with current price and market data
    """
    # Validate symbol
    symbol = validate_coin_id(symbol)
    
    coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/simple/price"
    params = {
        'ids': symbol,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true'
    }
    
    response = requests.get(
        coingecko_url,
        params=params,
        timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
    )
    response.raise_for_status()
    
    data = response.json()
    if symbol not in data:
        raise NotFoundError(f'Cryptocurrency {symbol} not found')
    
    crypto_data = data[symbol]
    result = {
        'symbol': symbol.upper(),
        'price_usd': crypto_data.get('usd'),
        'market_cap_usd': crypto_data.get('usd_market_cap'),
        'volume_24h_usd': crypto_data.get('usd_24h_vol'),
        'price_change_24h_percent': crypto_data.get('usd_24h_change')
    }
    
    return json_response_with_timestamp(result)


@csrf_exempt
@require_http_methods(["GET"])
@rate_limit(max_requests=50, window_seconds=60)  # 50 requests per minute
@handle_api_errors
@cached(timeout=300, key_prefix="crypto_history")  # Cache for 5 minutes
def get_crypto_history(request: HttpRequest, symbol: str) -> JsonResponse:
    """
    Get historical price data for a cryptocurrency
    
    Args:
        request: HTTP request
        symbol: Cryptocurrency symbol or ID
    
    Returns:
        JSON response with historical price data
    """
    # Validate inputs
    symbol = validate_coin_id(symbol)
    days = validate_positive_integer(
        request.GET.get('days', 30),
        name='days',
        min_val=1,
        max_val=365
    )
    
    coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/coins/{symbol}/market_chart"
    params = {'vs_currency': 'usd', 'days': days}
    
    response = requests.get(
        coingecko_url,
        params=params,
        timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
    )
    response.raise_for_status()
    
    data = response.json()
    prices = [
        {'timestamp': int(ts / 1000), 'price': price}
        for ts, price in data.get('prices', [])
    ]
    
    result = {
        'symbol': symbol.upper(),
        'days': days,
        'data_points': len(prices),
        'prices': prices
    }
    
    return json_response_with_timestamp(result)


@csrf_exempt
@require_http_methods(["GET"])
@rate_limit(max_requests=60, window_seconds=60)  # 60 requests per minute
@handle_api_errors
@cached(timeout=120, key_prefix="market_overview")  # Cache for 2 minutes
def get_market_overview(request: HttpRequest) -> JsonResponse:
    """
    Get market overview with top cryptocurrencies
    
    Args:
        request: HTTP request with optional 'limit' query parameter
    
    Returns:
        JSON response with market overview data
    """
    # Validate limit parameter
    limit = validate_positive_integer(
        request.GET.get('limit', 10),
        name='limit',
        min_val=1,
        max_val=50
    )
    
    coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '24h'
    }
    
    response = requests.get(
        coingecko_url,
        params=params,
        timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
    )
    response.raise_for_status()
    
    data = response.json()
    market_data = [
        {
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name'),
            'price_usd': coin.get('current_price'),
            'market_cap_usd': coin.get('market_cap'),
            'volume_24h_usd': coin.get('total_volume'),
            'price_change_24h_percent': coin.get('price_change_percentage_24h'),
            'market_cap_rank': coin.get('market_cap_rank')
        }
        for coin in data
    ]
    
    result = {
        'market_overview': market_data,
        'total_cryptocurrencies': len(market_data)
    }
    
    return json_response_with_timestamp(result)


@csrf_exempt
@require_http_methods(["GET"])
@rate_limit(max_requests=100, window_seconds=60)  # 100 requests per minute
@handle_api_errors
@cached(timeout=300, key_prefix="search_crypto")  # Cache for 5 minutes
def search_crypto(request: HttpRequest) -> JsonResponse:
    """
    Search for cryptocurrencies by name or symbol
    
    Args:
        request: HTTP request with 'query' parameter
    
    Returns:
        JSON response with search results
    """
    # Get and validate query parameter
    query = request.GET.get('query', '').strip()
    
    if not query:
        raise ValidationError('Query parameter is required')
    
    if len(query) < 2:
        raise ValidationError('Query must be at least 2 characters')
    
    if len(query) > 100:
        raise ValidationError('Query must be at most 100 characters')
    
    # Sanitize query
    query = sanitize_string(query, max_length=100)
    
    # Use CoinGecko's search endpoint
    coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/search"
    params = {'query': query}
    
    response = requests.get(
        coingecko_url,
        params=params,
        timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
    )
    response.raise_for_status()
    
    data = response.json()
    coins = data.get('coins', [])[:20]  # Limit to top 20 results
    
    results = [
        {
            'id': coin.get('id'),
            'name': coin.get('name'),
            'symbol': coin.get('symbol', '').upper(),
            'market_cap_rank': coin.get('market_cap_rank'),
            'thumb': coin.get('thumb'),
            'large': coin.get('large')
        }
        for coin in coins
    ]
    
    result = {
        'query': query,
        'results': results,
        'count': len(results)
    }
    
    return json_response_with_timestamp(result)


# ========== Watchlist Endpoints ==========

@csrf_exempt
@require_http_methods(["GET"])
@rate_limit(max_requests=120, window_seconds=60)  # 120 requests per minute
@handle_api_errors
@cached(timeout=30, key_prefix="watchlist")  # Cache for 30 seconds
def get_watchlist(request: HttpRequest) -> JsonResponse:
    """
    Get all cryptocurrencies in the watchlist with current prices
    
    Args:
        request: HTTP request with optional filter parameters
    
    Returns:
        JSON response with watchlist items and current prices
    """
    # Apply filters
    queryset = WatchlistItem.objects.all()
    
    # Filter by favorite if requested
    if request.GET.get('favorite') == 'true':
        queryset = queryset.filter(is_favorite=True)
    
    watchlist_items = list(queryset)
    
    # Get current prices for all watchlist items
    coin_ids = [item.coin_id for item in watchlist_items]
    
    prices_data = {}
    if coin_ids:
        # Batch fetch prices from CoinGecko
        coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        try:
            response = requests.get(
                coingecko_url,
                params=params,
                timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
            )
            response.raise_for_status()
            prices_data = response.json()
        except RequestException as e:
            logger.warning(f"Failed to fetch prices for watchlist: {e}")
            # Continue with empty prices_data
    
    results = []
    for item in watchlist_items:
        price_info = prices_data.get(item.coin_id, {})
        results.append({
            'id': item.coin_id,
            'name': item.coin_name,
            'symbol': item.coin_symbol.upper(),
            'added_at': item.added_at.isoformat(),
            'current_price_usd': price_info.get('usd'),
            'price_change_24h_percent': price_info.get('usd_24h_change'),
            'market_cap_usd': price_info.get('usd_market_cap'),
            'volume_24h_usd': price_info.get('usd_24h_vol'),
            'last_price': float(item.last_price) if item.last_price else None,
            'last_updated': item.last_updated.isoformat(),
            'is_favorite': item.is_favorite,
            'alert_enabled': item.alert_enabled
        })
    
    result = {
        'watchlist': results,
        'count': len(results)
    }
    
    return json_response_with_timestamp(result)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit(max_requests=30, window_seconds=60)  # 30 requests per minute
@handle_api_errors
def add_to_watchlist(request: HttpRequest) -> JsonResponse:
    """
    Add a cryptocurrency to the watchlist
    
    Args:
        request: HTTP request with JSON body containing coin information
    
    Returns:
        JSON response confirming addition
    """
    # Parse and validate request body
    try:
        data = json_lib.loads(request.body)
    except json_lib.JSONDecodeError:
        raise ValidationError('Invalid JSON in request body')
    
    # Validate required fields
    coin_id = data.get('coin_id', '').strip()
    coin_name = data.get('coin_name', '').strip()
    coin_symbol = data.get('coin_symbol', '').strip()
    
    if not all([coin_id, coin_name, coin_symbol]):
        raise ValidationError('coin_id, coin_name, and coin_symbol are required')
    
    # Validate and sanitize inputs
    coin_id = validate_coin_id(coin_id)
    coin_symbol = validate_symbol(coin_symbol)
    coin_name = sanitize_string(coin_name, max_length=200)
    
    # Optional fields
    is_favorite = data.get('is_favorite', False)
    alert_enabled = data.get('alert_enabled', False)
    description = sanitize_string(data.get('description', ''), max_length=5000)
    website_url = sanitize_string(data.get('website_url', ''), max_length=500)
    image_url = sanitize_string(data.get('image_url', ''), max_length=500)
    
    # Check if already in watchlist
    if WatchlistItem.objects.filter(coin_id=coin_id).exists():
        raise ValidationError(f'{coin_name} is already in your watchlist')
    
    # Get current price and metadata
    current_price = None
    market_cap = None
    volume_24h = None
    price_change_24h = None
    
    try:
        coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        response = requests.get(
            coingecko_url,
            params=params,
            timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
        )
        response.raise_for_status()
        price_data = response.json()
        
        if coin_id in price_data:
            coin_data = price_data[coin_id]
            current_price = Decimal(str(coin_data.get('usd', 0)))
            market_cap = Decimal(str(coin_data.get('usd_market_cap', 0))) if coin_data.get('usd_market_cap') else None
            volume_24h = Decimal(str(coin_data.get('usd_24h_vol', 0))) if coin_data.get('usd_24h_vol') else None
            price_change_24h = Decimal(str(coin_data.get('usd_24h_change', 0))) if coin_data.get('usd_24h_change') else None
    except RequestException as e:
        logger.warning(f"Failed to fetch initial price for {coin_id}: {e}")
        # Continue without price data
    
    # Add to watchlist
    item = WatchlistItem.objects.create(
        coin_id=coin_id,
        coin_name=coin_name,
        coin_symbol=coin_symbol,
        last_price=current_price,
        market_cap=market_cap,
        volume_24h=volume_24h,
        price_change_24h=price_change_24h,
        is_favorite=is_favorite,
        alert_enabled=alert_enabled,
        description=description,
        website_url=website_url,
        image_url=image_url
    )
    
    result = {
        'success': True,
        'message': f'{coin_name} added to watchlist',
        'item': {
            'id': item.coin_id,
            'name': item.coin_name,
            'symbol': item.coin_symbol.upper(),
            'added_at': item.added_at.isoformat(),
            'current_price_usd': float(current_price) if current_price else None,
            'is_favorite': item.is_favorite
        }
    }
    
    return json_response_with_timestamp(result, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
@rate_limit(max_requests=60, window_seconds=60)  # 60 requests per minute
@handle_api_errors
def remove_from_watchlist(request: HttpRequest, coin_id: str) -> JsonResponse:
    """
    Remove a cryptocurrency from the watchlist
    
    Args:
        request: HTTP request
        coin_id: Cryptocurrency ID to remove
    
    Returns:
        JSON response confirming removal
    """
    # Validate coin_id
    coin_id = validate_coin_id(coin_id)
    
    try:
        item = WatchlistItem.objects.get(coin_id=coin_id)
        coin_name = item.coin_name
        item.delete()
        
        result = {
            'success': True,
            'message': f'{coin_name} removed from watchlist'
        }
        
        return json_response_with_timestamp(result)
    
    except WatchlistItem.DoesNotExist:
        raise NotFoundError('Cryptocurrency not found in watchlist')


@csrf_exempt
@require_http_methods(["PATCH"])
@rate_limit(max_requests=60, window_seconds=60)  # 60 requests per minute
@handle_api_errors
def update_watchlist_item(request: HttpRequest, coin_id: str) -> JsonResponse:
    """
    Update watchlist item preferences
    
    Args:
        request: HTTP request with JSON body
        coin_id: Cryptocurrency ID to update
    
    Returns:
        JSON response with updated item
    """
    # Validate coin_id
    coin_id = validate_coin_id(coin_id)
    
    try:
        item = WatchlistItem.objects.get(coin_id=coin_id)
    except WatchlistItem.DoesNotExist:
        raise NotFoundError('Cryptocurrency not found in watchlist')
    
    # Parse request body
    try:
        data = json_lib.loads(request.body)
    except json_lib.JSONDecodeError:
        raise ValidationError('Invalid JSON in request body')
    
    # Update allowed fields
    if 'is_favorite' in data:
        item.is_favorite = bool(data['is_favorite'])
    
    if 'alert_enabled' in data:
        item.alert_enabled = bool(data['alert_enabled'])
    
    if 'alert_price_threshold' in data:
        threshold = data['alert_price_threshold']
        if threshold is not None:
            item.alert_price_threshold = validate_decimal(threshold, 'alert_price_threshold')
        else:
            item.alert_price_threshold = None
    
    if 'description' in data:
        item.description = sanitize_string(data['description'], max_length=5000)
    
    item.save()
    
    result = {
        'success': True,
        'message': f'{item.coin_name} updated',
        'item': {
            'id': item.coin_id,
            'name': item.coin_name,
            'symbol': item.coin_symbol.upper(),
            'is_favorite': item.is_favorite,
            'alert_enabled': item.alert_enabled,
            'alert_price_threshold': float(item.alert_price_threshold) if item.alert_price_threshold else None
        }
    }
    
    return json_response_with_timestamp(result)


# ========== Dashboard View ==========

def dashboard(request: HttpRequest) -> JsonResponse:
    """Render the main dashboard page"""
    return render(request, 'dashboard.html')
