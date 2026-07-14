# TDD — feature #8 `cli_count`

Contract: `features/cli_count.feature` (@s1..@s7).
Discipline: The Three Laws of TDD, one test at a time, Red→Green→Refactor.
Imitated test pattern: `tests/test_cli.TestCli` (tempfile.TemporaryDirectory +
patch of `storage.DEFAULT_NOTES_PATH`, `_run` helper with redirect_stdout/stderr).

## Cycle log

### Cycle 1 — @s1 (empty store → "0")
- **RED:** `test_count_empty_store_prints_zero`. Fails with
  `argparse.ArgumentError: invalid choice: 'count'` (the subcommand doesn't exist).
- **GREEN (minimal):** `cmd_count` with `print(0)` + `count` subparser. Deliberate
  fake with a constant (there is no test yet that disproves it).
- **REFACTOR:** nothing to clean up; a one-line function.

### Cycle 2 — @s2 (non-existent store → "0")
- **RED/test:** `test_count_missing_store_prints_zero` (asserts the file
  does NOT exist before running). Passes immediately because the constant `0`
  also covers this case; behavior already correct. Generalization will be
  forced by @s3.
- **GREEN:** no production change.
- **REFACTOR:** nothing.

### Cycle 3 — @s3 (one note → "1")
- **RED:** `test_count_single_note_prints_one`. Fails: the constant `0` is no
  longer enough (expected `"1\n"`, got `"0\n"`).
- **GREEN (minimal):** generalize `cmd_count` to
  `notes = storage.load(); print(len(notes))`.
- **REFACTOR:** function already short and with clear names; nothing to touch.

### Cycle 4 — @s4 (three notes → "3", the precise number)
- **RED/test:** `test_count_three_notes_prints_three`. Already passes: the
  implementation was generalized in cycle 3. The scenario is a case distinct
  from the contract ("exact N, not ≥1") and deserves its own guard test.
- **GREEN:** no change.
- **REFACTOR:** nothing.

### Cycle 5 — @s5 (bare integer, no "Total")
- **RED/test:** `test_count_output_is_bare_integer_without_text`. Passes by
  construction (`print(len(...))` emits no text). Guards against a regression
  toward `Total: N`.
- **GREEN:** no change.
- **REFACTOR:** nothing.

### Cycle 6 — @s6 (doesn't mutate the file, byte by byte)
- **RED/test:** `test_count_does_not_mutate_store`. Passes: `cmd_count` never
  calls `storage.save`. A real guard: an implementation that wrote would
  fail the byte comparison.
- **GREEN:** no change.
- **REFACTOR:** nothing.

### Cycle 7 — @s7 (idempotent on a non-existent store; still doesn't exist)
- **RED/test:** `test_count_does_not_create_store_when_missing`. Passes:
  `storage.load` of an absent file returns `[]` without creating it. Guards
  against an implementation that touched the file.
- **GREEN:** no change.
- **REFACTOR:** nothing.

## Note on the Three Laws

Only two cycles (1 and 3) required new production code, and each after
a red test: `print(0)` (constant, Law 3) and then `print(len(storage.load()))`
(generalization forced by @s3). Cycles 2, 4-7 add guard tests that
encode distinct edges of the contract; they pass by construction and don't
introduce "for the future" production code. There were no refactors while red.

## Traceability @s → test

- @s1 (empty store → "0")                 → `test_count_empty_store_prints_zero`
- @s2 (non-existent store → "0")          → `test_count_missing_store_prints_zero`
- @s3 (one note → "1")                    → `test_count_single_note_prints_one`
- @s4 (three notes → exact "3")           → `test_count_three_notes_prints_three`
- @s5 (bare integer, no "Total")          → `test_count_output_is_bare_integer_without_text`
- @s6 (doesn't mutate the file, byte by byte) → `test_count_does_not_mutate_store`
- @s7 (idempotent, file still absent)     → `test_count_does_not_create_store_when_missing`

## Final state

- `./init.sh` GREEN end to end (34 tests, OK).
- Implementation: `cmd_count` + `count` subparser in `src/cli.py`.
- 7 new tests in `tests/test_cli.py` (one per scenario).
- Feature #8 still `in_progress`. NOT marked `done` (pending judge +
  mutation_tester).
