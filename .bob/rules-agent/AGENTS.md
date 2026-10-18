# AGENTS.md — Coding Rules (Non-Obvious Only)

This file provides guidance to agents when working with code in this repository.

## Critical Coding Gates
- **TRANSFORM gate**: `L2L_CONTRACTS.md` must have an entry for the module before editing any source file. No contract = refuse to edit.
- **VERIFY gate**: `[Module]ContractTest.java` must pass before moving to the next module. A test failure goes in `AUDIT_REPORT.md` under "Contract Violations" — do not silently fix.
- **AUDIT mode**: only `AUDIT_REPORT.md` is writable. The `l2l-audit` custom mode enforces this via `fileRegex: "AUDIT_REPORT\.md$"`.
- **VERIFY mode**: only files matching `.*VerifyTest\.java$|CHANGE_LEDGER\.md$|AUDIT_REPORT\.md$` are writable.

## Commit Format — Parsed by `ledger.py`
Every staged file must use this commit subject (em-dash `—`, not plain hyphen `-`):
```
L2L[PHASE]: <module> — <summary> — CVEs: <CVE-ID,CVE-ID or NONE>
```
`ledger.py` filters git log for lines starting with `L2L[` — commits not in this format are silently dropped from the ledger.

## Java Transform Specifics
- `javax.*` → `jakarta.*` (Spring Boot 3 only).
- Logger declaration must be exactly:
  ```java
  private static final Logger log = LoggerFactory.getLogger(ClassName.class);
  ```
- REST endpoints: add under `/api/**` prefix, never remove the JSP controller alongside them.
- SQL: `JdbcTemplate` parameterized queries only — no string concatenation.
- Complexity reduction: extract private helpers — **never inline**. `System.out.println` must not remain after transform.

## Scoring Script — `pipeline/scripts/score.py`
- Must be run from repo root (it resolves `pipeline/l2l.config.json` relative to `__file__`).
- All five `--` args are required; `--framework-current` accepts `true`/`false`/`yes`/`1`.
- `scoring` weights in `l2l.config.json` **must sum to 100** — script hard-exits otherwise.
- CVE penalty is non-linear: `min(cve_count × ceil(weight/10), weight)` — not a simple ratio.

## Ledger Script — `pipeline/scripts/ledger.py`
- Reads `target_repo_path` from `l2l.config.json` and runs `git log` in that directory.
- `pipeline/scores/` first file = baseline, last file = final (sorted alphabetically by timestamp filename).
- Output: `pipeline/L2L_CHANGE_LEDGER.json` (not `CHANGE_LEDGER.md` — different file, different location).

## 5-Checkpoint Confirmation (print after every module transform)
```
[ ] Contract test exists and passes
[ ] No new CVEs introduced (check pom.xml diff)
[ ] No System.out.println remaining in changed files
[ ] Cyclomatic complexity did not increase
[ ] Build succeeds (mvn clean test)
```
