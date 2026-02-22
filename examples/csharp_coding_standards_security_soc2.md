Create security-focused C# coding standards that support SOC 2 compliance.

Cover each SOC 2 trust principle with concrete coding practices:
- **Security**: Authentication, authorization, input validation, secure defaults
- **Availability**: Health checks, resilience, graceful degradation
- **Processing Integrity**: Validation, transactions, idempotency, audit trails
- **Confidentiality**: Encryption, access controls, data classification
- **Privacy**: Consent, data minimization, retention, deletion

For each area include:
- Code examples (C#) showing compliant implementation
- Anti-patterns to avoid
- Specific SOC 2 control references where applicable (CC6.1, CC7.2, etc.)

Also include:
- Secrets management (NEVER hardcode secrets)
- Audit logging requirements (1-year retention, immutable)
- GitHub security settings (branch protection, CODEOWNERS, secret scanning)
- API security standards

Format with clear headings and practical examples. Team uses .NET 8, ASP.NET Core, EF Core, Azure, GitHub.