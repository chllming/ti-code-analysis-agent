"""
Tests for the Flake8 runner.

This module contains tests for the Flake8 integration.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY

import pytest

from src.utils.flake8_runner import (
    analyze_code,
    parse_flake8_results,
    run_flake8
)


# Sample code with Flake8 issues
SAMPLE_CODE_WITH_ISSUES = """
def function(a, b):
  x = a+b
  y=x*2
  return y
"""

# Sample code without Flake8 issues
SAMPLE_CODE_CLEAN = '''
def function(a, b):
    """Return the sum of a and b multiplied by 2."""
    x = a + b
    y = x * 2
    return y
'''

# Sample Flake8 output in standard format
SAMPLE_FLAKE8_OUTPUT = """/path/to/temp.py:3:3: E111 indentation is not a multiple of 4
/path/to/temp.py:3:7: E225 missing whitespace around operator
/path/to/temp.py:4:3: E225 missing whitespace around operator
"""

# Sample parsed Flake8 issues
SAMPLE_PARSED_ISSUES = [
    {
        "file": "temp.py",
        "line": 3,
        "column": 3,
        "code": "E111",
        "message": "indentation is not a multiple of 4"
    },
    {
        "file": "temp.py",
        "line": 3,
        "column": 7,
        "code": "E225",
        "message": "missing whitespace around operator"
    },
    {
        "file": "temp.py",
        "line": 4,
        "column": 3,
        "code": "E225",
        "message": "missing whitespace around operator"
    }
]


def test_parse_flake8_results():
    """Test parsing Flake8 results."""
    # Parse the sample output
    issues = parse_flake8_results(SAMPLE_FLAKE8_OUTPUT)
    
    # Verify the result
    assert len(issues) == 3
    assert issues[0]["file"] == "temp.py"
    assert issues[0]["line"] == 3
    assert issues[0]["column"] == 3
    assert issues[0]["code"] == "E111"
    assert issues[0]["message"] == "indentation is not a multiple of 4"


@patch("subprocess.run")
def test_run_flake8(mock_run):
    """Test running Flake8."""
    # Set up the mock
    mock_process = MagicMock()
    mock_process.stdout = SAMPLE_FLAKE8_OUTPUT
    mock_run.return_value = mock_process
    
    # Run Flake8
    output = run_flake8(Path("/path/to/temp.py"))
    
    # Verify the result
    assert output == SAMPLE_FLAKE8_OUTPUT
    mock_run.assert_called_once()
    # No longer using --format=json
    assert "--max-line-length" in mock_run.call_args[0][0]


@patch("src.utils.flake8_runner.run_flake8")
@patch("src.utils.file_handler.secure_temp_file")
def test_analyze_code(mock_secure_temp_file, mock_run_flake8):
    """Test analyzing code with Flake8."""
    # Set up the mocks
    mock_path = MagicMock()
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    mock_run_flake8.return_value = SAMPLE_FLAKE8_OUTPUT
    
    # Analyze code
    result = analyze_code(SAMPLE_CODE_WITH_ISSUES)
    
    # Verify the result
    assert result["summary"]["totalIssues"] == 3
    assert len(result["issues"]) == 3
    assert result["issues"][0]["code"] == "E111"
    assert result["issues"][0]["line"] == 3
    assert result["issues"][0]["column"] == 3
    assert result["issues"][0]["message"] == "indentation is not a multiple of 4"


@patch("src.utils.flake8_runner.run_flake8")
@patch("src.utils.file_handler.secure_temp_file")
def test_analyze_code_clean(mock_secure_temp_file, mock_run_flake8):
    """Test analyzing clean code with Flake8."""
    # Set up the mocks
    mock_path = MagicMock()
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    mock_run_flake8.return_value = ""  # No issues
    
    # Analyze code
    result = analyze_code(SAMPLE_CODE_CLEAN)
    
    # Verify the result
    assert result["summary"]["totalIssues"] == 0
    assert len(result["issues"]) == 0


@patch("src.utils.flake8_runner.run_flake8")
@patch("src.utils.file_handler.secure_temp_file")
def test_analyze_code_with_config(mock_secure_temp_file, mock_run_flake8):
    """Test analyzing code with a custom config."""
    # Set up the mocks
    mock_path = MagicMock()
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    mock_run_flake8.return_value = SAMPLE_FLAKE8_OUTPUT
    
    # Analyze code with custom config
    result = analyze_code(SAMPLE_CODE_WITH_ISSUES, config_path="custom_config.ini")
    
    # Verify the result
    assert result["summary"]["totalIssues"] == 3
    mock_run_flake8.assert_called_once_with(ANY, "custom_config.ini") 