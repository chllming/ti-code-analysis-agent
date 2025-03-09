"""
Tests for the file handler module.

This module contains tests for the file handler utilities.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.utils.file_handler import (
    TEMP_DIR,
    TempFileManager,
    secure_temp_file
)


def test_setup_temp_directory():
    """Test setting up the temporary directory."""
    # Mock the os.makedirs function
    with patch('os.makedirs') as mock_makedirs:
        # Call the setup function
        TempFileManager.setup_temp_directory()
        
        # Verify that os.makedirs was called with the correct arguments
        mock_makedirs.assert_called_once_with(TEMP_DIR, exist_ok=True)


def test_create_temp_file():
    """Test creating a temporary file."""
    # Mock the setup_temp_directory method and tempfile.mkdtemp function
    with patch.object(TempFileManager, 'setup_temp_directory') as mock_setup, \
         patch('tempfile.mkdtemp') as mock_mkdtemp, \
         patch('pathlib.Path.write_text') as mock_write_text:
        
        # Set up the mocks
        mock_mkdtemp.return_value = '/tmp/mcp_temp/abcd1234'
        
        # Call the function
        code = "def test(): pass"
        filename = "test.py"
        file_path = TempFileManager.create_temp_file(code, filename)
        
        # Verify the function called the expected methods
        mock_setup.assert_called_once()
        mock_mkdtemp.assert_called_once_with(dir=TEMP_DIR)
        mock_write_text.assert_called_once_with(code)
        
        # Verify the returned file path
        assert str(file_path) == '/tmp/mcp_temp/abcd1234/test.py'


def test_cleanup_temp_file():
    """Test cleaning up a temporary file."""
    # Mock the Path.exists, Path.unlink, and Path.parent methods
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.unlink') as mock_unlink, \
         patch('pathlib.Path.iterdir') as mock_iterdir, \
         patch('pathlib.Path.rmdir') as mock_rmdir:
        
        # Set up the mocks
        mock_exists.return_value = True
        mock_iterdir.return_value = []  # Empty directory
        
        # Call the function
        file_path = Path('/tmp/mcp_temp/abcd1234/test.py')
        TempFileManager.cleanup_temp_file(file_path)
        
        # Verify the function called the expected methods
        mock_exists.assert_any_call()  # Check if file exists
        mock_unlink.assert_called_once()  # Delete the file
        mock_iterdir.assert_called_once()  # Check if directory is empty
        mock_rmdir.assert_called_once()  # Delete the directory


def test_secure_temp_file():
    """Test the secure_temp_file context manager."""
    # Create a test file path
    test_file_path = Path('/tmp/mcp_temp/abcd1234/test.py')
    
    # Mock the TempFileManager methods
    with patch.object(TempFileManager, 'create_temp_file') as mock_create, \
         patch.object(TempFileManager, 'cleanup_temp_file') as mock_cleanup:
        
        # Set up the mocks
        mock_create.return_value = test_file_path
        
        # Use the context manager
        code = "def test(): pass"
        with secure_temp_file(code, "test.py") as file_path:
            # Check the file path
            assert file_path == test_file_path
            
            # Verify that create_temp_file was called
            mock_create.assert_called_once_with(code, "test.py")
            
            # Verify that cleanup_temp_file hasn't been called yet
            mock_cleanup.assert_not_called()
        
        # Verify that cleanup_temp_file was called after the context block
        mock_cleanup.assert_called_once_with(test_file_path)


def test_secure_temp_file_exception():
    """Test the secure_temp_file context manager with an exception."""
    # Create a test file path
    test_file_path = Path('/tmp/mcp_temp/abcd1234/test.py')
    
    # Mock the TempFileManager methods
    with patch.object(TempFileManager, 'create_temp_file') as mock_create, \
         patch.object(TempFileManager, 'cleanup_temp_file') as mock_cleanup:
        
        # Set up the mocks
        mock_create.return_value = test_file_path
        
        # Use the context manager
        code = "def test(): pass"
        
        try:
            with secure_temp_file(code, "test.py") as file_path:
                # Check the file path
                assert file_path == test_file_path
                
                # Raise an exception
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Verify that cleanup_temp_file was called despite the exception
        mock_cleanup.assert_called_once_with(test_file_path) 