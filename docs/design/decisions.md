# Vörs ting: Critical Design Decisions

This document captures the key architectural and design decisions made during the development of Vörs ting. It serves as the authoritative record of *why* we chose certain approaches, the alternatives considered, and the implications of each decision. Keep this document updated as new decisions are made.

---

## 1. Consensus Threshold and Small‑Group Rounding

### Context
When using a supermajority threshold (e.g., 80%) for convergence, the number of required votes depends on the number of agents. For small groups (3–4 agents), simple `ceil(agent_count * threshold)` can produce unexpected results:

| Agents | 80% raw | ceil() | Result | Implication         |
|--------|---------|--------|--------|---------------------|
| 3      | 2.4     | 3      | 100%   | stricter than intended |
| 4      | 3.2     | 4      | 100%   | stricter than intended |
| 5      | 4.0     | 4      | 80%    | exact               |
| 6      | 4.8     | 5      | 83%    | slightly higher     |

### Options Considered
1. **Always ceil** – Simple but unintentionally forces unanimity for 3‑4 agents.
2. **Always floor** – For 3 agents would require 2 (66%), which is below the intended 80% supermajority.
3. **Hybrid: floor for groups ≤ 4, ceil otherwise** – Balances intent across all group sizes.
4. **Unanimous under N** – Force unanimity for very small groups (e.g., <5) and then switch to threshold.

### Decision
Adopt **hybrid: floor for groups ≤ 4, ceil otherwise**. This yields:

| Agents | Required | Actual % |
|--------|----------|----------|
| 1      | 1        | 100%     |
| 2      | 2        | 100%     |
| 3      | 2        | 66.7%    |
| 4      | 3        | 75%      |
| 5      | 4        | 80%      |
| 6      | 5        | 83%      |
| …      | …        | …        |

The slight under‑shoot for 3‑4 agents is acceptable because in practice these groups are rare, and the alternative (forcing unanimity) would be too restrictive. The strategy is configurable via `small_group_strategy` (options: `floor`, `ceil`, `unanimous_under`).

---

## 2. Disagreement Triage Method

### Context
When agents disagree, we need to classify the disagreement as **factual**, **value‑based**, or **semantic** to decide whether to escalate immediately, continue iterating, or update the rubric.

### Options Considered
1. **Pure LLM classification** – Use an LLM to classify each disagreement. Accurate but slow, costly, and may introduce meta‑disagreement.
2. **Pure heuristic classification** – Rule‑based detection (citations → factual, value words → value). Fast and free, but brittle and misses nuance.
3. **Hybrid: heuristics first, LLM fallback** – Use heuristics with confidence scores; if confidence < threshold, invoke an LLM. Caches results to avoid repeated calls.

### Decision
Adopt **hybrid triage**. Heuristics provide a fast path for clear cases; the LLM is only used for ambiguous disagreements. This balances speed, cost, and accuracy.

- Heuristics include:
  - **Factual**: detection of citations (RFC, section numbers, `[1]`‑style references) with confidence based on pattern specificity.
  - **Value**: explicit value words (`should`, `better`) → confidence 0.9; implicit value words (`maintainable`, `clean`) → confidence 0.7‑0.3 depending on density.
  - **Semantic**: high embedding similarity (>0.7) but low word overlap (<0.5) suggests the same idea expressed differently.
- Confidence threshold for fallback is configurable (default 0.8).
- LLM fallback uses a small, cheap model (e.g., `gpt‑3.5‑turbo`). Results are cached.

---

## 3. Devil’s Advocate Selection

### Context
The Devil’s Advocate (DA) role prevents groupthink by forcing one agent to argue against the emerging consensus. Selection must balance giving everyone a chance with rewarding high‑trust agents.

### Options Considered
1. **Uniform random** – Simplest, but ignores performance.
2. **Trust‑weighted** – Higher‑trust agents more likely to be selected. Rewards proven dissenters.
3. **Round‑robin** – Deterministic rotation. Can become predictable.

### Decision
Adopt **trust‑weighted selection** as the default, with a fallback to uniform random if no agent meets the minimum trust threshold. Additionally:

- **Probation period**: New agents must participate in at least 5 rounds before becoming eligible.
- **Minimum trust**: Agents with trust < 0.2 are excluded (unless no others exist).
- **Cooldown**: After being DA, an agent receives a penalty in subsequent rounds to prevent fatigue. Penalty decays linearly over the cooldown period (default 3 rounds).
- **Skip rate**: 10% of rounds have no DA at all, to establish a baseline and avoid over‑use of the safeguard.

---

## 4. Shadow Rubric and Drift Handling

### Context
The living rubric evolves based on human overrides and agent feedback. We need to detect when it drifts too far from the original (gold) rubric to decide if the drift is beneficial or harmful.

### Options Considered
1. **Auto‑revert** – Automatically restore the gold rubric when drift exceeds a threshold. Risky because drift might be intentional improvement.
2. **Alert only** – Log drift and notify humans, but never auto‑revert. Humans decide.
3. **Pause and review** – If critical drift detected, pause the run and ask for human input.

### Decision
Adopt **alert only**, with escalating severity:

- **Info** (<5% drift): logged only.
- **Warning** (5‑15% drift): logged and flagged in dashboard.
- **Critical** (>15% drift): logged, flagged, and optionally pauses execution (configurable). Humans are alerted to review the comparison.

**Never auto‑revert**. Drift may represent genuine learning; humans should always make the final call.

Check frequency: every 3 rounds **and** after every human override.

---

## 5. Metrics Logging Format

### Context
We need to capture detailed event data for debugging, analysis, and dashboarding.

### Options Considered
1. **Single JSON file** – Simple but hard to query and grows large.
2. **Separate files per round** – Better organisation but many files.
3. **Hybrid: JSONL for events + CSV for time series + JSON summary** – Balances completeness and ease of analysis.

### Decision
Adopt the **hybrid approach**:

- **events.jsonl** – Newline‑delimited JSON, one event per line. Contains full fidelity data (every dissent, override, vote, etc.). Ideal for replay and deep debugging.
- **metrics.csv** – Flattened, time‑series data (one row per round) with key metrics: similarity scores, dissent count, convergence time, etc. Easy to plot.
- **summary.json** – Final run statistics: total rounds, regret rate, average trust change, etc. Used for dashboards and post‑run reports.

Logging is buffered and flushed periodically (every 60s or 100 events) to balance performance and durability.

---

## 6. Agent Memory Trust Score Components

### Context
The trust score determines how much weight an agent’s opinions carry and eligibility for special roles. It must resist gaming while reflecting genuine value.

### Options Considered
1. **Only dissent impact** – Simple, but agents could focus on quantity over quality.
2. **Dissent impact + regret ratio** – Adds a penalty for overrides that were later regretted.
3. **Add dissent depth** – Measures the quality of each dissent (length, rubric citations, novelty). Prevents shallow dissents.

### Decision
Adopt **three‑component trust score**:

```
trust_score = 0.4 * dissent_impact_ratio
             + 0.3 * avg_dissent_depth
             + 0.3 * (1 - regret_ratio)
```

- **dissent_impact_ratio** = impactful dissents / total dissents.
- **avg_dissent_depth** = mean of depth scores (length + citations + novelty, capped at 2.0).
- **regret_ratio** = regretted overrides / total overrides.

Depth calculation includes novelty via embedding similarity to previous dissents by the same agent, preventing repetitive shallow critiques.

---

## 7. Probation and Cooldown Periods

### Context
New agents should not immediately be trusted with critical roles, and recently used agents should be given a rest to avoid fatigue.

### Options Considered
1. **No probation** – New agents immediately eligible. Risk of poor early decisions.
2. **Fixed‑round probation** – Require a minimum number of participations.
3. **Trust‑based probation** – Wait until trust reaches a threshold.

### Decision
Adopt **fixed‑round probation** (default 5 rounds) for simplicity. After probation, agents are eligible for roles like Devil’s Advocate.

For cooldown, use a **decaying penalty** over a fixed number of rounds (default 3). The penalty is applied to the agent’s trust weight during selection, with a maximum penalty of 70% immediately after being DA, decaying to zero by the end of the cooldown.

---

## 8. Per‑Safeguard Toggles

### Context
During testing and debugging, we may need to disable individual safeguards to
isolate behavior or measure baseline performance.

### Options Considered

1. **Master switch only** – All safeguards on/off together. Too coarse.
2. **Individual flags** – Each safeguard can be enabled/disabled independently.
3. **Master + individual** – Master turns all off; individual flags override when master is on.

### Decision

Adopt **master + individual toggles**. The configuration includes:

```yaml
safeguards:
  enabled: true                # master
  devil_advocate:
    enabled: true
    # ... DA‑specific settings
  shadow_rubric:
    enabled: true
  probation_period:
    enabled: true
    rounds: 5
  cooldown:
    enabled: true
    rounds: 3
```

If `safeguards.enabled` is false, all safeguards are off regardless of individual flags. This allows quick global disable while retaining fine‑grained control.

---

## 9. Testing Mode

### Context

Automated tests must be deterministic and not depend on live LLM APIs. We need
a way to mock LLM responses and control randomness.

### Decision

Implement a **testing mode** activated by a configuration flag (`mode: "test"`). In testing mode:

- LLM calls are replaced by a `MockLLM` that returns pre‑defined responses in a cycle.
- Random number generation is seeded (configurable seed) for reproducibility.
- All safeguard decisions are logged in detail.
- A special `deterministic: true` flag disables any remaining randomness (e.g., in DA selection) to make tests fully repeatable.

The mock LLM responses are stored in a separate file (`test/fixtures/mock_responses.json`) and can be versioned alongside the tests.

---

## 10. Divergence Mode (Future)

### Context
For brainstorming and exploration, we need a mode where the goal is to generate diverse options rather than converge on a single answer.

### Decision (Provisional)
Divergence mode will be implemented in Phase 5. Key differences from convergence mode:

- **Curator agent** replaces the moderator. It clusters ideas (using embedding similarity) and highlights disagreements.
- **Peer review** focuses on identifying differences, not scoring.
- **Human sensemaker** reviews the landscape and provides direction.
- **Convergence rules** are replaced by **diversity rules** (e.g., maintain at least 3 distinct approaches).

Detailed design will be documented separately before Phase 5 begins.

---

## 11. Configuration Schema Evolution

### Context
As features are added, the configuration schema will grow. We need a strategy to manage changes without breaking existing user configs.

### Decision
- Use **semantic versioning** for the configuration schema (major.minor.patch).
- Backward‑compatible changes (adding optional fields) increase minor version.
- Breaking changes (renaming or removing fields) increase major version.
- The system will read the config and, if a schema version is specified, validate against that version. If no version is specified, assume the latest.

All configuration examples in documentation will include the schema version.

---

## 12. Error Handling and Resilience

### Context

LLM API calls can fail, rate‑limit, or time out. The system must handle these gracefully.

### Decision

- Use LiteLLM’s built‑in retry mechanism with exponential backoff for transient errors (rate limits, 5xx).
- For persistent failures, the agent is marked as `unavailable` for that round and a warning is logged.
- If too many agents become unavailable, the orchestrator pauses and alerts the user.
- All errors are logged in the event stream with full context for later analysis.

---

## Summary

These decisions form the backbone of Vörs ting’s design. They have been shaped by adversarial review and edge‑case analysis to ensure the system is robust, interpretable, and adaptable. Future design decisions should be added to this document with the same level of detail: context, options considered, and final rationale.

*Last updated: 2025‑02‑15*