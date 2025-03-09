#!/usr/bin/env python3
"""
Test the Flake8 analysis functionality of the MCP server.
"""

import json
import requests
import sys

# MCP server URL
MCP_URL = "http://localhost:5001/mcp"

def read_code_file(filename):
    """Read code from a file."""
    with open(filename, 'r') as f:
        return f.read()

def send_tools_call(code):
    """Send a tools/call request to analyze the provided code."""
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {
                "code": code
            }
        }
    }
    
    try:
        print("Sending code to MCP server for Flake8 analysis...")
        response = requests.post(MCP_URL, json=payload, timeout=10)
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def main():
    """Run the test."""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        code = read_code_file(filename)
    else:
        print("No file specified, using example code...")
        code = """def example():
  x=1+2
  print('hello world')
  return None"""
    
    # Send the code for analysis
    result = send_tools_call(code)
    
    # Display results
    print("\nAnalysis Results:")
    print(json.dumps(result, indent=2))
    
    # Check if we received actual analysis results
    if "result" in result and "result" in result["result"] and "issues" in result["result"]["result"]:
        issues = result["result"]["result"]["issues"]
        if issues:
            print(f"\nFound {len(issues)} issues:")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. Line {issue.get('line', '?')}, Column {issue.get('column', '?')}: {issue.get('message', '?')} ({issue.get('code', '?')})")
        else:
            print("\nNo issues found. Code passes Flake8 checks!")
    elif "error" in result:
        print(f"\nError: {result['error']}")
    else:
        print("\nUnexpected response format.")

if __name__ == "__main__":
    main() 