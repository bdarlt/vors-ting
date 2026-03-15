# Interaction Patterns

Reference documentation for Vörs ting agent interaction patterns. Describes the structural configurations for multi-agent workflows.

## Quick Reference

| Pattern | Structure | Best For | Vörs ting Mode |
|---------|-----------|----------|----------------|
| Dyadic | 1 creator + 1 reviewer | Deep iteration on single artifact | Build→Review→Refine loop |
| Polyadic | N creators peer-review | Exploring solution space | Multi-agent with peer feedback |
| Parallel | N creators, no interaction | Maximum divergence | Divergence mode (pre-curator) |
| Layered | Review the review | Quality control on feedback | Meta-evaluation safeguard |
| Moderated | N agents + 1 curator | Synthesis after exploration | Convergence with curator |

---

## Pattern Specifications

### Dyadic

**Structure**: One creator agent paired with one reviewer agent.

**Configuration**:
- Minimum agents: 2
- Agent roles: 1 creator, 1 reviewer
- Interaction: Bidirectional feedback loop

**Vörs ting Mode**: `converge`

**Typical Round Count**: 3-5 rounds

**Parameters**:
```yaml
mode: converge
agents:
  - name: Creator
    role: creator
  - name: Reviewer
    role: reviewer
rounds: 5
```

---

### Polyadic

**Structure**: Multiple creator agents with peer-to-peer review capability.

**Configuration**:
- Minimum agents: 3
- Agent roles: 2+ creators, 0+ reviewers (peer review)
- Interaction: Mesh network (each agent can review others)

**Vörs ting Mode**: `converge` or `diverge`

**Typical Round Count**: 2-4 rounds

**Parameters**:
```yaml
mode: converge
agents:
  - name: CreatorA
    role: creator
  - name: CreatorB
    role: creator
  - name: CreatorC
    role: creator
rounds: 3
```

---

### Parallel

**Structure**: Multiple independent creator agents with no inter-agent communication.

**Configuration**:
- Minimum agents: 2
- Agent roles: N creators
- Interaction: None (isolated execution)

**Vörs ting Mode**: `diverge`

**Typical Round Count**: 1 round (single generation)

**Parameters**:
```yaml
mode: diverge
agents:
  - name: CreatorA
    role: creator
  - name: CreatorB
    role: creator
  - name: CreatorC
    role: creator
rounds: 1
```

---

### Layered

**Structure**: A meta-review layer that evaluates the quality of feedback from other reviewers.

**Configuration**:
- Minimum agents: 3
- Agent roles: 1+ creators, 1+ primary reviewers, 1 meta-reviewer
- Interaction: Hierarchical (meta-reviewer evaluates reviewer output)

**Vörs ting Mode**: `converge`

**Typical Round Count**: 2-3 rounds per layer

**Parameters**:
```yaml
mode: converge
agents:
  - name: Creator
    role: creator
  - name: PrimaryReviewer
    role: reviewer
  - name: MetaReviewer
    role: reviewer
rounds: 3
```

---

### Moderated

**Structure**: Multiple agents with a designated curator agent responsible for synthesis and convergence decisions.

**Configuration**:
- Minimum agents: 3
- Agent roles: 1+ creators, 0+ reviewers, 1 curator
- Interaction: Star topology (curator at center)

**Vörs ting Mode**: `converge`

**Typical Round Count**: 2-4 rounds

**Parameters**:
```yaml
mode: converge
agents:
  - name: CreatorA
    role: creator
  - name: CreatorB
    role: creator
  - name: Curator
    role: curator
rounds: 3
```

---

## Pattern Comparison

| Attribute | Dyadic | Polyadic | Parallel | Layered | Moderated |
|-----------|--------|----------|----------|---------|-----------|
| Min Agents | 2 | 3 | 2 | 3 | 3 |
| Max Agents | 2 | Unlimited | Unlimited | Unlimited | Unlimited |
| Communication | Bidirectional | Mesh | None | Hierarchical | Star |
| Convergence Speed | Medium | Slow | N/A | Slow | Fast |
| Divergence Potential | Low | Medium | High | Low | Low |
| Use Case | Iteration | Exploration | Generation | Quality Control | Synthesis |

---

## Mode Mapping

| Mode | Compatible Patterns |
|------|---------------------|
| `converge` | Dyadic, Polyadic, Layered, Moderated |
| `diverge` | Polyadic, Parallel |

---

## Agent Role Compatibility

| Pattern | Creator | Reviewer | Curator |
|---------|---------|----------|---------|
| Dyadic | Required (1) | Required (1) | Not used |
| Polyadic | Required (2+) | Optional | Not used |
| Parallel | Required (2+) | Not used | Not used |
| Layered | Required (1+) | Required (1+) | Not used |
| Moderated | Required (1+) | Optional | Required (1) |
