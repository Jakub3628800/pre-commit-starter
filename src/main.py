#!/usr/bin/env python3
"""
Pre-commit Starter
A smart CLI tool that automatically generates pre-commit configurations based on repository content.
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import rich
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .file_scanner import FileScanner
from .hook_registry import HookRegistry
from .yaml_builder import YAMLBuilder

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = ".pre-commit-config.yaml"
CUSTOM_HOOKS_FILE = ".pre-commit-starter-hooks.yaml"
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
        confidence_str = f"{info.confidence*100:.1f}%"
        confidence_style = (
            "bright_green"
            if info.confidence > 0.8
            else "green"
            if info.confidence > 0.6
            else "yellow"
            if info.confidence > 0.4
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
    for tech, info in detected_techs.items():
        confidence_text = f"confidence: {info.confidence*100:.1f}%"
        confidence_style = (
            "bright_green"
            if info.confidence > 0.8
            else "green"
            if info.confidence > 0.6
            else "yellow"
            if info.confidence > 0.4
            else "red"
        )

        # Display hooks available for this technology
        display_hooks_for_tech(tech, hook_registry)

        # Default to include techs with confidence > 0.6
        default = info.confidence > 0.6 if "confidence" in info else True

        ask_text = (
            f"Include [cyan]{tech.capitalize()}[/cyan] "
            f"([{confidence_style}]{confidence_text}[/{confidence_style}])?"
        )
        if Confirm.ask(ask_text, default=default):
            selected_techs.append(tech)
            console.print(f"[green]✓ Added hooks for {tech.capitalize()}[/green]")
        else:
            console.print(f"[yellow]Skipped hooks for {tech.capitalize()}[/yellow]")

    if not selected_techs:
        if Confirm.ask(
            "No technologies selected. Include basic hooks only?", default=True
        ):
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


def run_generation(args: argparse.Namespace):
    """Main logic for scanning and generating the config."""
    try:
        repo_path = Path(args.path).resolve()
        if not repo_path.is_dir():
            console.print(f"[red]Error: {args.path} is not a valid directory[/red]")
            return

        console.print(Panel.fit("🔍 Scanning repository...", style="blue"))

        # Initialize components
        scanner = FileScanner()
        detected_techs = scanner.scan_repository(str(repo_path))

        if not detected_techs:
            console.print(
                "[yellow]No supported file types detected in the repository.[/yellow]"
            )
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
        selected_techs = (
            list(detected_techs.keys())
            if args.auto
            else select_technologies(detected_techs, hook_registry)
        )

        if not selected_techs:
            return  # User opted not to generate a config

        # Read custom hooks if file exists
        custom_hooks_data = None
        custom_hooks_path = repo_path / CUSTOM_HOOKS_FILE
        if custom_hooks_path.exists():
            console.print(f"ℹ️ Found custom hooks file: {custom_hooks_path.name}")
            try:
                with open(custom_hooks_path, "r", encoding="utf-8") as f:
                    custom_hooks_data = yaml.safe_load(f)
                if (
                    not isinstance(custom_hooks_data, dict)
                    or "repos" not in custom_hooks_data
                ):
                    warning_msg = (
                        f"[yellow]Warning: Custom hooks file '{custom_hooks_path.name}' "
                        f"does not have the expected format "
                        f"(dictionary with a 'repos' key). Ignoring.[/yellow]"
                    )
                    console.print(warning_msg)
                    custom_hooks_data = None
                elif not isinstance(custom_hooks_data.get("repos"), list):
                    warning_msg = (
                        f"[yellow]Warning: 'repos' key in "
                        f"custom hooks file '{custom_hooks_path.name}' "
                        f"is not a list. Ignoring.[/yellow]"
                    )
                    console.print(warning_msg)
                    custom_hooks_data = None

            except yaml.YAMLError as e:
                console.print(
                    f"[red]Error parsing custom hooks file {custom_hooks_path.name}: {e}[/red]"
                )
                custom_hooks_data = None  # Don't proceed with bad custom hooks
            except Exception as e:
                console.print(
                    f"[red]Error reading custom hooks file {custom_hooks_path.name}: {e}[/red]"
                )
                custom_hooks_data = None

        # Generate configuration
        # Pass custom hooks data to YAMLBuilder
        yaml_builder = YAMLBuilder(hook_registry, custom_hooks_data=custom_hooks_data)
        config = yaml_builder.build_config(selected_techs)

        # Check if config is None (might happen if custom hooks failed validation)
        if not config:
            console.print(
                "[yellow]Unable to generate configuration due to issues with custom hooks.[/yellow]"
            )
            return

        # Display the config in dry-run mode
        if args.dry_run:
            display_configuration(config)
            console.print(
                "\n[yellow]Dry run mode: Configuration not written to disk.[/yellow]"
            )
            return

        # Write configuration
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config)

        console.print("[green]✓ Successfully generated .pre-commit-config.yaml[/green]")
        display_next_steps()

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


def main():
    """Parses arguments and runs the generation."""
    parser = argparse.ArgumentParser(
        description="Generate pre-commit config based on repository content."
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to the repository (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .pre-commit-config.yaml",
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
    run_generation(args)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
