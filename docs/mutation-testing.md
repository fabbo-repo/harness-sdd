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

## This repo's mutator: `tools/mutate.py`

No external dependencies (we keep `requirements.txt` empty). The script:

1. Reads a file from `src/`.
2. Applies, **one by one**, a catalog of textual mutations:

   | Category     | Example mutation                             |
   |--------------|----------------------------------------------|
   | Comparison   | `<=` → `<`, `==` → `!=`, `>` → `>=`          |
   | Arithmetic   | `+` → `-`, `- 1` → `+ 1`                      |
   | Boolean      | `and` → `or`, `True` → `False`               |
   | Constants    | `0` → `1`, `1` → `0`                          |
   | Return       | `return <expr>` → `return None`              |

3. For each mutant: writes the mutated file, runs
   `python3 -m unittest discover -s tests -q`, restores the original.
4. Reports `total`, `killed`, `survived`, `score` and the list of
   survivors (file:line + mutation).

```bash
python3 tools/mutate.py src/cli.py            # mutate a file
python3 tools/mutate.py src/cli.py --max 80   # cap the number of mutants
```

The script **always restores** the original file, even if you interrupt
it (it handles cleanup in `finally`).

## The threshold

- By default, the feature requires **100% killed mutants over the new or
  touched lines** of that feature.
- For legacy code not touched by the feature, no threshold is required on this
  branch (it is measured, not blocked).
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
