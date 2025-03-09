#!/usr/bin/env python3
"""
Test Cursor IDE connection to the MCP server.

This script sends test requests to the MCP server to verify that it's working
and can be connected to from Cursor IDE.
"""

import json
import sys
import requests

# Default MCP server URL
MCP_URL = "http://localhost:5001/mcp"


def send_request(method, params=None):
    """Send a JSON-RPC request to the MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method
    }
    
    if params:
        payload["params"] = params
    
    try:
        response = requests.post(MCP_URL, json=payload, timeout=5)
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}


def test_initialize():
    """Test the initialize method."""
    print("\nTesting 'initialize' method...")
    response = send_request("initialize")
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False
    
    print(f"✅ Server name: {response['result']['name']}")
    print(f"✅ Server version: {response['result']['version']}")
    print(f"✅ Capabilities: {', '.join(response['result']['capabilities'])}")
    return True


def test_tools_list():
    """Test the tools/list method."""
    print("\nTesting 'tools/list' method...")
    response = send_request("tools/list")
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False
    
    tools = response["result"]["tools"]
    print(f"✅ Available tools: {len(tools)}")
    
    for tool in tools:
        print(f"  - {tool['name']} (v{tool['version']}): {tool['description']}")
    
    return True


def main():
    """Run the tests."""
    print(f"Testing connection to MCP server at {MCP_URL}")
    
    # Test server health
    try:
        health_url = MCP_URL.replace("/mcp", "/health")
        health_response = requests.get(health_url, timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"\n✅ Server is healthy (version: {health_data.get('version', 'unknown')})")
        else:
            print(f"\n❌ Server health check failed: {health_response.status_code}")
            return 1
    except requests.RequestException as e:
        print(f"\n❌ Server health check failed: {str(e)}")
        print("Make sure the MCP server is running.")
        return 1
    
    # Test JSON-RPC methods
    initialize_ok = test_initialize()
    tools_list_ok = test_tools_list()
    
    if initialize_ok and tools_list_ok:
        print("\n✅ All tests passed! The MCP server is ready for Cursor IDE integration.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        MCP_URL = sys.argv[1]
    
    sys.exit(main()) 