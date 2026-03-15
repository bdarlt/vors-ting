# Vörs ting Glossary

Common language for the project.

## Agent Roles

### Creator
**Config role:** `creator`  
**Purpose:** Produces artifacts (documents, code, decisions)  
**Communication style:** Collaborative  
**In Socratic Sparring:** The "thesis" producer; generates initial documents and revisions

### Critic / Reviewer / Skeptic
**Config role:** `reviewer`  
**Purpose:** Stress-tests artifacts, identifies gaps and flaws  
**Communication style:** Adversarial  
**In Socratic Sparring:** The "antithesis" provider; produces substantive critiques

### Sage / Moderator
**Config role:** `moderator`  
**Purpose:** Mediates dialogue, detects pathologies, intervenes when needed  
**Communication style:** Neutral  
**In Socratic Sparring:** The broker and diagnostician; routes messages and monitors session health

### Curator
**Config role:** `curator`  
**Purpose:** Clusters and synthesizes diverse outputs  
**Used in:** Divergence mode, Moderated interaction pattern

## Key Concepts

### Socratic Sparring
A moderated, dyadic interaction pattern where a Creator and Critic engage in structured adversarial dialogue, converging on refined artifacts within 3-5 rounds. See `socratic-sparring.md`.

### Pathologies
Session dysfunctions detected by the Sage:
- **Oscillation:** A ↔ ¬A pattern (flip-flopping between positions)
- **Sycophancy:** Vacuous agreement without substantive critique
- **Semantic Drift:** Agents discussing different topics

### Interventions
Techniques the Sage uses to address pathologies:
- **Reframing:** Shifts perspective (user/market/time/scale)
- **Steel-Man:** Strengthens position before critique
- **Comparative Analysis:** Breaks binary oscillation with third option

## Interaction Patterns

### Dyadic
1 creator + 1 reviewer. Best for deep iteration on single artifact.

### Polyadic
N creators with peer-review. Best for exploring solution space.

### Parallel
N creators, no interaction. Maximum divergence.

### Layered
Review the review. Quality control on feedback.

### Moderated
N agents + 1 curator. Synthesis after exploration.

## Safeguards

### Devil's Advocate
A role assignment that forces one agent to argue against emerging consensus to prevent groupthink.

### Shadow Rubric
A fixed baseline rubric used to detect drift in the living rubric over time.

### Rejection Option
Agents can decline to proceed when information is insufficient.

## Metrics

### Regret Rate
The percentage of human overrides that were later reverted, indicating the override was incorrect.

### Dissent Impact
The percentage of dissents that resulted in meaningful changes to the final output.

### Trust Score
A weighted combination of dissent impact ratio, average dissent depth, and regret ratio.

## Artifact Types

### ADR
Architecture Decision Record. Documents significant architectural decisions.

### Process Doc
Documentation of workflows, procedures, or methodologies.

### Cursor Rules
AI-assisted development configuration files.

## Review Types

### Critique
"What's wrong or missing?" Identifies flaws, risks, gaps.

### Amplification
"What else could this become?" Extensions, applications, connections.

### Clarification
"What do you mean?" Requests for detail, assumption probes.

### Adjudication
"Which is best, and are we done?" Decision, synthesis, convergence.

## Communication Styles

### Adversarial
Direct, challenging. Best for devil's advocate, security review.

### Collaborative
Supportive, building. Best for ideation, team building.

### Neutral
Factual, observational. Best for technical documentation, audits.
