"""
File handling utilities for the MCP server.

This module provides utilities for handling temporary files securely for code analysis.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the temporary directory path from environment variable
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/mcp_temp")


class TempFileManager:
    """Manager for temporary files used for code analysis."""

    @staticmethod
    def setup_temp_directory() -> None:
        """Set up the temporary directory for file processing."""
        os.makedirs(TEMP_DIR, exist_ok=True)

    @classmethod
    def create_temp_file(cls, code: str, filename: str = "temp.py") -> Path:
        """
        Create a temporary file with the given code.
        
        Args:
            code: The code to write to the file
            filename: The filename to use for the temporary file
            
        Returns:
            The path to the temporary file
        """
        # Ensure the temporary directory exists
        cls.setup_temp_directory()
        
        # Create a temporary directory within our base temp directory
        temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
        
        # Create the file path
        temp_file_path = Path(temp_dir) / filename
        
        # Write the code to the file
        temp_file_path.write_text(code)
        
        return temp_file_path

    @staticmethod
    def cleanup_temp_file(file_path: Path) -> None:
        """
        Clean up a temporary file and its directory.
        
        Args:
            file_path: The path to the temporary file
        """
        try:
            # Remove the file
            if file_path.exists():
                file_path.unlink()
            
            # Remove the directory if it's empty
            parent_dir = file_path.parent
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
        except (OSError, PermissionError) as e:
            # Log the error but don't crash
            import logging
            logging.getLogger("mcp_server").warning(
                f"Error cleaning up temporary file {file_path}: {str(e)}"
            )


class SecureTempFile:
    """
    Context manager for securely handling temporary files.
    
    This class creates a temporary file, yields its path, and ensures
    the file is cleaned up when the context is exited.
    """
    
    def __init__(self, code: str, filename: str = "temp.py"):
        """
        Initialize the context manager.
        
        Args:
            code: The code to write to the file
            filename: The filename to use for the temporary file
        """
        self.code = code
        self.filename = filename
        self.temp_file_path = None
    
    def __enter__(self) -> Path:
        """
        Enter the context manager.
        
        Returns:
            The path to the temporary file
        """
        # Create the temporary file
        self.temp_file_path = TempFileManager.create_temp_file(self.code, self.filename)
        return self.temp_file_path
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager and clean up the temporary file.
        
        Args:
            exc_type: The exception type if an exception was raised
            exc_val: The exception value if an exception was raised
            exc_tb: The exception traceback if an exception was raised
        """
        # Clean up the temporary file
        if self.temp_file_path:
            TempFileManager.cleanup_temp_file(self.temp_file_path)


# For backward compatibility
def secure_temp_file(code: str, filename: str = "temp.py") -> SecureTempFile:
    """
    Create a secure temporary file context manager.
    
    Args:
        code: The code to write to the file
        filename: The filename to use for the temporary file
        
    Returns:
        A context manager that yields the path to the temporary file
    """
    return SecureTempFile(code, filename) 