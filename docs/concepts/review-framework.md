# Vörs ting Review Framework: Quick Reference

## 1. Overview
Brief intro: "This framework defines the types of feedback agents can provide 
and the interaction patterns they use to deliver it."

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

## 4. Combination Matrix
[NEW: Shows which review types work well in which patterns]

Example:
| Review Type | Dyadic | Polyadic | Parallel | Layered | Moderated |
|-------------|--------|----------|----------|---------|-----------|
| Critique | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| Stress Test | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ |
| Comparative | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Meta-Review | ⭐ | ⭐⭐ | - | ⭐⭐⭐ | ⭐⭐ |

⭐⭐⭐ = Ideal fit
⭐⭐ = Works well
⭐ = Possible but suboptimal
- = Not applicable

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

## Alternative: Modular Approach

If you expect this to grow significantly, you could do:
```
review-framework/
├── README.md (overview + links to sections)
├── review-types.md (Table 1 + descriptions)
├── interaction-patterns.md (Table 2 + descriptions)
├── combination-guide.md (matrix + config examples)
└── decision-tree.md (flowchart for choosing)
