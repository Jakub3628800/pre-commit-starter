"""Tests for untested edge cases in render_template.py module."""

from pre_commit_starter.config import PreCommitConfig
from pre_commit_starter.hook_templates import render_config


class TestComplexConfigurations:
    """Test complex configuration scenarios."""

    def test_render_config_all_hooks_enabled(self):
        """Test rendering with all hook types enabled."""
        config = PreCommitConfig(
            python=True,
            python_version="python3.11",
            python_base=True,
            uv_lock=True,
            pyrefly_args=["--strict"],
            js=True,
            typescript=True,
            jsx=True,
            go=True,
            go_critic=True,
            docker=True,
            dockerfile_linting=True,
            github_actions=True,
            workflow_validation=True,
            security_scanning=True,
            yaml=True,
            json=True,
            toml=True,
            xml=True,
            case_conflict=True,
            executables=True,
        )

        result = render_config(config)

        # Verify key sections are present
        assert "python3.11" in result
        assert "ruff" in result
        assert "repos:" in result
        assert "pyrefly" in result

    def test_render_config_minimal_configuration(self):
        """Test rendering with minimal configuration."""
        config = PreCommitConfig()  # All defaults

        result = render_config(config)

        # Should still have basic structure
        assert "repos:" in result
        assert "pre-commit-config.yaml created with" in result

    def test_render_config_python_only_complex(self):
        """Test rendering Python-only configuration with complex parameters."""
        config = PreCommitConfig(
            python=True,
            python_version="python3.9",
            pyrefly_args=["--strict", "--ignore-missing-imports"],
        )

        result = render_config(config)

        assert "python3.9" in result
        assert "--strict" in result

    def test_render_config_structure_validation(self):
        """Test that rendered config has proper YAML structure."""
        config = PreCommitConfig(python=True, yaml=True, python_version="python3.12")
        result = render_config(config)

        # Should have proper YAML structure
        lines = result.split("\n")

        # Check for proper indentation
        repo_lines = [line for line in lines if line.strip().startswith("- repo:")]
        assert len(repo_lines) > 0
        for line in repo_lines:
            assert line.startswith("  - repo:")  # Should be indented

        # Should contain required sections
        assert "repos:" in result
        assert "default_language_version:" in result
