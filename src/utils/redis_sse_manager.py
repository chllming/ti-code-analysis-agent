"""
Redis-based Server-Sent Events (SSE) manager for MCP server.

This module provides utilities for managing SSE connections and sending events to clients
using Redis for cross-worker communication.
"""

import json
import logging
import queue
import threading
import time
import uuid
import os
import redis
from typing import Dict, Any, Optional, List, Set

# Configure logger
logger = logging.getLogger(__name__)

# Get Redis URL from environment variable or use a default
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class RedisSSEClient:
    """Represents a connected SSE client with message queue."""
    
    def __init__(self, client_id: str, redis_client: redis.Redis):
        self.client_id = client_id
        self.connected = True
        self.last_activity = time.time()
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.redis = redis_client
        
        # Initialize in Redis
        self._update_redis()
    
    def _update_redis(self):
        """Update client state in Redis."""
        self.redis.hset(
            f"sse:client:{self.client_id}",
            mapping={
                "connected": "1" if self.connected else "0",
                "last_activity": str(self.last_activity)
            }
        )
        # Set expiration to ensure cleanup
        self.redis.expire(f"sse:client:{self.client_id}", 3600)  # 1 hour
    
    def add_message(self, data: Any, event: Optional[str] = None) -> None:
        """Add a message to this client's queue."""
        with self.lock:
            if self.connected:
                message = {
                    "data": data,
                    "event": event,
                    "timestamp": time.time()
                }
                # Add to local queue for immediate processing
                self.message_queue.put({
                    "data": data,
                    "event": event
                })
                # Also publish to Redis for cross-worker communication
                self.redis.publish(
                    f"sse:messages:{self.client_id}",
                    json.dumps(message)
                )
                self.last_activity = time.time()
                self._update_redis()
    
    def get_message(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Get the next message from the queue."""
        try:
            # Check local queue first
            message = self.message_queue.get(block=True, timeout=timeout)
            return message
        except queue.Empty:
            # Check Redis for messages from other workers
            pubsub = self.redis.pubsub()
            pubsub.subscribe(f"sse:messages:{self.client_id}")
            try:
                message = pubsub.get_message(timeout=timeout)
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    return {
                        "data": data["data"],
                        "event": data["event"]
                    }
            finally:
                pubsub.unsubscribe()
                pubsub.close()
            return None
    
    def close(self) -> None:
        """Mark client as disconnected."""
        with self.lock:
            self.connected = False
            self._update_redis()


class RedisSSEManager:
    """Manages SSE connections and message broadcasting using Redis."""
    
    def __init__(self, heartbeat_interval: int = 30, client_cleanup_delay: int = 60):
        self.clients: Dict[str, RedisSSEClient] = {}
        self.lock = threading.Lock()
        self.heartbeat_interval = heartbeat_interval
        self.client_cleanup_delay = client_cleanup_delay
        
        # Initialize Redis connection
        try:
            self.redis = redis.from_url(REDIS_URL)
            logger.info(f"Connected to Redis at {REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_clients, daemon=True)
        self.cleanup_thread.start()
        
        # Start message listener thread
        self.listener_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
        self.listener_thread.start()
    
    def register_client(self) -> str:
        """Register a new SSE client and return its ID."""
        if not self.redis:
            logger.error("Redis not available, cannot register client")
            return str(uuid.uuid4())  # Return a fake ID
        
        client_id = str(uuid.uuid4())
        
        with self.lock:
            self.clients[client_id] = RedisSSEClient(client_id, self.redis)
            logger.info(f"Registered new SSE client: {client_id}")
        
        return client_id
    
    def unregister_client(self, client_id: str) -> None:
        """
        Mark client as disconnected but keep it in memory for a while.
        """
        with self.lock:
            if client_id in self.clients:
                # Mark as disconnected
                self.clients[client_id].close()
                logger.info(f"Marked SSE client as disconnected: {client_id}")
        
        if self.redis:
            # Set a delayed cleanup in Redis
            self.redis.setex(
                f"sse:disconnect:{client_id}",
                self.client_cleanup_delay,
                time.time()
            )
    
    def get_client(self, client_id: str) -> Optional[RedisSSEClient]:
        """
        Get client by ID if exists locally or in Redis.
        """
        # Check local cache first
        with self.lock:
            if client_id in self.clients:
                return self.clients[client_id]
        
        # If not in local cache, check Redis
        if self.redis and self.redis.exists(f"sse:client:{client_id}"):
            # Client exists in Redis but not locally, create a local instance
            client = RedisSSEClient(client_id, self.redis)
            with self.lock:
                self.clients[client_id] = client
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
        
        # Publish to Redis broadcast channel
        if self.redis:
            message = {
                "data": serialized_data,
                "event": event,
                "timestamp": time.time()
            }
            self.redis.publish("sse:broadcast", json.dumps(message))
        
        # Also send to local clients
        with self.lock:
            active_clients = [c for c in self.clients.values() if c.connected]
            
        for client in active_clients:
            client.add_message(serialized_data, event)
        
        logger.debug(f"Broadcast message to {len(active_clients)} local clients")
    
    def _listen_for_messages(self) -> None:
        """Listen for broadcast messages from Redis."""
        if not self.redis:
            return
        
        pubsub = self.redis.pubsub()
        pubsub.subscribe("sse:broadcast")
        
        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        # Send to all local clients
                        with self.lock:
                            active_clients = [c for c in self.clients.values() if c.connected]
                        
                        for client in active_clients:
                            client.message_queue.put({
                                "data": data["data"],
                                "event": data["event"]
                            })
                    except Exception as e:
                        logger.error(f"Error processing broadcast message: {e}")
        except Exception as e:
            logger.error(f"Error in Redis message listener: {e}")
        finally:
            pubsub.unsubscribe()
            pubsub.close()
    
    def _cleanup_inactive_clients(self) -> None:
        """Periodically clean up inactive and disconnected clients."""
        while True:
            time.sleep(60)  # Check every minute
            
            if not self.redis:
                continue
            
            now = time.time()
            to_remove: List[str] = []
            
            with self.lock:
                # Check for inactive clients
                for client_id, client in list(self.clients.items()):
                    if client.connected and now - client.last_activity > self.heartbeat_interval:
                        logger.info(f"Client {client_id} inactive for {self.heartbeat_interval}s, marking as disconnected")
                        client.close()
                
                # Remove disconnected clients from local cache
                for client_id in list(self.clients.keys()):
                    if not self.clients[client_id].connected:
                        # Check if it's time to remove
                        disconnect_time = self.redis.get(f"sse:disconnect:{client_id}")
                        if disconnect_time and float(disconnect_time) + self.client_cleanup_delay < now:
                            to_remove.append(client_id)
            
            # Remove clients outside the lock
            for client_id in to_remove:
                with self.lock:
                    if client_id in self.clients:
                        del self.clients[client_id]
                # Clean up Redis keys
                self.redis.delete(f"sse:client:{client_id}")
                self.redis.delete(f"sse:disconnect:{client_id}")
            
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} disconnected SSE clients")
    
    @staticmethod
    def format_sse_message(data: str, event: Optional[str] = None) -> str:
        """Format a message as an SSE event."""
        message = ""
        if event:
            message += f"event: {event}\n"
        
        # Split data by newlines and prefix each line with "data: "
        for line in data.split("\n"):
            message += f"data: {line}\n"
        
        # End with an extra newline to complete the event
        message += "\n"
        return message


# Create a shared instance
redis_sse_manager = RedisSSEManager() 