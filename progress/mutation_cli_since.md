# Mutation — feature #12 `cli_since` (`since` command)

**Verdict:** PASS
**Score (feature lines):** killed/total = 100% (threshold: 100% over new/touched lines)
**Score (whole file `src/cli.py`):** 34/38 = 89.5% (informative; includes out-of-scope legacy code)

## Command run
```bash
python3 tools/mutate.py src/cli.py --max 200
```

## Feature scope (`progress/tdd_cli_since.md` → "Touched files")
New/touched lines by `cli_since` in `src/cli.py`:
- 11-12 → constants `DATE_LENGTH`, `DATE_FORMAT`
- 94-104 → `cmd_since` (validation, filter, order, printing, `return 0`)
- 147-149 → `since` subparser

## Mutants over the feature lines — ALL KILLED (100%)
- `src/cli.py:100`  operator  `'>=' -> '>'`            → killed
  (killed by `test_since_includes_note_created_on_exact_date` / `..._excludes_earlier_includes_later`:
   with `>` the exact inclusive bound would leave out the note from the exact day.)
- `src/cli.py:101`  keyword   `'True' -> 'False'`       → killed
  (killed by `test_since_orders_matches_by_created_at_desc`: the order would stop being descending.)
- `src/cli.py:104`  number    `'0' -> '1'`              → killed
- `src/cli.py:104`  return    `'return 0' -> 'return None'` → killed
  (any success scenario expects exit 0; `1`/`None` breaks the contract.)

Lines 11-12 (constants) and 147-149 (subparser) generate no mutants
mutable by the catalog (definitions/strings), or their mutants don't compile.
Date validation (line 96, `strptime` + `ValueError`) is covered by
`test_since_invalid_date_format_is_error` and `test_since_impossible_calendar_date_is_error`,
but `strptime`/`raise` produce no mutants in the current catalog.

## Surviving mutants — OUT OF SCOPE for the feature (legacy/shared code)
Measured but do NOT block (rule from `docs/mutation-testing.md`: the threshold only
applies to new/touched lines; untouched legacy is measured, not required).
None belong to `cmd_since` or its subparser:

- `src/cli.py:64`  number  `'0' -> '1'`   → in `cmd_recent` (feature #11, not touched by `since`)
  Missing: a test that distinguishes `--limit 0` (error) from `--limit 1`.
- `src/cli.py:68`  number  `'0' -> '1'`   → in `cmd_recent` (empty-store branch → `return 0`)
  Missing: a test that asserts exact exit 0 of `recent` with an empty store.
- `src/cli.py:115` keyword `'True' -> 'False'` → in `build_parser` (subparsers `required=True`; shared infrastructure)
  Missing: a test that asserts invoking without a subcommand is an error (exit != 0).
- `src/cli.py:164` return `'return 1' -> 'return None'` → in `main` (`NoteError` error branch; shared infrastructure)
  Missing: a test that asserts exact exit code == 1 in `main`'s error branch.

> These 4 survivors are the `tdd_craftsman`'s job for their respective features
> (`recent` and/or the `main`/`build_parser` contract), not `cli_since`'s.

## Conclusion
The mutation score of the `cli_since` feature over its new/touched lines
is **100%**: every mutant generated in `cmd_since` and its path dies with the
current suite. It meets the threshold. **PASS.**
