"""
Tests for the MCP server.

This module contains tests for the MCP server JSON-RPC 2.0 implementation.
"""

import json
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask

# Import from the src package
import src.mcp_server
from src.mcp_server import app, create_error_response, create_success_response


@pytest.fixture
def client():
    """Create a test client for the MCP server."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data


def test_mcp_endpoint_wrong_content_type(client):
    """Test the MCP endpoint with the wrong content type."""
    response = client.post('/mcp', data=json.dumps({}), content_type='text/plain')
    assert response.status_code == 415
    data = json.loads(response.data)
    assert data['error']['code'] == -32700


def test_mcp_endpoint_invalid_json(client):
    """Test the MCP endpoint with invalid JSON."""
    response = client.post('/mcp', data='{ invalid json', content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == -32700


def test_initialize_method(client):
    """Test the initialize method."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize"
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['jsonrpc'] == '2.0'
    assert data['id'] == 1
    assert 'result' in data
    assert data['result']['name'] == 'MCP Server'
    assert 'capabilities' in data['result']
    assert 'tools/list' in data['result']['capabilities']
    assert 'tools/call' in data['result']['capabilities']


def test_tools_list_method(client):
    """Test the tools/list method."""
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['jsonrpc'] == '2.0'
    assert data['id'] == 2
    assert 'result' in data
    assert 'tools' in data['result']
    assert len(data['result']['tools']) > 0
    assert data['result']['tools'][0]['name'] == 'flake8'


@patch('src.mcp_server.handle_tools_call')
def test_tools_call_method(mock_handle_tools_call, client):
    """Test the tools/call method."""
    # Set up the mock
    mock_handle_tools_call.return_value = {
        "result": {
            "issues": [],
            "summary": {
                "totalIssues": 0,
                "filesAnalyzed": 1
            }
        },
        "status": "success"
    }
    
    # Create the payload
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {
                "code": "def test(): pass"
            }
        }
    }
    
    # Send the request
    response = client.post('/mcp', json=payload)
    
    # Verify the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['jsonrpc'] == '2.0'
    assert data['id'] == 3
    assert 'result' in data
    assert 'status' in data['result']
    assert data['result']['status'] == 'success'
    
    # Verify the mock was called with the correct parameters
    mock_handle_tools_call.assert_called_once()
    assert mock_handle_tools_call.call_args[0][0] == payload['params']


@patch('src.mcp_server.flake8_analyze_code')
def test_handle_tools_call(mock_analyze_code, client):
    """Test handling a tools/call request."""
    # Set up the mock
    mock_analyze_code.return_value = {
        "issues": [],
        "summary": {
            "totalIssues": 0
        }
    }
    
    # Create a request to execute Flake8
    payload = {
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
    
    # Send the request
    response = client.post('/mcp', json=payload)
    
    # Check the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'result' in data
    assert data['result']['status'] == 'success'
    assert 'result' in data['result']
    assert 'issues' in data['result']['result']
    assert 'summary' in data['result']['result']
    
    # Verify the analyze_code function was called
    mock_analyze_code.assert_called_once_with("def test(): pass")


def test_tools_call_method_missing_code(client):
    """Test the tools/call method with missing code."""
    payload = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {}
        }
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'result' in data
    assert data['result']['status'] == 'error'
    assert 'message' in data['result']
    assert 'No code provided for analysis' in data['result']['message']


def test_tools_call_method_unknown_tool(client):
    """Test the tools/call method with an unknown tool."""
    payload = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "unknown_tool",
            "args": {
                "code": "def test(): pass"
            }
        }
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'result' in data
    assert data['result']['status'] == 'error'
    assert 'message' in data['result']
    assert 'Unknown tool' in data['result']['message']


def test_method_not_found(client):
    """Test calling a method that doesn't exist."""
    payload = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "non_existent_method"
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['jsonrpc'] == '2.0'
    assert data['id'] == 7
    assert 'error' in data
    assert data['error']['code'] == -32601  # Method not found


def test_invalid_jsonrpc_version(client):
    """Test with an invalid JSON-RPC version."""
    payload = {
        "jsonrpc": "1.0",
        "id": 8,
        "method": "initialize"
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['jsonrpc'] == '2.0'
    assert data['id'] == 8
    assert 'error' in data
    assert data['error']['code'] == -32600  # Invalid Request


def test_missing_method(client):
    """Test with a missing method."""
    payload = {
        "jsonrpc": "2.0",
        "id": 9
    }
    response = client.post('/mcp', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['jsonrpc'] == '2.0'
    assert data['id'] == 9
    assert 'error' in data
    assert data['error']['code'] == -32600  # Invalid Request


def test_create_success_response():
    """Test the create_success_response function."""
    response = create_success_response(1, {"test": "data"})
    assert response['jsonrpc'] == '2.0'
    assert response['id'] == 1
    assert response['result'] == {"test": "data"}


def test_create_error_response():
    """Test the create_error_response function."""
    response = create_error_response(1, -32600, "Test error")
    assert response['jsonrpc'] == '2.0'
    assert response['id'] == 1
    assert response['error']['code'] == -32600
    assert response['error']['message'] == "Test error"
    
    # Test with additional data
    response = create_error_response(1, -32600, "Test error", {"details": "More info"})
    assert response['error']['data'] == {"details": "More info"} 