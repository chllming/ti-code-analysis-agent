const http = require('http');
const https = require('https');

// Configuration
const LOCAL_PORT = 5001;
const REMOTE_MCP_URL = 'https://ti-code-analysis-agent-production.up.railway.app/mcp';

console.log(`MCP Proxy starting on port ${LOCAL_PORT}`);
console.log(`Forwarding requests to ${REMOTE_MCP_URL}`);

// Create a server to receive requests from Cursor
const server = http.createServer((req, res) => {
  // Only handle POST requests to /mcp
  if (req.method === 'POST' && req.url === '/mcp') {
    console.log('Received request from Cursor');
    
    // Collect request body data
    let body = '';
    req.on('data', (chunk) => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      // Parse the request to log what's being requested
      try {
        const requestData = JSON.parse(body);
        console.log(`Method: ${requestData.method}, ID: ${requestData.id}`);
      } catch (e) {
        console.error('Error parsing request JSON:', e.message);
      }
      
      // Options for the HTTPS request to our Railway server
      const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body)
        }
      };
      
      // Forward the request to the Railway server
      const proxy_req = https.request(REMOTE_MCP_URL, options, (proxy_res) => {
        // Set CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        
        // Set status code and headers
        res.writeHead(proxy_res.statusCode, proxy_res.headers);
        
        // Collect and forward response data
        let responseData = '';
        proxy_res.on('data', (chunk) => {
          responseData += chunk;
          res.write(chunk);
        });
        
        proxy_res.on('end', () => {
          console.log('Response from Railway server:', responseData);
          res.end();
        });
      });
      
      proxy_req.on('error', (error) => {
        console.error('Error forwarding request:', error);
        res.writeHead(500);
        res.end(JSON.stringify({
          jsonrpc: "2.0",
          id: null,
          error: {
            code: -32603,
            message: `Proxy error: ${error.message}`
          }
        }));
      });
      
      // Send the request to the Railway server
      proxy_req.write(body);
      proxy_req.end();
    });
  } else if (req.method === 'OPTIONS' && req.url === '/mcp') {
    // Handle OPTIONS requests for CORS preflight
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.writeHead(200);
    res.end();
  } else {
    // Health check endpoint
    if (req.url === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'healthy', proxy: true }));
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  }
});

// Start the server
server.listen(LOCAL_PORT, () => {
  console.log(`MCP Proxy running at http://localhost:${LOCAL_PORT}/`);
  console.log('Use Ctrl+C to stop');
}); 