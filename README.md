L2L — Legacy-to-Lockdown
What this is

A reusable IBM Bob pipeline for modernizing legacy Java applications. L2L ships as Bob configuration files (modes, rules, templates) that developers install into their own repos. Bob is the intelligence layer; L2L provides the structure.
Stack

    IBM Bob (custom modes, rules, skills)
    JSON (pipeline configuration)
    Markdown (report templates, ADRs)
    Shell scripts (scoring utilities)

Key commands

    Start an audit: switch to /l2l-audit mode
    Run a transform: switch to /l2l-transform mode
    Verify equivalence: switch to /l2l-verify mode
    Edit target config: pipeline/l2l.config.json

Project layout

.bob/
  custom_modes.yaml        # l2l-audit, l2l-transform, l2l-verify modes
  rules/
    audit.md               # AUDIT phase rules
    transform.md           # TRANSFORM phase rules
    verify.md              # VERIFY phase rules
pipeline/
  l2l.config.json          # target-specific values (set per repo)
templates/
  AUDIT_REPORT.md          # audit output template
  ADR_TEMPLATE.md          # Architecture Decision Record template
  CHANGE_LEDGER.md         # per-module change log template
scripts/
  score.sh                 # compute modernization score delta
AGENTS.md                  # pipeline overview (this project)
CLAUDE.md                  # Bob workspace instructions (this file)

Notes

    pipeline/l2l.config.json is the ONLY file that changes per target repo. All Bob rules and mode definitions are target-agnostic.
    Bob modes are workspace-scoped (.bob/custom_modes.yaml), so installing L2L into a target repo makes the modes available only in that workspace.
    Never edit source Java directly in /l2l-audit mode — it is read-only.
    TRANSFORM gates: each module must pass VERIFY before the next begins.
## How to Point L2L at Your Own App
1. Clone this repo
2. Edit pipeline/l2l.config.json with your target path
3. Open l2l/ in Bob IDE

here are the next steps
Step 0 — one-time setup:
  Edit pipeline/l2l.config.json:
    "target_repo_path": "../inventory-tracker"
  
  That's the only file you touch to point L2L at any target.

Step 1 — bootstrap Bob's context:
  /init

Step 2 — run the audit:
  /l2l-audit

  Bob reads l2l.config.json, finds ../inventory-tracker,
  reads its pom.xml and src/ tree, runs score.py,
  writes L2L_AUDIT_REPORT.md into l2l/ (not into the target).

Step 3 — generate the migration plan:
  /plan
  Read l2l.config.json and L2L_AUDIT_REPORT.md,
  then generate L2L_MIGRATION_PLAN.md here in l2l/.

Step 4 — transform a module:
  /l2l-transform ProductController

  Bob reads ../inventory-tracker/src/.../ProductController.java,
  edits it IN PLACE in the target repo,
  writes contracts to l2l/L2L_CONTRACTS.md,
  stages the commit in the TARGET repo's git history.

Step 5 — verify it:
  /l2l-verify ProductController

  Bob writes the test file to ../inventory-tracker/src/test/...,
  runs mvn test from ../inventory-tracker/,
  reports results back into the l2l/ chat session.

  pre- modernization repo - https://github.com/breakingcircuits1337/InventoryTracker-Demo-Target2 can be used for testing L2L
  
  Baseline Score: 23 / 100 — 🔴 Critical    ----- 92/100 final score     https://github.com/breakingcircuits1337/InventoryTracker-Demo-Target is the modernized version from the demo.
