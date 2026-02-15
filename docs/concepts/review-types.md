# Review Types in Vörs ting

Purpose: Explain the different kinds of interactions (what you suggested)



---

## Quick Reference

| Type | Keyword | Core Question | Role Examples | Output |
|------|---------|---------------|---------------|--------|
| **Critique** | Adversarial | Dyadic | "What's wrong or missing?" | Skeptic, Devil's Advocate | List of flaws, risks, gaps |
| **Amplification** | Synergistic | Polyadic | "What else could this become?" | Creator, Builder | Extensions, applications, connections |
| **Clarification** | Investigative | Socratic | "What do you mean?" | Questioner, Socratic agent | Requests for detail, assumption probes, clarification |
| **Adjudication** | Decisive |Synthetic | "Which is best, and are we done?" | Moderator, Judge | Decision, synthesis, convergence declaration |

---

## Design Implications

### For Prompt Engineering
- Each role's system prompt should emphasize its primary review type
- Rubric criteria should align with expected review types
- Devil's Advocate prompt should explicitly invoke **Critique** mode
- Moderator prompt should emphasize **Adjudication** with rubric

### For Memory System
- **Dissent history** primarily captures Critique events
- **Amplification history** (future) will track synergistic contributions
- **Reasoning traces** should indicate which review type was used
- Trust score could eventually weight all three productive types (Critique, Amplification, Clarification) while penalizing unproductive agreement

### For Safeguards
- **Devil's Advocate** forces Critique mode when consensus threatens
- **Rejection option** enables Clarification when information is insufficient
- **Shadow rubric** ensures Adjudication remains aligned with gold standard
- **Disagreement triage** distinguishes which review type is needed next

---

## Common Pitfalls

| Pitfall | Manifestation | Prevention |
|---------|---------------|------------|
| **Critique without path forward** | Agent identifies flaws but offers no constructive direction | Rubric should include "actionable feedback" criterion |
| **Amplification without foundation** | Agent builds on misunderstood premise | Require explicit acknowledgment of what's being amplified |
| **Clarification loop** | Agents endlessly ask questions without progress | Limit clarification rounds; require synthesis after N rounds |
| **Premature adjudication** | Moderator declares convergence while substantive disagreements remain | Disagreement triage must run before convergence check |
| **Role confusion** | Skeptic starts amplifying instead of critiquing | Clear system prompts; memory tracks deviation patterns |

---

## Future Directions

- **Explicit review type tagging** in agent outputs (agents declare "This is a critique" or "This is amplification")
- **Review type balance metrics** (is the system over‑indexing on critique vs. amplification?)
- **Adaptive role assignment** based on which review types an agent historically excels at
- **Human review of review types** (did the agent correctly identify its own mode?)

---

This document serves as both a conceptual guide and a specification for how Vörs ting's agents should behave. When designing prompts, evaluating agent performance, or troubleshooting unexpected behavior, return here to ensure the intended interaction mode is clear.

