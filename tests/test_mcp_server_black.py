"""
Tests for the Black integration in the MCP server.
"""

import json
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask

from src.mcp_server import app as mcp_app
from src.utils.black_runner import format_code, check_formatting


@pytest.fixture
def client():
    """Create a test client for the MCP server."""
    with mcp_app.test_client() as client:
        yield client


def test_tools_list_includes_black(client):
    """Test that the tools/list endpoint includes Black."""
    # Create a JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    # Send the request
    response = client.post(
        "/mcp",
        data=json.dumps(request_data),
        content_type="application/json"
    )
    
    # Check the response
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Verify the response format
    assert "jsonrpc" in response_data
    assert response_data["jsonrpc"] == "2.0"
    assert "id" in response_data
    assert response_data["id"] == 1
    assert "result" in response_data
    
    # Verify the tools list
    result = response_data["result"]
    assert "tools" in result
    
    # Check that Black is in the tools list
    black_tool = None
    for tool in result["tools"]:
        if tool["name"] == "black":
            black_tool = tool
            break
    
    assert black_tool is not None
    assert "description" in black_tool
    assert "version" in black_tool
    assert "capabilities" in black_tool
    assert "formatting" in black_tool["capabilities"]


@patch("src.mcp_server.format_code")
def test_tools_call_black_format(mock_format_code, client):
    """Test that the tools/call endpoint can format code with Black."""
    # Sample code
    code = "def example(a,b): return a+b"
    
    # Mock the format_code function
    formatted_code = "def example(a, b):\n    return a + b\n"
    mock_format_code.return_value = {
        "formatted_code": formatted_code,
        "success": True,
        "already_formatted": False,
        "filename": "temp.py",
        "summary": {
            "line_length": 88,
            "skip_string_normalization": False
        }
    }
    
    # Create a JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "black",
            "args": {
                "code": code,
                "operation": "format",
                "line_length": 88
            }
        }
    }
    
    # Send the request
    response = client.post(
        "/mcp",
        data=json.dumps(request_data),
        content_type="application/json"
    )
    
    # Check the response
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Verify the response format
    assert "jsonrpc" in response_data
    assert response_data["jsonrpc"] == "2.0"
    assert "id" in response_data
    assert response_data["id"] == 1
    assert "result" in response_data
    
    # Verify the result
    result = response_data["result"]
    assert result["status"] == "success"
    assert "result" in result
    assert result["result"]["formatted_code"] == formatted_code
    assert result["result"]["success"] is True
    
    # Verify the format_code function was called with the correct arguments
    mock_format_code.assert_called_once_with(
        code,
        line_length=88,
        skip_string_normalization=None
    )


@patch("src.mcp_server.check_formatting")
def test_tools_call_black_check(mock_check_formatting, client):
    """Test that the tools/call endpoint can check code formatting with Black."""
    # Sample code
    code = "def example(a,b): return a+b"
    
    # Mock the check_formatting function
    mock_check_formatting.return_value = {
        "is_formatted": False,
        "diff": "--- temp.py\n+++ temp.py\n@@ -1 +1,2 @@\n-def example(a,b): return a+b\n+def example(a, b):\n+    return a + b",
        "filename": "temp.py",
        "summary": {
            "line_length": 88,
            "skip_string_normalization": False
        }
    }
    
    # Create a JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "black",
            "args": {
                "code": code,
                "operation": "check",
                "line_length": 88
            }
        }
    }
    
    # Send the request
    response = client.post(
        "/mcp",
        data=json.dumps(request_data),
        content_type="application/json"
    )
    
    # Check the response
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Verify the response format
    assert "jsonrpc" in response_data
    assert response_data["jsonrpc"] == "2.0"
    assert "id" in response_data
    assert response_data["id"] == 1
    assert "result" in response_data
    
    # Verify the result
    result = response_data["result"]
    assert result["status"] == "success"
    assert "result" in result
    assert result["result"]["is_formatted"] is False
    assert "diff" in result["result"]
    
    # Verify the check_formatting function was called with the correct arguments
    mock_check_formatting.assert_called_once_with(
        code,
        line_length=88,
        skip_string_normalization=None
    )


def test_tools_call_black_invalid_operation(client):
    """Test the tools/call endpoint with an invalid operation for Black."""
    # Create a JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "black",
            "args": {
                "code": "def example(): pass",
                "operation": "invalid"
            }
        }
    }
    
    # Send the request
    response = client.post(
        "/mcp",
        data=json.dumps(request_data),
        content_type="application/json"
    )
    
    # Check the response
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Verify the result indicates an error
    result = response_data["result"]
    assert result["status"] == "error"
    assert "message" in result
    assert "Unknown operation" in result["message"] 