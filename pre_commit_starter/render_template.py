"""Consolidated template rendering for pre-commit configuration.

This module provides a unified interface for generating pre-commit hooks
and rendering complete configurations with all templates located in the hook_templates directory.
"""

from pathlib import Path
from typing import Any, ClassVar, Optional

from jinja2 import Environment, FileSystemLoader

from .config import PreCommitConfig


class TemplateRenderer:
    """Consolidated template renderer with parameter specification."""

    # Parameter specifications for each hook type
    HOOK_PARAMS: ClassVar[dict[str, dict[str, type]]] = {
        "base": {
            "yaml": bool,
            "json": bool,
            "toml": bool,
            "xml": bool,
            "case_conflict": bool,
            "executables": bool,
            "symlinks": bool,
            "python": bool,
        },
        "python": {
            "uv_lock": bool,
            "mypy_args": str,
            "additional_dependencies": list,
        },
        "docker": {
            "dockerfile_linting": bool,
            "dockerignore_check": bool,
        },
        "js": {
            "typescript": bool,
            "jsx": bool,
            "prettier_config": bool,
            "eslint_config": bool,
        },
        "go": {
            "go_critic": bool,
        },
        "github_actions": {
            "workflow_validation": bool,
            "security_scanning": bool,
        },
    }

    @classmethod
    def get_hook_params(cls, hook_type: str) -> dict[str, type]:
        """Get the parameters for a specific hook type.

        Args:
            hook_type: The type of hook to get parameters for

        Returns:
            Dictionary mapping parameter names to their types
        """
        return cls.HOOK_PARAMS.get(hook_type, {})

    @classmethod
    def list_hook_types(cls) -> list[str]:
        """List all available hook types."""
        return list(cls.HOOK_PARAMS.keys())

    @classmethod
    def generate_hooks(cls, hook_type: str, **kwargs: Any) -> str:
        """Generate hooks for the specified type with given parameters.

        Args:
            hook_type: The type of hook to generate
            **kwargs: Parameters for the hook generation

        Returns:
            Generated hook configuration as string

        Raises:
            ValueError: If hook_type is not supported
        """
        template_mapping = {
            "base": "base.j2",
            "python": "python.j2",
            "docker": "docker.j2",
            "js": "js.j2",
            "go": "go.j2",
            "github_actions": "github_actions.j2",
        }

        if hook_type not in template_mapping:
            raise ValueError(f"Unsupported hook type: {hook_type}")

        # Get the hook_templates directory path
        templates_dir = Path(__file__).parent / "hook_templates"

        # Create Jinja2 environment
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template(template_mapping[hook_type])

        return template.render(**kwargs)

    @classmethod
    def generate_meta_wrapper(
        cls, content: str, python_version: Optional[str] = None
    ) -> str:
        """Generate the meta wrapper for pre-commit config.

        Args:
            content: The rendered hooks content
            python_version: Python version for default_language_version
        """
        templates_dir = Path(__file__).parent / "hook_templates"
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template("meta.j2")

        return template.render(content=content, python_version=python_version)

    @classmethod
    def render_config(cls, config: PreCommitConfig) -> str:
        """Render the complete pre-commit configuration.

        Args:
            config: Pre-commit configuration object

        Returns:
            Complete pre-commit configuration as YAML string
        """
        hooks_content = []

        # Generate base hooks
        base_content = cls.generate_hooks(
            "base",
            yaml=config.yaml_check,
            json=config.json_check,
            toml=config.toml_check,
            xml=config.xml_check,
            case_conflict=config.case_conflict,
            executables=config.executables,
            symlinks=config.symlinks,
            python=config.python_base,
        )
        hooks_content.append(base_content)

        # Generate Python hooks if requested
        if config.python:
            python_content = cls.generate_hooks(
                "python",
                uv_lock=config.uv_lock,
                mypy_args=config.mypy_args,
                additional_dependencies=config.additional_dependencies,
            )
            hooks_content.append(python_content)

        # Generate Docker hooks if requested
        if config.docker:
            docker_content = cls.generate_hooks(
                "docker",
                dockerfile_linting=config.dockerfile_linting,
                dockerignore_check=config.dockerignore_check,
            )
            hooks_content.append(docker_content)

        # Generate GitHub Actions hooks if requested
        if config.github_actions:
            github_actions_content = cls.generate_hooks(
                "github_actions",
                workflow_validation=config.workflow_validation,
                security_scanning=config.security_scanning,
            )
            hooks_content.append(github_actions_content)

        # Generate JavaScript hooks if requested
        if config.js:
            js_content = cls.generate_hooks(
                "js",
                typescript=config.typescript,
                jsx=config.jsx,
                prettier_config=config.prettier_config,
                eslint_config=config.eslint_config,
            )
            hooks_content.append(js_content)

        # Generate Go hooks if requested
        if config.go:
            go_content = cls.generate_hooks("go", go_critic=config.go_critic)
            hooks_content.append(go_content)

        # Combine all hooks
        combined_content = "\n\n".join(hooks_content)

        # Wrap with meta template
        return cls.generate_meta_wrapper(
            content=combined_content, python_version=config.python_version
        )


# Convenience functions for direct access (backwards compatibility)
def generate_base_hooks(**kwargs: Any) -> str:
    """Generate base hooks. See TemplateRenderer.HOOK_PARAMS['base'] for parameters."""
    return TemplateRenderer.generate_hooks("base", **kwargs)


def generate_python_hooks(**kwargs: Any) -> str:
    """Generate Python hooks. See TemplateRenderer.HOOK_PARAMS['python'] for parameters."""
    return TemplateRenderer.generate_hooks("python", **kwargs)


def generate_docker_hooks(**kwargs: Any) -> str:
    """Generate Docker hooks. See TemplateRenderer.HOOK_PARAMS['docker'] for parameters."""
    return TemplateRenderer.generate_hooks("docker", **kwargs)


def generate_js_hooks(**kwargs: Any) -> str:
    """Generate JavaScript hooks. See TemplateRenderer.HOOK_PARAMS['js'] for parameters."""
    return TemplateRenderer.generate_hooks("js", **kwargs)


def generate_go_hooks(**kwargs: Any) -> str:
    """Generate Go hooks. See TemplateRenderer.HOOK_PARAMS['go'] for parameters."""
    return TemplateRenderer.generate_hooks("go", **kwargs)


def generate_github_actions_hooks(**kwargs: Any) -> str:
    """Generate GitHub Actions hooks.

    See TemplateRenderer.HOOK_PARAMS['github_actions'] for parameters.
    """
    return TemplateRenderer.generate_hooks("github_actions", **kwargs)


def generate_meta_wrapper(content: str, python_version: Optional[str] = None) -> str:
    """Generate the meta wrapper for pre-commit config.

    Args:
        content: The rendered hooks content
        python_version: Python version for default_language_version
    """
    return TemplateRenderer.generate_meta_wrapper(content, python_version)


def render_config(config: PreCommitConfig) -> str:
    """Render the complete pre-commit configuration.

    Args:
        config: Pre-commit configuration object

    Returns:
        Complete pre-commit configuration as YAML string
    """
    return TemplateRenderer.render_config(config)


# Parameter documentation
HOOK_DOCUMENTATION = {
    "base": """
    Base hooks for common pre-commit functionality:
    - yaml: Include YAML syntax checking
    - json: Include JSON syntax checking
    - toml: Include TOML syntax checking
    - xml: Include XML syntax checking
    - case_conflict: Include case conflict checking
    - executables: Include executable shebang checking
    - symlinks: Include symlink checking
    - python: Include Python AST checking
    """,
    "python": """
    Python-specific hooks:
    - uv_lock: Include uv.lock checking
    - mypy_args: Additional arguments for mypy
    - additional_dependencies: Additional dependencies for mypy
    """,
    "docker": """
    Docker-specific hooks:
    - dockerfile_linting: Include Dockerfile linting
    - dockerignore_check: Include .dockerignore checking
    """,
    "js": """
    JavaScript/TypeScript-specific hooks:
    - typescript: Include TypeScript support
    - jsx: Include JSX support
    - prettier_config: Include Prettier configuration
    - eslint_config: Include ESLint configuration
    """,
    "go": """
    Go-specific hooks:
    - go_critic: Include go-critic linting
    """,
    "github_actions": """
    GitHub Actions-specific hooks:
    - workflow_validation: Include workflow validation
    - security_scanning: Include security scanning
    """,
}


def get_hook_documentation(hook_type: str) -> str:
    """Get documentation for a specific hook type."""
    return HOOK_DOCUMENTATION.get(hook_type, "No documentation available.")


def print_all_hook_params() -> None:
    """Print all available hook types and their parameters."""
    for hook_type in TemplateRenderer.list_hook_types():
        print(f"\n{hook_type.upper()} HOOKS:")
        params = TemplateRenderer.get_hook_params(hook_type)
        for param_name, param_type in params.items():
            print(f"  {param_name}: {param_type.__name__}")
        print(get_hook_documentation(hook_type))


def main() -> None:
    """Main entry point for the render_template module."""
    print("Available hook types:")
    for hook_type in TemplateRenderer.list_hook_types():
        print(f"  - {hook_type}")

    print("\nUse print_all_hook_params() for detailed parameter information.")
    print_all_hook_params()


if __name__ == "__main__":
    main()
