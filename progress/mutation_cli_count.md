# Mutation — feature #8 `cli_count`

**Verdict:** PASS
**Score (feature lines):** killed/total = 2/2 = 100% (threshold: 100%)
**Score (whole file, informative):** killed/total = 30/34 = 88.2%

## Verified pre-conditions

- Judge: APPROVED (`progress/judge_cli_count.md:2`).
- `./init.sh`: exit 0, 34 tests green.
- File touched by the feature: `src/cli.py`, function `cmd_count`
  (`src/cli.py:90-93`) and `count` subparser (`src/cli.py:130-131`), per
  `progress/tdd_cli_count.md`.

## Command run

```bash
python3 tools/mutate.py src/cli.py
```

34 valid mutants (0 discarded for not compiling). No truncation, no
`--max`: the whole file was measured.

## Mutants over the FEATURE LINES (`cmd_count` + `count` subparser)

All KILLED. The 100% threshold over new/touched lines is met.

- `src/cli.py:93` number (`'0' -> '1'`) → **killed** [18/34].
  `print(len(notes))` mutated to `print(len(notes) + 1)`-equivalent is killed by
  `test_count_empty_store_prints_zero` (expects `"0\n"`),
  `test_count_single_note_prints_one` (`"1\n"`) and
  `test_count_three_notes_prints_three` (`"3\n"`).
- `src/cli.py:93` return (`'return 0' -> 'return None'`) → **killed** [31/34].
  Distinguished by any test that asserts `code == 0` (@s1..@s4).
- `count` subparser (`src/cli.py:130-131`): generates no textual mutants from
  the catalog (there are no comparisons, numbers or returns in those two lines),
  but its correct existence is covered: without the subparser, the 7 `count`
  tests would fail with `invalid choice: 'count'` (a real red in cycle 1,
  `progress/tdd_cli_count.md:11-13`). Mutating `func=cmd_count` is not in the
  mutator's catalog; it falls outside the scope of the textual threshold.

Total textual mutants on the feature lines: 2 — both killed → 100%.

## Surviving mutants in LEGACY CODE (measured, do NOT block)

None fall in `cmd_count` or its subparser. Reported for hygiene:

- `src/cli.py:60` number (`'0' -> '1'`) — function `cmd_recent`
  (`if args.limit <= 0` → `if args.limit <= 1`).
  Missing: a test that exercises `recent --limit 1` and verifies it does NOT
  raise `NoteError` (limit 1 is still valid). Legacy, outside this feature.
- `src/cli.py:64` number (`'0' -> '1'`) — function `cmd_recent`
  (`return 0` of the "no notes" case → `return 1`).
  Missing: a test that asserts `code == 0` when requesting `recent` over an
  empty store. Legacy.
- `src/cli.py:98` keyword (`'True' -> 'False'`) — function `build_parser`
  (`add_subparsers(..., required=True)` → `required=False`).
  Missing: a test that invokes the CLI without a subcommand and expects an error
  (non-zero exit code). Shared parser infra, not added by this feature. Legacy.
- `src/cli.py:143` return (`'return 1' -> 'return None'`) — function `main`
  (`NoteError` capture branch).
  Missing: a test that verifies the exit code on a `NoteError` is exactly
  `1` (today stderr is asserted but not `code == 1` on the `main` path).
  Legacy.

None of these four is a genuine equivalent: they all change observable
behavior (exit codes or argument validation) and are killable with additional
tests. But they belong to `cmd_recent`, `build_parser` and `main`, not to the
`cli_count` feature, so they are measured and do not block (rule from
`docs/mutation-testing.md:55-57`).

## Conclusion

The `cli_count` feature (`cmd_count` + `count` subparser) has 100% killed
mutants over its new/touched lines. PASS. The 4 survivors are holes in legacy
code, candidates for future `tdd_craftsman` work, outside the scope of this
feature.
