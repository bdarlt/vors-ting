# Coding Standards for MCP Server Git

This document outlines the essential coding standards for the MCP Server Git project. Follow these standards to maintain consistency and readability.

## Core Standards (Required)

### PEP 8 Compliance
- Follow PEP 8 guidelines strictly
- Use 4 spaces for indentation
- Limit lines to 88 characters
- Use descriptive names following PEP 8 conventions

### Code Formatting
- **Formatter**: Ruff (automatic formatting)
- **Line Length**: 88 characters maximum
- **Quotes**: Double quotes preferred (`"`)
- **Trailing Commas**: Required in multi-line structures
- **Imports**: Organized automatically by Ruff

### Python Version
- **Target**: Python 3.12+
- Use modern Python features where appropriate
- Avoid deprecated features and patterns

### Type Annotations (Required)
All functions and methods must include type annotations:

```python
def git_status(repo: git.Repo) -> str:
    return repo.git.status()

def validate_repo_path(repo_path: Path, allowed_repository: Path | None) -> None:
    # implementation
```

**Type Annotation Rules:**
- Use `Optional[T]` or `T | None` for nullable parameters
- Prefer `list[str]`, `dict[str, int]` over `List[str]`, `Dict[str, int]`
- Use `|` union operator instead of `Union[T1, T2]`
- Use `Sequence[T]` for read-only sequences when appropriate

## Code Organization

### Import Conventions

**Import Order:**
1. Standard library imports
2. Third-party library imports
3. Local application imports

**Import Style:**
```python
# Standard library
import logging
from pathlib import Path
from typing import Optional

# Third-party
import git
from pydantic import BaseModel

# Local imports (use relative imports)
from .server import serve
```

**Import Rules:**
- Use absolute imports for third-party packages
- Use relative imports for local modules
- Group imports by category with blank lines between groups
- Import specific exceptions rather than entire modules

### Naming Conventions

**Functions and Methods:**
- Use `snake_case`
- Be descriptive but concise
- Use verbs for action functions

**Classes:**
- Use `PascalCase`
- Use descriptive nouns

**Constants and Enums:**
- Use `UPPER_SNAKE_CASE` for constants
- Enum values should be descriptive strings

**Variables and Parameters:**
- Use `snake_case`
- Be descriptive but avoid excessive length
- Use `repo` instead of `repository` when context is clear

## Advanced Patterns (Use When Needed)

### PEP 695: Modern Type Parameter Syntax

Use PEP 695 syntax for new generic functionality:

```python
# Modern PEP 695 syntax
def process_items[T](items: Sequence[T]) -> list[T]:
    return list(items)

class Repository[T]:
    def __init__(self, repo: T) -> None:
        self.repo = repo

# For bounded type parameters
def sortable_items[T: Comparable](items: Sequence[T]) -> list[T]:
    return sorted(items)
```

**Migration Note**: Existing code using traditional `TypeVar` syntax can remain as-is.

### Modern Python Features

**Match-Case (Python 3.10+):**
```python
match branch_type:
    case 'local':
        b_type = None
    case 'remote':
        b_type = "-r"
    case 'all':
        b_type = "-a"
    case _:
        return f"Invalid branch type: {branch_type}"
```

**Walrus Operator:**
```python
# Use when it improves readability
if (result := expensive_computation()) is not None:
    return result
```

## Documentation Standards

### Docstrings
All public functions, classes, and methods should have docstrings:

```python
def validate_repo_path(repo_path: Path, allowed_repository: Path | None) -> None:
    """Validate that repo_path is within the allowed repository path."""
    # implementation
```

### Complex Functions
For functions with complex logic, include inline comments:

```python
def git_log(repo: git.Repo, max_count: int = 10) -> list[str]:
    # Use git log command with date filtering
    args = ['--format=%H%n%an%n%ad%n%s%n']
    
    # Process commits in groups of 4 (hash, author, date, message)
    log_output = repo.git.log(*args).split('\n')
    # ... rest of implementation
```

## Security Considerations

### Input Validation
- Validate all user input that could be passed to shell commands
- Prevent flag injection attacks
- Sanitize file paths and command arguments

**Examples:**
```python
# Prevent flag injection
if target.startswith("-"):
    raise BadName(f"Invalid target: '{target}' - cannot start with '-'")

# Prevent path traversal
try:
    resolved_repo.relative_to(resolved_allowed)
except ValueError:
    raise ValueError(
        f"Repository path '{repo_path}' is outside the allowed repository '{allowed_repository}'"
    )
```

## Tool Configuration Standards

### Configuration File Location
- **All tool configuration must be stored in `pyproject.toml`** following [PEP 621](https://peps.python.org/pep-0621/)
- Avoid separate configuration files (`.ini`, `.cfg`, `.yaml`, etc.) when possible
- Use standardized PEP 621 sections for tool configuration

**Example structure:**
```toml
[project]
# PEP 621 project metadata

[tool.ruff]
# Ruff configuration

[tool.pyright]
# Pyright configuration

[tool.pytest.ini_options]
# Pytest configuration
```

## Lessons Learned and Best Practices

### Import Structure

**Use absolute imports consistently** to avoid mocking issues in tests and make refactoring easier:

```python
# ✅ Recommended
from vors_ting.agents.creator import CreatorAgent
from vors_ting.core.config import Config

# ❌ Avoid
from ..agents.creator import CreatorAgent
from ..core.config import Config
```

### Testing Strategy

**Mock at the right level** - where the code under test imports from, not where classes are defined:

```python
# ✅ Correct mock target
@patch('vors_ting.orchestration.orchestrator.CreatorAgent')

# ❌ Incorrect mock target (causes tests to fail)
@patch('vors_ting.agents.creator.CreatorAgent')
```

### Project Structure

**Create `__init__.py` files immediately** for all packages to avoid "implicit namespace package" warnings:

```bash
# Create package structure with init files
touch src/vors_ting/{agents,core,orchestration,utils}/__init__.py
```

### Type Annotations

**Use modern Python 3.10+ syntax** instead of legacy typing module:

```python
# ✅ Modern syntax (Python 3.10+)
from typing import Any

def function(arg: str | None = None) -> dict[str, Any]:
    pass

# ❌ Legacy syntax
from typing import Optional, Dict, Any

def function(arg: Optional[str] = None) -> Dict[str, Any]:
    pass
```

## Additional Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Ruff Formatter](https://docs.astral.sh/ruff/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 695: Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [PEP 621: Project Metadata](https://peps.python.org/pep-0621/)
- [Development Guide](development_guide.md) - Comprehensive development advice
- [Agent Development Guide](agents.md) - Specific guidance for agent implementation

---

*This document focuses on essential coding standards. For development workflow, tool configuration, and contribution guidelines, see CONTRIBUTING.md and TOOLS.md.*