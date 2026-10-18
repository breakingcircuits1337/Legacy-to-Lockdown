# Bob rules — AUDIT phase
# Active in: /l2l-audit mode
# These rules are read-only constraints. No source files may be modified.

## Core constraints
- You are in READ-ONLY mode. Never write to, delete, or refactor any source file.
- Every finding must be traceable to a specific file and line number.
- Do not speculate about intent. Report only what the code demonstrably does.

## Scope of analysis
Examine the target codebase for the following dimensions:

1. SECURITY — Known vulnerability patterns:
   - Hardcoded credentials or secrets
   - Unsafe deserialization (ObjectInputStream without validation)
   - SQL string concatenation (potential injection)
   - Deprecated cryptographic algorithms (MD5, SHA1, DES)
   - Missing input validation on public API endpoints

2. COMPLEXITY — Structural debt indicators:
   - Classes exceeding 500 lines
   - Methods exceeding 50 lines or cyclomatic complexity > 10
   - Deep inheritance chains (> 4 levels)
   - Circular dependencies between packages

3. COVERAGE — Test health:
   - Identify modules with no corresponding test class
   - Flag public methods with no test coverage
   - Note presence or absence of integration tests

4. API GAPS — Modernization blockers:
   - Use of deprecated Java APIs (java.util.Date, raw Collections, etc.)
   - Direct javax.* references not migrated to jakarta.*
   - EJB 2.x or older patterns
   - Blocking I/O in hot paths

## Output
Produce a structured AUDIT_REPORT.md using the template at
`templates/AUDIT_REPORT.md`. Every section must have a severity
rating: CRITICAL / HIGH / MEDIUM / LOW / INFO.
