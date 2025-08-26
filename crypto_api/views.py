import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
import requests
import time

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint for AWS load balancer
    """
    try:
        # Basic health checks
        status = {
            'status': 'healthy',
            'timestamp': int(time.time()),
            'version': '1.0.0',
            'components': {
                'database': 'ok',
                'external_apis': 'ok'
            }
        }
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] != 1:
                status['components']['database'] = 'error'
                status['status'] = 'unhealthy'
        
        # Test external API connectivity (CoinGecko)
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
        return JsonResponse(status, status=http_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': int(time.time())
        }, status=503)


def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes/ECS
    """
    try:
        # Check if the application is ready to serve traffic
        from django.db import connection
        connection.ensure_connection()
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': int(time.time())
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': int(time.time())
        }, status=503)


def liveness_check(request):
    """
    Liveness check endpoint for Kubernetes/ECS
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': int(time.time())
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_crypto_price(request, symbol):
    """
    Get current price for a cryptocurrency
    """
    try:
        # Fetch price from CoinGecko
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
            'price_change_24h_percent': crypto_data.get('usd_24h_change'),
            'timestamp': int(time.time())
        }
        
        return JsonResponse(result)
        
    except requests.RequestException as e:
        logger.error(f"API request failed for {symbol}: {e}")
        return JsonResponse({
            'error': 'External API unavailable',
            'symbol': symbol
        }, status=503)
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'symbol': symbol
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_crypto_history(request, symbol):
    """
    Get historical price data for a cryptocurrency
    """
    try:
        days = int(request.GET.get('days', 30))
        if days > 365:
            days = 365  # Limit to 1 year
        
        # Fetch historical data from CoinGecko
        coingecko_url = f"{settings.CRYPTO_API_SETTINGS['COINGECKO_API_URL']}/coins/{symbol.lower()}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days
        }
        
        response = requests.get(
            coingecko_url,
            params=params,
            timeout=settings.CRYPTO_API_SETTINGS['REQUEST_TIMEOUT']
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Format data for easier consumption
        prices = []
        for timestamp, price in data.get('prices', []):
            prices.append({
                'timestamp': int(timestamp / 1000),  # Convert to seconds
                'price': price
            })
        
        result = {
            'symbol': symbol.upper(),
            'days': days,
            'data_points': len(prices),
            'prices': prices,
            'timestamp': int(time.time())
        }
        
        return JsonResponse(result)
        
    except requests.RequestException as e:
        logger.error(f"API request failed for {symbol} history: {e}")
        return JsonResponse({
            'error': 'External API unavailable',
            'symbol': symbol
        }, status=503)
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'symbol': symbol
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_market_overview(request):
    """
    Get market overview with top cryptocurrencies
    """
    try:
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
        
        market_data = []
        for coin in data:
            market_data.append({
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name'),
                'price_usd': coin.get('current_price'),
                'market_cap_usd': coin.get('market_cap'),
                'volume_24h_usd': coin.get('total_volume'),
                'price_change_24h_percent': coin.get('price_change_percentage_24h'),
                'market_cap_rank': coin.get('market_cap_rank')
            })
        
        result = {
            'market_overview': market_data,
            'total_cryptocurrencies': len(market_data),
            'timestamp': int(time.time())
        }
        
        return JsonResponse(result)
        
    except requests.RequestException as e:
        logger.error(f"API request failed for market overview: {e}")
        return JsonResponse({
            'error': 'External API unavailable'
        }, status=503)
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)
