# Mutation testing — validate that the tests bite

> "Mutation testing is resource-heavy, but the ROI on code correctness is
> worth every cycle." / "We are shifting from a bottleneck of human typing
> speed to a bottleneck of compute-driven validation."

## The problem it solves

A green suite says "the code doesn't blow up with these inputs". It does
**not** say "the tests would fail if the code were wrong". A test without
strong asserts always passes and protects nothing.

Mutation testing measures it the other way around: it introduces a small
defect into the code (a *mutant*) and observes the suite.

- If **some test fails** → the mutant is **killed**. Good: the net caught
  the defect.
- If **all tests pass** → the mutant **survives**. Bad: there's a hole.
  An assert or a case is missing.

**Mutation score** = `killed / total`. The higher, the more the tests bite.

## This repo's mutator: `tools/mutate.py` (language-agnostic)

Dependency-free and **works on any language**. Instead of parsing a specific
language's AST, it mutates **text** and decides KILLED vs SURVIVED purely by
the **exit code of your test command** (from `harness.json`). The script:

1. Reads `test_command` and `line_comment` from `harness.json`.
2. Reads the target file and finds mutation sites, applying **one by one** a
   small catalog of operators/keywords common across languages:

   | Category           | Mutations                              |
   |--------------------|----------------------------------------|
   | Comparison         | `==` ↔ `!=`, `<=` → `<`, `>=` → `>`     |
   | Boolean connectors | `&&` ↔ `\|\|`, `and` ↔ `or`             |
   | Arithmetic         | ` + ` ↔ ` - `                          |
   | Booleans           | `true` ↔ `false`, `True` ↔ `False`     |

   Whole-line comments (the `line_comment` prefix) are skipped.
3. For each mutant: writes the mutated file, runs `test_command`, restores
   the original. **Non-zero exit = killed.**
4. Reports `total`, `killed`, `survived`, `score` and the list of survivors
   (file:line + mutation).

```bash
python3 tools/mutate.py src/<module>.py            # mutate a file
python3 tools/mutate.py src/<module>.py --max 80   # cap (random sample)
```

The script **always restores** the original file, even if you interrupt it
(cleanup in `finally`).

**Lightweight tradeoffs (by design):** because it's text-based, it can touch
strings or inline comments (occasional noise), and a mutant that breaks
compilation makes the test command fail, so it counts as KILLED. Keeping the
catalog to operators/keywords and functions small keeps the score meaningful.
The harness *tooling* runs on Python 3.9+; the *project under test* can be any
language.

## The phase is optional (and this is where you decide)

Mutation testing is the most expensive phase — it re-runs the whole suite once
per mutant. It is therefore **opt-out**, configured in `harness.json`:

```json
"mutation": { "enabled": "ask", "threshold": 1.0 }
```

| `enabled` | Behavior                                                                  |
|-----------|---------------------------------------------------------------------------|
| `true`    | The phase always runs. No feature closes without clearing the threshold.   |
| `false`   | The phase never runs. A feature closes with the `judge`'s approval alone.  |
| `"ask"`   | The `craftsman_lead` asks the human, once per feature, at the Gherkin approval gate. |

### Resolution order (the only rule that matters)

1. The feature's own entry in `feature_list.json` has `"mutation": true` or
   `"mutation": false` → **that wins**.
2. Otherwise `harness.json` → `mutation.enabled` is `true` or `false` → that.
3. Otherwise (`"ask"`) → the `craftsman_lead` asks the human at the approval
   gate and **writes the answer** into that feature's entry, so the question is
   asked once and survives a lost session.

If the block is missing from `harness.json`, the phase is treated as enabled.

### What "disabled" changes

- The `craftsman_lead` does **not** launch the `mutation_tester`.
- The feature closes on the `judge`'s approval alone; everything before it
  (spec conversation, Gherkin gate, strict TDD, review) is **unchanged**.
- `progress/mutation_<name>.md` is not written, and checkpoint C7 in
  `CHECKPOINTS.md` is marked `N/A` instead of left empty.

Disabling trades away the proof that the tests bite. It's a legitimate trade
for a spike or a throwaway prototype; it is not one for code you intend to keep.

## The threshold

- By default (`mutation.threshold: 1.0` in `harness.json`), the feature
  requires **100% killed mutants over the new or touched lines** of that
  feature.
- For pre-existing code not touched by the feature, no threshold is required
  (it is measured, not blocked).
- An **equivalent** mutant (doesn't change the observable behavior; e.g.
  mutating a value that is never used) may be excluded, but **only** with
  explicit justification written in `progress/mutation_<name>.md`. Abusing
  this route is cheating the judge.

## Who does what

- The `mutation_tester` **measures** and reports. It doesn't edit code.
- A surviving mutant is the `tdd_craftsman`'s job: write the red test
  that kills it and go through the `judge` again. It is the compute-bound
  improvement cycle: the CPU finds the hole, the craftsman plugs it with a test.

## Why it's worth the cost

Re-running the whole suite for each mutant is expensive. But that is exactly
the shift the thread describes: the limit is no longer how fast a human
types, but how much validation your CPU can afford. Code correctness is the
return, and it pays off every cycle.
