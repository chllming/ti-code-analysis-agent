"""
Structured logging module for the MCP server.

This module provides a JSON formatter for structured logging, making logs easier
to parse and analyze in monitoring systems.
"""

import json
import logging
import sys
import traceback
import uuid
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Formatter for generating JSON structured logs.
    
    This formats log records as JSON objects with consistent fields,
    making them easier to parse and analyze in monitoring systems.
    """
    
    def format(self, record):
        """Format the log record as a JSON string."""
        # Basic log record data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": getattr(record, "request_id", str(uuid.uuid4())),
        }
        
        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", 
                          "filename", "funcName", "id", "levelname", "levelno", 
                          "lineno", "module", "msecs", "message", "msg", 
                          "name", "pathname", "process", "processName", 
                          "relativeCreated", "stack_info", "thread", "threadName",
                          "request_id"]:
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add stack info if present
        if record.stack_info:
            log_data["stack_info"] = record.stack_info
            
        return json.dumps(log_data)


def configure_logging(app_name, log_level=logging.INFO, enable_json=True):
    """
    Configure structured logging for the application.
    
    Args:
        app_name (str): Name of the application for the logger
        log_level (int): Logging level (default: logging.INFO)
        enable_json (bool): Whether to use JSON formatting (default: True)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Apply JSON formatter if enabled
    if enable_json:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    logger.addHandler(handler)
    return logger


class LoggingMiddleware:
    """
    Flask middleware for adding request context to logs.
    
    This middleware adds request information to all logs generated
    during request processing, making it easier to trace issues.
    """
    
    def __init__(self, app, logger):
        """
        Initialize the middleware.
        
        Args:
            app (Flask): The Flask application
            logger (logging.Logger): The logger instance
        """
        self.app = app
        self.logger = logger
        
    def __call__(self, environ, start_response):
        """Process the request and add logging context."""
        request_id = str(uuid.uuid4())
        
        # Add a log filter to append request_id to all logs during this request
        class RequestFilter(logging.Filter):
            def filter(self, record):
                record.request_id = request_id
                return True
        
        # Apply the filter to the logger
        request_filter = RequestFilter()
        self.logger.addFilter(request_filter)
        
        # Log the start of the request
        self.logger.info("Request started", extra={
            "method": environ.get("REQUEST_METHOD"),
            "path": environ.get("PATH_INFO"),
            "remote_addr": environ.get("REMOTE_ADDR"),
            "http_referer": environ.get("HTTP_REFERER", ""),
            "http_user_agent": environ.get("HTTP_USER_AGENT", ""),
        })
        
        # Process the request and capture the response
        def custom_start_response(status, headers, exc_info=None):
            # Log the response status
            status_code = int(status.split()[0])
            self.logger.info("Request completed", extra={
                "status_code": status_code,
                "status": status,
            })
            
            # Remove the filter after request processing
            self.logger.removeFilter(request_filter)
            
            # Call the original start_response
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response) 