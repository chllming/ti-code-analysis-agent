#!/usr/bin/env python3
"""
Comprehensive real-world test of the Code Analysis Agent.

This script tests the MCP server's ability to analyze Python code using:
1. Flake8 - for linting and style checking
2. Black - for code formatting
3. Bandit - for security analysis

It uses a realistic Python code sample with style, formatting, and security issues.
"""

import json
import os
import requests
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuration
MCP_URL = os.environ.get("MCP_URL", "http://localhost:5000/mcp")
VERBOSE = os.environ.get("VERBOSE", "true").lower() == "true"

# Sample Python code with multiple issues:
# - Style issues for Flake8
# - Formatting issues for Black
# - Security issues for Bandit
SAMPLE_CODE = '''
import os
import pickle
import yaml
import subprocess
import tempfile
from typing import List,Dict, Any,Union
import json

def load_configuration(config_path:str)->Dict[str,Any]:
    """Load configuration from a file."""
    if config_path.endswith('.yaml'):
        with open(config_path, 'r') as f:
            # BAD: Using yaml.load() is unsafe (Bandit)
            return yaml.load(f.read())
    elif config_path.endswith('.json'):
            with open(config_path, 'r') as f:
                return json.load(f)  # Indentation is incorrect (Flake8)
    elif config_path.endswith('.pkl'):
        with open(config_path, 'rb') as f:
            # BAD: Using pickle is unsafe (Bandit)
            return pickle.load(f)
    else:
        raise ValueError(f"Unsupported config format: {config_path}")

def execute_command(command:str,timeout:int = 30)->str:
    """Execute a system command and return the output."""
    # BAD: shell=True is unsafe (Bandit)
    try:
      result = subprocess.check_output(command, shell=True, timeout=timeout)
      return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Command failed with code {e.returncode}")
        return ""

class FileHandler:
    def __init__(self, base_dir:str):
        self.base_dir=base_dir  # No space around equals (Black)
        
    def read_file(self, filename:str)->str:
        """Read a file and return its contents."""
        path = os.path.join(self.base_dir, filename)
        # BAD: Potential path traversal (Bandit)
        with open(path, 'r') as f:
            return f.read()
    
    def write_file(self,filename:str,content:str)->None:
        """Write content to a file."""
        path=os.path.join(self.base_dir, filename)
        with open(path, 'w') as f:
            f.write(content)
            
    def delete_file(self, filename: str) -> bool:
        """Delete a file."""
        path = os.path.join(self.base_dir, filename)
        try:
            os.remove(path)
            return True
        except:  # Bare except (Flake8)
            return False

def process_data(data:List[Dict[str,Any]])->List[Dict[str,Any]]:
    """Process a list of data items."""
    result=[]  # No space after equals (Black)
    for item in data:
        if 'status' in item and item['status'] == 'active':
           processed = transform_item(item)  # Indentation error (Flake8)
           result.append(processed)
    return result

def transform_item(item:Dict[str,Any])->Dict[str,Any]:
    """Transform a data item."""
    transformed = item.copy()
    # Add a derived field with wrong spacing around operators (Black)
    transformed['full_name']=item.get('first_name','')+' '+item.get('last_name','')
    if 'age' in item and item['age'] < 0:
        # Inconsistent return (Flake8)
        return None
    return transformed
'''

def main():
    """Run the comprehensive test."""
    print(f"Testing Code Analysis Agent at {MCP_URL}")
    
    # Check that the server is running
    try:
        # Test health endpoint if available
        health_url = MCP_URL.replace("/mcp", "/health")
        response = requests.get(health_url)
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("⚠️ Server health check failed, but continuing anyway")
    except Exception as e:
        print(f"⚠️ Couldn't check server health: {str(e)}, but continuing anyway")
    
    # Step 1: Check available tools
    print("\nStep 1: Checking available tools...")
    tools_list_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        response = requests.post(
            MCP_URL,
            json=tools_list_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        tools_data = response.json()
        if VERBOSE:
            print(f"Got response: {json.dumps(tools_data, indent=2)}")
        
        # Check if all required tools are available
        available_tools = []
        for tool in tools_data.get("result", {}).get("tools", []):
            tool_name = tool.get("name")
            available_tools.append(tool_name)
        
        # Check each required tool
        required_tools = ["flake8", "black", "bandit"]
        missing_tools = [t for t in required_tools if t not in available_tools]
        
        if not missing_tools:
            print(f"✅ All required tools are available: {', '.join(required_tools)}")
        else:
            print(f"❌ Missing tools: {', '.join(missing_tools)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error checking tools list: {str(e)}")
        return 1
    
    # Step 2: Test Flake8 linting
    print("\nStep 2: Testing Flake8 linting...")
    flake8_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "flake8",
            "args": {
                "code": SAMPLE_CODE
            }
        }
    }
    
    try:
        response = requests.post(
            MCP_URL,
            json=flake8_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        flake8_data = response.json()
        result = flake8_data.get("result", {})
        
        if result.get("status") == "success":
            issues = result.get("result", {}).get("issues", [])
            print(f"✅ Successfully analyzed code with Flake8, found {len(issues)} style issues")
            
            # Print summary of issues
            if issues:
                print("\nFlake8 issues found:")
                for issue in issues[:5]:  # Show up to 5 issues
                    print(f"  Line {issue.get('line')}: {issue.get('code')} - {issue.get('message')}")
                
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more issues")
            
            if VERBOSE:
                print(f"\nFull Flake8 results: {json.dumps(result.get('result', {}), indent=2)}")
        else:
            print(f"❌ Error analyzing code with Flake8: {json.dumps(result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error analyzing code with Flake8: {str(e)}")
        return 1
    
    # Step 3: Test Black formatting
    print("\nStep 3: Testing Black formatting...")
    black_check_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "black",
            "args": {
                "code": SAMPLE_CODE,
                "operation": "check"
            }
        }
    }
    
    try:
        response = requests.post(
            MCP_URL,
            json=black_check_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        black_check_data = response.json()
        check_result = black_check_data.get("result", {})
        
        if check_result.get("status") == "success":
            is_formatted = check_result.get("result", {}).get("is_formatted", True)
            diff = check_result.get("result", {}).get("diff", "")
            
            if not is_formatted:
                print("✅ Black correctly identified formatting issues")
                if diff and VERBOSE:
                    print("\nFormatting diff:")
                    print(diff)
            else:
                print("❓ Black unexpectedly reported that the code is well-formatted")
        else:
            print(f"❌ Error checking formatting with Black: {json.dumps(check_result, indent=2)}")
            return 1
        
        # Now test Black formatting
        black_format_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "black",
                "args": {
                    "code": SAMPLE_CODE,
                    "operation": "format"
                }
            }
        }
        
        response = requests.post(
            MCP_URL,
            json=black_format_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        black_format_data = response.json()
        format_result = black_format_data.get("result", {})
        
        if format_result.get("status") == "success":
            formatted_code = format_result.get("result", {}).get("formatted_code", "")
            success = format_result.get("result", {}).get("success", False)
            
            if success and formatted_code:
                print("✅ Successfully formatted code with Black")
                
                # Save original and formatted code for comparison if verbose
                if VERBOSE:
                    with open("original_code.py", "w") as f:
                        f.write(SAMPLE_CODE)
                    with open("formatted_code.py", "w") as f:
                        f.write(formatted_code)
                    print("\nSaved original code to 'original_code.py' and formatted code to 'formatted_code.py'")
            else:
                print("❌ Black formatting failed or returned empty code")
                return 1
        else:
            print(f"❌ Error formatting code with Black: {json.dumps(format_result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error with Black formatting: {str(e)}")
        return 1
    
    # Step 4: Test Bandit security analysis
    print("\nStep 4: Testing Bandit security analysis...")
    bandit_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "bandit",
            "args": {
                "code": SAMPLE_CODE
            }
        }
    }
    
    try:
        response = requests.post(
            MCP_URL,
            json=bandit_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        bandit_data = response.json()
        result = bandit_data.get("result", {})
        
        if result.get("status") == "success":
            issues = result.get("result", {}).get("issues", [])
            severity_counts = result.get("result", {}).get("summary", {}).get("severityCounts", {})
            
            print(f"✅ Successfully analyzed code with Bandit, found {len(issues)} security issues")
            print(f"   Severity counts: HIGH: {severity_counts.get('HIGH', 0)}, MEDIUM: {severity_counts.get('MEDIUM', 0)}, LOW: {severity_counts.get('LOW', 0)}")
            
            # Print summary of security issues
            if issues:
                print("\nSecurity issues found:")
                for issue in issues[:5]:  # Show up to 5 issues
                    print(f"  Line {issue.get('line')}: {issue.get('code')} - {issue.get('message')} (Severity: {issue.get('severity')})")
                
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more issues")
            
            if VERBOSE and issues:
                print(f"\nFull Bandit results: {json.dumps(result.get('result', {}), indent=2)}")
        else:
            print(f"❌ Error analyzing code with Bandit: {json.dumps(result, indent=2)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error analyzing code with Bandit: {str(e)}")
        return 1
    
    # Done
    print("\n✅ All tests completed successfully!")
    print("\nSummary:")
    print("1. Flake8 style checking - ✅ Successful")
    print("2. Black code formatting - ✅ Successful")
    print("3. Bandit security analysis - ✅ Successful")
    
    print("\nThe code analysis agent is fully operational!")
    return 0


if __name__ == "__main__":
    # Start the timer
    start_time = time.time()
    
    # Run the main function
    exit_code = main()
    
    # Print execution time
    execution_time = time.time() - start_time
    print(f"\nExecution time: {execution_time:.2f} seconds")
    
    # Exit with the appropriate code
    sys.exit(exit_code) 