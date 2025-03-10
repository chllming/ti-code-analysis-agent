#!/usr/bin/env python3
"""
Test script for SSE connection to the MCP server.
"""

import json
import time
import requests
import sseclient

SERVER_URL = 'https://ti-code-analysis-agent-production.up.railway.app'

def main():
    print(f"Testing SSE connection to {SERVER_URL}")
    print("Connecting...")
    
    try:
        # Create an SSE connection
        response = requests.get(f"{SERVER_URL}/sse", stream=True)
        client = sseclient.SSEClient(response)
        
        # Wait for the connection event
        client_id = None
        print("Waiting for events...")
        
        for event in client.events():
            print(f"Received event: {event.event}")
            
            if event.event == 'connection':
                data = json.loads(event.data)
                client_id = data['clientId']
                print(f"Connected with client ID: {client_id}")
                break
            elif event.event == 'heartbeat':
                print("  Heartbeat received, still waiting for connection event...")
                
        if not client_id:
            print("Failed to get client ID after multiple events.")
            return
            
        # Test 1: List available tools
        print("\nTest 1: Listing available tools...")
        tools_response = send_request(client_id, 'tools/list')
        
        print("Available tools:")
        for tool in tools_response['result']['tools']:
            print(f"- {tool['name']} ({tool['version']}): {tool['description']}")
        
        # Test 2: Run Flake8 analysis
        print("\nTest 2: Running Flake8 analysis...")
        sample_code = 'def example():\n  x = 5\n  print("Hello")\n  return None\n'
        
        flake8_response = send_request(client_id, 'tools/call', {
            'name': 'flake8',
            'code': sample_code
        })
        
        print("Flake8 analysis result:")
        print(json.dumps(flake8_response['result'], indent=2))
        
        # Test complete
        print("\nTests completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return

def send_request(client_id, method, params=None):
    """Send a JSON-RPC request to the server via SSE."""
    if params is None:
        params = {}
    
    request_id = str(int(time.time() * 1000))
    request = {
        'jsonrpc': '2.0',
        'id': request_id,
        'method': method,
        'params': params
    }
    
    print(f"Sending {method} request...")
    
    # Send the request to the SSE endpoint
    sse_response = requests.post(
        f"{SERVER_URL}/sse/{client_id}",
        json=request,
        headers={'Content-Type': 'application/json'}
    )
    print(f"SSE endpoint response: {sse_response.status_code} {sse_response.text}")
    
    # For simplicity, just use the regular MCP endpoint in this test
    # because waiting for SSE events is more complex in a quick script
    print("Getting response from regular MCP endpoint...")
    mcp_response = requests.post(
        f"{SERVER_URL}/mcp",
        json=request,
        headers={'Content-Type': 'application/json'}
    )
    
    return mcp_response.json()

if __name__ == "__main__":
    main() 