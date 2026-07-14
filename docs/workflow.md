# The Uncle Bob flow (Harness Engineering, craftsman edition)

> This project organizes the `notes-cli` around the process that
> Robert C. Martin describes in his thread: **converse the spec, distill it into
> Gherkin scenarios, carve the code with strict TDD, prune with judgment and
> validate with mutation testing**. The app code is trivial on
> purpose; what the repo teaches is the *process*.

## The pipeline at a glance

```
pending
  │  spec_partner — CONVERSATION  ───────────────►  project-spec.md
  │      "We debate various topics and decisions."
  │
  │  gherkin_author — DISTILLATION ──────────────►  features/<name>.feature
  │      ".feature files from the project-spec.md"
  │
  ▼  ⏸  HUMAN GATE: the human approves the scenarios (the contract)
  │
in_progress
  │  tdd_craftsman — RED → GREEN → REFACTOR ─────►  src/ + tests/
  │      one test at a time; the Three Laws of TDD
  │
  │  judge — REVIEW ─────────────────────────────►  progress/judge_<name>.md
  │      "The review step is the whole game. Agents draft, judgment prunes."
  │
  │  mutation_tester — MUTATION ─────────────────►  progress/mutation_<name>.md
  │      "Mutation testing is resource-heavy, but the ROI is worth every cycle."
  ▼
done
```

One feature at a time. One single human approval gate: over the Gherkin
scenarios, **before** writing production code.

## Why this order (the insights from the thread)

### 1. The spec is born from a conversation, not a dictation
The human doesn't hand over a closed document. They debate with the `spec_partner`:
edge cases, output contracts, discarded alternatives. The result,
`project-spec.md`, is the reasoned agreement — including the **decisions** and
their rationale. A spec without debate hides the gaps; the debate brings them out.

### 2. Gherkin turns prose into an executable contract
> "Once the project-spec.md is done, I have it create a set of .feature
> files."

Each behavior becomes a `Scenario` with a verifiable `Given/When/Then`.
This is what the human signs. From here on,
ambiguity is a bug in the contract, not in the code. See `docs/gherkin.md`.

### 3. The human gate is over the contract, not over the code
Approving late (when there is already code) is expensive. Approving the `.feature` is
cheap and is the point of maximum leverage: a poorly defined scenario
drags all of the TDD down. The `craftsman_lead` **stops** here and waits.

### 4. Strict TDD: one test at a time
> "single test followed by code (TDD)"

Not all tests are written up front. You live the small cycle:
a red test → the minimal green → refactor while green. The Three Laws in
`docs/tdd.md`. The code that no test asked for doesn't exist.

### 5. Review is the whole game
> "Agents draft, judgment prunes."

Generating drafts is cheap (the model types infinitely). The scarce value
is the **judgment** that decides what survives. The `judge` doesn't edit: it prunes. If a
scenario has no test, or there is code no one asked for, it rejects.

### 6. Validation is the new bottleneck, and it's compute-bound
> "Raw computer power is the limiting factor." / "Mutation testing is
> resource-heavy, but the ROI on code correctness is worth every cycle."

A green suite only says the code doesn't blow up, not that the tests
are useful. Mutation testing introduces defects and demands that some test
fail. It's expensive in CPU —it re-runs the suite for each mutant— but it's the
real measure of whether the net catches fish. See `docs/mutation-testing.md`.

## Artifact map (who writes what)

| File                             | Written by        | Contains                                            |
|----------------------------------|-------------------|-----------------------------------------------------|
| `project-spec.md`                | spec_partner      | Conversed spec: purpose, contract, decisions        |
| `features/<name>.feature`        | gherkin_author    | Gherkin scenarios `@s1..@sn` (the signed contract)  |
| `src/`, `tests/`                 | tdd_craftsman     | Code and tests, carved by TDD                       |
| `progress/tdd_<name>.md`         | tdd_craftsman     | Cycle log + `@s → test` map                         |
| `progress/judge_<name>.md`       | judge             | Review verdict + checkpoints                        |
| `progress/mutation_<name>.md`    | mutation_tester   | Mutation score + surviving mutants                  |
| `feature_list.json`              | craftsman_lead / tdd_craftsman | `pending → spec_ready → in_progress → done` |

Anti-broken-telephone rule: the subagents write to disk and
return a line of reference. The content doesn't circulate through chat.
