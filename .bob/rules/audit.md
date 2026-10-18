You are in AUDIT phase. Read-only. Make no file changes except 
to write L2L output files (AUDIT_REPORT.md, AGENTS.md updates).

When auditing:
- Treat every dependency without an explicit version pin as a risk.
- Treat every method with cyclomatic complexity > 5 as a finding.
- Treat every public method with no corresponding test as a 
  coverage gap.
- Treat every user-facing input that reaches a DB call without 
  parameterization as a critical security finding.
- Use the scoring formula in pipeline/scripts/score.py to 
  calculate the baseline L2L Migration Score. Never estimate 
  the score — run the script.
