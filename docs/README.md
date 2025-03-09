<!-- Generated from ti-templates version 1.0.0  on 2025-03-06 -->
# Ti-code-analysis-agent

## Overview
This repository contains the code-analysis agent component of the Tailored Intelligence architecture. It implements a Python-based Model Command Protocol (MCP) server that integrates Flake8 static code analysis directly into Cursor IDE, allowing for AI-driven code quality assessments through natural language commands.

## Architecture
This component implements parts of the Tailored Intelligence architecture:

### Personality Pillar Integration
- Enhances the AI's ability to evaluate and improve code quality through static analysis
- Provides standardized code quality feedback for the AI Code Quality Advisor component
- Enables natural language command parsing for code analysis operations

### Agency Pillar Integration
- Implements a key part of the Tool Selection Layer through the MCP protocol
- Establishes a standardized pattern for tool integration with Cursor's AI
- Demonstrates autonomous invocation and interpretation of external code quality tools

## Features
- Flask-based MCP server implementing JSON-RPC 2.0 protocol
- Flake8 integration for Python code style and quality analysis
- Secure temporary file handling for code analysis
- Standardized response formatting for AI consumption
- Natural language command integration with Cursor IDE
- Future extensions planned for Black (formatting) and Bandit (security analysis)

## Technology Stack
- Python 3.9+
- Flask 2.0.0+
- Flake8 6.0.0+
- JSON-RPC 2.0
- Docker & Docker Compose (for containerized deployment)

## Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Docker & Docker Compose (for containerized deployment)

### Standard Installation
```bash
# Clone the repository
git clone https://github.com/tailored-intelligence/ti-code-analysis-agent.git
cd ti-code-analysis-agent

# Install dependencies
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env with your configuration values

# Run the application
python src/mcp_server.py
```

### Docker Installation
```bash
# Clone the repository
git clone https://github.com/tailored-intelligence/ti-code-analysis-agent.git
cd ti-code-analysis-agent

# Configuration
cp .env.example .env
# Edit .env with your configuration values

# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## Usage
The MCP server is designed to be integrated with Cursor IDE, enabling natural language interaction with code analysis tools.

### Cursor IDE Integration
```
# In Cursor IDE Settings:
1. Navigate to Settings > MCP
2. Add MCP server URL: http://localhost:5000/mcp
3. Enable the server
```

### Example Natural Language Commands
Once integrated with Cursor, you can use commands like:

```
Run Flake8 analysis on this file.
Check if this Python code follows PEP 8 guidelines.
Analyze src/module.py with Flake8 and explain any issues.
```

### API Usage Example
If you want to use the MCP server directly through its API:

```python
# Python example
import requests
import json

def call_mcp_flake8(code, filename="example.py"):
    response = requests.post(
        "http://localhost:5000/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "flake8",
                "args": {
                    "code": code,
                    "filename": filename
                }
            }
        }
    )
    
    return response.json()

# Example usage
code = """
def example():
  print("Hello world")
  return None
"""

result = call_mcp_flake8(code)
print(json.dumps(result, indent=2))
```

## API Reference
The MCP server implements the JSON-RPC 2.0 protocol with the following methods:

### Key Components

#### MCP Endpoint
The server exposes a single `/mcp` endpoint that accepts JSON-RPC 2.0 requests.

**Methods:**
- `initialize`: Establishes a connection with the MCP server
- `tools/list`: Lists available tools (Flake8 and planned extensions)
- `tools/call`: Executes a specified tool on provided code

#### Flake8 Integration
The Flake8 integration provides Python code analysis.

**Parameters:**
- `code`: The Python code to analyze (string)
- `filename`: Optional filename for the code (default: temp.py)
- `config`: Optional configuration object for Flake8 settings

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/tailored-intelligence/ti-code-analysis-agent.git
cd ti-code-analysis-agent

# Create and activate a virtual environment
python -m venv mcp_env
source mcp_env/bin/activate  # Linux/Mac
# or
# mcp_env\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Using Docker for Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests in the container
docker-compose -f docker-compose.dev.yml exec app pytest tests/

# Stop the environment
docker-compose -f docker-compose.dev.yml down
```

### Cursor IDE Integration
This project is configured for optimal use with Cursor IDE, providing AI-powered assistance for development.

#### Cursor Setup
```bash
# Run the cursor setup script to configure your environment
./scripts/setup-cursor.sh
```

This will set up:
- AI rules tailored to this project's best practices
- Optimal cursor configuration for the codebase
- Technology-specific guidelines for Python

#### Using Cursor with this Project
For detailed information on using Cursor with this project, see:
- `CURSOR.md` in the project root
- `docs/cursor_best_practices.md` for best practices

### Project Structure
```
ti-code-analysis-agent/
├── src/                  # Source code
│   ├── mcp_server.py     # Main MCP server implementation
│   ├── flake8_tool.py    # Flake8 integration module
│   └── utils/            # Utility modules
├── tests/                # Test files
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── config/               # Configuration files
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── plan.md               # Development plan
└── progress.md           # Development progress
```

### Development Workflow
1. Check `plan.md` for the next task to implement
2. Write tests for the functionality
3. Implement the functionality
4. Run tests to verify implementation
5. Update `progress.md` with completion details
6. Commit changes with descriptive message
7. Push changes to GitHub

## Testing
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_flake8.py

# Run tests with coverage report
pytest --cov=src tests/
```

## Deployment
The MCP server can be deployed as a standalone service or as part of a larger TI environment.

### Production Deployment
```bash
# Build optimized Docker image
docker build -t ti-code-analysis-agent:prod --target production .

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing
1. Check the `plan.md` file for current development status
2. Pick a task from the upcoming tasks section
3. Create a feature branch (`git checkout -b feature/task-description`)
4. Implement the task following the test requirements
5. Update `progress.md` with your implementation details
6. Submit a pull request

## License
[License information]

## Related Projects
- [TI Core Framework]: Core components of the Tailored Intelligence architecture
- [TI Cursor Integration]: Cursor IDE integration for the TI ecosystem
