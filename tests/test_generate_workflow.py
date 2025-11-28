"""Tests for generate_workflow module."""



from pre_commit_tools.generate_workflow import generate_workflow


def test_generate_workflow_basic():
    """Test basic workflow generation."""
    workflow = generate_workflow()

    assert "name: pre-commit" in workflow
    assert "on:" in workflow
    assert "jobs:" in workflow
    assert "pre-commit:" in workflow
    assert "uvx pre-commit run --all-files" in workflow
    assert "astral-sh/setup-uv@v4" in workflow


def test_generate_workflow_custom_branch():
    """Test workflow generation with custom branch."""
    workflow = generate_workflow(main_branch="master")

    assert "branches: [ master ]" in workflow


def test_generate_workflow_with_config(tmp_path):
    """Test workflow generation with pre-commit config."""
    # Create a test config
    config_file = tmp_path / ".pre-commit-config.yaml"
    config_file.write_text(
        """
default_language_version:
  python: python3.12
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.0
    hooks:
      - id: trailing-whitespace
"""
    )

    workflow = generate_workflow(config_path=config_file)

    assert "python-version: '3.12'" in workflow


def test_generate_workflow_write_file(tmp_path):
    """Test writing workflow to file."""
    output_file = tmp_path / ".github" / "workflows" / "pre-commit.yml"

    generate_workflow(output_path=output_file, main_branch="main")

    assert output_file.exists()
    content = output_file.read_text()
    assert "name: pre-commit" in content
    assert "branches: [ main ]" in content


def test_generate_workflow_skip_no_commit_branch():
    """Test that no-commit-to-branch is skipped in CI."""
    workflow = generate_workflow()

    assert "SKIP: no-commit-to-branch" in workflow
