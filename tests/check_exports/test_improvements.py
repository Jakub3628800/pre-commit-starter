import pytest
from pre_commit_tools.check_exports.validator import validate_library


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository structure."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Create library
    lib = repo / "mylib"
    lib.mkdir()
    (lib / "__init__.py").write_text("from .utils import public_func, _private_func")
    (lib / "utils.py").write_text("def public_func(): pass\ndef _private_func(): pass")

    # Create internal consumer
    (lib / "internal.py").write_text("from .utils import _private_func")

    # Create external consumer
    (repo / "app.py").write_text("from mylib.utils import _private_func")

    return repo


def test_underscore_warning(temp_repo):
    """Test that exporting underscore symbols triggers a warning."""
    lib_path = str(temp_repo / "mylib")
    violations, _ = validate_library(lib_path)

    warnings = [v for v in violations if v.is_warning]
    assert len(warnings) == 1
    assert warnings[0].func_name == "_private_func"
    assert "starts with underscore" in str(warnings[0])


def test_public_submodules(tmp_path):
    """Test public submodules configuration."""
    repo = tmp_path / "repo"
    repo.mkdir()
    lib = repo / "mylib"
    lib.mkdir()
    (lib / "__init__.py").write_text("")

    sub = lib / "sub"
    sub.mkdir()
    (sub / "__init__.py").write_text("def foo(): pass")

    # Consumer imports from submodule
    (repo / "app.py").write_text("from mylib.sub import foo")

    lib_path = str(lib)

    # Without config -> Violation
    violations, _ = validate_library(lib_path)
    assert len(violations) == 1

    # With config -> No violation
    violations, _ = validate_library(lib_path, public_submodules=["sub"])
    assert len(violations) == 0


def test_auto_suggestion(tmp_path):
    """Test auto-suggestion for missing exports."""
    repo = tmp_path / "repo"
    repo.mkdir()
    lib = repo / "mylib"
    lib.mkdir()
    (lib / "__init__.py").write_text("")
    (lib / "utils.py").write_text("def helper(): pass")

    (repo / "app.py").write_text("from mylib.utils import helper")

    lib_path = str(lib)
    violations, _ = validate_library(lib_path)

    assert len(violations) == 1
    assert violations[0].hint is not None
    assert "utils" in violations[0].hint
    assert "public_submodules" in violations[0].hint or "export" in violations[0].hint
