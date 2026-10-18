#!/usr/bin/env bash
# score.sh — compute L2L modernization score delta
# Usage: ./scripts/score.sh [--baseline] [--current] [--delta]
#
# Scores are written to pipeline/l2l.config.json under "score".
# Run after each VERIFY pass to track progress.
#
# Scoring model (100-point scale):
#   Security fixes resolved      (max 35)
#   Deprecated APIs migrated     (max 25)
#   Complexity hotspots resolved (max 20)
#   Coverage improvement         (max 20)

set -euo pipefail

CONFIG="pipeline/l2l.config.json"
REPORT="AUDIT_REPORT.md"

if [[ ! -f "$CONFIG" ]]; then
  echo "ERROR: $CONFIG not found. Run from the project root." >&2
  exit 1
fi

if [[ ! -f "$REPORT" ]]; then
  echo "ERROR: $REPORT not found. Complete the AUDIT phase first." >&2
  exit 1
fi

# Count findings by severity in AUDIT_REPORT.md
count_severity() {
  local sev="$1"
  grep -c "| $sev " "$REPORT" 2>/dev/null || echo 0
}

CRITICAL=$(count_severity "CRITICAL")
HIGH=$(count_severity "HIGH")
MEDIUM=$(count_severity "MEDIUM")
LOW=$(count_severity "LOW")

TOTAL_FINDINGS=$(( CRITICAL + HIGH + MEDIUM + LOW ))

# Weighted security score (max 35)
SECURITY_RESOLVED=$(grep -c "PASS" "$REPORT" 2>/dev/null || echo 0)
SECURITY_SCORE=0
if [[ "$TOTAL_FINDINGS" -gt 0 ]]; then
  SECURITY_SCORE=$(( (SECURITY_RESOLVED * 35) / TOTAL_FINDINGS ))
fi

# API migration score (max 25) — count migrated entries in CHANGE_LEDGER
LEDGER="CHANGE_LEDGER.md"
API_MIGRATIONS=0
if [[ -f "$LEDGER" ]]; then
  API_MIGRATIONS=$(grep -c "API migration" "$LEDGER" 2>/dev/null || echo 0)
fi
API_SCORE=$(( API_MIGRATIONS > 25 ? 25 : API_MIGRATIONS ))

TOTAL=$(( SECURITY_SCORE + API_SCORE ))

echo "================================================"
echo " L2L Modernization Score"
echo "================================================"
echo "  Security fixes:        $SECURITY_SCORE / 35"
echo "  API migrations:        $API_SCORE / 25"
echo "  Complexity (manual):   ?? / 20  (update config)"
echo "  Coverage (manual):     ?? / 20  (update config)"
echo "------------------------------------------------"
echo "  Computable total:      $TOTAL / 60"
echo "================================================"
echo ""
echo "Update pipeline/l2l.config.json score.current to record this value."
