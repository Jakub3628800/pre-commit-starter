"""Hook registry module containing all pre-commit hook configurations."""

from typing import Any, ClassVar


class HookRegistry:
    """Registry of pre-commit hooks for different technologies."""

    # Descriptions for hooks to provide more context in interactive mode
    HOOK_DESCRIPTIONS: ClassVar[dict[str, str]] = {
        # Basic hooks
        "trailing-whitespace": "Remove trailing whitespace from files",
        "end-of-file-fixer": "Ensure files end with a newline",
        "check-yaml": "Check YAML files for syntax errors",
        "check-added-large-files": "Prevent committing large files",
        "check-merge-conflict": "Check for merge conflict strings",
        "detect-private-key": "Detect private keys in code",
        "check-case-conflict": "Check for files with names that differ only in case",
        "check-executables-have-shebangs": "Ensure executables have shebangs",
        "check-toml": "Check TOML files for syntax errors",
        "check-vcs-permalinks": "Check that VCS links are permalinks",
        # Python hooks
        "ruff-format": "Format Python code using Ruff",
        "ruff": "Lint Python code using Ruff",
        "pyright": "Type check Python code using Pyright",
        "validate-pyproject": "Validate pyproject.toml file",
        # JavaScript/TypeScript hooks
        "prettier": "Format code (JS, TS, JSON, CSS, etc.) using Prettier",
        "eslint": "Lint JavaScript/TypeScript code using ESLint",
        # HTML/CSS hooks
        "curlylint": "Lint HTML templates",
        "csslint": "Lint CSS files",
        # YAML/Markdown hooks
        "yamllint": "Lint YAML files",
        "markdownlint": "Lint Markdown files",
        # Docker hooks
        "hadolint": "Lint Dockerfile files",
        # Terraform hooks
        "terraform_fmt": "Format Terraform files",
        "terraform_tflint": "Lint Terraform files using TFLint",
        "terraform_docs": "Generate Terraform documentation",
        "tflint": "Lint Terraform files",
        # Shell hooks
        "shellcheck": "Lint shell scripts",
        # Go hooks
        "golangci-lint": "Lint Go code using GolangCI",
        "go-fmt": "Format Go code",
        "go-imports": "Format Go imports",
        "go-critic": "Examine Go code with additional linters",
        # Rust hooks
        "fmt": "Format Rust code",
        "cargo-check": "Check Rust code for errors",
        "clippy": "Lint Rust code using Clippy",
        # Security hooks
        "gitleaks": "Detect hardcoded secrets in code",
        # Pre-push hooks
        "no-commit-to-branch": "Prevent commits to specific branches",
        # GitHub Actions hooks
        "actionlint": "Lint GitHub Actions workflow files",
        # React hooks
        "react": "Format React files",
    }

    def __init__(self):
        """Initialize the hook registry."""
        self._hooks = {
            "basic": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "id": "trailing-whitespace",
                    "name": "Trim trailing whitespace",
                },
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "id": "end-of-file-fixer",
                    "name": "Fix end of files",
                },
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "id": "check-yaml",
                    "name": "Check YAML",
                },
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "id": "check-added-large-files",
                    "name": "Check for added large files",
                },
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "id": "check-merge-conflict",
                    "name": "Check for merge conflict strings",
                },
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "id": "detect-private-key",
                    "name": "Detect private keys",
                },
                {
                    "repo": "https://github.com/gitleaks/gitleaks",
                    "rev": "v8.24.3",
                    "id": "gitleaks",
                    "name": "Detect hardcoded secrets",
                },
            ],
            "python": [
                {
                    "repo": "https://github.com/astral-sh/ruff-pre-commit",
                    "rev": "v0.11.6",
                    "id": "ruff-format",
                    "name": "Format Python code with Ruff",
                },
                {
                    "repo": "https://github.com/astral-sh/ruff-pre-commit",
                    "rev": "v0.11.6",
                    "id": "ruff",
                    "name": "Run Ruff linter and formatter",
                    "args": ["--fix"],
                },
                {
                    "repo": "https://github.com/RobertCraigie/pyright-python",
                    "rev": "v1.1.399",
                    "id": "pyright",
                    "name": "Run Pyright type checker",
                },
                {
                    "repo": "https://github.com/abravalheri/validate-pyproject",
                    "rev": "v0.15",
                    "id": "validate-pyproject",
                    "name": "Validate pyproject.toml",
                },
            ],
            "javascript": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format JavaScript files",
                    "types": ["javascript"],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v9.0.0",
                    "id": "eslint",
                    "name": "Lint JavaScript files",
                },
            ],
            "typescript": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format TypeScript files",
                    "types": ["typescript"],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v9.0.0",
                    "id": "eslint",
                    "name": "Lint TypeScript files",
                },
            ],
            "html": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format HTML files",
                    "types": ["html"],
                },
                {
                    "repo": "https://github.com/thibaudcolas/curlylint",
                    "rev": "v0.13.1",
                    "id": "curlylint",
                    "name": "Lint HTML templates",
                },
            ],
            "css": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format CSS files",
                    "types": ["css"],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-csslint",
                    "rev": "v1.0.5",
                    "id": "csslint",
                    "name": "Lint CSS files",
                },
            ],
            "json": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format JSON files",
                    "types": ["json"],
                },
            ],
            "markdown": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format Markdown files",
                    "types": ["markdown"],
                },
            ],
            "react": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format React files",
                    "types": ["jsx", "tsx"],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v9.0.0",
                    "id": "eslint",
                    "name": "Lint React files",
                },
            ],
            "yaml": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v4.0.0-alpha.8",
                    "id": "prettier",
                    "name": "Format YAML files",
                    "types": ["yaml"],
                },
            ],
            "shell": [
                {
                    "repo": "https://github.com/shellcheck-py/shellcheck-py",
                    "rev": "v0.9.0.6",
                    "id": "shellcheck",
                    "name": "Lint shell scripts",
                },
            ],
            "go": [
                {
                    "repo": "https://github.com/golangci/golangci-lint",
                    "rev": "v1.56.2",
                    "id": "golangci-lint",
                    "name": "Run golangci-lint",
                },
                {
                    "repo": "https://github.com/dnephin/pre-commit-golang",
                    "rev": "v0.5.1",
                    "id": "go-fmt",
                    "name": "Run go fmt",
                },
                {
                    "repo": "https://github.com/dnephin/pre-commit-golang",
                    "rev": "v0.5.1",
                    "id": "go-imports",
                    "name": "Format Go imports",
                },
                {
                    "repo": "https://github.com/dnephin/pre-commit-golang",
                    "rev": "v0.5.1",
                    "id": "go-vet",
                    "name": "Run go vet",
                },
                {
                    "repo": "https://github.com/dnephin/pre-commit-golang",
                    "rev": "v0.5.1",
                    "id": "go-critic",
                    "name": "Run go-critic",
                },
            ],
            "rust": [
                {
                    "repo": "https://github.com/doublify/pre-commit-rust",
                    "rev": "v1.0",
                    "id": "fmt",
                    "name": "Format Rust code",
                },
                {
                    "repo": "https://github.com/doublify/pre-commit-rust",
                    "rev": "v1.0",
                    "id": "cargo-check",
                    "name": "Check Rust code for errors",
                },
                {
                    "repo": "https://github.com/doublify/pre-commit-rust",
                    "rev": "v1.0",
                    "id": "clippy",
                    "name": "Lint Rust code",
                },
            ],
            "terraform": [
                {
                    "repo": "https://github.com/antonbabenko/pre-commit-terraform",
                    "rev": "v1.88.0",
                    "id": "terraform_fmt",
                    "name": "Format Terraform code",
                },
                {
                    "repo": "https://github.com/antonbabenko/pre-commit-terraform",
                    "rev": "v1.88.0",
                    "id": "terraform_tflint",
                    "name": "Lint Terraform code",
                },
            ],
            "docker": [
                {
                    "repo": "https://github.com/hadolint/hadolint",
                    "rev": "v2.12.0",
                    "id": "hadolint",
                    "name": "Lint Dockerfiles",
                },
            ],
            "github_actions": [
                {
                    "repo": "https://github.com/rhysd/actionlint",
                    "rev": "v1.6.27",
                    "id": "actionlint",
                    "name": "Lint GitHub Actions workflow files",
                },
            ],
        }

    @property
    def hooks(self):
        return self._hooks

    def get_basic_hooks(self) -> list[dict[str, Any]]:
        """Get basic hooks that should be included in all configurations."""
        return self._hooks["basic"]

    def get_hooks_for_tech(self, tech: str) -> list[dict[str, Any]]:
        """Get hooks for a specific technology."""
        return self._hooks.get(tech.lower(), [])

    def get_supported_technologies(self) -> list[str]:
        """Get list of supported technologies."""
        return sorted(tech for tech in self._hooks.keys() if tech != "basic")

    def get_all_hooks(self) -> list[dict[str, Any]]:
        """Return all hooks from all technologies.

        Returns:
            Combined list of all hook configurations.
        """
        all_hooks = self.get_basic_hooks()
        for tech_hooks in self._hooks.values():
            all_hooks.extend(tech_hooks)
        return all_hooks

    def get_common_hooks(self) -> dict:
        """Return the common hooks that apply to multiple file types."""
        return {"basic": self.get_basic_hooks()}

    def get_pre_push_hooks(self) -> dict:
        """Return pre-push hooks.

        Returns:
            Dictionary containing pre-push hook configurations.
        """
        return {
            "repo": "https://github.com/pre-commit/pre-commit-hooks",
            "rev": "v5.0.0",
            "hooks": [
                {
                    "id": "no-commit-to-branch",
                    "args": ["--branch", "main", "--branch", "master"],
                    "stages": ["push"],
                }
            ],
        }

    def get_hook_description(self, hook_id: str) -> str:
        """Get the description of a hook."""
        return self._hooks.get(hook_id, {}).get("description", "")

    def get_hook_ids_for_tech(self, tech: str) -> list[str]:
        """Get all hook IDs available for a technology.

        Args:
            tech: Technology name.

        Returns:
            List of hook IDs for the technology.
        """
        hooks = []
        for hook_config in self.get_hooks_for_tech(tech):
            for hook in hook_config.get("hooks", []):
                hook_id = hook.get("id")
                if hook_id:
                    hooks.append(hook_id)
        return hooks
