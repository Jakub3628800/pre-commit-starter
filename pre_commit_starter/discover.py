"""Discovery script for detecting project technologies and generating config."""

import argparse
import fnmatch
import json
from pathlib import Path
from typing import Optional

from .config import PreCommitConfig


def detect_project_dependencies(path: Path) -> set[str]:
    """Detect project dependencies from pyproject.toml, requirements.txt, etc."""
    dependencies = set()

    # Check pyproject.toml
    pyproject_file = path / "pyproject.toml"
    if pyproject_file.exists():
        toml_lib = None
        try:
            import tomllib

            toml_lib = tomllib
        except ImportError:
            try:
                import tomli

                toml_lib = tomli
            except ImportError:
                pass

        if toml_lib:
            try:
                with open(pyproject_file, "rb") as f:
                    data = toml_lib.load(f)

                # Get dependencies from project.dependencies
                if "project" in data and "dependencies" in data["project"]:
                    for dep in data["project"]["dependencies"]:
                        # Extract package name (before ==, >=, etc.)
                        pkg_name = dep.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
                        dependencies.add(pkg_name)

                # Get dev dependencies
                if "project" in data and "optional-dependencies" in data["project"]:
                    for group in data["project"]["optional-dependencies"].values():
                        for dep in group:
                            pkg_name = dep.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
                            dependencies.add(pkg_name)

            except Exception:
                pass

    # Check requirements.txt files
    for req_file in [
        "requirements.txt",
        "requirements-dev.txt",
        "dev-requirements.txt",
    ]:
        req_path = path / req_file
        if req_path.exists():
            try:
                with open(req_path, encoding="utf-8") as f:
                    for raw_line in f:
                        line = raw_line.strip()
                        if line and not line.startswith("#") and not line.startswith("-"):
                            pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
                            dependencies.add(pkg_name)
            except Exception:
                pass

    return dependencies


def read_gitignore_patterns(path: Path) -> set[str]:
    """Read .gitignore file and return patterns."""
    gitignore_file = path / ".gitignore"
    patterns = set()

    if gitignore_file.exists():
        try:
            with open(gitignore_file, encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except Exception:
            # If we can't read gitignore, continue without it
            pass

    return patterns


def is_ignored_by_gitignore(file_path: Path, project_root: Path, gitignore_patterns: set[str]) -> bool:
    """Check if a file should be ignored based on gitignore patterns."""
    try:
        # Get relative path from project root
        rel_path = file_path.relative_to(project_root)
        rel_path_str = str(rel_path)

        # Check if file is in any parent directory that should be ignored
        for part in rel_path.parts:
            if part in {".git", ".venv", "venv", "env", "node_modules", "__pycache__"}:
                return True

        for pattern in gitignore_patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith("/"):
                if fnmatch.fnmatch(rel_path_str + "/", pattern) or fnmatch.fnmatch(rel_path_str, pattern[:-1]):
                    return True
            # Handle file patterns
            elif fnmatch.fnmatch(rel_path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True

        return False
    except ValueError:
        # File is not relative to project root
        return False


def discover_files(path: Path) -> set[str]:
    """Discover all files in the given path (recursive), respecting .gitignore."""
    files = set()

    # Read gitignore patterns
    gitignore_patterns = read_gitignore_patterns(path)

    # Always exclude .git directory regardless of gitignore
    gitignore_patterns.add(".git/")
    gitignore_patterns.add(".git")

    # Add some basic patterns if no gitignore exists
    if len(gitignore_patterns) <= 2:  # Only .git patterns added
        gitignore_patterns.update(
            {
                "__pycache__/",
                "node_modules/",
                ".venv/",
                "venv/",
                "env/",
                "build/",
                "dist/",
                ".pytest_cache/",
                ".pyrefly_cache/",
                ".ruff_cache/",
            }
        )

    for file_path in path.rglob("*"):
        if file_path.is_file():
            # Skip if ignored by gitignore patterns
            if not is_ignored_by_gitignore(file_path, path, gitignore_patterns):
                files.add(file_path.name.lower())
                # Also add file extensions
                if file_path.suffix:
                    files.add(file_path.suffix.lower())

    return files


def detect_python(files: set[str]) -> bool:
    """Detect if this is a Python project."""
    python_indicators = {
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        "pipfile",
        "poetry.lock",
        "setup.cfg",
        "tox.ini",
        "pytest.ini",
        ".py",
        "manage.py",
        "__init__.py",
    }
    return bool(python_indicators & files)


def detect_uv_lock(files: set[str]) -> bool:
    """Detect if project uses uv with uv.lock file."""
    return "uv.lock" in files


def detect_javascript(files: set[str]) -> bool:
    """Detect if this is a JavaScript project."""
    js_indicators = {
        "package.json",
        "yarn.lock",
        "package-lock.json",
        "npm-shrinkwrap.json",
        ".js",
        ".mjs",
        ".cjs",
        "webpack.config.js",
        "vite.config.js",
        "rollup.config.js",
        "babel.config.js",
        ".babelrc",
    }
    return bool(js_indicators & files)


def detect_typescript(files: set[str]) -> bool:
    """Detect if project uses TypeScript."""
    ts_indicators = {
        "tsconfig.json",
        "tsconfig.base.json",
        "tsconfig.build.json",
        ".ts",
        ".tsx",
        ".d.ts",
    }
    return bool(ts_indicators & files)


def detect_jsx(files: set[str]) -> bool:
    """Detect if project uses JSX/React."""
    jsx_indicators = {
        ".jsx",
        ".tsx",
        "next.config.js",
        "gatsby-config.js",
        "react-scripts",
        ".storybook",
    }
    return bool(jsx_indicators & files)


def detect_go(files: set[str]) -> bool:
    """Detect if this is a Go project."""
    go_indicators = {"go.mod", "go.sum", "main.go", ".go", "vendor"}
    return bool(go_indicators & files)


def detect_docker(files: set[str]) -> bool:
    """Detect if project uses Docker."""
    docker_indicators = {
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".dockerignore",
        "dockerfile.dev",
        "dockerfile.prod",
    }
    return bool(docker_indicators & files)


def detect_github_actions(files: set[str], path: Path) -> bool:
    """Detect if project uses GitHub Actions."""
    # Check for .github/workflows directory
    github_workflows = path / ".github" / "workflows"
    if github_workflows.exists() and github_workflows.is_dir():
        workflow_files = list(github_workflows.glob("*.yml")) + list(github_workflows.glob("*.yaml"))
        return len(workflow_files) > 0
    return False


def detect_yaml_files(files: set[str]) -> bool:
    """Detect if project has YAML files."""
    yaml_indicators = {".yml", ".yaml", "docker-compose.yml", "docker-compose.yaml"}
    return bool(yaml_indicators & files)


def detect_json_files(files: set[str]) -> bool:
    """Detect if project has JSON files."""
    return ".json" in files


def detect_toml_files(files: set[str]) -> bool:
    """Detect if project has TOML files."""
    return ".toml" in files or "pyproject.toml" in files


def detect_xml_files(files: set[str]) -> bool:
    """Detect if project has XML files."""
    return ".xml" in files


def detect_python_version(path: Path) -> Optional[str]:
    """Attempt to detect Python version from project files."""
    # Check pyproject.toml
    pyproject_file = path / "pyproject.toml"
    if pyproject_file.exists():
        try:
            import tomllib

            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)

            # Check requires-python
            project = data.get("project", {})
            requires_python = project.get("requires-python")
            if requires_python and isinstance(requires_python, str):
                # Extract version like ">=3.9" -> "python3.9"
                if ">=" in requires_python:
                    version = requires_python.split(">=")[1].strip()
                    return f"python{version}"
        except Exception:
            pass

    # Check .python-version file
    python_version_file = path / ".python-version"
    if python_version_file.exists():
        try:
            version = python_version_file.read_text().strip()
            if version and not version.startswith("python"):
                return f"python{version}"
            return version if version else None
        except Exception:
            pass

    return None


def find_config_files(path: Path, files: set[str]) -> dict:
    """Find configuration files for various tools."""
    config_files = {}

    # Prettier configs
    prettier_configs = [
        ".prettierrc",
        ".prettierrc.json",
        ".prettierrc.yml",
        ".prettierrc.yaml",
        ".prettierrc.js",
        "prettier.config.js",
    ]
    for config in prettier_configs:
        if config.lower() in files:
            config_files["prettier_config"] = config
            break

    # ESLint configs
    eslint_configs = [
        ".eslintrc",
        ".eslintrc.json",
        ".eslintrc.yml",
        ".eslintrc.yaml",
        ".eslintrc.js",
        "eslint.config.js",
    ]
    for config in eslint_configs:
        if config.lower() in files:
            config_files["eslint_config"] = config
            break

    return config_files


def discover_config(path: Path) -> PreCommitConfig:
    """Discover project configuration by analyzing files."""
    files = discover_files(path)

    # Detect technologies
    has_python = detect_python(files)
    has_js = detect_javascript(files)
    has_typescript = detect_typescript(files)
    has_jsx = detect_jsx(files)
    has_go = detect_go(files)
    has_docker = detect_docker(files)
    has_github_actions = detect_github_actions(files, path)

    # Detect file types
    has_yaml = detect_yaml_files(files)
    has_json = detect_json_files(files)
    has_toml = detect_toml_files(files)
    has_xml = detect_xml_files(files)

    # Detect Python version
    python_version = detect_python_version(path) if has_python else None

    # Find config files
    config_files = find_config_files(path, files)

    # Build configuration
    config = PreCommitConfig(
        python_version=python_version,
        yaml=has_yaml,
        json=has_json,
        toml=has_toml,
        xml=has_xml,
        case_conflict=True,  # Always enable for cross-platform compatibility
        executables=True,  # Always enable for shell script safety
        python=has_python,
        python_base=has_python,  # Include Python base checks if Python detected
        uv_lock=has_python,  # Always use uv for Python projects
        js=has_js,
        typescript=has_typescript,
        jsx=has_jsx,
        go=has_go,
        docker=has_docker,
        github_actions=has_github_actions,
        **config_files,
    )

    return config


def main() -> None:
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(description="Discover project technologies and generate config")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Path to analyze (default: current directory)",
    )
    parser.add_argument(
        "--output",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    # Discover configuration
    config = discover_config(args.path)

    if args.output == "json":
        # Output as JSON
        config_dict = config.model_dump(by_alias=True)
        print(json.dumps(config_dict, indent=2))
    else:
        # Output as YAML (for future use)
        import yaml

        config_dict = config.model_dump(by_alias=True)
        print(yaml.dump(config_dict, default_flow_style=False))


if __name__ == "__main__":
    main()
