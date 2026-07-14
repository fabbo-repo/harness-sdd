# Verification — How to prove the work works

> Golden rule: **the agent doesn't say "it works", it proves it**.
> Every feature ends with executable evidence, not with claims.

## Verification levels

### Level 1 — Unit tests (mandatory)

Every public function in `src/` has at least one test in `tests/` that:

1. Covers the happy path.
2. Covers at least one error path if the function can fail.

Command:
```bash
python3 -m unittest discover -s tests -v
```

### Level 2 — CLI integration test (mandatory for UI features)

Features that add commands to the CLI are verified by running the real CLI
against a temporary file:

```python
import subprocess, tempfile, os
with tempfile.TemporaryDirectory() as d:
    env = {**os.environ, "NOTES_FILE": os.path.join(d, "notes.json")}
    out = subprocess.check_output(
        ["python3", "-m", "src.cli", "add", "hello", "--body", "world"],
        env=env, text=True,
    )
    assert "id=" in out
```

### Level 3 — Manual smoke test (optional but recommended)

Before closing the session, run an end-to-end flow with a temporary
file in `/tmp`:

```bash
NOTES_FILE=/tmp/notes_demo.json python3 -m src.cli add "test" --body "x"
NOTES_FILE=/tmp/notes_demo.json python3 -m src.cli list
rm /tmp/notes_demo.json
```

### Level 4 — Scenario traceability (mandatory for features with `"sdd": true`)

Each `@s` scenario of `features/<name>.feature` must be mappable to at
least one concrete test in `tests/`. The `judge` rejects if coverage is missing.

The `tdd_craftsman` documents the map in `progress/tdd_<name>.md`:

```markdown
## Traceability
- @s1 (empty file → 0) → test_count_empty_file
- @s2 (several notes → 3)  → test_count_several_notes
- @s3 (doesn't mutate the file) → test_count_does_not_mutate_file
```

### Level 5 — Mutation testing (mandatory to close an sdd feature)

A green suite is not enough: you must prove that the tests **bite**. The
`mutation_tester` runs the mutator and demands the threshold in
`docs/mutation-testing.md`:

```bash
python3 tools/mutate.py src/cli.py
```

Every surviving mutant is killed with a new test or justified as
equivalent in `progress/mutation_<name>.md`.

## Anti-patterns (do not do)

- ❌ "I added the command, it should work." → an executable test is missing.
- ❌ A test that only verifies the function doesn't raise an exception. → it has
  to check the concrete result.
- ❌ `mock` of the filesystem. → use a real `tempfile.TemporaryDirectory()`.
- ❌ Marking the feature as `done` without passing `./init.sh`.

## Final verification before closing

```bash
./init.sh                       # must finish with [OK] Environment ready
python3 tools/mutate.py src/cli.py   # score above the threshold
```

If `./init.sh` is red or mutants survive without justification, do **not**
mark anything as `done`. Note the blocker in `progress/current.md` with
a `blocked` state in `feature_list.json`.
