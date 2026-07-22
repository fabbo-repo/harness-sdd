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
  → [mutation_tester] MUTATION (validates that the tests bite)   ← optional
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
| `mutation_tester` | Measures whether the tests **bite**. Doesn't edit code. Optional phase — see `harness.json` → `mutation`. | `progress/mutation_*` |

Definitions in `.opencode/agents/` (mirrored in `.claude/agents/` for
Claude Code users).

### Model per agent

Each agent pins the model that matches its responsibility: **Opus where there
is judgment** (orchestrating, debating, approving/rejecting), **Sonnet where
production is bounded by a contract**, **Haiku where the work is mechanical**.
The `tdd_craftsman` burns the most tokens but its errors are caught by two
nets behind it (judge + mutation), so it doesn't need the most expensive
model; the `judge` is the worst place to cut costs — a weak judge lets bad
work through and the whole pipeline loses its point.

| Agent             | opencode (`model:`)          | Claude Code (`model:`) | Rationale                                          |
|-------------------|------------------------------|------------------------|-----------------------------------------------------|
| `craftsman_lead`  | `anthropic/claude-opus-4-8`  | `opus`                 | Few tokens, high-impact decisions (gates, verdicts) |
| `spec_partner`    | `anthropic/claude-opus-4-8`  | `opus`                 | The pushback quality *is* the product               |
| `gherkin_author`  | `anthropic/claude-sonnet-5`  | `sonnet`               | Structured spec → Gherkin, human gate after         |
| `tdd_craftsman`   | `anthropic/claude-sonnet-5`  | `sonnet`               | Biggest token consumer; contract + 2 nets behind    |
| `judge`           | `anthropic/claude-opus-4-8`  | `opus`                 | "Review is the whole game" — don't cheap out here   |
| `mutation_tester` | `anthropic/claude-haiku-4-5` | `haiku`                | Mostly mechanical: run script, compare threshold    |

opencode requires the full provider-prefixed ID; Claude Code takes **aliases**
(`opus`, `sonnet`, `haiku`) that track the current model without maintenance —
when a new model generation ships, update the opencode IDs and the Claude
Code side follows automatically. Per-agent models are the right granularity:
each subagent is a separate context, so mixing tiers carries no prompt-cache
penalty (unlike switching models mid-session).

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
  "line_comment": "#",
  "mutation": { "enabled": "ask", "threshold": 1.0 }
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
5. Open the repo in **opencode**, switch to the `craftsman_lead` primary
   agent (**Tab** cycles primary agents) and ask: **"implement the next
   pending feature"**. `AGENTS.md` §0 forces the top-level agent into the
   `craftsman_lead` role (orchestrates, doesn't edit code) and
   `docs/workflow.md` enforces the pipeline.

   > Claude Code still works too: `CLAUDE.md` and `.claude/` mirror the
   > opencode setup. Note that opencode ignores `CLAUDE.md` when `AGENTS.md`
   > exists — which is why the role mandate lives in `AGENTS.md`.

What happens:

- **Phase 1 — Spec.** `spec_partner` debates with you and writes/extends
  `project-spec.md`. Then `gherkin_author` distills
  `features/<feature>.feature` and leaves it in `spec_ready`. The lead
  **stops and asks you to approve** the scenarios.
- **Phase 2 — Code.** After your "approved", the lead moves to `in_progress`
  and launches `tdd_craftsman` (Red-Green-Refactor, one test at a time), then
  `judge` (review) and then — **if the mutation phase is on** —
  `mutation_tester` (`python3 tools/mutate.py src/<module>.py`). The feature
  moves to `done` once every gate that applies has passed.

> **The mutation phase is optional.** `harness.json` → `mutation.enabled`
> takes `true` (always run), `false` (never run — the `judge` is the last
> gate) or `"ask"` (the default: the lead asks you at the approval gate above,
> and records your answer as `"mutation": true|false` in that feature's entry,
> so you are asked once per feature). A feature's own value always wins over
> the global one. Details in `docs/mutation-testing.md`.

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

Optional field: `"mutation": true | false` overrides `harness.json` →
`mutation.enabled` for this feature alone. Leave it out to inherit the global
policy (and, under `"ask"`, to be asked at the approval gate — the lead writes
your answer back into this entry).

## Structure

```
.
├── AGENTS.md                 # Map for agents + the craftsman_lead role mandate (§0)
├── CHECKPOINTS.md            # "Correct final state" criteria (C1–C7)
├── CLAUDE.md                 # Same mandate for Claude Code (opencode ignores it)
├── opencode.json             # opencode config: pre-approved harness commands
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
├── .opencode/
│   ├── agents/               # craftsman_lead, spec_partner, gherkin_author,
│   │                         #   tdd_craftsman, judge, mutation_tester
│   └── plugins/
│       └── harness-verify.js # Runs the suite after src/tests edits; init.sh on idle
├── .claude/                  # Claude Code mirror of the above (agents + hooks)
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
