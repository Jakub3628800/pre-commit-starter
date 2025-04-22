"""YAML builder module for generating pre-commit configurations."""

import json
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Set, Union

import yaml

from .hook_registry import HookRegistry


class PreCommitDumper(yaml.SafeDumper):
    """Custom YAML dumper for pre-commit configuration."""

    def represent_scalar(
        self, tag: str, value: str, style: Optional[str] = None
    ) -> yaml.ScalarNode:
        """Represent scalar values with proper quoting."""
        if isinstance(value, str):
            if value.startswith("@") or "/" in value or " " in value or "-" in value:
                style = '"'
        return super().represent_scalar(tag, value, style)

    def represent_sequence(
        self, tag: str, sequence: Any, flow_style: Optional[bool] = None
    ) -> yaml.SequenceNode:
        """Represent sequences with proper flow style."""
        if isinstance(sequence, list) and all(isinstance(item, str) for item in sequence):
            flow_style = True
        return super().represent_sequence(tag, sequence, flow_style)


class YAMLBuilder:
    """Builds pre-commit YAML configuration based on detected technologies."""

    # Default hook versions - used as fallback if versions file not found
    DEFAULT_HOOK_VERSIONS: ClassVar[Dict[str, str]] = {
        "https://github.com/pre-commit/pre-commit-hooks": "v5.0.0",
        "https://github.com/astral-sh/ruff-pre-commit": "v0.11.6",
        "https://github.com/RobertCraigie/pyright-python": "v1.1.399",
        "https://github.com/abravalheri/validate-pyproject": "v0.24.1",
        "https://github.com/gitleaks/gitleaks": "v8.24.3",
        "https://github.com/psf/black": "25.1.0",
        "https://github.com/pycqa/isort": "6.0.1",
        "https://github.com/pycqa/flake8": "7.2.0",
        "https://github.com/pre-commit/mirrors-prettier": "v4.0.0-alpha.8",
        "https://github.com/pre-commit/mirrors-eslint": "v9.25.0",
        "https://github.com/thibaudcolas/curlylint": "v0.13.1",
        "https://github.com/pre-commit/mirrors-csslint": "v1.0.5",
        "https://github.com/adrienverge/yamllint": "v1.37.0",
        "https://github.com/igorshubovych/markdownlint-cli": "v0.44.0",
        "https://github.com/hadolint/hadolint": "v2.12.0",
        "https://github.com/antonbabenko/pre-commit-terraform": "v1.83.5",
        "https://github.com/terraform-linters/tflint": "v0.48.0",
        "https://github.com/shellcheck-py/shellcheck-py": "v0.10.0.1",
        "https://github.com/golangci/golangci-lint": "v1.55.2",
        "https://github.com/dnephin/pre-commit-golang": "v0.5.1",
        "https://github.com/doublify/pre-commit-rust": "v1.0",
    }

    def __init__(self, hook_registry: HookRegistry, custom_hooks_data: Optional[Dict] = None):
        """Initialize YAMLBuilder with a hook registry and optional custom hooks.

        Args:
            hook_registry: The HookRegistry instance.
            custom_hooks_data: Parsed YAML data from the custom hooks file, expected
                               to be a dictionary with a 'repos' key.
        """
        self.hook_registry = hook_registry
        # Store custom hooks, ensuring it's a list if valid
        self.custom_repos = []
        if custom_hooks_data and isinstance(custom_hooks_data.get("repos"), list):
            self.custom_repos = custom_hooks_data["repos"]
        elif custom_hooks_data:
            # Warning already printed in main.py, just ensure we don't use invalid data
            pass

        # Load hook versions from external file if available
        self.hook_versions = self._load_hook_versions()

    def _load_hook_versions(self) -> Dict[str, str]:
        """Load hook versions from external files.

        Looks for hook versions in:
        1. ~/.prec-hook-autodetect/versions.json
        2. src/generator/hook_versions.json

        Falls back to hardcoded defaults if not found.

        Returns:
            Dictionary mapping hook repository URLs to version strings
        """
        # Try user's home directory first
        user_config_path = Path.home() / ".prec-hook-autodetect" / "versions.json"
        if user_config_path.exists():
            try:
                with open(user_config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # Fall back to default versions if user config is invalid
                pass

        # Try package directory
        package_dir = Path(__file__).parent
        package_config_path = package_dir / "hook_versions.json"
        if package_config_path.exists():
            try:
                with open(package_config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # Fall back to default versions if package config is invalid
                pass

        # Fall back to hardcoded defaults
        return self.DEFAULT_HOOK_VERSIONS

    def _sort_repos(self, repos: List[Dict]) -> List[Dict]:
        """Sort repositories to prioritize pre-commit hooks."""
        priority_map = {
            "https://github.com/pre-commit/pre-commit-hooks": 0,  # Basic checks first
            "https://github.com/gitleaks/gitleaks": 1,  # Security checks second
            # Python tools
            "https://github.com/astral-sh/ruff-pre-commit": 10,
            "https://github.com/psf/black": 11,
            "https://github.com/pycqa/isort": 12,
            "https://github.com/pycqa/flake8": 13,
            "https://github.com/RobertCraigie/pyright-python": 14,
            "https://github.com/abravalheri/validate-pyproject": 15,
            # JavaScript and web tools
            "https://github.com/pre-commit/mirrors-prettier": 20,
            "https://github.com/pre-commit/mirrors-eslint": 21,
            "https://github.com/thibaudcolas/curlylint": 22,
            "https://github.com/pre-commit/mirrors-csslint": 23,
            # Document formats
            "https://github.com/adrienverge/yamllint": 30,
            "https://github.com/markdownlint/markdownlint": 31,
            # Infrastructure and DevOps tools
            "https://github.com/hadolint/hadolint": 40,
            "https://github.com/antonbabenko/pre-commit-terraform": 41,
            "https://github.com/terraform-linters/tflint": 42,
            "https://github.com/shellcheck-py/shellcheck-py": 43,
            # Systems languages
            "https://github.com/golangci/golangci-lint": 50,
            "https://github.com/dnephin/pre-commit-golang": 51,
            "https://github.com/doublify/pre-commit-rust": 60,
        }

        def get_priority(repo: Dict) -> int:
            repo_url = repo["repo"]
            return priority_map.get(repo_url, 999)

        return sorted(repos, key=get_priority)

    def _merge_hooks(self, hooks: list[dict], new_hooks: list[dict]) -> list[dict]:
        """Merge hooks from the same repository."""
        merged: dict[str, list[dict]] = {}

        # First, collect all hooks by ID
        for hook in hooks:
            hook_id = hook["id"]
            if hook_id not in merged:
                merged[hook_id] = []
            merged[hook_id].append(hook.copy())

        # Then merge in new hooks
        for new_hook in new_hooks:
            hook_id = new_hook["id"]
            if hook_id not in merged:
                merged[hook_id] = []

            # Special handling for prettier hook
            if hook_id == "prettier":
                # Check if we already have a hook with the same types
                new_hook_copy = new_hook.copy()
                types = new_hook.get("types", [])
                found_match = False

                # For JavaScript prettier hooks, remove the types field if it exists
                if types and ("javascript" in types):
                    new_hook_copy.pop("types", None)
                    new_hook_copy["name"] = "Format JavaScript code"

                for existing_hook in merged[hook_id]:
                    existing_types = existing_hook.get("types", [])
                    if types == existing_types:
                        # Merge additional_dependencies if present
                        if "additional_dependencies" in new_hook:
                            if "additional_dependencies" not in existing_hook:
                                existing_hook["additional_dependencies"] = []
                            deps = set(existing_hook["additional_dependencies"])
                            deps.update(new_hook["additional_dependencies"])
                            existing_hook["additional_dependencies"] = sorted(list(deps))
                        found_match = True
                        break

                if not found_match:
                    merged[hook_id].append(new_hook_copy)
            else:
                # For other hooks, just take the latest version
                merged[hook_id] = [new_hook.copy()]

        # Flatten the hooks list
        result = []
        for hooks_list in merged.values():
            result.extend(hooks_list)
        return result

    def _flatten_hooks(self, hook_data: List[Dict]) -> List[Dict]:
        """Flatten nested hook structure and ensure correct versions."""
        repos_by_url: Dict[str, Dict[str, Any]] = {}

        # Process each repo
        for repo_entry in hook_data:
            repo_url = repo_entry["repo"]
            hooks = repo_entry["hooks"]

            # Get latest rev for this repo
            rev = self.hook_versions.get(repo_url, repo_entry.get("rev", "main"))

            # Add to existing repo or create a new one
            if repo_url in repos_by_url:
                # Merge hooks for this repo
                repos_by_url[repo_url]["hooks"] = self._merge_hooks(
                    repos_by_url[repo_url]["hooks"], hooks
                )
            else:
                # Create a new repo entry
                repos_by_url[repo_url] = {"repo": repo_url, "rev": rev, "hooks": hooks}

        return list(repos_by_url.values())

    def build_config(self, detected_techs: Union[List[str], Set[str]]) -> str:
        """Build pre-commit configuration based on detected technologies.

        Args:
            detected_techs: List or set of technology names

        Returns:
            YAML configuration as a string
        """
        # Convert to set if it's a list
        techs = set(detected_techs)

        # Always include basic hooks
        repos = self.hook_registry.get_basic_hooks()

        # Include hooks for each detected technology
        tech_hooks = []
        for tech in techs:
            tech_hooks.extend(self.hook_registry.get_hooks_for_tech(tech))

        # Flatten hooks - handles deduplication and version management
        flattened_hooks = self._flatten_hooks(tech_hooks)

        # Combine all repos
        repos.extend(flattened_hooks)

        # Append custom hooks if they exist
        if self.custom_repos:
            repos.extend(self.custom_repos)

        # Sort repos for consistent and logical ordering
        sorted_repos = self._sort_repos(repos)

        # Create header comment
        header = [
            "---",
            "# Pre-commit configuration generated by prec-hook-autodetect",
        ]

        # Add detected technologies to header if any were found
        if techs:
            header.append(f"# Technologies detected: {', '.join(sorted(techs))}")
        else:
            header.append("# No technologies detected")

        header.extend(
            [
                "# To install: pre-commit install",
                "# To update: pre-commit autoupdate",
            ]
        )

        if self.custom_repos:
            header.append("# Includes custom hooks from .prec-hook-autodetect-hooks.yaml")

        header_str = "\n".join(header) + "\n\n"

        # Configure custom dumper to handle formatting
        yaml.add_representer(
            list,
            lambda dumper, data: dumper.represent_sequence(
                "tag:yaml.org,2002:seq",
                data,
                flow_style=all(isinstance(item, str) for item in data),
            ),
            Dumper=PreCommitDumper,
        )

        # Generate YAML with blank lines between repositories
        # Instead of using yaml.dump directly on the whole config, dump each repo separately
        # and add blank lines
        yaml_lines = ["repos:"]

        for i, repo in enumerate(sorted_repos):
            # Add a blank line before each repo except the first one
            if i > 0:
                yaml_lines.append("")

            # Create a temporary dict with just this repo and dump it
            # then extract just the repo-specific YAML (skipping the "repos:" line)
            repo_yaml = yaml.dump({"repos": [repo]}, sort_keys=False, Dumper=PreCommitDumper)
            repo_lines = repo_yaml.splitlines()[1:]  # Skip the "repos:" line
            yaml_lines.extend(repo_lines)

        # Join the lines to form the final YAML
        yaml_str = "\n".join(yaml_lines)

        # Return configuration with header
        return header_str + yaml_str

    def _load_user_hook_versions(self) -> Dict[str, str]:
        """Load hook versions from user's config in $HOME/.prec-hook-autodetect/
        hook_versions.json."""
        user_config_path = Path.home() / ".prec-hook-autodetect" / "hook_versions.json"
        if user_config_path.exists():
            try:
                with open(user_config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # Fall back to default versions if user config is invalid
                pass
        return {}

    def _load_package_hook_versions(self) -> Dict[str, str]:
        """Load hook versions from the package's hook_versions.json file."""
        package_config_path = Path(__file__).parent / "hook_versions.json"
        if package_config_path.exists():
            try:
                with open(package_config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # Fall back to default versions if package config is invalid
                pass
        return {}
