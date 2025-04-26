"""YAML configuration builder module."""

import json
from pathlib import Path
from typing import Any

import yaml

from .hooks.hook_registry import HookRegistry

# Maximum length for flow-style sequences
MAX_FLOW_STYLE_LENGTH = 5


def str_presenter(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    """Present strings in a more readable format."""
    if "\n" in data:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


class PreCommitYamlDumper(yaml.SafeDumper):
    """Custom YAML dumper for pre-commit configuration."""

    def represent_sequence(
        self, tag: str, sequence: list, flow_style: bool | None = None
    ) -> yaml.Node:
        """Represent sequences in flow style if they are short and simple."""
        # Use flow style for simple string lists (e.g., args) that are short
        if isinstance(sequence, list) and all(isinstance(item, str) for item in sequence):
            if len(sequence) <= MAX_FLOW_STYLE_LENGTH and not any(" " in item for item in sequence):
                flow_style = True
        return super().represent_sequence(tag, sequence, flow_style)


class YAMLBuilder:
    """Builder for pre-commit configuration YAML."""

    def __init__(self, hook_registry: HookRegistry):
        """Initialize the YAML builder."""
        self.hook_registry = hook_registry

    def _merge_hooks(self, hooks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge hooks from the same repository."""
        repo_hooks: dict[str, dict[str, Any]] = {}

        # First, add pre-commit hooks
        for hook_data in hooks:
            repo = hook_data["repo"]
            if repo not in repo_hooks:
                repo_hooks[repo] = {
                    "repo": repo,
                    "rev": hook_data.get("rev", ""),
                    "hooks": [],
                }

            # Convert single hook to hooks list format if needed
            if "hooks" not in hook_data:
                hook_info = {k: v for k, v in hook_data.items() if k not in ["repo", "rev"]}
                repo_hooks[repo]["hooks"].append(hook_info)
            else:
                # Ensure all hook fields are preserved for local hooks
                repo_hooks[repo]["hooks"].extend(hook_data["hooks"])

        # Sort repositories to ensure consistent order, with pre-commit-hooks first
        sorted_repos = sorted(
            repo_hooks.values(),
            key=lambda x: (
                # pre-commit-hooks should be first
                0 if x["repo"] == "https://github.com/pre-commit/pre-commit-hooks" else 1,
                # Then sort by repo URL
                x["repo"],
            ),
        )
        return sorted_repos

    def build_config(
        self, technologies: list, custom_hooks: list[dict[str, Any]] | None = None
    ) -> str:
        """Build pre-commit configuration YAML."""
        # Load hook versions
        user_hook_versions = self._load_user_hook_versions()
        package_hook_versions = self._load_package_hook_versions()
        hook_versions = {**package_hook_versions, **user_hook_versions}

        # Start with basic hooks
        hooks = self.hook_registry.get_basic_hooks()

        # Add hooks for each technology
        tech_names = []
        for tech in technologies:
            if hasattr(tech, "name"):
                tech_name = str(tech.name).lower()
            else:
                tech_name = str(tech).lower()
            tech_names.append(tech_name)
            hooks.extend(self.hook_registry.get_hooks_for_tech(tech_name))

        # Merge hooks from the same repository
        merged_hooks = self._merge_hooks(hooks)

        # Add hook versions
        for hook in merged_hooks:
            if hook["repo"] in hook_versions and not hook.get("rev"):
                hook["rev"] = hook_versions[hook["repo"]]

        # Add custom hooks if provided
        if custom_hooks:
            # Only add custom hooks that don't already exist
            for hook in custom_hooks:
                if not any(h["repo"] == hook["repo"] for h in merged_hooks):
                    merged_hooks.append(hook)

        # Build the configuration
        config = {"repos": merged_hooks}

        # Convert to YAML
        yaml.add_representer(str, str_presenter, Dumper=PreCommitYamlDumper)
        yaml_str = yaml.dump(config, Dumper=PreCommitYamlDumper, sort_keys=False)

        # Post-process: insert a blank line before each top-level '- repo:' entry except the first
        yaml_lines = yaml_str.splitlines()
        processed_lines = []
        for _, line in enumerate(yaml_lines):
            if line.lstrip().startswith("- repo:") and processed_lines:
                # Insert a blank line before this repo (not before the first one)
                if processed_lines[-1].strip() != "":
                    processed_lines.append("")
            processed_lines.append(line)
        yaml_str = "\n".join(processed_lines)

        # Build header
        header_lines = [
            "# Pre-commit configuration generated by pre-commit-starter (https://github.com/Jakub3628800/pre-commit-starter)",
            f"# Technologies detected: {', '.join(tech_names)}",
        ]
        if custom_hooks:
            header_lines.append("# Includes custom hooks from .pre-commit-starter-hooks.yaml")

        # Always end with a single newline
        return "\n".join([*header_lines, "", yaml_str.rstrip()]) + "\n"

    def _load_user_hook_versions(self) -> dict[str, str]:
        """Load hook versions from user's config in $HOME/.pre-commit-starter/
        hook_versions.json."""
        config_dir = Path.home() / ".pre-commit-starter"
        config_file = config_dir / "hook_versions.json"

        try:
            with open(config_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return {}

    def _load_package_hook_versions(self) -> dict[str, str]:
        """Load hook versions from the package's hook_versions.json file."""
        package_config_path = Path(__file__).parent / "hook_versions.json"

        try:
            with open(package_config_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return {}
