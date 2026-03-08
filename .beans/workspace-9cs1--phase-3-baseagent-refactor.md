---
# workspace-9cs1
title: 'Phase 3: BaseAgent Refactor'
status: completed
type: task
priority: normal
created_at: 2026-03-08T14:04:31Z
updated_at: 2026-03-08T14:42:30Z
parent: workspace-aikw
blocked_by:
    - workspace-qev7
---

## Phase 3: BaseAgent Refactor

Replace manual LLM calling with Pydantic AI Agent in src/vors_ting/agents/base.py.

### Key Changes
- Remove 60 lines of manual retry logic
- Remove RateLimitError handling (built into Pydantic AI)
- Remove manual response parsing
- Make methods async
- Add output_type parameter for structured outputs

### New Implementation Highlights
- Import Agent from pydantic_ai
- Add _create_agent() method that creates Agent with retries=3
- Make _call_llm() async with output_type parameter
- Update abstract methods to be async

### Steps
- [x] Refactor src/vors_ting/agents/base.py
- [x] Add _create_agent() method
- [x] Make _call_llm() async with output_type parameter
- [x] Update abstract methods to be async
- [x] Run tests and type checks

### Parent
Part of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add src/vors_ting/agents/base.py
git commit -m "Phase 3: Refactor BaseAgent to use Pydantic AI

- Replace manual LLM calling with Pydantic AI Agent
- Remove 60 lines of custom retry logic
- Remove RateLimitError handling (built into Pydantic AI)
- Make _call_llm() async with output_type parameter
- Add _create_agent() method with retries=3
"
```
