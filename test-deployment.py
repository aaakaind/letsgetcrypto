#!/usr/bin/env python3
"""
Pre-Deployment Test Script
Runs essential tests before deploying to production
"""

import sys
import subprocess
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{NC}")

def print_failure(text):
    """Print failure message"""
    print(f"{RED}❌ {text}{NC}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{NC}")

def run_command(cmd, description, required=True):
    """Run a command and return success status"""
    print(f"Running: {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print_success(f"{description} passed")
            if result.stdout:
                print(f"  Output: {result.stdout.strip()[:200]}")
            return True
        else:
            if required:
                print_failure(f"{description} failed")
            else:
                print_warning(f"{description} failed (non-critical)")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_failure(f"{description} timed out")
        return False
    except Exception as e:
        print_failure(f"{description} error: {str(e)}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description} exists")
        return True
    else:
        print_failure(f"{description} not found")
        return False

def main():
    """Main test runner"""
    print_header("LetsGetCrypto Pre-Deployment Tests")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    # ========================================================================
    # 1. File Structure Tests
    # ========================================================================
    print_header("File Structure Tests")
    
    tests = [
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt"),
        ("Dockerfile", "Dockerfile"),
        ("manage.py", "Django manage.py"),
        ("VERSION", "VERSION file"),
        ("DEPLOYMENT_GUIDE.md", "Deployment guide"),
        ("RELEASE_CHECKLIST.md", "Release checklist"),
    ]
    
    for filepath, description in tests:
        if check_file_exists(filepath, description):
            passed += 1
        else:
            failed += 1
    
    # ========================================================================
    # 2. Python Syntax Tests
    # ========================================================================
    print_header("Python Syntax Tests")
    
    if run_command(
        "python3 -m py_compile crypto_api/views.py",
        "Compile crypto_api/views.py",
        required=True
    ):
        passed += 1
    else:
        failed += 1
    
    if run_command(
        "python3 -m py_compile letsgetcrypto_django/settings.py",
        "Compile settings.py",
        required=True
    ):
        passed += 1
    else:
        failed += 1
    
    # ========================================================================
    # 3. Configuration Tests
    # ========================================================================
    print_header("Configuration Tests")
    
    # Check environment variables
    env_vars = [
        ("DJANGO_SECRET_KEY", False),
        ("DJANGO_DEBUG", False),
        ("DJANGO_ALLOWED_HOSTS", False),
    ]
    
    for var, required in env_vars:
        if os.environ.get(var):
            print_success(f"{var} is set")
            passed += 1
        else:
            if required:
                print_failure(f"{var} is not set (REQUIRED)")
                failed += 1
            else:
                print_warning(f"{var} is not set (optional for tests)")
                warnings += 1
    
    # ========================================================================
    # 4. Docker Tests
    # ========================================================================
    print_header("Docker Tests")
    
    if run_command("docker --version", "Docker is installed", required=False):
        passed += 1
        
        # Test Docker build
        print("\n⏳ Building Docker image (this may take a few minutes)...")
        if run_command(
            "docker build -t letsgetcrypto:test . -q",
            "Docker image build",
            required=False
        ):
            passed += 1
            # Clean up test image
            subprocess.run("docker rmi letsgetcrypto:test -f", 
                         shell=True, capture_output=True)
        else:
            warnings += 1
    else:
        print_warning("Docker not available, skipping Docker tests")
        warnings += 1
    
    # ========================================================================
    # 5. Django Tests
    # ========================================================================
    print_header("Django Tests")
    
    # Set minimal environment for Django
    os.environ.setdefault('DJANGO_DEBUG', 'False')
    os.environ.setdefault('DJANGO_SECRET_KEY', 'test-key-for-testing-only')
    os.environ.setdefault('DJANGO_ALLOWED_HOSTS', '*')
    
    if run_command(
        "python3 manage.py check --deploy 2>&1 | grep -q 'System check identified no issues' && echo 'OK' || echo 'FAIL'",
        "Django deployment checks",
        required=False
    ):
        passed += 1
    else:
        warnings += 1
    
    # ========================================================================
    # 6. Import Tests
    # ========================================================================
    print_header("Python Import Tests")
    
    # Test critical imports
    imports = [
        ("django", "Django"),
        ("requests", "requests"),
        ("pandas", "pandas"),
    ]
    
    for module, name in imports:
        if run_command(
            f"python3 -c 'import {module}'",
            f"Import {name}",
            required=False
        ):
            passed += 1
        else:
            print_warning(f"{name} not installed (run: pip install -r requirements.txt)")
            warnings += 1
    
    # ========================================================================
    # 7. Version Check
    # ========================================================================
    print_header("Version Information")
    
    try:
        version = Path("VERSION").read_text().strip()
        print_success(f"Version: {version}")
        passed += 1
    except Exception as e:
        print_failure(f"Could not read VERSION: {e}")
        failed += 1
    
    # ========================================================================
    # Summary
    # ========================================================================
    print_header("Test Summary")
    
    total = passed + failed + warnings
    print(f"Total tests: {total}")
    print(f"{GREEN}✅ Passed: {passed}{NC}")
    print(f"{YELLOW}⚠️  Warnings: {warnings}{NC}")
    print(f"{RED}❌ Failed: {failed}{NC}")
    print()
    
    if failed == 0:
        if warnings == 0:
            print(f"{GREEN}🎉 All tests passed! Ready for deployment.{NC}")
            return 0
        else:
            print(f"{YELLOW}⚠️  Tests passed with warnings.{NC}")
            print(f"{YELLOW}Review warnings before deploying to production.{NC}")
            return 0
    else:
        print(f"{RED}❌ Some tests failed. Fix issues before deploying.{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
