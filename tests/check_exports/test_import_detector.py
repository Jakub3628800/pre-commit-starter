"""Tests for import_detector module."""

from pre_commit_tools.check_exports.import_detector import find_imports_via_ast


class TestFindImportsViaAST:
    """Test finding imports via AST parsing."""

    def test_find_from_import(self, temp_codebase):
        """Test finding 'from X import Y' statements."""
        # Create library
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()
        (lib_dir / "__init__.py").write_text("def func(): pass")
        (lib_dir / "core.py").write_text("def helper(): pass")

        # Create external code importing from library
        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text(
            "from mylib import func\nfrom mylib.core import helper"
        )

        imports = find_imports_via_ast(lib_dir)

        assert "mylib.func" in imports
        assert "mylib.core.helper" in imports  # Changed from mylib.helper
        assert len(imports["mylib.func"]) == 1
        assert len(imports["mylib.core.helper"]) == 1

    def test_find_direct_import(self, temp_codebase):
        """Test finding 'import X' statements."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()
        (lib_dir / "__init__.py").write_text("")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("import mylib")

        imports = find_imports_via_ast(lib_dir)
        assert "mylib.mylib" in imports

    def test_skip_internal_imports(self, temp_codebase):
        """Test that internal imports within the library are skipped."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()

        (lib_dir / "__init__.py").write_text("from mylib.core import helper")
        (lib_dir / "core.py").write_text("def helper(): pass")

        imports = find_imports_via_ast(lib_dir)

        # Should be empty because imports are only from external files
        assert len(imports) == 0

    def test_no_imports(self, temp_codebase):
        """Test when there are no imports from the library."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()
        (lib_dir / "__init__.py").write_text("")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("import os\nimport sys")

        imports = find_imports_via_ast(lib_dir)
        assert len(imports) == 0

    def test_multiple_locations(self, temp_codebase):
        """Test finding same import in multiple files."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()
        (lib_dir / "__init__.py").write_text("def func(): pass")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app1.py").write_text("from mylib import func")
        (external_dir / "app2.py").write_text("from mylib import func")

        imports = find_imports_via_ast(lib_dir)

        assert "mylib.func" in imports
        assert len(imports["mylib.func"]) == 2

    def test_syntax_error_files_skipped(self, temp_codebase):
        """Test that files with syntax errors are skipped gracefully."""
        lib_dir = temp_codebase / "mylib"
        lib_dir.mkdir()
        (lib_dir / "__init__.py").write_text("def func(): pass")

        external_dir = temp_codebase / "external"
        external_dir.mkdir()
        (external_dir / "app.py").write_text("from mylib import func")
        (external_dir / "broken.py").write_text("this is not valid python !!!")

        imports = find_imports_via_ast(lib_dir)

        # Should still find the import in app.py despite broken.py
        assert "mylib.func" in imports
