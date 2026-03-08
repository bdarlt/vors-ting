---
# workspace-r0o2
title: 'Phase 1: Dependencies - Add pydantic-ai, remove litellm'
status: completed
type: task
priority: normal
created_at: 2026-03-08T14:03:56Z
updated_at: 2026-03-08T14:36:53Z
parent: workspace-aikw
---

## Phase 1: Dependencies

Update pyproject.toml to replace LiteLLM with Pydantic AI.

### Changes
- Remove "litellm>=1.0" from dependencies
- Add "pydantic-ai>=0.0.50" to dependencies

### Steps
- [x] Update pyproject.toml dependencies
- [ ] Run `uv sync` to update lock file
- [ ] Verify installation works

### Parent
Part of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add pyproject.toml uv.lock
git commit -m "Phase 1: Add pydantic-ai dependency, remove litellm

- Replace litellm>=1.0 with pydantic-ai>=0.0.50
- Update lock file with uv sync
"
```
