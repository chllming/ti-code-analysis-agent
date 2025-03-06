<!-- Generated from ti-templates version 1.0.0  on 2025-03-06 -->
# python Specific Guidelines

## Architecture Guidelines

### Project Structure
- Follow standard python project structure
- Organize modules according to TI architecture pattern
- Separate concerns: data, logic, and presentation layers
- Use clear dependency management via [TECHNOLOGY-specific dependency tool]

### Design Patterns
- Implement the observer pattern for event-driven components
- Use dependency injection for modular and testable code
- Apply the repository pattern for data access operations
- Implement factory pattern for object creation when appropriate

## Coding Conventions

### Naming Conventions
- Use [camelCase/snake_case/PascalCase] for variables
- Use [camelCase/snake_case/PascalCase] for function/method names
- Use [camelCase/snake_case/PascalCase] for class names
- Use [UPPER_SNAKE_CASE] for constants
- Prefix private members with [_ or appropriate prefix]

### Documentation
- Document all public functions and classes using [TECHNOLOGY-specific doc format]
- Include examples in documentation for complex operations
- Document side effects and return values
- Use consistent tense and voice in comments
- Keep inline comments focused on "why" not "what"

## Best Practices

### Error Handling
- Use [TECHNOLOGY-specific error handling pattern]
- Avoid silent failures
- Log all errors with appropriate severity
- Include useful debugging information in error messages
- Centralize error handling where possible

### Performance Optimization
- Use asynchronous operations for I/O-bound operations 
- Implement caching for expensive operations
- Minimize object allocation in performance-critical code
- Use appropriate data structures for operations
- Profile code to identify bottlenecks

### Testing
- Write unit tests for all public functions
- Use [TECHNOLOGY-specific testing framework]
- Mock external dependencies in tests
- Test error conditions explicitly
- Achieve at least 80% code coverage

## Security Considerations

### Input Validation
- Validate all user inputs
- Use parameterized queries for database operations
- Sanitize data before displaying to users
- Implement appropriate access controls
- Apply principle of least privilege

### Data Protection
- Use environment variables for sensitive configuration
- Never store credentials or secrets in code
- Apply encryption for sensitive data at rest
- Use secure communication protocols
- Regularly update dependencies to address vulnerabilities

## Technology-Specific Libraries

### Recommended Libraries
- [Library 1]: For [purpose]
- [Library 2]: For [purpose]
- [Library 3]: For [purpose]
- [Library 4]: For [purpose]

### Library Usage Guidelines
- Prefer established libraries over custom implementations
- Review licenses before adding new dependencies
- Maintain consistent versions across the project
- Document reasons for library choices
- Include fallback strategies for critical library functionality

## Tailored Intelligence Integration

### TI Component Interaction
- Follow established integration patterns with other TI components
- Use standardized request/response formats for inter-component communication
- Document all integration points clearly
- Implement graceful degradation when dependencies are unavailable
- Include appropriate metrics and monitoring at integration boundaries

### Deployment Considerations
- Package applications following python best practices
- Create slim container images
- Support both development and production environments
- Include health check endpoints
- Externalize all configuration

## Cursor AI Usage Tips

### Code Generation
- Ask for python-specific implementations
- Request examples that follow TI architecture patterns
- Use "Generate test for this function" to create comprehensive tests
- Ask for documentation in python standard format

### Code Analysis
- Use "Review this code for python best practices" for feedback
- Request performance improvement suggestions
- Ask for security vulnerability analysis
- Get help with complex debugging scenarios

### Learning Resources
- [Resource 1]: [Description]
- [Resource 2]: [Description]
- [Resource 3]: [Description]
- [Resource 4]: [Description] 