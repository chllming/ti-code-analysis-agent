#!/usr/bin/env python3
"""
Test Flake8 integration through the MCP server.

This script sends a request to the MCP server to analyze Python code with Flake8.
"""

import json
import sys
import requests

# Default MCP URL
MCP_URL = "http://localhost:5001/mcp"

# Sample code with Flake8 issues
SAMPLE_CODE_WITH_ISSUES = """
def function(a, b):
  x = a+b
  y=x*2
  return y
"""

# Sample code without Flake8 issues
SAMPLE_CODE_CLEAN = '''
def function(a, b):
    """Return the sum of a and b multiplied by 2."""
    x = a + b
    y = x * 2
    return y
'''


def analyze_code(code: str, filename: str = "example.py") -> dict:
    """
    Send a request to analyze code with Flake8.
    
    Args:
        code: The code to analyze
        filename: The filename to use for the code
        
    Returns:
        The analysis results
    """
    # Create the request payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {
                "code": code,
                "filename": filename
            }
        }
    }
    
    print(f"Sending request: {json.dumps(payload, indent=2)}")
    
    # Send the request
    try:
        response = requests.post(MCP_URL, json=payload, timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    except requests.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}


def print_analysis_results(results: dict) -> None:
    """
    Print the analysis results in a human-readable format.
    
    Args:
        results: The analysis results
    """
    print("\nFlake8 Analysis Results:")
    print("========================")
    
    # Check for errors
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
        
    if "error" in results.get("result", {}):
        print(f"❌ Error: {results['result']['error']}")
        return
    
    # Get the result
    result = results.get("result", {}).get("result", {})
    issues = result.get("issues", [])
    summary = result.get("summary", {})
    
    # Print summary
    print(f"Total issues: {summary.get('totalIssues', 0)}")
    print(f"Files analyzed: {summary.get('filesAnalyzed', 0)}")
    print("")
    
    # Print issues
    if issues:
        print("Issues found:")
        for issue in issues:
            file = issue.get("file", "unknown")
            line = issue.get("line", 0)
            column = issue.get("column", 0)
            code = issue.get("code", "unknown")
            message = issue.get("message", "unknown")
            
            print(f"  - {file}:{line}:{column} [{code}] {message}")
    else:
        print("✅ No issues found!")


def main() -> int:
    """
    Run the test.
    
    Returns:
        The exit code (0 for success, 1 for failure)
    """
    print("Testing Flake8 integration with MCP server")
    print(f"MCP URL: {MCP_URL}")
    
    # Test with code that has issues
    print("\n1. Testing code with issues:")
    print("---------------------------")
    print(SAMPLE_CODE_WITH_ISSUES)
    
    results = analyze_code(SAMPLE_CODE_WITH_ISSUES, "issues.py")
    print_analysis_results(results)
    
    # Test with clean code
    print("\n2. Testing clean code:")
    print("--------------------")
    print(SAMPLE_CODE_CLEAN)
    
    results = analyze_code(SAMPLE_CODE_CLEAN, "clean.py")
    print_analysis_results(results)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 