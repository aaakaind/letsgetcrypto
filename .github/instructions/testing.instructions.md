---
applyTo:
  - "test_*.py"
  - "**/*test*.py"
---

# Testing Guidelines

## Test Structure

### File Organization
- Test files use `test_*.py` naming convention
- Group related tests in the same file
- Keep test files in the same directory as code they test
- Use descriptive test function names starting with `test_`

### Test Frameworks
- Use `pytest` as the primary testing framework
- Use `unittest` for Django-specific tests
- Mock external API calls to avoid rate limits
- Use fixtures for common setup/teardown

## Writing Tests

### Test Function Structure
```python
def test_feature_name():
    # Arrange: Set up test data
    data = {...}
    
    # Act: Execute the function being tested
    result = function_under_test(data)
    
    # Assert: Verify the result
    assert result == expected_value
```

### Assertions
- Use descriptive assertion messages
- Test both success and failure cases
- Test edge cases and boundary conditions
- Verify error handling with `pytest.raises()`

### Mocking
- Mock external API calls (CoinGecko, Binance, NewsAPI)
- Mock file I/O operations
- Mock database operations when testing business logic
- Use `unittest.mock.patch` or `pytest-mock`

## Test Categories

### Unit Tests
- Test individual functions in isolation
- Mock all external dependencies
- Fast execution (< 1 second per test)
- High coverage of edge cases

### Integration Tests
- Test multiple components together
- Use test databases (Django's test database)
- May use real API calls with test credentials
- Slower execution acceptable (< 5 seconds per test)

### End-to-End Tests
- Test complete workflows
- Use test/sandbox environments
- Include GUI/API interaction tests
- Longest execution time acceptable

## Test Data

### Fixtures
- Create reusable test data with pytest fixtures
- Use factories for complex object creation
- Keep test data minimal but representative
- Use separate test database for Django tests

### Mocked Responses
- Store sample API responses in test fixtures
- Use realistic data matching actual API formats
- Include both success and error responses
- Update when API formats change

## Django Testing

### Test Database
- Use Django's test database (automatic setup/teardown)
- Use `TestCase` for database-dependent tests
- Use `TransactionTestCase` when testing transactions
- Clean up test data in tearDown()

### API Testing
- Test all HTTP methods (GET, POST, PUT, DELETE)
- Verify status codes and response formats
- Test authentication and authorization
- Test input validation and error messages

## Running Tests

### Commands
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_integration.py

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=crypto_api
```

### Continuous Integration
- All tests must pass before merging
- Run tests in CI/CD pipeline
- Monitor test coverage
- Fix flaky tests immediately

## Best Practices

### Test Independence
- Each test should be independent
- Don't rely on test execution order
- Clean up resources after each test
- Reset mocks between tests

### Test Readability
- Use descriptive test names
- Add comments for complex test logic
- Keep tests simple and focused
- One assertion per test when possible

### Error Messages
- Provide helpful failure messages
- Include context in assertions
- Log relevant information on failure
- Make debugging easy

### Performance
- Keep unit tests fast
- Use mocking to avoid slow operations
- Run slow tests separately
- Optimize test setup/teardown
