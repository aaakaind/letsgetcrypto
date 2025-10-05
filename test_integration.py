#!/usr/bin/env python3
"""
Integration test to verify MCP server and streamlined API code
"""

import sys


def test_mcp_server():
    """Test MCP server can be imported and configured"""
    print("Testing MCP Server Integration...")
    try:
        import mcp_server
        
        # Test configuration
        config = mcp_server.CryptoAPIConfig(
            base_url='http://localhost:8000',
            timeout=30
        )
        
        assert config.base_url == 'http://localhost:8000'
        assert config.timeout == 30
        
        print("  ✓ MCP server module imports successfully")
        print("  ✓ CryptoAPIConfig works correctly")
        return True
    except Exception as e:
        print(f"  ✗ MCP server test failed: {e}")
        return False


def test_views_syntax():
    """Test that views.py has valid syntax"""
    print("\nTesting Views Module...")
    try:
        import py_compile
        py_compile.compile('crypto_api/views.py', doraise=True)
        print("  ✓ views.py syntax is valid")
        return True
    except Exception as e:
        print(f"  ✗ views.py syntax check failed: {e}")
        return False


def test_mcp_config():
    """Test MCP configuration file is valid JSON"""
    print("\nTesting MCP Configuration...")
    try:
        import json
        with open('mcp-config.json', 'r') as f:
            config = json.load(f)
        
        assert 'mcpServers' in config
        assert 'letsgetcrypto' in config['mcpServers']
        
        server_config = config['mcpServers']['letsgetcrypto']
        assert 'command' in server_config
        assert 'args' in server_config
        assert server_config['command'] == 'python'
        
        print("  ✓ mcp-config.json is valid")
        print(f"  ✓ Contains {len(server_config.get('tools', []))} tool definitions")
        return True
    except Exception as e:
        print(f"  ✗ MCP config test failed: {e}")
        return False


def test_requirements():
    """Test that requirements.txt includes MCP"""
    print("\nTesting Requirements...")
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        assert 'mcp' in requirements.lower()
        print("  ✓ requirements.txt includes MCP package")
        return True
    except Exception as e:
        print(f"  ✗ Requirements test failed: {e}")
        return False


def test_documentation():
    """Test that documentation files exist"""
    print("\nTesting Documentation...")
    try:
        import os
        
        docs = {
            'MCP_SERVER.md': 'MCP Server documentation',
            'AWS_DEPLOYMENT.md': 'AWS Deployment guide',
            'README.md': 'Main README'
        }
        
        for doc_file, description in docs.items():
            if not os.path.exists(doc_file):
                print(f"  ✗ Missing {description}: {doc_file}")
                return False
            print(f"  ✓ {description} exists")
        
        return True
    except Exception as e:
        print(f"  ✗ Documentation test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("LetsGetCrypto Integration Tests")
    print("=" * 60)
    
    tests = [
        test_mcp_server,
        test_views_syntax,
        test_mcp_config,
        test_requirements,
        test_documentation
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Error running test {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
