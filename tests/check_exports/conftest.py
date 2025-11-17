"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_lib(temp_codebase):
    """Create a sample library with some functions."""
    lib_dir = temp_codebase / "mylib"
    lib_dir.mkdir()

    # Create __init__.py with some exports
    (lib_dir / "__init__.py").write_text(
        """
from mylib.core import public_function

__all__ = ["public_function"]
"""
    )

    # Create core.py with public and private functions
    (lib_dir / "core.py").write_text(
        """
def public_function():
    '''A public function exported from __init__.py'''
    return "public"

def _private_function():
    '''A private function not exported'''
    return "private"
"""
    )

    # Create internal.py with helper functions
    (lib_dir / "internal.py").write_text(
        """
from mylib.core import _private_function

def _internal_helper():
    '''Internal helper that uses private function'''
    return _private_function()
"""
    )

    return temp_codebase, lib_dir


@pytest.fixture
def lib_with_violation(sample_lib):
    """Create a sample with a violation."""
    temp_codebase, lib_dir = sample_lib

    # Create external code that imports a private function
    external_dir = temp_codebase / "external"
    external_dir.mkdir()

    (external_dir / "app.py").write_text(
        """
from mylib.core import _private_function

result = _private_function()
"""
    )

    return temp_codebase, lib_dir
