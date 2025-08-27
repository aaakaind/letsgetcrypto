#!/usr/bin/env python3
"""
Test script to validate AWS deployment readiness for LetsGetCrypto
"""

import os
import sys
import requests
import time
import subprocess
import json
from urllib.parse import urljoin

class AWSDeploymentTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("🔍 Testing health check endpoint...")
        try:
            url = urljoin(self.base_url, "/api/health/")
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if data.get('status') not in ['healthy', 'degraded']:
                print(f"❌ Health check status is: {data.get('status')}")
                return False
            
            print(f"✅ Health check passed: {data.get('status')}")
            return True
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_readiness_endpoint(self):
        """Test readiness check endpoint"""
        print("🔍 Testing readiness endpoint...")
        try:
            url = urljoin(self.base_url, "/api/readiness/")
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Readiness check failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if data.get('status') != 'ready':
                print(f"❌ Readiness status is: {data.get('status')}")
                return False
            
            print("✅ Readiness check passed")
            return True
        except Exception as e:
            print(f"❌ Readiness check error: {e}")
            return False

    def test_liveness_endpoint(self):
        """Test liveness check endpoint"""
        print("🔍 Testing liveness endpoint...")
        try:
            url = urljoin(self.base_url, "/api/liveness/")
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Liveness check failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if data.get('status') != 'alive':
                print(f"❌ Liveness status is: {data.get('status')}")
                return False
            
            print("✅ Liveness check passed")
            return True
        except Exception as e:
            print(f"❌ Liveness check error: {e}")
            return False

    def test_api_endpoints(self):
        """Test main API endpoints"""
        print("🔍 Testing API endpoints...")
        
        # Test root endpoint
        try:
            response = self.session.get(self.base_url + "/")
            if response.status_code != 200:
                print(f"❌ Root endpoint failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if 'message' not in data or 'endpoints' not in data:
                print("❌ Root endpoint response invalid")
                return False
            
            print("✅ Root endpoint passed")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False

        # Test crypto price endpoint (should handle external API failures gracefully)
        try:
            url = urljoin(self.base_url, "/api/price/bitcoin/")
            response = self.session.get(url)
            
            # Should return either success or graceful error
            if response.status_code not in [200, 503]:
                print(f"❌ Crypto price endpoint failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if response.status_code == 200:
                if 'symbol' not in data or 'price_usd' not in data:
                    print("❌ Crypto price response invalid")
                    return False
                print("✅ Crypto price endpoint passed (external API available)")
            else:
                if 'error' not in data:
                    print("❌ Crypto price error response invalid")
                    return False
                print("✅ Crypto price endpoint passed (graceful error handling)")
            
        except Exception as e:
            print(f"❌ Crypto price endpoint error: {e}")
            return False

        return True

    def test_database_connectivity(self):
        """Test database connectivity through health endpoint"""
        print("🔍 Testing database connectivity...")
        try:
            url = urljoin(self.base_url, "/api/health/")
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Cannot check database: HTTP {response.status_code}")
                return False
            
            data = response.json()
            db_status = data.get('components', {}).get('database', 'unknown')
            
            if db_status == 'ok':
                print("✅ Database connectivity passed")
                return True
            else:
                print(f"❌ Database status is: {db_status}")
                return False
        except Exception as e:
            print(f"❌ Database connectivity error: {e}")
            return False

    def test_security_headers(self):
        """Test security headers for production deployment"""
        print("🔍 Testing security configuration...")
        try:
            response = self.session.get(self.base_url + "/")
            headers = response.headers
            
            # Check for security headers (when not in debug mode)
            security_score = 0
            total_checks = 4
            
            if 'X-Content-Type-Options' in headers:
                print("✅ X-Content-Type-Options header present")
                security_score += 1
            else:
                print("⚠️ X-Content-Type-Options header missing")
            
            if 'X-Frame-Options' in headers:
                print("✅ X-Frame-Options header present")
                security_score += 1
            else:
                print("⚠️ X-Frame-Options header missing")
            
            if 'Strict-Transport-Security' in headers:
                print("✅ HSTS header present")
                security_score += 1
            else:
                print("ℹ️ HSTS header not present (normal for HTTP)")
                security_score += 1  # Don't penalize for HTTP in development
            
            if 'Server' not in headers or 'gunicorn' not in headers.get('Server', '').lower():
                print("✅ Server header appropriately configured")
                security_score += 1
            else:
                print("⚠️ Server header exposes technology stack")
            
            if security_score >= total_checks * 0.75:
                print(f"✅ Security configuration passed ({security_score}/{total_checks})")
                return True
            else:
                print(f"⚠️ Security configuration needs improvement ({security_score}/{total_checks})")
                return False
                
        except Exception as e:
            print(f"❌ Security check error: {e}")
            return False

    def test_performance(self):
        """Test basic performance characteristics"""
        print("🔍 Testing performance...")
        try:
            # Test response times for health check
            start_time = time.time()
            url = urljoin(self.base_url, "/api/health/")
            response = self.session.get(url)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                print(f"❌ Performance test failed: HTTP {response.status_code}")
                return False
            
            if response_time > 5.0:
                print(f"⚠️ Health check response time is slow: {response_time:.2f}s")
                return False
            
            print(f"✅ Performance check passed: {response_time:.2f}s response time")
            return True
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False

    def run_all_tests(self):
        """Run all AWS deployment readiness tests"""
        print("🚀 Starting AWS Deployment Readiness Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Readiness Check", self.test_readiness_endpoint),
            ("Liveness Check", self.test_liveness_endpoint),
            ("API Endpoints", self.test_api_endpoints),
            ("Database Connectivity", self.test_database_connectivity),
            ("Security Configuration", self.test_security_headers),
            ("Performance", self.test_performance),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready for AWS deployment.")
            return True
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed. Review failures before AWS deployment.")
            return False
        else:
            print("❌ Multiple tests failed. Fix issues before AWS deployment.")
            return False


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test AWS deployment readiness')
    parser.add_argument('--url', default='http://localhost:8000',
                        help='Base URL to test (default: http://localhost:8000)')
    parser.add_argument('--wait', type=int, default=0,
                        help='Wait seconds before starting tests')
    
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"⏳ Waiting {args.wait} seconds before starting tests...")
        time.sleep(args.wait)
    
    tester = AWSDeploymentTester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()