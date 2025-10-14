#!/usr/bin/env python3
"""
Unified Test Runner for LetsGetCrypto
Runs all available test suites and provides a comprehensive summary
"""

import sys
import os
import subprocess
from typing import Tuple, List, Dict

# Use colorama for cross-platform color support
import colorama
colorama.init(autoreset=True)
from colorama import Fore, Style

GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
class TestRunner:
    """Unified test runner for all LetsGetCrypto test suites"""
    
    def __init__(self):
        self.test_modules = {
            'integration': {
                'file': 'test_integration.py',
                'description': 'Integration Tests (MCP Server, Views, Config)',
                'required_deps': []
            },
            'mcp': {
                'file': 'test_mcp_server.py',
                'description': 'MCP Server Tests',
                'required_deps': ['mcp']
            },
            'claude': {
                'file': 'test_claude_integration.py',
                'description': 'Claude AI Integration Tests',
                'required_deps': ['anthropic', 'pandas']
            },
            'feedback': {
                'file': 'test_feedback_loop_simple.py',
                'description': 'Feedback Loop Tests',
                'required_deps': ['pandas']
            },
            'aws': {
                'file': 'test_aws_deployment.py',
                'description': 'AWS Deployment Tests',
                'required_deps': ['requests'],
                'requires_server': True
            }
        }
        self.results = {}
    
    def check_dependencies(self, deps: List[str]) -> Tuple[bool, List[str]]:
        """Check if required dependencies are available"""
        missing = []
        for dep in deps:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        return len(missing) == 0, missing
    
    def run_test_suite(self, name: str, config: Dict) -> Tuple[bool, str]:
        """Run a single test suite"""
        print(f"\n{BLUE}{'=' * 70}{RESET}")
        print(f"{BOLD}Running: {config['description']}{RESET}")
        print(f"{BLUE}{'=' * 70}{RESET}")
        
        # Check if test file exists
        if not os.path.exists(config['file']):
            return False, f"Test file not found: {config['file']}"
        
        # Check dependencies
        required_deps = config.get('required_deps', [])
        if required_deps:
            deps_ok, missing = self.check_dependencies(required_deps)
            if not deps_ok:
                msg = f"Missing dependencies: {', '.join(missing)}"
                print(f"{YELLOW}⚠️  SKIPPED: {msg}{RESET}")
                return None, msg
        
        # Check if server is required
        if config.get('requires_server', False):
            print(f"{YELLOW}⚠️  SKIPPED: Requires running server{RESET}")
            return None, "Requires running server"
        
        # Run the test
        try:
            result = subprocess.run(
                [sys.executable, config['file']],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(f"{RED}STDERR:{RESET}")
                print(result.stderr)
            
            success = result.returncode == 0
            status = "PASSED" if success else "FAILED"
            
            return success, status
        except subprocess.TimeoutExpired:
            print(f"{RED}Test timed out after 60 seconds{RESET}")
            return False, "TIMEOUT"
        except Exception as e:
            print(f"{RED}Error running test: {e}{RESET}")
            return False, str(e)
    
    def run_all_tests(self, specific_tests: List[str] = None):
        """Run all or specific test suites"""
        print(f"\n{BOLD}{BLUE}{'=' * 70}")
        print("LetsGetCrypto - Unified Test Runner")
        print(f"{'=' * 70}{RESET}\n")
        
        # Determine which tests to run
        tests_to_run = specific_tests if specific_tests else list(self.test_modules.keys())
        
        # Run each test suite
        for name in tests_to_run:
            if name not in self.test_modules:
                print(f"{RED}Unknown test suite: {name}{RESET}")
                continue
            
            config = self.test_modules[name]
            success, message = self.run_test_suite(name, config)
            self.results[name] = {
                'success': success,
                'message': message,
                'description': config['description']
            }
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print(f"\n{BOLD}{BLUE}{'=' * 70}")
        print("Test Summary")
        print(f"{'=' * 70}{RESET}\n")
        
        passed = sum(1 for r in self.results.values() if r['success'] is True)
        failed = sum(1 for r in self.results.values() if r['success'] is False)
        skipped = sum(1 for r in self.results.values() if r['success'] is None)
        total = len(self.results)
        
        # Print individual results
        for name, result in self.results.items():
            status = result['success']
            msg = result['message']
            desc = result['description']
            
            if status is True:
                print(f"  {GREEN}✓ PASSED{RESET}  - {desc}")
            elif status is False:
                print(f"  {RED}✗ FAILED{RESET}  - {desc}")
                if msg and msg != "FAILED":
                    print(f"            Reason: {msg}")
            else:  # status is None (skipped)
                print(f"  {YELLOW}⊘ SKIPPED{RESET} - {desc}")
                print(f"            Reason: {msg}")
        
        # Print overall summary
        print(f"\n{BOLD}Results:{RESET}")
        print(f"  Total:   {total}")
        print(f"  {GREEN}Passed:  {passed}{RESET}")
        print(f"  {RED}Failed:  {failed}{RESET}")
        print(f"  {YELLOW}Skipped: {skipped}{RESET}")
        
        # Print final status
        print(f"\n{BLUE}{'=' * 70}{RESET}")
        if failed == 0 and passed > 0:
            print(f"{GREEN}{BOLD}🎉 All executed tests passed!{RESET}")
        elif failed > 0:
            print(f"{RED}{BOLD}⚠️  Some tests failed!{RESET}")
        else:
            print(f"{YELLOW}{BOLD}⚠️  No tests were executed!{RESET}")
        print(f"{BLUE}{'=' * 70}{RESET}\n")
        
        return failed == 0 and passed > 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Unified test runner for LetsGetCrypto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python test_all.py
  
  # Run specific test suites
  python test_all.py --tests integration claude
  
  # List available test suites
  python test_all.py --list

Available test suites:
  integration - Integration Tests (MCP Server, Views, Config)
  mcp         - MCP Server Tests
  claude      - Claude AI Integration Tests
  feedback    - Feedback Loop Tests
  aws         - AWS Deployment Tests (requires running server)
        """
    )
    
    parser.add_argument(
        '--tests', '-t',
        nargs='+',
        help='Specific test suites to run (default: all)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available test suites'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # List test suites if requested
    if args.list:
        print(f"\n{BOLD}Available Test Suites:{RESET}\n")
        for name, config in runner.test_modules.items():
            deps = config.get('required_deps', [])
            deps_str = f" (requires: {', '.join(deps)})" if deps else ""
            server_str = " [requires server]" if config.get('requires_server') else ""
            print(f"  {name:12} - {config['description']}{deps_str}{server_str}")
        print()
        return 0
    
    # Run tests
    runner.run_all_tests(args.tests)
    
    # Return exit code based on results
    if any(r['success'] is False for r in runner.results.values()):
        return 1
    elif not any(r['success'] is True for r in runner.results.values()):
        return 2  # No tests executed
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
