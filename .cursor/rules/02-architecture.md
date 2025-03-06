# TI Architecture Guidelines

## Two-Pillar Architecture
- All implementations must align with the Tailored Intelligence two-pillar architecture:
  - **Personality Pillar**: Components focused on personalization, preference learning, and contextual awareness
  - **Agency Pillar**: Components enabling action execution, decision-making, and response refinement
- Integration points between pillars must be clearly defined and documented
- Each component should have a single, well-defined responsibility within the architecture
- Cross-component communication should follow standardized patterns

## Component Design
- Apply clean architecture principles with clear separation of concerns
- Organize code into domain-driven layers (presentation, application, domain, infrastructure)
- Minimize dependencies between components
- Use dependency injection and inversion of control patterns
- Define clear interfaces between components

## Cross-Component Integration
- Define clear interfaces for integration with other TI components
- Follow the Model Command Protocol (MCP) for standardized communication
- Implement comprehensive error handling at integration points
- Document all dependencies and requirements for integration

## API Design
- Design APIs following RESTful principles where appropriate
- Use consistent naming conventions for endpoints
- Structure requests and responses with clear schemas
- Implement proper error handling and status codes
- Document all APIs using standardized formats (OpenAPI/Swagger) 