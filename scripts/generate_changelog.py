#!/usr/bin/env python3
"""Generate changelog from git commits."""

import re
import subprocess
from datetime import datetime
from pathlib import Path


def get_latest_tag():
    """Get the latest git tag."""
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"], universal_newlines=True
        ).strip()
    except subprocess.CalledProcessError:
        return None


def get_commits_since_tag(tag=None):
    """Get all commits since the specified tag."""
    cmd = ["git", "log", "--pretty=format:%s|%h|%an|%ad", "--date=short"]
    if tag:
        cmd.append(f"{tag}..HEAD")

    output = subprocess.check_output(cmd, universal_newlines=True)
    return output.strip().split("\n")


def parse_commit(commit_line):
    """Parse a commit line into its components."""
    try:
        message, hash_id, author, date = commit_line.split("|")

        # Parse conventional commit format
        match = re.match(r"^(\w+)(?:\(([^)]+)\))?: (.+)$", message)
        if match:
            type_, scope, desc = match.groups()
            return {
                "type": type_,
                "scope": scope,
                "description": desc,
                "hash": hash_id,
                "author": author,
                "date": date,
            }
        return {
            "type": "other",
            "scope": None,
            "description": message,
            "hash": hash_id,
            "author": author,
            "date": date,
        }
    except ValueError:
        return None


def group_commits(commits):
    """Group commits by type."""
    groups = {
        "feat": [],
        "fix": [],
        "docs": [],
        "style": [],
        "refactor": [],
        "perf": [],
        "test": [],
        "build": [],
        "ci": [],
        "chore": [],
        "other": [],
    }

    for commit in commits:
        if commit:
            groups.setdefault(commit["type"], []).append(commit)

    return groups


def generate_changelog(tag=None):
    """Generate changelog content."""
    commits = get_commits_since_tag(tag)
    parsed_commits = [parse_commit(c) for c in commits if c]
    grouped_commits = group_commits(parsed_commits)

    # Generate markdown
    today = datetime.now().strftime("%Y-%m-%d")
    content = [f"# Changelog\n\n## [Unreleased] - {today}\n"]

    type_titles = {
        "feat": "### Features",
        "fix": "### Bug Fixes",
        "docs": "### Documentation",
        "style": "### Style",
        "refactor": "### Refactoring",
        "perf": "### Performance",
        "test": "### Testing",
        "build": "### Build",
        "ci": "### CI",
        "chore": "### Maintenance",
        "other": "### Other",
    }

    for type_, title in type_titles.items():
        commits = grouped_commits.get(type_, [])
        if commits:
            content.append(f"\n{title}\n")
            for commit in commits:
                scope = f"({commit['scope']})" if commit["scope"] else ""
                content.append(f"- {commit['description']} {scope} ({commit['hash']})")

    return "\n".join(content)


def main():
    """Main function."""
    changelog_path = Path("CHANGELOG.md")
    tag = get_latest_tag()

    content = generate_changelog(tag)

    # Update CHANGELOG.md
    if changelog_path.exists():
        old_content = changelog_path.read_text()
        # Remove the old unreleased section if it exists
        old_content = re.sub(r"## \[Unreleased\].*?\n(?=## |$)", "", old_content, flags=re.DOTALL)
        content = f"{content}\n\n{old_content.strip()}"

    changelog_path.write_text(content)
    print(f"Updated {changelog_path}")


if __name__ == "__main__":
    main()
