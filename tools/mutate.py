#!/usr/bin/env python3
"""Language-agnostic, dependency-free mutator for mutation testing.

Reads the project's test command from `harness.json`, introduces ONE small
textual defect into a target file at a time (a *mutant*), runs the suite, and
checks whether some test fails (KILLED) or all pass (SURVIVED). A survivor is
a hole in the test net.

Usage:
    python3 tools/mutate.py path/to/source_file
    python3 tools/mutate.py path/to/source_file --max 80

Design (deliberately lightweight — works on ANY language):
- Operates on TEXT, not a language AST, so it runs against Python, JS/TS, Go,
  Rust, Java, … It swaps a small catalog of operators/keywords that are common
  across languages (comparisons, boolean connectors, arithmetic, booleans).
- Skips whole-line comments (the `line_comment` prefix from harness.json) to
  avoid trivial noise. It may still touch strings or inline comments — keep
  functions small and the score stays meaningful.
- KILLED vs SURVIVED is decided purely by the test command's exit code
  (non-zero = killed). A mutant that breaks compilation makes the command fail,
  so it counts as KILLED; that's why the catalog sticks to operators/keywords.
- ALWAYS restores the original file, even on Ctrl-C (finally block).

See docs/mutation-testing.md.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys

CONFIG_PATH = "harness.json"

# (compiled regex, replacement, human label). The lookarounds keep us away from
# compound operators (===, !==, <=, +=, ++, --, …) in the common languages.
_RULES = [
    (re.compile(r"(?<![=!<>])==(?!=)"), "!=", "== -> !="),
    (re.compile(r"(?<![=!])!=(?!=)"), "==", "!= -> =="),
    (re.compile(r"<="), "<", "<= -> <"),
    (re.compile(r">="), ">", ">= -> >"),
    (re.compile(r"&&"), "||", "&& -> ||"),
    (re.compile(r"\|\|"), "&&", "|| -> &&"),
    (re.compile(r"(?<=\s)\+(?=\s)"), "-", "+ -> -"),
    (re.compile(r"(?<=\s)-(?=\s)"), "+", "- -> +"),
    (re.compile(r"\btrue\b"), "false", "true -> false"),
    (re.compile(r"\bfalse\b"), "true", "false -> true"),
    (re.compile(r"\bTrue\b"), "False", "True -> False"),
    (re.compile(r"\bFalse\b"), "True", "False -> True"),
    (re.compile(r"\band\b"), "or", "and -> or"),
    (re.compile(r"\bor\b"), "and", "or -> and"),
]


def load_config(path: str = CONFIG_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"[mutate] config not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"[mutate] invalid {path}: {exc}")


def find_sites(lines: list[str], line_comment: str) -> list[tuple]:
    """One entry per possible single mutation: (line_index, start, end, repl, label)."""
    sites = []
    for i, line in enumerate(lines):
        if line_comment and line.lstrip().startswith(line_comment):
            continue
        for rx, repl, label in _RULES:
            for m in rx.finditer(line):
                sites.append((i, m.start(), m.end(), repl, label))
    return sites


def mutate_line(line: str, start: int, end: int, repl: str) -> str:
    return line[:start] + repl + line[end:]


def run_tests(test_command: str) -> int:
    proc = subprocess.run(test_command, shell=True)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Language-agnostic mutation tester.")
    parser.add_argument("target", help="Source file to mutate.")
    parser.add_argument("--max", type=int, default=0,
                        help="Cap the number of mutants (0 = all). Sampled at random.")
    parser.add_argument("--config", default=CONFIG_PATH, help="Path to harness.json.")
    args = parser.parse_args()

    config = load_config(args.config)
    test_command = config["test_command"]
    line_comment = config.get("line_comment", "")

    with open(args.target, encoding="utf-8") as fh:
        original = fh.read()
    lines = original.splitlines(keepends=True)

    sites = find_sites(lines, line_comment)
    if not sites:
        print(f"[mutate] no mutable operators/keywords found in {args.target}")
        return 0

    if args.max and len(sites) > args.max:
        sites = random.sample(sites, args.max)

    killed, survived = 0, []
    print(f"[mutate] {args.target}: {len(sites)} mutants | test: {test_command}\n")
    try:
        for n, (i, s, e, repl, label) in enumerate(sites, 1):
            mutated = lines[:]
            mutated[i] = mutate_line(lines[i], s, e, repl)
            with open(args.target, "w", encoding="utf-8") as fh:
                fh.write("".join(mutated))
            rc = run_tests(test_command)
            if rc != 0:
                killed += 1
                status = "killed"
            else:
                survived.append((i + 1, label))
                status = "SURVIVED"
            print(f"  [{n}/{len(sites)}] line {i + 1}: {label:<16} -> {status}")
    finally:
        with open(args.target, "w", encoding="utf-8") as fh:
            fh.write(original)

    total = len(sites)
    score = 100.0 * killed / total if total else 0.0
    print(f"\n[mutate] total={total} killed={killed} survived={len(survived)} "
          f"score={score:.1f}%")
    if survived:
        print("[mutate] surviving mutants (holes in the net):")
        for line_no, label in survived:
            print(f"  {args.target}:{line_no}  {label}")
    return 0 if not survived else 1


if __name__ == "__main__":
    raise SystemExit(main())
