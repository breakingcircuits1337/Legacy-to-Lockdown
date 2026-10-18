# Bob rules — TRANSFORM phase
# Active in: /l2l-transform mode
# Module-by-module refactoring with mandatory safety gates.

## Safety gates — MUST pass before proceeding
1. The module targeted for transformation must have a corresponding entry
   in AUDIT_REPORT.md (i.e., it has been audited).
2. A VERIFY checkpoint must exist and pass for the previous module
   before the current module's transform begins.
3. All changes must be logged in templates/CHANGE_LEDGER.md with:
   - Module name
   - What changed and why
   - Before/after signature for any public API that changed
   - ADR reference if an architectural decision was made

## Transformation principles
- One module at a time. Do not refactor across module boundaries in a
  single session.
- Preserve behavioral contracts. If a public method's semantics change,
  it is a BREAKING CHANGE — document it in an ADR.
- Prefer minimal diffs. Do not reformat unrelated code.
- Remove dead code only when confirmed by coverage data in AUDIT_REPORT.md.
- Migrate deprecated APIs using the replacement table in l2l.config.json
  under `"api_migrations"`.

## Dependency upgrades
- Only upgrade a dependency if it is listed in l2l.config.json under
  `"target_dependencies"`.
- Pin all upgraded versions explicitly. Do not use open ranges.
- After a dependency upgrade, add an entry to CHANGE_LEDGER.md.

## Commit discipline
- Each transformed module produces exactly one logical commit.
- Commit message format: `transform(<module>): <what changed>`
- Do not bundle unrelated fixes into a transform commit.

## Forbidden during TRANSFORM
- Do not alter test files. Test changes are the VERIFY phase's job.
- Do not change l2l.config.json. Config is set before the pipeline runs.
- Do not generate new ADRs without a confirmed architectural decision.
