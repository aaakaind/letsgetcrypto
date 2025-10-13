# Testing Guide for LetsGetCrypto

This document provides information about testing the LetsGetCrypto application.

## Overview

LetsGetCrypto includes a comprehensive test suite covering various aspects of the application:

- **Integration Tests** - Core functionality, MCP server, views, and configuration
- **MCP Server Tests** - Model Context Protocol server functionality
- **Claude AI Integration Tests** - AI-powered market analysis features
- **Feedback Loop Tests** - Automated learning and training system
- **AWS Deployment Tests** - Cloud deployment readiness checks

## Quick Start

### Running All Tests

The easiest way to run all tests is using the unified test runner:

```bash
python test_all.py
```

This will:
- Run all available test suites
- Skip tests with missing dependencies
- Provide a comprehensive summary

### Running Specific Tests

Run one or more specific test suites:

```bash
# Run only integration tests
python test_all.py --tests integration

# Run multiple specific suites
python test_all.py --tests integration claude
```

### List Available Tests

See all available test suites:

```bash
python test_all.py --list
```

## Individual Test Suites

Each test suite can also be run independently:

### 1. Integration Tests

Tests core functionality without heavy dependencies.

```bash
python test_integration.py
```

**What it tests:**
- MCP server module imports and configuration
- Views module syntax validation
- MCP configuration file validity
- Requirements file completeness
- Documentation presence

**Dependencies:** None (minimal dependencies)

### 2. MCP Server Tests

Tests the Model Context Protocol server implementation.

```bash
python test_mcp_server.py
```

**What it tests:**
- Server initialization
- Tool listing functionality
- Resource endpoints
- JSON-RPC communication

**Dependencies:** `mcp`

### 3. Claude AI Integration Tests

Tests the Claude Opus 4.1 integration for AI-powered insights.

```bash
python test_claude_integration.py
```

**What it tests:**
- Claude library availability
- API key configuration
- Analyzer initialization
- Integration points
- Mock analysis structure

**Dependencies:** `anthropic`, `pandas`

### 4. Feedback Loop Tests

Tests the automated learning and training system.

```bash
python test_feedback_loop_simple.py
```

**What it tests:**
- Code syntax and structure
- FeedbackLoop class existence
- Method completeness
- Configuration structure
- GUI integration

**Dependencies:** `pandas`

### 5. AWS Deployment Tests

Tests AWS deployment readiness and health endpoints.

```bash
python test_aws_deployment.py
```

**What it tests:**
- Health check endpoints
- Readiness endpoints
- Liveness checks
- API endpoints
- Database connectivity
- Security headers
- Performance metrics

**Dependencies:** `requests`
**Note:** Requires a running server (default: http://localhost:8000)

## Installing Dependencies

To run all tests, install all dependencies:

```bash
pip install -r requirements.txt
```

To install only what you need for specific tests:

```bash
# For MCP tests
pip install mcp

# For Claude tests
pip install anthropic pandas

# For AWS tests
pip install requests
```

## Test Output

The unified test runner provides colored output:
- ✓ **Green** - Tests passed
- ✗ **Red** - Tests failed
- ⊘ **Yellow** - Tests skipped (missing dependencies or requirements)

### Example Output

```
======================================================================
Test Summary
======================================================================

  ✓ PASSED  - Integration Tests (MCP Server, Views, Config)
  ⊘ SKIPPED - MCP Server Tests
            Reason: Missing dependencies: mcp
  ✓ PASSED  - Claude AI Integration Tests
  ✗ FAILED  - AWS Deployment Tests
            Reason: Connection refused

Results:
  Total:   4
  Passed:  2
  Failed:  1
  Skipped: 1
```

## Exit Codes

The test runner uses standard exit codes:
- `0` - All executed tests passed
- `1` - One or more tests failed
- `2` - No tests were executed

This makes it easy to integrate with CI/CD pipelines:

```bash
# Example CI script
if python test_all.py; then
    echo "Tests passed!"
else
    echo "Tests failed!"
    exit 1
fi
```

## Continuous Integration

The test suite is designed to work with CI/CD systems:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: python test_all.py
  
- name: Run integration tests only
  run: python test_all.py --tests integration
```

## Troubleshooting

### Tests are Skipped

If tests are being skipped, you're likely missing dependencies:

```bash
# Check what's missing
python test_all.py

# Install missing dependencies
pip install mcp anthropic pandas requests
```

### AWS Tests Fail

AWS deployment tests require a running server:

```bash
# Start the server in one terminal
python manage.py runserver

# Run tests in another terminal
python test_aws_deployment.py
```

Or specify a different URL:

```bash
python test_aws_deployment.py --url http://your-server:8000
```

### Import Errors

If you see import errors, ensure you're in the correct directory:

```bash
cd /path/to/letsgetcrypto
python test_all.py
```

## Adding New Tests

To add a new test suite:

1. Create a new test file (e.g., `test_newfeature.py`)
2. Implement a `main()` function that returns an exit code
3. Add the test to `test_all.py`:

```python
self.test_modules = {
    # ... existing tests ...
    'newfeature': {
        'file': 'test_newfeature.py',
        'description': 'New Feature Tests',
        'required_deps': ['some_package']
    }
}
```

## Best Practices

1. **Run tests early and often** - Catch issues before they become problems
2. **Test incrementally** - Use `--tests` to focus on what you're working on
3. **Check dependencies** - Use `--list` to see what's required
4. **Read the output** - Test failures include helpful diagnostic information
5. **Keep tests fast** - Individual test suites should complete in under 60 seconds

## Related Documentation

- [README.md](README.md) - Main project documentation
- [MCP_SERVER.md](MCP_SERVER.md) - MCP server setup and usage
- [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - AWS deployment guide
- [FEEDBACK_LOOP.md](FEEDBACK_LOOP.md) - Feedback loop documentation

## Support

If you encounter issues with tests:

1. Check this documentation
2. Review the test output for specific error messages
3. Ensure all dependencies are installed
4. Check that you're using a supported Python version (3.8+)
5. Open an issue on GitHub with the test output
