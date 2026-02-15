# Agent Memory System Design

## 1. Overview

The agent memory system provides persistent, cross‑session storage for each agent’s performance history, enabling **anti‑fragile learning**—the ability to improve from attacks, mistakes, and human feedback. It tracks key events (dissents, human overrides) and computes dynamic trust metrics that influence agent roles and behavior. This document details the design, data structures, integration points, and usage of the memory system.

## 2. Goals

- **Capture agent behavior over time** – record every dissent, every human override, and their outcomes.
- **Compute dynamic trust scores** – quantify how reliable an agent’s critiques and generations are.
- **Influence agent roles** – use trust scores to exclude low‑quality dissenters from the Devil’s Advocate role, or to weight feedback.
- **Enable living rubric adjustments** – high‑trust human overrides can trigger rubric updates.
- **Support resume capability** – reload agent state when continuing a previous run.
- **Provide data for metrics** – dissent impact, regret rate, and escalation usefulness are derived from memory.

## 3. Data Architecture

Each agent has its own memory file stored in a `memory/` directory (e.g., `memory/Creator1.json`). The file contains:

### 3.1 Agent Metadata
- `agent_name`: unique identifier (matches config)
- `model`: model used (may change over time)
- `primary_role`: creator/reviewer/curator (may evolve)

### 3.2 Dissent History
List of all instances where the agent acted as a dissenter (e.g., as Devil’s Advocate or during peer review with significant disagreement).

```json
"dissent_history": [
  {
    "round_id": "run_20250214_153000/round_2",
    "timestamp": "2025-02-14T16:20:00Z",
    "context": {
      "task": "Write ADR for GraphQL migration",
      "artifact_type": "adr"
    },
    "dissent_text": "The decision to use GraphQL ignores existing REST tooling...",
    "rubric_citations": ["Accuracy", "Completeness"],
    "impact": true,   // whether the dissent changed the final output
    "depth_score": 1.4,  // computed via dissent_depth() (see 4.1)
    "feedback_incorporated": true
  }
]
```

### 3.3 Override History
Records every time a human overrode the system’s converged output (or an agent’s suggestion).

```json
"override_history": [
  {
    "round_id": "run_20250214_153000/round_4",
    "timestamp": "2025-02-14T17:00:00Z",
    "context": { "task": "..." },
    "agent_output": "original text...",
    "human_decision": "modified text...",
    "regret": false,   // later marked true if reverted
    "auto_check_deadline": "2025-02-15T17:00:00Z",  // for revert detection
    "reverted_by": null
  }
]
```

### 3.4 Trust Score and History
A floating value between 0 and 1, updated after each relevant event.

```json
"trust_score": 0.78,
"trust_score_history": [
  { "timestamp": "...", "score": 0.72, "reason": "initial" },
  { "timestamp": "...", "score": 0.75, "reason": "dissent_impact_true" }
]
```

### 3.5 Long‑Term Statistics (Decayed Aggregates)
To prevent memory bloat, recent events are kept raw (last 100), while older data is compressed into rolling statistics.

```json
"long_term_stats": {
  "avg_dissent_depth_last_90d": 0.75,
  "dissent_impact_ratio_last_90d": 0.6,
  "total_overrides": 42,
  "regret_rate_last_90d": 0.1
}
```

### 3.6 Participation Tracking
```json
"rounds_participated": 24,
"probation_until": "2025-03-01T00:00:00Z"  // if applicable
```

## 4. Trust Score Calculation

The trust score is a weighted combination of three factors:

- **Dissent Impact Ratio** = `(impactful_dissents) / (total_dissents)` – measures how often dissents change outcomes.
- **Average Dissent Depth** – computed over recent dissents (see 4.1).
- **Regret Ratio** = `(regretted_overrides) / (total_overrides)` – high regret reduces trust.

Formula:

```
trust_score = 0.4 * impact_ratio + 0.3 * avg_dissent_depth + 0.3 * (1 - regret_ratio)
```

Where:
- `impact_ratio` and `regret_ratio` are based on a rolling window (e.g., last 90 days) or all history if insufficient data.
- `avg_dissent_depth` is the mean of recent `depth_score` values.

### 4.1 Dissent Depth Calculation

To prevent shallow gaming, each dissent is assigned a depth score combining:

- **Length** (normalized word count, capped at 1.0).
- **Rubric citations** (each citation adds 0.2, capped at 0.5).
- **Novelty** (1 minus maximum cosine similarity to past dissents by the same agent).

```python
def dissent_depth(dissent_text, rubric_citations, previous_dissents=None):
    base = min(len(dissent_text.split()) / 50, 1.0)  # Cap at 1.0
    citation_bonus = min(len(rubric_citations) * 0.2, 0.5)  # Cap at 0.5
    novelty = 0.0
    if previous_dissents:
        # Compute embeddings (using sentence-transformers or LiteLLM)
        novelty = 1 - max(cosine_sim(dissent_text, past) for past in previous_dissents)
    return min(base + citation_bonus + novelty, 2.0)  # Max depth = 2.0
```

The novelty term requires storing embeddings of past dissents (or computing on the fly). For efficiency, we can store a pre‑computed embedding for each dissent.

## 5. Safeguards and Role Assignment

### 5.1 Devil’s Advocate Selection
The orchestrator uses memory to filter and weight candidates for the Devil’s Advocate role:

```python
def assign_devils_advocate(candidates):
    # Filter out agents with very low trust (e.g., < 0.2) or still on probation
    viable = [
        agent for agent in candidates
        if agent.get("trust_score", 0.6) > 0.2
        and agent.get("rounds_participated", 0) >= 5  # probation period
    ]
    if not viable:
        viable = candidates  # Fallback

    # Weighted random selection: higher trust = higher chance
    weights = [agent.get("trust_score", 0.6) for agent in viable]
    return random.choices(viable, weights=weights, k=1)[0]
```

### 5.2 Probation for New Agents
New agents start with an initial trust score of 0.6 and are ineligible for critical roles until they have participated in at least 5 rounds.

### 5.3 Echo Chamber Prevention
Low‑trust agents are not permanently excluded—they still have a chance (proportional to trust) to be selected. If an agent’s trust falls below 0.2, they are excluded entirely (fallback ensures at least one candidate).

## 6. Automated Regret Inference

To reduce reliance on human labeling, the system automatically infers regret if an override is later reverted.

```python
def log_override(agent_memory, round_id, agent_output, human_decision):
    override = {
        "round_id": round_id,
        "agent_output": agent_output,
        "human_decision": human_decision,
        "regret": False,
        "auto_check_deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
        "reverted_by": None
    }
    agent_memory["override_history"].append(override)
    return override

def check_reverts(agent_memory, round_id, final_output):
    for override in agent_memory["override_history"]:
        if (override["round_id"] == round_id and
            override["human_decision"] != final_output and
            datetime.now() > datetime.fromisoformat(override["auto_check_deadline"])):
            override["regret"] = True
            override["reverted_by"] = "system"  # or the human who reverted
```

If another human later undoes the override (detected via version comparison), we mark it as reverted immediately.

## 7. Integration with Orchestrator

- **Initialization**: Orchestrator calls `AgentMemory.load(agent_name)` for each agent at startup.
- **During rounds**: After each dissent or override, orchestrator calls `log_dissent()` or `log_override()`.
- **After convergence**: If human overrides the final output, log override and optionally re‑run check_reverts later.
- **Before role assignment**: Orchestrator queries memory for trust scores and participation counts.

## 8. Implementation Plan

| Phase | Goal | Tasks |
|-------|------|-------|
| 4.1 | Core Memory System | Implement `AgentMemory` class, JSON schema, basic logging. |
| 4.2 | Trust Score Refinements | Add dissent depth, decay, probation logic. |
| 4.3 | Automated Regret Inference | Implement revert detection and controversy tracking. |
| 4.4 | Devil’s Advocate Safeguards | Add probabilistic inclusion and trust‑weighted role assignment. |
| 4.5 | Metrics Integration | Feed memory data to metrics logger (dissent impact, regret rate). |

## 9. Future Enhancements

- **Dissent diversity tracking**: Compute entropy of rubric citations to detect gaming (e.g., always citing same criteria). Flag for human review if diversity drops while trust remains high.
- **Cross‑agent memory**: Track which agents influence each other.
- **Predictive dissent**: Use memory to predict which agents will dissent effectively on a given topic.

## 10. Conclusion

The agent memory system transforms the scaffolding from a stateless loop into a learning organization. By remembering past successes and failures, it can dynamically prune ineffective behaviors, amplify trustworthy agents, and continuously adapt to human preferences. This is the foundation of anti‑fragility—getting stronger from every mistake and every attack.
```
