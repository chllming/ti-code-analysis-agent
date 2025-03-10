#!/usr/bin/env python3
"""
Test script to simulate Cursor MCP client interaction with our server.
This script will:
1. Establish an SSE connection
2. Send a tools/list request and print the tools
3. Send a simple Flake8 analysis request

Usage: python cursor_mcp_test.py
"""

import json
import time
import threading
import sys
from queue import Queue
import requests

SERVER_URL = 'https://ti-code-analysis-agent-production.up.railway.app'

class MCPClient:
    """Simulate Cursor's MCP client."""
    
    def __init__(self, server_url):
        self.server_url = server_url
        self.client_id = None
        self.response_queue = Queue()
        self.sse_thread = None
        self.running = False
        self.debug = True
    
    def log(self, message):
        """Log a message if debug is enabled."""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def connect(self):
        """Establish SSE connection."""
        print(f"Connecting to {self.server_url}/sse")
        self.running = True
        
        # Start SSE connection in a separate thread
        self.sse_thread = threading.Thread(target=self._sse_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        
        # Wait for client ID to be received
        timeout = 10  # seconds
        start_time = time.time()
        while not self.client_id and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not self.client_id:
            raise ConnectionError("Failed to connect: No client ID received")
        
        print(f"Connected with client ID: {self.client_id}")
        return self.client_id
    
    def _sse_listener(self):
        """Listen for SSE events."""
        try:
            response = requests.get(f"{self.server_url}/sse", stream=True)
            
            if response.status_code != 200:
                print(f"Error connecting to SSE endpoint: {response.status_code}")
                return
            
            # Parse the SSE stream
            buffer = ""
            for chunk in response.iter_content(chunk_size=1):
                if not self.running:
                    break
                
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    buffer += chunk_str
                    
                    if buffer.endswith('\n\n'):
                        # Complete event received
                        self._process_event(buffer.strip())
                        buffer = ""
        except Exception as e:
            print(f"SSE listener error: {str(e)}")
        finally:
            self.running = False
    
    def _process_event(self, event_data):
        """Process a complete SSE event."""
        event_type = None
        data = None
        
        # Parse event data
        lines = event_data.split('\n')
        for line in lines:
            if line.startswith('event:'):
                event_type = line[6:].strip()
            elif line.startswith('data:'):
                data = line[5:].strip()
        
        if not event_type or not data:
            return
        
        self.log(f"Received event: {event_type}")
        
        try:
            json_data = json.loads(data)
            
            if event_type == 'connection':
                self.client_id = json_data.get('clientId')
                self.log(f"Got client ID: {self.client_id}")
            
            elif event_type == 'jsonrpc':
                self.log(f"Got JSON-RPC response: {json.dumps(json_data)[:100]}...")
                self.response_queue.put(json_data)
            
            elif event_type == 'heartbeat':
                self.log("Heartbeat received")
        
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {data}")
    
    def send_request(self, method, params=None, timeout=30):
        """Send a JSON-RPC request and wait for the response."""
        if not self.client_id:
            raise ValueError("Not connected")
        
        if params is None:
            params = {}
        
        request_id = str(int(time.time() * 1000))
        request = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
            'params': params
        }
        
        print(f"Sending {method} request (ID: {request_id})...")
        
        # Send the request to the SSE endpoint
        try:
            response = requests.post(
                f"{self.server_url}/sse/{self.client_id}",
                json=request,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                error_msg = f"Error sending request: {response.status_code} - {response.text}"
                print(error_msg)
                return {"error": {"message": error_msg}}
            
            print(f"Request sent successfully, waiting for response...")
            
            # Wait for response in the queue
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Check if there's a response in the queue
                    response = self.response_queue.get(timeout=1)
                    
                    # Check if this is the response for our request
                    if response.get('id') == request_id:
                        return response
                    
                    # Not our response, put it back in the queue
                    self.response_queue.put(response)
                
                except Exception as e:
                    # Queue is empty or other error, continue waiting
                    pass
            
            return {"error": {"message": f"Timeout waiting for response to {method}"}}
        
        except Exception as e:
            error_msg = f"Exception sending request: {str(e)}"
            print(error_msg)
            return {"error": {"message": error_msg}}
    
    def disconnect(self):
        """Close the SSE connection."""
        self.running = False
        if self.sse_thread:
            self.sse_thread.join(timeout=2)
        print("Disconnected")


def main():
    """Run the test."""
    client = MCPClient(SERVER_URL)
    
    try:
        client.connect()
        
        # Test 1: List tools
        print("\n=== TEST 1: List Available Tools ===")
        tools_response = client.send_request('tools/list')
        
        if 'error' in tools_response:
            print(f"Error getting tools: {tools_response['error']['message']}")
        else:
            print("Available tools:")
            for tool in tools_response['result']['tools']:
                print(f"- {tool['name']} ({tool['version']}): {tool['description']}")
        
        # Test 2: Flake8 analysis
        print("\n=== TEST 2: Run Flake8 Analysis ===")
        sample_code = 'def example():\n  x = 5\n  print("Hello")\n  return None\n'
        
        flake8_response = client.send_request('tools/call', {
            'name': 'flake8',
            'code': sample_code
        })
        
        if 'error' in flake8_response:
            print(f"Error running Flake8: {flake8_response['error']['message']}")
        else:
            print("Flake8 analysis result:")
            print(json.dumps(flake8_response['result'], indent=2))
        
        # Test 3: Black formatting
        print("\n=== TEST 3: Format Code with Black ===")
        black_response = client.send_request('tools/call', {
            'name': 'black',
            'args': {
                'code': sample_code,
                'operation': 'format'
            }
        })
        
        if 'error' in black_response:
            print(f"Error running Black: {black_response['error']['message']}")
        else:
            print("Black formatting result:")
            print(json.dumps(black_response['result'], indent=2))
        
        print("\n=== ALL TESTS COMPLETED ===")
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main() 