# Gherkin — the executable contract

> "Once the project-spec.md is done, I have it create a set of .feature
> files from the project-spec.md." The `.feature` files are what the human
> approves at the gate, and the map that the `tdd_craftsman` walks.

The files live in `features/<name>.feature`, where `<name>` matches
the `name` field of `feature_list.json`.

## Structure

```gherkin
Feature: <purpose in one sentence>
  As a <role> I want <capability> so that <benefit>.   # optional context

  @s1
  Scenario: <observable behavior>
    Given <starting state>
    When <concrete user action>
    Then <measurable result: stdout / stderr / exit code>

  @s2
  Scenario: <edge case or error>
    Given ...
    When ...
    Then ...
```

## Hard rules

- **One `Scenario` per observable behavior**, including the error
  paths (non-existent id, invalid flag, empty file). If the
  `project-spec.md` mentions an edge case, it has its scenario.
- **Stable tags** `@s1`, `@s2`, … They are the identifier that the
  `tdd_craftsman` (`@s → test` map) and the `judge` (coverage) cite.
- **Each `Then` asserts something measurable.** "The system works" is
  forbidden. Valid: "Then standard output is exactly `3`", "Then the exit
  code is non-zero", "Then stderr contains `--limit`".
- **A single `When` per scenario** (the action under test). If you need
  two actions, they are probably two scenarios.
- **No implementation details.** The `.feature` describes
  behavior, not functions or variable names.

## Example (a generic `count`-style feature)

```gherkin
Feature: Count stored items
  As a user I want to know how many items I have so I get a quick overview.

  @s1
  Scenario: Empty store prints 0
    Given an empty store
    When I run "python -m src.<entrypoint> count"
    Then standard output is exactly "0"
    And the exit code is 0

  @s2
  Scenario: Several items print the exact total
    Given a store with 3 items
    When I run "python -m src.<entrypoint> count"
    Then standard output is exactly "3"

  @s3
  Scenario: count doesn't modify the store
    Given a store with 2 items
    When I run "python -m src.<entrypoint> count"
    Then the store file is left byte-for-byte the same as before
```

## From Gherkin to test

We don't use a BDD runner (`behave`, `pytest-bdd`, `cucumber`, …) so as not to
add a dependency. Instead, each `Scenario` is translated **by hand** into a
test in your project's own framework (whatever `harness.json`'s `test_command`
runs) whose name cites the scenario:

```
@s1 → test_count_empty_store
@s2 → test_count_several_items
@s3 → test_count_does_not_mutate_store
```

The `tdd_craftsman` writes these tests one by one (Red→Green→Refactor) and
leaves the map in `progress/tdd_<name>.md`. This way the `.feature` remains the
human-readable source of truth, without paying the cost of a framework.
