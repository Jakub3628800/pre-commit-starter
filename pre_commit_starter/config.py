"""Configuration model for pre-commit hook generation."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PreCommitConfig(BaseModel):
    """Configuration for pre-commit hook generation."""

    # Python version for default_language_version
    python_version: Optional[str] = Field(None, alias="python_version")

    # Base hooks options
    yaml_check: bool = Field(False, alias="yaml")
    json_check: bool = Field(False, alias="json")
    toml_check: bool = Field(False, alias="toml")
    xml_check: bool = Field(False, alias="xml")
    case_conflict: bool = Field(False)
    executables: bool = Field(False)
    symlinks: bool = Field(False)
    python_base: bool = Field(False)

    # Python hooks options
    python: bool = Field(False)
    uv_lock: bool = Field(False)
    mypy_args: Optional[list[str]] = Field(None)
    additional_dependencies: Optional[list[str]] = Field(None)

    # Docker hooks options
    docker: bool = Field(False)
    dockerfile_linting: bool = Field(True)
    dockerignore_check: bool = Field(False)

    # GitHub Actions hooks options
    github_actions: bool = Field(False)
    workflow_validation: bool = Field(True)
    security_scanning: bool = Field(False)

    # JavaScript hooks options
    js: bool = Field(False)
    typescript: bool = Field(False)
    jsx: bool = Field(False)
    prettier_config: Optional[str] = Field(None)
    eslint_config: Optional[str] = Field(None)

    # Go hooks options
    go: bool = Field(False)
    go_critic: bool = Field(False)

    @field_validator("python_version")
    @classmethod
    def validate_python_version(cls, v: str) -> str:
        """Validate Python version format."""
        if v is not None and not v.startswith("python"):
            raise ValueError(
                'Python version must start with "python" (e.g., python3.9)'
            )
        return v
