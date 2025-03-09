#!/bin/bash
set -e

# Run tests for the MCP server

# Check if in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Warning: It doesn't look like you're in a virtual environment."
  echo "It's recommended to run tests in a virtual environment."
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Install dependencies if needed
if ! python -c "import pytest" &> /dev/null; then
  echo "Installing test dependencies..."
  pip install -r requirements-dev.txt
fi

# Run the tests
echo "Running tests..."
pytest "$@"

# If no arguments and tests passed, run with coverage
if [ $? -eq 0 ] && [ $# -eq 0 ]; then
  echo
  echo "Running tests with coverage..."
  pytest --cov=src tests/
fi 