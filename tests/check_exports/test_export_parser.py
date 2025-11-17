"""Tests for export_parser module."""

from pre_commit_tools.check_exports.export_parser import get_exported_functions, get_init_path, get_library_root


class TestGetExportedFunctions:
    """Test extraction of exported functions from __init__.py."""

    def test_extract_from_all_list(self, temp_codebase):
        """Test extracting functions listed in __all__."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text(
            """
from lib.core import func_a, func_b

__all__ = ["func_a", "func_b"]
"""
        )

        exported = get_exported_functions(lib_dir / "__init__.py")
        assert "func_a" in exported
        assert "func_b" in exported

    def test_extract_direct_definitions(self, temp_codebase):
        """Test extracting directly defined functions."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text(
            """
def my_function():
    pass

def another_function():
    pass
"""
        )

        exported = get_exported_functions(lib_dir / "__init__.py")
        assert "my_function" in exported
        assert "another_function" in exported

    def test_extract_imports_with_as(self, temp_codebase):
        """Test extracting imported names with 'as' aliases."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text(
            """
from lib.utils import helper as public_helper
from lib.core import process as public_process
"""
        )

        exported = get_exported_functions(lib_dir / "__init__.py")
        assert "public_helper" in exported
        assert "public_process" in exported

    def test_empty_init(self, temp_codebase):
        """Test handling of empty __init__.py."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()
        (lib_dir / "__init__.py").write_text("")

        exported = get_exported_functions(lib_dir / "__init__.py")
        assert len(exported) == 0

    def test_nonexistent_init(self, temp_codebase):
        """Test handling when __init__.py doesn't exist."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()

        exported = get_exported_functions(lib_dir / "__init__.py")
        assert len(exported) == 0

    def test_syntax_error_in_init(self, temp_codebase):
        """Test handling of syntax errors in __init__.py."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text("this is not valid python !!!")

        exported = get_exported_functions(lib_dir / "__init__.py")
        assert len(exported) == 0


class TestGetLibraryRoot:
    """Test library root path resolution."""

    def test_relative_path(self, temp_codebase):
        """Test resolving relative paths."""
        lib_path = "mylib"
        root = get_library_root(lib_path)
        assert root.is_absolute()

    def test_absolute_path(self, temp_codebase):
        """Test with absolute paths."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()
        root = get_library_root(str(lib_dir))
        assert root == lib_dir


class TestGetInitPath:
    """Test __init__.py path generation."""

    def test_init_path_generation(self, temp_codebase):
        """Test that init path is correctly generated."""
        lib_dir = temp_codebase / "lib"
        lib_dir.mkdir()

        init_path = get_init_path(lib_dir)
        assert init_path == lib_dir / "__init__.py"
