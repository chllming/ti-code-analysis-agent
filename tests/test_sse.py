"""
Test the SSE implementation of the MCP server.

This tests the Server-Sent Events (SSE) endpoints and functionality.
"""

import json
import pytest
import time
import threading
import requests
from sseclient import SSEClient  # Need to add this to requirements-dev.txt

from src.mcp_server import app, init_app
from src.utils.sse_manager import sse_manager


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Initialize the application with SSE support
    init_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestSSE:
    """Test the SSE functionality."""

    def test_sse_connect(self, client):
        """Test connecting to the SSE endpoint."""
        # This test won't actually test the streaming functionality
        # as test_client doesn't support streaming responses properly
        response = client.get('/sse')
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        assert 'Cache-Control' in response.headers
        assert 'no-cache' in response.headers['Cache-Control']
        assert 'Connection' in response.headers
        assert 'keep-alive' in response.headers['Connection']

    def test_sse_message_unknown_client(self, client):
        """Test sending a message to an unknown client."""
        fake_client_id = 'non-existent-client-id'
        response = client.post(
            f'/sse/{fake_client_id}',
            json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'},
            content_type='application/json'
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Unknown client ID' in data['message']

    def test_sse_message_invalid_format(self, client):
        """Test sending a message with invalid format."""
        # Register a client manually
        client_id = sse_manager.register_client()
        try:
            # Send a non-JSON message
            response = client.post(
                f'/sse/{client_id}',
                data='not-json',
                content_type='text/plain'
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'Message must be JSON' in data['message']
        finally:
            # Clean up the client
            sse_manager.unregister_client(client_id)


# The following test demonstrates integration testing with a running server
# This test is marked skip as it requires a running server
@pytest.mark.skip(reason="Requires a running server")
def test_sse_client_integration():
    """Integration test of the SSE client with a running server."""
    server_url = "http://localhost:5000"
    messages_received = []
    event_stream = None

    def process_stream():
        """Process the SSE stream in a separate thread."""
        nonlocal event_stream
        try:
            # Connect to the SSE endpoint
            event_stream = SSEClient(f"{server_url}/sse")
            
            # Process events
            for event in event_stream:
                if event.event == 'connection':
                    # Got the connection event with client ID
                    data = json.loads(event.data)
                    client_id = data['clientId']
                    messages_received.append(('connection', client_id))
                    
                    # Send a JSON-RPC request
                    response = requests.post(
                        f"{server_url}/sse/{client_id}",
                        json={
                            'jsonrpc': '2.0',
                            'id': 1,
                            'method': 'tools/list'
                        },
                        headers={'Content-Type': 'application/json'}
                    )
                
                elif event.event == 'jsonrpc':
                    # Got a JSON-RPC response
                    data = json.loads(event.data)
                    messages_received.append(('jsonrpc', data))
                    break  # We got our response, can stop listening
        except Exception as e:
            print(f"Error in SSE client: {e}")
    
    # Start the stream processing in a separate thread
    thread = threading.Thread(target=process_stream)
    thread.daemon = True
    thread.start()
    
    # Wait for the thread to complete or timeout
    thread.join(timeout=10)
    
    # Close the event stream
    if event_stream:
        event_stream.close()
    
    # Verify the results
    assert len(messages_received) >= 2
    assert messages_received[0][0] == 'connection'
    assert messages_received[1][0] == 'jsonrpc'
    
    # Verify the JSON-RPC response
    jsonrpc_response = messages_received[1][1]
    assert jsonrpc_response['jsonrpc'] == '2.0'
    assert jsonrpc_response['id'] == 1
    assert 'result' in jsonrpc_response
    assert 'tools' in jsonrpc_response['result'] 