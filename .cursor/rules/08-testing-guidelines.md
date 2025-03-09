# Testing Guidelines

## Test Coverage Requirements
- Unit tests must cover at least 85% of code
- All public interfaces must have comprehensive test coverage
- All edge cases and error conditions must be tested
- Critical paths must have 100% test coverage
- Tests must be maintained and updated alongside code changes

## Test Types
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Verify interactions between components
- **Functional Tests**: Verify end-to-end functionality
- **Performance Tests**: Verify response time and resource usage
- **Security Tests**: Verify security mechanisms and identify vulnerabilities

## Test-Driven Development
- Write tests before implementing functionality
- Use tests to define and verify requirements
- Refactor code only after tests are passing
- Maintain test independence to allow parallel execution
- Use descriptive test names that explain what is being tested

## Test Structure Guidelines
- Each test should focus on a single aspect of functionality
- Follow the Arrange-Act-Assert pattern
- Setup and teardown should be clean and efficient
- Avoid test interdependencies
- Mock external dependencies appropriately
- Use fixtures for common test data

## Test Maintenance
- Keep tests up to date with code changes
- Refactor tests when refactoring code
- Delete tests for removed functionality
- Add tests for new functionality
- Document test approach and any special testing requirements
- Ensure tests remain fast and reliable

## Test Automation
- Integrate tests with CI/CD pipeline
- Run tests automatically on code changes
- Set up test environments that mirror production
- Generate test reports and track coverage over time
- Use code coverage tools appropriate for your language
- Implement visual testing for UI components when applicable

# Testing Guidelines for MCP Server

## Test Frameworks and Tools

### Unit Testing
- Use pytest as the primary testing framework
- Implement proper fixtures for reusable test components
- Use parameterized tests for testing multiple inputs
- Leverage pytest markers to categorize tests
- Implement proper assertion messages for clarity

### Integration Testing
- Test the complete flow from API request to tool execution
- Use pytest-flask for Flask application testing
- Create fixtures that represent real-world scenarios
- Test error handling and edge cases
- Verify proper HTTP status codes and response formats

### Mocking and Stubs
- Use unittest.mock or pytest-mock for mocking dependencies
- Create test doubles for external tools like Flake8
- Implement custom test fixtures for MCP protocol testing
- Use context managers for temporary test resources
- Document mock behavior and assumptions

## Test Coverage

### Coverage Targets
- Aim for at least 90% code coverage for core functionality
- Ensure 100% coverage for critical path code
- Use pytest-cov to generate coverage reports
- Exclude boilerplate and generated code from coverage metrics
- Configure CI to fail if coverage drops below thresholds

### Coverage Types
- Ensure statement coverage (executed lines)
- Implement branch coverage (decision points)
- Test exception paths and error handling
- Cover boundary conditions and edge cases
- Test both successful and failure scenarios

## MCP Server Testing

### JSON-RPC Testing
- Validate compliance with JSON-RPC 2.0 specification
- Test required methods: initialize, tools/list, tools/call
- Verify proper error codes for invalid requests
- Test method parameter validation
- Verify response format matches specification

### Flake8 Integration Testing
- Test secure file handling for code analysis
- Verify Flake8 execution with various configuration options
- Test result parsing and formatting
- Verify proper cleanup of temporary files
- Test handling of various Python syntax errors

### Cursor Integration Testing
- Test natural language command parsing
- Verify proper handling of file paths
- Test various code input methods
- Verify correct display of analysis results
- Test error feedback in the UI

## Test Organization

### Directory Structure
- Organize tests to mirror the application structure
- Keep test files separate from implementation files
- Group tests by functionality
- Create separate directories for unit and integration tests
- Store test fixtures and data in dedicated directories

### Test Naming
- Use descriptive test names that explain the test purpose
- Follow a consistent naming convention (test_<function_name>_<scenario>)
- Group related tests in classes when appropriate
- Use docstrings to explain complex test scenarios
- Include expected outcome in the test name

## Test Execution

### Local Testing
- Run tests with `pytest` command
- Use `-v` flag for verbose output
- Use `-x` flag to stop on first failure
- Use `-k` flag to run specific tests by name
- Generate coverage reports with `--cov=src`

### CI Testing
- Configure automated testing in CI pipeline
- Run tests on multiple Python versions
- Generate and publish test reports
- Enforce code coverage thresholds
- Configure tests to fail the build on error

## Test-Driven Development

### TDD Workflow
- Write tests before implementing features
- Start with failing tests that describe expected behavior
- Implement the minimal code to make tests pass
- Refactor code while maintaining passing tests
- Use test coverage to identify missed scenarios

### Testing Patterns
- Arrange-Act-Assert pattern for test organization
- Test fixtures for complex setup
- Parameterized tests for multiple inputs
- Context managers for resource cleanup
- Factory methods for test data generation

## Performance Testing

### Response Time Testing
- Measure response time for various code sizes
- Test performance with multiple concurrent requests
- Establish baselines and thresholds for acceptable performance
- Implement load testing for production readiness
- Test memory usage with large inputs

### Tool Execution Testing
- Measure execution time for Flake8 on various file sizes
- Test parallel execution capabilities
- Verify proper timeout handling for long-running analyses
- Test resource usage during peak load
- Verify proper cleanup of resources after execution 