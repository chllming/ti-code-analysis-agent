#!/usr/bin/env python3
"""
Comprehensive MCP Server Testing Script

This script tests various aspects of the MCP server:
1. Server connectivity and health check
2. JSON-RPC methods (initialize, tools/list)
3. Code analysis with Flake8 (with both clean and problematic code)
"""

import json
import requests
import sys
import time

# MCP server URL
MCP_URL = "http://localhost:5001/mcp"

# Sample code with issues
PROBLEMATIC_CODE = """def bad_function( ):
    x=1+2 # no space around operators
    if(x>5):
        print('hello world')
        return None
    else:
        y = [1,2,3,4,5]
        print(y[0])
"""

# Sample clean code
CLEAN_CODE = """def good_function():
    \"\"\"A simple example function.\"\"\"
    x = 1 + 2
    if x > 5:
        print("Hello world")
        return True
    return False
"""

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


def test_health():
    """Test server health endpoint."""
    print("\n==== Testing Server Health ====")
    try:
        health_url = MCP_URL.replace("/mcp", "/health")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy (version: {data.get('version', 'unknown')})")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Server health check failed: {str(e)}")
        return False


def test_initialize():
    """Test the initialize method."""
    print("\n==== Testing 'initialize' Method ====")
    response = send_request("initialize")
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False
    
    if "result" in response:
        print(f"✅ Server name: {response['result']['name']}")
        print(f"✅ Server version: {response['result']['version']}")
        print(f"✅ Capabilities: {', '.join(response['result']['capabilities'])}")
        return True
    return False


def test_tools_list():
    """Test the tools/list method."""
    print("\n==== Testing 'tools/list' Method ====")
    response = send_request("tools/list")
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return False
    
    if "result" in response and "tools" in response["result"]:
        tools = response["result"]["tools"]
        print(f"✅ Available tools: {len(tools)}")
        
        for tool in tools:
            print(f"  - {tool['name']} (v{tool['version']}): {tool['description']}")
        
        return True
    print("❌ Unexpected response format")
    return False


def test_flake8_analysis(code, expected_issues=0, description=""):
    """Test the Flake8 analysis tool."""
    print(f"\n==== Testing Flake8 Analysis ({description}) ====")
    
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
        response = requests.post(MCP_URL, json=payload, timeout=10)
        result = response.json()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        if "result" in result and "result" in result["result"] and "issues" in result["result"]["result"]:
            issues = result["result"]["result"]["issues"]
            issue_count = len(issues)
            
            if expected_issues == 0 and issue_count == 0:
                print("✅ No issues found, as expected!")
                return True
            elif expected_issues > 0 and issue_count > 0:
                print(f"✅ Found {issue_count} issues, as expected!")
                # Print first 5 issues if there are many
                for i, issue in enumerate(issues[:5], 1):
                    print(f"  {i}. Line {issue.get('line', '?')}: {issue.get('message', '?')} ({issue.get('code', '?')})")
                if issue_count > 5:
                    print(f"  ... and {issue_count - 5} more issues")
                return True
            else:
                print(f"❌ Expected ~{expected_issues} issues, but found {issue_count}")
                return False
        
        print("❌ Unexpected response format")
        return False
    
    except requests.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("===============================================")
    print("    Comprehensive MCP Server Test Suite")
    print("===============================================")
    
    # Run all tests
    health_ok = test_health()
    if not health_ok:
        print("\n❌ Health check failed. Cannot proceed with further tests.")
        return 1
    
    initialize_ok = test_initialize()
    tools_list_ok = test_tools_list()
    
    # Small delay between tests
    time.sleep(0.5)
    
    # Test code analysis
    clean_analysis_ok = test_flake8_analysis(CLEAN_CODE, 0, "Clean Code")
    problem_analysis_ok = test_flake8_analysis(PROBLEMATIC_CODE, 8, "Problematic Code")
    
    # Summarize results
    print("\n===============================================")
    print("              Test Results")
    print("===============================================")
    print(f"Health Check:      {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Initialize Method: {'✅ PASS' if initialize_ok else '❌ FAIL'}")
    print(f"Tools List Method: {'✅ PASS' if tools_list_ok else '❌ FAIL'}")
    print(f"Clean Code:        {'✅ PASS' if clean_analysis_ok else '❌ FAIL'}")
    print(f"Problematic Code:  {'✅ PASS' if problem_analysis_ok else '❌ FAIL'}")
    
    # Overall result
    all_passed = all([health_ok, initialize_ok, tools_list_ok, clean_analysis_ok, problem_analysis_ok])
    print("\n===============================================")
    if all_passed:
        print("✅ ALL TESTS PASSED! The MCP server is fully operational.")
        return 0
    else:
        print("❌ SOME TESTS FAILED. The MCP server may not be fully operational.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 