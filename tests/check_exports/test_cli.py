"""Tests for CLI module."""

import sys
from unittest.mock import patch

from pre_commit_tools.check_exports.cli import main


class TestCLI:
    """Test CLI functionality."""

    def test_no_arguments(self):
        """Test CLI with no arguments."""
        with patch.object(sys, "argv", ["check-exports"]):
            assert main() == 1

    def test_single_library_pass(self, temp_codebase):
        """Test CLI with single library that passes validation."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text(
            """
from mylib.core import public_func

__all__ = ["public_func"]
"""
        )

        (lib_dir / "core.py").write_text("def public_func(): pass")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("from mylib import public_func")

        with patch.object(sys, "argv", ["check-exports", str(lib_dir)]):
            assert main() == 0

    def test_single_library_fail(self, temp_codebase):
        """Test CLI with single library that fails validation."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text("__all__ = []")

        (lib_dir / "core.py").write_text("def _private(): pass")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("from mylib.core import _private")

        with patch.object(sys, "argv", ["check-exports", str(lib_dir)]):
            assert main() == 1

    def test_multiple_libraries(self, temp_codebase):
        """Test CLI with multiple libraries."""
        # Create two valid libraries
        lib1_dir = temp_codebase / "lib1"
        lib1_dir.mkdir()
        (lib1_dir / "__init__.py").write_text("from lib1.core import func1\n__all__ = ['func1']")
        (lib1_dir / "core.py").write_text("def func1(): pass")

        lib2_dir = temp_codebase / "lib2"
        lib2_dir.mkdir()
        (lib2_dir / "__init__.py").write_text("from lib2.core import func2\n__all__ = ['func2']")
        (lib2_dir / "core.py").write_text("def func2(): pass")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text(
            """
from lib1 import func1
from lib2 import func2
"""
        )

        with patch.object(sys, "argv", ["check-exports", str(lib1_dir), str(lib2_dir)]):
            assert main() == 0
