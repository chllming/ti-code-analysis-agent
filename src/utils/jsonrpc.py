"""
JSON-RPC 2.0 utilities for the MCP server.

This module provides utilities for validating and working with JSON-RPC 2.0 requests.
"""

import json
from typing import Any, Dict, Optional, Union

import jsonschema

# JSON-RPC 2.0 request schema
JSONRPC_REQUEST_SCHEMA = {
    "type": "object",
    "required": ["jsonrpc", "method"],
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string", "minLength": 1},
        "params": {"type": "object"},
        "id": {"anyOf": [{"type": "string"}, {"type": "number"}, {"type": "null"}]},
    },
}

# Schema for the initialize method
INITIALIZE_METHOD_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

# Schema for the tools/list method
TOOLS_LIST_METHOD_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

# Schema for the tools/call method
TOOLS_CALL_METHOD_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "tool": {"type": "string"},
        "args": {"type": "object"},
        "code": {"type": "string"}
    },
    "anyOf": [
        {"required": ["name", "args"]},
        {"required": ["tool", "args"]},
        {"required": ["name", "code"]},
        {"required": ["tool", "code"]}
    ]
}

# Map of method names to their parameter schemas
METHOD_SCHEMA_MAP = {
    "initialize": INITIALIZE_METHOD_SCHEMA,
    "tools/list": TOOLS_LIST_METHOD_SCHEMA,
    "tools/call": TOOLS_CALL_METHOD_SCHEMA,
}


def validate_jsonrpc_request(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate a JSON-RPC 2.0 request.
    
    Args:
        data: The JSON-RPC request to validate
        
    Returns:
        None if the request is valid, or an error response if invalid
    """
    try:
        jsonschema.validate(instance=data, schema=JSONRPC_REQUEST_SCHEMA)
        
        # Validate method-specific parameters if present
        method = data.get("method")
        params = data.get("params", {})
        
        if method in METHOD_SCHEMA_MAP and params:
            jsonschema.validate(instance=params, schema=METHOD_SCHEMA_MAP[method])
            
        return None
    except jsonschema.exceptions.ValidationError as e:
        return {
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "error": {
                "code": -32600,  # Invalid request
                "message": f"Invalid request: {str(e)}",
            },
        }


def parse_jsonrpc_request(request_str: str) -> Union[Dict[str, Any], Dict[str, Any]]:
    """
    Parse a JSON-RPC 2.0 request string.
    
    Args:
        request_str: The JSON-RPC request string to parse
        
    Returns:
        The parsed JSON-RPC request, or an error response if parsing fails
    """
    try:
        data = json.loads(request_str)
        return data
    except json.JSONDecodeError as e:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,  # Parse error
                "message": f"Parse error: {str(e)}",
            },
        } 