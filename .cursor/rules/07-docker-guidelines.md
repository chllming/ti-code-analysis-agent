# Docker Guidelines

## Docker Best Practices
- Use multi-stage builds to minimize image size
- Follow the principle of least privilege
- Use specific version tags for base images (avoid `latest` tag)
- Order Dockerfile commands for optimal layer caching
- Include proper labels and metadata
- Run containers as non-root users
- Set appropriate file permissions
- Scan images for vulnerabilities
- Minimize installed packages
- Use secrets management for sensitive data
- Never store credentials in Docker images

## Base Image Selection
- Use official images when possible
- Use slim or alpine variants to reduce image size
- Pin specific versions (avoid `latest` tag)
- Use distroless images for production when appropriate
- Document base image selection rationale

## Environment Configuration
- Use environment variables for all configuration
- Provide sensible defaults where appropriate
- Use .env files for local development only
- Follow 12-factor app principles for configuration
- Pass secrets via environment variables or dedicated secrets management
- Document all required environment variables

## Docker Compose Usage
- Use Docker Compose for local development
- Define service dependencies clearly
- Use volumes for persistent data
- Configure networks appropriately
- Set resource limits for containers
- Use health checks for service dependencies

## Build Optimization
- Leverage build cache effectively
- Group related RUN commands with && to reduce layers
- Clean up package manager caches in the same layer
- Use .dockerignore to exclude unnecessary files
- Minimize the number of layers
- Only copy necessary files into the container 