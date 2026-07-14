# Architecture — What "doing good work" means

> This document defines the quality standard. The reviewer agents
> evaluate code against this file. If it's not here, it's not a requirement.

## Principles

1. **Clear layers.** The project has three layers and only three:
   - `storage.py` — persistence (JSON on disk).
   - `notes.py` — domain model (`Note`).
   - `cli.py` — user interface (argparse).
   Do not introduce additional layers (services, repositories, ORMs) until
   there is a concrete reason documented in `feature_list.json`.

2. **No external dependencies.** Only Python's stdlib. If a feature
   requires a dependency, it is discussed first (`blocked` state).

3. **Explicit errors.** Functions that can fail (id doesn't exist,
   corrupt file) raise named exceptions, they don't return `None`.

4. **Immutability by default.** `Note` is a `@dataclass(frozen=True)`.
   Modifying = creating a new instance.

5. **Atomicity on disk.** Every write to `notes.json` is done first
   to a temp file and then `os.replace()`. Never leave the file
   half-written.

## Data flow

```
user     ─→  cli.py (argparse)
              │
              ├─ builds a Note with notes.Note.new(...)
              │
              └─→  storage.load() / storage.save()
                       │
                       └─→  .notes.json (in CWD)
```

## What NOT to do

- Don't use `print()` for errors. Use `sys.stderr` and a non-zero exit code.
- Don't mix IO with domain logic inside `notes.py`.
- Don't read/write the file on every operation inside a loop.
  Load at the start, modify in memory, save at the end.
- Don't add a configuration system. The file path is passed
  explicitly or uses the default constant.
