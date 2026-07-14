# Strict TDD — the `tdd_craftsman`'s discipline

> "Do you let it write all tests up front, then code or single test
> followed by code (TDD)?" — This branch's answer: **single test
> followed by code**. One test at a time. Never the whole battery up front.

## The Three Laws of TDD

1. **You don't write production code** except to make a failing test
   pass.
2. **You don't write more of a test than is enough to fail** — and not
   compiling or not importing counts as failing.
3. **You don't write more production code than is enough** to pass the
   single failing test.

The effect: you never have code without a test to justify it, nor a test
that isn't pushing real code. Scope doesn't inflate.

## The cycle, small and repeated

```
   ┌──────────────────────────────────────────────┐
   │                                                │
   ▼                                                │
 RED             GREEN                REFACTOR       │
 write ONE   →   minimal code    →    clean up with ─┘
 failing         to make it            the green
 test            green                 bar
```

- **RED** — the test derives from the next `@s` scenario of the `.feature`.
  Verify it fails for real (`python3 -m unittest …`). A test that
  passes on the first try proves nothing: adjust it or be suspicious of the setup.
- **GREEN** — the **minimal** implementation. Cheating is allowed
  (returning a constant) if there is no test yet that disproves it. The
  next cycle will force the generalization. This is deliberate.
- **REFACTOR** — only while green. Remove duplication, improve names,
  split long functions. Re-run the tests after each change. If
  something turns red, you're not refactoring: you're changing behavior.

## Granularity: one scenario, one or more cycles

Each `@s` of the `.feature` is translated into at least one Red-Green-
Refactor cycle. A scenario with several edges (e.g. "empty list prints 0"
and "three notes prints 3") may need two cycles to force the
generalization of the code.

## Mandatory traceability

On close, each `@s` must be covered by at least one concrete test.
The `tdd_craftsman` writes the map in `progress/tdd_<name>.md`:

```markdown
## Traceability
- @s1 (empty file → 0) → test_count_empty_file
- @s2 (three notes → 3)    → test_count_several_notes
- @s3 (doesn't modify the file) → test_count_does_not_mutate_file
```

The `judge` rejects if any `@s` is left without a test, and the `mutation_tester`
rejects if the tests exist but don't bite.

## Smells the `judge` looks for

- Production code that **no red test** asked for (violates Law 1).
- Tests written "for the future" for scenarios not yet reached.
- Refactors done while red.
- Long functions or opaque names that survived the REFACTOR step.
