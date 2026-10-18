# AGENTS.md — Architectural Constraints (Non-Obvious Only)

This file provides guidance to agents when working with code in this repository.

## Non-Negotiable Architectural Constraints

### Phase ordering is strictly enforced
AUDIT → (PLAN) → TRANSFORM → VERIFY per module. The TRANSFORM mode's auto-activation instructions (`l2l-transformer.md`) refuse to proceed if the module is not next in `L2L_MIGRATION_PLAN.md`. Do not skip or reorder modules.

### Contract-first, always
Business logic must not be touched without a prior passing contract test. This is not a style preference — it is a hard pipeline gate. Planning must always account for: write contracts → TRANSFORM → write tests → VERIFY before advancing.

### Mode write permissions are code-enforced
`custom_modes.yaml` uses `fileRegex` within the `edit` group to restrict writes per mode. Plans that assume an audit agent can write migration plans or transform output files will be rejected by the mode at runtime.

### Two scorers exist — they are not interchangeable
- `scripts/score.sh` → partial shell scorer, 60-point ceiling, human-readable summary only.
- `pipeline/scripts/score.py` → authoritative Python scorer, 100-point scale, writes JSON to `pipeline/scores/`.
Any scoring plan must reference `score.py`. `score.sh` is for quick manual inspection only.

### Scoring weights are a project invariant
`pipeline/l2l.config.json` `scoring` weights must sum to exactly 100. Any plan to adjust weights must account for rebalancing all five dimensions (`cve_weight`, `test_coverage_weight`, `api_enablement_weight`, `complexity_weight`, `framework_currency_weight`).

### `ledger.py` depends on git history in the target repo
The ledger is generated from `git log` in the path specified by `target_repo_path`. If that repo path is wrong or commits do not follow `L2L[PHASE]:` format, the ledger will be empty. Plans that include ledger generation must ensure the target repo and commit format are correct first.

### TRANSFORM does not touch tests; VERIFY does not touch source
These are hard mode boundaries enforced by `fileRegex`. Cross-phase edits will be silently rejected.
