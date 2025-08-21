from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader

from pre_commit_starter.config import PreCommitConfig


HOOK_PARAMS: dict[str, dict[str, type]] = {
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


def _generate_hooks(hook_type: str, **kwargs: Any) -> str:
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

    templates_dir = Path(__file__).parent

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_mapping[hook_type])

    return template.render(**kwargs)


def _generate_meta_wrapper(content: str, python_version: Optional[str] = None) -> str:
    templates_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("meta.j2")

    return template.render(content=content, python_version=python_version)


def render_config(config: PreCommitConfig) -> str:
    """Render the complete pre-commit configuration.

    Args:
        config: Pre-commit configuration object

    Returns:
        Complete pre-commit configuration as YAML string
    """
    hooks_content = []

    base_content = _generate_hooks(
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

    if config.python:
        python_content = _generate_hooks(
            "python",
            uv_lock=config.uv_lock,
            mypy_args=config.mypy_args,
            additional_dependencies=config.additional_dependencies,
        )
        hooks_content.append(python_content)

    if config.docker:
        docker_content = _generate_hooks(
            "docker",
            dockerfile_linting=config.dockerfile_linting,
            dockerignore_check=config.dockerignore_check,
        )
        hooks_content.append(docker_content)

    if config.github_actions:
        github_actions_content = _generate_hooks(
            "github_actions",
            workflow_validation=config.workflow_validation,
            security_scanning=config.security_scanning,
        )
        hooks_content.append(github_actions_content)

    if config.js:
        js_content = _generate_hooks(
            "js",
            typescript=config.typescript,
            jsx=config.jsx,
            prettier_config=config.prettier_config,
            eslint_config=config.eslint_config,
        )
        hooks_content.append(js_content)

    if config.go:
        go_content = _generate_hooks("go", go_critic=config.go_critic)
        hooks_content.append(go_content)

    combined_content = "\n\n".join(hooks_content)

    return _generate_meta_wrapper(
        content=combined_content, python_version=config.python_version
    )


def generate_base_hooks(**kwargs: Any) -> str:
    return _generate_hooks("base", **kwargs)


def generate_python_hooks(**kwargs: Any) -> str:
    return _generate_hooks("python", **kwargs)


def generate_docker_hooks(**kwargs: Any) -> str:
    return _generate_hooks("docker", **kwargs)


def generate_js_hooks(**kwargs: Any) -> str:
    return _generate_hooks("js", **kwargs)


def generate_go_hooks(**kwargs: Any) -> str:
    return _generate_hooks("go", **kwargs)


def generate_github_actions_hooks(**kwargs: Any) -> str:
    return _generate_hooks("github_actions", **kwargs)


def generate_meta_wrapper(content: str, python_version: Optional[str] = None) -> str:
    templates_dir = Path(__file__).parent / "hook_templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("meta.j2")

    return template.render(content=content, python_version=python_version)
