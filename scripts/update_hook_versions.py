#!/usr/bin/env python3
"""
Automated pre-commit hook version updater for template files.

This script:
1. Creates a temporary directory
2. Extracts current hook revisions from template files
3. Generates a complete .pre-commit-config.yaml from templates
4. Runs pre-commit autoupdate to get latest versions
5. Updates the template files with new versions
6. Reports all changes made
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}")
    print("Install with: uv pip install pyyaml jinja2")
    sys.exit(1)


class TemplateUpdater:
    """Handles updating pre-commit hook versions in template files."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.template_dir = self.repo_root / "pre_commit_starter" / "hook_templates"
        self.temp_dir: Optional[Path] = None
        self.original_revisions: Dict[str, str] = {}
        self.updated_hooks: List[Dict[str, str]] = []

        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

    def setup_temp_directory(self) -> Path:
        """Create a temporary directory for the update process."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pre-commit-update-"))
        print(f"Created temporary directory: {self.temp_dir}")

        # Initialize git repo (required by pre-commit)
        try:
            subprocess.run(["git", "init"], cwd=str(self.temp_dir), capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=str(self.temp_dir),
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], cwd=str(self.temp_dir), capture_output=True, check=True
            )
            print("Initialized git repository in temp directory")
        except subprocess.CalledProcessError as e:
            print(f"WARNING: Failed to initialize git repo: {e}")

        return self.temp_dir

    def cleanup_temp_directory(self):
        """Remove the temporary directory."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)  # type: ignore[deprecated]
            print(f"Cleaned up temporary directory: {self.temp_dir}")

    def extract_original_revisions(self) -> Dict[str, str]:
        """Extract current hook revisions from all template files."""
        print("\n=== Extracting original revisions from templates ===")
        revisions = {}

        for template_file in self.template_dir.glob("*.j2"):
            if template_file.name == "meta.j2":
                continue

            print(f"Reading {template_file.name}")
            content = template_file.read_text()

            # Match repo URLs and their revisions
            # Handles various revision formats: v1.2.3, 1.2.3, v1.2.3-alpha, etc.
            pattern = r"- repo: (https://github\.com/[^\n]+)\n\s+rev: ([^\s\n]+)"
            matches = re.findall(pattern, content)

            for repo_url, rev in matches:
                revisions[repo_url] = rev
                print(f"  Found: {repo_url} @ {rev}")

        self.original_revisions = revisions
        print(f"\nTotal hooks found: {len(revisions)}")
        return revisions

    def generate_full_config(self) -> Path:
        """Generate a complete .pre-commit-config.yaml from all templates."""
        print("\n=== Generating complete pre-commit config ===")

        assert self.temp_dir is not None, "Temp directory must be set up first"
        output_file = self.temp_dir / ".pre-commit-config.yaml"
        env = Environment(loader=FileSystemLoader(str(self.template_dir)))

        # Context with all features enabled to include all hooks
        context = {
            "yaml": True,
            "json": True,
            "toml": True,
            "xml": True,
            "case_conflict": True,
            "executables": True,
            "symlinks": True,
            "python": True,
            "dockerfile_linting": True,
            "dockerignore_check": True,
            "workflow_validation": True,
            "security_scanning": True,
            "go_critic": True,
            "typescript": True,
            "jsx": True,
            "prettier_config": ".prettierrc",
            "eslint_config": ".eslintrc.js",
            "pyrefly_args": ["--config=pyproject.toml"],
            "uv_lock": True,
            "python_version": "'3.10'",
        }

        # Render all template files (except meta.j2)
        all_content = []
        template_files = sorted(
            [f for f in self.template_dir.glob("*.j2") if f.name != "meta.j2"], key=lambda x: x.name
        )

        for template_file in template_files:
            template = env.get_template(template_file.name)
            content = template.render(context)
            all_content.append(content)  # type: ignore[arg-type]
            print(f"Rendered {template_file.name}")

        # Combine all content
        combined_content = "\n".join(all_content)

        # Render meta template with combined content
        meta_template = env.get_template("meta.j2")
        final_config = meta_template.render({**context, "content": combined_content})

        # Write the final config
        output_file.write_text(final_config)
        print(f"\nGenerated config at: {output_file}")

        # Verify it's valid YAML
        try:
            with open(output_file) as f:
                config = yaml.safe_load(f)
            if config and isinstance(config, dict):
                repos = config.get("repos", [])
                print(f"Config contains {len(repos)} repositories")
        except yaml.YAMLError as e:
            print(f"ERROR: Generated invalid YAML: {e}")
            raise

        return output_file

    def run_autoupdate(self) -> tuple[bool, str]:
        """Run pre-commit autoupdate and return success status and stdout."""
        print("\n=== Running pre-commit autoupdate ===")

        # Check if pre-commit is installed
        try:
            result = subprocess.run(["pre-commit", "--version"], capture_output=True, text=True, check=True)
            print(f"Using {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: pre-commit is not installed or not in PATH")
            print("Install with: pip install pre-commit")
            return False, ""

        # Configure environment to prevent credential prompts
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"  # Disable git credential prompts
        env["GIT_ASKPASS"] = "echo"  # Provide dummy askpass

        # Try to update each repo individually for better error handling
        all_updates = []

        assert self.temp_dir is not None, "Temp directory must be set up first"

        try:
            with open(self.temp_dir / ".pre-commit-config.yaml") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"ERROR: Failed to read config: {e}")
            return False, ""

        if config is None or not isinstance(config, dict):
            print("ERROR: Invalid config file")
            return False, ""

        repos = config.get("repos", [])
        print(f"Checking {len(repos)} repositories for updates...\n")

        for repo in repos:
            repo_url = repo.get("repo")
            if not repo_url:
                continue

            repo_name = repo_url.split("/")[-1]
            print(f"Updating {repo_name}...", end=" ", flush=True)

            try:
                result = subprocess.run(
                    ["pre-commit", "autoupdate", "--repo", repo_url],
                    cwd=str(self.temp_dir),
                    capture_output=True,
                    text=True,
                    timeout=60,  # 1 minute per repo
                    env=env,  # Use environment without credential prompts
                )

                if result.returncode == 0:
                    # Parse the output for this specific repo
                    if "updating" in result.stdout:
                        print("✓ Updated")
                        all_updates.append(result.stdout)  # type: ignore[arg-type]
                    else:
                        print("✓ Already up to date")
                else:
                    print("✗ Failed (skipping)")

            except subprocess.TimeoutExpired:
                print("✗ Timeout (skipping)")
            except Exception as e:
                print(f"✗ Error: {e}")

        # Combine all updates
        combined_output = "\n".join(all_updates)

        if not combined_output:
            print("\nNo updates found.")
            return True, ""

        print(f"\n{combined_output}")
        return True, combined_output

    def parse_autoupdate_output(self, autoupdate_stdout: str) -> List[Dict[str, str]]:
        """Parse pre-commit autoupdate stdout to extract version changes."""
        print("\n=== Parsing version updates ===")

        updated_hooks = []

        # Parse lines like: [https://github.com/pre-commit/pre-commit-hooks] updating v5.0.0 -> v6.0.0
        pattern = r"\[(https://github\.com/[^\]]+)\] updating ([^\s]+) -> ([^\s]+)"

        for line in autoupdate_stdout.splitlines():
            match = re.search(pattern, line)
            if match:
                repo_url = match.group(1)
                old_rev = match.group(2)
                new_rev = match.group(3)

                updated_hooks.append({"repo": repo_url, "old_rev": old_rev, "new_rev": new_rev})
                print(f"  {repo_url}")
                print(f"    {old_rev} → {new_rev}")

        self.updated_hooks = updated_hooks

        if not updated_hooks:
            print("No version updates found. All hooks are already up to date!")
        else:
            print(f"\nFound {len(updated_hooks)} hooks with updates")

        return updated_hooks

    def apply_updates_to_templates(self) -> Dict[str, int]:
        """Apply version updates back to the template files."""
        print("\n=== Applying updates to template files ===")

        if not self.updated_hooks:
            print("No updates to apply")
            return {}

        updates_per_file = {}

        for template_file in self.template_dir.glob("*.j2"):
            if template_file.name == "meta.j2":
                continue

            content = template_file.read_text()
            updates_made = 0

            for hook in self.updated_hooks:
                if hook["repo"] in content:
                    # Replace the old revision with the new one
                    old_pattern = f"rev: {hook['old_rev']}"
                    new_pattern = f"rev: {hook['new_rev']}"

                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        updates_made += 1
                        print(f"  Updated {template_file.name}: {hook['old_rev']} → {hook['new_rev']}")

            if updates_made > 0:
                template_file.write_text(content)
                updates_per_file[template_file.name] = updates_made

        return updates_per_file

    def generate_report(self, updates_per_file: Dict[str, int]):
        """Generate a summary report of all changes."""
        print("\n" + "=" * 70)
        print("UPDATE SUMMARY")
        print("=" * 70)

        if not self.updated_hooks:
            print("\nNo updates were made. All hook versions are current.")
            return

        print(f"\nTotal hooks updated: {len(self.updated_hooks)}")
        print(f"Template files modified: {len(updates_per_file)}")

        print("\n--- Version Changes ---")
        for hook in self.updated_hooks:
            repo_name = hook["repo"].split("/")[-1]
            print(f"\n  {repo_name}")
            print(f"    Repo: {hook['repo']}")
            print(f"    {hook['old_rev']} → {hook['new_rev']}")

        print("\n--- Files Modified ---")
        for filename, count in sorted(updates_per_file.items()):
            print(f"  {filename}: {count} hook(s) updated")

        print("\n" + "=" * 70)

    def run(self) -> bool:  # type: ignore[return]
        """Execute the complete update process."""
        try:
            # Setup
            self.setup_temp_directory()

            # Step 1: Extract original revisions
            self.extract_original_revisions()

            # Step 2: Generate complete config
            self.generate_full_config()

            # Step 3: Run autoupdate
            success, autoupdate_stdout = self.run_autoupdate()
            if not success:
                return False

            # Step 4: Parse autoupdate output to extract version changes
            self.parse_autoupdate_output(autoupdate_stdout)

            # Step 5: Apply updates to templates
            updates_per_file = self.apply_updates_to_templates()

            # Step 6: Generate report
            self.generate_report(updates_per_file)

            return True

        except Exception as e:
            print(f"\nERROR: Update process failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        finally:
            # Always cleanup
            self.cleanup_temp_directory()


def main():
    """Main entry point."""
    print("Pre-commit Hook Version Updater")
    print("=" * 70)

    # Allow specifying repo root as argument
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    try:
        updater = TemplateUpdater(repo_root)
        success = updater.run()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nUpdate cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
