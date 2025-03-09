"""
Tests for the Bandit integration in the MCP server.
"""

import json
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask

from src.mcp_server import app as mcp_app
from src.utils.bandit_runner import analyze_code


@pytest.fixture
def client():
    """Create a test client for the MCP server."""
    with mcp_app.test_client() as client:
        yield client


def test_tools_list_includes_bandit(client):
    """Test that the tools/list endpoint includes Bandit."""
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
    
    # Check that Bandit is in the tools list
    bandit_tool = None
    for tool in result["tools"]:
        if tool["name"] == "bandit":
            bandit_tool = tool
            break
    
    assert bandit_tool is not None
    assert "description" in bandit_tool
    assert "version" in bandit_tool
    assert "capabilities" in bandit_tool
    assert "security" in bandit_tool["capabilities"]
    assert "vulnerability-detection" in bandit_tool["capabilities"]


@patch("src.mcp_server.bandit_analyze_code")
def test_tools_call_bandit(mock_analyze_code, client):
    """Test that the tools/call endpoint can analyze code with Bandit."""
    # Sample vulnerable code
    code = """
    import pickle
    
    def load_data(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)  # Security issue
    """
    
    # Mock the analyze_code function
    mock_analyze_code.return_value = {
        "issues": [
            {
                "file": "temp.py",
                "line": 6,
                "code": "B301",
                "severity": "HIGH",
                "confidence": "HIGH",
                "message": "Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.",
                "more_info": "https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b301-pickle"
            }
        ],
        "summary": {
            "totalIssues": 1,
            "severityCounts": {
                "HIGH": 1,
                "MEDIUM": 0,
                "LOW": 0
            }
        }
    }
    
    # Create a JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "bandit",
            "args": {
                "code": code
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
    assert result["result"]["summary"]["totalIssues"] == 1
    assert len(result["result"]["issues"]) == 1
    assert result["result"]["issues"][0]["code"] == "B301"
    
    # Verify the analyze_code function was called with the correct arguments
    mock_analyze_code.assert_called_once_with(
        code,
        config_path=None,
        severity=None,
        confidence=None
    )


@patch("src.mcp_server.bandit_analyze_code")
def test_tools_call_bandit_with_config(mock_analyze_code, client):
    """Test that the tools/call endpoint can analyze code with Bandit using custom configuration."""
    # Sample vulnerable code
    code = """
    import pickle
    
    def load_data(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)  # Security issue
    """
    
    # Mock the analyze_code function
    mock_analyze_code.return_value = {
        "issues": [
            {
                "file": "temp.py",
                "line": 6,
                "code": "B301",
                "severity": "HIGH",
                "confidence": "HIGH",
                "message": "Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.",
                "more_info": "https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b301-pickle"
            }
        ],
        "summary": {
            "totalIssues": 1,
            "severityCounts": {
                "HIGH": 1,
                "MEDIUM": 0,
                "LOW": 0
            }
        }
    }
    
    # Create a JSON-RPC request with custom configuration
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "bandit",
            "args": {
                "code": code,
                "severity": "HIGH",
                "confidence": "HIGH"
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
    
    # Verify the result
    result = response_data["result"]
    assert result["status"] == "success"
    
    # Verify the analyze_code function was called with the correct arguments
    mock_analyze_code.assert_called_once_with(
        code,
        config_path=None,
        severity="HIGH",
        confidence="HIGH"
    ) 