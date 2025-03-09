#!/usr/bin/env python3
"""
Test the tools/call endpoint of the MCP server.

This is a focused script for debugging issues with the tools/call endpoint.
"""

import json
import requests
import sys

# Default MCP URL
MCP_URL = "http://localhost:5001/mcp"

# Simple Python code for testing with Flake8 issues
TEST_CODE = """
def add(a, b):
  x=a+b  # Missing whitespace around operator
  y = a*b  # Too short variable name
  
  if x>10:  # Missing whitespace around operator
    return y
  else:
    return x
"""

def main():
    """Run the test for tools/call."""
    print("Testing tools/call endpoint")
    print(f"Target URL: {MCP_URL}")
    print(f"Test code:\n{TEST_CODE}")
    
    # Create the request payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {
                "code": TEST_CODE,
                "filename": "test.py"
            }
        }
    }
    
    # Send the request
    try:
        print("\nSending request...")
        print(f"Request payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(MCP_URL, json=payload, timeout=10)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response content type: {response.headers.get('Content-Type')}")
        
        result = response.json()
        print(f"Response body: {json.dumps(result, indent=2)}")
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
        else:
            print("\n✅ Success!")
            print(f"Result: {json.dumps(result.get('result', {}), indent=2)}")
        
    except requests.RequestException as e:
        print(f"\n❌ Request failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 