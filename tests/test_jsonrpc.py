"""
Tests for the JSON-RPC utilities.

This module contains tests for the JSON-RPC 2.0 utilities.
"""

import json
import pytest

from src.utils.jsonrpc import (
    JSONRPC_REQUEST_SCHEMA,
    METHOD_SCHEMA_MAP,
    parse_jsonrpc_request,
    validate_jsonrpc_request,
)


def test_jsonrpc_request_schema():
    """Test the JSON-RPC request schema."""
    assert "jsonrpc" in JSONRPC_REQUEST_SCHEMA["required"]
    assert "method" in JSONRPC_REQUEST_SCHEMA["required"]


def test_method_schema_map():
    """Test the method schema map."""
    assert "initialize" in METHOD_SCHEMA_MAP
    assert "tools/list" in METHOD_SCHEMA_MAP
    assert "tools/call" in METHOD_SCHEMA_MAP


def test_validate_jsonrpc_request_valid():
    """Test validating a valid JSON-RPC request."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize"
    }
    error = validate_jsonrpc_request(request)
    assert error is None


def test_validate_jsonrpc_request_invalid_version():
    """Test validating a JSON-RPC request with an invalid version."""
    request = {
        "jsonrpc": "1.0",
        "id": 1,
        "method": "initialize"
    }
    error = validate_jsonrpc_request(request)
    assert error is not None
    assert error["error"]["code"] == -32600


def test_validate_jsonrpc_request_missing_method():
    """Test validating a JSON-RPC request with a missing method."""
    request = {
        "jsonrpc": "2.0",
        "id": 1
    }
    error = validate_jsonrpc_request(request)
    assert error is not None
    assert error["error"]["code"] == -32600


def test_validate_jsonrpc_request_invalid_params():
    """Test validating a JSON-RPC request with invalid parameters."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            # Missing required 'name' field
            "args": {
                "code": "def test(): pass"
            }
        }
    }
    error = validate_jsonrpc_request(request)
    assert error is not None
    assert error["error"]["code"] == -32600


def test_validate_jsonrpc_request_valid_with_params():
    """Test validating a valid JSON-RPC request with parameters."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {
                "code": "def test(): pass"
            }
        }
    }
    error = validate_jsonrpc_request(request)
    assert error is None


def test_parse_jsonrpc_request_valid():
    """Test parsing a valid JSON-RPC request string."""
    request_str = '{"jsonrpc": "2.0", "id": 1, "method": "initialize"}'
    request = parse_jsonrpc_request(request_str)
    assert request["jsonrpc"] == "2.0"
    assert request["id"] == 1
    assert request["method"] == "initialize"


def test_parse_jsonrpc_request_invalid():
    """Test parsing an invalid JSON-RPC request string."""
    request_str = '{"jsonrpc": "2.0", "id": 1, "method": "initialize"'  # Missing closing brace
    request = parse_jsonrpc_request(request_str)
    assert "error" in request
    assert request["error"]["code"] == -32700  # Parse error 