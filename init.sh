#!/usr/bin/env bash
# init.sh — Environment verification and initialization
#
# This script is run by the agent when STARTING a session and before
# declaring any task as `done`. If it fails, the session must not proceed.
#
# Language-agnostic: the harness *tooling* (this script + tools/mutate.py)
# runs on Python 3.9+, but the *target project* can be in any language. The
# test command lives in harness.json (`test_command`).

set -u
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()    { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
fail()  { printf "${RED}[FAIL]${NC}  %s\n" "$1"; }

EXIT_CODE=0

echo "── 1. Verifying harness tooling runtime ────────────────"

# The harness tooling needs Python 3.9+ (for tools/mutate.py and JSON
# validation). This is independent of your project's language. Accept either
# `python3` or `python` so it works on Windows too.
PYTHON=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1 \
     && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
    PYTHON="$cand"
    break
  fi
done
if [ -z "$PYTHON" ]; then
  fail "No Python >= 3.9 found (needed for the harness tooling). Install it or fix your PATH."
  exit 1
fi
ok "harness tooling python -> $("$PYTHON" --version 2>&1) [$PYTHON]"
export PYTHON

# The mutation phase is optional. harness.json -> mutation.enabled is
# true (always) | false (never) | "ask" (the craftsman_lead asks the human at
# the Gherkin approval gate). Missing block == enabled.
MUTATION=$("$PYTHON" -c "
import json
cfg = json.load(open('harness.json')).get('mutation', {})
v = cfg.get('enabled', True)
print('ask' if str(v).lower() == 'ask' else ('true' if v is True else 'false'))
" 2>/dev/null) || MUTATION="true"

case "$MUTATION" in
  true)  ok   "mutation phase -> ENABLED (threshold in docs/mutation-testing.md)" ;;
  ask)   ok   "mutation phase -> ASK (decided per feature at the approval gate)" ;;
  false) warn "mutation phase -> DISABLED (harness.json: mutation.enabled = false)" ;;
esac

echo ""
echo "── 2. Verifying harness base files ─────────────────────"

BASE_FILES="AGENTS.md feature_list.json harness.json progress/current.md docs/architecture.md docs/conventions.md docs/verification.md docs/workflow.md CHECKPOINTS.md"
# tools/mutate.py is only required when the mutation phase can actually run.
if [ "$MUTATION" != "false" ]; then
  BASE_FILES="$BASE_FILES tools/mutate.py"
fi

for f in $BASE_FILES; do
  if [ ! -f "$f" ]; then
    fail "Missing base file: $f"
    EXIT_CODE=1
  else
    ok "$f exists"
  fi
done

echo ""
echo "── 3. Validating feature_list.json and scenarios ──────"

"$PYTHON" - <<'PY'
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
echo "── 4. Running the project's test suite ─────────────────"

SRC_DIR=$("$PYTHON" -c "import json; print(json.load(open('harness.json')).get('source_dir', 'src'))")
if [ -n "$(find "$SRC_DIR" -type f ! -name '.gitkeep' 2>/dev/null | head -1)" ]; then
  if bash tools/run_tests.sh; then
    ok "Test suite passes"
  else
    fail "The test suite is red"
    EXIT_CODE=1
  fi
else
  warn "No source in '$SRC_DIR' yet — skipping tests (fresh template)"
fi

echo ""
echo "── 5. Summary ──────────────────────────────────────────"

if [ $EXIT_CODE -eq 0 ]; then
  ok "Environment ready. You can start working."
else
  fail "Environment is NOT ready. Fix the errors before proceeding."
fi

exit $EXIT_CODE
