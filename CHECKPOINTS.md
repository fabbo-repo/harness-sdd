# CHECKPOINTS — Final state evaluation

> In multi-agent systems you don't evaluate the path, you evaluate the
> destination. These are the objective checkpoints a judge (human or AI) can
> use to decide whether the project is healthy.

## C1 — The harness is complete

- [ ] The 4 base files exist: `AGENTS.md`, `init.sh`, `feature_list.json`,
      `progress/current.md`.
- [ ] The 3 docs exist: `docs/architecture.md`, `docs/conventions.md`,
      `docs/verification.md`.
- [ ] `./init.sh` finishes with exit code 0.

## C2 — The state is coherent

- [ ] At most one feature in `in_progress` in `feature_list.json`.
- [ ] Every `done` feature has associated tests that pass.
- [ ] `progress/current.md` is empty or describes the active session
      (contains no garbage from previous sessions).

## C3 — The code respects the architecture

- [ ] `src/` only contains the modules foreseen in `docs/architecture.md`.
- [ ] There are no external dependencies in `requirements.txt` (it must be empty
      or not exist).
- [ ] There are no stray debug `print()`s, nor TODOs without context.

## C4 — Verification is real

- [ ] `tests/` has at least one test per module of `src/`.
- [ ] The tests use `tempfile.TemporaryDirectory()`, not fs mocks.
- [ ] `python3 -m unittest discover -s tests -v` shows > 0 tests
      and all green.

## C5 — The session was closed properly

- [ ] There are no suspicious untracked files (`*.tmp`, `__pycache__`
      outside `.gitignore`).
- [ ] `progress/history.md` has an entry for the last session.
- [ ] The last feature worked on is reflected in its correct state.

## C6 — Gherkin contract (BDD)

- [ ] Every feature with `"sdd": true` in state `spec_ready`, `in_progress`
      or `done` has its `features/<name>.feature` and a section in
      `project-spec.md`.
- [ ] The `.feature` uses Gherkin with scenarios tagged `@s1`, `@s2`, …
      and each `Then` asserts something measurable (see `docs/gherkin.md`).
- [ ] Every `@s` scenario is covered by at least one concrete test in
      `tests/` (`@s → test` map in `progress/tdd_<name>.md`).
- [ ] There is no production code that no red test asked for
      (TDD discipline, see `docs/tdd.md`).

## C7 — Mutation testing

- [ ] The `done` feature cleared the mutation test
      (`python3 tools/mutate.py src/<file>.py`) with the score above
      the threshold in `docs/mutation-testing.md`.
- [ ] Any surviving mutant is documented in
      `progress/mutation_<name>.md` (killed with a new test, or
      justified as equivalent).

---

**How to use this file:** the `judge` agent (`.claude/agents/judge.md`)
walks C1-C6 and the `mutation_tester` validates C7. The session close is
rejected if any boxes remain empty.
