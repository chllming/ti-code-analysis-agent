#!/bin/bash
set -e

# Run the MCP server

# Check if in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Warning: It doesn't look like you're in a virtual environment."
  echo "It's recommended to run the server in a virtual environment."
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Install dependencies if needed
if ! python -c "import flask" &> /dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
fi

# Create temp directory if needed
TEMP_DIR=$(grep TEMP_DIR .env | cut -d '=' -f2 || echo "/tmp/mcp_temp")
mkdir -p $TEMP_DIR

# Run the server using the run.py script
echo "Starting MCP server..."
python ./run.py 