---
# workspace-es5v
title: 'Phase 6: CuratorAgent Update'
status: completed
type: task
priority: normal
created_at: 2026-03-08T14:05:06Z
updated_at: 2026-03-08T14:45:54Z
parent: workspace-aikw
blocked_by:
    - workspace-9cs1
---

## Phase 6: CuratorAgent Update

Update src/vors_ting/agents/curator.py to use Pydantic AI.

### Key Changes
- Make methods async
- Add @override decorator for type safety
- Update cluster_ideas() to be async

### Steps
- [ ] Add @override decorators
- [ ] Make generate(), review(), refine() async
- [ ] Make cluster_ideas() async
- [ ] Run tests and type checks

### Parent
Part of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add src/vors_ting/agents/curator.py
git commit -m "Phase 6: Update CuratorAgent for Pydantic AI

- Add @override decorators for type safety
- Make generate(), review(), refine() async
- Make cluster_ideas() async
"
```
