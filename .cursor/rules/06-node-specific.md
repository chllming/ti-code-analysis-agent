# Node.js Specific Guidelines

## Node.js Version
- Use Node.js 18+ (LTS) for all new projects
- Document Node.js version requirements in package.json
- Use package.json "engines" field to specify Node.js version
- Monitor for security updates to Node.js
- Use the latest LTS version for production deployments

## TypeScript Usage
- Use TypeScript for all new projects
- Use strict mode in tsconfig.json
- Define proper interfaces for all data structures
- Use proper typing for function parameters and returns
- Avoid using `any` type unless absolutely necessary
- Leverage union types and generics appropriately
- Use type guards for runtime type checking

## Project Structure
```
project_name/
├── src/
│   ├── index.ts
│   ├── module1/
│   │   ├── index.ts
│   │   └── service1.ts
│   └── module2/
│       ├── index.ts
│       └── service2.ts
├── tests/
│   ├── module1/
│   │   └── service1.spec.ts
│   └── module2/
│       └── service2.spec.ts
├── docs/
├── package.json
└── README.md
```

## Dependency Management
- Use npm or yarn consistently across projects
- Lock dependencies with package-lock.json or yarn.lock
- Keep dependencies up to date
- Use security scanning tools for dependencies
- Minimize production dependencies
- Separate dev dependencies appropriately
- Document third-party service dependencies

## Error Handling
- Use async/await with proper try/catch blocks
- Create custom error classes for domain-specific errors
- Implement centralized error handling middleware for APIs
- Log errors with appropriate context
- Implement graceful degradation strategies
- Handle uncaught exceptions and unhandled rejections
- Return appropriate HTTP status codes in API responses

## Performance
- Use clustering to leverage multiple CPU cores
- Implement proper connection pooling for databases
- Use streaming for large data processing
- Implement caching strategies
- Profile memory usage and fix leaks
- Use asynchronous I/O operations
- Avoid blocking the event loop with CPU-intensive operations

## Testing
- Use Jest or Mocha for testing
- Create unit tests for all business logic
- Implement integration tests for API endpoints
- Use supertest for HTTP testing
- Use mocks for external dependencies
- Implement test coverage reporting
- Create end-to-end tests for critical flows

## Security
- Validate and sanitize all user inputs
- Implement proper authentication and authorization
- Use HTTPS for all connections
- Implement rate limiting for API endpoints
- Use security headers in HTTP responses
- Keep dependencies updated to avoid vulnerabilities
- Use parameterized queries for database operations 