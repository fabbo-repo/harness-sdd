# CHECKPOINTS — Final state evaluation

> In multi-agent systems you don't evaluate the path, you evaluate the
> destination. These are the objective checkpoints a judge (human or AI) can
> use to decide whether the project is healthy.

## C1 — The harness is complete

- [ ] The base files exist: `AGENTS.md`, `init.sh`, `feature_list.json`,
      `harness.json`, `progress/current.md`.
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
- [ ] There are no undeclared external dependencies (see the "no external
      dependencies by default" rule in `docs/architecture.md`).
- [ ] There are no stray debug prints, nor TODOs without context.

## C4 — Verification is real

- [ ] `tests/` has at least one test per module of `src/`.
- [ ] The tests exercise real behavior against an isolated environment, not
      broad mocks of the filesystem/IO.
- [ ] The project's test command (`harness.json`) shows > 0 tests and all
      green.

## C5 — The session was closed properly

- [ ] There are no suspicious untracked files (`*.tmp`, `__pycache__`
      outside `.gitignore`).
- [ ] The last session's work is captured in a git commit (`git log`) and its `progress/<phase>_<name>.md` reports.
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

## C7 — Mutation testing *(applies only if the phase is enabled)*

The mutation phase is optional. Resolve it first: the feature's own
`"mutation": true|false` in `feature_list.json` wins; otherwise
`harness.json` → `mutation.enabled` (`true` | `false` | `"ask"`). See
`docs/mutation-testing.md`.

- [ ] The policy is **resolved and recorded**: either a `"mutation"` value in
      the feature's entry, or an unambiguous `true`/`false` in `harness.json`.
      A feature closed while the policy was still `"ask"` and never answered is
      a failed checkpoint.

**If enabled:**

- [ ] The `done` feature cleared the mutation test
      (`python3 tools/mutate.py src/<file>.py`) with the score above
      `mutation.threshold` in `harness.json`.
- [ ] Any surviving mutant is documented in
      `progress/mutation_<name>.md` (killed with a new test, or
      justified as equivalent).

**If disabled:** mark both boxes above as `N/A` — an empty box means
"not done", `N/A` means "did not apply". No `progress/mutation_<name>.md` is
expected. C4 (verification is real) carries the weight instead.

---

**How to use this file:** the `judge` agent (`.opencode/agents/judge.md`)
walks C1-C6 and the `mutation_tester` validates C7. The session close is
rejected if any boxes remain empty.
