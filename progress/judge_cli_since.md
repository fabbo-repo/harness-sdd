# Review — feature #12 `cli_since`

**Verdict:** APPROVED

## Scenario coverage (@s ↔ test)  (all in `tests/test_cli.py`)
- @s1 (exact inclusive bound, 23:00): [x] `test_since_includes_note_created_on_exact_date`
  (l. 278) — note `2026-05-01T23:00:00` is included; bites the inclusivity (`>=` vs `>`).
- @s2 (earlier out / later in): [x] `test_since_excludes_earlier_includes_later`
  (l. 284) — asserts `assertIn("newer")` and `assertNotIn("older")`.
- @s3 (descending order): [x] `test_since_orders_matches_by_created_at_desc` (l. 292) —
  inserts 1,3,2 and requires titles `[day-three, day-two, day-one]`.
- @s4 (format `<id>\t<created_at>\t<title>`): [x] `test_since_line_format_matches_list`
  (l. 303) — 3 fields per TAB + exact match `2\t2026-05-04T08:00:00+00:00\tsecond`.
- @s5 (invalid format `2026/05/01`): [x] `test_since_invalid_date_format_is_error`
  (l. 317) — exit!=0, empty stdout, "date" in stderr.
- @s6 (impossible date `2026-13-40`): [x] `test_since_impossible_calendar_date_is_error`
  (l. 324) — `strptime` rejects it; exit!=0, stderr mentions the date.
- @s7 (no matches): [x] `test_since_no_matches_outputs_nothing` (l. 331) —
  empty out, exit 0 (doesn't fail like `search`).
- @s8 (empty/non-existent store): [x] `test_since_empty_store_outputs_nothing` (l. 338) —
  no file, empty out, exit 0.
- @s9 (doesn't mutate): [x] `test_since_does_not_mutate_store` (l. 345) — compares bytes before/after.

## TDD discipline
- Production code without a test asking for it? NO. `cmd_since` (src/cli.py:94-104), the
  `since` subparser (l. 147-149), and the `DATE_LENGTH`/`DATE_FORMAT` constants (l. 11-12) are all
  required by concrete scenarios. `import datetime` is asked for by @s5/@s6 (strptime validation).
- Evidence of Red→Green→Refactor? YES. The log `progress/tdd_cli_since.md` documents
  9 cycles, one test at a time, with deliberate cheats (cycle 1 lists everything → cycle 2 forces
  the filter) and the "lock tests" (@s4/@s6/@s7/@s8/@s9) explain why they bite even though they pass
  on the first try. Consistent with `docs/tdd.md`.

## Quality
- `cmd_since` is short (11 lines), a single reason to change; revealing names.
- No magic numbers/literals: `DATE_LENGTH = len("YYYY-MM-DD")`, `DATE_FORMAT = "%Y-%m-%d"`.
- Correct error contract: validates the date BEFORE `storage.load()` and before printing
  (src/cli.py:95-98), raises `NoteError` → `main` (l. 162-164) writes to `sys.stderr` and
  returns 1. That's why @s5/@s6 see empty stdout even with notes present.
- Comparison by inclusive calendar date as per the spec: `n["created_at"][:DATE_LENGTH]
  >= args.date` (l. 100). Verified against `project-spec.md` §`since` (inclusive bound `>=`).
- Style consistent with `recent`/`list`: same `f"{n['id']}\t{n['created_at']}\t{n['title']}"`
  and `sorted(..., key=created_at, reverse=True)`. No shared helper was extracted (a documented
  decision to not inflate scope beyond the feature).
- Architecture respected: only touches `cli.py`, uses `storage.load()`, never `storage.save()`
  (hence @s9). No external dependencies (there is no `requirements.txt`). No debug `print()`
  or TODOs.

## Checkpoints
- C1 (harness complete, `./init.sh` exit 0): [x] — 43 tests, "Environment ready".
- C2 (coherent state, a single one in in_progress): [x] — #12 the only one in `in_progress`.
- C3 (architecture, no debug prints or deps): [x]
- C4 (real verification, tempdir, green suite): [x] — uses `TemporaryDirectory`, 43 OK.
- C5 (session): [x] — N/A for the judge (doesn't close the session).
- C6 (Gherkin contract, @s↔test, no unrequested code): [x]
- C7 (mutation): [ ] — pending; validated by `mutation_tester` after this approval.

## Required changes
None. The coverage of the 9 scenarios is real and asserts what each one says; the
TDD discipline is documented; the suite is green. Moves on to mutation testing.
