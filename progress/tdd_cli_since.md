# TDD log — feature #12 `cli_since` (`since` command)

Feature in progress: #12 — cli_since
Scenarios walked: @s1..@s9 (from `features/cli_since.feature`).

> Discipline: one red test at a time → minimal production → refactor while green.
> Base pattern: `cmd_recent` (same line format and descending order).
> Final state: `./init.sh` green, 43 tests OK (34 base + 9 new).
> Feature status: stays `in_progress` (not marked `done`: pending judge + mutation).

## Red-Green-Refactor cycles

### Cycle 1 — @s1 (exact inclusive bound)
- RED: `test_since_includes_note_created_on_exact_date` — a note at 23:00 on the
  exact day must be included. Fails: the `since` subcommand doesn't exist (argparse SystemExit 2).
- GREEN: I add `cmd_since` (lists all notes, deliberate cheat) + `since` subparser
  with positional argument `date`.
- REFACTOR: nothing (trivial).

### Cycle 2 — @s2 (earlier out, later in)
- RED: `test_since_excludes_earlier_includes_later` — `2026-04-30` out,
  `2026-05-02` in. Fails: the cheat prints both.
- GREEN: filter by calendar date `n["created_at"][:DATE_LENGTH] >= args.date`.
- REFACTOR: I introduce the constant `DATE_LENGTH = len("YYYY-MM-DD")` (no magic numbers).

### Cycle 3 — @s3 (descending order)
- RED: `test_since_orders_matches_by_created_at_desc` — notes added in
  order 1,3,2; expected output 3,2,1. Fails: it came out in insertion order.
- GREEN: `sorted(matches, key=created_at, reverse=True)` (same as `cmd_recent`).
- REFACTOR: nothing.

### Cycle 4 — @s4 (format `<id>\t<created_at>\t<title>`)
- RED/lock: `test_since_line_format_matches_list` — verifies 3 fields separated
  by TAB. Passes on the first try (the format was already correct since @s1). Verified it
  bites: a space separator would give 1 field and break the assert (`len==3`).
- GREEN/REFACTOR: no production changes (contract already met).

### Cycle 5 — @s5 (invalid date format `2026/05/01`)
- RED: `test_since_invalid_date_format_is_error` — exit != 0, empty stdout,
  stderr mentions "date". Fails: it came out exit 0 with no error.
- GREEN: I validate with `datetime.strptime(args.date, DATE_FORMAT)`; on `ValueError`
  I raise `NoteError` (captured by `main` → stderr + exit 1). `DATE_FORMAT` constant.
- REFACTOR: nothing.

### Cycle 6 — @s6 (impossible date `2026-13-40`)
- RED/lock: `test_since_impossible_calendar_date_is_error`. Passes on the first try
  because `strptime` already rejects impossible calendar dates. Verified it
  bites the decision: a regex `\d{4}-\d{2}-\d{2}` WOULD ACCEPT `2026-13-40`; only
  `strptime` rejects it. The test guards that decision (format vs calendar validity).
- GREEN/REFACTOR: no changes (covered by @s5's validation).

### Cycle 7 — @s7 (no matches → empty, exit 0)
- RED/lock: `test_since_no_matches_outputs_nothing` — only one earlier note.
  Passes with the current filter. Distinguishes `since`'s contract (empty + exit 0)
  from `search`'s (error on no-match): bites if someone made `since`
  fail like `search`.
- GREEN/REFACTOR: no changes.

### Cycle 8 — @s8 (empty/non-existent store → empty, exit 0)
- RED/lock: `test_since_empty_store_outputs_nothing` — no notes file.
  Passes because `storage.load()` returns `[]` for a non-existent file.
- GREEN/REFACTOR: no changes.

### Cycle 9 — @s9 (doesn't modify the store)
- RED/lock: `test_since_does_not_mutate_store` — compares the file byte by byte
  before/after. Passes because `cmd_since` never calls `storage.save()`. Guards
  against regressions (would fail if someone added a write).

## Final REFACTOR (while green)
- `cmd_since` stays short, with revealing names and constants (`DATE_LENGTH`,
  `DATE_FORMAT`) instead of magic numbers/literals. No comments (unnecessary).
- Extracting a shared print helper with `list`/`search`/`recent` was deliberately
  avoided: it would widen the scope to code outside this feature.

## Traceability @s → test  (all in `tests/test_cli.py`)
- @s1 (exact inclusive bound)          → `test_since_includes_note_created_on_exact_date`
- @s2 (earlier out, later in)          → `test_since_excludes_earlier_includes_later`
- @s3 (descending order)               → `test_since_orders_matches_by_created_at_desc`
- @s4 (line format = list)             → `test_since_line_format_matches_list`
- @s5 (invalid date format)            → `test_since_invalid_date_format_is_error`
- @s6 (impossible calendar date)       → `test_since_impossible_calendar_date_is_error`
- @s7 (no matches → empty)             → `test_since_no_matches_outputs_nothing`
- @s8 (empty store → empty)            → `test_since_empty_store_outputs_nothing`
- @s9 (doesn't modify the store)       → `test_since_does_not_mutate_store`

## Close — DONE (2026-06-02)
- judge: APPROVED (`progress/judge_cli_since.md`).
- mutation: PASS, score 100% over the feature lines (`progress/mutation_cli_since.md`).
- `./init.sh` re-verified green: 43 tests OK.
- Feature #12 status changed to `"done"` in `feature_list.json`.

## Touched files
- `src/cli.py`: `cmd_since`, `since` subparser, `DATE_LENGTH`/`DATE_FORMAT` constants,
  `datetime` import.
- `tests/test_cli.py`: 9 new tests (reuse `_add_with_created_at`, `_run`).
