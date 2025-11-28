"""Tests for validator module."""

from pre_commit_tools.check_exports.validator import validate_library, validate_libraries, Violation


class TestValidateLibrary:
    """Test library validation logic."""

    def test_no_violations_with_proper_exports(self, temp_codebase):
        """Test that properly exported functions pass validation."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text(
            """
from mylib.core import public_function

__all__ = ["public_function"]
"""
        )

        (lib_dir / "core.py").write_text(
            """
def public_function():
    return "public"

def _private_function():
    return "private"
"""
        )

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("from mylib import public_function")

        violations, stats = validate_library(str(lib_dir))
        assert len(violations) == 0

    def test_violation_on_private_import(self, temp_codebase):
        """Test that importing non-exported functions creates violations."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text("__all__ = []")

        (lib_dir / "core.py").write_text(
            """
def _private_function():
    return "private"
"""
        )

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("from mylib.core import _private_function")

        violations, stats = validate_library(str(lib_dir))
        assert len(violations) == 1
        assert violations[0].func_name == "core._private_function"  # Now includes module path

    def test_internal_import_allowed(self, temp_codebase):
        """Test that internal library imports don't create violations."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text("")

        (lib_dir / "core.py").write_text(
            """
def _private_function():
    return "private"
"""
        )

        (lib_dir / "utils.py").write_text(
            """
from mylib.core import _private_function

def use_private():
    return _private_function()
"""
        )

        violations, stats = validate_library(str(lib_dir))
        # Internal imports should not create violations
        assert len(violations) == 0

    def test_multiple_violations(self, temp_codebase):
        """Test detecting multiple violations."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text("__all__ = []")

        (lib_dir / "core.py").write_text(
            """
def _func_a():
    pass

def _func_b():
    pass
"""
        )

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text(
            """
from mylib.core import _func_a, _func_b
"""
        )

        violations, stats = validate_library(str(lib_dir))
        assert len(violations) == 2


class TestValidateLibraries:
    """Test validating multiple libraries."""

    def test_multiple_libraries(self, temp_codebase):
        """Test validating multiple libraries at once."""
        # Create first library
        lib1_dir = temp_codebase / "lib1"
        lib1_dir.mkdir()
        (lib1_dir / "__init__.py").write_text("")
        (lib1_dir / "core.py").write_text("def _private(): pass")

        # Create second library
        lib2_dir = temp_codebase / "lib2"
        lib2_dir.mkdir()
        (lib2_dir / "__init__.py").write_text("")
        (lib2_dir / "core.py").write_text("def _secret(): pass")

        # Create external code with violations in both
        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text(
            """
from lib1.core import _private
from lib2.core import _secret
"""
        )

        violations, stats = validate_libraries([str(lib1_dir), str(lib2_dir)])
        assert len(violations) == 2


class TestViolation:
    """Test Violation class."""

    def test_violation_repr(self):
        """Test violation string representation."""
        v = Violation("mylib", "some_func", "path/to/file.py", 42)
        repr_str = repr(v)

        assert "mylib" in repr_str
        assert "some_func" in repr_str
        assert "path/to/file.py:42" in repr_str
