#!/usr/bin/env bash
# run_tests.sh — runs the project's test suite as declared in harness.json.
#
# Language-agnostic: it just reads `test_command` and execs it. Used by both
# init.sh and the .claude/settings.json hooks so the command lives in one place.
set -e

# Pick a Python that actually runs (the Windows `python3` Store stub resolves
# on PATH but fails to execute, so we verify with a real invocation).
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys' >/dev/null 2>&1; then
      PY="$c"; break
    fi
  done
fi
if [ -z "$PY" ]; then
  echo "run_tests.sh: no python found to read harness.json" >&2
  exit 127
fi

CMD=$("$PY" -c "import json; print(json.load(open('harness.json'))['test_command'])")
exec bash -c "$CMD"
