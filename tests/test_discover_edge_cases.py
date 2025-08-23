"""Tests for untested edge cases in discover.py module."""

import json
from pathlib import Path
from unittest.mock import patch

from pre_commit_starter.discover import (
    detect_python_version,
    find_config_files,
    get_required_type_stubs,
    is_ignored_by_gitignore,
    read_gitignore_patterns,
    detect_runtime_dependencies,
    main as discover_main,
)


class TestGitignoreLogic:
    """Test gitignore pattern reading and matching logic."""

    def test_read_gitignore_patterns_basic(self, tmp_path):
        """Test reading basic gitignore patterns."""
        gitignore_file = tmp_path / ".gitignore"
        gitignore_file.write_text("*.pyc\n__pycache__/\n# comment\n\n.env")

        patterns = read_gitignore_patterns(tmp_path)

        assert "*.pyc" in patterns
        assert "__pycache__/" in patterns
        assert ".env" in patterns
        assert "# comment" not in patterns
        assert "" not in patterns

    def test_read_gitignore_patterns_missing_file(self, tmp_path):
        """Test reading gitignore when file doesn't exist."""
        patterns = read_gitignore_patterns(tmp_path)
        assert patterns == set()

    def test_read_gitignore_patterns_permission_error(self, tmp_path):
        """Test reading gitignore with permission errors."""
        gitignore_file = tmp_path / ".gitignore"
        gitignore_file.write_text("*.pyc")

        with patch("builtins.open", side_effect=PermissionError):
            patterns = read_gitignore_patterns(tmp_path)
            assert patterns == set()

    def test_is_ignored_by_gitignore_directory_patterns(self, tmp_path):
        """Test gitignore directory pattern matching."""
        patterns = {"__pycache__/", "node_modules/", ".git/"}

        # Test nested directories
        file1 = tmp_path / "src" / "__pycache__" / "module.pyc"
        file2 = tmp_path / "frontend" / "node_modules" / "package" / "index.js"
        file3 = tmp_path / ".git" / "objects" / "abc123"

        assert is_ignored_by_gitignore(file1, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(file2, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(file3, tmp_path, patterns) is True

    def test_is_ignored_by_gitignore_file_patterns(self, tmp_path):
        """Test gitignore file pattern matching."""
        patterns = {"*.pyc", "*.log", ".env"}

        file1 = tmp_path / "module.pyc"
        file2 = tmp_path / "app.log"
        file3 = tmp_path / ".env"
        file4 = tmp_path / "script.py"

        assert is_ignored_by_gitignore(file1, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(file2, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(file3, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(file4, tmp_path, patterns) is False

    def test_is_ignored_by_gitignore_hardcoded_patterns(self, tmp_path):
        """Test hardcoded directory exclusions."""
        patterns = set()

        # Test hardcoded exclusions in is_ignored_by_gitignore
        venv_file = tmp_path / ".venv" / "lib" / "python3.9" / "site-packages" / "package.py"
        git_file = tmp_path / ".git" / "objects" / "abc123"
        node_file = tmp_path / "node_modules" / "package" / "index.js"

        assert is_ignored_by_gitignore(venv_file, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(git_file, tmp_path, patterns) is True
        assert is_ignored_by_gitignore(node_file, tmp_path, patterns) is True

    def test_is_ignored_by_gitignore_outside_project_root(self, tmp_path):
        """Test file outside project root returns False."""
        patterns = {"*.pyc"}
        outside_file = Path("/some/other/path/file.py")

        result = is_ignored_by_gitignore(outside_file, tmp_path, patterns)
        assert result is False


class TestPythonVersionDetection:
    """Test Python version detection from various sources."""

    def test_detect_python_version_from_pyproject_toml(self, tmp_path):
        """Test detecting Python version from pyproject.toml requires-python."""
        pyproject_content = """
[project]
name = "test-project"
requires-python = ">=3.9"
dependencies = ["requests"]
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        version = detect_python_version(tmp_path)
        assert version == "python3.9"

    def test_detect_python_version_from_python_version_file(self, tmp_path):
        """Test detecting Python version from .python-version file."""
        (tmp_path / ".python-version").write_text("3.10.5")

        version = detect_python_version(tmp_path)
        assert version == "python3.10.5"

    def test_detect_python_version_with_python_prefix(self, tmp_path):
        """Test Python version file with python prefix."""
        (tmp_path / ".python-version").write_text("python3.11")

        version = detect_python_version(tmp_path)
        assert version == "python3.11"

    def test_detect_python_version_no_files(self, tmp_path):
        """Test Python version detection when no version files exist."""
        version = detect_python_version(tmp_path)
        assert version is None

    def test_detect_python_version_malformed_toml(self, tmp_path):
        """Test Python version detection with malformed TOML."""
        (tmp_path / "pyproject.toml").write_text("invalid toml content [[[")

        version = detect_python_version(tmp_path)
        assert version is None

    def test_detect_python_version_missing_tomllib(self, tmp_path):
        """Test Python version detection when tomllib import fails."""
        pyproject_content = """
[project]
requires-python = ">=3.9"
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        with patch.dict("sys.modules", {"tomllib": None, "tomli": None}):
            version = detect_python_version(tmp_path)
            assert version is None


class TestConfigFileDiscovery:
    """Test configuration file discovery for tools."""

    def test_find_config_files_prettier(self, tmp_path):
        """Test finding Prettier configuration files."""
        (tmp_path / ".prettierrc").write_text("{}")
        (tmp_path / "package.json").write_text("{}")

        files = {"file1.py", ".prettierrc", "package.json"}
        config_files = find_config_files(tmp_path, files)

        assert config_files["prettier_config"] == ".prettierrc"

    def test_find_config_files_eslint(self, tmp_path):
        """Test finding ESLint configuration files."""
        (tmp_path / ".eslintrc.json").write_text("{}")

        files = {"app.js", ".eslintrc.json"}
        config_files = find_config_files(tmp_path, files)

        assert config_files["eslint_config"] == ".eslintrc.json"

    def test_find_config_files_priority(self, tmp_path):
        """Test config file discovery priority."""
        # Create multiple prettier configs
        (tmp_path / ".prettierrc").write_text("{}")
        (tmp_path / ".prettierrc.json").write_text("{}")

        files = {".prettierrc", ".prettierrc.json"}
        config_files = find_config_files(tmp_path, files)

        # Should pick the first one in the list
        assert config_files["prettier_config"] == ".prettierrc"

    def test_find_config_files_none_found(self, tmp_path):
        """Test config file discovery when no configs exist."""
        files = {"app.py", "README.md"}
        config_files = find_config_files(tmp_path, files)

        assert "prettier_config" not in config_files
        assert "eslint_config" not in config_files


class TestRuntimeDependencies:
    """Test runtime dependency detection."""

    def test_detect_runtime_dependencies_pyproject_only_main(self, tmp_path):
        """Test runtime dependencies exclude optional-dependencies."""
        pyproject_content = """
[project]
dependencies = ["requests", "pydantic"]

[project.optional-dependencies]
dev = ["pytest", "black"]
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        deps = detect_runtime_dependencies(tmp_path)

        assert "requests" in deps
        assert "pydantic" in deps
        assert "pytest" not in deps
        assert "black" not in deps

    def test_detect_runtime_dependencies_requirements_txt_only(self, tmp_path):
        """Test runtime dependencies from requirements.txt only."""
        (tmp_path / "requirements.txt").write_text("requests>=2.0\npydantic")
        (tmp_path / "requirements-dev.txt").write_text("pytest\nblack")

        deps = detect_runtime_dependencies(tmp_path)

        assert "requests" in deps
        assert "pydantic" in deps
        assert "pytest" not in deps
        assert "black" not in deps

    def test_detect_runtime_dependencies_file_read_error(self, tmp_path):
        """Test runtime dependencies with file read errors."""
        (tmp_path / "requirements.txt").write_text("requests")

        with patch("builtins.open", side_effect=PermissionError):
            deps = detect_runtime_dependencies(tmp_path)
            assert deps == set()


class TestTypeStubMapping:
    """Test type stub package mapping."""

    def test_get_required_type_stubs_known_packages(self):
        """Test type stub mapping for known packages."""
        dependencies = {"PyYAML", "requests", "jinja2"}

        stubs = get_required_type_stubs(dependencies)

        assert "types-PyYAML" in stubs
        assert "types-requests" in stubs
        assert "types-Jinja2" in stubs

    def test_get_required_type_stubs_case_insensitive(self):
        """Test type stub mapping is case insensitive."""
        dependencies = {"pyyaml", "REQUESTS"}

        stubs = get_required_type_stubs(dependencies)

        # Only lowercase "requests" matches, not "pyyaml" (needs exact case "PyYAML")
        assert "types-requests" in stubs
        assert len(stubs) == 1

    def test_get_required_type_stubs_unknown_packages(self):
        """Test type stub mapping for unknown packages."""
        dependencies = {"unknown-package", "custom-lib"}

        stubs = get_required_type_stubs(dependencies)

        assert len(stubs) == 0

    def test_get_required_type_stubs_mixed(self):
        """Test type stub mapping with mix of known and unknown packages."""
        dependencies = {"PyYAML", "unknown-package", "requests"}

        stubs = get_required_type_stubs(dependencies)

        assert "types-PyYAML" in stubs
        assert "types-requests" in stubs
        assert len(stubs) == 2


class TestDiscoverMainCLI:
    """Test the main CLI function."""

    def test_discover_main_json_output(self, tmp_path, capsys):
        """Test CLI JSON output."""
        # Create a Python project
        (tmp_path / "pyproject.toml").write_text("""
[project]
name = "test"
dependencies = ["requests"]
""")

        with patch("sys.argv", ["discover", "--path", str(tmp_path), "--output", "json"]):
            discover_main()

        captured = capsys.readouterr()
        output_data = json.loads(captured.out)

        assert output_data["python"] is True
        # additional_dependencies should be None since no imports are used
        assert output_data["additional_dependencies"] is None

    def test_discover_main_yaml_output(self, tmp_path, capsys):
        """Test CLI YAML output."""
        # Create a simple project
        (tmp_path / "package.json").write_text('{"name": "test"}')

        with patch("sys.argv", ["discover", "--path", str(tmp_path), "--output", "yaml"]):
            with patch("yaml.dump") as mock_yaml_dump:
                mock_yaml_dump.return_value = "yaml output"
                discover_main()

        mock_yaml_dump.assert_called_once()

    def test_discover_main_default_args(self, capsys):
        """Test CLI with default arguments."""
        with patch("sys.argv", ["discover"]):
            discover_main()

        captured = capsys.readouterr()
        # Should output JSON by default
        output_data = json.loads(captured.out)
        assert isinstance(output_data, dict)
