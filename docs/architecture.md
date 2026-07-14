# Architecture — What "doing good work" means

> This document defines **your project's** quality standard. The reviewer
> agents (`judge`) evaluate code against this file. If it's not here, it's not
> a requirement.
>
> It ships as a **template**: the principles below are sensible defaults for a
> small, dependency-free Python project. Edit them to fit your project — add
> your layers, your invariants, your "do / don't" — before you start building.

## Principles (defaults — edit for your project)

1. **Clear, few layers.** Define the layers your project has and keep them
   few and explicit. Do not introduce additional layers (services,
   repositories, ORMs, …) until there is a concrete reason documented in
   `feature_list.json`.

   _Fill in your layers, e.g.:_
   - `<persistence>.py` — how state is stored.
   - `<domain>.py` — the domain model.
   - `<interface>.py` — the entry point (CLI, HTTP, …).

2. **No external dependencies by default.** Prefer Python's stdlib. If a
   feature genuinely requires a dependency, it is discussed first (`blocked`
   state) — this keeps the harness reproducible and the mutator
   (`tools/mutate.py`) meaningful.

3. **Explicit errors.** Functions that can fail raise named exceptions; they
   don't silently return `None`.

4. **Immutability by default.** Prefer immutable data (`@dataclass(frozen=True)`).
   Modifying = creating a new instance.

5. **Atomicity on disk.** If you persist state, write to a temp file and then
   `os.replace()`. Never leave a file half-written.

## Data flow

_Sketch how a request travels through your layers, e.g.:_

```
user ─→ <interface>  ─→  <domain>  ─→  <persistence>  ─→  storage
```

## What NOT to do (defaults — edit for your project)

- Don't use `print()` for errors. Use `sys.stderr` and a non-zero exit code.
- Don't mix IO with domain logic.
- Don't read/write persistent state inside a tight loop. Load once, modify in
  memory, save once.
- Don't add a configuration system before a feature needs one; pass paths and
  options explicitly or via a documented default constant.
