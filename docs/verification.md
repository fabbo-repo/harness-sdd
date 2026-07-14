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

Features that expose an entry point (CLI/HTTP/…) are verified by running the
real interface against a temporary, isolated environment:

```python
import subprocess, tempfile, os
with tempfile.TemporaryDirectory() as d:
    env = {**os.environ, "STORE_FILE": os.path.join(d, "store.json")}
    out = subprocess.check_output(
        ["python3", "-m", "src.<entrypoint>", "<command>", "<args>"],
        env=env, text=True,
    )
    assert "<expected>" in out
```

### Level 3 — Manual smoke test (optional but recommended)

Before closing the session, run an end-to-end flow against a temporary,
throwaway environment:

```bash
STORE_FILE=/tmp/demo_store.json python3 -m src.<entrypoint> <command> <args>
STORE_FILE=/tmp/demo_store.json python3 -m src.<entrypoint> <read-command>
rm /tmp/demo_store.json
```

### Level 4 — Scenario traceability (mandatory for features with `"sdd": true`)

Each `@s` scenario of `features/<name>.feature` must be mappable to at
least one concrete test in `tests/`. The `judge` rejects if coverage is missing.

The `tdd_craftsman` documents the map in `progress/tdd_<name>.md`:

```markdown
## Traceability
- @s1 (<happy path>)     → test_<behavior>
- @s2 (<edge case>)      → test_<edge_case>
- @s3 (<error path>)     → test_<error_path>
```

### Level 5 — Mutation testing (mandatory to close an sdd feature)

A green suite is not enough: you must prove that the tests **bite**. The
`mutation_tester` runs the mutator and demands the threshold in
`docs/mutation-testing.md`:

```bash
python3 tools/mutate.py src/<module>.py
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
python3 tools/mutate.py src/<module>.py   # score above the threshold
```

If `./init.sh` is red or mutants survive without justification, do **not**
mark anything as `done`. Note the blocker in `progress/current.md` with
a `blocked` state in `feature_list.json`.
