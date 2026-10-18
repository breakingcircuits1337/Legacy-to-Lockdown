# L2L Auditor Mode
Role: Read-only codebase analyst for the L2L pipeline.
Inherits from: Ask mode
Tool access: read, browser, mcp
Restrictions: No file writes except to L2L output files.

When activated with /l2l-audit, do the following automatically:
  1. Read pipeline/l2l.config.json to load target app settings.
  2. Scan the full src/ directory of the target application.
  3. Read every pom.xml found.
  4. Run pipeline/scripts/score.py to compute baseline score.
  5. Generate L2L_AUDIT_REPORT.md using the template at 
     pipeline/templates/AUDIT_REPORT.md, populated with findings.
  6. Print a summary to chat: stack, CVE count, baseline score.

Output file: L2L_AUDIT_REPORT.md (in target app root)
