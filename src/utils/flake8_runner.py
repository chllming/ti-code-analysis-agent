"""
Flake8 runner for code analysis.

This module provides utilities for running Flake8 on code and parsing the results.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

from .file_handler import secure_temp_file

# Load environment variables
load_dotenv()

# Get Flake8 configuration
FLAKE8_CONFIG = os.getenv("FLAKE8_CONFIG", "./config/flake8.ini")
FLAKE8_MAX_LINE_LENGTH = os.getenv("FLAKE8_MAX_LINE_LENGTH", "100")

# Issue type for type hints
Flake8Issue = Dict[str, Union[str, int]]


def run_flake8(file_path: Path, config_path: Optional[str] = None) -> str:
    """
    Run Flake8 on a file and return the output.
    
    Args:
        file_path: The path to the file to analyze
        config_path: The path to the Flake8 configuration file
        
    Returns:
        The Flake8 output
    """
    import logging
    logger = logging.getLogger("mcp_server")
    
    # Determine the config path
    config_file = config_path or FLAKE8_CONFIG
    
    # Build the command - use default format instead of JSON
    cmd = ["flake8", str(file_path)]
    
    # Add config file if it exists
    if Path(config_file).exists():
        cmd.extend(["--config", config_file])
        logger.debug(f"Using config file: {config_file}")
    else:
        # Fall back to default options if config file doesn't exist
        cmd.extend(["--max-line-length", FLAKE8_MAX_LINE_LENGTH])
        logger.debug(f"Using default max line length: {FLAKE8_MAX_LINE_LENGTH}")
    
    logger.debug(f"Running Flake8 command: {' '.join(cmd)}")
    
    # Run Flake8
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.debug(f"Flake8 exit code: {result.returncode}")
    logger.debug(f"Flake8 stdout: {result.stdout}")
    logger.debug(f"Flake8 stderr: {result.stderr}")
    
    # Return the output
    return result.stdout


def parse_flake8_results(output: str) -> List[Flake8Issue]:
    """
    Parse Flake8 output into a list of issues.
    
    Args:
        output: The Flake8 output
        
    Returns:
        A list of Flake8 issues
    """
    import logging
    logger = logging.getLogger("mcp_server")
    
    # Parse the output line by line
    result = []
    
    if not output.strip():
        return result
    
    for line in output.strip().split('\n'):
        try:
            # Parse the line (format: "file:line:column: code message")
            parts = line.split(':', 3)
            if len(parts) < 4:
                continue
                
            file_path = parts[0]
            line_num = int(parts[1])
            col_num = int(parts[2])
            code_message = parts[3].strip()
            
            # Split the code and message
            code_parts = code_message.split(' ', 1)
            if len(code_parts) < 2:
                continue
                
            code = code_parts[0]
            message = code_parts[1]
            
            # Add the issue to the result
            result.append({
                "file": Path(file_path).name,  # Just use the filename, not the full path
                "line": line_num,
                "column": col_num,
                "code": code,
                "message": message
            })
        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing Flake8 line '{line}': {str(e)}")
            continue
    
    return result


def analyze_code(code: str, filename: str = "temp.py", config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze code with Flake8.
    
    Args:
        code: The code to analyze
        filename: The filename to use for the temporary file
        config_path: The path to the Flake8 configuration file
        
    Returns:
        A dictionary with the analysis results
    """
    with secure_temp_file(code, filename) as temp_file_path:
        # Run Flake8
        output = run_flake8(temp_file_path, config_path)
        
        # Parse the results
        issues = parse_flake8_results(output)
        
        # Create a standardized result
        result = {
            "issues": issues,
            "summary": {
                "totalIssues": len(issues),
                "filesAnalyzed": 1
            }
        }
        
        return result 