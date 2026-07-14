# project-spec.md — notes-cli

> A **conversed** specification, not a dictated one. Each section is born from
> a debate between the human and the `spec_partner`: what it does, what the
> exact contract is, what edge cases exist, and what alternatives were
> discarded and why. From here the `gherkin_author` distills
> `features/<name>.feature`.

## Project purpose

`notes-cli` is a minimalist command-line note manager. The code is
deliberately simple: the repo teaches **process** (Harness Engineering,
craftsman editing), not domain complexity.

## Global decisions

- **No external dependencies.** `requirements.txt` stays empty. Everything is
  done with the stdlib (`argparse`, `json`, `tempfile`, `unittest`). This
  keeps the harness reproducible and enables the homemade mutator
  (`tools/mutate.py`). *Discarded alternative:* `click` + `pytest-bdd` —
  more ergonomic, but it introduces dependencies and hides the mechanism.
- **Atomic JSON store.** The notes live in a single JSON file
  (`NOTES_FILE`, defaulting to `.notes.json`). Writing is atomic
  (temp file + `os.replace`). *Reason:* never leave the file half-written
  if the process dies.
- **Uniform error contract.** Domain errors (`NoteError`,
  `NoteNotFound`) are printed to **stderr** and return a **non-zero exit
  code**. Useful output goes to **stdout**. This makes each command composable
  and testable by its observable contract.
- **One note = `{id, title, body, created_at}`.** Incremental `id`,
  `created_at` in ISO 8601.

## Commands

### `count` — count notes  *(feature #8, under construction)*

- **Purpose:** answer "how many notes do I have?" at a glance.
- **Behavior:** prints a single integer, the total number of notes.
- **Contract:**
  - `python -m src.cli count` → stdout: the total as an integer, exit code 0.
  - Empty or non-existent store → stdout `0`, exit code 0.
  - The command **does not modify** the notes file (read-only).
- **Edge cases:**
  1. No notes file → `0`.
  2. File with N notes → exactly `N` (not "≥1", the precise number).
  3. Idempotent: running it doesn't change the store.
- **Decisions:**
  - *Output = bare integer, no text* (`3`, not `Total: 3`). Reason:
    composable with `| wc`, `$(...)`, etc. *Discarded alternative:* a
    descriptive line — friendlier, less composable. Composability wins for
    coherence with `list`/`recent`.
  - *Non-existent store counts as 0*, not as an error. Reason: "no notes
    yet" is a valid state, not a failure. Consistent with `list`, which
    also doesn't fail when there are no notes.

### `recent` — N most recent notes  *(feature #7, done)*

- **Purpose:** see the latest notes without listing everything.
- **Contract:**
  - `python -m src.cli recent` → up to 5 notes, `created_at` desc order.
  - `--limit K` changes the number.
  - `--limit <= 0` → message on stderr, non-zero exit code.
  - Empty store → prints nothing, exit code 0.
  - Per-line format: `<id>\t<created_at>\t<title>` (same as `list`).
- **Decision:** same format as `list` so as not to invent a second
  presentation contract.

### `since` — filter by date  *(feature #12)*

- **Purpose:** see "what I jotted down since Monday" — the notes created on
  a given calendar date or after it.
- **Behavior:** receives a `YYYY-MM-DD` date, validates it as a real calendar
  date, and lists the notes whose creation date is equal to or later than the
  given one, ordered from most recent to oldest.
- **Contract:**
  - `python -m src.cli since 2026-05-01` → stdout: the notes with a creation
    date `>= 2026-05-01`, one per line, format
    `<id>\t<created_at>\t<title>` (identical to `list`/`recent`), ordered by
    `created_at` **descending**; exit code 0.
  - The argument is parsed with `datetime.strptime(arg, "%Y-%m-%d")`. If it is
    NOT a real and valid calendar date —whether due to incorrect format
    (`2026/05/01`, `may`) or an impossible date (`2026-13-40`,
    `2026-02-30`)— → a clear message on **stderr**, non-zero exit code.
  - Comparison by **calendar date, inclusive bound**: the date part of
    `created_at` is taken (its first 10 characters / `.date()`)
    and the note is included if that date is **>=** the given date. A note
    created at 23:00 on the exact day counts.
  - No note meets the criterion → prints nothing, exit code 0
    (consistent with `list`/`recent`).
  - Empty or non-existent store → prints nothing, exit code 0.
  - The command **does not modify** the notes file (read-only).
- **Edge cases:**
  1. Exact inclusive bound: a note created right on the given date is included
     in the result (even if its time is 23:00).
  2. No matches: no note `>=` the date → empty stdout, exit
     code 0.
  3. Date with invalid format (`2026/05/01`, `may`) → stderr, exit code
     != 0.
  4. Date with correct format but impossible (`2026-13-40`, `2026-02-30`)
     → stderr, non-zero exit code.
  5. Empty or non-existent notes file → empty stdout, exit code 0.
  6. Idempotent: running it doesn't change the store.
- **Decisions:**
  - *Validation with `strptime("%Y-%m-%d")`, rejecting impossible dates.*
    Reason: the user deserves a clear error for `2026-13-40` or
    `2026-02-30`, not a silent filtering over an absurd date.
    *Discarded alternative:* validating only the regex pattern `YYYY-MM-DD` —
    simpler, but lets impossible calendar dates through without warning.
  - *Comparison by calendar date with inclusive bound (`>=`).*
    Reason: the user's mental model is "day", not "instant"; a note
    created at 23:00 on the given day should count. The date part of
    `created_at` is compared against the given date. *Discarded alternative:*
    comparing full instants by treating the date as midnight —
    type-consistent, but it would exclude same-day notes created
    after 00:00, contradicting the intuition of "since Monday".
  - *Same output format and descending order as `recent`.* Reason: don't
    invent a second presentation contract; `since` is a `list` filtered by
    date. Consistent with the global decision of composable output.

### Already existing commands (summarized contract)

`add`, `list`, `show`, `delete`, `search`, `edit` — see `src/cli.py`. They
were built before adopting this flow; their contract is implicit in their
tests. They are not rewritten unless a new feature touches them.

## Pending features (not yet debated in detail)

- `cli_export` (#9) — export to Markdown.
- `cli_stats` (#10) — aggregate statistics.
- `cli_clear` (#11) — destructive deletion with confirmation.

Each will enter through its own conversation with the `spec_partner` before
having a `.feature`.

## Open questions

_(none for now)_
