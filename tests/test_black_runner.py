"""
Tests for the Black code formatter runner.

This module contains tests for the Black integration.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock, ANY

import pytest

from src.utils.black_runner import (
    format_code,
    check_formatting,
    run_black
)


# Sample code that needs formatting
SAMPLE_UNFORMATTED_CODE = """
def example_function(a,b, c ):
    x=a+b
    y= x*c
    return { 'result':y,'inputs':[a,b,c]  }
"""

# Sample code that is already formatted
SAMPLE_FORMATTED_CODE = """
def example_function(a, b, c):
    x = a + b
    y = x * c
    return {"result": y, "inputs": [a, b, c]}
"""

# Sample formatted output from Black
SAMPLE_BLACK_OUTPUT = """
def example_function(a, b, c):
    x = a + b
    y = x * c
    return {"result": y, "inputs": [a, b, c]}
"""

# Sample diff output from Black check
SAMPLE_BLACK_DIFF = """
--- temp.py	2023-03-06 12:00:00.000000 +0000
+++ temp.py	2023-03-06 12:00:00.000000 +0000
@@ -1,4 +1,4 @@
 
-def example_function(a,b, c ):
-    x=a+b
-    y= x*c
-    return { 'result':y,'inputs':[a,b,c]  }
+def example_function(a, b, c):
+    x = a + b
+    y = x * c
+    return {"result": y, "inputs": [a, b, c]}
"""


@patch("subprocess.run")
def test_run_black(mock_run):
    """Test running Black on a file."""
    # Mock the subprocess.run result
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = SAMPLE_BLACK_OUTPUT
    mock_process.stderr = ""
    mock_run.return_value = mock_process
    
    # Mock the file reading
    mock_path = MagicMock(spec=Path)
    mock_path.read_text.return_value = SAMPLE_BLACK_OUTPUT
    
    # Run Black
    result, success = run_black(mock_path)
    
    # Check the result
    assert success is True
    assert result == SAMPLE_BLACK_OUTPUT
    
    # Verify the command
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert "black" in cmd
    assert "--line-length" in cmd
    assert str(mock_path) in cmd


@patch("subprocess.run")
def test_run_black_check_mode(mock_run):
    """Test running Black in check mode."""
    # Mock the subprocess.run result
    mock_process = MagicMock()
    mock_process.returncode = 1  # Non-zero exit code means formatting changes would be needed
    mock_process.stdout = SAMPLE_BLACK_DIFF
    mock_process.stderr = ""
    mock_run.return_value = mock_process
    
    # Run Black in check mode
    mock_path = MagicMock(spec=Path)
    result, is_formatted = run_black(mock_path, check_only=True)
    
    # Check the result
    assert is_formatted is False
    assert result == SAMPLE_BLACK_DIFF
    
    # Verify the command
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert "black" in cmd
    assert "--check" in cmd
    assert "--diff" in cmd


@patch("src.utils.black_runner.run_black")
@patch("src.utils.file_handler.secure_temp_file")
def test_format_code(mock_secure_temp_file, mock_run_black):
    """Test formatting code with Black."""
    # Mock the secure_temp_file context manager
    mock_path = MagicMock(spec=Path)
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    
    # Mock the run_black function
    mock_run_black.side_effect = [
        (SAMPLE_BLACK_OUTPUT, True),  # First call returns formatted code
        ("", True)  # Second call (check) returns empty diff (would have been formatted)
    ]
    
    # Format the code
    result = format_code(SAMPLE_UNFORMATTED_CODE)
    
    # Check the result
    assert result["success"] is True
    assert result["formatted_code"] == SAMPLE_BLACK_OUTPUT
    assert result["already_formatted"] is True
    assert isinstance(result["summary"]["line_length"], int)
    
    # Verify the calls
    assert mock_run_black.call_count == 2
    mock_run_black.assert_any_call(ANY, line_length=None, skip_string_normalization=None)
    mock_run_black.assert_any_call(ANY, line_length=None, skip_string_normalization=None, check_only=True)


@patch("src.utils.black_runner.run_black")
@patch("src.utils.file_handler.secure_temp_file")
def test_check_formatting(mock_secure_temp_file, mock_run_black):
    """Test checking code formatting with Black."""
    # Mock the secure_temp_file context manager
    mock_path = MagicMock(spec=Path)
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    
    # Mock the run_black function
    mock_run_black.return_value = (SAMPLE_BLACK_DIFF, False)  # Formatting changes needed
    
    # Check the formatting
    result = check_formatting(SAMPLE_UNFORMATTED_CODE)
    
    # Check the result
    assert result["is_formatted"] is False
    assert result["diff"] == SAMPLE_BLACK_DIFF
    assert isinstance(result["summary"]["line_length"], int)
    
    # Verify the call
    mock_run_black.assert_called_once_with(ANY, line_length=None, skip_string_normalization=None, check_only=True)


@patch("src.utils.black_runner.run_black")
@patch("src.utils.file_handler.secure_temp_file")
def test_check_formatting_already_formatted(mock_secure_temp_file, mock_run_black):
    """Test checking code that is already formatted."""
    # Mock the secure_temp_file context manager
    mock_path = MagicMock(spec=Path)
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    
    # Mock the run_black function
    mock_run_black.return_value = ("", True)  # No changes needed
    
    # Check the formatting
    result = check_formatting(SAMPLE_FORMATTED_CODE)
    
    # Check the result
    assert result["is_formatted"] is True
    assert result["diff"] == ""
    
    # Verify the call
    mock_run_black.assert_called_once_with(ANY, line_length=None, skip_string_normalization=None, check_only=True)


@patch("src.utils.black_runner.run_black")
@patch("src.utils.file_handler.secure_temp_file")
def test_format_code_with_options(mock_secure_temp_file, mock_run_black):
    """Test formatting code with Black with custom options."""
    # Mock the secure_temp_file context manager
    mock_path = MagicMock(spec=Path)
    mock_secure_temp_file.return_value.__enter__.return_value = mock_path
    
    # Mock the run_black function
    mock_run_black.side_effect = [
        (SAMPLE_BLACK_OUTPUT, True),  # First call returns formatted code
        ("", True)  # Second call (check) returns empty diff
    ]
    
    # Format the code with custom options
    result = format_code(
        SAMPLE_UNFORMATTED_CODE,
        line_length=100,
        skip_string_normalization=True
    )
    
    # Check the result
    assert result["success"] is True
    assert result["formatted_code"] == SAMPLE_BLACK_OUTPUT
    assert result["summary"]["line_length"] == 100
    assert result["summary"]["skip_string_normalization"] is True
    
    # Verify the calls
    assert mock_run_black.call_count == 2
    mock_run_black.assert_any_call(ANY, line_length=100, skip_string_normalization=True)
    mock_run_black.assert_any_call(ANY, line_length=100, skip_string_normalization=True, check_only=True) 