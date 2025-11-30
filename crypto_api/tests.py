import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from .models import WatchlistItem
from .utils import InMemoryCache, RateLimiter


class WatchlistItemModelTest(TestCase):
    """Test WatchlistItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.item = WatchlistItem.objects.create(
            coin_id='bitcoin',
            coin_name='Bitcoin',
            coin_symbol='BTC',
            last_price=Decimal('50000.00'),
            market_cap=Decimal('1000000000000'),
            volume_24h=Decimal('50000000000'),
            price_change_24h=Decimal('2.5'),
            is_favorite=True
        )
    
    def test_model_creation(self):
        """Test model can be created"""
        self.assertEqual(self.item.coin_id, 'bitcoin')
        self.assertEqual(self.item.coin_name, 'Bitcoin')
        self.assertEqual(self.item.coin_symbol, 'BTC')
        self.assertTrue(self.item.is_favorite)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.item), 'Bitcoin (BTC)')
    
    def test_get_price_change_percentage(self):
        """Test price change percentage method"""
        self.assertEqual(self.item.get_price_change_percentage(), 2.5)
    
    def test_update_price_data(self):
        """Test update price data method"""
        new_price = Decimal('51000.00')
        self.item.update_price_data(price=new_price)
        self.item.refresh_from_db()
        self.assertEqual(self.item.last_price, new_price)


class HealthCheckViewTest(TestCase):
    """Test health check endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    @patch('crypto_api.views.requests.get')
    def test_health_check_success(self, mock_get):
        """Test health check returns healthy status"""
        # Mock external API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response = self.client.get(reverse('crypto_api:health_check'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('version', data)
        self.assertIn('components', data)
    
    def test_readiness_check(self):
        """Test readiness check"""
        response = self.client.get(reverse('crypto_api:readiness_check'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ready')
    
    def test_liveness_check(self):
        """Test liveness check"""
        response = self.client.get(reverse('crypto_api:liveness_check'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'alive')


class WatchlistViewTest(TestCase):
    """Test watchlist endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.item = WatchlistItem.objects.create(
            coin_id='bitcoin',
            coin_name='Bitcoin',
            coin_symbol='BTC',
            last_price=Decimal('50000.00')
        )
    
    @patch('crypto_api.views.requests.get')
    def test_get_watchlist(self, mock_get):
        """Test get watchlist endpoint"""
        # Mock CoinGecko API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'bitcoin': {
                'usd': 50000,
                'usd_24h_change': 2.5,
                'usd_market_cap': 1000000000000,
                'usd_24h_vol': 50000000000
            }
        }
        mock_get.return_value = mock_response
        
        response = self.client.get(reverse('crypto_api:get_watchlist'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('watchlist', data)
        self.assertEqual(data['count'], 1)
    
    @patch('crypto_api.views.requests.get')
    def test_add_to_watchlist(self, mock_get):
        """Test add to watchlist endpoint"""
        # Mock CoinGecko API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ethereum': {'usd': 3000}
        }
        mock_get.return_value = mock_response
        
        data = {
            'coin_id': 'ethereum',
            'coin_name': 'Ethereum',
            'coin_symbol': 'ETH'
        }
        
        response = self.client.post(
            reverse('crypto_api:add_to_watchlist'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Verify item was created
        self.assertTrue(WatchlistItem.objects.filter(coin_id='ethereum').exists())
    
    def test_add_duplicate_to_watchlist(self):
        """Test adding duplicate item returns error"""
        data = {
            'coin_id': 'bitcoin',
            'coin_name': 'Bitcoin',
            'coin_symbol': 'BTC'
        }
        
        response = self.client.post(
            reverse('crypto_api:add_to_watchlist'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
    
    def test_remove_from_watchlist(self):
        """Test remove from watchlist endpoint"""
        response = self.client.delete(
            reverse('crypto_api:remove_from_watchlist', kwargs={'coin_id': 'bitcoin'})
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Verify item was deleted
        self.assertFalse(WatchlistItem.objects.filter(coin_id='bitcoin').exists())
    
    def test_update_watchlist_item(self):
        """Test update watchlist item endpoint"""
        data = {
            'is_favorite': True,
            'alert_enabled': True
        }
        
        response = self.client.patch(
            reverse('crypto_api:update_watchlist_item', kwargs={'coin_id': 'bitcoin'}),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify item was updated
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_favorite)
        self.assertTrue(self.item.alert_enabled)


class ValidationTest(TestCase):
    """Test validation utilities"""
    
    def test_validate_coin_id(self):
        """Test coin ID validation"""
        from .utils import validate_coin_id
        
        # Valid coin IDs
        self.assertEqual(validate_coin_id('bitcoin'), 'bitcoin')
        self.assertEqual(validate_coin_id('BITCOIN'), 'bitcoin')
        
        # Invalid coin IDs
        with self.assertRaises(ValueError):
            validate_coin_id('')
        
        with self.assertRaises(ValueError):
            validate_coin_id('invalid@coin')
    
    def test_validate_symbol(self):
        """Test symbol validation"""
        from .utils import validate_symbol
        
        # Valid symbols
        self.assertEqual(validate_symbol('btc'), 'BTC')
        self.assertEqual(validate_symbol('BTC'), 'BTC')
        
        # Invalid symbols
        with self.assertRaises(ValueError):
            validate_symbol('')


class CachingTest(TestCase):
    """Test caching functionality"""
    
    def test_in_memory_cache(self):
        """Test in-memory cache"""
        cache = InMemoryCache()
        
        # Set and get value
        cache.set('test_key', 'test_value', timeout=60)
        self.assertEqual(cache.get('test_key'), 'test_value')
        
        # Test expiry
        cache.set('expired_key', 'value', timeout=0)
        self.assertIsNone(cache.get('expired_key'))
        
        # Test delete
        cache.delete('test_key')
        self.assertIsNone(cache.get('test_key'))
        
        # Test clear
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.clear()
        self.assertIsNone(cache.get('key1'))
        self.assertIsNone(cache.get('key2'))


class RateLimitingTest(TestCase):
    """Test rate limiting functionality"""
    
    def test_rate_limiter(self):
        """Test rate limiter"""
        limiter = RateLimiter()
        
        # Test within limit
        for i in range(10):
            self.assertTrue(limiter.is_allowed('test_client', max_requests=10, window_seconds=60))
        
        # Test over limit
        self.assertFalse(limiter.is_allowed('test_client', max_requests=10, window_seconds=60))
        
        # Test remaining
        limiter.reset('test_client')
        remaining = limiter.get_remaining('test_client', max_requests=10, window_seconds=60)
        self.assertEqual(remaining, 10)

