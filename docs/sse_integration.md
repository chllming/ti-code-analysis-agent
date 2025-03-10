# Server-Sent Events (SSE) Integration

This document explains how to use the SSE protocol for connecting Cursor IDE directly to the remote MCP server.

## Overview

The MCP server now supports a bidirectional communication channel using Server-Sent Events (SSE) protocol. This allows:

1. Long-lived connections between Cursor IDE and the MCP server
2. Real-time communication using JSON-RPC 2.0 over SSE
3. Reconnection handling and heartbeats for stable connections
4. Direct integration with remote deployments (e.g., on Railway)

## Endpoints

The server exposes the following endpoints for SSE communication:

- `GET /sse` - Establishes an SSE connection and returns a client ID
- `POST /sse/<client_id>` - Accepts messages from the client with the given ID

## Connection Flow

1. **Establish Connection**: The client connects to the `/sse` endpoint to create a long-lived SSE connection.
2. **Receive Client ID**: The server sends a connection event with a client ID that should be used for future communication.
3. **Send Requests**: The client sends JSON-RPC requests to `/sse/<client_id>`.
4. **Receive Responses**: The server sends JSON-RPC responses back through the SSE channel.

## Example Client Implementation

Here's a minimal example of how to implement an SSE client in JavaScript for use with Cursor IDE:

```javascript
class MCPSSEClient {
  constructor(serverUrl) {
    this.serverUrl = serverUrl;
    this.clientId = null;
    this.evtSource = null;
    this.requestCallbacks = {};
  }

  // Connect to the SSE endpoint
  connect() {
    return new Promise((resolve, reject) => {
      this.evtSource = new EventSource(`${this.serverUrl}/sse`);
      
      // Handle connection event to get client ID
      this.evtSource.addEventListener('connection', (event) => {
        const data = JSON.parse(event.data);
        this.clientId = data.clientId;
        console.log(`Connected with client ID: ${this.clientId}`);
        resolve(this.clientId);
      });
      
      // Handle JSON-RPC responses
      this.evtSource.addEventListener('jsonrpc', (event) => {
        const response = JSON.parse(event.data);
        if (response.id && this.requestCallbacks[response.id]) {
          this.requestCallbacks[response.id](response);
          delete this.requestCallbacks[response.id];
        }
      });
      
      // Handle heartbeats
      this.evtSource.addEventListener('heartbeat', (event) => {
        console.log('Received heartbeat');
      });
      
      // Handle connection errors
      this.evtSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        this.reconnect();
      };
    });
  }
  
  // Reconnect if the connection is lost
  reconnect() {
    if (this.evtSource) {
      this.evtSource.close();
    }
    console.log('Reconnecting...');
    setTimeout(() => this.connect(), 1000);
  }
  
  // Send a JSON-RPC request
  async sendRequest(method, params = {}) {
    if (!this.clientId) {
      throw new Error('Not connected');
    }
    
    const requestId = Date.now().toString();
    const request = {
      jsonrpc: '2.0',
      id: requestId,
      method,
      params
    };
    
    return new Promise((resolve) => {
      // Store callback to handle the response
      this.requestCallbacks[requestId] = resolve;
      
      // Send the request
      fetch(`${this.serverUrl}/sse/${this.clientId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });
    });
  }
  
  // Close the connection
  disconnect() {
    if (this.evtSource) {
      this.evtSource.close();
      this.evtSource = null;
    }
  }
}

// Example usage:
async function example() {
  const client = new MCPSSEClient('https://your-mcp-server.railway.app');
  await client.connect();
  
  // List available tools
  const toolsListResponse = await client.sendRequest('tools/list');
  console.log('Available tools:', toolsListResponse.result.tools);
  
  // Run Flake8 analysis
  const analysisResponse = await client.sendRequest('tools/call', {
    name: 'flake8',
    code: 'def example():\n    return None\n'
  });
  console.log('Analysis result:', analysisResponse.result);
  
  // Disconnect when done
  client.disconnect();
}
```

## Integration with Cursor IDE

To integrate this with Cursor IDE:

1. Include the above client code in a Cursor extension or plugin
2. Connect to the remote MCP server using the Railway deployment URL
3. Use the client to send JSON-RPC requests for code analysis tools
4. Display the results in the Cursor IDE UI

## Error Handling

The SSE implementation includes:

- Heartbeats to detect connection issues
- Automatic cleanup of inactive connections
- Error responses for invalid requests
- Client-side reconnection logic

## Performance Considerations

When using SSE for remote connections:

- Keep message sizes reasonable (large code files should be chunked if necessary)
- Consider network latency when implementing UI feedback
- Implement proper error handling and retry logic
- Monitor connection state and reconnect as needed

## Security Considerations

When deploying this solution:

- Implement proper authentication for production deployments
- Consider rate limiting to prevent abuse
- Use HTTPS for all communications
- Add proper access control if needed

## Troubleshooting

Common issues:

- **Connection drops frequently**: Check network stability and adjust heartbeat interval
- **High latency**: Consider deploying the server closer to users
- **Memory usage grows**: Check for connection leaks in the server or client 