# GitHub Actions CI/CD Pipeline Setup Guide

This guide provides detailed instructions for setting up and testing the GitHub Actions CI/CD pipeline for the MCP server deployment to Railway.

## Prerequisites

Before setting up the CI/CD pipeline, ensure you have:

- A GitHub repository with your MCP server code
- A Railway account with a project set up
- Admin access to the GitHub repository for adding secrets

## Step 1: Generate a Railway Token

1. If you haven't already, generate a Railway token using the Railway CLI:
   ```bash
   railway login --generate-token
   ```

2. Copy the generated token. You'll need it in the next step.

## Step 2: Configure GitHub Repository Secrets

Add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add the following secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `RAILWAY_TOKEN` | Your Railway API token | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `RAILWAY_APP_URL` | The URL of your deployed application | `https://mcp-server-production.up.railway.app` |
| `RAILWAY_PROJECT_ID` | (Optional) Your Railway project ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |

To get your `RAILWAY_APP_URL`:
- Deploy your application manually first using `railway up`
- Check the Railway dashboard for your service's URL
- You can also run `railway status` to see deployment information

To get your `RAILWAY_PROJECT_ID`:
- It's visible in the URL when you view your project in the Railway dashboard
- The format is typically `https://railway.app/project/YOUR-PROJECT-ID`

## Step 3: Review the GitHub Actions Workflow

Our workflow file (`.github/workflows/railway-deploy.yml`) is configured to:

1. Run on pushes to the main branch or manual trigger
2. Run all tests before deployment
3. Install the Railway CLI
4. Deploy the application to Railway
5. Verify the deployment with a health check

The workflow file is already set up, but you may want to review it and make changes based on your specific needs.

## Step 4: Test the CI/CD Pipeline

You can test the CI/CD pipeline in two ways:

### Option 1: Push to the Main Branch

Make a small change to your code and push it to the main branch:

```bash
git add .
git commit -m "Test CI/CD pipeline"
git push origin main
```

### Option 2: Manual Trigger

1. Go to your GitHub repository
2. Navigate to Actions
3. Select the "Deploy to Railway" workflow
4. Click "Run workflow"
5. Select the branch to run the workflow on
6. Click "Run workflow"

## Step 5: Monitor the Deployment

1. Go to your GitHub repository
2. Navigate to Actions
3. Select the latest run of the "Deploy to Railway" workflow
4. Monitor the progress of the workflow
5. Check the logs for any errors

If the deployment is successful, you should see something like:
```
Deployment successful and health check passed!
Deployment completed successfully!
```

## Troubleshooting

### Common Issues

1. **Health check fails**:
   - Verify your `RAILWAY_APP_URL` is correct
   - Ensure the health endpoint is working properly
   - Check Railway logs for any errors

2. **Authentication failures**:
   - Verify your `RAILWAY_TOKEN` is valid and has not expired
   - Regenerate the token if necessary

3. **Project linking issues**:
   - Provide a `RAILWAY_PROJECT_ID` to ensure the correct project is selected
   - Check that the service exists in your Railway project

4. **Test failures blocking deployment**:
   - Fix failing tests before retrying the deployment
   - You can temporarily modify the workflow to skip tests for debugging (not recommended for production)

### Getting Logs

For more detailed information on a failed deployment:

1. Check the GitHub Actions run logs
2. Check the Railway logs using `railway logs`

## Customizing the Pipeline

You can customize the CI/CD pipeline by editing the `.github/workflows/railway-deploy.yml` file:

- Add additional test steps
- Configure notifications (e.g., Slack, email)
- Adjust the health check timeout
- Add approval steps for production deployments

## Security Considerations

1. Never commit the Railway token to your repository
2. Rotate your Railway token periodically
3. Consider using branch protection rules to prevent direct pushes to main
4. Review GitHub Actions permissions to ensure they're not too permissive 