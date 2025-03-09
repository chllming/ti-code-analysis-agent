# MCP Server for Code Analysis

This repository contains a Python-based Model Command Protocol (MCP) server that integrates Flake8 static code analysis directly into Cursor IDE, allowing for AI-driven code quality assessments through natural language commands.

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tailored-intelligence/ti-code-analysis-agent.git
cd ti-code-analysis-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
# venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the environment:
```bash
cp .env.example .env
# Edit .env if needed
```

### Running the Server

```bash
python src/mcp_server.py
```

The server will start on http://localhost:5000 by default.

### Running Tests

```bash
pytest
```

For coverage report:
```bash
pytest --cov=src tests/
```

## MCP Protocol

The server implements the JSON-RPC 2.0 protocol with the following methods:

- `initialize`: Initialize the server connection
- `tools/list`: List available code analysis tools
- `tools/call`: Execute a tool on provided code (implementation in progress)

### Example Requests

#### Initialize
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize"
}
```

#### List Tools
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

#### Call Tool (not yet implemented)
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "flake8",
    "args": {
      "code": "def example():\n  print('Hello world')\n  return None"
    }
  }
}
```

## Cursor IDE Integration

Once the server is running, you can configure Cursor IDE to use it:

1. In Cursor, navigate to Settings > MCP
2. Add the MCP server URL: http://localhost:5000/mcp
3. Enable the server

You'll then be able to use natural language commands like:
- "Run Flake8 analysis on this file"
- "Check if this Python code follows PEP 8 guidelines"

## Project Structure

```
ti-code-analysis-agent/
├── src/                  # Source code
│   ├── mcp_server.py     # Main MCP server implementation
│   └── utils/            # Utility modules
│       └── jsonrpc.py    # JSON-RPC utilities
├── tests/                # Test files
├── config/               # Configuration files
│   └── flake8.ini        # Flake8 configuration
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
``` 