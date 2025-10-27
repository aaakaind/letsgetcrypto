import logging
import time
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import connection
import requests

logger = logging.getLogger(__name__)


def handle_api_errors(func):
    """Decorator to handle common API errors"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"API request failed in {func.__name__}: {e}")
            return JsonResponse({
                'error': 'External API unavailable'
            }, status=503)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return JsonResponse({
                'error': 'Internal server error'
            }, status=500)
    return wrapper


def json_response_with_timestamp(data, status=200):
    """Create a JSON response with timestamp"""
    data['timestamp'] = int(time.time())
    return JsonResponse(data, status=status)


def health_check(request):
    """Health check endpoint for AWS load balancer"""
    try:
        status = {
            'status': 'healthy',
            'version': '1.0.0',
            'components': {
                'database': 'ok',
                'external_apis': 'ok'
            }
        }
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone()[0] != 1:
                status['components']['database'] = 'error'
                status['status'] = 'unhealthy'
        
        # Test external API connectivity
        try:
            response = requests.get(
                f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/ping",
                timeout=5
            )
            if response.status_code != 200:
                status['components']['external_apis'] = 'degraded'
        except Exception as e:
            logger.warning(f"External API check failed: {e}")
            status['components']['external_apis'] = 'degraded'
        
        http_status = 200 if status['status'] == 'healthy' else 503
        return json_response_with_timestamp(status, http_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return json_response_with_timestamp({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)


def readiness_check(request):
    """Readiness check endpoint for Kubernetes/ECS"""
    try:
        connection.ensure_connection()
        return json_response_with_timestamp({'status': 'ready'})
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return json_response_with_timestamp({
            'status': 'not_ready',
            'error': str(e)
        }, status=503)


def liveness_check(request):
    """Liveness check endpoint for Kubernetes/ECS"""
    return json_response_with_timestamp({'status': 'alive'})


@csrf_exempt
@require_http_methods(["GET"])
@handle_api_errors
def get_crypto_price(request, symbol):
    """Get current price for a cryptocurrency"""
    coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/simple/price"
    params = {
        'ids': symbol.lower(),
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
    if symbol.lower() not in data:
        return JsonResponse({
            'error': f'Cryptocurrency {symbol} not found'
        }, status=404)
    
    crypto_data = data[symbol.lower()]
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
@handle_api_errors
def get_crypto_history(request, symbol):
    """Get historical price data for a cryptocurrency"""
    days = min(int(request.GET.get('days', 30)), 365)  # Limit to 1 year
    
    coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/coins/{symbol.lower()}/market_chart"
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
@handle_api_errors
def get_market_overview(request):
    """Get market overview with top cryptocurrencies"""
    limit = min(int(request.GET.get('limit', 10)), 50)  # Max 50
    
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
@handle_api_errors
def search_crypto(request):
    """Search for cryptocurrencies by name or symbol"""
    query = request.GET.get('query', '').strip()
    
    if not query:
        return JsonResponse({
            'error': 'Query parameter is required'
        }, status=400)
    
    if len(query) < 2:
        return JsonResponse({
            'error': 'Query must be at least 2 characters'
        }, status=400)
    
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


@csrf_exempt
@require_http_methods(["GET"])
@handle_api_errors
def get_watchlist(request):
    """Get all cryptocurrencies in the watchlist"""
    from .models import WatchlistItem
    
    watchlist_items = WatchlistItem.objects.all()
    
    # Get current prices for all watchlist items
    coin_ids = [item.coin_id for item in watchlist_items]
    
    if coin_ids:
        # Batch fetch prices from CoinGecko
        coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        try:
            response = requests.get(
                coingecko_url,
                params=params,
                timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
            )
            response.raise_for_status()
            prices_data = response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch prices for watchlist: {e}")
            prices_data = {}
    else:
        prices_data = {}
    
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
            'last_price': float(item.last_price) if item.last_price else None,
            'last_updated': item.last_updated.isoformat()
        })
    
    result = {
        'watchlist': results,
        'count': len(results)
    }
    
    return json_response_with_timestamp(result)


@csrf_exempt
@require_http_methods(["POST"])
@handle_api_errors
def add_to_watchlist(request):
    """Add a cryptocurrency to the watchlist"""
    import json as json_lib
    from .models import WatchlistItem
    
    try:
        data = json_lib.loads(request.body)
    except json_lib.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    coin_id = data.get('coin_id', '').strip()
    coin_name = data.get('coin_name', '').strip()
    coin_symbol = data.get('coin_symbol', '').strip()
    
    if not all([coin_id, coin_name, coin_symbol]):
        return JsonResponse({
            'error': 'coin_id, coin_name, and coin_symbol are required'
        }, status=400)
    
    # Check if already in watchlist
    if WatchlistItem.objects.filter(coin_id=coin_id).exists():
        return JsonResponse({
            'error': f'{coin_name} is already in your watchlist'
        }, status=409)
    
    # Get current price
    try:
        coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd'
        }
        response = requests.get(
            coingecko_url,
            params=params,
            timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
        )
        response.raise_for_status()
        price_data = response.json()
        current_price = price_data.get(coin_id, {}).get('usd')
    except Exception as e:
        logger.warning(f"Failed to fetch initial price: {e}")
        current_price = None
    
    # Add to watchlist
    item = WatchlistItem.objects.create(
        coin_id=coin_id,
        coin_name=coin_name,
        coin_symbol=coin_symbol,
        last_price=current_price
    )
    
    result = {
        'success': True,
        'message': f'{coin_name} added to watchlist',
        'item': {
            'id': item.coin_id,
            'name': item.coin_name,
            'symbol': item.coin_symbol.upper(),
            'added_at': item.added_at.isoformat()
        }
    }
    
    return json_response_with_timestamp(result, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
@handle_api_errors
def remove_from_watchlist(request, coin_id):
    """Remove a cryptocurrency from the watchlist"""
    from .models import WatchlistItem
    
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
        return JsonResponse({
            'error': 'Cryptocurrency not found in watchlist'
        }, status=404)


def dashboard(request):
    """Render the main dashboard page"""
    return render(request, 'dashboard.html')
