# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## What This Project Is
L2L is a reusable IBM Bob pipeline for modernizing legacy Java applications. It ships as Bob configuration files (modes, rules, templates) installed into a target repo. Bob is the intelligence layer; L2L provides structure.

## Stack
- IBM Bob (custom modes, rules)
- JSON (`pipeline/l2l.config.json` — the only file that changes per target repo)
- Python 3 (`pipeline/scripts/score.py`, `pipeline/scripts/ledger.py`)
- Shell (`scripts/score.sh`)
- Markdown (report templates, ADRs)

## Pipeline Phases & Bob Modes
| Mode              | Phase     | Writable outputs                              |
|-------------------|-----------|-----------------------------------------------|
| `/l2l-audit`      | AUDIT     | `AUDIT_REPORT.md` only (read-only otherwise)  |
| `/l2l-transform`  | TRANSFORM | Source files + `CHANGE_LEDGER.md`             |
| `/l2l-verify`     | VERIFY    | `*VerifyTest.java`, `CHANGE_LEDGER.md`, `AUDIT_REPORT.md` |

## Key Commands
```bash
# Compute migration score (run from repo root, AUDIT_REPORT.md must exist first)
python pipeline/scripts/score.py \
  --cve-count 4 \
  --test-coverage 0.72 \
  --api-coverage 0.5 \
  --complexity-violations 3 \
  --framework-current false

# Generate change ledger JSON from git history in the target repo
python pipeline/scripts/ledger.py
python pipeline/scripts/ledger.py --score-baseline 22 --score-final 74

# Shell-based score summary (simpler, partial — 60-point scale only)
./scripts/score.sh
```
Scores are saved to `pipeline/scores/score_<timestamp>.json`. The first file in that directory is treated as baseline; the last as final.

## Non-Obvious Rules

### Commit format — enforced by `core.md`, parsed by `ledger.py`
Every changed file must be committed using **exactly** this format (em-dash `—`, not hyphen):
```
L2L[PHASE]: <module> — <summary> — CVEs: <CVE-ID,CVE-ID or NONE>
```
`ledger.py` only picks up commits whose subject starts with `L2L[`. Plain hyphens are tolerated by the regex but em-dashes are canonical.

### Hard gates — do not proceed without these
- **No edits before contracts**: `L2L_CONTRACTS.md` must contain an entry for the module before any source file is touched in TRANSFORM.
- **No module advance before VERIFY**: every module must have a passing `[Module]ContractTest.java` before moving to the next.
- **Never mock the class under test**: use `@SpringBootTest` + `MockMvc` for controller tests.

### Transform rules (non-obvious specifics)
- `javax.*` → `jakarta.*` for Spring Boot 3 migrations.
- Log4j 1.x → SLF4J + Logback. Required import pattern:
  ```java
  private static final Logger log = LoggerFactory.getLogger(ClassName.class);
  ```
- REST endpoints go under `/api/**` prefix **alongside** (not replacing) the JSP controller.
- SQL injection fixes use `JdbcTemplate` parameterized queries — **never** string concatenation.
- Methods with cyclomatic complexity > 5: extract private helpers, **do not inline** the extraction.

### Scoring formula (`pipeline/scripts/score.py`)
Weights live in `pipeline/l2l.config.json` under `scoring` and **must sum to 100**. The script exits with an error if they don't. CVE score is not linear — each CVE deducts `ceil(weight/10)` points.

### Audit strictness
- Any unpinned dependency = risk finding.
- Any method with cyclomatic complexity > 5 = finding.
- Any public method without a test = coverage gap.
- Any user-facing input reaching a DB call without parameterization = **CRITICAL**.
- Never estimate the baseline score — always run `score.py`.

### `l2l-audit` mode file permissions
The `l2l-audit` custom mode (`custom_modes.yaml`) restricts edits to files matching `AUDIT_REPORT\.md$` only. All other writes are blocked at the mode level.

### `l2l-verify` mode file permissions
Restricted to files matching `.*VerifyTest\.java$|CHANGE_LEDGER\.md$|AUDIT_REPORT\.md$`.

## Project Layout
```
.bob/
  custom_modes.yaml          # mode definitions (slug, groups/fileRegex)
  modes/                     # per-mode auto-activation instructions
  rules/                     # audit.md, core.md, transform.md, verify.md
pipeline/
  l2l.config.json            # ONLY file changed per target repo
  scripts/score.py           # authoritative scorer (Python, 100-pt scale)
  scripts/ledger.py          # git-history ledger generator
  scores/                    # timestamped score snapshots
templates/
  AUDIT_REPORT.md            # audit output template
  ADR_TEMPLATE.md            # Architecture Decision Record template
  CHANGE_LEDGER.md           # per-module change log template
scripts/
  score.sh                   # simplified bash scorer (60-pt partial scale)
dashboard/
  index.html                 # score visualization dashboard
```
