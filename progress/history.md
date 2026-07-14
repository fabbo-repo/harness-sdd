# Historical log (append-only)

> Every time a session is closed, its summary is added here.
> Don't edit previous entries. You only append at the end.

---

## 2026-04-20 — Project bootstrap
- **Agent:** human (Martín)
- **Changes:** initial harness structure (AGENTS.md, init.sh, feature_list.json, docs/).
- **Result:** environment ready. `./init.sh` green.

## 2026-04-22 — Feature 1: storage_layer
- **Agent:** implementer #1
- **Plan:** create `src/storage.py` with atomic `load()` / `save()` and tests.
- **Changes:** `src/storage.py`, `tests/test_storage.py`.
- **Verification:** `./init.sh` green, 3 tests pass.
- **Close:** feature 1 marked `done`.

## 2026-04-23 — Feature 2: note_model
- **Agent:** implementer #2
- **Plan:** `Note` dataclass with `Note.new(title, body)` and dict serialization.
- **Changes:** `src/notes.py`, `tests/test_notes.py`.
- **Verification:** `./init.sh` green.
- **Close:** feature 2 marked `done`.

## 2026-04-25 — Feature 3: cli_add_list
- **Agent:** implementer #3, reviewed by reviewer-agent.
- **Plan:** `src/cli.py` with argparse, `add` and `list` commands.
- **Changes:** `src/cli.py`, `tests/test_cli.py`.
- **Verification:** `./init.sh` green, 7 tests pass.
- **Close:** feature 3 marked `done`. Next: feature 4 (show/delete).

## 2026-04-27 — Feature 4: cli_show_delete
- **Agent:** Claude Opus 4.7
- **Plan:** add `cmd_show` and `cmd_delete` in `src/cli.py` with `NoteNotFound` handling (stderr + exit 1).
- **Changes:** `src/cli.py` (`show`/`delete` subcommands and `NoteError` capture in `main`), `tests/test_cli.py` (4 new tests: success and failure of each command, stderr capture).
- **Verification:** `./init.sh` green, 14 tests pass.
- **Close:** feature 4 marked `done`. Next: feature 5 (search).

## 2026-04-27 — Feature 5: cli_search
- **Agent:** Claude Opus 4.6
- **Plan:** add `cmd_search` in `src/cli.py` with case-insensitive search in title and body. No matches → NoteNotFound (stderr + exit 1).
- **Changes:** `src/cli.py` (`search` subcommand with `cmd_search`), `tests/test_cli.py` (3 new tests: match, no-match, case-insensitivity).
- **Verification:** `./init.sh` green, 17 tests pass.
- **Close:** feature 5 marked `done`. All features completed.

## 2026-04-29 — Feature 6: cli_edit
- **Agent:** Claude Opus 4.7 (leader) → implementer → reviewer.
- **Plan:** add `cmd_edit` in `src/cli.py` with optional `--title` and `--body`; no flags → `NoteError`; non-existent id → `NoteNotFound`.
- **Changes:** `src/cli.py` (`edit` subcommand and `cmd_edit` that builds a new `Note` instance preserving `id`/`created_at`), `tests/test_cli.py` (5 tests: each flag, both together, non-existent id, absence of flags).
- **Verification:** `./init.sh` green, 22 tests pass. Reviewer APPROVED (`progress/review_cli_edit.md`).
- **Close:** feature 6 marked `done`. All project features completed.

## 2026-05-13 — Feature 7: cli_recent
- **Agent:** Claude Opus 4.7 (leader) → spec_author → implementer → reviewer.
- **Plan:** execute the 8 tasks of `specs/cli_recent/tasks.md`: add `cmd_recent` and `recent` subparser in `src/cli.py`, cover R1–R7 with tests, validate traceability and `./init.sh`.
- **Changes:** `src/cli.py` (`cmd_recent` + subparser with `--limit`), `tests/test_cli.py` (5 new tests: default order, custom limit, empty file, limit 0, negative limit; `_add_with_created_at` helper).
- **Verification:** `./init.sh` green, 27 tests pass. Reviewer APPROVED (`progress/review_cli_recent.md`); traceability in `progress/impl_cli_recent.md`.
- **Close:** feature 7 marked `done`. Next: feature 8 (cli_count).

## 2026-06-02 — Feature 8: cli_count
- **Agent:** Claude Opus 4.8 (tdd_craftsman), `uncle-bob-harness` branch.
- **Walkthrough:** Gherkin (`features/cli_count.feature`, @s1..@s7) → strict TDD Red-Green-Refactor (7 cycles, one test at a time; only cycles 1 and 3 introduced production code) → judge **APPROVED** (`progress/judge_cli_count.md`) → mutation **100%** over feature lines (`progress/mutation_cli_count.md`, 2/2 mutants killed).
- **Changes:** `src/cli.py` (`cmd_count` + `count` subparser), `tests/test_cli.py` (7 tests, one per scenario), `features/cli_count.feature` (contract @s1..@s7).
- **Traceability @s → test:**
  - @s1 (empty store → "0")                 → `test_count_empty_store_prints_zero`
  - @s2 (non-existent store → "0")          → `test_count_missing_store_prints_zero`
  - @s3 (one note → "1")                    → `test_count_single_note_prints_one`
  - @s4 (three notes → exact "3")           → `test_count_three_notes_prints_three`
  - @s5 (bare integer, no "Total")          → `test_count_output_is_bare_integer_without_text`
  - @s6 (doesn't mutate the file, byte by byte) → `test_count_does_not_mutate_store`
  - @s7 (idempotent, file still absent)     → `test_count_does_not_create_store_when_missing`
- **Verification:** `./init.sh` green, 34 tests pass.
- **Close:** feature 8 marked `done`. Next: feature 9 (cli_export).

## 2026-06-02 — Feature 12: cli_since
- **Agent:** Claude Opus 4.8 (craftsman_lead), `uncle-bob-harness` branch. Orchestrated the full pipeline: spec_partner → gherkin_author → ⏸ human approval → tdd_craftsman → judge → mutation_tester.
- **Spec conversation:** 2 decisions debated and closed with the human — (1) validate a real date with `strptime("%Y-%m-%d")` (rejects invalid format AND impossible dates like `2026-13-40`); (2) comparison by calendar date (first 10 chars of `created_at`), inclusive bound `>=`. Recorded in `project-spec.md` (`since` section).
- **Walkthrough:** Gherkin (`features/cli_since.feature`, @s1..@s9) → strict TDD Red-Green-Refactor (9 cycles, one test at a time; production introduced in cycles 1, 2, 3 and 5) → judge **APPROVED** (`progress/judge_cli_since.md`) → mutation **100%** over feature lines (`progress/mutation_cli_since.md`; the file's 4 surviving mutants are out of scope, in `cmd_recent`/`build_parser`/`main`).
- **Changes:** `src/cli.py` (`cmd_since` + `since` subparser, `DATE_LENGTH`/`DATE_FORMAT` constants, `datetime` import), `tests/test_cli.py` (9 new tests), `features/cli_since.feature` (contract @s1..@s9), `project-spec.md`.
- **Traceability @s → test:**
  - @s1 (exact inclusive bound)          → `test_since_includes_note_created_on_exact_date`
  - @s2 (earlier out, later in)          → `test_since_excludes_earlier_includes_later`
  - @s3 (descending order)               → `test_since_orders_matches_by_created_at_desc`
  - @s4 (line format = list)             → `test_since_line_format_matches_list`
  - @s5 (invalid date format)            → `test_since_invalid_date_format_is_error`
  - @s6 (impossible calendar date)       → `test_since_impossible_calendar_date_is_error`
  - @s7 (no matches → empty)             → `test_since_no_matches_outputs_nothing`
  - @s8 (empty store → empty)            → `test_since_empty_store_outputs_nothing`
  - @s9 (doesn't modify the store)       → `test_since_does_not_mutate_store`
- **Verification:** `./init.sh` green, 43 tests pass.
- **Close:** feature 12 marked `done`. Next: feature 9 (cli_export).
