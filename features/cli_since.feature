Feature: Filter notes by date
  As a user I want to see what I jotted down since a given date so I can review
  my recent activity without listing the whole file.

  @s1
  Scenario: A note created exactly on the given date is included (inclusive bound)
    Given a store with a note created on "2026-05-01" at 23:00
    When I run "python -m src.cli since 2026-05-01"
    Then standard output includes that note's line
    And the exit code is 0

  @s2
  Scenario: Notes earlier than the date are left out and later ones are included
    Given a store with a note from "2026-04-30" and another from "2026-05-02"
    When I run "python -m src.cli since 2026-05-01"
    Then standard output includes the line of the note from "2026-05-02"
    And standard output does not include the line of the note from "2026-04-30"
    And the exit code is 0

  @s3
  Scenario: Matching notes are ordered by created_at descending
    Given a store with notes from "2026-05-01", "2026-05-03" and "2026-05-02"
    When I run "python -m src.cli since 2026-05-01"
    Then the output lists the 3 notes ordered by created_at descending
    And the first line corresponds to the note from "2026-05-03"
    And the last line corresponds to the note from "2026-05-01"

  @s4
  Scenario: The format of each line matches list
    Given a store with 2 notes created on or after "2026-05-01"
    When I run "python -m src.cli since 2026-05-01"
    Then each line has the form "<id>\t<created_at>\t<title>"

  @s5
  Scenario: A date with an invalid format is an error
    Given a store with notes
    When I run "python -m src.cli since 2026/05/01"
    Then stderr contains a message about the date
    And the exit code is non-zero

  @s6
  Scenario: An impossible calendar date is an error
    Given a store with notes
    When I run "python -m src.cli since 2026-13-40"
    Then stderr contains a message about the date
    And the exit code is non-zero

  @s7
  Scenario: With no matches it prints nothing
    Given a store with a note from "2026-04-30"
    When I run "python -m src.cli since 2026-05-01"
    Then standard output is empty
    And the exit code is 0

  @s8
  Scenario: Empty store prints nothing
    Given an empty notes store
    When I run "python -m src.cli since 2026-05-01"
    Then standard output is empty
    And the exit code is 0

  @s9
  Scenario: since does not modify the store
    Given a store with 2 notes created on or after "2026-05-01"
    When I run "python -m src.cli since 2026-05-01"
    Then the notes file is left byte-for-byte the same as before
    And the exit code is 0
