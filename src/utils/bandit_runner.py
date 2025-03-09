"""
Bandit security analysis runner.

This module provides utilities for running Bandit security analysis on Python code.
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

# Get Bandit configuration
BANDIT_CONFIG = os.getenv("BANDIT_CONFIG", "./config/bandit.yaml")
BANDIT_SEVERITY = os.getenv("BANDIT_SEVERITY", "LOW,MEDIUM,HIGH")
BANDIT_CONFIDENCE = os.getenv("BANDIT_CONFIDENCE", "LOW,MEDIUM,HIGH")

# Issue type for type hints
BanditIssue = Dict[str, Union[str, int]]


def run_bandit(file_path: Path, config_path: Optional[str] = None,
               severity: Optional[str] = None, confidence: Optional[str] = None) -> str:
    """
    Run Bandit on a file and return the output in JSON format.
    
    Args:
        file_path: The path to the file to analyze
        config_path: The path to the Bandit configuration file
        severity: Severity levels to display (comma-separated)
        confidence: Confidence levels to display (comma-separated)
        
    Returns:
        The Bandit output in JSON format
    """
    import logging
    logger = logging.getLogger("mcp_server")
    
    # Ensure the file exists and log its contents for debugging
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return "{}"
    
    try:
        file_contents = file_path.read_text()
        logger.info(f"File contents of {file_path} (first 200 chars):\n{file_contents[:200]}...")
        logger.info(f"File size: {len(file_contents)} bytes")
    except Exception as e:
        logger.error(f"Error reading file contents: {str(e)}")
    
    # Build the command - note format is crucial: bandit [options] targets
    cmd = ["bandit", "-f", "json"]
    
    # Add config file if specified and it exists
    if config_path and Path(config_path).exists():
        cmd.extend(["-c", config_path])
        logger.debug(f"Using config file: {config_path}")
    elif Path(BANDIT_CONFIG).exists():
        cmd.extend(["-c", BANDIT_CONFIG])
        logger.debug(f"Using default config file: {BANDIT_CONFIG}")
    
    # Add severity level - must use --severity-level instead of -l
    if severity:
        # Convert comma-separated values to the right format
        sev_levels = severity.lower().split(",")
        if len(sev_levels) == 3 and set(sev_levels) == set(["low", "medium", "high"]):
            cmd.append("--severity-level=all")
        else:
            cmd.append(f"--severity-level={severity.lower()}")
    else:
        cmd.append("--severity-level=all")  # Default to all severity levels
    
    # Add confidence level - must use --confidence-level instead of -i
    if confidence:
        # Convert comma-separated values to the right format
        conf_levels = confidence.lower().split(",")
        if len(conf_levels) == 3 and set(conf_levels) == set(["low", "medium", "high"]):
            cmd.append("--confidence-level=all")
        else:
            cmd.append(f"--confidence-level={confidence.lower()}")
    else:
        cmd.append("--confidence-level=all")  # Default to all confidence levels
    
    # Add the file path (at the end of the command)
    cmd.append(str(file_path))
    
    logger.info(f"Running Bandit command: {' '.join(cmd)}")
    
    # Run Bandit
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logger.info(f"Bandit exit code: {result.returncode}")
        logger.info(f"Bandit stdout (first 500 chars): {result.stdout[:500] if result.stdout else 'Empty'}")
        logger.info(f"Bandit stderr (first 500 chars): {result.stderr[:500] if result.stderr else 'Empty'}")
        
        # Bandit returns exit code 1 when issues are found, but that's not an error for us
        if result.returncode not in [0, 1]:
            logger.error(f"Bandit failed with error code {result.returncode}")
            return "{}"
        
        # Return the output (stdout if available, otherwise an empty JSON object)
        return result.stdout or "{}"
    except Exception as e:
        logger.error(f"Error running Bandit: {str(e)}")
        return "{}"


def parse_bandit_results(output: str) -> List[BanditIssue]:
    """
    Parse Bandit JSON output into a list of issues.
    
    Args:
        output: The Bandit JSON output
        
    Returns:
        A list of Bandit issues
    """
    import logging
    logger = logging.getLogger("mcp_server")
    
    logger.info(f"Parsing Bandit output of size: {len(output)} characters")
    
    # Quick sanity check to see if it looks like valid JSON
    if not output.strip().startswith("{"):
        logger.warning(f"Bandit output doesn't look like valid JSON: {output[:100]}...")
        return []
    
    try:
        # Parse the JSON output
        data = json.loads(output)
        
        # Log the entire data structure for debugging
        logger.info(f"Parsed Bandit data: {json.dumps(data, indent=2)[:500]}...")
        
        # Extract the results
        results = data.get("results", [])
        logger.info(f"Found {len(results)} Bandit issues from raw output")
        
        # Transform into standardized format
        issues = []
        for result in results:
            issue = {
                "file": Path(result.get("filename", "unknown")).name,
                "line": result.get("line_number", 0),
                "code": result.get("test_id", ""),
                "severity": result.get("issue_severity", ""),
                "confidence": result.get("issue_confidence", ""),
                "message": result.get("issue_text", ""),
                "more_info": result.get("more_info", "")
            }
            issues.append(issue)
        
        return issues
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing Bandit output: {str(e)}")
        logger.error(f"Raw output: {output[:500]}...")  # Log first 500 chars of output
        return []
    except Exception as e:
        logger.error(f"Error processing Bandit results: {str(e)}")
        return []


def analyze_code(code: str, filename: str = "temp.py", config_path: Optional[str] = None,
                severity: Optional[str] = None, confidence: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze code with Bandit.
    
    Args:
        code: The code to analyze
        filename: The filename to use for the temporary file
        config_path: The path to the Bandit configuration file
        severity: Severity levels to display (comma-separated)
        confidence: Confidence levels to display (comma-separated)
        
    Returns:
        A dictionary with the analysis results
    """
    import logging
    logger = logging.getLogger("mcp_server")
    
    logger.info(f"Analyzing code with Bandit, code length: {len(code)} characters")
    logger.info(f"Code sample (first 200 chars): {code[:200]}...")
    
    with secure_temp_file(code, filename) as temp_file_path:
        logger.info(f"Created temporary file for Bandit analysis: {temp_file_path}")
        
        # Ensure the file was created correctly and has content
        try:
            temp_file_size = temp_file_path.stat().st_size
            logger.info(f"Temporary file size: {temp_file_size} bytes")
            if temp_file_size == 0:
                logger.error("Temporary file is empty!")
                return {"issues": [], "summary": {"totalIssues": 0, "severityCounts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}}}
        except Exception as e:
            logger.error(f"Error checking temporary file: {str(e)}")
        
        # Run Bandit directly using subprocess for debugging
        try:
            direct_cmd = ["bandit", "-f", "json", str(temp_file_path)]
            logger.info(f"Running direct diagnostic command: {' '.join(direct_cmd)}")
            direct_result = subprocess.run(direct_cmd, capture_output=True, text=True)
            logger.info(f"Direct Bandit exit code: {direct_result.returncode}")
            
            if direct_result.stdout:
                direct_data = json.loads(direct_result.stdout)
                direct_issues = direct_data.get("results", [])
                logger.info(f"Direct Bandit found {len(direct_issues)} issues")
                
                # Log some of the direct issues for comparison
                for i, issue in enumerate(direct_issues[:3]):
                    logger.info(f"Direct issue {i+1}: {issue.get('test_id')} - {issue.get('issue_text')}")
        except Exception as e:
            logger.error(f"Error running direct Bandit check: {str(e)}")
        
        # Run Bandit through our standard interface
        output = run_bandit(
            temp_file_path,
            config_path=config_path,
            severity=severity,
            confidence=confidence
        )
        
        # Parse the results
        issues = parse_bandit_results(output)
        logger.info(f"Found {len(issues)} Bandit issues after parsing")
        
        # If no issues found, but the direct run found issues, there's a problem with our integration
        if not issues and 'direct_issues' in locals() and direct_issues:
            logger.error("Discrepancy detected: Direct Bandit found issues but our integration didn't!")
        
        # Count severity levels
        high_count = sum(1 for i in issues if i.get("severity") == "HIGH")
        medium_count = sum(1 for i in issues if i.get("severity") == "MEDIUM")
        low_count = sum(1 for i in issues if i.get("severity") == "LOW")
        
        # Create a standardized result
        result = {
            "issues": issues,
            "summary": {
                "totalIssues": len(issues),
                "severityCounts": {
                    "HIGH": high_count,
                    "MEDIUM": medium_count,
                    "LOW": low_count
                }
            }
        }
        
        return result 