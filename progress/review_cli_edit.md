# Review — feature #6 `cli_edit`

**Verdict:** APPROVED

## Acceptance criteria

- [x] `--title` alone updates only the title → `test_edit_updates_only_title`
      (verifies `notes[0]["title"] == "new"` and `body == "body"`).
- [x] `--body` alone updates only the body → `test_edit_updates_only_body`
      (verifies the title is preserved).
- [x] Both flags update both fields → `test_edit_updates_both_fields`.
- [x] No flags → exit ≠ 0 + clear message → `test_edit_without_flags_returns_error`
      (asserts `code != 0`, `out == ""`, `err != ""`, and also that the note did
      not change on disk). Message at `cli.py:61`: `"you must pass --title and/or --body"`.
- [x] Non-existent id → exit ≠ 0 + message on stderr → `test_edit_missing_id_returns_error`
      (asserts `code != 0`, `out == ""`, `"99" in err`).
- [x] Coverage: 4 scenarios + absence of flags = 5 `test_edit_*` tests.

## Architecture (`docs/architecture.md`)

- [x] Layers respected. `cmd_edit` only uses `storage` and `notes`. Doesn't touch
      `storage.py` or `notes.py`.
- [x] No external dependencies. There is no `requirements.txt`. `cli.py` only
      imports `argparse`, `sys`, `src.storage`, `src.notes`.
- [x] Explicit errors. `NoteError` for "no flags" and `NoteNotFound` for a
      non-existent id. Both are captured in the `main()` handler.
- [x] `Note` immutability. `cli.py:65-70` builds a new `Note(...)` instance
      with `id` and `created_at` preserved; doesn't mutate the original.
- [x] Atomicity. `storage.py` intact; `cmd_edit` calls `storage.save()`
      without altering its contract.

## Conventions (`docs/conventions.md`)

- [x] PEP 8, lines ≤ 100 chars (verified with regex `^.{101,}` → 0 matches
      in `src/cli.py` and `tests/test_cli.py`).
- [x] Consistent double quotes.
- [x] f-strings (`f"edited id={args.id}"`, `f"no note with id={args.id}"`).
- [x] No decorative comments, no TODO/FIXME (grep in `src/` → 0 matches).
- [x] Correct names: `cmd_edit` (snake_case), preserves the pattern of
      `cmd_add`, `cmd_show`, etc.
- [x] `stderr` + exit 1 for domain errors: the `main()` handler
      (cli.py:116-118) captures `NoteError` (base class of `NoteNotFound`),
      prints to `sys.stderr` and returns 1.

## Verification (`docs/verification.md`)

- [x] Tests use `tempfile.TemporaryDirectory()` (inherited from `TestCli`'s
      setUp, lines 16-17).
- [x] No filesystem mocks. Only the `DEFAULT_NOTES_PATH` constant is mocked
      with `patch.object`, which is legitimate.
- [x] Tests verify concrete output: content of `notes[0]["title"]`,
      `notes[0]["body"]`, `id=1` in stdout, `"99"` in stderr, etc. There are no
      "doesn't raise an exception" asserts.

## CHECKPOINTS.md

- [x] C1 — Harness complete. `./init.sh` exit 0; the 4 base files and the 3
      docs exist.
- [x] C2 — Coherent state. 0 features in `in_progress` in
      `feature_list.json` (feature #6 = `done`). All `done` features
      have green tests. `progress/current.md` describes the active session.
- [x] C3 — Architecture. `src/` only contains `cli.py`, `notes.py`,
      `storage.py`, `__init__.py`. There is no `requirements.txt`. No debug
      prints or TODOs.
- [x] C4 — Real verification. Each module of `src/` has its test;
      `tempfile.TemporaryDirectory()` in use; 22 green tests.
- [x] C5 — Session closed properly. There are no suspicious untracked `*.tmp`
      or `__pycache__` files. Feature #6 is reflected as `done`.
      Minor note: `progress/history.md` doesn't yet have the entry for the
      #6 session, but by convention the history is appended when the session
      is closed, not when the feature is closed; the leader should add it before
      the final close.

## Final output of `./init.sh`

```
── 4. Running tests ────────────────────────────────────
test_add_creates_note_and_prints_id (test_cli.TestCli.test_add_creates_note_and_prints_id) ... ok
test_delete_missing_id_returns_error (test_cli.TestCli.test_delete_missing_id_returns_error) ... ok
test_delete_removes_note_and_confirms (test_cli.TestCli.test_delete_removes_note_and_confirms) ... ok
test_edit_missing_id_returns_error (test_cli.TestCli.test_edit_missing_id_returns_error) ... ok
test_edit_updates_both_fields (test_cli.TestCli.test_edit_updates_both_fields) ... ok
test_edit_updates_only_body (test_cli.TestCli.test_edit_updates_only_body) ... ok
test_edit_updates_only_title (test_cli.TestCli.test_edit_updates_only_title) ... ok
test_edit_without_flags_returns_error (test_cli.TestCli.test_edit_without_flags_returns_error) ... ok
test_list_empty_outputs_nothing (test_cli.TestCli.test_list_empty_outputs_nothing) ... ok
test_list_shows_existing_notes (test_cli.TestCli.test_list_shows_existing_notes) ... ok
test_search_finds_matching_notes (test_cli.TestCli.test_search_finds_matching_notes) ... ok
test_search_is_case_insensitive (test_cli.TestCli.test_search_is_case_insensitive) ... ok
test_search_no_match_returns_error (test_cli.TestCli.test_search_no_match_returns_error) ... ok
test_show_missing_id_returns_error (test_cli.TestCli.test_show_missing_id_returns_error) ... ok
test_show_prints_title_date_body (test_cli.TestCli.test_show_prints_title_date_body) ... ok
test_new_assigns_id_one_when_no_existing (test_notes.TestNote.test_new_assigns_id_one_when_no_existing) ... ok
test_new_increments_id (test_notes.TestNote.test_new_increments_id) ... ok
test_note_is_frozen (test_notes.TestNote.test_note_is_frozen) ... ok
test_to_dict_round_trip (test_notes.TestNote.test_to_dict_round_trip) ... ok
test_load_returns_empty_when_file_missing (test_storage.TestStorage.test_load_returns_empty_when_file_missing) ... ok
test_save_is_atomic (test_storage.TestStorage.test_save_is_atomic) ... ok
test_save_then_load_roundtrip (test_storage.TestStorage.test_save_then_load_roundtrip) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.020s

OK
[OK]    All tests pass

── 5. Summary ──────────────────────────────────────────
[OK]    Environment ready. You can start working.
```

22 green tests, matching the implementer's report (17 previous + 5 new).

## Close

Feature #6 `cli_edit` literally meets the 6 acceptance criteria,
respects the architecture, the conventions and the verification protocol.
The `status: "done"` mark in `feature_list.json` is legitimate and can
be kept. Minor (non-blocking) recommendation to the leader: add the session
entry in `progress/history.md` before closing the session.
