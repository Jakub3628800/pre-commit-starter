"""Configuration model for pre-commit hook generation."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PreCommitConfig(BaseModel):
    """Configuration for pre-commit hook generation."""

    # Python version for default_language_version
    python_version: Optional[str] = Field(
        None, description="Python version (e.g., python3.9)"
    )

    # Base hooks options
    yaml_check: bool = Field(
        False, alias="yaml", description="Include YAML syntax checking"
    )
    json_check: bool = Field(
        False, alias="json", description="Include JSON syntax checking"
    )
    toml_check: bool = Field(
        False, alias="toml", description="Include TOML syntax checking"
    )
    xml_check: bool = Field(
        False, alias="xml", description="Include XML syntax checking"
    )
    case_conflict: bool = Field(False, description="Include case conflict checking")
    executables: bool = Field(False, description="Include executable shebang checking")
    symlinks: bool = Field(False, description="Include symlink checking")
    python_base: bool = Field(False, description="Include Python-specific base checks")

    # Python hooks options
    python: bool = Field(False, description="Include Python-specific hooks")
    uv_lock: bool = Field(False, description="Include uv.lock checking")
    mypy_args: Optional[list[str]] = Field(
        None, description="Additional arguments for MyPy"
    )
    additional_dependencies: Optional[list[str]] = Field(
        None, description="Additional dependencies for MyPy"
    )

    # Docker hooks options
    docker: bool = Field(False, description="Include Docker-specific hooks")
    dockerfile_linting: bool = Field(True, description="Include Dockerfile linting")
    dockerignore_check: bool = Field(False, description="Include .dockerignore checks")

    # GitHub Actions hooks options
    github_actions: bool = Field(False, description="Include GitHub Actions hooks")
    workflow_validation: bool = Field(True, description="Include workflow validation")
    security_scanning: bool = Field(False, description="Include security scanning")

    # JavaScript hooks options
    js: bool = Field(False, description="Include JavaScript/TypeScript hooks")
    typescript: bool = Field(False, description="Include TypeScript support")
    jsx: bool = Field(False, description="Include JSX/React support")
    prettier_config: Optional[str] = Field(
        None, description="Prettier config file path"
    )
    eslint_config: Optional[str] = Field(None, description="ESLint config file path")

    # Go hooks options
    go: bool = Field(False, description="Include Go-specific hooks")
    go_critic: bool = Field(False, description="Include go-critic linting")

    @field_validator("python_version")
    @classmethod
    def validate_python_version(cls, v: str) -> str:
        """Validate Python version format."""
        if v is not None and not v.startswith("python"):
            raise ValueError(
                'Python version must start with "python" (e.g., python3.9)'
            )
        return v
