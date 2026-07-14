#!/usr/bin/env bash
# init.sh — Environment verification and initialization
#
# This script is run by the agent when STARTING a session and before
# declaring any task as `done`. If it fails, the session must not proceed.
#
# Expected output: clear exit codes and blocks marked with [OK]/[FAIL].

set -u
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()    { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
fail()  { printf "${RED}[FAIL]${NC}  %s\n" "$1"; }

EXIT_CODE=0

echo "── 1. Verifying environment ───────────────────────────"

# Python available
if ! command -v python3 >/dev/null 2>&1; then
  fail "python3 is not installed"
  exit 1
fi
ok "python3 -> $(python3 --version)"

# Minimum version 3.9 (dataclasses + modern typing)
PY_VERSION_OK=$(python3 -c 'import sys; print(int(sys.version_info >= (3, 9)))')
if [ "$PY_VERSION_OK" != "1" ]; then
  fail "Python >= 3.9 is required"
  exit 1
fi
ok "Compatible Python version"

echo ""
echo "── 2. Verifying harness base files ─────────────────────"

for f in AGENTS.md feature_list.json progress/current.md docs/architecture.md docs/conventions.md docs/verification.md docs/workflow.md tools/mutate.py CHECKPOINTS.md; do
  if [ ! -f "$f" ]; then
    fail "Missing base file: $f"
    EXIT_CODE=1
  else
    ok "$f exists"
  fi
done

echo ""
echo "── 3. Validating feature_list.json and scenarios ──────"

python3 - <<'PY'
import json, os, sys
try:
    data = json.load(open("feature_list.json"))
    valid = {"pending", "spec_ready", "in_progress", "done", "blocked"}
    in_progress = [f for f in data["features"] if f["status"] == "in_progress"]
    if len(in_progress) > 1:
        print(f"[FAIL]  There are {len(in_progress)} features in in_progress (maximum 1)")
        sys.exit(1)
    requires_spec = {"spec_ready", "in_progress", "done"}
    spec_errors = []
    for f in data["features"]:
        if f["status"] not in valid:
            print(f"[FAIL]  Invalid status in feature {f['id']}: {f['status']}")
            sys.exit(1)
        if f.get("sdd") and f["status"] in requires_spec:
            feature_file = os.path.join("features", f["name"] + ".feature")
            if not os.path.isfile(feature_file):
                spec_errors.append(
                    f"feature {f['id']} ({f['name']}) in {f['status']} "
                    f"without {feature_file}"
                )
    if spec_errors:
        for e in spec_errors:
            print(f"[FAIL]  {e}")
        sys.exit(1)
    print(f"[OK]    feature_list.json valid ({len(data['features'])} features)")
    print(f"[OK]    .feature scenarios present for non-pending sdd features")
except SystemExit:
    raise
except Exception as e:
    print(f"[FAIL]  feature_list.json or specs invalid: {e}")
    sys.exit(1)
PY

if [ $? -ne 0 ]; then EXIT_CODE=1; fi

echo ""
echo "── 4. Running tests ────────────────────────────────────"

if [ -d "tests" ]; then
  TEST_OUTPUT=$(python3 -m unittest discover -s tests -v 2>&1)
  TEST_RC=$?
  echo "$TEST_OUTPUT"
  if [ "$TEST_RC" -eq 0 ]; then
    ok "All tests pass"
  elif [ "$TEST_RC" -eq 5 ]; then
    # Python 3.12+ returns 5 when no tests are collected. A fresh template
    # legitimately has no tests yet — that's not a failure.
    warn "No tests collected yet (fresh template)"
  else
    fail "There are broken tests"
    EXIT_CODE=1
  fi
else
  warn "tests/ folder does not exist yet"
fi

echo ""
echo "── 5. Summary ──────────────────────────────────────────"

if [ $EXIT_CODE -eq 0 ]; then
  ok "Environment ready. You can start working."
else
  fail "Environment is NOT ready. Fix the errors before proceeding."
fi

exit $EXIT_CODE
