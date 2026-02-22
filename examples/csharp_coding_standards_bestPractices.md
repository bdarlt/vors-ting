Create practical C# coding standards focused on maintainability, readability, and testability. 

Cover these areas with DO/DON'T examples:
- Naming conventions (classes, methods, variables, booleans)
- Class design (SRP, constructors, properties, dependency injection)
- Method design (length, parameters, guard clauses)
- Exception handling (when to throw, custom exceptions, logging)
- Code organization (file layout, regions, project structure)
- Comments (when useful, XML docs, self-documenting code)

Include these patterns with examples:

- Guard clauses
- Factory
- Builder
- Strategy
- Repository
- Options
- Materialized View
- Transactional Outbox
- Circuit Breaker
- Bulkhead
- Event Sourcing
- Retry Pattern
- Facade Pattern
- Observer Pattern
- Command Pattern
- Singleton Pattern

Include these anti-patterns to avoid:
- Primitive obsession, God classes, Feature envy, Temporal coupling

Format with clear headings and code examples showing bad vs. good. Keep it
practical - assume readers know C# basics but want to level up their code quality.

Team uses .NET 10, Dot Next, OpenTelemetry, Cosmos DB, Event Grid

- In Container App: .Net Aspire, ASP.NET Core (minimal api)
- In Function App: .Net 10
- For Testing:  xUnit v3, Shouldly, Moq, iLogger-Moq, fsCheck
