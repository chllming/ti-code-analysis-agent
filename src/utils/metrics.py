"""
Metrics module for the MCP server.

This module provides functionality for tracking and reporting metrics,
such as request counts, response times, and error rates.
"""

import json
import threading
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """Store metrics for individual requests."""
    request_id: str
    method: str
    start_time: float
    end_time: Optional[float] = None
    status_code: Optional[int] = None
    is_error: bool = False
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate request duration in milliseconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return None


class MetricsStore:
    """
    Store and report application metrics.
    
    This class provides thread-safe tracking of various metrics
    such as request counts, response times, and error rates.
    """
    
    def __init__(self, max_request_history: int = 1000):
        """
        Initialize the metrics store.
        
        Args:
            max_request_history: Maximum number of requests to store in history
        """
        self._lock = threading.Lock()
        self._max_request_history = max_request_history
        self._start_time = time.time()
        
        # Metrics counters
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._request_methods: Dict[str, int] = {}
        self._status_codes: Dict[int, int] = {}
        
        # Request history for calculating recent metrics
        self._request_history: List[RequestMetrics] = []
        
        # Active requests (in progress)
        self._active_requests: Dict[str, RequestMetrics] = {}
    
    @property
    def uptime_seconds(self) -> float:
        """Get the server uptime in seconds."""
        return time.time() - self._start_time
    
    def start_request(self, request_id: str, method: str) -> None:
        """
        Start tracking a new request.
        
        Args:
            request_id: The unique ID of the request
            method: The request method name
        """
        with self._lock:
            metrics = RequestMetrics(
                request_id=request_id,
                method=method,
                start_time=time.time()
            )
            self._active_requests[request_id] = metrics
            
            # Update method counter
            self._request_methods[method] = self._request_methods.get(method, 0) + 1
            
            # Update total requests counter
            self._total_requests += 1
    
    def end_request(
        self, request_id: str, status_code: int, is_error: bool = False
    ) -> None:
        """
        End tracking a request.
        
        Args:
            request_id: The unique ID of the request
            status_code: The HTTP status code
            is_error: Whether the request resulted in an error
        """
        with self._lock:
            if request_id in self._active_requests:
                metrics = self._active_requests.pop(request_id)
                metrics.end_time = time.time()
                metrics.status_code = status_code
                metrics.is_error = is_error
                
                # Add to request history, removing oldest if at capacity
                self._request_history.append(metrics)
                if len(self._request_history) > self._max_request_history:
                    self._request_history.pop(0)
                
                # Update status code counter
                self._status_codes[status_code] = self._status_codes.get(status_code, 0) + 1
                
                # Update success/failure counters
                if is_error:
                    self._failed_requests += 1
                else:
                    self._successful_requests += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.
        
        Returns:
            Dictionary of metrics
        """
        with self._lock:
            # Calculate average response time from history
            avg_response_time_ms = 0
            if self._request_history:
                durations = [m.duration_ms for m in self._request_history if m.duration_ms is not None]
                if durations:
                    avg_response_time_ms = sum(durations) / len(durations)
            
            # Calculate error rate
            error_rate = 0
            if self._total_requests > 0:
                error_rate = (self._failed_requests / self._total_requests) * 100
            
            # Construct metrics dictionary
            return {
                "uptime_seconds": self.uptime_seconds,
                "total_requests": self._total_requests,
                "active_requests": len(self._active_requests),
                "successful_requests": self._successful_requests,
                "failed_requests": self._failed_requests,
                "error_rate_percent": error_rate,
                "avg_response_time_ms": avg_response_time_ms,
                "request_methods": self._request_methods,
                "status_codes": self._status_codes
            }


# Singleton instance
_metrics_store = MetricsStore()


def get_metrics_store() -> MetricsStore:
    """
    Get the global metrics store instance.
    
    Returns:
        The global MetricsStore instance
    """
    return _metrics_store 