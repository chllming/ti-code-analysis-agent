# Deploying MCP Server to Railway

This document provides detailed instructions on how to deploy the MCP (Model Command Protocol) server to Railway.

## Prerequisites

Before you begin, ensure you have the following:

- A Railway account (https://railway.app)
- Railway CLI installed on your development machine
- GitHub account (for CI/CD)
- Git repository with the MCP server code

## Setup Process

### 1. Assisted Setup

The easiest way to set up Railway deployment is using our setup script:

```bash
chmod +x scripts/setup_railway.sh
./scripts/setup_railway.sh
```

This script will:
- Install Railway CLI if not already installed
- Guide you through logging in to Railway
- Initialize a new Railway project
- Guide you through the process of creating a service via the Railway dashboard
- Set up required environment variables
- Deploy the application (optional)
- Generate a token for CI/CD (optional)

### 2. Manual Setup (Alternative)

If you prefer to set up Railway manually, follow these steps:

1. Install Railway CLI:
   ```bash
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. Log in to Railway:
   ```bash
   railway login
   ```

3. Initialize a new project:
   ```bash
   railway init
   ```

4. Create a new service in the Railway dashboard:
   - Visit https://railway.app/dashboard
   - Select your project
   - Click "+ New" and select "GitHub Repo" or "Empty Service"
   - If using GitHub, connect to your GitHub repository
   - Select "Dockerfile" as the deployment method
   - Specify "Dockerfile.railway" as the Docker file to use

5. Link to the service:
   ```bash
   railway link
   ```

6. Set required environment variables:
   ```bash
   railway variables --set "PORT=5001" --set "MCP_HOST=0.0.0.0" --set "MCP_PORT=5001"
   railway variables --set "LOG_LEVEL=INFO" --set "FLAKE8_CONFIG=/app/config/flake8.ini" --set "TEMP_DIR=/tmp/mcp_temp"
   ```

7. Deploy the application:
   ```bash
   railway up
   ```

### 3. GitHub Actions CI/CD Setup

To enable continuous deployment with GitHub Actions:

1. Generate a Railway token:
   ```bash
   railway login --generate-token
   ```

2. Add the following secrets to your GitHub repository:
   - `RAILWAY_TOKEN`: The token generated in the previous step
   - `RAILWAY_APP_URL`: The URL of your deployed application (e.g., https://mcp-server-production.up.railway.app)
   - `RAILWAY_PROJECT_ID`: (Optional) Your Railway project ID

3. Ensure the GitHub Actions workflow file is in place:
   - `.github/workflows/railway-deploy.yml` (already included in the repository)

4. Push to the main branch to trigger a deployment:
   ```bash
   git push origin main
   ```

## Project Structure

These files are specifically configured for Railway deployment:

- `Dockerfile.railway` - Optimized Docker configuration for Railway
- `.dockerignore` - Excludes unnecessary files from the Docker image
- `railway.toml` - Railway-specific configuration
- `.github/workflows/railway-deploy.yml` - GitHub Actions workflow for CI/CD
- `scripts/setup_railway.sh` - Helper script for initial setup

## Environment Variables

The following environment variables are used:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| PORT | The port on which the server runs | 5001 |
| MCP_HOST | The host address to bind to | 0.0.0.0 |
| MCP_PORT | The port the MCP server listens on | 5001 |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| FLAKE8_CONFIG | Path to Flake8 configuration | /app/config/flake8.ini |
| TEMP_DIR | Directory for temporary files | /tmp/mcp_temp |

## Monitoring and Maintenance

### Viewing Logs

To view logs for your deployed application:

```bash
railway logs
```

### Checking Status

To check the status of your deployment:

```bash
railway status
```

### Manual Redeployment

To manually trigger a redeployment:

```bash
railway up
```

## Troubleshooting

### Common Issues

1. **"No service linked" error when setting variables**:
   - Make sure you've linked to your service using `railway link`
   - Create a service in the Railway dashboard before attempting to set variables

2. **"Unexpected argument" errors with Railway CLI**:
   - The Railway CLI syntax may have changed; check the current syntax with `railway --help`
   - For setting variables, use `railway variables --set "KEY=VALUE"`

3. **Health check fails**:
   - Verify the /health endpoint is working properly
   - Check logs for any startup errors

4. **Deployment failures**:
   - Check if your Dockerfile.railway is properly configured
   - Ensure all required environment variables are set
   - Check the Railway logs for detailed error messages

### Getting Support

If you encounter issues with your Railway deployment:

1. Check the Railway documentation: https://docs.railway.app/
2. Review the Railway status page: https://railway.app/status
3. Join the Railway Discord: https://discord.gg/railway

## Security Considerations

1. Never commit Railway tokens to your repository
2. Regularly rotate your Railway tokens
3. Use environment variables for all sensitive configuration
4. Ensure your Docker image follows security best practices (non-root user, minimal dependencies)

## Performance Optimization

To optimize performance on Railway:

1. Configure the right number of worker processes for your Gunicorn server
2. Monitor memory and CPU usage in the Railway dashboard
3. Consider using multiple replicas for high-availability
4. Implement response caching for frequently accessed routes

## Railway CLI Reference

The Railway CLI commands have been updated in recent versions. Here are the most commonly used commands:

```bash
# Login to Railway
railway login

# List all commands and options
railway --help

# Initialize a new project
railway init

# Link to an existing project/service
railway link

# Set environment variables
railway variables --set "KEY=VALUE" --set "ANOTHER_KEY=VALUE"

# List environment variables
railway variables

# Deploy your application
railway up

# View logs
railway logs

# Check status
railway status
``` 