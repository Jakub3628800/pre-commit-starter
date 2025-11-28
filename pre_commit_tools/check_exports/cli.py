"""Command-line interface for check-exports."""

import argparse
import sys
from pathlib import Path

from pre_commit_tools.check_exports.validator import validate_libraries
from pre_commit_tools.check_exports.reporter import report_violations, report_success, report_summary
from pre_commit_tools.check_exports.config import Config


def _create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="check-exports",
        description="Validate that non-exported functions are not imported from outside libraries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ENVIRONMENT VARIABLES:
  CHECK_EXPORTS_LIBS            Comma-separated library paths
  CHECK_EXPORTS_JSON            Set to 'true' for JSON output
  CHECK_EXPORTS_NO_COLOR        Set to 'true' to disable colors
  CHECK_EXPORTS_VERBOSE         Set to 'true' for verbose output
  CHECK_EXPORTS_EXCLUDE         Comma-separated exclude patterns
  CHECK_EXPORTS_MAX_VIOLATIONS  Maximum violations threshold
  CHECK_EXPORTS_PUBLIC_SUBMODULES Comma-separated public submodules

CONFIG FILE FORMAT (.check-exports.toml):
  [tool.check-exports]
  libraries = ["./lib1", "./lib2"]
  json = false
  quiet = false
  no_color = false
  verbose = false
  exclude = ["tests/*", "build/*"]
  max_violations = 10
  public_submodules = ["utils", "network"]

EXAMPLES:
  check-exports ./mylib
  check-exports ./lib1 ./lib2 ./lib3
  check-exports --json ./mylib
  check-exports --verbose ./lib1
  check-exports --no-color --quiet ./lib
  check-exports --exclude "tests/*,build/*" ./lib
  check-exports --max-violations 5 ./lib
  check-exports --config ./config.toml
  check-exports --public-submodules "utils,network" ./lib
  CHECK_EXPORTS_LIBS="./lib1,./lib2" check-exports
        """,
    )

    parser.add_argument(
        "libraries",
        nargs="*",
        help="Library paths to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success message",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output (for CI/scripts)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed statistics and timing",
    )
    parser.add_argument(
        "--config",
        help="Load configuration from file (default: .check-exports.toml)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude file patterns (can be specified multiple times or comma-separated)",
    )
    parser.add_argument(
        "--max-violations",
        type=int,
        help="Fail if violations exceed this number",
    )
    parser.add_argument(
        "--public-submodules",
        help="Comma-separated list of submodules allowed to be imported directly",
    )

    return parser


def main() -> int:
    """
    Main entry point for check-exports CLI.

    Returns:
        0 if no violations found, 1 if violations found
    """
    parser = _create_parser()
    parsed_args = parser.parse_args()

    # Get library paths from CLI
    lib_paths = parsed_args.libraries or []

    # Try to load config: env vars > config file > CLI args
    env_config = Config.load_from_env()
    file_config = None
    if not lib_paths:
        file_config = Config.load_from_file(Path(parsed_args.config) if parsed_args.config else None)

    # Merge configs (CLI args take precedence)
    if env_config:
        lib_paths = lib_paths or env_config.libraries
        json_format = parsed_args.json or env_config.json_format
        quiet = parsed_args.quiet or env_config.quiet
        no_color = parsed_args.no_color or env_config.no_color
        verbose = parsed_args.verbose or env_config.verbose
        exclude_patterns = _parse_exclude_patterns(parsed_args.exclude, env_config.exclude_patterns)

        max_violations = parsed_args.max_violations or env_config.max_violations
        public_submodules = _parse_list(parsed_args.public_submodules) or env_config.public_submodules
    elif file_config:
        lib_paths = lib_paths or file_config.libraries
        json_format = parsed_args.json or file_config.json_format
        quiet = parsed_args.quiet or file_config.quiet
        no_color = parsed_args.no_color or file_config.no_color
        verbose = parsed_args.verbose or file_config.verbose
        exclude_patterns = _parse_exclude_patterns(parsed_args.exclude, file_config.exclude_patterns)
        max_violations = parsed_args.max_violations or file_config.max_violations
        public_submodules = _parse_list(parsed_args.public_submodules) or file_config.public_submodules
    else:
        json_format = parsed_args.json
        quiet = parsed_args.quiet
        no_color = parsed_args.no_color
        verbose = parsed_args.verbose
        exclude_patterns = _parse_exclude_patterns(parsed_args.exclude)
        max_violations = parsed_args.max_violations
        public_submodules = _parse_list(parsed_args.public_submodules)

    if not lib_paths:
        parser.print_help()
        return 1

    # Validate all libraries
    violations, stats = validate_libraries(lib_paths, exclude_patterns, public_submodules, verbose)

    # Filter out warnings from exit code determination
    error_violations = [v for v in violations if not v.is_warning]

    # Check max violations threshold (only count errors)
    if max_violations and len(error_violations) > max_violations:
        if not quiet:
            print(
                f"Error: Found {len(error_violations)} violations, exceeds max of {max_violations}",
                file=sys.stderr,
            )
        return 1

    # Report results
    use_colors = not no_color
    if violations:
        report_violations(violations, format="json" if json_format else "text", use_colors=use_colors)

        if verbose:
            report_summary(
                total_files=stats["total_imports"],
                total_exports=stats["total_exports"],
                violations_count=len(violations),
                execution_time=stats["total_execution_time"],
                format="json" if json_format else "text",
                use_colors=use_colors,
            )

        # Return 1 only if there are actual errors (not just warnings)
        return 1 if error_violations else 0

    if not quiet:
        report_success(
            format="json" if json_format else "text",
            use_colors=use_colors,
        )

        if verbose:
            report_summary(
                total_files=stats["total_imports"],
                total_exports=stats["total_exports"],
                violations_count=0,
                execution_time=stats["total_execution_time"],
                format="json" if json_format else "text",
                use_colors=use_colors,
            )

    return 0


def _parse_exclude_patterns(cli_exclude: list | None, config_exclude: list | None = None) -> list:
    """Parse exclude patterns from CLI and config.

    Args:
        cli_exclude: List of exclude patterns from CLI (may contain comma-separated values)
        config_exclude: List of exclude patterns from config file

    Returns:
        Combined list of exclude patterns
    """
    patterns = []

    # Add patterns from config
    if config_exclude:
        patterns.extend(config_exclude)

    # Add patterns from CLI (splitting on commas)
    if cli_exclude:
        for pattern_arg in cli_exclude:
            patterns.extend([p.strip() for p in pattern_arg.split(",")])

    return patterns


def _parse_list(arg: str | None) -> list[str]:
    """Parse comma-separated list from CLI arg."""
    if not arg:
        return []
    return [s.strip() for s in arg.split(",") if s.strip()]


if __name__ == "__main__":
    sys.exit(main())
