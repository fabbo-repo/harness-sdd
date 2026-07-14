# Code conventions

> Extreme homogeneity. The AI predicts better when the repository looks
> like itself everywhere.
>
> The rules below are the **defaults for the template's Python stack**. If your
> `harness.json` targets another language, replace this section with that
> language's conventions (style guide, naming, error handling) — the intent
> (homogeneity, explicit errors, small functions) carries over.

## Python style

- **Version:** Python 3.9+ (`list[str]` syntax allowed).
- **Format:** PEP 8. Lines at most 100 characters.
- **Imports:** stdlib first, then local. One line per module.
- **Strings:** double quotes `"..."` always. Single quotes only
  to escape double quotes inside.
- **f-strings** for interpolation. No `.format()` or `%`.

## Names

| Type                    | Convention        | Example               |
|-------------------------|-------------------|-----------------------|
| Modules                 | `snake_case`      | `storage.py`          |
| Classes                 | `PascalCase`      | `Record`              |
| Functions / variables   | `snake_case`      | `load_records`        |
| Constants               | `UPPER_SNAKE`     | `DEFAULT_STORE_PATH`  |
| Private                 | `_` prefix        | `_atomic_write`       |

## File structure

Each file in `src/` starts with:

```python
"""One line describing the module's purpose."""
from __future__ import annotations

# stdlib imports
import json
import os

# local imports
from src.domain import Record
```

## Tests

- One test file per module: `tests/test_<module>.py`.
- One `Test<Thing>(unittest.TestCase)` class per logical unit.
- Each test uses a `tempfile.TemporaryDirectory()` and cleans up after itself.
- Descriptive test names: `test_load_returns_empty_when_file_missing`.

## Error handling

Define your domain exceptions in one place (e.g. `src/domain.py`):

```python
class AppError(Exception):
    """Base for domain errors."""

class NotFound(AppError):
    """Raised when a non-existent entity is looked up."""
```

The entry point captures domain exceptions, prints a message to `stderr` and
exits with a non-zero code. It never propagates stack traces to the user.

## Comments

By default they are **not** written. They are only allowed when they explain a
non-obvious *why* (e.g. a documented workaround, a subtle invariant). Names should
do the rest.
