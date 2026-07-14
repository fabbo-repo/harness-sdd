Feature: Count notes
  As a user I want to know how many notes I have at a glance so I get
  a quick overview of the store, composable with other tools.

  @s1
  Scenario: Empty store prints 0
    Given an empty notes store
    When I run "python -m src.cli count"
    Then standard output is exactly "0"
    And the exit code is 0

  @s2
  Scenario: Non-existent store prints 0
    Given the notes file does not exist
    When I run "python -m src.cli count"
    Then standard output is exactly "0"
    And the exit code is 0

  @s3
  Scenario: A single note prints 1
    Given a store with 1 note
    When I run "python -m src.cli count"
    Then standard output is exactly "1"
    And the exit code is 0

  @s4
  Scenario: Several notes prints the exact total
    Given a store with 3 notes
    When I run "python -m src.cli count"
    Then standard output is exactly "3"
    And the exit code is 0

  @s5
  Scenario: The output is a bare integer without descriptive text
    Given a store with 2 notes
    When I run "python -m src.cli count"
    Then standard output is exactly "2"
    And standard output does not contain the string "Total"

  @s6
  Scenario: count does not modify the store
    Given a store with 2 notes
    When I run "python -m src.cli count"
    Then the notes file is left byte-for-byte the same as before
    And the exit code is 0

  @s7
  Scenario: count is idempotent when run on a non-existent store
    Given the notes file does not exist
    When I run "python -m src.cli count"
    Then the notes file still does not exist
    And the exit code is 0
