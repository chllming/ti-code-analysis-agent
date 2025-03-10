"""
JSON-RPC over SSE handler for the MCP server.

This module handles processing JSON-RPC requests and sending responses over SSE.
"""

import json
import logging
import traceback
from typing import Dict, Any, Optional, Callable

from .sse_manager import sse_manager
from .redis_sse_manager import redis_sse_manager
from .jsonrpc import validate_jsonrpc_request, parse_jsonrpc_request
import os

# Configure logger
logger = logging.getLogger(__name__)

# Determine which SSE manager to use
USE_REDIS = os.environ.get("USE_REDIS", "true").lower() == "true"
active_sse_manager = redis_sse_manager if USE_REDIS else sse_manager

class SSEJsonRpcHandler:
    """Handles JSON-RPC over SSE communication."""
    
    def __init__(self, jsonrpc_handler_func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """
        Initialize with a function that processes JSON-RPC requests.
        
        Args:
            jsonrpc_handler_func: Function that takes a JSON-RPC request dict and
                                 returns a JSON-RPC response dict
        """
        self.jsonrpc_handler_func = jsonrpc_handler_func
    
    def process_message(self, client_id: str, message: str) -> None:
        """
        Process an incoming JSON-RPC message from a client.
        
        Args:
            client_id: The SSE client ID
            message: The JSON-RPC request message as a string
        """
        logger.debug(f"Processing message from client {client_id}: {message[:100]}...")
        
        try:
            # Parse the JSON-RPC request
            request_data = parse_jsonrpc_request(message)
            
            # Extract the request ID if available
            request_id = request_data.get("id")
            
            # Log the method being called
            method = request_data.get("method", "unknown")
            logger.info(f"SSE client {client_id} called method: {method}")
            
            # Check if parsing failed
            if "error" in request_data:
                logger.warning(f"Error parsing JSON-RPC request: {request_data['error']['message']}")
                self._send_response(client_id, request_data)
                return
            
            # Process the request with the handler function
            try:
                response_data = self.jsonrpc_handler_func(request_data)
                
                # Send the response back to the client
                self._send_response(client_id, response_data)
                logger.info(f"Successfully processed {method} request for client {client_id}")
                
            except Exception as e:
                logger.exception(f"Error processing JSON-RPC method {method}: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,  # Internal error
                        "message": str(e),
                        "data": {
                            "traceback": traceback.format_exc()
                        }
                    }
                }
                self._send_response(client_id, error_response)
            
        except Exception as e:
            logger.exception(f"Error processing message: {str(e)}")
            # Send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": None,  # We don't know the request ID at this point
                "error": {
                    "code": -32603,  # Internal error
                    "message": f"Internal error: {str(e)}"
                }
            }
            self._send_response(client_id, error_response)
    
    def _send_response(self, client_id: str, response_data: Dict[str, Any]) -> None:
        """
        Send a JSON-RPC response to a client.
        
        Args:
            client_id: The SSE client ID
            response_data: The JSON-RPC response data
        """
        try:
            # Ensure the response has the correct format
            if "jsonrpc" not in response_data:
                response_data["jsonrpc"] = "2.0"
                
            # Send the response as a JSON-RPC event
            success = active_sse_manager.send_message(
                client_id=client_id,
                data=response_data,
                event="jsonrpc"
            )
            
            if success:
                logger.debug(f"Sent response to client {client_id}")
            else:
                logger.warning(f"Failed to send response to client {client_id}, client may be disconnected")
            
        except Exception as e:
            logger.error(f"Error sending response to client {client_id}: {str(e)}")


# Create a shared instance to be configured later
sse_jsonrpc_handler: Optional[SSEJsonRpcHandler] = None 