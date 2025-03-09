#!/usr/bin/env python3
"""
Standalone test for Bandit security analysis.

This script creates a file with known security vulnerabilities, 
runs Bandit directly on it, and then tests our MCP server's 
Bandit integration to verify it detects the same issues.
"""

import json
import os
import subprocess
import tempfile
import requests
import sys
from pathlib import Path

# Configuration
MCP_URL = os.environ.get("MCP_URL", "http://localhost:5000/mcp")

# Sample code with clear security vulnerabilities for Bandit to detect
VULNERABLE_CODE = '''
import pickle
import yaml
import subprocess
import os
from urllib.request import urlopen

def insecure_deserialization(filename):
    """
    B301: Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data.
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Insecure deserialization

def insecure_yaml_load(data):
    """
    B506: Use of unsafe yaml load. Allows instantiation of arbitrary objects.
    """
    return yaml.load(data)  # Insecure YAML load

def os_command_injection(user_input):
    """
    B602: subprocess call with shell=True identified, security issue.
    """
    os.system(f"ls {user_input}")  # OS command injection
    
    # Another command injection vector
    subprocess.call("echo " + user_input, shell=True)  # Command injection

def sql_injection(user_id):
    """
    B608: Possible SQL injection vector through string-based query construction.
    """
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    # execute_query(query)  # SQL injection - commented for testing
    return query

def insecure_temp_file():
    """
    B108: Probable insecure usage of temp file/directory.
    """
    temp_file = "/tmp/insecure-" + str(os.getpid())
    return temp_file

def hardcoded_password():
    """
    B105: Hardcoded password string detected.
    """
    password = "super_secret_password123"  # Hardcoded password
    api_key = "Ahd67aGHDn5c89K5zwo"  # Hardcoded API key
    return password

def insecure_file_permissions():
    """
    B103: Test for setting permissive file permissions.
    """
    os.chmod("/tmp/some_file", 0o777)  # Insecure file permissions
'''

def run_direct_bandit_check():
    """Run Bandit directly on a file containing vulnerable code."""
    print("Step 1: Testing direct Bandit execution...")
    
    # Create a temporary file with vulnerable code
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(VULNERABLE_CODE)
        temp_file = f.name
    
    try:
        # Run Bandit on the file with JSON output
        cmd = ["bandit", "-f", "json", temp_file]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse the JSON output
        if not result.stdout:
            print("❌ Bandit didn't produce any output")
            return False
        
        bandit_results = json.loads(result.stdout)
        
        # Check if any issues were found
        issues = bandit_results.get("results", [])
        
        print(f"Bandit found {len(issues)} security issues:")
        
        # Print the issues found
        for i, issue in enumerate(issues):
            print(f"  {i+1}. Line {issue.get('line_number')}: {issue.get('issue_text')} ({issue.get('test_id')})")
        
        # Verify that at least some expected issues were found
        expected_issues = ["B301", "B506", "B602", "B105"]
        found_issues = set(issue.get("test_id") for issue in issues)
        
        missing_issues = [issue for issue in expected_issues if issue not in found_issues]
        if missing_issues:
            print(f"❌ Bandit failed to find these expected issues: {', '.join(missing_issues)}")
            return False
        else:
            print("✅ Bandit direct execution successfully found all expected issues")
            return True
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)

def test_mcp_bandit():
    """Test the MCP server's Bandit integration."""
    print("\nStep 2: Testing MCP server Bandit integration...")
    
    # Create a Bandit request to the MCP server
    bandit_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "bandit",
            "args": {
                "code": VULNERABLE_CODE,
                "filename": "vulnerable_test.py"  # Make sure to specify a Python filename
            }
        }
    }
    
    try:
        # Send the request to the MCP server
        response = requests.post(
            MCP_URL,
            json=bandit_request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Print raw response for debugging
        print(f"Raw response: {response.text[:500]}...")
        
        # Parse the response
        result = response.json().get("result", {})
        
        if result.get("status") != "success":
            print(f"❌ Error from MCP server: {json.dumps(result, indent=2)}")
            return False
        
        # Check the security issues found
        issues = result.get("result", {}).get("issues", [])
        severity_counts = result.get("result", {}).get("summary", {}).get("severityCounts", {})
        
        print(f"MCP server found {len(issues)} security issues:")
        print(f"Severity counts: HIGH: {severity_counts.get('HIGH', 0)}, MEDIUM: {severity_counts.get('MEDIUM', 0)}, LOW: {severity_counts.get('LOW', 0)}")
        
        # Print the issues found
        for i, issue in enumerate(issues[:10]):  # Show up to 10 issues
            print(f"  {i+1}. Line {issue.get('line')}: {issue.get('code')} - {issue.get('message')} (Severity: {issue.get('severity')})")
        
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
        
        # Verify that at least some expected issues were found
        expected_issues = ["B301", "B506", "B602", "B105"]
        found_issues = set(issue.get("code") for issue in issues)
        
        missing_issues = [issue for issue in expected_issues if issue not in found_issues]
        if missing_issues:
            print(f"❌ MCP Bandit integration failed to find these expected issues: {', '.join(missing_issues)}")
            return False
        else:
            print("✅ MCP Bandit integration successfully found all expected issues")
            return True
        
    except Exception as e:
        print(f"❌ Error testing MCP Bandit integration: {str(e)}")
        return False

def main():
    """Run both tests."""
    print("Running Bandit security analysis tests\n")
    
    # Run both tests
    direct_success = run_direct_bandit_check()
    mcp_success = test_mcp_bandit()
    
    # Summarize results
    print("\nTest Results:")
    print(f"1. Direct Bandit execution: {'✅ Passed' if direct_success else '❌ Failed'}")
    print(f"2. MCP Bandit integration: {'✅ Passed' if mcp_success else '❌ Failed'}")
    
    if direct_success and mcp_success:
        print("\n✅ Overall: Bandit security analysis is working correctly")
        return 0
    else:
        print("\n❌ Overall: There are issues with Bandit security analysis")
        if direct_success and not mcp_success:
            print("  - Bandit works directly but the MCP integration has issues")
        elif not direct_success and mcp_success:
            print("  - MCP integration works but Bandit itself may have issues")
        else:
            print("  - Both direct Bandit and MCP integration have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 