#!/usr/bin/env python3
"""
prec-hook-autodetect
A smart CLI tool that automatically generates pre-commit configurations based on repository content.
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .detector.file_scanner import FileScanner
from .generator.hooks.hook_registry import HookRegistry
from .generator.yaml_builder import YAMLBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Simplified format without level
    stream=sys.stdout,  # Output to stdout instead of stderr
)
logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = ".pre-commit-config.yaml"
CUSTOM_HOOKS_FILE = ".pre-commit-starter-hooks.yaml"
# Confidence thresholds
HIGH_CONFIDENCE = 0.8
MEDIUM_CONFIDENCE = 0.6
LOW_CONFIDENCE = 0.4
INTERACTIVE_HELP = """
# Available Commands

- `y`: Include this technology
- `n`: Skip this technology
- `d`: Display available hooks for this technology
- `a`: Include all remaining technologies
- `s`: Skip all remaining technologies
- `q`: Quit without generating config
"""

console = Console()


def display_summary(detected_techs: dict):
    """Display a summary of detected technologies and proposed hooks."""
    table = Table(title="Detected Technologies")
    table.add_column("Technology", style="cyan")
    table.add_column("Files Found", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Confidence", style="magenta")

    for tech, info in detected_techs.items():
        version_str = info.version if info.version else "Unknown"
        confidence_str = f"{info.confidence * 100:.1f}%"
        confidence_style = (
            "bright_green"
            if info.confidence > HIGH_CONFIDENCE
            else "green"
            if info.confidence > MEDIUM_CONFIDENCE
            else "yellow"
            if info.confidence > LOW_CONFIDENCE
            else "red"
        )

        table.add_row(
            tech.capitalize(),
            str(info.count),
            version_str,
            Text(confidence_str, style=confidence_style),
        )

    console.print(table)


def display_hooks_for_tech(tech: str, hook_registry: HookRegistry):
    """Display hooks available for a technology."""
    hook_ids = hook_registry.get_hook_ids_for_tech(tech)

    if not hook_ids:
        console.print(f"[yellow]No specific hooks available for {tech}[/yellow]")
        return

    console.print(f"\n[bold]Hooks for {tech.capitalize()}:[/bold]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Hook", style="cyan")
    table.add_column("Description", style="green")

    for hook_id in hook_ids:
        description = hook_registry.get_hook_description(hook_id)
        table.add_row(hook_id, description)

    console.print(table)


def select_technologies(detected_techs: dict, hook_registry: HookRegistry) -> list:
    """Interactive mode: Allow user to select which technologies to include hooks for."""
    if not detected_techs:
        return []

    console.print("\n[bold]Select technologies to include hooks for:[/bold]")
    console.print("(Technologies with higher confidence are recommended)")

    selected_techs = []
    for tech_name, tech_info in detected_techs.items():
        confidence_text = f"confidence: {tech_info.confidence * 100:.1f}%"
        confidence_style = (
            "bright_green"
            if tech_info.confidence > HIGH_CONFIDENCE
            else "green"
            if tech_info.confidence > MEDIUM_CONFIDENCE
            else "yellow"
            if tech_info.confidence > LOW_CONFIDENCE
            else "red"
        )

        # Display hooks available for this technology
        display_hooks_for_tech(tech_name, hook_registry)

        # Default to include techs with confidence > 0.6
        default = tech_info.confidence > MEDIUM_CONFIDENCE

        ask_text = (
            f"Include [cyan]{tech_name.capitalize()}[/cyan] "
            f"([{confidence_style}]{confidence_text}[/{confidence_style}])?"
        )
        if Confirm.ask(ask_text, default=default):
            selected_techs.append(tech_info)
            console.print(f"[green]✓ Added hooks for {tech_name.capitalize()}[/green]")
        else:
            console.print(f"[yellow]Skipped hooks for {tech_name.capitalize()}[/yellow]")

    if not selected_techs:
        if Confirm.ask("No technologies selected. Include basic hooks only?", default=True):
            console.print("[yellow]Including only basic hooks.[/yellow]")
        else:
            msg = "[yellow]No technologies selected. Configuration will not be generated.[/yellow]"
            console.print(msg)
            return []

    return selected_techs


def display_configuration(config: str):
    """Display the generated configuration."""
    console.print("\n[bold]Generated Configuration:[/bold]")
    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)


def display_next_steps():
    """Display next steps for the user."""
    console.print("\n[bold]Next steps:[/bold]")
    steps = """
1. Install pre-commit:
   ```
   pip install pre-commit
   ```

2. Install the hooks:
   ```
   pre-commit install
   ```

3. Run the hooks on all files:
   ```
   pre-commit run --all-files
   ```
    """
    console.print(Markdown(steps))


def validate_custom_hooks(custom_hooks_data: dict) -> bool:
    """Validate custom hooks data."""
    if not isinstance(custom_hooks_data, dict):
        console.print("Error: Custom hooks file must contain a valid YAML dictionary")
        return False

    if "repos" not in custom_hooks_data:
        console.print("Error: Custom hooks file must contain a 'repos' key")
        return False

    for repo in custom_hooks_data["repos"]:
        if not isinstance(repo, dict):
            console.print("Error: Each repository must be a dictionary")
            return False

        if "repo" not in repo:
            console.print("Error: Each repository must have a 'repo' key")
            return False

        # Skip 'rev' check for local hooks
        if repo["repo"] != "local" and "rev" not in repo:
            console.print("Error: Each non-local repository must have a 'rev' key")
            return False

    return True


def load_custom_hooks(repo_path: Path) -> dict | None:
    """Loads custom hooks from the specified file in the repository root."""
    custom_hooks_path = repo_path / CUSTOM_HOOKS_FILE
    result = None

    if custom_hooks_path.is_file():
        try:
            with open(custom_hooks_path, encoding="utf-8") as f:
                custom_data = yaml.safe_load(f)

            if (
                custom_data
                and isinstance(custom_data, dict)
                and isinstance(custom_data.get("repos"), list)
                and validate_custom_hooks(custom_data)
            ):
                logger.info("Loaded custom hooks from %s", CUSTOM_HOOKS_FILE)
                result = custom_data
            else:
                logger.warning(
                    "Custom hooks file %s is invalid or empty. Skipping.", CUSTOM_HOOKS_FILE
                )
        except ImportError:
            logger.warning(
                "PyYAML is not installed. Cannot load custom hooks from %s. Skipping.",
                CUSTOM_HOOKS_FILE,
            )
        except yaml.YAMLError as e:
            logger.warning(
                "Error parsing custom hooks file %s: %s. Skipping.", CUSTOM_HOOKS_FILE, e
            )
        except OSError as e:
            logger.warning(
                "Error reading custom hooks file %s: %s. Skipping.", CUSTOM_HOOKS_FILE, e
            )

    return result


def run_generation(args: argparse.Namespace):
    """Main logic for scanning and generating the config."""
    try:
        repo_path = Path(args.path).resolve()
        if not repo_path.is_dir():
            console.print(f"[red]Error: {args.path} is not a valid directory[/red]")
            sys.exit(1)

        # Check if it's a git repository
        git_dir = repo_path / ".git"
        if not git_dir.is_dir():
            print("not a valid Git repository", file=sys.stderr)
            sys.exit(1)

        console.print(Panel.fit("🔍 Scanning repository...", style="blue"))

        # Initialize components
        scanner = FileScanner()
        detected_techs = scanner.scan_repository(str(repo_path))

        if not detected_techs:
            console.print("[yellow]No supported file types detected in the repository.[/yellow]")
            return

        # Display findings
        display_summary(detected_techs)

        # Check for existing config
        config_path = repo_path / CONFIG_FILE
        if config_path.exists() and not args.force and not args.dry_run:
            message = (
                "[yellow]'.pre-commit-config.yaml' already exists. "
                "Use --force to overwrite.[/yellow]"
            )
            console.print(message)
            return

        # Initialize hook registry
        hook_registry = HookRegistry()

        # Technology selection based on mode
        if args.auto or args.force:
            # In force mode, only include technologies with high confidence
            if args.force:
                selected_techs = [
                    tech_info
                    for tech_info in detected_techs.values()
                    if tech_info.confidence > HIGH_CONFIDENCE
                ]
                selected_names = [tech.name for tech in selected_techs]
                console.print(
                    f"[blue]Selected technologies (high confidence): {selected_names}[/blue]"
                )
                if not selected_techs:
                    console.print(
                        "[yellow]No technologies detected with high confidence (>80%).[/yellow]"
                    )
                    console.print("[yellow]Including only basic hooks.[/yellow]")
            else:
                # In auto mode, include all detected technologies
                selected_techs = list(detected_techs.values())
                selected_names = [tech.name for tech in selected_techs]
                console.print(f"[blue]Selected technologies (auto mode): {selected_names}[/blue]")
        else:
            # Interactive mode
            selected_techs = select_technologies(detected_techs, hook_registry)
            selected_names = [tech.name for tech in selected_techs]
            console.print(
                f"[blue]Selected technologies (interactive mode): {selected_names}[/blue]"
            )

        # Load custom hooks
        custom_hooks = None
        custom_hooks_path = repo_path / CUSTOM_HOOKS_FILE
        if custom_hooks_path.exists():
            try:
                with open(custom_hooks_path, encoding="utf-8") as f:
                    custom_hooks_data = yaml.safe_load(f)
                    if not custom_hooks_data:
                        console.print(f"Custom hooks file {CUSTOM_HOOKS_FILE} is invalid or empty")
                    elif "repos" not in custom_hooks_data:
                        console.print("Error parsing custom hooks file: missing 'repos' key")
                    else:
                        custom_hooks = custom_hooks_data["repos"]
                        if validate_custom_hooks(custom_hooks_data):
                            console.print(f"Loaded custom hooks from {CUSTOM_HOOKS_FILE}")
                        else:
                            console.print(
                                f"Error: Custom hooks file {CUSTOM_HOOKS_FILE} is invalid"
                            )
                            custom_hooks = None
            except (yaml.YAMLError, OSError) as e:
                console.print(f"Error parsing custom hooks file: {e}")

        # Generate configuration
        yaml_builder = YAMLBuilder(hook_registry)
        config = yaml_builder.build_config(selected_techs, custom_hooks=custom_hooks)

        # Check if config is None (might happen if custom hooks failed validation)
        if not config:
            console.print(
                "[yellow]Unable to generate configuration due to issues with custom hooks.[/yellow]"
            )
            return

        # Display the config in dry-run mode
        if args.dry_run:
            display_configuration(config)
            console.print("\n[yellow]Dry run mode: Configuration not written to disk.[/yellow]")
            return

        # Write configuration
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config)

        console.print("[green]✓ Successfully generated .pre-commit-config.yaml[/green]")
        display_next_steps()

    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")


def main():
    """Main function for the pre-commit-starter CLI tool."""
    parser = argparse.ArgumentParser(
        description="Generate pre-commit configuration based on repository content."
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .pre-commit-config.yaml without prompting",
    )
    parser.add_argument(
        "--list-technologies",
        action="store_true",
        help="List supported technologies and exit",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically accept all suggested hooks (non-interactive mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )
    parser.add_argument("--verbose", action="store_true", help="Display verbose output")

    args = parser.parse_args()

    if args.list_technologies:
        print("Supported technologies:")
        for tech in sorted(HookRegistry().get_supported_technologies()):
            print(f"- {tech}")
        sys.exit(0)

    run_generation(args)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
