# Harness SDD — Uncle Bob Workflow
> Spec-driven, test-first development pipeline for AI agents, built around a minimal notes CLI.

This project organizes the `notes-cli` around the process of
**Robert C. Martin (Uncle Bob)** described in his thread: converse the spec,
distill it into **Gherkin** scenarios, carve the code with **strict TDD**,
prune with **judgment**, and validate with **mutation testing**.

> The app code is deliberately simple. What matters is not **what** it does,
> but **how** it is structured so that an agent can work autonomously and
> verifiably — and with the discipline of the craftsman.

## The pipeline

```
pending
  → [spec_partner]    CONVERSATION  → project-spec.md
  → [gherkin_author]  DISTILLATION  → features/<name>.feature   (spec_ready)
  → ⏸  HUMAN GATE: the human approves the scenarios
  → in_progress
  → [tdd_craftsman]   RED → GREEN → REFACTOR  → src/ + tests/
  → [judge]           REVIEW ("the whole game")
  → [mutation_tester] MUTATION (validates that the tests bite)
  → done
```

One feature at a time. One single human approval gate: over the Gherkin
contract, **before** writing production code.

## The insights from the thread, mapped to each step

| Step              | Idea from the thread                                                           | Where it lives in the repo       |
|-------------------|--------------------------------------------------------------------------------|----------------------------------|
| Conversed spec    | "I have the AI write the spec by having a conversation… we debate decisions"   | `spec_partner` → `project-spec.md` |
| Gherkin           | "create a set of .feature files from the project-spec.md"                      | `gherkin_author` → `features/`   |
| TDD               | "single test followed by code (TDD)" — one test at a time                      | `tdd_craftsman`, `docs/tdd.md`   |
| Review            | "The review step is the whole game. Agents draft, judgment prunes."            | `judge`                          |
| Mutation          | "Mutation testing is resource-heavy, but the ROI… is worth every cycle."       | `mutation_tester`, `tools/mutate.py` |
| Compute-bound     | "Raw computer power is the limiting factor" — the bottleneck is validating, not typing | mutation re-runs the suite for each mutant |

Full detail in **`docs/workflow.md`** (insight per phase).

## The agents

| Agent             | Role                                                                | Writes                               |
|-------------------|----------------------------------------------------------------------|--------------------------------------|
| `craftsman_lead`  | Orchestrates the 5 phases. Doesn't implement. Guards the gates.      | `feature_list.json` (transitions)    |
| `spec_partner`    | Converses and **debates** the spec with the human.                  | `project-spec.md`                    |
| `gherkin_author`  | Distills the spec into `.feature` scenarios.                        | `features/<name>.feature`            |
| `tdd_craftsman`   | Strict TDD, one test at a time (the Three Laws of TDD).             | `src/`, `tests/`, `progress/tdd_*`   |
| `judge`           | Review is the game: approves or **prunes**. Doesn't edit code.      | `progress/judge_*`                   |
| `mutation_tester` | Measures whether the tests **bite**. Doesn't edit code.            | `progress/mutation_*`                |

Definitions in `.claude/agents/`.

## Try it yourself with Claude Code

Open Claude Code at the repo root: `CLAUDE.md` forces the model to act as
`craftsman_lead` (orchestrates, doesn't edit code) and `docs/workflow.md`
enforces the pipeline.

1. `./init.sh` — must finish green.
2. In `feature_list.json` leave a feature with `status: "pending"` and
   `"sdd": true` (e.g. #9 `cli_export`).
3. Launch `claude` and ask: **"implement the next pending feature"**.

What happens:

- **Phase 1 — Spec.** `spec_partner` debates with you and writes/extends
  `project-spec.md`. Then `gherkin_author` distills
  `features/<feature>.feature` and leaves it in `spec_ready`. The lead
  **stops and asks you to approve** the scenarios.
- **Phase 2 — Code.** After your "approved", the lead moves to `in_progress`
  and launches `tdd_craftsman` (Red-Green-Refactor, one test at a time), then
  `judge` (review) and then `mutation_tester`
  (`python3 tools/mutate.py src/cli.py`). Only if mutation clears the
  threshold does the feature move to `done`.

Open `features/`, `project-spec.md` and `progress/` in your editor while
Claude works: each report appears as soon as the subagent finishes. That is
the anti-broken-telephone rule — the content lives on disk, not in chat.

## Example already executed: `cli_count` (#8)

The repo includes a full end-to-end run of the `cli_count` feature,
ready to inspect (or film):

| Artifact                         | What it shows                                            |
|----------------------------------|----------------------------------------------------------|
| `features/cli_count.feature`     | The contract: 7 scenarios `@s1..@s7`                     |
| `progress/tdd_cli_count.md`      | Red-Green-Refactor log + `@s → test` map                 |
| `progress/judge_cli_count.md`    | Review verdict (APPROVED) + checkpoints                  |
| `progress/mutation_cli_count.md` | Mutation score: **100%** over the feature's lines        |
| `src/cli.py`, `tests/test_cli.py`| The code and its 7 tests (one per scenario)              |

Reproduce the mutation test:

```bash
python3 tools/mutate.py src/cli.py
```

## Using the app (humans)

```bash
python3 -m src.cli add "buy bread" --body "and milk"
python3 -m src.cli list
python3 -m src.cli count
```

## Structure

```
.
├── AGENTS.md                 # Map for agents (progressive disclosure)
├── CHECKPOINTS.md            # "Correct final state" criteria (C1–C7)
├── CLAUDE.md                 # Forces the craftsman_lead role
├── feature_list.json         # Scope: one feature at a time
├── init.sh                   # Verification and initialization
├── project-spec.md           # Conversed spec (spec_partner)
├── features/<name>.feature   # Gherkin contract (gherkin_author)
├── progress/
│   ├── current.md            # Active session (live state)
│   ├── tdd_<name>.md         # TDD log + traceability
│   ├── judge_<name>.md       # Review verdict
│   └── mutation_<name>.md    # Mutation report
├── docs/
│   ├── workflow.md           # The pipeline and the insights of each phase
│   ├── tdd.md                # The Three Laws of TDD; Red-Green-Refactor
│   ├── gherkin.md            # How to write .feature; from Gherkin to test
│   ├── mutation-testing.md   # Why/how; threshold; tools/mutate.py
│   ├── architecture.md       # What "good work" means
│   ├── conventions.md        # Style, names, errors
│   └── verification.md       # How to prove it works
├── tools/
│   └── mutate.py             # Dependency-free mutator
├── .claude/
│   ├── agents/               # craftsman_lead, spec_partner, gherkin_author,
│   │                         #   tdd_craftsman, judge, mutation_tester
│   └── settings.json         # Hooks that automate verification
├── src/
│   ├── storage.py            # Atomic persistence (JSON)
│   ├── notes.py              # Domain model
│   └── cli.py                # argparse interface
└── tests/
    ├── test_storage.py
    ├── test_notes.py
    └── test_cli.py
```

## Lessons this project illustrates

- **The spec is born from a debate**, not a dictation: the `spec_partner`
  questions edge cases and records decisions with their rationale.
- **Gherkin as executable contract**: ambiguity is resolved before writing
  code, at the point of maximum leverage (the human gate).
- **Strict TDD**: one test at a time; no production code without a red test
  that demands it. Scope doesn't inflate.
- **Review is the whole game**: drafting is cheap; the judgment that prunes
  is the scarce value.
- **Validation is compute-bound**: mutation testing proves the tests bite, at
  the cost of CPU. The limit is no longer typing, it's validating.
- **State on disk, not in chat**: `project-spec.md`, `features/` and
  `progress/` survive restarts and blown context windows.
