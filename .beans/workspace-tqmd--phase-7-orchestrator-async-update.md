---
# workspace-tqmd
title: 'Phase 7: Orchestrator Async Update'
status: todo
type: task
priority: normal
created_at: 2026-03-08T14:05:06Z
updated_at: 2026-03-08T14:14:16Z
parent: workspace-aikw
blocked_by:
    - workspace-ud1o
    - workspace-tjiu
    - workspace-es5v
---

## Phase 7: Orchestrator Async Update

Update src/vors_ting/orchestration/orchestrator.py for async support and parallel execution.

### Key Changes
- Make run() method async
- Make _run_converge_mode() async
- Add _initial_generation() for parallel artifact generation
- Add _review_phase() for parallel reviews
- Add _refine_phase() for parallel refinements
- Use asyncio.gather() for parallel execution

### Steps
- [ ] Add import asyncio
- [ ] Make run() async
- [ ] Implement _initial_generation() with asyncio.gather()
- [ ] Implement _review_phase() with asyncio.gather()
- [ ] Implement _refine_phase() with asyncio.gather()
- [ ] Update _run_converge_mode() to use new async phases
- [ ] Run tests and type checks

### Parent
Part of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add src/vors_ting/orchestration/orchestrator.py
git commit -m "Phase 7: Update Orchestrator for async/parallel execution

- Make run() and _run_converge_mode() async
- Add _initial_generation() with asyncio.gather()
- Add _review_phase() with parallel reviews
- Add _refine_phase() with parallel refinements
"
```
