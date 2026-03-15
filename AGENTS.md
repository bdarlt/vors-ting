# Vörs ting - Agent Context

Multi-agent workflow tool. Python 3.13. Orchestrates feedback loops via CLI + YAML config.

## Critical Rule for AGENTS.MD file

optimize for token efficiency and practical utility. I should make it very
dense, structured, and actionable. Remove fluff, maximize signal.

**IMPORTANT**: before you do anything else, run the `beans prime` command and heed its output.

## Critical Rules (Break = Fail)

1. **Imports: ABSOLUTE ONLY** - `from vors_ting.xxx.yyy import Zzz` - never relative
2. **Mock target:** Where code imports FROM, not where class defined
3. **Line length:** 88 max
4. **Formatter:** Ruff (configured in pyproject.toml)
5. **Type hints:** Required, modern syntax: `str | None`, `dict[str, Any]`, not `Optional/Dict`
6. **Tool config:** pyproject.toml only, never separate .ini/.cfg files
7. **Python 3.13+** - use match-case, walrus, PEP 695 generics

## Fast Check Commands

```bash
uv run pytest -x                    # fail fast tests
uv run pytest -m "not slow"         # skip slow tests (embedding model)
uv run ruff check --fix .           # lint + auto-fix
uv run format                # format
uv run pyright                      # type check

# Run vors (verbose shows LLM calls, feedback, previews)
uv run vors examples/simple.yaml

# Run quietly
uv run vors examples/simple.yaml -q

# Using main.py entry point
uv run python main.py run examples/simple.yaml -q
```

### Windows Shell Quirks
```powershell
# ❌ Doesn't work on Windows
cd path && uv run pytest

# ✅ Use semicolons on Windows
Set-Location path; uv run pytest
# or
cd path; uv run pytest
```

### Test Markers
- `@pytest.mark.slow` — Tests that load embedding models (~20s first run)
- `@pytest.mark.integration` — Tests requiring API keys
- Skip slow: `pytest -m "not slow"`
- Run only slow: `pytest -m slow`

## Devcontainer Tools (Available in `devcontainer/Dockerfile.kimi`)

| Tool | Purpose | Example |
|------|---------|---------|
| `rg` | Fast grep with gitignore | `rg 'class.*Agent' src/` |
| `bat` | Syntax-highlighted cat | `bat src/vors_ting/core/config.py` |
| `eza` | Modern ls (alias: `ls`) | `eza -la --git` |
| `yq` | YAML processor | `yq '.agents[0].model' examples/simple.yaml` |
| `fzf` | Fuzzy finder | `fd -t f | fzf` |
| `hyperfine` | Benchmark | `hyperfine 'uv run pytest -x'` |
| `dust` | Visual du | `dust -d 2` |
| `xh` | HTTP client | `xh httpie.io/hello` |
| `rga` | Search in PDFs/zips | `rga 'TODO' docs/` |
| `tre` | Git-aware tree | `tre -e` |
| `tokei` | Code stats | `tokei src/` |
| `procs` | Modern ps | `procs --tree` |
| `sd` | Modern sed | `sd 'old' 'new' *.py` |
| `choose` | Column select | `ps aux | choose 1 11` |
| `sg` | ast-grep (structural) | `sg -p 'class $C' -l python` |
| `difft` | difftastic | `git difftool --tool=difftastic` |
| `fdf` | fd-find (alias: `fd`) | `fd -e py 'config'` |
| `delta` | Git pager | `git diff | delta` |
| `zoxide` | Smart cd | `z src` (or `cd src`) |
| `jq` | JSON processor | `cat file.json \| jq '.key'` |
| `scc` | Code counter | `scc src/` |
| `broot` | Interactive file tree | `broot` (or `br`) |
| `glow` | Markdown renderer | `glow README.md` |
| `git-extras` | Git utilities | `git summary`, `git effort` |
| `tldr` | Quick command help (tealdeer) | `tldr tar` |

## Code Patterns

### Correct Import Pattern
```python
# ✅ DO
from vors_ting.agents.creator import CreatorAgent
from vors_ting.core.config import Config

# ❌ NEVER
from ..agents.creator import CreatorAgent
```

### Correct Mock Pattern
```python
# ✅ DO - mock where IMPORTED (in code under test)
@patch('vors_ting.orchestration.orchestrator.CreatorAgent')

# ❌ NEVER - mock where DEFINED
@patch('vors_ting.agents.creator.CreatorAgent')
```

### Type Annotations
```python
# ✅ DO
from typing import Any
def func(arg: str | None = None) -> dict[str, Any]: ...
class Repo[T]: ...

# ❌ NEVER
from typing import Optional, Dict
def func(arg: Optional[str] = None) -> Dict[str, Any]: ...
```

## Architecture

```
src/vors_ting/
├── agents/           # BaseAgent → CreatorAgent, ReviewerAgent, CuratorAgent
├── core/             # Config (Pydantic), models, validation
├── orchestration/    # Orchestrator - runs feedback loops
└── utils/            # Helpers, logging

tests/                # Mirror src structure
examples/             # YAML configs showing usage patterns
```

## Agent Lifecycle

1. **Init:** Config → Agent instance with system prompt + LLM (LiteLLM)
2. **Generate:** Creator generates content from task
3. **Review:** Reviewer evaluates via rubric → feedback dict
4. **Refine:** Creator revises based on feedback
5. **Loop:** Repeat N rounds or until convergence

## Common Failures & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError` relative import | Using `from ..x import` | Change to `from vors_ting.x import` |
| Mock not working | Mocked wrong path | Target where code UNDER TEST imports |
| Pydantic validator fail | Used `self` not `cls` | `@validator` uses `cls` (V1) or migrate to `@field_validator` (V2) |
| Implicit namespace warning | Missing `__init__.py` | `touch src/vors_ting/newpkg/__init__.py` |
| Type check fail | Legacy typing | Use `\| None`, `dict[]`, `list[]` |
| Test needs API key | Not mocked properly | Mock `litellm.completion` or agent's LLM call |

## YAML Config Structure

```yaml
task: "Write ADR for X"
artifact_type: "adr"  # adr | test | doc | cursor-rules | meeting | generic
agents:
  - name: "Creator1"
    role: "creator"   # creator | reviewer | curator
    model: "claude-3-opus-20240229"
    provider: "anthropic"  # LiteLLM provider (optional)
    temperature: 0.7
    file: "prompts/custom.md"  # External prompt file (optional)
  - name: "Skeptic"
    role: "reviewer"
    model: "gemini-1.5-pro"
    provider: "google"
rounds: 5
mode: "converge"      # converge | diverge
rubrics:              # Optional evaluation criteria
  clarity: "Is it clear?"
  completeness: "All sections covered?"
```

### Model Format

LiteLLM uses `provider/model-name` format:
- `provider: "mistral"` + `model: "devstral-latest"` → `mistral/devstral-latest`
- `provider: null` + `model: "openai/gpt-4"` → `openai/gpt-4`

## Dependencies

- **LiteLLM** - LLM abstraction (OpenAI, Anthropic, Google, etc.)
- **Pydantic** - Config validation
- **Typer** - CLI
- **Rich** - Terminal output
- **sentence-transformers** - Embeddings for clustering/curator

Manage with UV: `uv add <pkg>` / `uv add --dev <pkg>`

## Testing Strategy

```python
# Pattern for unit tests
@patch('vors_ting.orchestration.orchestrator.litellm.completion')
def test_orchestrator_run(mock_llm):
    mock_llm.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"score": 8}'))]
    )
    config = Config(...)  # or load from YAML
    orch = Orchestrator(config)
    result = orch.run()
    assert "artifact" in result
```

## Memory System (Anti-fragile)

- Tracks agent performance over time
- Learns from failures/successes/human feedback
- Embeddings cluster similar tasks
- Improves prompts dynamically

## When to Read Full Docs

- `docs/agents.md` - Creating new agent types, custom behavior
- `docs/CODING_STANDARDS.md` - Edge cases, security patterns
- `docs/development_guide.md` - Deep debugging, architecture decisions
- `docs/design.md` - System design rationale
- `docs/memory-system.md` - Working with persistent memory
- `docs/development/migration-to-pydantic-ai.md` - Migrating from LiteLLM to Pydantic AI
