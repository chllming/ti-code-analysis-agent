#!/bin/bash
# Railway setup and deployment script
# This script helps with initial Railway setup and first deployment

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Function to convert to lowercase (compatible with different shells)
to_lowercase() {
  echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
  print_message "Railway CLI not found. Installing..."
  curl -fsSL https://railway.app/install.sh | sh
  
  if ! command -v railway &> /dev/null; then
    print_error "Failed to install Railway CLI. Please install it manually: curl -fsSL https://railway.app/install.sh | sh"
    exit 1
  fi
fi

print_message "Railway CLI is installed."

# Check if user is logged in
if ! railway whoami &> /dev/null; then
  print_message "Please log in to Railway:"
  railway login
  
  if ! railway whoami &> /dev/null; then
    print_error "Failed to log in to Railway. Please try again."
    exit 1
  fi
fi

RAILWAY_USER=$(railway whoami)
print_message "Logged in as: ${RAILWAY_USER}"

# Check if we're in the correct directory
if [ ! -f "railway.toml" ]; then
  print_error "railway.toml not found. Please run this script from the project root."
  exit 1
fi

# Create a new project or link to existing
read -p "Create a new Railway project? (y/n, default: y): " CREATE_NEW
CREATE_NEW=${CREATE_NEW:-y}

if [ "$(to_lowercase "$CREATE_NEW")" = "y" ]; then
  print_message "Creating a new Railway project..."
  railway init
else
  print_message "Please select a project to link:"
  railway link
fi

# Get help on how to create a service with the current CLI version
print_message "Checking Railway CLI commands..."
railway --help

# Create a service using Railway UI
print_message "Let's create a new service. Please follow these steps:"
print_message "1. Visit the Railway dashboard at: https://railway.app/dashboard"
print_message "2. Select your project 'ti-deployment-agent'"
print_message "3. Click '+ New' and select 'GitHub Repo'"
print_message "4. Connect to your GitHub repository"
print_message "5. Select 'Dockerfile' as the deployment method"
print_message "6. Choose 'Dockerfile.railway' as the Dockerfile to use"
print_message "7. Click 'Deploy'"
print_message "8. Once deployment is complete, come back to this terminal"

read -p "Have you created the service in the Railway dashboard? (y/n): " SERVICE_CREATED
if [ "$(to_lowercase "$SERVICE_CREATED")" != "y" ]; then
  print_error "Please create the service before continuing."
  exit 1
fi

# Link to the existing service
print_message "Linking to the service..."
railway link

# Configure the project
print_message "Setting up environment variables..."

# Set variables with the correct syntax
print_message "Setting environment variables with Railway CLI..."
railway variables --set "PORT=5001" --set "MCP_HOST=0.0.0.0" --set "MCP_PORT=5001"
railway variables --set "LOG_LEVEL=INFO" --set "FLAKE8_CONFIG=/app/config/flake8.ini" --set "TEMP_DIR=/tmp/mcp_temp"

print_message "Environment variables configured successfully."

# Deploy manually if needed
read -p "Deploy now? (y/n, default: y): " DEPLOY_NOW
DEPLOY_NOW=${DEPLOY_NOW:-y}

if [ "$(to_lowercase "$DEPLOY_NOW")" = "y" ]; then
  print_message "Deploying to Railway..."
  railway up
  
  if [ $? -eq 0 ]; then
    print_message "Deployment successful!"
    print_message "Getting service URL..."
    railway status
  else
    print_error "Deployment failed. Check the logs for details."
    exit 1
  fi
else
  print_message "Skipping deployment. You can deploy later with 'railway up'."
fi

# Generate and save token for CI/CD if needed
read -p "Generate a token for CI/CD? (y/n, default: y): " GENERATE_TOKEN
GENERATE_TOKEN=${GENERATE_TOKEN:-y}

if [ "$(to_lowercase "$GENERATE_TOKEN")" = "y" ]; then
  print_message "Generating a new Railway token..."
  TOKEN=$(railway login --generate-token)
  
  if [ -n "$TOKEN" ]; then
    echo "$TOKEN" > .railway_token
    print_message "Token generated and saved to .railway_token"
    print_warning "IMPORTANT: Add this token as a secret in your GitHub repository (RAILWAY_TOKEN)"
    print_warning "DO NOT commit the .railway_token file to your repository!"
    
    # Add to .gitignore if not already there
    if ! grep -q ".railway_token" .gitignore; then
      echo ".railway_token" >> .gitignore
      print_message "Added .railway_token to .gitignore"
    fi
  else
    print_error "Failed to generate token."
  fi
fi

print_message "Setup complete! Next steps:"
print_message "1. If you generated a token, add it to your GitHub repository secrets as RAILWAY_TOKEN"
print_message "2. Add the deployed app URL to your GitHub repository secrets as RAILWAY_APP_URL"
print_message "3. Push to your main branch to trigger automatic deployment"
print_message "4. Monitor your deployment on the Railway dashboard"

exit 0 