#!/usr/bin/env python3
"""
Startup script for the Advanced Cryptocurrency Trading & Prediction Tool

This script provides a simple way to launch the application with proper
error handling and dependency checking.
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'PyQt5', 'pandas', 'numpy', 'matplotlib', 'scikit-learn',
        'xgboost', 'ccxt', 'requests', 'ta', 'loguru'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies satisfied")
    return True

def main():
    """Main startup function"""
    print("🚀 Advanced Cryptocurrency Trading & Prediction Tool")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n⚠️  RISK DISCLOSURE")
    print("-" * 20)
    print("This tool is for EDUCATIONAL PURPOSES ONLY.")
    print("Cryptocurrency trading involves substantial risk.")
    print("Never invest more than you can afford to lose.")
    print("Always use testnet/sandbox mode for learning.")
    
    # Ask for confirmation
    try:
        response = input("\n📋 Do you acknowledge the risks? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting. Stay safe! 👋")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nExiting. Stay safe! 👋")
        sys.exit(0)
    
    print("\n🎯 Starting application...")
    
    try:
        # Import and run the main application
        from main import main as run_app
        run_app()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure main.py is in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application error: {e}")
        print("Check the logs for more details")
        sys.exit(1)

if __name__ == "__main__":
    main()