#!/usr/bin/env python3
"""
Setup Validation Script
Tests that all components are properly configured for running from GitHub clone
"""

import sys
import os
import subprocess
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(msg):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{msg}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def check_python_version():
    """Check Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description} - OK")
        return True
    else:
        print_error(f"{description} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).is_dir():
        print_success(f"{description} - OK")
        return True
    else:
        print_warning(f"{description} - NOT FOUND (will be created)")
        return False

def check_import(module_name):
    """Check if a Python module can be imported"""
    try:
        __import__(module_name)
        print_success(f"{module_name} - Installed")
        return True
    except ImportError:
        print_warning(f"{module_name} - Not installed")
        return False

def main():
    print_header("LetsGetCrypto Setup Validation")
    
    all_checks = []
    
    # Check Python version
    print_header("1. Python Environment")
    all_checks.append(check_python_version())
    
    # Check essential files
    print_header("2. Essential Files")
    all_checks.append(check_file_exists("setup.sh", "Setup script"))
    all_checks.append(check_file_exists("init_ml_environment.sh", "ML initialization script"))
    all_checks.append(check_file_exists("run.sh", "Run script"))
    all_checks.append(check_file_exists("manage.py", "Django manage.py"))
    all_checks.append(check_file_exists("main.py", "Desktop GUI main.py"))
    all_checks.append(check_file_exists("requirements.txt", "Requirements file"))
    all_checks.append(check_file_exists(".env.example", "Environment template"))
    
    # Check documentation
    print_header("3. Documentation")
    all_checks.append(check_file_exists("README.md", "Main README"))
    all_checks.append(check_file_exists("GITHUB_CLONE_GUIDE.md", "GitHub Clone Guide"))
    all_checks.append(check_file_exists("GITHUB_PAGES_INTEGRATION.md", "GitHub Pages Integration Guide"))
    
    # Check directory structure
    print_header("4. Directory Structure")
    check_directory_exists("docs", "GitHub Pages directory")
    check_directory_exists("crypto_api", "Django app directory")
    check_directory_exists("letsgetcrypto_django", "Django project directory")
    
    # These directories might not exist yet (created by setup)
    print("\n  Directories created by setup.sh:")
    check_directory_exists("model_weights", "ML models directory")
    check_directory_exists("data_cache", "Data cache directory")
    check_directory_exists("staticfiles", "Static files directory")
    
    # Check if key dependencies can be imported (if installed)
    print_header("5. Python Dependencies (if installed)")
    print("  Core libraries:")
    check_import("django")
    check_import("pandas")
    check_import("numpy")
    check_import("sklearn")
    check_import("xgboost")
    
    print("\n  Optional libraries:")
    check_import("tensorflow")
    check_import("PyQt5")
    check_import("anthropic")
    
    # Check scripts are executable
    print_header("6. Script Permissions")
    scripts = ["setup.sh", "init_ml_environment.sh", "run.sh", "quick-start.sh"]
    for script in scripts:
        if Path(script).exists():
            is_executable = os.access(script, os.X_OK)
            if is_executable:
                print_success(f"{script} - Executable")
            else:
                print_warning(f"{script} - Not executable (run: chmod +x {script})")
    
    # Summary
    print_header("Summary")
    
    if all(all_checks):
        print_success("All essential checks passed!")
        print(f"\n{Colors.GREEN}Next steps:{Colors.END}")
        print("  1. Run ./setup.sh to complete setup")
        print("  2. Then run ./run.sh to start the application")
    else:
        failed = sum(1 for x in all_checks if not x)
        print_warning(f"{failed} checks failed or incomplete")
        print(f"\n{Colors.YELLOW}Recommendation:{Colors.END}")
        print("  Run ./setup.sh to install dependencies and create directories")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if all(all_checks) else 1

if __name__ == "__main__":
    sys.exit(main())
