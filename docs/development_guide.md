# Vörs ting Development Guide

This guide provides practical advice and lessons learned for developing the Vörs ting project.

## Table of Contents

- [Project Setup](#project-setup)
- [Development Workflow](#development-workflow)
- [Testing Strategies](#testing-strategies)
- [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
- [Code Quality and Tooling](#code-quality-and-tooling)
- [Lessons Learned](#lessons-learned)

## Project Setup

### Initial Project Structure

```bash
# Create project structure
mkdir -p src/vors_ting/{agents,core,orchestration,utils} tests examples

# Create empty __init__.py files immediately
touch src/vors_ting/{agents,core,orchestration,utils}/__init__.py
```

### Dependency Management with UV

```bash
# Install core dependencies
uv add litellm pyyaml typer rich python-dotenv numpy scikit-learn sentence-transformers

# Install development dependencies
uv add --dev black mypy ruff pytest pytest-cov pytest-mock pytest-asyncio
```

## Development Workflow

### Recommended Development Order

1. **Configuration System** - Start with config loading and validation
2. **Core Abstractions** - Define agent interfaces and base classes
3. **Individual Components** - Implement each agent type separately
4. **Orchestration Layer** - Build the feedback loop management
5. **CLI Interface** - Add user-facing commands
6. **Advanced Features** - Convergence detection, memory system, etc.

### Incremental Development Tips

- **Build features in isolation** before integrating them
- **Test each component** before connecting it to others
- **Use feature flags** for experimental functionality
- **Commit frequently** with small, focused changes

## Testing Strategies

### Mocking Guidelines

**Do mock at the right level:**

```python
# ✅ GOOD: Mock where the code under test imports from
@patch('vors_ting.orchestration.orchestrator.CreatorAgent')
def test_orchestrator(mock_creator):
    # Test orchestrator with mocked agent
    pass

# ❌ BAD: Mocking implementation details
@patch('vors_ting.agents.creator.CreatorAgent._call_llm')
def test_creator(mock_llm):
    # This makes tests brittle
    pass
```

### Test Structure

```python
# Recommended test structure
def test_feature_name():
    """Brief description of what's being tested."""
    # Setup
    config = create_test_config()
    
    # Exercise
    result = system_under_test(config)
    
    # Verify
    assert expected_outcome(result)
    
    # Teardown (if needed)
```

### Avoid External Dependencies in Tests

```python
# ✅ GOOD: Mock external services
@patch('litellm.completion')
def test_agent_without_api_calls(mock_completion):
    mock_completion.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="test"))])
    # Test agent behavior without real API calls

# ❌ BAD: Tests that require API keys or network
# def test_agent_real_api():
#     agent = CreatorAgent()  # This will fail in CI/CD
#     result = agent.generate("test")
```

## Common Pitfalls and Solutions

### Import Issues

**Problem:** Relative imports causing mocking difficulties and circular dependencies

**Solution:** Use absolute imports consistently

```python
# ✅ GOOD: Absolute imports
from vors_ting.agents.creator import CreatorAgent
from vors_ting.core.config import Config

# ❌ BAD: Relative imports from parent modules
from ..agents.creator import CreatorAgent
from ..core.config import Config
```

### Pydantic Validator Issues

**Problem:** Using `self` instead of `cls` in `@validator` methods

**Solution:** Use `cls` for class methods in Pydantic V1 (or migrate to `@field_validator` in V2)

```python
# ✅ GOOD: For Pydantic V1
@validator("agents")
def validate_agents(cls, v):  # Note: cls, not self
    if not v:
        raise ValueError("At least one agent required")
    return v

# ❌ BAD: This will cause errors
@validator("agents")
def validate_agents(self, v):  # Wrong!
    if not v:
        raise ValueError("At least one agent required")
    return v
```

### Type Annotation Issues

**Problem:** Using deprecated typing syntax

**Solution:** Use modern Python 3.10+ type annotations

```python
# ✅ GOOD: Modern syntax
from typing import Any

def function(arg: str | None = None) -> dict[str, Any]:
    pass

# ❌ BAD: Legacy syntax
from typing import Optional, Dict, Any

def function(arg: Optional[str] = None) -> Dict[str, Any]:
    pass
```

## Code Quality and Tooling

### Black Configuration

```toml
[tool.black]
line-length = 88
target-version = ["py313"]
```

**Tip:** Run `black --check` frequently to catch formatting issues early.

### Ruff Configuration

```toml
[tool.ruff.lint]
line-length = 88
target-version = "py313"
select = ["E", "F", "W", "I", "N", "D", "UP", "YTT", "S", "B", "A", "C4"]
ignore = ["D203", "D213", "S101"]  # Ignore docstring and assert warnings in tests
```

**Tip:** Use `ruff check --fix` to automatically fix many issues.

### MyPy Configuration

```toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Pytest Configuration

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-v --tb=short --cov=vors_ting --cov-report=term-missing"
```

## Lessons Learned

### Import Structure

**Issue:** Relative imports caused problems with mocking in tests and made the code harder to refactor.

**Solution:** Use absolute imports from the beginning, even if they seem slightly more verbose.

### Pydantic Validators

**Issue:** Pydantic V1 validators use `cls` not `self`, which is counterintuitive.

**Solution:** Either use `cls` consistently or migrate to Pydantic V2's `@field_validator`.

### Mocking Strategy

**Issue:** Mocks weren't targeting the right modules, causing tests to call real implementations.

**Solution:** Always mock where the code under test imports from, not where the class is defined.

### Configuration Management

**Issue:** Environment variables and API keys caused test failures.

**Solution:** Ensure all tests mock external dependencies and don't require real credentials.

### Code Quality Tools

**Issue:** Ruff's configuration format changed, causing warnings.

**Solution:** Use the new `lint` section format and keep tooling updated.

### Project Structure

**Issue:** Missing `__init__.py` files caused "implicit namespace package" warnings.

**Solution:** Create empty `__init__.py` files immediately, even for simple modules.

## Debugging Tips

### Common Error Patterns

1. **ImportErrors**: Usually caused by circular imports or missing `__init__.py` files
2. **AttributeErrors in tests**: Often due to incorrect mock targeting
3. **TypeErrors**: Usually missing or incorrect type annotations
4. **ConfigurationErrors**: Typically missing required fields in YAML configs

### Debugging Workflow

1. **Reproduce the issue** with a minimal test case
2. **Check the stack trace** to identify the root cause
3. **Add debug prints** temporarily if needed
4. **Consult the documentation** for the specific tool/library
5. **Search for similar issues** in the project's issue tracker

## Contributing to This Guide

This is a living document! Please update it with:

- New lessons learned during development
- Solutions to common problems
- Best practices that emerge over time
- Updates when tools or libraries change

Add new sections as needed to keep this guide comprehensive and useful.
