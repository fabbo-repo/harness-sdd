# Review — feature 7 (cli_recent)

**Verdict:** APPROVED

## Requirements ↔ tests traceability

- R1 (default <= 5 notes): [x] covered by `test_recent_default_limit_orders_by_created_at_desc`
  (`tests/test_cli.py:166-178`, creates 7 notes, expects exactly 5 lines).
- R2 (`--limit N` with N > 0): [x] covered by `test_recent_custom_limit`
  (`tests/test_cli.py:180-193`, creates 6 notes, `--limit 3`, expects 3 lines).
- R3 (order by `created_at` desc): [x] covered by
  `test_recent_default_limit_orders_by_created_at_desc`
  (`tests/test_cli.py:175-178`, validates `timestamps == sorted(reverse=True)` and
  the title order `note-6..note-2`).
- R4 (format `<id>\t<created_at>\t<title>`): [x] covered by
  `test_recent_custom_limit` (`tests/test_cli.py:189-193`, validates 3 fields
  separated by tab, first field numeric, second field ISO 8601).
- R5 (no notes: exit 0, empty stdout): [x] covered by
  `test_recent_empty_outputs_nothing` (`tests/test_cli.py:195-199`, checks
  `code == 0`, `out == ""`, `err == ""`).
- R6 (`--limit <= 0`: exit != 0, non-empty stderr): [x] covered by
  `test_recent_invalid_limit_zero` (`tests/test_cli.py:201-213`) and
  `test_recent_invalid_limit_negative` (`tests/test_cli.py:215-227`).
- R7 (`--limit <= 0`: doesn't modify the file): [x] covered by the same
  two tests (compare `before/after` with `storage.load` and the file's exact
  bytes).

## Completed tasks

- T1 (`cmd_recent` in `src/cli.py`): [x]
- T2 (`recent` subparser in `build_parser`): [x]
- T3 (`test_recent_default_limit_orders_by_created_at_desc`): [x]
- T4 (`test_recent_custom_limit`): [x]
- T5 (`test_recent_empty_outputs_nothing`): [x]
- T6 (`test_recent_invalid_limit_zero` + `test_recent_invalid_limit_negative`): [x]
- T7 (traceability in `progress/impl_cli_recent.md`): [x]
- T8 (`./init.sh` green): [x]

All tasks of `specs/cli_recent/tasks.md` *(legacy Kiro-style SDD layout, no
longer in the repo — replaced by `features/cli_recent.feature`)* are marked `[x]`.

## Compliance with `docs/architecture.md`

- [x] Layers respected: `cmd_recent` lives in `src/cli.py` (UI), uses
  `storage.load()` and doesn't touch `src/notes.py` or `src/storage.py`.
- [x] No external dependencies (there is no `requirements.txt`).
- [x] Explicit errors: `NoteError("--limit must be a positive integer")`
  (named exception, not `None`).
- [x] No IO mixed into the domain (the feature only adds
  presentation logic).
- [x] Error message goes to `stderr` via the existing `main()` handler
  (`src/cli.py:132-134`), exit code 1.

## Compliance with `docs/conventions.md`

- [x] File header intact (`src/cli.py:1-2`: docstring +
  `from __future__ import annotations`).
- [x] Double quotes throughout the new implementation.
- [x] f-strings for interpolation (`src/cli.py:61, 67`).
- [x] `snake_case` names (`cmd_recent`, `p_recent`).
- [x] Tests use `tempfile.TemporaryDirectory()` via `setUp`/`tearDown`
  (`tests/test_cli.py:16-24`).
- [x] Descriptive test names
  (`test_recent_default_limit_orders_by_created_at_desc`,
  `test_recent_invalid_limit_negative`, etc.).
- [x] No superfluous comments.

## Checkpoints

- C1 — Harness complete: [x] (`./init.sh` exit 0, 4 base files present,
  3 docs present).
- C2 — Coherent state: [x] (the only `in_progress` feature is #7
  `cli_recent`; `progress/current.md` describes the active session).
- C3 — Code respects architecture: [x] (`src/` with the 3 foreseen modules,
  no `requirements.txt`, no debug `print()` or TODOs).
- C4 — Real verification: [x] (`tests/test_cli.py`, `test_notes.py`,
  `test_storage.py`; 27 green tests; uses `TemporaryDirectory`, no mocks).
- C5 — Session: [x] (there are no suspicious untracked files; `progress/`
  reflects the current session; the `in_progress` state is kept awaiting
  the leader who closes the feature).
- C6 — SDD: [x] (feature #7 has its `specs/cli_recent/` folder with
  `requirements.md`, `design.md`, `tasks.md`; requirements in strict
  EARS; all tasks `[x]`; each `R<n>` covered by at least one
  concrete test). *(That `specs/` folder is the legacy Kiro-style SDD
  layout, since replaced by the Gherkin flow — `project-spec.md` +
  `features/cli_recent.feature`; it no longer exists in the repo.)*

## Execution

```
./init.sh
Ran 27 tests in 0.040s
OK
```

## Required changes

None. The feature is ready for the leader to mark it `done` in
`feature_list.json`.
