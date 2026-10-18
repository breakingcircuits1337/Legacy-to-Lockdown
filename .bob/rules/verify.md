# Bob rules — VERIFY phase
# Active in: /l2l-verify mode
# Behavioral equivalence testing before any module is considered done.

## Purpose
VERIFY confirms that a transformed module behaves identically to its
pre-transformation counterpart for all observable contracts. A module
that does not pass VERIFY must not proceed to the next TRANSFORM step.

## Equivalence criteria
A module passes VERIFY when ALL of the following are true:
1. All pre-existing tests pass without modification.
2. Every public method that existed before transformation still exists
   with a compatible signature (or is explicitly documented as a
   BREAKING CHANGE in the CHANGE_LEDGER.md and an ADR).
3. New tests cover at least the happy path and one error path for each
   method changed during TRANSFORM.
4. No new exceptions are thrown from pre-existing call sites.

## Test generation rules
- Generate unit tests using JUnit 5 (Jupiter) unless l2l.config.json
  specifies a different `"test_framework"`.
- Use Mockito for dependency isolation unless `"mock_framework"` overrides.
- Test class naming: `<OriginalClassName>VerifyTest.java`
- Place generated tests in the same package as the class under test,
  under the project's test source root.
- Do not modify production code to make tests pass. If a test cannot
  pass without a production change, flag it as a VERIFY FAILURE and
  return to TRANSFORM.

## Scoring
After all tests pass, run `scripts/score.sh` to compute the delta
between the pre-transform and post-transform modernization scores.
Record the result in AUDIT_REPORT.md under the relevant module's
VERIFY section.

## VERIFY FAILURE protocol
If any criterion above is not met:
1. Append a VERIFY FAILURE entry to CHANGE_LEDGER.md.
2. Switch back to `/l2l-transform` mode.
3. Do NOT advance the pipeline to the next module.
