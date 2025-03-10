#!/usr/bin/env python3
"""
Cursor MCP Client Simulator

This script simulates how Cursor IDE connects to MCP servers via the SSE protocol.
It helps debug issues with SSE connections in a way that matches Cursor's behavior.
"""

import json
import time
import threading
import argparse
import requests
import sys
from queue import Queue
from urllib.parse import urljoin

class CursorMCPSimulator:
    """Simulate Cursor IDE's MCP connection behavior."""
    
    def __init__(self, server_url, debug=False):
        """Initialize with server URL."""
        self.server_url = server_url
        self.client_id = None
        self.response_queue = Queue()
        self.tools = []
        self.sse_thread = None
        self.running = False
        self.debug = debug
        self.timeout = 30  # connection timeout seconds
    
    def log(self, message):
        """Print a log message if debug is enabled."""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def connect(self):
        """
        Connect to the SSE endpoint and wait for tools list.
        This is how Cursor IDE connects to an MCP server.
        """
        print(f"Connecting to {self.server_url}")
        self.running = True
        
        # Start SSE connection thread
        self.sse_thread = threading.Thread(target=self._sse_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        
        # Wait for client ID and tools list
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.client_id and self.tools:
                return True
            time.sleep(0.1)
        
        if not self.client_id:
            print("Error: Failed to get client ID")
            return False
        
        if not self.tools:
            print("Error: Failed to get tools list")
            return False
        
        return False
    
    def _sse_listener(self):
        """Listen for SSE events."""
        try:
            # This is how Cursor connects to SSE
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
            
            response = requests.get(
                urljoin(self.server_url, "/sse"), 
                stream=True,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Error: SSE connection failed with status {response.status_code}")
                return
            
            # Parse SSE events (similar to Cursor's implementation)
            buffer = ""
            for chunk in response.iter_content(chunk_size=1):
                if not self.running:
                    break
                
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    buffer += chunk_str
                    
                    if buffer.endswith('\n\n'):
                        # Process complete event
                        self._process_event(buffer)
                        buffer = ""
        
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            print(f"Error in SSE connection: {str(e)}")
        finally:
            self.running = False
    
    def _process_event(self, event_data):
        """Process an SSE event."""
        event_type = None
        data = None
        
        try:
            # Parse SSE format
            lines = event_data.split('\n')
            for line in lines:
                if line.startswith('event:'):
                    event_type = line[6:].strip()
                elif line.startswith('data:'):
                    if data is None:
                        data = line[5:].strip()
                    else:
                        data += '\n' + line[5:].strip()
            
            if not event_type or not data:
                return
            
            if event_type == 'connection':
                json_data = json.loads(data)
                self.client_id = json_data.get('clientId')
                print(f"✅ Connected with client ID: {self.client_id}")
                
                # After connection, Cursor immediately requests tools/list
                self.log("Automatically requesting tools/list (like Cursor does)")
                self.send_request('tools/list')
            
            elif event_type == 'jsonrpc':
                json_data = json.loads(data)
                request_id = json_data.get('id')
                
                if request_id == 'init' or json_data.get('method') == 'tools/list':
                    # Process tools list response
                    if 'result' in json_data and 'tools' in json_data['result']:
                        self.tools = json_data['result']['tools']
                        print(f"✅ Received {len(self.tools)} tools:")
                        for tool in self.tools:
                            print(f"  - {tool['name']}: {tool['description']}")
                
                # Add to response queue for other handlers
                self.response_queue.put(json_data)
            
            elif event_type == 'heartbeat':
                self.log("Heartbeat received")
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except Exception as e:
            print(f"Error processing event: {str(e)}")
    
    def send_request(self, method, params=None):
        """Send a JSON-RPC request like Cursor would."""
        if not self.client_id:
            print("Error: Not connected")
            return None
        
        if params is None:
            params = {}
        
        # Create a request ID - Cursor uses timestamp + random suffix
        request_id = f"{int(time.time() * 1000)}"
        
        # Create JSON-RPC request
        request = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
            'params': params
        }
        
        print(f"Sending request: {method}")
        self.log(f"Request details: {json.dumps(request)}")
        
        try:
            # First Cursor tries the /sse/<client_id> endpoint
            response = requests.post(
                urljoin(self.server_url, f"/sse/{self.client_id}"),
                json=request,
                headers={'Content-Type': 'application/json'}
            )
            
            # Check HTTP response
            if response.status_code != 200:
                print(f"Error sending request: {response.status_code} - {response.text}")
                return None
            
            print(f"Request sent, waiting for response...")
            
            # Wait for the response in the event stream
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    # Check if there's a response
                    if not self.response_queue.empty():
                        response = self.response_queue.get(block=False)
                        
                        # Check if this is the response for our request
                        if response.get('id') == request_id:
                            if 'error' in response:
                                print(f"Error in response: {response['error']['message']}")
                            else:
                                print("✅ Received successful response")
                            return response
                        
                        # Not our response, put it back
                        self.response_queue.put(response)
                        
                except Exception:
                    pass
                
                time.sleep(0.1)
            
            print(f"Timeout waiting for response to {method}")
            return None
            
        except Exception as e:
            print(f"Error sending request: {str(e)}")
            return None
    
    def run_tool(self, tool_name, code):
        """Run a specific tool with code sample."""
        print(f"\n=== Running {tool_name} ===")
        
        # Find the tool to get info
        tool_info = None
        for tool in self.tools:
            if tool['name'] == tool_name:
                tool_info = tool
                break
        
        if not tool_info:
            print(f"Error: Tool '{tool_name}' not found")
            return
        
        print(f"Tool description: {tool_info['description']}")
        
        # Prepare the parameters based on tool type
        params = {
            'name': tool_name,
            'code': code
        }
        
        # Send the request
        response = self.send_request('tools/call', params)
        
        # Process the response
        if response and 'result' in response:
            print("\nResults:")
            print(json.dumps(response['result'], indent=2))
        else:
            print("No valid response received")
    
    def disconnect(self):
        """Close the connection."""
        self.running = False
        if self.sse_thread:
            self.sse_thread.join(timeout=2)
        print("Disconnected")


def main():
    """Run the Cursor MCP simulator."""
    parser = argparse.ArgumentParser(description='Simulate Cursor MCP client behavior')
    parser.add_argument('server_url', help='MCP server URL (e.g., http://localhost:5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Create the simulator
    simulator = CursorMCPSimulator(args.server_url, debug=args.debug)
    
    try:
        # Connect to the server
        if not simulator.connect():
            print("Failed to connect properly")
            return 1
        
        # Continue only if connected with tools
        if not simulator.tools:
            print("No tools available")
            return 1
        
        # Interactive mode
        while True:
            print("\nAvailable commands:")
            print("  1. Run flake8")
            print("  2. Run black")
            print("  3. Run bandit")
            print("  0. Exit")
            
            choice = input("\nEnter command (0-3): ")
            
            if choice == '0':
                break
            
            # Sample code for testing
            sample_code = 'def example():\n  x = 5\n  print("Hello")\n  return None\n'
            
            if choice == '1':
                simulator.run_tool('flake8', sample_code)
            elif choice == '2':
                simulator.run_tool('black', sample_code)
            elif choice == '3':
                simulator.run_tool('bandit', sample_code)
            else:
                print("Unknown command")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        simulator.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 