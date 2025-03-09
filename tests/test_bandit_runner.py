"""
Tests for the Bandit security analysis runner.

This module contains tests for the Bandit integration.
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY

import pytest

from src.utils.bandit_runner import (
    analyze_code,
    parse_bandit_results,
    run_bandit
)


# Sample code with security issues
SAMPLE_VULNERABLE_CODE = """
import pickle
import yaml
import subprocess
import os

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # B301 (pickle)

def parse_yaml(data):
    return yaml.load(data)  # B506 (yaml)

def run_command(cmd):
    return subprocess.call(cmd, shell=True)  # B602 (shell)

def delete_file(filename):
    os.remove(filename)
"""

# Sample code without security issues
SAMPLE_SAFE_CODE = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""

# Sample Bandit output in JSON format
SAMPLE_BANDIT_OUTPUT = """
{
  "errors": [],
  "generated_at": "2023-03-06 12:00:00Z",
  "metrics": {
    "CONFIDENCE.HIGH": 3,
    "CONFIDENCE.LOW": 0,
    "CONFIDENCE.MEDIUM": 0,
    "CONFIDENCE.UNDEFINED": 0,
    "SEVERITY.HIGH": 2,
    "SEVERITY.LOW": 1,
    "SEVERITY.MEDIUM": 0,
    "SEVERITY.UNDEFINED": 0,
    "loc": 14,
    "nosec": 0
  },
  "results": [
    {
      "code": "    return pickle.load(f)  # B301 (pickle)\\n",
      "filename": "/tmp/mcp_temp/tmpabcdefg/temp.py",
      "issue_confidence": "HIGH",
      "issue_severity": "HIGH",
      "issue_text": "Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.",
      "line_number": 7,
      "line_range": [7],
      "more_info": "https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b301-pickle",
      "test_id": "B301",
      "test_name": "blacklist_calls"
    },
    {
      "code": "    return yaml.load(data)  # B506 (yaml)\\n",
      "filename": "/tmp/mcp_temp/tmpabcdefg/temp.py",
      "issue_confidence": "HIGH",
      "issue_severity": "HIGH",
      "issue_text": "Use of unsafe yaml load. Allows instantiation of arbitrary objects. Consider yaml.safe_load().",
      "line_number": 10,
      "line_range": [10],
      "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b506_yaml_load.html",
      "test_id": "B506",
      "test_name": "yaml_load"
    },
    {
      "code": "    return subprocess.call(cmd, shell=True)  # B602 (shell)\\n",
      "filename": "/tmp/mcp_temp/tmpabcdefg/temp.py",
      "issue_confidence": "HIGH",
      "issue_severity": "LOW",
      "issue_text": "subprocess call with shell=True identified, security issue.",
      "line_number": 13,
      "line_range": [13],
      "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html",
      "test_id": "B602",
      "test_name": "subprocess_popen_with_shell_equals_true"
    }
  ]
}
"""


def test_parse_bandit_results():
    """Test parsing Bandit results."""
    # Parse the sample output
    issues = parse_bandit_results(SAMPLE_BANDIT_OUTPUT)
    
    # Verify the result
    assert len(issues) == 3
    assert issues[0]["file"] == "temp.py"
    assert issues[0]["line"] == 7
    assert issues[0]["code"] == "B301"
    assert issues[0]["severity"] == "HIGH"
    assert issues[0]["confidence"] == "HIGH"
    assert "pickle" in issues[0]["message"].lower()
    assert "https://" in issues[0]["more_info"]


@patch("subprocess.run")
def test_run_bandit(mock_run):
    """Test running Bandit."""
    # Set up the mock
    mock_process = MagicMock()
    mock_process.stdout = SAMPLE_BANDIT_OUTPUT
    mock_process.stderr = ""
    mock_run.return_value = mock_process
    
    # Run Bandit
    output = run_bandit(Path("/path/to/temp.py"))
    
    # Verify the result
    assert output == SAMPLE_BANDIT_OUTPUT
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert "bandit" in cmd
    assert "-f" in cmd
    assert "json" in cmd
    assert "-l" in cmd  # Check that severity levels are specified
    assert "-i" in cmd  # Check that confidence levels are specified


@patch("src.utils.bandit_runner.run_bandit")
@patch("src.utils.file_handler.secure_temp_file")
def test_analyze_code(mock_secure_temp_file, mock_run_bandit):
    """Test analyzing code with Bandit."""
    # Set up the mocks
    mock_path = MagicMock()
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    mock_run_bandit.return_value = SAMPLE_BANDIT_OUTPUT
    
    # Analyze code
    result = analyze_code(SAMPLE_VULNERABLE_CODE)
    
    # Verify the result
    assert result["summary"]["totalIssues"] == 3
    assert len(result["issues"]) == 3
    assert result["issues"][0]["code"] == "B301"
    assert result["issues"][0]["line"] == 7
    assert result["issues"][0]["severity"] == "HIGH"
    assert result["summary"]["severityCounts"]["HIGH"] == 2
    assert result["summary"]["severityCounts"]["LOW"] == 1
    
    # Verify the call
    mock_run_bandit.assert_called_once_with(
        ANY, config_path=None, severity=None, confidence=None
    )


@patch("src.utils.bandit_runner.run_bandit")
@patch("src.utils.file_handler.secure_temp_file")
def test_analyze_code_safe(mock_secure_temp_file, mock_run_bandit):
    """Test analyzing safe code with Bandit."""
    # Set up the mocks
    mock_path = MagicMock()
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    mock_run_bandit.return_value = "{}"  # No issues found
    
    # Analyze code
    result = analyze_code(SAMPLE_SAFE_CODE)
    
    # Verify the result
    assert result["summary"]["totalIssues"] == 0
    assert len(result["issues"]) == 0
    assert result["summary"]["severityCounts"]["HIGH"] == 0
    assert result["summary"]["severityCounts"]["MEDIUM"] == 0
    assert result["summary"]["severityCounts"]["LOW"] == 0


@patch("src.utils.bandit_runner.run_bandit")
@patch("src.utils.file_handler.secure_temp_file")
def test_analyze_code_with_config(mock_secure_temp_file, mock_run_bandit):
    """Test analyzing code with custom configuration."""
    # Set up the mocks
    mock_path = MagicMock()
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    mock_run_bandit.return_value = SAMPLE_BANDIT_OUTPUT
    
    # Analyze code with custom config
    result = analyze_code(
        SAMPLE_VULNERABLE_CODE,
        config_path="custom_config.yaml",
        severity="HIGH",
        confidence="HIGH"
    )
    
    # Verify the result
    assert result["summary"]["totalIssues"] == 3
    
    # Verify the call with custom configuration
    mock_run_bandit.assert_called_once_with(
        ANY,
        config_path="custom_config.yaml",
        severity="HIGH",
        confidence="HIGH"
    ) 