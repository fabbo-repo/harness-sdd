# Implementation — cli_recent

> Feature #7 of `feature_list.json`. Summary of the implementation and
> `R<n> → test` traceability required by `docs/specs.md`
> *(legacy Kiro-style SDD doc, since replaced by the Gherkin flow —
> `project-spec.md` + `features/cli_recent.feature`; this file no longer
> exists in the repo).*

## Summary of changes

- `src/cli.py`
  - New function `cmd_recent(args)`: validates `args.limit > 0` (raises
    `NoteError` otherwise), loads the notes with `storage.load()`, orders them
    by `created_at` descending, applies the slice `[: args.limit]` and
    prints each one with the format `<id>\t<created_at>\t<title>`.
  - New `recent` subparser in `build_parser()` with
    `--limit` (`type=int`, `default=5`) and `set_defaults(func=cmd_recent)`.
- `tests/test_cli.py`
  - New helper `_add_with_created_at` that writes a note directly
    into the notes file with a controlled `created_at` (necessary
    because `Note.new` uses `timespec="seconds"` and notes created in the
    same second would share a timestamp).
  - 5 new tests (see table below).

`src/notes.py` and `src/storage.py` were not touched, in accordance with
`design.md`.

## Traceability

| Requirement | Test                                                        |
|-------------|-------------------------------------------------------------|
| R1          | `test_recent_default_limit_orders_by_created_at_desc`       |
| R2          | `test_recent_custom_limit`                                  |
| R3          | `test_recent_default_limit_orders_by_created_at_desc`       |
| R4          | `test_recent_custom_limit`                                  |
| R5          | `test_recent_empty_outputs_nothing`                         |
| R6          | `test_recent_invalid_limit_zero`, `test_recent_invalid_limit_negative` |
| R7          | `test_recent_invalid_limit_zero`, `test_recent_invalid_limit_negative` |

Detail:

- **R1** (default <= 5): `test_recent_default_limit_orders_by_created_at_desc`
  creates 7 notes and checks that `recent` (no flags) prints exactly 5
  lines.
- **R2** (custom `--limit`): `test_recent_custom_limit` creates 6 notes and
  checks that `recent --limit 3` prints exactly 3 lines.
- **R3** (order by `created_at` desc):
  `test_recent_default_limit_orders_by_created_at_desc` verifies that the
  timestamps are in descending order and that the titles are the 5 most
  recent.
- **R4** (format `<id>\t<created_at>\t<title>`): `test_recent_custom_limit`
  checks that each line has exactly 3 fields separated by a
  tab and that the second one is an ISO 8601 timestamp.
- **R5** (no notes: exit 0, empty stdout): `test_recent_empty_outputs_nothing`
  runs `recent` over a file with no notes and verifies `code == 0`,
  `out == ""` and `err == ""`.
- **R6** (`--limit <= 0`: exit != 0 and message on stderr):
  `test_recent_invalid_limit_zero` (with `--limit 0`) and
  `test_recent_invalid_limit_negative` (with `--limit -3`).
- **R7** (`--limit <= 0`: doesn't modify notes): the same two tests
  compare the content of the notes file before and after (at the
  byte level and at the loaded-object level) and verify it doesn't change.

## Verification

- `./init.sh` run at the end: **27 tests OK** (5 new + 22
  pre-existing).

## Tasks

All tasks T1..T8 of `specs/cli_recent/tasks.md` *(legacy Kiro-style SDD
layout, no longer in the repo — replaced by `features/cli_recent.feature`)*
are marked `[x]` except that the reviewer may request changes.

## Status

Ready for review. **Not** marked `done` in `feature_list.json` —
that is left to the reviewer/leader per the protocol.
