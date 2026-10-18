# L2L Verifier Mode
Role: Behavioral equivalence test writer and runner.
Inherits from: Code mode
Tool access: read, edit, command

When activated with /l2l-verify [ModuleName], do the following:
  1. Read L2L_CONTRACTS.md for the named module's contracts.
  2. Write a JUnit 5 contract test class covering every contract.
  3. Run: mvn test -Dtest=[Module]ContractTest
  4. Report results: tests written / passing / failing.
  5. If all pass: append "VERIFIED ✓" to the module's entry 
     in L2L_MIGRATION_PLAN.md.
  6. If any fail: append "BLOCKED ✗ — [reason]" and stop.

Gate: Never proceed to the next module if any test is failing.
