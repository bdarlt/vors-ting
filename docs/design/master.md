# Multi‑Agent Critical Feedback Scaffolding: Master Design Document

## 1. Introduction

This document describes a Python‑based scaffolding system that automates iterative multi‑agent feedback loops to improve work products such as ADRs, unit tests, process documentation, and AI‑assisted development artifacts. The system supports two primary interaction patterns:

- **Dyadic (creator + skeptic)** – two agents with distinct roles engage in iterative refinement.
- **Polyadic (multiple creators)** – several agents (possibly using different LLMs) generate independent versions, critique each other, and refine until convergence.

The core iterative cycle is **generate → critique → refine → repeat**, with feedback aggregated in a structured format. The design incorporates principles from the **Agentic Design Skill** document: minimalist safeguards, robust metrics, and anti‑fragile learning via a persistent agent memory system.

This document provides a high‑level overview; detailed specifications for the agent memory can be found in the separate [Agent Memory System Design](agent_memory.md).

## 2. System Goals

- **Automate** the manual workflows you described.
- **Support both interaction patterns** with a single, configurable orchestrator.
- **Integrate multiple LLM providers** (Anthropic, OpenAI, Mistral, Google Gemini, DeepSeek, etc.) via LiteLLM.
- **Persist all rounds** (artifacts, feedback, reasoning traces, metrics) to disk for inspection, debugging, and resume capability.
- **Inject domain‑specific “skills”** and **structured rubrics** without changing the core scaffolding.
- **Detect convergence** using configurable strategies (consensus, similarity, max rounds) with **disagreement triage** to reduce false escalations.
- **Implement minimalist safeguards** (Devil’s Advocate, shadow rubric, rejection option) to prevent sycophancy, groupthink, and drift.
- **Track metrics** (regret rate, dissent impact, time‑to‑convergence) to measure whether structure helps.
- **Support divergence mode** for brainstorming and exploration, with a curator agent and human sensemaking.
- **Enable anti‑fragile learning** via a persistent agent memory that tracks performance and adapts trust scores (detailed in the separate memory document).

## 3. High‑Level Architecture

```
┌─────────────────┐
│     User CLI    │
└────────┬────────┘
         │  provide config
         ▼
┌─────────────────────────────────┐
│          Orchestrator            │
│  (main loop, round management)   │
└────────┬──────────────┬──────────┘
         │               │
         ▼               ▼
┌─────────────────┐  ┌─────────────────┐
│   Agent Pool    │  │   File System   │
│ (role‑specific  │  │ (round storage, │
│   wrappers)     │  │  agent memory)  │
└────────┬────────┘  └─────────────────┘
         │                    ▲
         ▼                    │
┌─────────────────┐            │
│    LiteLLM      │            │
│ (unified API)   │            │
└─────────────────┘            │
         │                    │
         └────────────────────┘
         (feedback/versions passed)
         ▼
┌─────────────────┐
│  Convergence    │
│   Detector      │  (with triage, devil's advocate)
└─────────────────┘
         ▼
┌─────────────────┐
│ Metrics Logger  │  (regret, dissent, etc.)
└─────────────────┘
```

### 3.1 Core Components

- **Configuration** (YAML/JSON): Defines the task, agents, rubric, safeguards, convergence method, divergence settings, and skill prompts. (See Section 4 for schema.)
- **Agent Abstraction**: Wraps an LLM with role‑specific system prompts (creator, reviewer, curator). Includes methods `generate()`, `review()`, `refine()`, and optional `reject()`. Each agent has access to its persistent memory (see memory document).
- **Orchestrator**: Manages the round loop, calls agents, aggregates feedback, invokes convergence detection, logs metrics, and handles mode switching (converge/diverge).
- **Feedback Aggregator**: Combines individual feedback reports (with rubric scores if provided) into a single document with clear section headers.
- **Convergence Detector**: Implements configurable methods (consensus, similarity, hybrid) and performs disagreement triage (factual/value/semantic). Also manages the Devil’s Advocate safeguard.
- **Metrics Logger**: Tracks per‑run and cumulative metrics (regret rate, dissent impact, time‑to‑convergence, escalation usefulness). Outputs to JSON/CSV for analysis.
- **Agent Memory System**: Persistent storage per agent of dissent history, override history, trust scores, and long‑term statistics. Enables anti‑fragile learning. Fully detailed in the [separate document](agent_memory.md).

## 4. Configuration Schema

Below is an example configuration with all key sections. For detailed explanations of each field, refer to the in‑line comments.

```yaml
task: "Write an ADR for migrating from REST to GraphQL"
artifact_type: "adr"
agents:
  - name: "Creator1"
    role: "creator"
    model: "claude-3-opus-20240229"
    provider: "anthropic"
    temperature: 0.2
  - name: "Skeptic"
    role: "reviewer"
    model: "gemini-1.5-pro"
    provider: "google"
  - name: "Creator2"
    role: "creator"
    model: "mistral-large-latest"
    provider: "mistral"

rounds: 5
mode: "converge"  # or "diverge"

# Rubric for evaluation (used by reviewers and convergence)
rubric:
  criteria:
    - name: "Accuracy"
      weight: 0.4
      guidelines: "Check facts against known sources; no hallucinations."
    - name: "Clarity"
      weight: 0.3
      guidelines: "Is it understandable to a non-expert?"
    - name: "Completeness"
      weight: 0.3
      guidelines: "Does it address all aspects of the task?"
  living: true                     # enable shadow comparison
  shadow_path: "rubric_gold.yaml"  # fixed baseline for drift detection

# Convergence settings
convergence:
  method: "consensus"  # or "similarity" or "hybrid"
  similarity_threshold: 0.95
  max_rounds: 5
  triage: true         # classify disagreements (factual/value/semantic)

# Safeguards
safeguards:
  devil_advocate:
    enabled: true
    rotation: "random_per_round"   # or "fixed_agent"
    skip_rate: 0.1                 # 10% of rounds with no DA
    impact_threshold: 0.1           # alert if dissent impact <10%
  rejection_option: true            # agents can say "insufficient information"
  shadow_rubric:
    enabled: true
    check_frequency: 3              # compare every 3 rounds or after each human override

# Metrics
metrics:
  log_dir: "metrics/"
  regret_tracking: true
  dissent_impact: true
  escalation_usefulness: true

# Divergence mode settings (used when mode: "diverge")
divergence:
  min_clusters: 3
  clustering_method: "embedding"   # or "keyword"
  curator_model: "gpt-4-turbo"
  human_sensemaker: true            # pause for human review after clustering

# Skill prompts (domain expertise)
skill_prompts:
  adr: "You are an expert software architect. Follow the ADR template: Title, Status, Context, Decision, Consequences."
```

## 5. Orchestration Flow

### 5.1 Dyadic Pattern (Creator + Skeptic)
1. **Round 0**: Creator generates initial artifact + reasoning trace. Saved.
2. **Round 1**:
   - (Optional) Devil’s Advocate assigned to Skeptic.
   - Skeptic reviews artifact using rubric, provides scores and feedback.
   - Aggregator creates report.
   - Creator refines using report + trace.
   - Metrics logged.
3. **Convergence check**: If not converged, repeat.
   - After N rounds without convergence, triage disagreement and possibly escalate.

### 5.2 Polyadic Pattern (Multiple Creators)
1. **Round 0**: All creators generate versions + traces.
2. **Round 1**:
   - Each creator reviews all others (peer review) using rubric.
   - Aggregator compiles all feedback into one report.
   - (Optional) Devil’s Advocate role rotates among creators.
   - Each creator refines own version.
3. **Convergence check**: Compare versions (similarity) or ask moderator for consensus.
4. Repeat.

### 5.3 Divergence Mode
1. **Round 0**: Creators generate diverse solutions + traces.
2. **Round 1**:
   - Peer review focuses on identifying differences, not scoring.
   - Curator clusters ideas (embedding similarity) and highlights disagreements.
   - Human sensemaker reviews landscape, provides direction.
   - If more divergence needed, Curator guides next round.
   - When sensemaking complete, human synthesizes or selects top options.

## 6. Integration with Agent Memory System

The orchestrator interacts with the memory system as follows:
- At startup, loads each agent’s memory (or creates a new one).
- After each round, logs dissents, overrides, and other events to memory.
- Uses memory data to:
  - Filter candidates for Devil’s Advocate based on trust scores.
  - Adjust trust scores based on outcomes.
  - Compute metrics (dissent impact, regret rate, etc.).

All memory operations are handled through the `AgentMemory` class, whose full specification is in the separate [Agent Memory System Design](agent_memory.md).

## 7. Implementation Phases

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| 1 | Core Infrastructure | Config loader, basic `Agent` class, file persistence. |
| 2 | Basic Orchestration | Orchestrator with dyadic/polyadic loops, feedback aggregation, `refine()`. |
| 3 | Convergence & Safeguards | Convergence detector, triage, Devil’s Advocate, shadow rubric, metrics logging. |
| 4 | Agent Memory System | `AgentMemory` class, trust score calculation, dissent depth, memory decay, probation. |
| 5 | Divergence Mode | Curator agent, clustering, human sensemaker interface. |
| 6 | Metrics Dashboard & Polish | HTML reports, cost tracking, error handling, documentation. |
| 7 | Hostile Actor Stress Test | Simulation harness, validation of defenses. |

