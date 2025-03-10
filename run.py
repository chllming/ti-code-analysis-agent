#!/usr/bin/env python3
"""
Run script for the MCP server.

This script runs the MCP server as a Python module, which helps with import paths.
"""

import os
import sys

from src.mcp_server import app, MCP_HOST, MCP_PORT, LOG_LEVEL, logger, init_app

def main():
    """Run the MCP server."""
    # Set up the temporary directory
    from src.utils.file_handler import TempFileManager
    TempFileManager.setup_temp_directory()
    logger.info(f"Temporary directory set up at {os.getenv('TEMP_DIR', '/tmp/mcp_temp')}")
    
    # Initialize the application with SSE support
    init_app()
    logger.info("MCP Server initialized with SSE support")
    
    # Start server with threaded=True for better SSE support in development
    logger.info(f"Starting MCP Server on {MCP_HOST}:{MCP_PORT}")
    app.run(
        host=MCP_HOST, 
        port=MCP_PORT, 
        debug=(LOG_LEVEL.upper() == "DEBUG"),
        threaded=True,
        use_reloader=(LOG_LEVEL.upper() == "DEBUG")
    )

if __name__ == "__main__":
    main() 