"""
Black code formatter runner.

This module provides utilities for running Black code formatter on Python code.
"""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from dotenv import load_dotenv

from .file_handler import secure_temp_file

# Load environment variables
load_dotenv()

# Get Black configuration
BLACK_LINE_LENGTH = os.getenv("BLACK_LINE_LENGTH", "88")
BLACK_SKIP_STRING_NORMALIZATION = os.getenv("BLACK_SKIP_STRING_NORMALIZATION", "false").lower() == "true"
BLACK_PYTHON_VERSION = os.getenv("BLACK_PYTHON_VERSION", "py39")


def run_black(file_path: Path, line_length: Optional[int] = None, skip_string_normalization: Optional[bool] = None, 
              check_only: bool = False) -> Tuple[str, bool]:
    """
    Run Black on a file and return the formatted code.
    
    Args:
        file_path: The path to the file to format
        line_length: The line length to use for formatting
        skip_string_normalization: Whether to skip string normalization
        check_only: When True, don't modify the file, just check if it would be reformatted
        
    Returns:
        A tuple containing the formatted code (or diff) and a boolean indicating success
    """
    import logging
    logger = logging.getLogger("mcp_server")
    
    # Build the command
    cmd = ["black"]
    
    # Add options
    if line_length is not None:
        cmd.extend(["--line-length", str(line_length)])
    else:
        cmd.extend(["--line-length", BLACK_LINE_LENGTH])
    
    if skip_string_normalization is not None:
        if skip_string_normalization:
            cmd.append("--skip-string-normalization")
    elif BLACK_SKIP_STRING_NORMALIZATION:
        cmd.append("--skip-string-normalization")
    
    # Add target Python version
    cmd.extend(["--target-version", BLACK_PYTHON_VERSION])
    
    # Add check mode if requested
    if check_only:
        cmd.append("--check")
        cmd.append("--diff")
    
    # Add the file path
    cmd.append(str(file_path))
    
    logger.debug(f"Running Black command: {' '.join(cmd)}")
    
    # Run Black
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.debug(f"Black exit code: {result.returncode}")
    logger.debug(f"Black stdout: {result.stdout}")
    logger.debug(f"Black stderr: {result.stderr}")
    
    # If in check-only mode, return the diff output
    if check_only:
        # Return the diff if there are changes, empty string if already formatted
        return result.stdout or result.stderr, result.returncode == 0
    
    # For normal formatting mode: If Black succeeded (exit code 0), read the formatted code from the file
    if result.returncode == 0:
        return file_path.read_text(), True
    else:
        # If Black failed, return the error message and False
        return result.stderr or result.stdout, False


def format_code(code: str, filename: str = "temp.py", line_length: Optional[int] = None, 
                skip_string_normalization: Optional[bool] = None) -> Dict[str, Any]:
    """
    Format code with Black.
    
    Args:
        code: The code to format
        filename: The filename to use for the temporary file
        line_length: The line length to use for formatting
        skip_string_normalization: Whether to skip string normalization
        
    Returns:
        A dictionary with the formatting results
    """
    with secure_temp_file(code, filename) as temp_file_path:
        # Run Black
        formatted_code, success = run_black(
            temp_file_path, 
            line_length=line_length,
            skip_string_normalization=skip_string_normalization
        )
        
        # Check if the code was already formatted by running in check mode
        _, was_already_formatted = run_black(
            temp_file_path,
            line_length=line_length,
            skip_string_normalization=skip_string_normalization,
            check_only=True
        )
        
        # Create a standardized result
        result = {
            "formatted_code": formatted_code,
            "success": success,
            "already_formatted": was_already_formatted,
            "filename": filename,
            "summary": {
                "line_length": line_length or int(BLACK_LINE_LENGTH),
                "skip_string_normalization": (skip_string_normalization 
                                             if skip_string_normalization is not None 
                                             else BLACK_SKIP_STRING_NORMALIZATION)
            }
        }
        
        return result


def check_formatting(code: str, filename: str = "temp.py", line_length: Optional[int] = None,
                    skip_string_normalization: Optional[bool] = None) -> Dict[str, Any]:
    """
    Check if code is formatted according to Black's standards.
    
    Args:
        code: The code to check
        filename: The filename to use for the temporary file
        line_length: The line length to use for checking
        skip_string_normalization: Whether to skip string normalization
        
    Returns:
        A dictionary with the check results
    """
    with secure_temp_file(code, filename) as temp_file_path:
        # Run Black in check mode
        diff, is_formatted = run_black(
            temp_file_path,
            line_length=line_length,
            skip_string_normalization=skip_string_normalization,
            check_only=True
        )
        
        # Create a standardized result
        result = {
            "is_formatted": is_formatted,
            "diff": diff if not is_formatted else "",
            "filename": filename,
            "summary": {
                "line_length": line_length or int(BLACK_LINE_LENGTH),
                "skip_string_normalization": (skip_string_normalization 
                                             if skip_string_normalization is not None 
                                             else BLACK_SKIP_STRING_NORMALIZATION)
            }
        }
        
        return result 