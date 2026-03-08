---
# workspace-wmk5
title: 'Phase 10 (Optional): Pydantic Graph for Orchestration'
status: todo
type: feature
priority: normal
created_at: 2026-03-08T14:05:27Z
updated_at: 2026-03-08T14:14:44Z
parent: workspace-aikw
blocked_by:
    - workspace-a852
---

## Phase 10 (Optional): Pydantic Graph for Orchestration

Migrate the orchestrator to use pydantic-graph for declarative, visualizable, and resumable workflow graphs.

### Why Pydantic Graph?

| Current Orchestrator | With Pydantic Graph |
|---------------------|---------------------|
| Imperative phase logic | Declarative state machine |
| Manual convergence checking | Graph edges define transitions |
| No visualization | Auto-generated Mermaid diagrams |
| Lost on crash/restart | State persistence for resumable runs |
| Hard to extend | Add nodes without changing control flow |
| No human-in-the-loop | Pause/resume with external input |

### New Files to Create
- src/vors_ting/orchestration/graph_nodes.py: Graph nodes (Initialize, GenerateInitial, Review, CheckConvergence, Refine)
- src/vors_ting/orchestration/graph_orchestrator.py: Graph-based orchestrator

### Graph Nodes
- Initialize: Initialize agents and state
- GenerateInitial: Generate initial artifacts from creators
- Review: Review artifacts with reviewers
- CheckConvergence: Check if artifacts have converged
- Refine: Refine artifacts based on reviews

### Benefits
1. Visual Workflow Documentation - Generate Mermaid diagrams automatically
2. Resumable Runs with State Persistence - For long-running workflows or crash recovery
3. Human-in-the-Loop Support - Pause for human approval at critical points
4. Easy Extension - Add new phases without changing existing code

### When to Use
- Complex multi-phase workflows
- Need human-in-the-loop
- Long-running/resumable runs
- Visual documentation required
- Multiple workflow types (converge/diverge/custom)

### Migration Strategy
1. Complete Phases 1-9 first (basic pydantic-ai migration)
2. Stabilize: Run with new async orchestrator for a few weeks
3. Evaluate: Determine if graph complexity is needed
4. Phase 10 (if needed): Migrate to pydantic-graph

### Steps
- [ ] Evaluate if pydantic-graph is needed
- [ ] Create graph_nodes.py with all node classes
- [ ] Create graph_orchestrator.py
- [ ] Add visualize() method for Mermaid diagrams
- [ ] Add state persistence support
- [ ] Run tests and type checks

### Parent
Optional advanced phase of the LiteLLM → Pydantic AI migration (milestone: workspace-aikw).



### Git Commit Checkpoint
After completing this phase:
```bash
git add src/vors_ting/orchestration/graph_nodes.py     src/vors_ting/orchestration/graph_orchestrator.py
git commit -m "Phase 10: Add Pydantic Graph orchestration (optional)

- Add graph_nodes.py with Initialize, GenerateInitial, Review, CheckConvergence, Refine nodes
- Add graph_orchestrator.py for declarative workflow graphs
- Add visualize() method for Mermaid diagrams
- Support state persistence and human-in-the-loop
"
```
