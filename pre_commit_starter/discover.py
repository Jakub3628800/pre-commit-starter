"""Discovery script for detecting project technologies and generating config."""

import argparse
import fnmatch
import json
from pathlib import Path
from typing import Optional

from . import constants
from .config import PreCommitConfig


def _parse_dependency_name(dep: str) -> str:
    """Extracts the package name from a dependency string."""
    # This is a simple parser, might not cover all edge cases
    # e.g. `requests[security]>=2.0.0` -> `requests`
    for marker in ["==", ">=", "<=", "~=", ">", "<", "["]:
        if marker in dep:
            dep = dep.split(marker)[0]
    return dep.strip()


def detect_dependencies(path: Path, *, include_dev: bool) -> set[str]:
    """
    Detect project dependencies from pyproject.toml and requirements files.

    :param path: The project path to scan.
    :param include_dev: Whether to include development dependencies.
    """
    dependencies: set[str] = set()
    pyproject_file = path / "pyproject.toml"

    # 1. Parse pyproject.toml
    if pyproject_file.is_file():
        tomllib = None
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                pass  # No TOML parser available

        if tomllib:
            try:
                with pyproject_file.open("rb") as f:
                    data = tomllib.load(f)
                project_data = data.get("project", {})

                # Main dependencies
                main_deps = project_data.get("dependencies", [])
                for dep in main_deps:
                    dependencies.add(_parse_dependency_name(dep))

                # Optional/dev dependencies
                if include_dev:
                    opt_deps = project_data.get("optional-dependencies", {})
                    for group in opt_deps.values():
                        for dep in group:
                            dependencies.add(_parse_dependency_name(dep))
            except (tomllib.TOMLDecodeError, IOError, OSError):
                pass  # Ignore malformed TOML or file read errors

    # 2. Parse requirements files
    req_files = ["requirements.txt"]
    if include_dev:
        req_files.extend(["requirements-dev.txt", "dev-requirements.txt"])

    for req_filename in req_files:
        req_file = path / req_filename
        if req_file.is_file():
            try:
                with req_file.open(encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith(("#", "-")):
                            dependencies.add(_parse_dependency_name(line))
            except (IOError, OSError, UnicodeDecodeError):
                pass

    return dependencies


def get_required_type_stubs(dependencies: set[str]) -> set[str]:
    """Get type stub packages required for the given dependencies."""
    required_stubs = set()

    for dep in dependencies:
        # Check both the exact name and lowercase version
        for pkg_name in [dep, dep.lower()]:
            if pkg_name in constants.MYPY_PACKAGE_TO_STUB_MAP:
                required_stubs.add(constants.MYPY_PACKAGE_TO_STUB_MAP[pkg_name])
                break

    return required_stubs


def should_include_mypy_stubs(path: Path) -> bool:
    """Check if project should include type stubs for MyPy."""
    dependencies = detect_dependencies(path, include_dev=True)
    required_stubs = get_required_type_stubs(dependencies)
    return len(required_stubs) > 0


def read_gitignore_patterns(path: Path) -> set[str]:
    """Read .gitignore file and return patterns, including sensible defaults."""
    patterns = set(constants.DEFAULT_IGNORE_PATTERNS)
    gitignore_file = path / ".gitignore"
    if gitignore_file.is_file():
        try:
            with gitignore_file.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except IOError:
            pass  # Ignore errors if .gitignore can't be read
    return patterns


def is_path_ignored(
    file_path: Path, project_root: Path, ignore_patterns: set[str]
) -> bool:
    """Check if a file should be ignored based on gitignore-style patterns."""
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        return True  # File is not relative to the project root

    dir_patterns = {p.rstrip("/") for p in ignore_patterns if p.endswith("/")}
    file_patterns = {p for p in ignore_patterns if not p.endswith("/")}

    # 1. Check if the file is in an ignored directory
    # This checks if any part of the path is a subdirectory to be ignored
    if any(part in dir_patterns for part in rel_path.parts):
        return True

    # 2. Check if the file path or name matches a file pattern
    rel_path_str = str(rel_path)
    for pattern in file_patterns:
        if fnmatch.fnmatch(rel_path_str, pattern) or fnmatch.fnmatch(
            file_path.name, pattern
        ):
            return True

    return False


def discover_files(path: Path) -> set[str]:
    """Discover all files in the given path (recursive), respecting .gitignore."""
    discovered_items = set()
    ignore_patterns = read_gitignore_patterns(path)

    for file_path in path.rglob("*"):
        if file_path.is_file() and not is_path_ignored(
            file_path, path, ignore_patterns
        ):
            discovered_items.add(file_path.name.lower())
            if file_path.suffix:
                discovered_items.add(file_path.suffix.lower())

    return discovered_items


def _has_any_file(files: set[str], indicators: set[str]) -> bool:
    """Check if any of the indicator files are present in the discovered files."""
    return not files.isdisjoint(indicators)


def detect_python(files: set[str]) -> bool:
    """Detect if this is a Python project."""
    return _has_any_file(files, constants.PYTHON_INDICATORS)


def detect_uv_lock(files: set[str]) -> bool:
    """Detect if project uses uv with uv.lock file."""
    return _has_any_file(files, constants.UV_LOCK_INDICATORS)


def detect_javascript(files: set[str]) -> bool:
    """Detect if this is a JavaScript project."""
    return _has_any_file(files, constants.JS_INDICATORS)


def detect_typescript(files: set[str]) -> bool:
    """Detect if project uses TypeScript."""
    return _has_any_file(files, constants.TS_INDICATORS)


def detect_jsx(files: set[str]) -> bool:
    """Detect if project uses JSX/React."""
    return _has_any_file(files, constants.JSX_INDICATORS)


def detect_go(files: set[str]) -> bool:
    """Detect if this is a Go project."""
    return _has_any_file(files, constants.GO_INDICATORS)


def detect_docker(files: set[str]) -> bool:
    """Detect if project uses Docker."""
    return _has_any_file(files, constants.DOCKER_INDICATORS)


def detect_github_actions(files: set[str], path: Path) -> bool:
    """Detect if project uses GitHub Actions."""
    # Check for .github/workflows directory
    github_workflows = path / ".github" / "workflows"
    if github_workflows.exists() and github_workflows.is_dir():
        workflow_files = list(github_workflows.glob("*.yml")) + list(
            github_workflows.glob("*.yaml")
        )
        return len(workflow_files) > 0
    return False


def detect_yaml_files(files: set[str]) -> bool:
    """Detect if project has YAML files."""
    return _has_any_file(files, constants.YAML_INDICATORS)


def detect_json_files(files: set[str]) -> bool:
    """Detect if project has JSON files."""
    return _has_any_file(files, constants.JSON_INDICATORS)


def detect_toml_files(files: set[str]) -> bool:
    """Detect if project has TOML files."""
    return _has_any_file(files, constants.TOML_INDICATORS)


def detect_xml_files(files: set[str]) -> bool:
    """Detect if project has XML files."""
    return _has_any_file(files, constants.XML_INDICATORS)


def detect_python_version(path: Path) -> Optional[str]:
    """Attempt to detect Python version from project files."""
    # Check pyproject.toml
    pyproject_file = path / "pyproject.toml"
    if pyproject_file.exists():
        tomllib = None
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                pass  # No TOML parser available

        if tomllib:
            try:
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
            except (tomllib.TOMLDecodeError, IOError, OSError):
                pass  # Ignore malformed TOML or file read errors

    # Check .python-version file
    python_version_file = path / ".python-version"
    if python_version_file.exists():
        try:
            version = python_version_file.read_text().strip()
            if version and not version.startswith("python"):
                return f"python{version}"
            return version if version else None
        except (IOError, OSError, UnicodeDecodeError):
            pass

    return None


# --- Import Discovery ---
def _is_standard_library(module_name: str) -> bool:
    """Check if a module is part of the Python standard library."""
    return module_name in constants.STANDARD_LIBRARY_MODULES


def _discover_local_modules(project_path: Path) -> set[str]:
    """Discovers top-level local modules in the project."""
    local_modules = set()
    for p in project_path.iterdir():
        if p.is_dir() and (p / "__init__.py").is_file():
            local_modules.add(p.name)
        elif p.is_file() and p.suffix == ".py":
            local_modules.add(p.stem)
    return local_modules


def _get_used_imports(path: Path) -> set[str]:
    """Get third-party imports used in the project code by parsing Python files."""
    import ast

    used_imports: set[str] = set()
    local_modules = _discover_local_modules(path)
    ignore_patterns = read_gitignore_patterns(path)

    for file_path in path.rglob("*.py"):
        if is_path_ignored(file_path, path, ignore_patterns):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, IOError, UnicodeDecodeError, TypeError):
            continue  # Skip files that can't be parsed

        for node in ast.walk(tree):
            import_name: Optional[str] = None
            if isinstance(node, ast.Import):
                if node.names:
                    # Get the top-level package of the import
                    import_name = node.names[0].name.split(".")[0]
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:  # Absolute imports only
                    import_name = node.module.split(".")[0]

            if import_name:
                if (
                    import_name not in local_modules
                    and not _is_standard_library(import_name)
                ):
                    package_name = constants.IMPORT_TO_PACKAGE_MAP.get(
                        import_name, import_name
                    )
                    used_imports.add(package_name)

    return used_imports


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

    # Detect additional dependencies for MyPy if Python is detected
    # Include only dependencies that are actually imported in the code
    additional_deps = None
    if has_python:
        # Get actual imports used in the project
        used_imports = _get_used_imports(path)
        if used_imports:
            # Get type stubs for used imports
            type_stubs = get_required_type_stubs(used_imports)
            # Combine used imports and type stubs
            combined_deps = sorted(list(used_imports | type_stubs))
            additional_deps = combined_deps

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
        additional_dependencies=additional_deps,
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
    parser = argparse.ArgumentParser(
        description="Discover project technologies and generate config"
    )
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
