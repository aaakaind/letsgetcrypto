#!/usr/bin/env python3
"""
Test suite for cryptocurrency search and watchlist features
"""

import sys
import os
import json
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letsgetcrypto_django.settings')
django.setup()

# Now import Django models after setup
from django.test import TestCase, Client
from crypto_api.models import WatchlistItem


class SearchAPITest(TestCase):
    """Test cases for cryptocurrency search API"""
    
    def setUp(self):
        self.client = Client()
    
    def test_search_valid_query(self):
        """Test searching with a valid query"""
        print("Testing search with valid query...")
        response = self.client.get('/api/search/', {'query': 'bitcoin'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('query', data)
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertEqual(data['query'], 'bitcoin')
        self.assertGreater(data['count'], 0)
        
        print(f"  ✓ Search returned {data['count']} results")
    
    def test_search_empty_query(self):
        """Test searching with empty query"""
        print("Testing search with empty query...")
        response = self.client.get('/api/search/', {'query': ''})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        
        print("  ✓ Empty query correctly rejected")
    
    def test_search_short_query(self):
        """Test searching with query less than 2 characters"""
        print("Testing search with short query...")
        response = self.client.get('/api/search/', {'query': 'b'})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        
        print("  ✓ Short query correctly rejected")
    
    def test_search_no_query_param(self):
        """Test searching without query parameter"""
        print("Testing search without query parameter...")
        response = self.client.get('/api/search/')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        
        print("  ✓ Missing query parameter correctly rejected")


class WatchlistAPITest(TestCase):
    """Test cases for watchlist API"""
    
    def setUp(self):
        self.client = Client()
        # Clean up any existing watchlist items
        WatchlistItem.objects.all().delete()
    
    def test_get_empty_watchlist(self):
        """Test getting empty watchlist"""
        print("Testing get empty watchlist...")
        response = self.client.get('/api/watchlist/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('watchlist', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['watchlist']), 0)
        
        print("  ✓ Empty watchlist returned correctly")
    
    def test_add_to_watchlist(self):
        """Test adding cryptocurrency to watchlist"""
        print("Testing add to watchlist...")
        
        payload = {
            'coin_id': 'bitcoin',
            'coin_name': 'Bitcoin',
            'coin_symbol': 'BTC'
        }
        
        response = self.client.post(
            '/api/watchlist/add/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertTrue(data.get('success'))
        self.assertIn('item', data)
        self.assertEqual(data['item']['id'], 'bitcoin')
        
        # Verify it's in the database
        self.assertEqual(WatchlistItem.objects.count(), 1)
        item = WatchlistItem.objects.first()
        self.assertEqual(item.coin_id, 'bitcoin')
        self.assertEqual(item.coin_name, 'Bitcoin')
        self.assertEqual(item.coin_symbol, 'BTC')
        
        print("  ✓ Cryptocurrency added to watchlist successfully")
    
    def test_add_duplicate_to_watchlist(self):
        """Test adding duplicate cryptocurrency to watchlist"""
        print("Testing add duplicate to watchlist...")
        
        # Add first time
        WatchlistItem.objects.create(
            coin_id='ethereum',
            coin_name='Ethereum',
            coin_symbol='ETH'
        )
        
        # Try to add again
        payload = {
            'coin_id': 'ethereum',
            'coin_name': 'Ethereum',
            'coin_symbol': 'ETH'
        }
        
        response = self.client.post(
            '/api/watchlist/add/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertIn('error', data)
        
        # Verify still only one item
        self.assertEqual(WatchlistItem.objects.count(), 1)
        
        print("  ✓ Duplicate correctly rejected")
    
    def test_add_invalid_payload(self):
        """Test adding with invalid payload"""
        print("Testing add with invalid payload...")
        
        payload = {
            'coin_id': 'bitcoin'
            # Missing coin_name and coin_symbol
        }
        
        response = self.client.post(
            '/api/watchlist/add/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        
        print("  ✓ Invalid payload correctly rejected")
    
    def test_get_watchlist_with_items(self):
        """Test getting watchlist with items"""
        print("Testing get watchlist with items...")
        
        # Add some items
        WatchlistItem.objects.create(
            coin_id='bitcoin',
            coin_name='Bitcoin',
            coin_symbol='BTC'
        )
        WatchlistItem.objects.create(
            coin_id='ethereum',
            coin_name='Ethereum',
            coin_symbol='ETH'
        )
        
        response = self.client.get('/api/watchlist/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['watchlist']), 2)
        
        # Check structure of returned items
        item = data['watchlist'][0]
        self.assertIn('id', item)
        self.assertIn('name', item)
        self.assertIn('symbol', item)
        self.assertIn('added_at', item)
        self.assertIn('current_price_usd', item)
        
        print("  ✓ Watchlist with items returned correctly")
    
    def test_remove_from_watchlist(self):
        """Test removing cryptocurrency from watchlist"""
        print("Testing remove from watchlist...")
        
        # Add item first
        WatchlistItem.objects.create(
            coin_id='cardano',
            coin_name='Cardano',
            coin_symbol='ADA'
        )
        
        response = self.client.delete('/api/watchlist/remove/cardano/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        
        # Verify it's removed from database
        self.assertEqual(WatchlistItem.objects.count(), 0)
        
        print("  ✓ Cryptocurrency removed from watchlist successfully")
    
    def test_remove_nonexistent_from_watchlist(self):
        """Test removing non-existent cryptocurrency from watchlist"""
        print("Testing remove non-existent from watchlist...")
        
        response = self.client.delete('/api/watchlist/remove/nonexistent/')
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
        
        print("  ✓ Non-existent item correctly handled")


class WatchlistModelTest(TestCase):
    """Test cases for WatchlistItem model"""
    
    def test_create_watchlist_item(self):
        """Test creating a watchlist item"""
        print("Testing create watchlist item...")
        
        item = WatchlistItem.objects.create(
            coin_id='solana',
            coin_name='Solana',
            coin_symbol='SOL'
        )
        
        self.assertEqual(item.coin_id, 'solana')
        self.assertEqual(item.coin_name, 'Solana')
        self.assertEqual(item.coin_symbol, 'SOL')
        self.assertIsNotNone(item.added_at)
        self.assertIsNotNone(item.last_updated)
        
        print("  ✓ Watchlist item created successfully")
    
    def test_watchlist_item_str(self):
        """Test string representation of watchlist item"""
        print("Testing watchlist item string representation...")
        
        item = WatchlistItem.objects.create(
            coin_id='polkadot',
            coin_name='Polkadot',
            coin_symbol='DOT'
        )
        
        expected = "Polkadot (DOT)"
        self.assertEqual(str(item), expected)
        
        print("  ✓ String representation correct")
    
    def test_watchlist_unique_constraint(self):
        """Test unique constraint on coin_id"""
        print("Testing unique constraint on coin_id...")
        
        WatchlistItem.objects.create(
            coin_id='ripple',
            coin_name='XRP',
            coin_symbol='XRP'
        )
        
        # Try to create another with same coin_id
        with self.assertRaises(Exception):
            WatchlistItem.objects.create(
                coin_id='ripple',
                coin_name='Ripple',
                coin_symbol='XRP'
            )
        
        print("  ✓ Unique constraint enforced")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "=" * 70)
    print("CRYPTOCURRENCY SEARCH AND WATCHLIST TEST SUITE")
    print("=" * 70)
    
    from django.test.runner import DiscoverRunner
    
    # Create test runner
    runner = DiscoverRunner(verbosity=1, interactive=False, keepdb=False)
    
    # Run tests using module name
    failures = runner.run_tests([__name__])
    
    print("\n" + "=" * 70)
    if failures == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {failures} TEST(S) FAILED")
    print("=" * 70)
    
    return failures


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
