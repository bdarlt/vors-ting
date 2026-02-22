# Vörs ting Review Framework: Quick Reference

## 1. Overview
Brief intro: "This framework defines the types of feedback agents can provide 
and the interaction patterns they use to deliver it."

```text
Review Type (WHAT feedback)
    ↓
Interaction Pattern (HOW agents engage)
    ↓
Communication Style (TONE of delivery)
```

## 2. Review Types

Table 1: Review Types (What kind of feedback)

|Type|Core Question|Primary Output|Example Triggers|
|----|-------------|--------------|----------------|
|Critique|What's broken/missing?|Prioritized list of issues|Code review, design review|
|Stress Test|Where does this fail?|Edge cases, failure scenarios|Security audit, load testing|
|Gap Analysis|What's the delta to goal?|Missing components, roadmap|Progress review, pre-launch|
|Probing|What assumptions are hidden?|Questions that expose blindspots|Socratic dialogue, mentorship|
|Comparative|How does this relate to X?|Positioning, differentiation|Market analysis, prior art|
|Meta-Review|Is this feedback useful?|Assessment of review quality|Quality control, escalation|
|Synthesis|Which path forward?|Decision with rationale|Convergence, adjudication|

### Missing review types

Second-order implications - Downstream consequences
Constraint violations - Flags where work breaks requirements
Optimization proposals - Concrete improvements with tradeoffs
Alternative generation - Parallel versions, not just critique

### Missing output descriptions

- Format (structured rubric scores, prose, ranked list)
- Actionability (specific next steps vs. general observations)
- Scope (architectural vs. implementation-level)

### 2.1 Type Descriptions
Expand each review type with:
- When to use
- Example prompts
- Common pitfalls
- Output format expectations

## 3. Interaction Patterns  
Table 2: Interaction Patterns (How agents engage)

|Pattern|Structure|Best For|Vörs ting Mode|
|-------|---------|--------|--------------|
|Dyadic|1 creator + 1 reviewer|Deep iteration on single artifact|Build→Review→Refine loop|
|Polyadic|N creators peer-review|Exploring solution space|Multi-agent with peer feedback|
|Parallel|N creators, no interaction|Maximum divergence|Divergence mode (pre-curator)|
|Layered|Review the review|Quality control on feedback|Meta-evaluation safeguard|
|Moderated|N agents + 1 curator|Synthesis after exploration|Convergence with curator|

### 3.1 Pattern Descriptions
Expand each pattern with:
- Best use cases
- Agent count recommendations
- Typical round counts to convergence
- Vörs ting configuration snippet

## Communication Styles

Table 3: Communication Styles
|Style|Tone|Language Patterns|Best For|Avoid When|
|-----|----|-----------------|--------|----------|
|Adversarial|Direct, challenging|"This is wrong because...", "You're missing...", "This won't work..."|Devil's Advocate, security review, high-stakes|Creative brainstorming, morale-sensitive teams|
|Collaborative|Supportive, building|"What if we...", "Have you considered...", "This reminds me of..."|Ideation, team building, early exploration|Compliance, when objectivity required|
|Neutral|Factual, observational|"Observation:", "Data shows...", "Metric X is Y"|Technical documentation, audits, objective assessment|When emotional buy-in matters|

### Configuration Option Ideas

Some possible ways of incorporating communication style.

#### per Agent

Was already informally considering communication style with agent selection. Should be formalized.

```yaml
agents:
  - name: "Skeptic"
    role: "reviewer"
    model: "codex"
    communication_style: "adversarial"  # NEW
    temperature: 0.2
    
  - name: "Builder"
    role: "creator"
    model: "claude-opus"
    communication_style: "collaborative"  # NEW
    temperature: 0.7
```

#### Default Per run

```yaml
task: "Security review of authentication flow"
default_communication_style: "adversarial"  # high stakes, need harsh truth
```

#### Per Review Type

```yaml
review_types:
  critique:
    style: "adversarial"  # be harsh
  probing:
    style: "collaborative"  # be curious, not accusatory
  synthesis:
    style: "neutral"  # be objective
```

## 5. Combination Matrix
[NEW: Shows which review types work well in which patterns]

Example:
Three-Way Combination Guide

### 5.1 Critique + Dyadic + [Style]
- **Adversarial:** Classic code review, finds flaws fast, can demoralize
- **Collaborative:** Pair programming style, slower but builds skills
- **Neutral:** Technical audit, objective but may miss context

### 5.2 Probing + Polyadic + [Style]
- **Adversarial:** Hard questions expose assumptions fast
- **Collaborative:** Socratic method, educational, takes time
- **Neutral:** Survey-style, gathers data without bias

## 5. Configuration Examples
Show YAML snippets for common scenarios:
- "I want adversarial critique in dyadic mode"
- "I want comparative analysis across 5 parallel solutions"
- "I want meta-review after polyadic peer feedback"

## 6. Quick Decision Tree
Flowchart or decision table:
"I need feedback on..." → [artifact type] → [recommended review types + patterns]

## Appendices
A. Glossary of terms
B. Mapping to Vörs ting config parameters
C. Anti-patterns (common mistakes)
```

## Length Target

- **Full document:** 4-6 pages
- **Tables only (quick ref):** 1 page (can be pulled out and printed/posted)
- **With examples:** 8-10 pages

The tables should be **extractable** - someone should be able to print just sections 2 and 3 (the two tables) as a desk reference, but the full document provides the depth.

## What's Actually Missing
### From Vörs ting design:

- Triage - Classify disagreements (factual/value/semantic)
- Convergence detection - Are we done? (similarity/consensus/hybrid)
- Dependency flagging - Points out bottlenecks for downstream work
- Uncertainty quantification - Explicit confidence levels
- Completeness audit - Systematic check against spec

### From your agent conversations:

- Comparative analysis - Place work alongside similar efforts
- Reframing - Show from different perspective/discipline
- Steelman then challenge - Strongest version + where it still breaks
- Consistency mapping - Internal contradictions

### From real-world review processes:

- Security review - Threat modeling, attack vectors
- Performance review - Bottlenecks, scalability issues
- Accessibility review - WCAG compliance, usability
- Legal/compliance review - Regulatory requirements
- Cost analysis - Resource implications

## Alternative: Modular Approach

If you expect this to grow significantly, you could do:
```
review-framework/
├── README.md (overview + links to sections)
├── review-types.md (Table 1 + descriptions)
├── interaction-patterns.md (Table 2 + descriptions)
├── combination-guide.md (matrix + config examples)
└── decision-tree.md (flowchart for choosing)
