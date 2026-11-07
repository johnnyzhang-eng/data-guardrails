#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"

"$PY" -m checks.data_quality --selftest
"$PY" -m checks.result_integrity --selftest
"$PY" -m checks.claim_lint --selftest
"$PY" -m checks.json_batch --selftest
"$PY" -m checks.decision_gate --selftest

if command -v semgrep >/dev/null 2>&1; then
  SEMGREP_SEND_METRICS=off SEMGREP_ENABLE_VERSION_CHECK=0 \
    semgrep --test --config semgrep/rules semgrep/tests
elif [ "${REQUIRE_SEMGREP:-0}" = 1 ]; then
  echo "L4 static rule: FAIL (Semgrep required but unavailable)"
  exit 1
else
  echo "L4 static rule: SKIP (Semgrep is not installed)"
fi
echo "All executed selftests passed."
