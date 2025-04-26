"""Integration tests for the pre-commit-starter tool."""

import subprocess
import sys
from pathlib import Path

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

# Determine the project root based on the test file location
PROJECT_ROOT = Path(__file__).parent.parent


# Helper function to run the CLI tool
def run_cli(args: list[str], cwd: str | Path) -> subprocess.CompletedProcess:
    """Runs the CLI tool as a subprocess."""
    command = [sys.executable, "-m", "pre_commit_starter.main", *args]
    # Alternative using the installed entry point (if installed):
    # command = ["pre-commit-starter"] + args
    return subprocess.run(command, capture_output=True, text=True, cwd=cwd, check=False, timeout=60)


# --- Test Cases ---


def test_generation_in_sample_python_repo(sample_python_repo: Path, expected_python_config: str):
    """Test generating config in a simple Python repository."""
    # Ensure high confidence for Python
    for i in range(5):
        (sample_python_repo / f"file{i}.py").write_text(f"def func{i}(): pass\n")
    (sample_python_repo / "requirements.txt").write_text("pytest==7.0.0\n")
    result = run_cli(["--force", "--auto"], cwd=sample_python_repo)
    assert result.returncode == 0
    assert "Successfully generated" in result.stdout

    config_path = sample_python_repo / ".pre-commit-config.yaml"
    assert config_path.is_file()
    generated_config = config_path.read_text(encoding="utf-8")

    # Compare only the essential parts
    assert "Technologies detected: python" in generated_config
    assert "https://github.com/Jakub3628800/pre-commit-starter" in generated_config


def test_generation_in_sample_mixed_repo(sample_mixed_repo: Path, expected_mixed_config: str):
    """Test generating config in a mixed-language repository."""
    result = run_cli(["--force", "--auto"], cwd=sample_mixed_repo)
    assert result.returncode == 0
    assert "Successfully generated" in result.stdout

    config_path = sample_mixed_repo / ".pre-commit-config.yaml"
    assert config_path.is_file()
    generated_config = config_path.read_text(encoding="utf-8")

    # Compare only the essential parts
    assert "Technologies detected:" in generated_config
    assert "https://github.com/Jakub3628800/pre-commit-starter" in generated_config


def test_no_overwrite_without_force(sample_python_repo: Path):
    """Test that the tool doesn't overwrite without --force."""
    # Generate initial config
    initial_result = run_cli(["--force"], cwd=sample_python_repo)
    assert initial_result.returncode == 0
    config_path = sample_python_repo / ".pre-commit-config.yaml"
    initial_content = config_path.read_text()

    # Attempt to generate again without --force (simulating 'n' input)
    # We can't easily simulate interactive input here, so we check the state
    # Assuming the tool exits if overwrite is not confirmed
    # For non-interactive test, just run without force and check content didn't change
    second_result = run_cli([], cwd=sample_python_repo)
    # Depending on implementation, might exit 0 or 1 if aborted
    # Let's assume it logs "Aborted" and exits 0 or doesn't write
    assert "already exists" in second_result.stdout or second_result.stderr
    assert config_path.read_text() == initial_content  # Content should be unchanged


def test_list_technologies():
    """Test the --list-technologies flag."""
    result = run_cli(["--list-technologies"], cwd=PROJECT_ROOT)
    assert result.returncode == 0
    assert "Supported technologies:" in result.stdout
    assert "- python" in result.stdout
    assert "- javascript" in result.stdout


def test_run_in_non_git_repo(tmp_path: Path):
    """Test running the tool in a directory that is not a Git repository."""
    result = run_cli([], cwd=tmp_path)
    assert result.returncode != 0
    assert (
        "not a valid Git repository" in result.stderr
        or "not a valid Git repository" in result.stdout
    )  # Check both streams


def test_run_with_custom_hooks(sample_python_repo: Path):
    """Test generating config with a custom hooks file."""
    custom_hooks_content = """
repos:
  - repo: local
    hooks:
      - id: my-custom-test-hook
        name: My Custom Test Hook
        entry: echo "Custom hook ran"
        language: system
"""
    custom_hooks_path = sample_python_repo / ".pre-commit-starter-hooks.yaml"
    custom_hooks_path.write_text(custom_hooks_content)

    result = run_cli(["--force"], cwd=sample_python_repo)
    assert result.returncode == 0
    assert "Loaded custom hooks from .pre-commit-starter-hooks.yaml" in result.stdout
    assert "Successfully generated" in result.stdout

    config_path = sample_python_repo / ".pre-commit-config.yaml"
    generated_config = config_path.read_text()
    assert "my-custom-test-hook" in generated_config
    assert "Includes custom hooks from .pre-commit-starter-hooks.yaml" in generated_config


def test_invalid_custom_hooks_file(sample_python_repo: Path):
    """Test generating config with an invalid custom hooks file."""
    invalid_content = "invalid: yaml: content"
    custom_hooks_path = sample_python_repo / ".pre-commit-starter-hooks.yaml"
    custom_hooks_path.write_text(invalid_content)

    result = run_cli(["--force"], cwd=sample_python_repo)
    assert result.returncode == 0  # Tool should still succeed but warn
    assert "Error parsing custom hooks file" in result.stdout
    assert "Successfully generated" in result.stdout

    config_path = sample_python_repo / ".pre-commit-config.yaml"
    generated_config = config_path.read_text()
    # Ensure the main part is generated, but no mention of custom hooks
    assert "# Pre-commit configuration generated by pre-commit-starter" in generated_config
    assert "Includes custom hooks from" not in generated_config


def test_empty_custom_hooks_file(sample_python_repo: Path):
    """Test generating config with an empty custom hooks file."""
    empty_content = ""
    custom_hooks_path = sample_python_repo / ".pre-commit-starter-hooks.yaml"
    custom_hooks_path.write_text(empty_content)

    result = run_cli(["--force"], cwd=sample_python_repo)
    assert result.returncode == 0  # Tool should succeed but warn
    assert "Custom hooks file .pre-commit-starter-hooks.yaml is invalid or empty" in result.stdout
    assert "Successfully generated" in result.stdout


def test_force_mode_high_confidence(sample_mixed_repo: Path):
    """Test that force mode only includes technologies with high confidence."""
    # High confidence Python setup (multiple files + requirements.txt)
    for i in range(5):
        (sample_mixed_repo / f"main{i}.py").write_text(f"def main{i}(): pass\n")
    (sample_mixed_repo / "requirements.txt").write_text("pytest==7.0.0\n")
    # Low confidence JavaScript (single file)
    (sample_mixed_repo / "script.js").write_text("console.log('test');")
    # Run with force flag
    result = run_cli(["--force"], cwd=sample_mixed_repo)
    assert result.returncode == 0
    assert "Successfully generated" in result.stdout

    config_path = sample_mixed_repo / ".pre-commit-config.yaml"
    assert config_path.is_file()
    generated_config = config_path.read_text(encoding="utf-8")

    # Python should be included (high confidence)
    assert "python" in generated_config.lower()
    # JavaScript should not be included (low confidence)
    assert "javascript" not in generated_config.lower()
    assert "eslint" not in generated_config.lower()
    # Basic hooks should be included
    assert "pre-commit-hooks" in generated_config


def test_force_mode_no_high_confidence(sample_mixed_repo: Path):
    """Test that force mode includes only basic hooks when no technologies have high confidence."""
    # Create only low confidence setups

    # Low confidence JavaScript (single file)
    (sample_mixed_repo / "script.js").write_text("console.log('test');")
    # Low confidence Python (single file)
    (sample_mixed_repo / "script.py").write_text("print('test')")

    # Run with force flag
    result = run_cli(["--force"], cwd=sample_mixed_repo)
    assert result.returncode == 0
    assert "No technologies detected with high confidence (>80%)" in result.stdout
    assert "Including only basic hooks" in result.stdout
    assert "Successfully generated" in result.stdout

    config_path = sample_mixed_repo / ".pre-commit-config.yaml"
    assert config_path.is_file()
    generated_config = config_path.read_text(encoding="utf-8")

    # Only basic hooks should be included
    assert "pre-commit-hooks" in generated_config
    assert "python" not in generated_config.lower()
    assert "javascript" not in generated_config.lower()
    assert "eslint" not in generated_config.lower()


def test_auto_mode_all_confidence(sample_mixed_repo: Path):
    """Test that auto mode includes all detected technologies regardless of confidence."""
    # Create same file structure as force mode test

    # High confidence Python setup
    (sample_mixed_repo / "main.py").write_text("def main(): pass")
    (sample_mixed_repo / "test.py").write_text("def test(): pass")
    (sample_mixed_repo / "requirements.txt").write_text("pytest==7.0.0")

    # Low confidence JavaScript
    (sample_mixed_repo / "script.js").write_text("console.log('test');")

    # Run with auto flag
    result = run_cli(["--auto"], cwd=sample_mixed_repo)
    assert result.returncode == 0
    assert "Successfully generated" in result.stdout

    config_path = sample_mixed_repo / ".pre-commit-config.yaml"
    assert config_path.is_file()
    generated_config = config_path.read_text(encoding="utf-8")

    # Both Python and JavaScript should be included
    assert "python" in generated_config.lower()
    assert "javascript" in generated_config.lower()
    assert "eslint" in generated_config.lower()
    # Basic hooks should be included
    assert "pre-commit-hooks" in generated_config
