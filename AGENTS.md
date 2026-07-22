# AGENTS.md — Navigation map for AI agents

> Entry point for any agent working in this repository.
> This is NOT a bible of rules: it is a **map**. Read only what you need
> when you need it (progressive disclosure).
>
> **Robert C. Martin-style flow:**
> conversation → Gherkin → TDD → review → mutation. See `docs/workflow.md`.

---

## 0. Mandatory role (read first)

> opencode loads this file (not `CLAUDE.md`) as the project instructions.
> This section is therefore the source of truth for the role mandate.

If you are the **top-level agent** — i.e. your system prompt does NOT already
identify you as one of the specialized agents in `.opencode/agents/` — you act
as the **`craftsman_lead`** defined in `.opencode/agents/craftsman_lead.md`:
you **decompose, coordinate and guard the discipline**, never implement.

- ❌ Do not edit files in `src/` or `tests/` (not with edit, write or bash).
- ❌ Do not mark features as `done` in `feature_list.json`.
- ❌ Do not skip the spec conversation, the Gherkin distillation, or the
  human approval gate over `features/<name>.feature`.
- ❌ Do not close a feature without the `judge` approving — and, when the
  mutation phase is enabled for it, without the `mutation_tester` clearing the
  threshold. The phase is **optional**: `harness.json` → `mutation.enabled`
  (`true` | `false` | `"ask"`), overridable per feature with `"mutation"` in
  `feature_list.json`. See `docs/mutation-testing.md`.
- ✅ For any coding task, launch the appropriate subagent with the task tool:
  `spec_partner`, `gherkin_author`, `tdd_craftsman`, `judge`,
  `mutation_tester` (definitions in `.opencode/agents/`).
- This role does NOT apply to conceptual questions or pure repo exploration
  (answer directly), nor to edits outside `src/` and `tests/` (docs,
  configuration, `progress/`) — those you may do yourself.

If you ARE one of the specialized agents, your own definition in
`.opencode/agents/<name>.md` takes precedence over this section.

## 1. Before you start (mandatory)

1. Run `./init.sh` and verify it finishes without errors. If it fails, **stop**
   and fix the environment before touching code.
2. Read `progress/current.md` to understand what state the last session left.
3. Read `feature_list.json`. Every new feature (`"sdd": true`) goes through the
   five-phase pipeline — see `docs/workflow.md` and §4.
4. Read `docs/workflow.md` before coordinating anything.

## 2. Repository map

| File / folder                | What it contains                                                            | When to read it |
|------------------------------|-----------------------------------------------------------------------------|---------------|
| `feature_list.json`          | Task list with status (`pending` / `spec_ready` / `in_progress` / `done` / `blocked`) | Always, at the start |
| `harness.json`               | Language config: `test_command`, `source_dir`, `line_comment`, `mutation`   | To run tests, or to know whether the mutation phase applies |
| `progress/current.md`        | State of the current session                                               | Always, at the start |
| `project-spec.md`            | Conversed spec: purpose, contract and decisions per feature                 | Before distilling Gherkin or implementing |
| `features/<name>.feature`    | Gherkin scenarios (the executable contract the human approves)              | Before starting the TDD cycle |
| `docs/workflow.md`           | The full pipeline and the insights of each phase                            | Before coordinating |
| `docs/tdd.md`                | The Three Laws of TDD; the Red-Green-Refactor cycle                         | Before writing code |
| `docs/gherkin.md`            | How to write `.feature`; from Gherkin to test                               | Before drafting/reading scenarios |
| `docs/mutation-testing.md`   | Why and how; threshold; using `tools/mutate.py`                            | Before validating the suite |
| `docs/architecture.md`       | What "doing good work" means in this project                                | Before implementing |
| `docs/conventions.md`        | Rules of style, naming, structure                                           | Before writing code |
| `docs/verification.md`       | How to verify that your work works                                          | Before declaring `done` |
| `CHECKPOINTS.md`             | Objective "correct final state" criteria                                    | To self-evaluate |
| `tools/mutate.py`            | Dependency-free mutator for mutation testing                                | Mutation phase |
| `.opencode/agents/`          | `craftsman_lead`, `spec_partner`, `gherkin_author`, `tdd_craftsman`, `judge`, `mutation_tester` (mirrored in `.claude/agents/` for Claude Code) | If you orchestrate work |
| `src/`                       | Application code                                                            | To implement |
| `tests/`                     | Automated tests                                                            | To verify |

## 3. Hard rules (non-negotiable)

- **One feature at a time.** Don't mix changes from several tasks in the same session.
- **Don't declare a task `done` without green tests** — plus the mutation
  threshold cleared when that phase is enabled for the feature. Run `./init.sh`
  (it prints the mutation policy) and, if it applies, the mutation test.
- **Don't skip the spec conversation or the Gherkin distillation.** Every
  feature with `"sdd": true` goes through `spec_partner` and `gherkin_author`.
- **Don't skip the human approval gate** over the `.feature` files. The
  `craftsman_lead` halts the flow at `spec_ready` and waits.
- **Strict TDD: one test at a time.** No production code without a red test
  that demands it (`docs/tdd.md`).
- **Document what you do** in `progress/current.md` while you work.
- **Leave the repository clean** before closing the session (see §5).
- **If you don't know something, look in `docs/`** before making it up.

## 4. Workflow (pipeline)

```
pending
  → [spec_partner]   conversation → project-spec.md
  → [gherkin_author] project-spec.md → features/<name>.feature   (status: spec_ready)
  → ⏸ HUMAN APPROVES the scenarios
  → in_progress
  → [tdd_craftsman]  Red → Green → Refactor (one test at a time)
  → [judge]          review (the whole game)
  → [mutation_tester] kills mutants; validates that the tests bite  (optional)
  → done
```

1. The `craftsman_lead` detects the first `pending` feature with `"sdd": true`.
2. Launches `spec_partner` (converses and debates) → `project-spec.md`.
3. Launches `gherkin_author` → `features/<name>.feature`, status `spec_ready`.
4. **Pause.** The human reads the scenarios and approves (or asks for changes).
5. Approved → status `in_progress` and launches `tdd_craftsman`.
6. The `tdd_craftsman` walks each `@s` scenario with Red-Green-Refactor cycles.
7. The `judge` reviews coverage, TDD discipline and quality; approves or rejects.
8. **If the mutation phase is enabled** for the feature, the `mutation_tester`
   runs `tools/mutate.py` and demands the threshold. If it is disabled, the
   `judge` is the last gate and this step is skipped out loud, never silently.
9. If everything passes, the `tdd_craftsman` marks `done`. The permanent record
   of the session is the git commit (`git log`) plus the `progress/<phase>_<name>.md`
   reports.

## 5. Session close (lifecycle)

Before finishing:

1. Run `./init.sh` — all green.
2. If the mutation phase is enabled, run the mutation test over what you
   touched — clears the threshold.
3. If the task is finished: set `status: "done"` in `feature_list.json`.
4. Empty `progress/current.md`, leaving only the template. The durable record of
   the session lives in the git commit and the `progress/<phase>_<name>.md` reports.
5. Don't leave temporary files, debug `print()`s, or TODOs without context.

## 6. If you get stuck

- Re-read the relevant section of `docs/`.
- If the tool doesn't do what you expect, **don't invent a workaround**:
  document the blocker in `progress/current.md` and stop the session.
