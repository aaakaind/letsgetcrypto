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


def dashboard(request):
    """Render the main dashboard page"""
    return render(request, 'dashboard.html')
