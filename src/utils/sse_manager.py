"""
Server-Sent Events (SSE) manager for MCP server.

This module provides utilities for managing SSE connections and sending events to clients.
"""

import json
import logging
import queue
import threading
import time
import uuid
from typing import Dict, Any, Optional, List, Set

# Configure logger
logger = logging.getLogger(__name__)

class SSEClient:
    """Represents a connected SSE client with message queue."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.connected = True
        self.last_activity = time.time()
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
    
    def add_message(self, data: Any, event: Optional[str] = None) -> None:
        """Add a message to this client's queue."""
        with self.lock:
            if self.connected:
                self.message_queue.put({
                    "data": data,
                    "event": event
                })
                self.last_activity = time.time()
    
    def get_message(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Get the next message from the queue."""
        try:
            return self.message_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None
    
    def close(self) -> None:
        """Mark client as disconnected."""
        with self.lock:
            self.connected = False


class SSEManager:
    """Manages SSE connections and message broadcasting."""
    
    def __init__(self, heartbeat_interval: int = 30):
        self.clients: Dict[str, SSEClient] = {}
        self.lock = threading.Lock()
        self.heartbeat_interval = heartbeat_interval
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_clients, daemon=True)
        self.cleanup_thread.start()
    
    def register_client(self) -> str:
        """Register a new SSE client and return its ID."""
        client_id = str(uuid.uuid4())
        
        with self.lock:
            self.clients[client_id] = SSEClient(client_id)
            logger.info(f"Registered new SSE client: {client_id}")
        
        return client_id
    
    def unregister_client(self, client_id: str) -> None:
        """Unregister an SSE client."""
        with self.lock:
            if client_id in self.clients:
                self.clients[client_id].close()
                del self.clients[client_id]
                logger.info(f"Unregistered SSE client: {client_id}")
    
    def get_client(self, client_id: str) -> Optional[SSEClient]:
        """Get client by ID if exists and connected."""
        with self.lock:
            client = self.clients.get(client_id)
            if client and client.connected:
                return client
            return None
    
    def send_message(self, client_id: str, data: Any, event: Optional[str] = None) -> bool:
        """Send a message to a specific client."""
        client = self.get_client(client_id)
        if client:
            serialized_data = data
            if not isinstance(data, str):
                try:
                    serialized_data = json.dumps(data)
                except Exception as e:
                    logger.error(f"Error serializing message: {e}")
                    return False
                    
            client.add_message(serialized_data, event)
            return True
        return False
    
    def broadcast_message(self, data: Any, event: Optional[str] = None) -> None:
        """Broadcast a message to all connected clients."""
        serialized_data = data
        if not isinstance(data, str):
            try:
                serialized_data = json.dumps(data)
            except Exception as e:
                logger.error(f"Error serializing broadcast message: {e}")
                return
        
        with self.lock:
            active_clients = [c for c in self.clients.values() if c.connected]
            
        for client in active_clients:
            client.add_message(serialized_data, event)
        
        logger.debug(f"Broadcast message to {len(active_clients)} clients")
    
    def _cleanup_inactive_clients(self) -> None:
        """Periodically clean up inactive clients."""
        while True:
            time.sleep(60)  # Check every minute
            
            now = time.time()
            to_remove: List[str] = []
            
            with self.lock:
                for client_id, client in self.clients.items():
                    # Remove clients that haven't had activity in heartbeat_interval
                    if now - client.last_activity > self.heartbeat_interval:
                        to_remove.append(client_id)
            
            # Remove inactive clients
            for client_id in to_remove:
                self.unregister_client(client_id)
                
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} inactive SSE clients")
    
    def format_sse_message(self, data: str, event: Optional[str] = None, id: Optional[str] = None) -> str:
        """Format a message according to SSE protocol."""
        message = []
        
        if id is not None:
            message.append(f"id: {id}")
        
        if event is not None:
            message.append(f"event: {event}")
        
        # SSE data field must be sent line by line with 'data:' prefix
        for line in data.split('\n'):
            message.append(f"data: {line}")
        
        # Empty line to finish the message
        message.append("")
        
        return "\n".join(message)


# Create a singleton instance
sse_manager = SSEManager() 