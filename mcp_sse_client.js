/**
 * MCP Server SSE Client for Cursor IDE
 * 
 * This client implements a connection to the MCP server using Server-Sent Events (SSE)
 * protocol, allowing for bidirectional communication with a remote MCP server.
 */

class MCPSSEClient {
  /**
   * Create a new MCP SSE client
   * @param {string} serverUrl - The base URL of the MCP server (e.g., 'https://your-app.railway.app')
   */
  constructor(serverUrl) {
    this.serverUrl = serverUrl;
    this.clientId = null;
    this.evtSource = null;
    this.requestCallbacks = {};
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
    this.onConnectCallbacks = [];
    this.onDisconnectCallbacks = [];
  }

  /**
   * Register a callback to be called when connection is established
   * @param {Function} callback - Function to call on connection
   */
  onConnect(callback) {
    this.onConnectCallbacks.push(callback);
    if (this.connected && this.clientId) {
      callback(this.clientId);
    }
  }

  /**
   * Register a callback to be called when connection is lost
   * @param {Function} callback - Function to call on disconnection
   */
  onDisconnect(callback) {
    this.onDisconnectCallbacks.push(callback);
  }

  /**
   * Connect to the SSE endpoint
   * @returns {Promise<string>} - Promise that resolves with client ID when connected
   */
  connect() {
    return new Promise((resolve, reject) => {
      console.log(`Connecting to ${this.serverUrl}/sse`);
      
      this.evtSource = new EventSource(`${this.serverUrl}/sse`);
      
      // Set a connection timeout
      const connectionTimeout = setTimeout(() => {
        if (!this.connected) {
          this.evtSource.close();
          reject(new Error('Connection timeout'));
          this.reconnect();
        }
      }, 10000); // 10 second timeout
      
      // Handle connection event to get client ID
      this.evtSource.addEventListener('connection', (event) => {
        clearTimeout(connectionTimeout);
        try {
          const data = JSON.parse(event.data);
          this.clientId = data.clientId;
          this.connected = true;
          this.reconnectAttempts = 0;
          console.log(`Connected with client ID: ${this.clientId}`);
          
          // Notify connection callbacks
          this.onConnectCallbacks.forEach(callback => callback(this.clientId));
          
          resolve(this.clientId);
        } catch (error) {
          console.error('Error parsing connection data:', error);
          reject(error);
        }
      });
      
      // Handle JSON-RPC responses
      this.evtSource.addEventListener('jsonrpc', (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response.id && this.requestCallbacks[response.id]) {
            this.requestCallbacks[response.id](response);
            delete this.requestCallbacks[response.id];
          }
        } catch (error) {
          console.error('Error processing jsonrpc message:', error);
        }
      });
      
      // Handle heartbeats
      this.evtSource.addEventListener('heartbeat', (event) => {
        console.debug('Received heartbeat');
      });
      
      // Handle connection errors
      this.evtSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        
        if (this.connected) {
          this.connected = false;
          this.onDisconnectCallbacks.forEach(callback => callback());
        }
        
        this.reconnect();
      };
    });
  }
  
  /**
   * Reconnect if the connection is lost
   * @private
   */
  reconnect() {
    if (this.evtSource) {
      this.evtSource.close();
      this.evtSource = null;
    }
    
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts > this.maxReconnectAttempts) {
      console.error(`Failed to reconnect after ${this.maxReconnectAttempts} attempts`);
      return;
    }
    
    // Exponential backoff for reconnection attempts
    const delay = Math.min(30000, this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1));
    
    console.log(`Reconnecting (attempt ${this.reconnectAttempts}) in ${delay}ms...`);
    setTimeout(() => this.connect().catch(err => console.error('Reconnection failed:', err)), delay);
  }
  
  /**
   * Send a JSON-RPC request
   * @param {string} method - The JSON-RPC method to call
   * @param {Object} params - Parameters for the method
   * @returns {Promise<Object>} - Promise that resolves with the response
   */
  async sendRequest(method, params = {}) {
    if (!this.clientId || !this.connected) {
      throw new Error('Not connected to server');
    }
    
    const requestId = Date.now().toString();
    const request = {
      jsonrpc: '2.0',
      id: requestId,
      method,
      params
    };
    
    return new Promise((resolve, reject) => {
      // Set a timeout for the request
      const timeout = setTimeout(() => {
        if (this.requestCallbacks[requestId]) {
          delete this.requestCallbacks[requestId];
          reject(new Error('Request timeout'));
        }
      }, 30000); // 30 second timeout
      
      // Store callback to handle the response
      this.requestCallbacks[requestId] = (response) => {
        clearTimeout(timeout);
        
        if (response.error) {
          reject(new Error(response.error.message || 'Unknown error'));
        } else {
          resolve(response);
        }
      };
      
      // Send the request
      fetch(`${this.serverUrl}/sse/${this.clientId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      }).catch(error => {
        clearTimeout(timeout);
        delete this.requestCallbacks[requestId];
        reject(error);
      });
    });
  }
  
  /**
   * Run Flake8 analysis on code
   * @param {string} code - The Python code to analyze
   * @returns {Promise<Object>} - Promise that resolves with analysis results
   */
  async runFlake8Analysis(code) {
    const response = await this.sendRequest('tools/call', {
      name: 'flake8',
      code
    });
    return response.result;
  }
  
  /**
   * Format code using Black
   * @param {string} code - The Python code to format
   * @param {Object} options - Black options
   * @returns {Promise<Object>} - Promise that resolves with formatted code
   */
  async formatWithBlack(code, options = {}) {
    const params = {
      name: 'black',
      args: {
        code,
        operation: 'format',
        ...options
      }
    };
    
    const response = await this.sendRequest('tools/call', params);
    return response.result;
  }
  
  /**
   * Run Bandit security analysis on code
   * @param {string} code - The Python code to analyze
   * @param {Object} options - Bandit options
   * @returns {Promise<Object>} - Promise that resolves with analysis results
   */
  async runBanditAnalysis(code, options = {}) {
    const params = {
      name: 'bandit',
      args: {
        code,
        ...options
      }
    };
    
    const response = await this.sendRequest('tools/call', params);
    return response.result;
  }
  
  /**
   * Close the connection
   */
  disconnect() {
    if (this.evtSource) {
      this.evtSource.close();
      this.evtSource = null;
      this.connected = false;
      this.clientId = null;
      console.log('Disconnected from MCP server');
      
      this.onDisconnectCallbacks.forEach(callback => callback());
    }
  }
}

// Example usage in Cursor IDE
/*
// Initialize with the deployed server URL
const mcpClient = new MCPSSEClient('https://your-mcp-server.railway.app');

// Connect to the server
mcpClient.connect()
  .then(clientId => {
    console.log(`Connected to MCP server with client ID: ${clientId}`);
    
    // Get editor content
    const code = editor.getValue();
    
    // Run Flake8 analysis
    return mcpClient.runFlake8Analysis(code);
  })
  .then(result => {
    // Display results in Cursor IDE
    console.log('Flake8 analysis results:', result);
    
    // Format the code with Black
    const code = editor.getValue();
    return mcpClient.formatWithBlack(code);
  })
  .then(result => {
    if (result.success) {
      // Update editor with formatted code
      editor.setValue(result.formatted_code);
    }
    
    // Disconnect when done
    mcpClient.disconnect();
  })
  .catch(error => {
    console.error('Error:', error);
  });
*/

// For Node.js environments (testing)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MCPSSEClient };
} 