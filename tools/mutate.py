#!/usr/bin/env python3
"""Minimal, dependency-free mutator for mutation testing.

Introduces a small defect into a file in `src/`, runs the test suite
and checks whether some test fails (KILLED mutant) or all pass
(SURVIVING mutant). A survivor is a hole in the test net.

Usage:
    python3 tools/mutate.py src/cli.py
    python3 tools/mutate.py src/cli.py --max 80

Design:
- Works at the *token* level (the `tokenize` module), so it NEVER mutates
  the contents of strings or comments: only operators, keywords,
  numbers and `return` statements.
- Discards mutants that don't compile (they don't inflate the score).
- ALWAYS restores the original file, even on Ctrl-C (`finally`
  block).

See `docs/mutation-testing.md`.
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tokenize

# Operator mutations: OP token -> replacement.
OP_MUTATIONS = {
    "<=": "<",
    ">=": ">",
    "<": "<=",
    ">": ">=",
    "==": "!=",
    "!=": "==",
    "+": "-",
    "-": "+",
}

# Keyword/constant mutations: NAME token -> replacement.
NAME_MUTATIONS = {
    "and": "or",
    "or": "and",
    "True": "False",
    "False": "True",
}

TEST_CMD = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"]


class Mutant:
    """A single mutation: replaces a span (line, col) of the source."""

    def __init__(self, row: int, col_start: int, col_end: int,
                 original: str, replacement: str, label: str):
        self.row = row              # 1-based
        self.col_start = col_start  # 0-based
        self.col_end = col_end
        self.original = original
        self.replacement = replacement
        self.label = label

    def apply(self, lines: list[str]) -> str:
        out = list(lines)
        line = out[self.row - 1]
        out[self.row - 1] = line[: self.col_start] + \
            self.replacement + line[self.col_end:]
        return "".join(out)

    def describe(self, path: str) -> str:
        return f"{path}:{self.row}  {self.label}  ({self.original!r} -> {self.replacement!r})"


def _int_mutation(literal: str) -> str | None:
    """Integer literal mutation: n -> n+1 (and 0 -> 1, without touching floats)."""
    try:
        value = int(literal, 0)
    except ValueError:
        return None
    return str(value + 1)


def generate_mutants(source: str) -> list[Mutant]:
    mutants: list[Mutant] = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return mutants

    for tok in tokens:
        # multi-line tokens are left out (these mutations don't apply)
        if tok.start[0] != tok.end[0]:
            continue
        row = tok.start[0]
        col_start, col_end = tok.start[1], tok.end[1]
        text = tok.string

        if tok.type == tokenize.OP and text in OP_MUTATIONS:
            mutants.append(Mutant(row, col_start, col_end, text,
                                  OP_MUTATIONS[text], "operator"))
        elif tok.type == tokenize.NAME and text in NAME_MUTATIONS:
            mutants.append(Mutant(row, col_start, col_end, text,
                                  NAME_MUTATIONS[text], "keyword"))
        elif tok.type == tokenize.NUMBER:
            repl = _int_mutation(text)
            if repl is not None:
                mutants.append(Mutant(row, col_start, col_end, text,
                                      repl, "number"))

    # Return mutation: `return <expr>` -> `return None`.
    lines = source.splitlines(keepends=True)
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.lstrip()
        if not stripped.startswith("return "):
            continue
        rest = stripped[len("return "):].strip()
        if rest in ("", "None"):
            continue
        indent = len(raw) - len(stripped)
        # replace from 'return' to the end of the line's content
        content = raw.rstrip("\n")
        mutants.append(
            Mutant(idx, indent, len(content),
                   content[indent:], "return None", "return")
        )
    return mutants


def compiles(source: str, path: str) -> bool:
    try:
        compile(source, path, "exec")
        return True
    except SyntaxError:
        return False


def run_tests() -> bool:
    """Returns True if the suite passes (returncode 0)."""
    result = subprocess.run(TEST_CMD, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    return result.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Minimal mutation testing.")
    parser.add_argument("path", help="File in src/ to mutate.")
    parser.add_argument("--max", type=int, default=100,
                        help="Maximum number of mutants to evaluate (default 100).")
    args = parser.parse_args(argv)

    with open(args.path, "r", encoding="utf-8") as f:
        original = f.read()
    lines = original.splitlines(keepends=True)

    # Sanity check: the suite must be GREEN before mutating.
    if not run_tests():
        print("[FAIL] The suite is red without mutating. Fix the tests first.",
              file=sys.stderr)
        return 2

    mutants = generate_mutants(original)
    valid = [m for m in mutants if compiles(m.apply(lines), args.path)]
    skipped_noncompile = len(mutants) - len(valid)

    truncated = 0
    if len(valid) > args.max:
        truncated = len(valid) - args.max
        valid = valid[: args.max]

    killed: list[Mutant] = []
    survived: list[Mutant] = []

    print(f"── Mutating {args.path} ─ {len(valid)} valid mutants "
          f"({skipped_noncompile} discarded for not compiling)")
    try:
        for i, m in enumerate(valid, start=1):
            with open(args.path, "w", encoding="utf-8") as f:
                f.write(m.apply(lines))
            if run_tests():
                survived.append(m)
                mark = "SURVIVES"
            else:
                killed.append(m)
                mark = "killed"
            print(f"  [{i}/{len(valid)}] {mark:9} {m.describe(args.path)}")
    finally:
        with open(args.path, "w", encoding="utf-8") as f:
            f.write(original)

    total = len(valid)
    score = (len(killed) / total * 100) if total else 100.0

    print("\n── Summary ──────────────────────────────────────")
    print(f"  total:    {total}")
    print(f"  killed:   {len(killed)}")
    print(f"  survived: {len(survived)}")
    print(f"  score:    {score:.1f}%")
    if truncated:
        print(f"  [WARN] {truncated} valid mutants NOT evaluated "
              f"(limit --max={args.max}). Raise --max for full coverage.")
    if survived:
        print("\n  Surviving mutants (holes in the net):")
        for m in survived:
            print(f"   - {m.describe(args.path)}")

    # Exit code: 0 if none survive, 1 if any survives.
    return 0 if not survived else 1


if __name__ == "__main__":
    sys.exit(main())
