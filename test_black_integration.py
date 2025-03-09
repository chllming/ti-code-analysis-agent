"""
Integration test for Black formatter using the MCP server.

This test verifies that the Black formatter integration works correctly
by sending actual requests to the MCP server.
"""

import json
import os
import requests
import sys
from pathlib import Path

# Sample code with formatting issues
UNFORMATTED_CODE = '''
def test_function(a,b, c ):
    x=a+b
    y= x*c
    return { 'result':y,'inputs':[a,b,c]  }
'''

def main():
    """Run the integration test."""
    # Get the MCP server URL from environment or use default
    mcp_url = os.environ.get("MCP_URL", "http://localhost:5000/mcp")
    
    print(f"Testing Black formatter integration with MCP server at {mcp_url}")
    
    # Step 1: Check that Black is in the tools list
    print("\nStep 1: Checking if Black is in the tools list...")
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
        
        # Check if Black is in the tools list
        black_tool = None
        for tool in tools_data.get("result", {}).get("tools", []):
            if tool.get("name") == "black":
                black_tool = tool
                break
        
        if black_tool:
            print("✅ Black tool found in tools list")
        else:
            print("❌ Black tool not found in tools list")
            return 1
    
    except Exception as e:
        print(f"❌ Error checking tools list: {str(e)}")
        return 1
    
    # Step 2: Format code with Black
    print("\nStep 2: Formatting code with Black...")
    format_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "black",
            "args": {
                "code": UNFORMATTED_CODE,
                "operation": "format"
            }
        }
    }
    
    try:
        response = requests.post(
            mcp_url,
            json=format_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        format_data = response.json()
        result = format_data.get("result", {})
        
        if result.get("status") == "success":
            formatted_code = result.get("result", {}).get("formatted_code", "")
            print("✅ Successfully formatted code with Black")
            print(f"\nOriginal code:\n{UNFORMATTED_CODE}")
            print(f"\nFormatted code:\n{formatted_code}")
        else:
            print(f"❌ Error formatting code: {json.dumps(result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error formatting code: {str(e)}")
        return 1
    
    # Step 3: Check formatting
    print("\nStep 3: Checking code formatting...")
    check_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "black",
            "args": {
                "code": UNFORMATTED_CODE,
                "operation": "check"
            }
        }
    }
    
    try:
        response = requests.post(
            mcp_url,
            json=check_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        check_data = response.json()
        result = check_data.get("result", {})
        
        if result.get("status") == "success":
            is_formatted = result.get("result", {}).get("is_formatted", True)
            diff = result.get("result", {}).get("diff", "")
            
            if not is_formatted:
                print("✅ Check correctly identified unformatted code")
                print(f"\nDiff:\n{diff}")
            else:
                print("❌ Check incorrectly identified code as formatted")
                return 1
        else:
            print(f"❌ Error checking code: {json.dumps(result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error checking code: {str(e)}")
        return 1
    
    print("\n✅ All tests passed! Black formatter is correctly integrated with the MCP server.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 