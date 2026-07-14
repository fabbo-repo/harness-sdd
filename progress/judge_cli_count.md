# Review — feature #8 `cli_count`

**Verdict:** APPROVED

## Scenario coverage (@s ↔ test)

- @s1 (empty store → "0"): [x] covered by `test_count_empty_store_prints_zero`
  (`tests/test_cli.py:229`). Asserts `out == "0\n"` and `code == 0`.
- @s2 (non-existent store → "0"): [x] covered by `test_count_missing_store_prints_zero`
  (`tests/test_cli.py:235`). Verifies `not os.path.exists(self.path)` before
  running, then `out == "0\n"` and `code == 0`.
- @s3 (one note → "1"): [x] covered by `test_count_single_note_prints_one`
  (`tests/test_cli.py:241`). `out == "1\n"`, `code == 0`.
- @s4 (three notes → exact "3"): [x] covered by `test_count_three_notes_prints_three`
  (`tests/test_cli.py:247`). `out == "3\n"`, `code == 0`.
- @s5 (bare integer, no "Total"): [x] covered by
  `test_count_output_is_bare_integer_without_text` (`tests/test_cli.py:256`).
  `out.strip() == "2"` and `assertNotIn("Total", out)`.
- @s6 (doesn't mutate the file, byte by byte): [x] covered by
  `test_count_does_not_mutate_store` (`tests/test_cli.py:263`). Compares the
  file's bytes before/after with `assertEqual(before_bytes, f.read())`.
- @s7 (idempotent, file still absent): [x] covered by
  `test_count_does_not_create_store_when_missing` (`tests/test_cli.py:272`).
  Verifies `not os.path.exists(self.path)` before and after.

All 7 scenarios have at least one concrete, green test. The log's map
(`progress/tdd_cli_count.md:70-76`) matches the real tests.

## TDD discipline

- **Production code without a test asking for it?** NO. Total production is 4
  effective lines: `cmd_count` (`src/cli.py:90-93`) and the subparser
  `p_count = sub.add_parser("count", ...)` + `set_defaults`
  (`src/cli.py:130-131` of the diff). Both required by @s1/@s3. The log
  documents that only cycles 1 and 3 introduced production code
  (`progress/tdd_cli_count.md:60-66`); the other tests are guards that pass
  by construction, with no "for the future" code.
- **Evidence of Red→Green→Refactor?** YES. Log with 7 cycles
  (`progress/tdd_cli_count.md:8-58`). Cycle 1: real red
  (`invalid choice: 'count'`) → `print(0)` (constant fake, Law 3).
  Cycle 3: real red (expected `"1\n"`, got `"0\n"`) → generalization to
  `print(len(storage.load()))`. No refactors while red (there was nothing to
  refactor; a 2-line function).
- **Inflated scope?** NO. There are no flags, formats or descriptive text that
  no scenario asks for. `cmd_count` doesn't call `storage.save` (consistent
  with @s6/@s7).

## Quality

- `cmd_count` (`src/cli.py:90-93`): short function (a single reason to change),
  revealing name, no magic numbers, no duplication. Follows the pattern of
  its siblings `cmd_edit`/`cmd_recent` (`storage.load()` with no argument uses
  `DEFAULT_NOTES_PATH`, which is what the tests patch — `storage.py:11-12`).
- Respects `docs/architecture.md`: the `cli.py` layer delegates to `storage.load()`,
  doesn't touch the domain or rewrite the file. No debug `print()` or TODOs.
- Error contract: `count` has no error paths (a read-only operation with no
  arguments), so `return 0` is always correct; there are no domain exceptions
  to capture here. Consistent with `docs/conventions.md`.
- Style: double quotes, `from __future__ import annotations` already present in
  the module, lines < 100. No objections.

## Checkpoints

- C1 (harness complete): [x] — `./init.sh` exit 0, 34 tests green.
- C2 (coherent state): [x] — `cli_count` is the only `in_progress`
  (`feature_list.json:124`); `done` features with passing tests.
- C3 (respects architecture): [x] — only `cli.py` is touched; no external deps;
  no debug `print()` or TODOs.
- C4 (real verification): [x] — tests with `tempfile.TemporaryDirectory`
  (`tests/test_cli.py:16`), no fs mocks; `unittest discover` shows 34
  tests, all green.
- C5 (session closed): [x] (partial, non-blocking for this review) —
  TDD log present; no `*.tmp` or `__pycache__` observed outside
  `.gitignore` in the touched tree. The formal close (history, marking `done`)
  comes after judge + mutation_tester by workflow design.
- C6 (Gherkin contract): [x] — `features/cli_count.feature` with @s1..@s7,
  each `Then` measurable; `@s → test` map in `progress/tdd_cli_count.md`; no
  production code unrequested by a red test.
- C7 (mutation): [ ] — outside the judge's scope; validated by the
  `mutation_tester` after this approval.

## Required changes

None. The work survives: full coverage of @s1..@s7, TDD discipline
without inflated scope, craftsman quality and `./init.sh` green.
