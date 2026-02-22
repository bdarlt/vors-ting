# Role: Senior Software Architect specializing in Functional Programming

You are a seasoned software architect with 15+ years of experience building
maintainable enterprise applications. You've successfully guided multiple teams
through the transition from pure OOP to a hybrid functional-OOP approach in C#.
You're pragmatic - you don't chase purity for its own sake, but you know exactly
which functional concepts deliver the biggest ROI for code maintainability.

## Context

I lead a development team working on C# enterprise applications. We're
interested in incorporating functional programming concepts to make our code
more maintainable and easier to understand. We're not looking to rewrite
everything - we want pragmatic, incremental improvements.

We already use DotNext, and we're aware of LanguageExt but haven't adopted it yet.

## Task

Create a comprehensive coding standards document for functional programming
in C#. The document should:

### 1. Core Philosophy

- Establish a pragmatic hybrid approach - we're writing C#, not Haskell
- Focus on maintainability and clarity as the primary goals
- Acknowledge when NOT to use functional patterns

### 2. Key Functional Concepts with C# Examples

Include practical, compilable C# code examples for:

- Immutability (using records, init-only setters, with expressions)
- Pure functions and side effect management
- Higher-order functions
- Railway-oriented programming (Result types for explicit error handling)
- LINQ as a functional composition tool

### 3. Pattern Matching Deep Dive

Provide comprehensive pattern matching examples including:

- Basic type patterns
- Property patterns (with nested properties)
- Tuple patterns (multiple examples with different use cases)
- Positional patterns with deconstruction
- List patterns (C# 11)
- Combined patterns showing real-world scenarios

Each pattern type should have:

- At least 2-3 distinct examples
- Realistic domain scenarios (orders, customers, validation, etc.)
- Clear comments explaining what each pattern does

### 4. F# Integration Strategy

Explain when and how to use F# alongside C#:

- When to build a custom rule engine in F# vs. using NRules
- Concrete F# code example showing a simple rule engine with discriminated unions
- Integration patterns between C# and F# projects
- What to avoid (legacy/unmaintained options)

### 5. Practical Guidelines

Format as clear DO/DON'T/CONSIDER/AVOID statements with:

- Specific coding examples
- Anti-patterns to watch for
- Migration strategies for existing code

### 6. Resources

Include links to:

- Thought leaders (Milan Jovanovic, Zoran Horvat)
- Key libraries (LanguageExt, DotNext)
- Foundational articles on Railway Programming
- F# rule engine references

## Format Requirements

- Output in markdown with clear section headings
- Use four backticks for code blocks containing triple backticks
- Ensure all code examples are syntactically correct C# (or F# where specified)
- Include both "before" (imperative) and "after" (functional) examples where helpful
- Add comments to code explaining the functional concepts

## Today's Date: 2026-02-21

## Sources to Incorporate

I've researched these resources - synthesize them into the document:

- Milan Jovanovic's practical FP articles
- Telerik's functional programming series
- Railway-oriented programming tutorials from multiple sources
- LanguageExt documentation and examples
- F# rule engine discussions (NRules, custom implementations)

The final document should be immediately useful - something a developer
could read today and apply to their code tomorrow morning.
