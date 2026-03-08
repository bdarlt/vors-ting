---
# workspace-aikw
title: 'Migration: LiteLLM → Pydantic AI'
status: todo
type: milestone
priority: high
created_at: 2026-03-08T14:01:22Z
updated_at: 2026-03-08T14:14:54Z
---

Migrate the Vörs ting multi-agent framework from LiteLLM to Pydantic AI for better structured outputs, built-in retries, type safety, and async support.



## Migration Phases

### Core Migration (Phases 1-9)

| Phase | Task | Bean ID |
|-------|------|---------|
| 1 | Dependencies - Add pydantic-ai, remove litellm | workspace-r0o2 |
| 2 | Structured Output Schemas | workspace-qev7 |
| 3 | BaseAgent Refactor | workspace-9cs1 |
| 4 | ReviewerAgent Update | workspace-ud1o |
| 5 | CreatorAgent Update | workspace-tjiu |
| 6 | CuratorAgent Update | workspace-es5v |
| 7 | Orchestrator Async Update | workspace-tqmd |
| 8 | CLI Entry Point Update | workspace-0m5e |
| 9 | Test Updates | workspace-y561 |

### Optional Advanced Migration

| Phase | Task | Bean ID |
|-------|------|---------|
| 10 | Pydantic Graph for Orchestration | workspace-wmk5 |

### Verification

| Task | Bean ID |
|------|---------|
| Verification Checklist and Rollback Plan | workspace-a852 |

## Estimated Effort

- Phases 1-9: 1-2 days
- Phase 10 (Pydantic Graph): +1 day (optional)

## Impact

All agent classes, orchestrator, and tests

## Key Benefits

| Capability | LiteLLM (Current) | Pydantic AI (Target) |
|------------|-------------------|----------------------|
| Structured Output | Manual string parsing | Pydantic-validated models |
| Retry Logic | 60 lines custom code | retries=3 parameter |
| Type Safety | dict[str, Any] | Generic Agent[Deps, Output] |
| Async Support | Sync only | Native async + parallelism |
| Testing | Mock completion() calls | Inject TestModel |
| Observability | Print statements | OpenTelemetry tracing |
| Reflection | Not implemented | Auto-retry on validation failure |



## Git Commit Strategy

Each phase includes a git commit checkpoint. Follow this workflow:

1. **Work on the phase** - Make the required changes
2. **Run tests** - Ensure everything passes: `uv run pytest -x`
3. **Run type checks** - `uv run pyright`
4. **Run linting** - `uv run ruff check`
5. **Commit** - Use the provided commit message in each phase

### Branch Recommendation
```bash
# Create a feature branch for the migration
git checkout -b migrate/pydantic-ai

# After all phases complete and verified
git checkout main
git merge migrate/pydantic-ai
``"

### Rollback Tags (Optional)
```bash
# Tag before migration starts (if on main)
git tag before-pydantic-ai-migration

# Tag after each major phase group
git tag after-phase-3-baseagent  # Core refactor done
git tag after-phase-6-agents     # All agents updated
git tag after-phase-9-complete   # Migration complete
``"
