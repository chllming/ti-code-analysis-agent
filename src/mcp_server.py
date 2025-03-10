#!/usr/bin/env python3
"""
MCP Server - Model Command Protocol implementation for code analysis tools.

This server implements the JSON-RPC 2.0 protocol to provide a standardized way
for Cursor IDE to discover and execute code analysis tools like Flake8.
"""

import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, g, current_app, stream_with_context

from .utils.jsonrpc import validate_jsonrpc_request
from .utils.file_handler import TempFileManager
from .utils.flake8_runner import analyze_code as flake8_analyze_code
from .utils.black_runner import format_code, check_formatting
from .utils.bandit_runner import analyze_code as bandit_analyze_code
from .utils.structured_logging import configure_logging, LoggingMiddleware
from .utils.metrics import get_metrics_store
from .utils.sse_manager import sse_manager
from .utils.sse_jsonrpc_handler import SSEJsonRpcHandler, sse_jsonrpc_handler

# Load environment variables
load_dotenv()

# Configure logging with structured JSON format
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
enable_json_logs = os.getenv("ENABLE_JSON_LOGS", "true").lower() == "true"
logger = configure_logging(
    app_name="mcp_server",
    log_level=getattr(logging, LOG_LEVEL.upper()),
    enable_json=enable_json_logs
)

# Set up Flask app
app = Flask(__name__)

# Configure from environment
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "5000"))
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/mcp_temp")
SSE_HEARTBEAT_INTERVAL = int(os.getenv("SSE_HEARTBEAT_INTERVAL", "30"))

# Apply logging middleware
app.wsgi_app = LoggingMiddleware(app.wsgi_app, logger)

# Get metrics store
metrics_store = get_metrics_store()

# JSON-RPC error codes
ERROR_PARSE_ERROR = -32700
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602
ERROR_INTERNAL_ERROR = -32603


@app.before_request
def before_request():
    """Set up request context for metrics."""
    g.request_id = str(uuid.uuid4())
    g.start_time = os.environ.get('REQUEST_START_TIME')
    
    # Start metrics tracking
    if request.path == '/mcp' and request.method == 'POST':
        try:
            # For JSON-RPC requests, track the method if available
            data = request.get_json(silent=True)
            method = data.get('method', 'unknown') if data else 'unknown'
            metrics_store.start_request(g.request_id, method)
        except:
            # Fall back to path-based tracking if JSON parsing fails
            metrics_store.start_request(g.request_id, f"{request.method} {request.path}")
    else:
        # For regular HTTP requests
        metrics_store.start_request(g.request_id, f"{request.method} {request.path}")


@app.after_request
def after_request(response):
    """Update metrics after request completion and add CORS headers."""
    if hasattr(g, 'request_id'):
        is_error = response.status_code >= 400
        metrics_store.end_request(g.request_id, response.status_code, is_error)
    
    # Add CORS headers to allow Cursor to communicate with the server
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
    
    return response


def create_error_response(
    request_id: Optional[Union[str, int]], code: int, message: str, data: Any = None
) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 error response."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }
    
    if data is not None:
        response["error"]["data"] = data
    
    return response


def create_success_response(request_id: Optional[Union[str, int]], result: Any) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 success response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }


def handle_initialize() -> Dict[str, Any]:
    """Handle the initialize method."""
    logger.info("Handling initialize method")
    return {
        "name": "MCP Server",
        "version": "0.1.0",
        "capabilities": ["tools/list", "tools/call"],
    }


def handle_tools_list() -> Dict[str, Any]:
    """Handle the tools/list method."""
    logger.info("Handling tools/list method")
    return {
        "tools": [
            {
                "name": "flake8",
                "description": "Python code linter that checks for style and syntax errors",
                "version": "6.0.0",
                "capabilities": ["linting", "style-checking"]
            },
            {
                "name": "black",
                "description": "Python code formatter that enforces a consistent style",
                "version": "23.0.0",
                "capabilities": ["formatting", "style-enforcement"]
            },
            {
                "name": "bandit",
                "description": "Python security analysis that finds common security issues",
                "version": "1.7.0",
                "capabilities": ["security", "vulnerability-detection"]
            }
        ]
    }


def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the tools/call method."""
    # Support both 'name' and 'tool' parameters for flexibility
    tool_name = params.get("name") or params.get("tool")
    tool_args = params.get("args", {})
    
    logger.info(f"Handling tools/call method for tool: {tool_name}")
    
    # Extract code from arguments (either directly in params or inside args)
    code = tool_args.get("code") or params.get("code")
    if not code:
        logger.warning("No code provided for analysis")
        return {"status": "error", "message": "No code provided for analysis"}
    
    try:
        if tool_name == "flake8":
            # Run Flake8 analysis
            logger.info("Running Flake8 analysis")
            result = flake8_analyze_code(code)
            logger.info(f"Analysis complete, found {result.get('summary', {}).get('totalIssues', 0)} issues")
            return {"status": "success", "result": result}
        
        elif tool_name == "black":
            # Determine the operation (format or check)
            operation = tool_args.get("operation", "format")
            line_length = tool_args.get("line_length")
            skip_string_normalization = tool_args.get("skip_string_normalization")
            
            if line_length and isinstance(line_length, str):
                try:
                    line_length = int(line_length)
                except ValueError:
                    line_length = None
            
            if operation == "format":
                # Format the code with Black
                logger.info("Running Black formatter")
                result = format_code(
                    code, 
                    line_length=line_length,
                    skip_string_normalization=skip_string_normalization
                )
                logger.info(f"Formatting complete, success: {result.get('success', False)}")
                return {"status": "success", "result": result}
            
            elif operation == "check":
                # Check if code is formatted according to Black's standards
                logger.info("Running Black format check")
                result = check_formatting(
                    code,
                    line_length=line_length,
                    skip_string_normalization=skip_string_normalization
                )
                logger.info(f"Check complete, is formatted: {result.get('is_formatted', False)}")
                return {"status": "success", "result": result}
            
            else:
                logger.warning(f"Unknown operation for Black: {operation}")
                return {"status": "error", "message": f"Unknown operation: {operation}"}
        
        elif tool_name == "bandit":
            # Run Bandit security analysis
            logger.info("Running Bandit security analysis")
            
            # Get optional configuration
            config_path = tool_args.get("config_path")
            severity = tool_args.get("severity")
            confidence = tool_args.get("confidence")
            
            result = bandit_analyze_code(
                code,
                config_path=config_path,
                severity=severity,
                confidence=confidence
            )
            
            total_issues = result.get("summary", {}).get("totalIssues", 0)
            logger.info(f"Analysis complete, found {total_issues} security issues")
            return {"status": "success", "result": result}
        
        else:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
        
    except Exception as e:
        logger.exception(f"Error while processing tool {tool_name}: {str(e)}")
        return {"status": "error", "message": f"Processing error: {str(e)}"}


def handle_jsonrpc(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a JSON-RPC 2.0 request and return a response."""
    # Validate the JSON-RPC request
    validation_error = validate_jsonrpc_request(request_data)
    if validation_error:
        logger.warning(f"Invalid JSON-RPC request: {validation_error}")
        return validation_error
    
    # Extract request details
    request_id = request_data.get("id")
    method = request_data.get("method")
    params = request_data.get("params", {})
    
    logger.info(f"Processing JSON-RPC method: {method}", extra={"request_id": request_id})
    
    # Process the method
    try:
        if method == "initialize":
            result = handle_initialize()
            return create_success_response(request_id, result)
        
        elif method == "tools/list":
            result = handle_tools_list()
            return create_success_response(request_id, result)
        
        elif method == "tools/call":
            result = handle_tools_call(params)
            return create_success_response(request_id, result)
        
        else:
            logger.warning(f"Method not found: {method}")
            return create_error_response(
                request_id, ERROR_METHOD_NOT_FOUND, f"Method not found: {method}"
            )
    
    except Exception as e:
        logger.exception(f"Error processing method {method}: {str(e)}")
        return create_error_response(
            request_id, ERROR_INTERNAL_ERROR, f"Internal error: {str(e)}"
        )


@app.route("/mcp", methods=["POST"])
def mcp_endpoint() -> Response:
    """
    Main MCP endpoint that handles JSON-RPC requests.
    """
    # Track request in metrics
    request_id = str(uuid.uuid4())
    g.request_id = request_id
    metrics_store.start_request(request_id, request.method)
    
    # Process the request
    try:
        if not request.is_json:
            logger.warning("Request is not JSON", extra={"request_id": request_id})
            return jsonify(create_error_response(None, -32700, "Parse error: Request must be JSON")), 400
        
        request_data = request.get_json()
        response_data = handle_jsonrpc(request_data)
        return jsonify(response_data)
    except Exception as e:
        logger.exception("Unexpected error", extra={"request_id": request_id, "error": str(e)})
        return jsonify(create_error_response(None, -32603, f"Internal error: {str(e)}")), 500


@app.route("/mcp", methods=["OPTIONS"])
def mcp_options() -> Response:
    """
    Handle OPTIONS requests for CORS preflight.
    """
    return "", 200


@app.route("/health", methods=["GET"])
def health_check() -> Response:
    """Health check endpoint for monitoring."""
    logger.debug("Health check requested")
    return jsonify({
        "status": "healthy",
        "version": "0.1.0",
        "uptime_seconds": metrics_store.uptime_seconds
    })


@app.route("/metrics", methods=["GET"])
def metrics() -> Response:
    """Metrics endpoint for monitoring."""
    logger.debug("Metrics requested")
    return jsonify(metrics_store.get_metrics())


@app.route('/sse', methods=['GET'])
def sse_connect() -> Response:
    """
    Establish an SSE connection for bidirectional communication.
    This endpoint allows Cursor IDE to connect via SSE for real-time
    communication using the JSON-RPC protocol.
    """
    # Register a new client
    client_id = sse_manager.register_client()
    logger.info(f"New SSE connection established: {client_id}")
    
    # Add this connection to metrics - using request tracking instead of counter
    request_id = str(uuid.uuid4())
    metrics_store.start_request(request_id, "SSE_CONNECT")
    
    @stream_with_context
    def event_stream():
        """Generate SSE event stream for this client."""
        # Send initial connection message
        connection_message = sse_manager.format_sse_message(
            json.dumps({"status": "connected", "clientId": client_id}),
            event="connection"
        )
        yield connection_message
        
        # Loop to send messages from the queue and heartbeats
        try:
            client = sse_manager.get_client(client_id)
            if not client:
                logger.error(f"Client {client_id} not found after registration")
                return
                
            heartbeat_count = 0
            
            while client.connected:
                # Check for messages with a timeout
                message = client.get_message(timeout=SSE_HEARTBEAT_INTERVAL)
                
                if message:
                    # We have a message to send
                    sse_message = sse_manager.format_sse_message(
                        message["data"],
                        event=message["event"]
                    )
                    yield sse_message
                else:
                    # No message, send heartbeat
                    heartbeat_count += 1
                    heartbeat = sse_manager.format_sse_message(
                        json.dumps({"type": "heartbeat", "count": heartbeat_count}),
                        event="heartbeat"
                    )
                    yield heartbeat
        
        except GeneratorExit:
            # Client disconnected
            logger.info(f"SSE client disconnected: {client_id}")
        except Exception as e:
            logger.exception(f"Error in SSE stream for {client_id}: {str(e)}")
        finally:
            # Clean up the client
            sse_manager.unregister_client(client_id)
            # Record completion of the SSE connection
            metrics_store.end_request(request_id, 200)

    # Configure the response as an event stream
    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('Connection', 'keep-alive')
    response.headers.add('X-Accel-Buffering', 'no')  # Disable buffering for nginx
    return response


@app.route('/sse/<client_id>', methods=['POST'])
def sse_message(client_id: str) -> Response:
    """
    Handle incoming messages from SSE clients.
    This endpoint allows clients to send JSON-RPC requests over HTTP
    while receiving responses via the SSE connection.
    """
    # Verify the client exists
    client = sse_manager.get_client(client_id)
    if not client:
        logger.warning(f"Message received for unknown client: {client_id}")
        return jsonify({"status": "error", "message": "Unknown client ID"}), 404
    
    # Process the message
    try:
        if not request.is_json:
            logger.warning(f"Non-JSON message received from client {client_id}")
            return jsonify({"status": "error", "message": "Message must be JSON"}), 400
        
        # Get the message content
        message_data = request.get_json()
        
        # Handle JSON-RPC message
        if isinstance(message_data, dict) and "jsonrpc" in message_data:
            # Process JSON-RPC request and send response via SSE
            global sse_jsonrpc_handler
            if sse_jsonrpc_handler:
                sse_jsonrpc_handler.process_message(client_id, json.dumps(message_data))
                return jsonify({"status": "processing"})
            else:
                logger.error("SSE JSON-RPC handler not initialized")
                return jsonify({"status": "error", "message": "Server configuration error"}), 500
        else:
            # Unknown message format
            logger.warning(f"Unknown message format from client {client_id}")
            return jsonify({"status": "error", "message": "Unknown message format"}), 400
    
    except Exception as e:
        logger.exception(f"Error processing message from client {client_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


def init_app():
    """Initialize the application with all necessary components."""
    global sse_jsonrpc_handler
    
    # Initialize SSE JSON-RPC handler with our existing handler function
    sse_jsonrpc_handler = SSEJsonRpcHandler(handle_jsonrpc)
    
    logger.info("MCP Server initialized with SSE support")
    return app


if __name__ == "__main__":
    # Initialize the application
    init_app()
    
    # Start server
    logger.info(f"Starting MCP Server on {MCP_HOST}:{MCP_PORT}")
    app.run(host=MCP_HOST, port=MCP_PORT, debug=(LOG_LEVEL.upper() == "DEBUG")) 