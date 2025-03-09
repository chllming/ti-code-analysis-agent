#!/usr/bin/env python3
"""
Run script for the MCP server.

This script runs the MCP server as a Python module, which helps with import paths.
"""

import os
import sys

from src.mcp_server import app, MCP_HOST, MCP_PORT, LOG_LEVEL, logger
from src.utils.file_handler import TempFileManager

def main():
    """Run the MCP server."""
    # Set up the temporary directory
    TempFileManager.setup_temp_directory()
    logger.info(f"Temporary directory set up at {os.getenv('TEMP_DIR', '/tmp/mcp_temp')}")
    
    # Start server
    logger.info(f"Starting MCP Server on {MCP_HOST}:{MCP_PORT}")
    app.run(host=MCP_HOST, port=MCP_PORT, debug=(LOG_LEVEL.upper() == "DEBUG"))

if __name__ == "__main__":
    main() 