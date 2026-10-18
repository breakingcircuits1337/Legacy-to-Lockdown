# L2L — Legacy-to-Lockdown

> A reusable IBM Bob pipeline that modernizes legacy Java applications safely, verifiably, and with a full audit trail.

---

## What It Is

L2L ships as Bob configuration files — custom modes, rules, and templates — that you install into your workspace. Point it at any legacy Java repo, run four commands, and Bob drives the entire modernization: audit, transform, verify, document.

**Bob is the intelligence layer. L2L is the structure.**

---

## Demo Results

| Metric | Before | After |
|---|---|---|
| Known CVEs | 6 | 0 |
| Test Coverage | 0% | 81% |
| REST Endpoints | 0 | 12 |
| Complexity Violations | 2 | 0 |
| Framework | Spring MVC 4.3 (EOL) | Spring Boot 3.2 |
| **L2L Migration Score** | **23 / 100 🔴** | **92 / 100 🟢** |

**Target repos:**
- Pre-modernization: https://github.com/breakingcircuits1337/InventoryTracker-Demo-Target2
- Post-modernization: https://github.com/breakingcircuits1337/InventoryTracker-Demo-Target

---

## How It Works

```
AUDIT       →  map CVEs, complexity, coverage gaps      (/l2l-audit)
PLAN        →  prioritize migration order               (/plan)
TRANSFORM   →  module-by-module refactoring with gates  (/l2l-transform)
VERIFY      →  behavioral equivalence tests             (/l2l-verify)
DOCUMENT    →  change ledger, ADRs, OpenAPI spec        (auto-generated)
```

Each phase gates the next. Bob won't transform a module without first extracting its behavioral contracts, and won't move to the next module until verification passes.

---

## Project Layout

```
l2l/
├── .bob/
│   ├── custom_modes.yaml       # l2l-audit, l2l-transform, l2l-verify
│   └── rules/
│       ├── audit.md            # read-only analysis rules
│       ├── transform.md        # safe refactoring rules + gates
│       └── verify.md           # equivalence testing rules
├── pipeline/
│   ├── l2l.config.json         # ← only file you change per target
│   ├── templates/
│   │   ├── AUDIT_REPORT.md
│   │   ├── ADR_TEMPLATE.md
│   │   └── CHANGE_LEDGER.md
│   └── scripts/
│       └── score.sh
├── AGENTS.md                   # Bob's persistent pipeline context
└── CLAUDE.md                   # Bob workspace instructions
```

---

## Quick Start

**Prerequisites:** Bob IDE installed, legacy Java app cloned locally.

**Step 1 — Configure your target**

Edit the one line that changes per project:

```json
// pipeline/l2l.config.json
{
  "target_repo_path": "../your-legacy-app"
}
```

**Step 2 — Open `l2l/` in Bob IDE** (never open the target repo directly)

**Step 3 — Bootstrap**

```
/init
```

**Step 4 — Audit**

```
/l2l-audit
```

Bob reads your target's `pom.xml` and `src/` tree, scans for CVEs, maps complexity violations and coverage gaps, and writes `L2L_AUDIT_REPORT.md` with a baseline Migration Score.

**Step 5 — Plan**

```
/plan
```

Bob reads the audit report and generates `L2L_MIGRATION_PLAN.md` — a dependency-safe, prioritized module execution order.

**Step 6 — Transform a module**

```
/l2l-transform ProductController
```

Bob extracts behavioral contracts, refactors the module in place inside the target repo, and stages a commit with a structured message:
`L2L[TRANSFORM]: ProductController — Log4j→SLF4J, SQL injection fix, REST endpoint added — CVEs: CVE-2019-17571`

**Step 7 — Verify it**

```
/l2l-verify ProductController
```

Bob writes JUnit 5 contract tests, runs them against the target, and only marks the module complete when all tests pass.

**Step 8 — Repeat Steps 6–7** for each module in the migration plan.

---

## Key Rules

- `pipeline/l2l.config.json` is the **only** file that changes between target repos. All modes and rules are target-agnostic.
- Bob modes are workspace-scoped — install L2L into your workspace to activate `/l2l-audit`, `/l2l-transform`, and `/l2l-verify`.
- **`/l2l-audit` is read-only.** Bob makes no source changes in this mode.
- **Transform gates:** every module must pass `/l2l-verify` before the next module begins.

---

## Stack

- IBM Bob (custom modes, rules)
- JSON (pipeline config)
- Markdown (report templates, ADRs)
- Shell (scoring utilities)

---

## Built for AngelHack — Building with IBM Bob
**Track:** Experienced Developers — Modernize What Matters
