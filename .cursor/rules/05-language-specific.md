# Language-Specific Guidelines

## Python Best Practices
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Leverage dataclasses or Pydantic models for data validation
- Prefer context managers for resource handling
- Use virtual environments for dependency management
- Document functions with docstrings following Google or NumPy style
- Use list/dict comprehensions for clarity when appropriate
- Leverage generator expressions for memory efficiency
- Prefer explicit imports over wildcard imports
- Use pathlib for file path operations instead of os.path
- Implement proper exception handling with specific exception types
- Use f-strings for string formatting in Python 3.6+

## JavaScript/TypeScript Best Practices
- Use TypeScript for all new JavaScript projects
- Leverage strict type checking in TypeScript
- Follow ESLint and Prettier configurations
- Use async/await instead of raw Promises for async operations
- Implement proper error handling in async functions
- Use destructuring for cleaner code
- Prefer const over let, avoid var
- Leverage modern ES6+ features appropriately
- Use module systems consistently (ESM preferred)
- Implement proper null/undefined checks
- Follow functional programming principles where appropriate
- Use proper dependency injection patterns

## Node.js Specific
- Use the latest LTS version of Node.js
- Implement proper error handling for all async operations
- Utilize environment variables for configuration
- Follow the 12-factor app methodology
- Implement graceful shutdown handlers
- Use appropriate logging levels and structured logging
- Implement proper request validation for APIs
- Use connection pooling for database connections
- Implement circuit breakers for external dependencies
- Use proper middleware patterns in Express applications

## Go Best Practices
- Follow standard Go code formatting with gofmt
- Use meaningful error handling with proper error wrapping
- Implement Context for managing cancellation and deadlines
- Prefer composition over inheritance
- Use interfaces for abstraction and testing
- Implement proper concurrency patterns with goroutines and channels
- Follow standard project layout conventions
- Use proper dependency injection
- Leverage the standard library when possible
- Follow idiomatic Go naming conventions 