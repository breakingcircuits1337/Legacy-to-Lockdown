You are in VERIFY phase. You may read source files and write 
test files only.

Verification rules:
- Read L2L_CONTRACTS.md for the current module before writing 
  any test.
- Every contract listed must have at least one corresponding test.
- Write contract tests to:
    src/test/java/.../[Module]ContractTest.java
- Run tests immediately after writing them. Do not move to the 
  next module until all contract tests pass.
- If a test fails, document the violated contract in 
  L2L_AUDIT_REPORT.md under "Contract Violations" and STOP.
- Never mock the class under test. Use @SpringBootTest with 
  MockMvc for controller tests.
