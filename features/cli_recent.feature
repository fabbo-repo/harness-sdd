Feature: List the most recent notes
  As a user I want to see my latest notes without listing the whole file.

  # Legacy contract: this feature was closed before adopting the Gherkin
  # flow. The .feature documents its contract after the fact so that the
  # harness (init.sh, judge) treats it like the rest.

  @s1
  Scenario: By default shows up to 5 notes, most recent first
    Given a store with 7 notes created at distinct instants
    When I run "python -m src.cli recent"
    Then the output lists 5 notes
    And they are ordered by created_at descending
    And the exit code is 0

  @s2
  Scenario: The --limit flag changes the number of notes
    Given a store with 7 notes
    When I run "python -m src.cli recent --limit 3"
    Then the output lists exactly 3 notes

  @s3
  Scenario: A non-positive limit is an error
    Given a store with notes
    When I run "python -m src.cli recent --limit 0"
    Then stderr contains a message about --limit
    And the exit code is non-zero

  @s4
  Scenario: Empty store prints nothing
    Given an empty notes store
    When I run "python -m src.cli recent"
    Then standard output is empty
    And the exit code is 0

  @s5
  Scenario: The format of each line matches list
    Given a store with 2 notes
    When I run "python -m src.cli recent"
    Then each line has the form "<id>\t<created_at>\t<title>"
