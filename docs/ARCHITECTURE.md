# Technical Architecture

This document outlines the technical architecture of Pre-commit Starter, explaining the system design, component interactions, and implementation details.

## System Overview

Pre-commit Starter is a Python-based CLI tool that automates the generation of pre-commit hook configurations. The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   File Scanner  │────▶│  Hook Registry  │────▶│  YAML Builder   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                        ▲
        │                       │                        │
        └───────────────────────┴────────────────────────┘
                               ▲
                        ┌──────┴───────┐
                        │     CLI      │
                        └──────────────┘
```

## Component Details

### 1. File Scanner (`src/detector/file_scanner.py`)

#### Purpose
- Analyzes repository content
- Detects technologies and frameworks
- Counts file types

#### Implementation
```python
class FileScanner:
    def scan_repository(self, path: str) -> dict[str, int]:
        """
        Scan repository and return detected technologies.

        Args:
            path: Repository path

        Returns:
            Dict mapping technology names to file counts
        """
        # Implementation details
```

#### Key Features
- Recursive directory traversal
- File extension mapping
- Content-based detection
- Technology classification
- Support for various programming languages (Python, JavaScript, TypeScript, Go, Rust, etc.)

#### Technology Detection Patterns
The scanner uses both file extensions and content patterns to identify technologies:

- **Python**: `.py`, `.pyi`, `.pyx` files and patterns like `import` statements
- **JavaScript**: `.js`, `.jsx` files and patterns like `const`, `let` declarations
- **TypeScript**: `.ts`, `.tsx` files and patterns like `interface`, `type` declarations
- **Go**: `.go` files, `go.mod`, `go.sum` and patterns like `package`, `import`, `func` declarations
- **Rust**: `.rs` files, `Cargo.toml`, `Cargo.lock` and patterns like `fn`, `struct`, `impl`, `mod` declarations
- **Other technologies**: HTML, CSS, YAML, Docker, etc.

### 2. Hook Registry (`src/hooks/hook_registry.py`)

#### Purpose
- Maintains hook definitions
- Maps technologies to hooks
- Manages dependencies

#### Implementation
```python
class HookRegistry:
    def get_hooks_for_tech(self, tech: str) -> list[dict]:
        """
        Get appropriate hooks for a technology.

        Args:
            tech: Technology name

        Returns:
            List of hook configurations
        """
        # Implementation details
```

#### Key Features
- Hook priority system
- Version management
- Dependency resolution
- Configuration validation

### 3. YAML Builder (`src/generator/yaml_builder.py`)

#### Purpose
- Generates pre-commit configurations
- Merges hook definitions
- Ensures compatibility

#### Implementation
```python
class YAMLBuilder:
    def build_config(self) -> str:
        """
        Generate pre-commit configuration.

        Returns:
            YAML configuration string
        """
        # Implementation details
```

#### Key Features
- Smart hook merging
- Priority-based ordering
- Dependency deduplication
- Version compatibility

### 4. CLI Interface (`src/main.py`)

#### Purpose
- User interaction
- Command processing
- Output formatting

#### Implementation
```python
@click.command()
@click.option('--path', default='.')
@click.option('--force', is_flag=True)
def main(path: str, force: bool):
    """Main CLI entry point."""
    # Implementation details
```

#### Key Features
- Rich text output
- Progress indication
- Error handling
- Configuration backup

## Data Flow

1. **Repository Analysis**
   ```mermaid
   graph LR
       A[CLI] --> B[File Scanner]
       B --> C[Technology Detection]
       C --> D[File Counting]
       D --> E[Results]
   ```

2. **Hook Selection**
   ```mermaid
   graph LR
       A[Technologies] --> B[Hook Registry]
       B --> C[Hook Selection]
       C --> D[Dependency Resolution]
       D --> E[Configuration]
   ```

3. **Configuration Generation**
   ```mermaid
   graph LR
       A[Hook Configs] --> B[YAML Builder]
       B --> C[Merge Hooks]
       C --> D[Order Hooks]
       D --> E[Generate YAML]
   ```

## Hook Categories

The system organizes hooks into priority-based categories:

1. Security (Priority 1)
2. Basic Checks (Priority 2)
3. Language-Specific (Priority 3-4)
4. Framework-Specific (Priority 11)
5. Performance (Priority 12)
6. Accessibility (Priority 13)
7. Testing (Priority 14)
8. Dependencies (Priority 15)

## Configuration Management

### Hook Merging Strategy

1. **Repository Level**
   ```python
   def merge_repos(self, existing: dict, new: dict) -> dict:
       """Merge repository configurations."""
       # Check for existing repo
       # Merge hooks
       # Update versions
   ```

2. **Hook Level**
   ```python
   def merge_hooks(self, existing: dict, new: dict) -> dict:
       """Merge hook configurations."""
       # Check hook compatibility
       # Merge arguments
       # Resolve dependencies
   ```

### Version Management

1. **Version Selection**
   - Use latest stable versions
   - Check compatibility matrix
   - Handle peer dependencies

2. **Update Strategy**
   - Keep existing versions if working
   - Update only if necessary
   - Maintain compatibility

## Performance Considerations

1. **Scanning Optimization**
   - Skip unnecessary directories
   - Use efficient file operations
   - Cache technology detection

2. **Hook Execution**
   - Order hooks for efficiency
   - Minimize redundant checks
   - Enable parallel execution

## Error Handling

1. **Graceful Degradation**
   - Continue on non-critical errors
   - Provide helpful error messages
   - Maintain existing configuration

2. **Recovery Strategies**
   - Backup existing config
   - Rollback on failure
   - Log error details

## Future Enhancements

1. **Technical Improvements**
   - Async file scanning
   - Plugin system
   - Configuration profiles

2. **Feature Additions**
   - Custom hook definitions
   - CI/CD integration
   - Performance metrics

3. **User Experience**
   - Interactive configuration
   - Visual hook editor
   - Configuration validation

## Security Considerations

1. **Code Safety**
   - Validate hook sources
   - Check script contents
   - Verify dependencies

2. **Configuration Safety**
   - Validate YAML syntax
   - Check hook permissions
   - Secure sensitive data

## Testing Strategy

1. **Unit Tests**
   - Component isolation
   - Mock external systems
   - Edge case coverage

2. **Integration Tests**
   - Component interaction
   - Configuration generation
   - Hook execution

3. **Fixtures**
   - Sample repositories
   - Expected configurations
   - Test scenarios
