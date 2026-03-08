---
# workspace-0m5e
title: 'Phase 8: CLI Entry Point Update'
status: completed
type: task
priority: normal
created_at: 2026-03-08T14:04:31Z
updated_at: 2026-03-08T14:54:28Z
parent: workspace-aikw
blocked_by:
    - workspace-tqmd
---

## Phase 8: CLI Entry Point Update

Update src/vors_ting/cli.py to wrap async orchestrator with asyncio.run().

### Key Changes
- Add import asyncio
- Wrap orchestrator.run() with asyncio.run()

### Steps
- [ ] Add import asyncio to cli.py
- [ ] Wrap orchestrator.run() with asyncio.run()
- [ ] Test CLI works correctly
- [ ] Run tests and type checks

### Parent
Part of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add src/vors_ting/cli.py
git commit -m "Phase 8: Update CLI for async orchestrator

- Add import asyncio
- Wrap orchestrator.run() with asyncio.run()
"
```
