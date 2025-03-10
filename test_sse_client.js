#!/usr/bin/env node

// Simple script to test the SSE connection with our MCP server
const EventSource = require('eventsource');
const fetch = require('node-fetch');

const SERVER_URL = 'https://ti-code-analysis-agent-production.up.railway.app';
let clientId = null;

console.log('Testing SSE connection to', SERVER_URL);
console.log('Connecting...');

// Create an SSE connection
const evtSource = new EventSource(`${SERVER_URL}/sse`);

// Handle connection event
evtSource.addEventListener('connection', async (event) => {
  const data = JSON.parse(event.data);
  clientId = data.clientId;
  console.log(`Connected with client ID: ${clientId}`);
  
  // Test 1: List available tools
  console.log('\nTest 1: Listing available tools...');
  try {
    const toolsResponse = await sendRequest('tools/list');
    console.log('Available tools:');
    const tools = toolsResponse.result.tools;
    tools.forEach(tool => {
      console.log(`- ${tool.name} (${tool.version}): ${tool.description}`);
    });
    
    // Test 2: Run a simple Flake8 analysis
    console.log('\nTest 2: Running Flake8 analysis...');
    const sampleCode = 'def example():\n  x = 5\n  print("Hello")\n  return None\n';
    
    const flake8Response = await sendRequest('tools/call', {
      name: 'flake8',
      code: sampleCode
    });
    
    console.log('Flake8 analysis result:');
    console.log(JSON.stringify(flake8Response.result, null, 2));
    
    // Close the connection when done
    console.log('\nTests completed successfully. Closing connection.');
    evtSource.close();
    process.exit(0);
  } catch (error) {
    console.error('Error during tests:', error);
    evtSource.close();
    process.exit(1);
  }
});

// Handle JSON-RPC responses
evtSource.addEventListener('jsonrpc', (event) => {
  const response = JSON.parse(event.data);
  console.log('Received JSON-RPC response:', response);
});

// Handle heartbeats
evtSource.addEventListener('heartbeat', (event) => {
  console.log('Heartbeat received');
});

// Handle connection errors
evtSource.onerror = (error) => {
  console.error('SSE connection error:', error);
  evtSource.close();
  process.exit(1);
};

// Function to send a JSON-RPC request
async function sendRequest(method, params = {}) {
  const requestId = Date.now().toString();
  const request = {
    jsonrpc: '2.0',
    id: requestId,
    method,
    params
  };
  
  console.log(`Sending ${method} request...`);
  
  // Send the request
  const response = await fetch(`${SERVER_URL}/sse/${clientId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });
  
  const responseData = await response.json();
  console.log(`Got response from HTTP endpoint:`, responseData);
  
  // Wait for the actual response from the SSE stream
  return new Promise((resolve) => {
    const responseHandler = (event) => {
      const data = JSON.parse(event.data);
      if (data.id === requestId) {
        evtSource.removeEventListener('jsonrpc', responseHandler);
        resolve(data);
      }
    };
    
    evtSource.addEventListener('jsonrpc', responseHandler);
  });
} 