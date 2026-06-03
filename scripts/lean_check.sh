#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../formal"
/Users/yhl/.elan/bin/lake build Uav
cd ..
if rg -n "\\bsorry\\b|\\badmit\\b" formal; then
  echo "Lean files contain incomplete proofs" >&2
  exit 1
fi

axiom_pattern='^\s*(?:@\[[^]]+\]\s*)*(?:(?:private|protected|noncomputable|unsafe)\s+)*axiom\b'
axiom_count=$({ rg -n "$axiom_pattern" formal || true; } | wc -l | tr -d " ")
if [ "$axiom_count" -ne 0 ]; then
  echo "Expected exactly 0 axioms, found $axiom_count" >&2
  exit 1
fi

.venv/bin/python scripts/lean_trace_report.py
