"""Configuration file support for check-exports."""

import os
import sys
from pathlib import Path
from typing import List, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


class Config:
    """Represents check-exports configuration.

    Configuration can be loaded from CLI arguments, environment variables, or TOML files.
    Priority order: CLI args > environment variables > config file > defaults.

    Attributes:
        libraries: List of library paths to validate
        json_format: Whether to output in JSON format
        quiet: Whether to suppress success message
        no_color: Whether to disable colored output
        verbose: Whether to show detailed statistics
        exclude_patterns: File patterns to exclude from checking
        max_violations: Maximum allowed violations before failing
    """

    def __init__(
        self,
        libraries: List[str],
        json_format: bool = False,
        quiet: bool = False,
        no_color: bool = False,
        verbose: bool = False,
        exclude_patterns: Optional[List[str]] = None,
        max_violations: Optional[int] = None,
    ) -> None:
        """Initialize configuration object.

        Args:
            libraries: List of library paths to validate (required)
            json_format: Output in JSON format if True (default: False)
            quiet: Suppress success messages if True (default: False)
            no_color: Disable colored output if True (default: False)
            verbose: Show detailed stats if True (default: False)
            exclude_patterns: File patterns to exclude (default: [])
            max_violations: Max violations threshold (default: None)
        """
        self.libraries = libraries
        self.json_format = json_format
        self.quiet = quiet
        self.no_color = no_color
        self.verbose = verbose
        self.exclude_patterns = exclude_patterns or []
        self.max_violations = max_violations

    @staticmethod
    def load_from_file(config_path: Optional[Path] = None) -> Optional["Config"]:
        """
        Load configuration from .check-exports.toml file.

        Args:
            config_path: Path to config file. If None, searches current directory.

        Returns:
            Config object if file found, None otherwise
        """
        if config_path is None:
            config_path = Path(".check-exports.toml")

        if not config_path.exists():
            return None

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            # Extract configuration
            config_data = data.get("tool", {}).get("check-exports", {})
            libraries = config_data.get("libraries", [])
            json_format = config_data.get("json", False)
            quiet = config_data.get("quiet", False)
            no_color = config_data.get("no_color", False)
            verbose = config_data.get("verbose", False)
            exclude_patterns = config_data.get("exclude", [])
            max_violations = config_data.get("max_violations", None)

            if not libraries:
                return None

            return Config(
                libraries=libraries,
                json_format=json_format,
                quiet=quiet,
                no_color=no_color,
                verbose=verbose,
                exclude_patterns=exclude_patterns,
                max_violations=max_violations,
            )

        except FileNotFoundError:
            # Config file doesn't exist, which is fine
            return None
        except (OSError, ValueError) as e:
            # OSError for file read issues, ValueError for other config problems
            print(f"Error reading config file {config_path}: {e}", file=sys.stderr)
            return None

    @staticmethod
    def load_from_env() -> Optional["Config"]:
        """
        Load configuration from environment variables.

        Supported variables:
        - CHECK_EXPORTS_LIBS: Comma-separated library paths
        - CHECK_EXPORTS_JSON: Set to 'true' for JSON output
        - CHECK_EXPORTS_NO_COLOR: Set to 'true' to disable colors
        - CHECK_EXPORTS_VERBOSE: Set to 'true' for verbose output
        - CHECK_EXPORTS_EXCLUDE: Comma-separated exclude patterns
        - CHECK_EXPORTS_MAX_VIOLATIONS: Maximum violations threshold

        Returns:
            Config object if env vars set, None otherwise
        """
        libs = os.getenv("CHECK_EXPORTS_LIBS", "").strip()
        if not libs:
            return None

        libraries = [lib.strip() for lib in libs.split(",") if lib.strip()]
        json_format = os.getenv("CHECK_EXPORTS_JSON", "").lower() == "true"
        no_color = os.getenv("CHECK_EXPORTS_NO_COLOR", "").lower() == "true"
        verbose = os.getenv("CHECK_EXPORTS_VERBOSE", "").lower() == "true"
        exclude = os.getenv("CHECK_EXPORTS_EXCLUDE", "").split(",")
        exclude_patterns = [e.strip() for e in exclude if e.strip()]

        max_violations_str = os.getenv("CHECK_EXPORTS_MAX_VIOLATIONS", "")
        max_violations = None
        if max_violations_str.isdigit():
            max_violations = int(max_violations_str)

        return Config(
            libraries=libraries,
            json_format=json_format,
            no_color=no_color,
            verbose=verbose,
            exclude_patterns=exclude_patterns,
            max_violations=max_violations,
        )

    def to_dict(self) -> dict:
        """Convert config to dictionary representation."""
        return {
            "libraries": self.libraries,
            "json_format": self.json_format,
            "quiet": self.quiet,
            "no_color": self.no_color,
            "verbose": self.verbose,
            "exclude_patterns": self.exclude_patterns,
            "max_violations": self.max_violations,
        }
