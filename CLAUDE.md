# L2L — Legacy-to-Lockdown

## What this is
A reusable IBM Bob pipeline for modernizing legacy Java applications.
L2L ships as Bob configuration files (modes, rules, templates) that
developers install into their own repos. Bob is the intelligence layer;
L2L provides the structure.

## Stack
- IBM Bob (custom modes, rules, skills)
- JSON (pipeline configuration)
- Markdown (report templates, ADRs)
- Shell scripts (scoring utilities)

## Key commands
- Start an audit:      switch to `/l2l-audit` mode
- Run a transform:     switch to `/l2l-transform` mode
- Verify equivalence:  switch to `/l2l-verify` mode
- Edit target config:  `pipeline/l2l.config.json`

## Project layout
```
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
```

## Notes
- `pipeline/l2l.config.json` is the ONLY file that changes per target repo.
  All Bob rules and mode definitions are target-agnostic.
- Bob modes are workspace-scoped (`.bob/custom_modes.yaml`), so installing
  L2L into a target repo makes the modes available only in that workspace.
- Never edit source Java directly in `/l2l-audit` mode — it is read-only.
- TRANSFORM gates: each module must pass VERIFY before the next begins.
