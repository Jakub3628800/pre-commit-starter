import json
import re
from pathlib import Path


class TechDetector:
    def detect_technologies(self) -> set[str]:
        """Detect technologies used in the repository."""
        detected = set()

        # Define technology detection order
        tech_patterns = [
            ("python", r"\.(py|pyi|pyx|ipynb)$"),
            ("javascript", r"\.js$"),
            ("typescript", r"\.ts$"),
            ("react", r"\.(jsx|tsx)$"),
            ("html", r"\.html?$"),
            ("css", r"\.css$"),
            ("json", r"\.json$"),
            ("markdown", r"\.(md|markdown)$"),
            ("yaml", r"\.(ya?ml)$"),
            ("shell", r"\.(sh|bash|zsh)$"),
            ("go", r"\.go$"),
            ("rust", r"\.(rs|toml)$"),
            ("terraform", r"\.(tf|tfvars)$"),
            ("docker", r"Dockerfile"),
        ]

        # Check for package files first
        package_files = {
            "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "javascript": ["package.json"],
            "typescript": ["tsconfig.json"],
            "react": ["package.json"],  # Check package.json for React dependencies
            "go": ["go.mod", "go.sum"],
            "rust": ["Cargo.toml"],
            "terraform": [".terraform.lock.hcl"],
            "docker": ["docker-compose.yml", "docker-compose.yaml"],
        }

        for tech, files in package_files.items():
            for file in files:
                if any(Path(self.repo_path).glob(f"**/{file}")):
                    detected.add(tech)
                    # Special handling for package.json to detect React
                    if file == "package.json":
                        try:
                            with open(Path(self.repo_path) / file) as f:
                                package_data = json.load(f)
                                deps = {
                                    **package_data.get("dependencies", {}),
                                    **package_data.get("devDependencies", {}),
                                }
                                if "react" in deps:
                                    detected.add("react")
                        except (json.JSONDecodeError, FileNotFoundError):
                            pass

        # Then check file extensions
        for tech, pattern in tech_patterns:
            if any(re.search(pattern, str(file)) for file in self.files):
                detected.add(tech)

        return detected
