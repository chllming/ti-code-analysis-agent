"""
Integration test for Bandit security analysis using the MCP server.

This test verifies that the Bandit security analysis integration works correctly
by sending actual requests to the MCP server.
"""

import json
import os
import requests
import sys
from pathlib import Path

# Sample code with potential security issues
VULNERABLE_CODE = '''
import pickle
import yaml
import subprocess

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Security issue: B301 pickle

def parse_yaml(data):
    return yaml.load(data)  # Security issue: B506 yaml.load

def run_command(cmd):
    return subprocess.call(cmd, shell=True)  # Security issue: B602 shell=True
'''

# Sample code without security issues
SAFE_CODE = '''
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
'''


def main():
    """Run the integration test."""
    # Get the MCP server URL from environment or use default
    mcp_url = os.environ.get("MCP_URL", "http://localhost:5000/mcp")
    
    print(f"Testing Bandit security analysis integration with MCP server at {mcp_url}")
    
    # Step 1: Check that Bandit is in the tools list
    print("\nStep 1: Checking if Bandit is in the tools list...")
    tools_list_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        response = requests.post(
            mcp_url,
            json=tools_list_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        tools_data = response.json()
        print(f"Got response: {json.dumps(tools_data, indent=2)}")
        
        # Check if Bandit is in the tools list
        bandit_tool = None
        for tool in tools_data.get("result", {}).get("tools", []):
            if tool.get("name") == "bandit":
                bandit_tool = tool
                break
        
        if bandit_tool:
            print("✅ Bandit tool found in tools list")
        else:
            print("❌ Bandit tool not found in tools list")
            return 1
    
    except Exception as e:
        print(f"❌ Error checking tools list: {str(e)}")
        return 1
    
    # Step 2: Analyze code with Bandit (check if it works, not specific results)
    print("\nStep 2: Verifying Bandit analysis functionality...")
    analyze_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "bandit",
            "args": {
                "code": VULNERABLE_CODE
            }
        }
    }
    
    try:
        response = requests.post(
            mcp_url,
            json=analyze_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        analyze_data = response.json()
        result = analyze_data.get("result", {})
        
        if result.get("status") == "success":
            print("✅ Successfully analyzed code with Bandit")
            print(f"Summary: {json.dumps(result.get('result', {}).get('summary', {}), indent=2)}")
            print(f"Found {len(result.get('result', {}).get('issues', []))} issues")
            
            # Print first issue if any found
            issues = result.get('result', {}).get('issues', [])
            if issues:
                print(f"\nExample issue: {json.dumps(issues[0], indent=2)}")
        else:
            print(f"❌ Error analyzing code: {json.dumps(result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error analyzing code: {str(e)}")
        return 1
    
    # Step 3: Verify configuration options work
    print("\nStep 3: Verifying Bandit configuration options...")
    config_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "bandit",
            "args": {
                "code": VULNERABLE_CODE,
                "severity": "HIGH",
                "confidence": "HIGH"
            }
        }
    }
    
    try:
        response = requests.post(
            mcp_url,
            json=config_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        config_data = response.json()
        result = config_data.get("result", {})
        
        if result.get("status") == "success":
            print("✅ Successfully analyzed code with custom configuration")
        else:
            print(f"❌ Error analyzing code with custom configuration: {json.dumps(result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error analyzing code with custom configuration: {str(e)}")
        return 1
    
    print("\n✅ All tests passed! Bandit security analysis is correctly integrated with the MCP server.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 