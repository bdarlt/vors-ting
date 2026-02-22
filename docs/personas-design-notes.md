# Persona Design Notes for Vörs ting

Research and design exploration for a composable persona system for LLM agents.

---

## What We've Learned

### Persona vs. Task vs. Format

Three separate concerns emerged from exploration:

| Concern | Purpose | Example |
|---------|---------|---------|
| **Persona** | Who the agent is — identity, voice, behavioral tendencies | "Senior C# architect, direct, trusts working code" |
| **Task** | What to do right now | "Create coding standards for async/await" |
| **Format** | How to structure output | "DO/DON'T examples, max 5 lines per block" |

These should be **independent knobs**, not conflated in a single "system prompt."

### From QCRI Taxonomy (Useful Elements)

The [QCRI persona elements framework](https://persona.qcri.org/blog/elements-of-a-persona-profile/) provides a decent starting inventory:

- **Archetype** — base behavioral template (e.g., "Senior Architect", "Security Champion")
- **Personality/Defining Traits** — behavioral tendencies
- **Psychographics** — motivation, values, pain points (steers reasoning priorities)
- **Skills/Expertise** — capability boundaries
- **Quotes/Bio** — few-shot examples for voice capture

### From Method Acting / UX Matters

The [UX Matters article](https://www.uxmatters.com/mt/archives/2009/09/whats-my-persona-developing-a-deep-and-dimensioned-character.php) applies Stanislavski's Method Acting to persona development. Key insights:

**Three Dimensions of Character:**

| Dimension | Description | LLM Application |
|-----------|-------------|-----------------|
| **Psychology** | Mental models, emotional states, thought patterns | Reasoning style, priorities, skepticism |
| **Sociology** | Social context, relationships, cultural factors | How agent relates to user/other agents |
| **Physiology** | How physical state affects behavior | *(Less relevant for text-based agents)* |

**Key Distinction:**
- **Archetype** — abstract template (e.g., "The Skeptic") — *lifeless, academic*
- **Embodied Persona** — specific configuration with internal consistency — *dynamic, situated*

> *"The persona isn't a mask applied to outputs—it's an internal model that shapes how the agent processes and responds."*

**Anti-patterns to avoid:**
- Stereotypes (shallow mental pictures)
- Idealized worlds (personas that never fail or face friction)
- Irrelevant details (fluff that doesn't drive behavior)

### From BuildUX Polar Behaviors

The [BuildUX article](https://buildux.com/blog/exploring-persona-attributes-an-exhaustive-list-to-guide-you) provides **~85 polar behavior pairs** (gradient spectrums) organized into categories. These are highly composable for LLM agents.

### From HuggyMonkey 11-Part Series

The [HuggyMonkey series](https://medium.com/@HuggyMonkey/chatbots-persona-series-taking-your-ai-assistant-from-bland-to-unforgettable-a77e01145643) is a comprehensive guide to chatbot persona design. Key insights from across the series:

#### Part 1: Why Personas Matter — The "Helpful Assistant" Problem

> *"You are a helpful assistant" leads to bland, inconsistent, forgettable bots.*

The anti-pattern: vague prompts that produce "ChatGPT with a sticker slapped on." Personas impact clarity, trust, and engagement.

#### Part 2: Defining the Role — The Foundation

**Role = Job Description** with 4 components:
1. **Domain** — area of expertise
2. **Perspective** — teacher/peer/critic/cheerleader
3. **Level of authority** — junior/senior, friendly/authoritative
4. **Primary task** — reviewing/coaching/answering/brainstorming

Role comes *first* before tone or personality. A strong role limits drift.

**Template:**
```
You are a [seniority/role] who helps [target audience] with [primary task] 
in the domain of [domain/expertise]. You do this by [key behaviors/tone traits], 
and you always [key value/principle].
```

#### Part 3: Tone of Voice — The Expression Layer

**Tone dimensions (spectrums):**
- Formal ↔ Informal
- Warm ↔ Cold
- Serious ↔ Fun
- Precise ↔ Casual

Same role (e.g., "career coach") can have different tones (warm/encouraging vs. blunt/direct).

#### Part 4: Personality Traits — Dimensional Design

See earlier section. Key insight: **Tone ≠ Personality**
- Tone = *how* things are said (output style)
- Personality = *what* the bot does (behavioral tendencies)

**The "Shapeshifter Problem":** Without clear traits, bots feel like someone new in every message.

#### Part 5: Background Story — The Motivation Layer

The backstory provides the "why" behind behaviors. It doesn't need to be shared with users — it's for internal consistency.

**Template:**
```
You are a [role] created to [mission]. 
You were designed by [group] and shaped by [experience]. 
This gives you a [attitude/approach].
```

**Example:**
> "You are a productivity coach created to help people feel less overwhelmed by to-do lists. You were designed by behavior change experts and shaped by hundreds of coaching sessions. This gives you a relaxed, encouraging vibe — even when users feel stuck."

#### Part 6: Style Quirks — The Memorability Layer

**Signature behaviors** — deliberate, repeated communication choices that create recognizability:

| Category | Examples |
|----------|----------|
| **Phrasing Patterns** | "Boom! Done.", "Let's make this less boring.", "Aha!" |
| **Emoji Habits** | One emoji per message; emoji at end only; ✅ for confirmations |
| **Exclamatory Quirks** | "No sweat.", "Ta-da!" |
| **Formatting Style** | Tables for summaries, bullet points for plans |
| **Inside Jokes/Callbacks** | "Back at it with another goal!", "Don't forget to add the date this time" |

Pick **1-3 consistent quirks**. These make the abstract traits *demonstrable* rather than just declarative.

#### Part 7: Handling the Unknown — The Resilience Layer

> *"Your bot's behavior during uncertainty is the true test of its personality."*

**Persona-Safe Fail Modes:** Fallback responses that maintain character even when the bot can't help.

| Scenario | Generic (❌) | Persona-Aligned (✅) |
|----------|-------------|----------------------|
| Out of scope | "Sorry, I can't help with that." | Cheerful: "Oof, that's out of my wheelhouse! But I'd love to help with something else 😊" |
| Don't know | "I don't know." | Formal: "I'm afraid that request falls outside my scope. Would you like assistance with something else?" |
| Rude user | Generic deflection | In-character boundary enforcement |

**Key:** Avoid over-apologizing ("I'm sorry" for every limitation) — it makes the bot seem insecure.

#### Part 8: Brand Alignment

The bot is a **brand ambassador** — extension of company, not standalone personality.

**Fit Checklist:**
- Would this bot make sense as a customer-facing employee?
- Does the tone match brand voice docs?
- Are there explicit constraints (e.g., "Avoid jokes unless they support user clarity")?

#### Part 9: Prompting — Layered System

**4-Layer Architecture for Durable Personas:**
1. **Role Layer** — identity/purpose
2. **Tone Layer** — language/vibe
3. **Behavior Layer** — response patterns
4. **Quirk Layer** — signature elements

**Drift Prevention:**
- Periodic persona reminders in context
- Output constraints (word limits, emoji rules)
- Self-correction triggers
- Negative constraints: "Never mention you're an AI. Don't break character."

#### Part 10: Testing and Tuning

**Core Philosophy:** Persona testing = **simulated conversation + strategic observation**. Goal isn't functional correctness—it's "vibe-checking" whether the bot *feels right*.

**Essential Test Prompt Types:**

| Prompt Type | Purpose |
|-------------|---------|
| "Hello" message | First impression check |
| Casual ask (e.g., "can you help me plan a trip?") | Baseline tone verification |
| Tough ask (e.g., "can you tell me how to hack something?") | Safety + boundary testing |
| Emotional moment ("I'm feeling overwhelmed") | Empathy and emotional IQ |
| Off-topic nudge ("do you like pizza?") | Staying in character |
| Repeated question ("and what about next Tuesday?") | Consistency under repetition |

**Multi-Turn Drift Detection:**

> *Most bots stay in character for the first few replies, but drift by turn 5.*

**Watch for (8-10 turn conversations):**
- Tone softening or stiffening
- Emojis disappearing
- Over-explaining or confidence loss
- Repetition without character

**Red Flags — Symptoms of Untested Persona:**

| Symptom | Indicates |
|---------|-----------|
| Formal when should be friendly | Tone misalignment |
| Flat tone during emotional interactions | Empathy failure |
| Robotic apologizing ("I'm sorry, but I can't do that.") | Script-like responses |
| Losing voice after back-and-forths | **Persona drift** |

#### Part 11: The Quick Guide — 5-Component Model

**The Trinity + 2:**
```
Role → Tone → Traits/Behaviors → Quirks → Backstory
(⚠️ required)    (optional layers)
```

**Copy-Pasteable Persona Sheet:**
```
You are [name], a [tone + role]. You [backstory/purpose].
You always: [behaviors]
Avoid: [undesired behaviors]
Example phrases: [2-3 samples]
Example completions for edge cases: [apologizing, clarifying, handling feedback]
```

**Testing:** Read 5-10 multi-turn chats aloud; check for tone shifts during errors, long conversations, repetitive answers.

---

## Synthesis: Composable Persona Architecture

Based on all sources, here's a unified layered model:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 7: FALLBACK/EDGE HANDLING                            │
│  ├── Persona-safe fail modes                                │
│  ├── Boundary maintenance                                   │
│  └── Uncertainty behavior                                   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 6: STYLE SIGNATURE (Quirks)                          │
│  ├── Phrasing patterns                                      │
│  ├── Emoji/formatting rules                                 │
│  └── Catchphrases & callbacks                               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: BACKSTORY (Motivation)                            │
│  ├── Purpose (why you exist)                                │
│  ├── Origin (who designed you, what shaped you)             │
│  └── Resulting attitude                                     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: PERSONALITY (Traits)                              │
│  ├── Dimensional sliders (curiosity, playfulness, empathy)  │
│  └── Polar pairs (methodical↔spontaneous, etc.)             │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: TONE                                              │
│  ├── Formality (formal↔casual↔direct)                       │
│  ├── Energy (enthusiastic↔measured↔calm)                    │
│  └── Temperature (warm↔cold)                                │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: ROLE (Foundation)                                 │
│  ├── Domain expertise                                       │
│  ├── Perspective (teacher/peer/critic)                      │
│  ├── Authority level (junior↔senior)                        │
│  └── Primary task                                           │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: IDENTITY                                          │
│  ├── Archetype                                              │
│  ├── Background/experience                                  │
│  └── Relationship to user                                   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: CAPABILITY & BOUNDARIES                           │
│  ├── Expertise domains                                      │
│  ├── Blind spots                                            │
│  └── Hard constraints (refusals)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## What We Think We Need

### Required Components

1. **Identity** — archetype, background, role
2. **Role Definition** — domain, perspective, authority, task (the foundation)
3. **Tone** — output style (formal, casual, direct)
4. **Personality** — behavioral tendencies via dimensional sliders
5. **Backstory** — motivation layer (purpose, origin, attitude)
6. **Style Quirks** — signature behaviors for memorability
7. **Cognitive** — reasoning style, priorities, risk tolerance
8. **Capability** — expertise domains, blind spots
9. **Boundaries** — refusals, constraints
10. **Fallback** — persona-safe behavior for edge cases

### Composition Rules

- **Role comes first** — foundation that limits drift
- Components should be **additive** — `identity` + `behavioral` = consistent character
- **Dimensional traits** as gradients (0.0-1.0) allow fine-tuning and interpolation
- Need **override mechanisms** — specific task may need "be more verbose than usual"
- Format should be **separate** from persona

### Validation Needs

- Detect conflicts (e.g., "terse" + "exhaustive explanations")
- **Dramaturgical testing** — run through scenarios to check behavioral consistency
- **Fallback testing** — verify persona survives edge cases (confusion, rudeness, off-topic)
- Ensure consistency across long conversations

---

## What We Think We Don't Need

### Marketing Persona Bloat

From UX persona research — elements irrelevant for LLM agents:

- Demographics (age, location, salary, relationship status, ethnicity, religion)
- Consumption preferences (favorite apps, brands, channels, loyalty programs)
- Photo/avatar (unless for UI display)
- Work experience details unless relevant to expertise
- Physical context (climate, urban/rural, homeownership)

### Mechanistic Control

The "persona vectors" approach (steering model activations) is interesting but **overkill** for this use case. We're designing a prompt-engineering framework, not doing mechanistic interpretability research.

### Implicit Traits

Don't infer personality from demographics (e.g., "Gen Z = casual"). Be explicit about behavioral traits.

---

## Open Questions

1. **How many layers is too many?** Is 10-component composition usable or unwieldy?
2. **Can we auto-detect conflicts?** e.g., "terse" voice + "comprehensive" format request
3. **Should archetypes be predefined or user-defined?**
4. **How do we handle persona drift across long feedback loops?**
5. **Should polar pairs be normalized (0-1) or categorical (enum)?**
6. **Is Tone separate from Personality?** HuggyMonkey suggests yes, but is this distinction useful in practice?
7. **How do we validate "style quirks" don't become annoying?**

---

## References

| Source | URL | Helpfulness | Notes |
|--------|-----|-------------|-------|
| QCRI — Elements of a Persona Profile | https://persona.qcri.org/blog/elements-of-a-persona-profile/ | ✅ **Useful** | Good taxonomy of persona elements. Useful: Archetype, Personality, Skills, Psychographics. Missing: Interaction style, reasoning patterns, composition rules. |
| Interaction Design — AI for Personas | https://www.interaction-design.org/literature/article/ai-for-personas | ❌ **Not helpful** | About UX user personas (customer research), not agent personas. No composability discussion. |
| arXiv — Persona Vectors | https://arxiv.org/pdf/2507.21509 | ❌ **Not helpful** | Mechanistic interpretability research (steering model activations). No persona structure taxonomy. Wrong abstraction level. |
| UX Matters — Developing a Deep Character | https://www.uxmatters.com/mt/archives/2009/09/whats-my-persona-developing-a-deep-and-dimensioned-character.php | ✅ **Useful** | Method Acting approach. Key insights: 3 dimensions (psychology/sociology/physiology), archetype vs embodied persona, cause-and-effect rhythm. Anti-patterns: stereotypes, idealized worlds. |
| BuildUX — Persona Attributes | https://buildux.com/blog/exploring-persona-attributes-an-exhaustive-list-to-guide-you | ✅ **Useful** | Exhaustive list of ~85 polar behavior pairs. Highly composable as gradient spectrums. Extract ~35 core dimensions for agent use. Rest is marketing/UX bloat. |
| HuggyMonkey — Chatbot Persona Series | https://medium.com/@HuggyMonkey/chatbots-persona-series-taking-your-ai-assistant-from-bland-to-unforgettable-a77e01145643 | ✅ **Very Useful** | Comprehensive 11-part series. Key contributions: 5-Component Model, Role-as-foundation, Tone≠Personality, Style Quirks, Persona-Safe Fail Modes, Layered Prompting, Testing Framework (drift detection by turn 5), Drift Prevention. |

---

## Draft YAML Structure (Experimental)

```yaml
personas:
  senior_architect:
    identity:
      archetype: "Senior Software Architect"
      background: |
        15+ years shipping production C#. Seen migrations fail, databases corrupt, 
        3am pages. Trusts working code over perfect theory.
    
    role:  # Foundation layer (HuggyMonkey Part 2)
      domain: "software_architecture"
      perspective: "critic"  # teacher/peer/critic/cheerleader
      authority: "senior"     # junior/senior
      primary_task: "review_and_guide"
    
    tone:  # Expression layer (HuggyMonkey Part 3)
      formality: "direct"     # formal/casual/direct
      energy: "measured"      # enthusiastic/measured/calm
      warmth: 0.3             # warm (0) ↔ cold (1)
    
    personality:  # Dimensional traits (HuggyMonkey Part 4)
      curiosity: 0.3          # curious ↔ reserved
      playfulness: 0.2        # playful ↔ serious
      empathy: 0.4            # empathetic ↔ clinical
    
    backstory:  # Motivation layer (HuggyMonkey Part 5)
      purpose: "help teams write maintainable code that survives production"
      designed_by: "pragmatic engineers who've been paged at 3am"
      shaped_by: "years of refactoring nightmares and failed migrations"
      attitude: "relaxed but rigorous — encouraging but won't let shortcuts slide"
    
    quirks:  # Memorability layer (HuggyMonkey Part 6)
      phrasing_patterns:
        - "Here's the thing..."
        - "Don't do this. Do this instead."
      emoji_habit: "none"  # or "end_of_message", "for_confirmations"
      formatting_rules:
        - "DO/DON'T tables for every rule"
        - "Bullet points for action items"
    
    behavioral:
      communication:
        detail_orientation: 0.8   # detail-oriented (vs big-picture)
        directness: 0.9            # blunt (vs diplomatic)
        expressiveness: 0.4        # reserved (vs expressive)
    
    cognitive:
      reasoning: "analytical"
      priorities: ["correctness", "maintainability", "performance"]
      risk_tolerance: 0.2          # risk-averse
      skepticism: 0.8              # questions assumptions
    
    capability:
      domains: ["csharp", "dotnet", "cloud_architecture"]
      stack_context: ".NET 10, Aspire, Cosmos DB, Event Grid"
      blind_spots: ["frontend css", "mobile dev"]
    
    boundaries:
      refuses: 
        - "skip error handling"
        - "recommend deprecated patterns"
    
    fallback:  # Resilience layer (HuggyMonkey Part 7)
      when_uncertain: "ask_clarifying_questions"
      when_out_of_domain: "acknowledge_limitations"
      when_rude_user: "maintain_boundaries_calmy"
      tone_under_pressure: "maintain"
      example_responses:
        out_of_scope: "That's outside my wheelhouse — I focus on C# architecture. Want help with something in that space?"

# Usage
agents:
  - name: "PragmaticCoder"
    role: creator
    persona: senior_architect
    format: dodont  # separate from persona!
```

---

*Last updated: 2026-02-22*
*Updates: Full HuggyMonkey 11-part series synthesis (including Part 10 testing framework), added role/backstory/quirks/fallback layers, 10-component architecture*
*Status: Exploration phase — not implemented*
