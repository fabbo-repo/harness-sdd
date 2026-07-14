# Implementer report — Feature #6 `cli_edit`

## Modified files

- `src/cli.py` — added `cmd_edit` (load → mutate → save → print) and `edit`
  subparser with `id` (positional int) and optional `--title` / `--body` flags.
- `tests/test_cli.py` — added 5 tests: success of each flag separately,
  both flags together, non-existent id and absence of flags.
- `feature_list.json` — feature #6 moved from `in_progress` to `done`.

## Design

- **Absence of flags:** early check `if args.title is None and
  args.body is None: raise NoteError("you must pass --title and/or --body")`.
  The default arguments are `None` (not `""`), because an empty string is a
  legitimate value for `--body`. `NoteError` is captured by the existing
  generic handler in `main()`, which prints to stderr and exits with code 1.
- **Non-existent id:** I iterate `notes` by index; if I don't find the `id`,
  I raise `NoteNotFound` (same pattern as `cmd_show` and `cmd_delete`).
- **Immutability:** the note is replaced by building a new `Note(...)`
  instance with `id` and `created_at` preserved and the changed fields
  taken from `args` only when they are not `None`. Then `notes[i] =
  updated.to_dict()` and `storage.save(notes)`. `Note` stays `frozen`
  because we never mutate the original instance.
- **Confirmation:** `print(f"edited id={args.id}")` (the tests look for
  `id=1`, following the pattern of `cmd_delete` which prints `id=...`).
- No new dependencies, no new layers, without touching `notes.py` or
  `storage.py`.

## Output of the last `./init.sh`

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

22 green tests (17 previous + 5 new for `cli_edit`).

## Final state in `feature_list.json`

Feature #6 `cli_edit` → `status: "done"`. No features remain in `in_progress`.
