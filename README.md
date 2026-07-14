# Harness SDD — Spec-Driven Development harness for AI agents

> A reusable **template** that makes an AI agent build *your* Python project
> with the discipline of a craftsman: converse the spec, distill it into
> **Gherkin**, carve the code with **strict TDD**, prune with **judgment**, and
> validate with **mutation testing**.

This repo is not an application — it is the **harness** (the scaffolding, roles,
docs and gates) around Robert C. Martin's flow. You point it at your own
project: you describe features, and the agent walks each one through a fixed
pipeline, stopping at a single human approval gate before writing any code.

> The point is not *what* you build, but *how*: so an agent can work
> autonomously and verifiably, with the process — not chat — as the source of
> truth.

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

## The insights behind each step

| Step              | Idea from Uncle Bob's thread                                                   | Where it lives                   |
|-------------------|--------------------------------------------------------------------------------|----------------------------------|
| Conversed spec    | "I have the AI write the spec by having a conversation… we debate decisions"   | `spec_partner` → `project-spec.md` |
| Gherkin           | "create a set of .feature files from the project-spec.md"                      | `gherkin_author` → `features/`   |
| TDD               | "single test followed by code (TDD)" — one test at a time                      | `tdd_craftsman`, `docs/tdd.md`   |
| Review            | "The review step is the whole game. Agents draft, judgment prunes."            | `judge`                          |
| Mutation          | "Mutation testing is resource-heavy, but the ROI… is worth every cycle."       | `mutation_tester`, `tools/mutate.py` |
| Compute-bound     | "Raw computer power is the limiting factor" — the bottleneck is validating, not typing | mutation re-runs the suite per mutant |

Full detail in **`docs/workflow.md`** (one insight per phase).

## Works on any language

The **method** (spec → Gherkin → TDD → review → mutation) is language-neutral.
The only language-specific thing is *how you run tests* and *how you mutate*,
and that lives in a single config file, **`harness.json`**:

```json
{
  "language": "python",
  "test_command": "python3 -m unittest discover -s tests -q",
  "source_dir": "src",
  "line_comment": "#"
}
```

Point it at your stack by changing `test_command` (and `line_comment`):

| Language | `test_command`                          | `line_comment` |
|----------|-----------------------------------------|----------------|
| Python   | `python3 -m unittest discover -s tests -q` | `#`         |
| JS/TS    | `npm test --silent`                     | `//`           |
| Go       | `go test ./...`                         | `//`           |
| Rust     | `cargo test -q`                         | `//`           |

The **harness tooling** (`init.sh`, `tools/mutate.py`) runs on **Python 3.9+**
(either `python3` or `python`); this is independent of your project's language.
The mutator (`tools/mutate.py`) is a lightweight, language-agnostic **text**
mutator that decides killed/survived by your `test_command`'s exit code — see
`docs/mutation-testing.md`.

## How to use it

1. Use this repo as a template for your project.
2. Set `harness.json` for your language (table above).
3. `./init.sh` — must finish green.
4. Fill in `feature_list.json`: set `project`/`description` and add your first
   feature with `status: "pending"` and `"sdd": true` (shape below).
5. Open the repo in Claude Code and ask: **"implement the next pending feature"**.
   `CLAUDE.md` forces the model to act as `craftsman_lead` (orchestrates,
   doesn't edit code) and `docs/workflow.md` enforces the pipeline.

What happens:

- **Phase 1 — Spec.** `spec_partner` debates with you and writes/extends
  `project-spec.md`. Then `gherkin_author` distills
  `features/<feature>.feature` and leaves it in `spec_ready`. The lead
  **stops and asks you to approve** the scenarios.
- **Phase 2 — Code.** After your "approved", the lead moves to `in_progress`
  and launches `tdd_craftsman` (Red-Green-Refactor, one test at a time), then
  `judge` (review) and then `mutation_tester`
  (`python3 tools/mutate.py src/<module>.py`). Only if mutation clears the
  threshold does the feature move to `done`.

Open `features/`, `project-spec.md` and `progress/` in your editor while the
agent works: each report appears as soon as the subagent finishes. That is the
anti-broken-telephone rule — the content lives on disk, not in chat.

### Feature shape in `feature_list.json`

```json
{
  "id": 1,
  "name": "my_feature",
  "title": "Human-readable title",
  "description": "What the feature does, in one or two sentences.",
  "acceptance": [
    "A concrete, checkable statement about observable behavior",
    "Another one, including error/edge cases",
    "tests/ cover the cases above"
  ],
  "sdd": true,
  "status": "pending"
}
```

`"sdd": true` sends the feature through the full pipeline (spec → Gherkin →
TDD → review → mutation). `name` must match the `features/<name>.feature` file.

## Structure

```
.
├── AGENTS.md                 # Map for agents (progressive disclosure)
├── CHECKPOINTS.md            # "Correct final state" criteria (C1–C7)
├── CLAUDE.md                 # Forces the craftsman_lead role
├── harness.json              # Language config: test_command, source_dir, …
├── feature_list.json         # Scope: your features, one at a time
├── init.sh                   # Verification and initialization
├── project-spec.md           # Conversed spec (spec_partner) — starts empty
├── features/<name>.feature   # Gherkin contract (gherkin_author)
├── progress/
│   ├── current.md            # Active session (live state)
│   ├── tdd_<name>.md         # TDD log + traceability   (gitignored)
│   ├── judge_<name>.md       # Review verdict           (gitignored)
│   └── mutation_<name>.md    # Mutation report          (gitignored)
├── docs/
│   ├── workflow.md           # The pipeline and the insights of each phase
│   ├── tdd.md                # The Three Laws of TDD; Red-Green-Refactor
│   ├── gherkin.md            # How to write .feature; from Gherkin to test
│   ├── mutation-testing.md   # Why/how; threshold; tools/mutate.py
│   ├── architecture.md       # Your project's quality standard (template)
│   ├── conventions.md        # Style, names, errors
│   └── verification.md       # How to prove it works
├── tools/
│   ├── mutate.py             # Language-agnostic, dependency-free mutator
│   └── run_tests.sh          # Runs test_command from harness.json
├── .claude/
│   ├── agents/               # craftsman_lead, spec_partner, gherkin_author,
│   │                         #   tdd_craftsman, judge, mutation_tester
│   └── settings.json         # Hooks that automate verification
├── src/                      # Your application code (starts empty)
└── tests/                    # Your tests (starts empty)
```

The `progress/*` reports are regenerable working artifacts — they are
gitignored (only `progress/current.md` is tracked). The signed contracts
(`features/*.feature`) and the conversed spec (`project-spec.md`) are tracked.

## Principles this harness enforces

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
  `progress/current.md` survive restarts and blown context windows.
