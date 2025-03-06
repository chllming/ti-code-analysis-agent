#!/bin/bash
# Docker utility functions for TI components

# Display help
function show_help {
  echo "Docker utility functions for TI components"
  echo ""
  echo "Usage: ./docker-utils.sh [command]"
  echo ""
  echo "Commands:"
  echo "  build       Build Docker image"
  echo "  test        Run tests in Docker"
  echo "  dev         Start development environment"
  echo "  prod        Start production environment"
  echo "  stop        Stop running containers"
  echo "  clean       Clean Docker artifacts"
  echo "  exec        Execute command in running container"
  echo "  logs        View container logs"
  echo "  help        Show this help message"
  echo ""
}

# Build Docker image
function docker_build {
  echo "Building Docker image..."
  docker build -t ti-app .
}

# Run tests in Docker
function docker_test {
  echo "Running tests in Docker..."
  docker-compose run --rm test
}

# Start development environment
function docker_dev {
  echo "Starting development environment..."
  docker-compose up -d
  echo "Development environment started. View logs with './docker-utils.sh logs'"
}

# Start production environment
function docker_prod {
  echo "Starting production environment..."
  docker-compose -f docker-compose.prod.yml up -d
  echo "Production environment started. View logs with './docker-utils.sh logs'"
}

# Stop running containers
function docker_stop {
  echo "Stopping containers..."
  docker-compose down
}

# Clean Docker artifacts
function docker_clean {
  echo "Cleaning Docker artifacts..."
  docker-compose down -v
  docker system prune -f
  echo "Docker artifacts cleaned."
}

# Execute command in running container
function docker_exec {
  if [ $# -eq 0 ]; then
    echo "Error: Command required."
    echo "Usage: ./docker-utils.sh exec [command]"
    exit 1
  fi
  
  echo "Executing command in container..."
  docker-compose exec app "$@"
}

# View container logs
function docker_logs {
  echo "Viewing logs..."
  docker-compose logs -f
}

# Main function
function main {
  case "$1" in
    build)
      docker_build
      ;;
    test)
      docker_test
      ;;
    dev)
      docker_dev
      ;;
    prod)
      docker_prod
      ;;
    stop)
      docker_stop
      ;;
    clean)
      docker_clean
      ;;
    exec)
      shift
      docker_exec "$@"
      ;;
    logs)
      docker_logs
      ;;
    help|*)
      show_help
      ;;
  esac
}

# Make script executable
chmod +x "$0"

# Run main function with all arguments
main "$@"
