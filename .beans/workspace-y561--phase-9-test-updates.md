---
# workspace-y561
title: 'Phase 9: Test Updates'
status: todo
type: task
priority: normal
created_at: 2026-03-08T14:04:32Z
updated_at: 2026-03-08T14:14:30Z
parent: workspace-aikw
blocked_by:
    - workspace-0m5e
---

## Phase 9: Test Updates

Update tests in tests/test_agents.py to use TestModel for deterministic testing.

### Key Changes
- Use TestModel from pydantic_ai.models.test
- Make tests async with @pytest.mark.asyncio
- Inject test model into agents instead of mocking litellm.completion

### Steps
- [ ] Update test imports to use TestModel
- [ ] Add @pytest.mark.asyncio to all agent tests
- [ ] Replace mock_llm patches with TestModel injection
- [ ] Update assertions for structured outputs
- [ ] Run all tests

### Parent
Part of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add tests/
git commit -m "Phase 9: Update tests for Pydantic AI

- Use TestModel from pydantic_ai.models.test
- Add @pytest.mark.asyncio to agent tests
- Replace mock_llm patches with TestModel injection
- Update assertions for structured outputs
"
```
