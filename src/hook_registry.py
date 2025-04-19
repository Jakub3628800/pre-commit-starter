"""Hook registry module containing all pre-commit hook configurations."""
from typing import Any, Dict, List, Optional

import yaml


class HookRegistry:
    """Registry of all available pre-commit hooks."""

    # Descriptions for hooks to provide more context in interactive mode
    HOOK_DESCRIPTIONS = {
        # Basic hooks
        "trailing-whitespace": "Remove trailing whitespace from files",
        "end-of-file-fixer": "Ensure files end with a newline",
        "check-yaml": "Check YAML files for syntax errors",
        "check-added-large-files": "Prevent committing large files",
        "check-merge-conflict": "Check for merge conflict strings",
        "detect-private-key": "Detect private keys in code",
        "detect-aws-credentials": "Detect AWS credentials in code",
        "check-case-conflict": "Check for files with names that differ only in case",
        "check-executables-have-shebangs": "Ensure executables have shebangs",
        "check-toml": "Check TOML files for syntax errors",
        "check-vcs-permalinks": "Check that VCS links are permalinks",
        # Python hooks
        "ruff-format": "Format Python code using Ruff",
        "ruff": "Lint Python code using Ruff",
        "pyright": "Type check Python code using Pyright",
        "validate-pyproject": "Validate pyproject.toml file",
        "black": "Format Python code using Black",
        "isort": "Sort Python imports",
        "flake8": "Lint Python code using Flake8",
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
        "go-vet": "Examine Go code for potential issues",
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
    }

    def __init__(self):
        """Initialize the hook registry with predefined hooks."""
        self.basic_hooks = [
            {
                "repo": "https://github.com/pre-commit/pre-commit-hooks",
                "rev": "v4.5.0",
                "hooks": [
                    {
                        "id": "trailing-whitespace",
                        "args": ["--markdown-linebreak-ext=md"],
                    },
                    {"id": "end-of-file-fixer"},
                    {"id": "check-yaml"},
                    {"id": "check-added-large-files"},
                    {"id": "check-merge-conflict"},
                    {"id": "detect-private-key"},
                    {"id": "detect-aws-credentials"},
                    {"id": "check-case-conflict"},
                    {"id": "check-executables-have-shebangs"},
                    {"id": "check-toml"},
                    {"id": "check-vcs-permalinks"},
                ],
            }
        ]

        self.tech_hooks = {
            "python": [
                {
                    "repo": "https://github.com/astral-sh/ruff-pre-commit",
                    "rev": "v0.9.1",
                    "hooks": [
                        {"id": "ruff-format", "name": "Format Python code with Ruff"},
                        {
                            "id": "ruff",
                            "args": ["--fix"],
                            "name": "Lint Python code with Ruff",
                        },
                    ],
                },
                {
                    "repo": "https://github.com/RobertCraigie/pyright-python",
                    "rev": "v1.1.391",
                    "hooks": [
                        {"id": "pyright", "name": "Check Python types with Pyright"}
                    ],
                },
                {
                    "repo": "https://github.com/abravalheri/validate-pyproject",
                    "rev": "v0.13.0",
                    "hooks": [
                        {"id": "validate-pyproject", "name": "Validate pyproject.toml"}
                    ],
                },
                {
                    "repo": "https://github.com/gitleaks/gitleaks",
                    "rev": "v8.22.1",
                    "hooks": [{"id": "gitleaks", "name": "Detect hardcoded secrets"}],
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.12.1",
                    "hooks": [{"id": "black"}],
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "5.13.2",
                    "hooks": [{"id": "isort", "args": ["--profile", "black"]}],
                },
                {
                    "repo": "https://github.com/pycqa/flake8",
                    "rev": "6.1.0",
                    "hooks": [{"id": "flake8"}],
                },
            ],
            "javascript": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types": ["javascript"],
                            "name": "Format JavaScript code",
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v8.56.0",
                    "hooks": [
                        {
                            "id": "eslint",
                            "args": ["--fix"],
                            "types": ["javascript"],
                            "name": "Lint JavaScript code",
                        }
                    ],
                },
            ],
            "typescript": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types": ["typescript"],
                            "additional_dependencies": [
                                "prettier-plugin-organize-imports"
                            ],
                            "name": "Format TypeScript code",
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v8.56.0",
                    "hooks": [
                        {
                            "id": "eslint",
                            "args": ["--fix"],
                            "additional_dependencies": [
                                "@typescript-eslint/eslint-plugin",
                                "@typescript-eslint/parser",
                                "eslint-plugin-import",
                                "typescript",
                            ],
                            "types": ["typescript"],
                            "name": "Lint TypeScript code",
                        }
                    ],
                },
            ],
            "react": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types_or": ["javascript", "jsx", "typescript", "tsx"],
                            "additional_dependencies": [
                                "prettier-plugin-organize-imports"
                            ],
                            "name": "Format React code",
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v8.56.0",
                    "hooks": [
                        {
                            "id": "eslint",
                            "args": ["--fix"],
                            "additional_dependencies": [
                                "eslint-plugin-react",
                                "eslint-plugin-react-hooks",
                                "eslint-plugin-jsx-a11y",
                            ],
                            "files": ".*\\.(js|jsx|ts|tsx)$",
                            "name": "Lint React code",
                        }
                    ],
                },
            ],
            "vue": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "additional_dependencies": [
                                "prettier-plugin-organize-imports",
                                "@vue/eslint-config-prettier",
                            ],
                            "types_or": ["vue", "javascript", "typescript"],
                            "name": "Format Vue code",
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v8.56.0",
                    "hooks": [
                        {
                            "id": "eslint",
                            "args": ["--fix"],
                            "additional_dependencies": [
                                "eslint-plugin-vue",
                                "@vue/eslint-config-typescript",
                            ],
                            "types_or": ["vue", "javascript", "typescript"],
                            "name": "Lint Vue code",
                        }
                    ],
                },
            ],
            "svelte": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "additional_dependencies": [
                                "prettier-plugin-svelte",
                                "prettier-plugin-organize-imports",
                            ],
                            "types_or": ["svelte", "javascript", "typescript"],
                            "name": "Format Svelte code",
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-eslint",
                    "rev": "v8.56.0",
                    "hooks": [
                        {
                            "id": "eslint",
                            "args": ["--fix"],
                            "additional_dependencies": ["eslint-plugin-svelte"],
                            "types_or": ["svelte", "javascript", "typescript"],
                            "name": "Lint Svelte code",
                        }
                    ],
                },
            ],
            "html": [
                {
                    "repo": "https://github.com/thibaudcolas/curlylint",
                    "rev": "v0.13.1",
                    "hooks": [{"id": "curlylint", "name": "Lint HTML templates"}],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types": ["html"],
                            "name": "Format HTML code",
                        }
                    ],
                },
            ],
            "css": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-csslint",
                    "rev": "v1.0.5",
                    "hooks": [{"id": "csslint", "name": "Lint CSS code"}],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types_or": ["css", "scss", "sass", "less"],
                            "name": "Format CSS code",
                        }
                    ],
                },
            ],
            "yaml": [
                {
                    "repo": "https://github.com/adrienverge/yamllint",
                    "rev": "v1.33.0",
                    "hooks": [{"id": "yamllint", "name": "Lint YAML files"}],
                }
            ],
            "markdown": [
                {
                    "repo": "https://github.com/igorshubovych/markdownlint-cli",
                    "rev": "v0.39.0",
                    "hooks": [{"id": "markdownlint", "name": "Lint Markdown files"}],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types": ["markdown"],
                            "name": "Format Markdown files",
                        }
                    ],
                },
            ],
            "docker": [
                {
                    "repo": "https://github.com/hadolint/hadolint",
                    "rev": "v2.12.0",
                    "hooks": [{"id": "hadolint", "name": "Lint Dockerfile"}],
                }
            ],
            "terraform": [
                {
                    "repo": "https://github.com/antonbabenko/pre-commit-terraform",
                    "rev": "v1.83.5",
                    "hooks": [
                        {"id": "terraform_fmt", "name": "Format Terraform code"},
                        {
                            "id": "terraform_docs",
                            "name": "Generate Terraform documentation",
                        },
                    ],
                },
                {
                    "repo": "https://github.com/terraform-linters/tflint",
                    "rev": "v0.48.0",
                    "hooks": [{"id": "tflint", "name": "Lint Terraform code"}],
                },
            ],
            "shell": [
                {
                    "repo": "https://github.com/shellcheck-py/shellcheck-py",
                    "rev": "v0.9.0.6",
                    "hooks": [{"id": "shellcheck", "name": "Lint shell scripts"}],
                }
            ],
            "json": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {
                            "id": "prettier",
                            "types": ["json"],
                            "name": "Format JSON files",
                        }
                    ],
                }
            ],
            "go": [
                {
                    "repo": "https://github.com/golangci/golangci-lint",
                    "rev": "v1.55.2",
                    "hooks": [{"id": "golangci-lint", "name": "Lint Go code"}],
                },
                {
                    "repo": "https://github.com/dnephin/pre-commit-golang",
                    "rev": "v0.5.1",
                    "hooks": [
                        {"id": "go-fmt", "name": "Format Go code"},
                        {"id": "go-vet", "name": "Check for Go code issues"},
                        {"id": "go-imports", "name": "Format Go imports"},
                        {"id": "go-critic", "name": "Additional Go linting"},
                    ],
                },
            ],
            "rust": [
                {
                    "repo": "https://github.com/doublify/pre-commit-rust",
                    "rev": "v1.0",
                    "hooks": [
                        {"id": "fmt", "name": "Format Rust code with rustfmt"},
                        {"id": "cargo-check", "name": "Check Rust code for errors"},
                        {"id": "clippy", "name": "Lint Rust code with clippy"},
                    ],
                }
            ],
        }

        # Pre-push hooks: only added if requested
        self.pre_push_hooks = [
            {
                "repo": "https://github.com/pre-commit/pre-commit-hooks",
                "rev": "v4.5.0",
                "hooks": [
                    {
                        "id": "no-commit-to-branch",
                        "args": ["--branch", "main", "--branch", "master"],
                        "stages": ["push"],
                    }
                ],
            }
        ]

    def get_basic_hooks(self) -> List[Dict[str, Any]]:
        """Return the basic hooks that should be included for all repositories."""
        return self.basic_hooks.copy()

    def get_hooks_for_tech(self, tech: str) -> List[Dict[str, Any]]:
        """Return hooks specific to a technology.

        Args:
            tech: Technology name as it appears in tech_hooks dict.

        Returns:
            List of hook configurations for the technology. Empty list if tech not found.
        """
        return self.tech_hooks.get(tech, []).copy()

    def get_all_hooks(self) -> List[Dict[str, Any]]:
        """Return all hooks from all technologies.

        Returns:
            Combined list of all hook configurations.
        """
        all_hooks = self.get_basic_hooks()
        for tech_hooks in self.tech_hooks.values():
            all_hooks.extend(tech_hooks)
        return all_hooks

    @property
    def hooks(self) -> Dict[str, List[Dict]]:
        """Combined dictionary of all hooks by technology.

        Returns:
            Dict where keys are technology names and values are hook configuration lists.
        """
        return {
            "basic": self.basic_hooks,
            **self.tech_hooks,
            "pre_push": self.pre_push_hooks,
        }

    def get_common_hooks(self) -> Dict:
        """Return the common hooks that apply to multiple file types."""
        return {"basic": self.get_basic_hooks()}

    def get_pre_push_hooks(self) -> Dict:
        """Return pre-push hooks.

        Returns:
            Dictionary containing pre-push hook configurations.
        """
        return {
            "repo": "https://github.com/pre-commit/pre-commit-hooks",
            "rev": "v4.5.0",
            "hooks": [
                {
                    "id": "no-commit-to-branch",
                    "args": ["--branch", "main", "--branch", "master"],
                    "stages": ["push"],
                }
            ],
        }

    def get_hook_description(self, hook_id: str) -> str:
        """Get the description for a hook.

        Args:
            hook_id: The ID of the hook to describe.

        Returns:
            Description string, or generic message if no specific description found.
        """
        return self.HOOK_DESCRIPTIONS.get(
            hook_id, f"Hook '{hook_id}' (no description available)"
        )

    def get_hook_ids_for_tech(self, tech: str) -> List[str]:
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
