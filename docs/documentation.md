<!-- Generated from ti-templates version 1.0.0  on 2025-03-06 -->
# Ti-code-analysis-agent Documentation

## Resources

### Official Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

### TI Architecture References
- [TI Architecture Overview](URL)
- [Personality Pillar Documentation](URL)
- [Agency Pillar Documentation](URL)
- [Integration Guidelines](URL)

### API References
- [MCP Protocol Specification](URL)
- [Cursor MCP Integration](URL)

## Component Documentation

### Core Components

#### MCP Server
The MCP Server is a Flask-based implementation of the Model Command Protocol that enables Cursor IDE to interact with code analysis tools like Flake8. It follows the JSON-RPC 2.0 protocol to provide a standardized way to discover and execute tools.

**Interfaces:**
```typescript
interface MCPRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: Record<string, any>;
}

interface MCPResponse {
  jsonrpc: "2.0";
  id: string | number;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}
```

**Usage Example:**
```python
# Python example
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    req_data = request.json
    # Process the MCP request
    # ...
    return jsonify({
        "jsonrpc": "2.0",
        "id": req_data.get("id"),
        "result": result_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

#### Flake8 Integration
This component integrates the Flake8 linter into the MCP server, allowing Cursor to request Python code analysis and receive standardized results. It handles secure file operations and formats the output according to the MCP protocol.

**Interfaces:**
```typescript
interface Flake8Request {
  code: string;
  filename?: string;
  config?: {
    maxLineLength?: number;
    ignoredRules?: string[];
  };
}

interface Flake8Result {
  issues: Array<{
    file: string;
    line: number;
    column: number;
    code: string;
    message: string;
  }>;
  summary: {
    totalIssues: number;
    filesAnalyzed: number;
  };
}
```

**Usage Example:**
```python
# Python example
import tempfile
import subprocess
import json
from pathlib import Path

def run_flake8_analysis(code, filename="temp.py", config=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / filename
        temp_path.write_text(code)
        
        cmd = ["flake8", str(temp_path), "--format=json"]
        
        if config and "maxLineLength" in config:
            cmd.extend(["--max-line-length", str(config["maxLineLength"])])
            
        if config and "ignoredRules" in config:
            cmd.extend(["--ignore", ",".join(config["ignoredRules"])])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse and format the output
        flake8_output = json.loads(result.stdout)
        return format_flake8_results(flake8_output, filename)
```

### Integration Interfaces

#### Integration with Cursor IDE
The MCP server integrates with Cursor IDE through the MCP protocol, allowing users to run code analysis tools using natural language commands.

**Integration Points:**
- **MCP Endpoint**: Exposes `/mcp` endpoint that Cursor connects to
- **Tool Discovery**: Implements `tools/list` method for tool discovery
- **Tool Execution**: Implements `tools/call` method for executing analysis

**Interface Definition:**
```typescript
interface MCPToolsListRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: "tools/list";
}

interface MCPToolsListResponse {
  jsonrpc: "2.0";
  id: string | number;
  result: {
    tools: Array<{
      name: string;
      description: string;
      version: string;
      capabilities: string[];
    }>;
  };
}

interface MCPToolsCallRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: "tools/call";
  params: {
    name: string;
    args: Record<string, any>;
  };
}
```

**Example Flow:**
1. User enters a command in Cursor: "Run Flake8 analysis on this file"
2. Cursor sends a `tools/call` request to the MCP server
3. Server executes Flake8 on the specified code
4. Server formats and returns the analysis results
5. Cursor displays the results to the user

## Design Patterns

### Pattern 1: JSON-RPC Protocol
The MCP server follows the JSON-RPC 2.0 protocol for standardized communication with Cursor IDE.

**Implementation Example:**
```python
# Python implementation example
def handle_jsonrpc_request(request_data):
    """Handle a JSON-RPC 2.0 request."""
    # Validate JSON-RPC format
    if "jsonrpc" not in request_data or request_data["jsonrpc"] != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id", None),
            "error": {
                "code": -32600,
                "message": "Invalid Request"
            }
        }
    
    # Extract method and params
    method = request_data.get("method")
    params = request_data.get("params", {})
    
    # Call the appropriate method handler
    try:
        if method == "initialize":
            result = handle_initialize()
        elif method == "tools/list":
            result = handle_tools_list()
        elif method == "tools/call":
            result = handle_tools_call(params)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }
        
        # Return successful response
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": result
        }
    except Exception as e:
        # Handle errors
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }
```

### Pattern 2: Temporary File Management
The MCP server uses a secure pattern for handling temporary files during code analysis.

**Implementation Example:**
```python
# Python implementation example
import tempfile
import os
from contextlib import contextmanager

@contextmanager
def secure_temp_file(code, filename="temp.py"):
    """Create a secure temporary file with the given code."""
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file path
            temp_path = os.path.join(temp_dir, filename)
            
            # Write the code to the file
            with open(temp_path, "w") as f:
                f.write(code)
            
            # Yield the file path to the caller
            yield temp_path
    finally:
        # The contextmanager ensures cleanup even if exceptions occur
        pass
```

## Docker Configuration

### Container Structure
The MCP server is containerized for easy deployment and consistent execution environments. The Docker container includes the Flask server, Flake8, and all necessary dependencies.

### Environment Variables
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MCP_PORT` | Port for the MCP server | `5000` | No |
| `MCP_HOST` | Host to bind the server to | `0.0.0.0` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `FLAKE8_CONFIG` | Path to Flake8 config file | None | No |

### Volume Mounts
| Mount Point | Purpose | Persistence |
|-------------|---------|-------------|
| `/app/config` | Configuration files for the MCP server and tools | Yes |
| `/app/logs` | Log files | Yes |

### Network Configuration
The MCP server exposes port 5000 (by default) for the HTTP API. This must be accessible from the machine running Cursor IDE.

## Performance Considerations
- **Caching**: Implement result caching to avoid redundant analysis of unchanged code.
- **File Size Limits**: Set reasonable limits for file sizes to prevent resource exhaustion.
- **Asynchronous Processing**: Use async processing for handling multiple concurrent requests.

## Security Considerations
- **Code Isolation**: All analyzed code is kept in isolated temporary directories.
- **Input Validation**: Validate all inputs to prevent injection attacks.
- **Resource Limits**: Set timeouts and resource limits for tool execution.
- **Temporary File Cleanup**: Ensure all temporary files are securely deleted after analysis.

## Troubleshooting

### Common Issues

#### Issue 1: MCP Server Connection Failures
**Symptoms:**
- "Connection refused" errors in Cursor
- Timeout errors when attempting to use code analysis tools

**Resolution:**
1. Verify the MCP server is running: `docker ps` or `ps aux | grep mcp_server`
2. Check network connectivity between Cursor and the MCP server
3. Verify the port configuration matches in both Cursor settings and the MCP server

#### Issue 2: Incorrect Flake8 Results
**Symptoms:**
- Missing linting errors in results
- Unexpected linting errors being reported

**Resolution:**
1. Check the Flake8 configuration file for any custom rules
2. Verify the Python version compatibility between the code and the Flake8 environment
3. Try running Flake8 directly on the file to compare results

### Logging
The MCP server uses structured logging with configurable log levels. Logs are output to both the console and log files in the `/app/logs` directory when using Docker.

### Monitoring
The MCP server provides a `/health` endpoint for monitoring its status. It returns HTTP 200 with basic health metrics when the server is operational.

## Cursor IDE Integration

### Overview
This project uses Cursor IDE with AI-assisted development capabilities. Cursor provides intelligent code generation, refactoring, and documentation assistance specifically configured for TI projects.

### Configuration
The project includes a pre-configured Cursor setup with:

- **AI Rules**: Located in `.cursor/rules/` directory with guidelines for:
  - Core System Guidelines
  - Architecture Guidelines
  - Cursor Optimization Guidelines
  - Code Quality Guidelines
  - Language-Specific Guidelines for Python

- **Settings**: The `.cursor/settings.json` file contains optimized settings for:
  - AI model configuration
  - Code indexing patterns
  - Linting integration
  - Autocomplete behavior
  - Tool integration

- **Composer Guidance**: The AI assistant has been configured with TI-specific guidance to:
  - Follow TI architecture patterns
  - Maintain consistent coding standards
  - Implement proper error handling
  - Write comprehensive tests

### Usage
To use Cursor with this project:

1. Install Cursor IDE from https://cursor.sh/
2. Open this project in Cursor
3. Run `./scripts/setup-cursor.sh` to update your local Cursor configuration
4. Use ⌘+I (macOS) or Ctrl+I (Windows/Linux) to open Composer

#### Using Code Analysis Tools in Cursor
Once the MCP server is running and configured in Cursor, you can use natural language prompts to access code analysis features:

- **Flake8 Analysis**: "Run Flake8 analysis on this file" or "Check this Python code for style issues"
- **Detailed Review**: "Analyze @src/module.py with Flake8 and explain any issues found"
- **Future Tools**:
  - **Black Formatting**: "Format this code using Black for consistent style"
  - **Security Analysis**: "Run Bandit security analysis on this file to check for vulnerabilities"
