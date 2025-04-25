from typing import Any


class ConfigGenerator:
    def _generate_base_hooks(self) -> list[dict[str, Any]]:
        """Generate base hooks that should be included in all configurations."""
        return [
            {
                "id": "trailing-whitespace",
                "name": "trailing-whitespace",
                "args": ["--markdown-linebreak-ext=md"],
            },
            {
                "id": "end-of-file-fixer",
                "name": "end-of-file-fixer",
            },
            {
                "id": "check-yaml",
                "name": "check-yaml",
            },
            {
                "id": "check-added-large-files",
                "name": "check-added-large-files",
            },
        ]
