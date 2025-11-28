"""CLI for generating GitHub Actions workflows."""

import argparse
import sys
from pathlib import Path

from .generator import generate_workflow


def main() -> int:
    """Main entry point for generate-workflow CLI."""
    parser = argparse.ArgumentParser(
        description="Generate GitHub Actions workflow for pre-commit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  generate-workflow
  generate-workflow --branch master
  generate-workflow --output .github/workflows/my-workflow.yml
  generate-workflow --config /path/to/.pre-commit-config.yaml
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(".github/workflows/pre-commit.yml"),
        help="Output path for workflow file (default: .github/workflows/pre-commit.yml)",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Path to .pre-commit-config.yaml (default: .pre-commit-config.yaml)",
    )

    parser.add_argument(
        "-b",
        "--branch",
        type=str,
        default="main",
        help="Main branch name (default: main)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print workflow to stdout instead of writing file",
    )

    args = parser.parse_args()

    try:
        if args.dry_run:
            # Print to stdout
            workflow = generate_workflow(
                output_path=None,
                config_path=args.config,
                main_branch=args.branch,
            )
            print(workflow)
        else:
            # Write to file
            generate_workflow(
                output_path=args.output,
                config_path=args.config,
                main_branch=args.branch,
            )
            print(f"✓ Generated workflow: {args.output}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error generating workflow: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
