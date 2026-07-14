"""Integration tests for src/cli.py."""
from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src import cli, storage


class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "notes.json")
        self._patch = patch.object(storage, "DEFAULT_NOTES_PATH", self.path)
        self._patch.start()

    def tearDown(self) -> None:
        self._patch.stop()
        self.tmp.cleanup()

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            code = cli.main(argv)
        return code, out_buf.getvalue(), err_buf.getvalue()

    def test_add_creates_note_and_prints_id(self) -> None:
        code, out, _ = self._run(["add", "first", "--body", "hello"])
        self.assertEqual(code, 0)
        self.assertIn("id=1", out)
        notes = storage.load(self.path)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["title"], "first")

    def test_list_shows_existing_notes(self) -> None:
        self._run(["add", "one", "--body", "a"])
        self._run(["add", "two", "--body", "b"])
        code, out, _ = self._run(["list"])
        self.assertEqual(code, 0)
        self.assertIn("one", out)
        self.assertIn("two", out)
        self.assertEqual(len(out.strip().splitlines()), 2)

    def test_list_empty_outputs_nothing(self) -> None:
        code, out, _ = self._run(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_show_prints_title_date_body(self) -> None:
        self._run(["add", "title-one", "--body", "body-one"])
        code, out, _ = self._run(["show", "1"])
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertEqual(lines[0], "title-one")
        self.assertRegex(lines[1], r"\d{4}-\d{2}-\d{2}T")
        self.assertEqual(lines[2], "body-one")

    def test_show_missing_id_returns_error(self) -> None:
        code, out, err = self._run(["show", "99"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("99", err)

    def test_delete_removes_note_and_confirms(self) -> None:
        self._run(["add", "one", "--body", "a"])
        self._run(["add", "two", "--body", "b"])
        code, out, _ = self._run(["delete", "1"])
        self.assertEqual(code, 0)
        self.assertIn("id=1", out)
        notes = storage.load(self.path)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["id"], 2)

    def test_delete_missing_id_returns_error(self) -> None:
        self._run(["add", "one", "--body", "a"])
        code, out, err = self._run(["delete", "42"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("42", err)
        notes = storage.load(self.path)
        self.assertEqual(len(notes), 1)


    def test_search_finds_matching_notes(self) -> None:
        self._run(["add", "buy milk", "--body", "at the store"])
        self._run(["add", "call doctor", "--body", "monday appointment"])
        code, out, _ = self._run(["search", "milk"])
        self.assertEqual(code, 0)
        self.assertIn("buy milk", out)
        self.assertNotIn("call doctor", out)

    def test_search_no_match_returns_error(self) -> None:
        self._run(["add", "buy milk", "--body", "at the store"])
        code, out, err = self._run(["search", "shoes"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("shoes", err)

    def test_search_is_case_insensitive(self) -> None:
        self._run(["add", "Buy MILK", "--body", "at the store"])
        code, out, _ = self._run(["search", "buy milk"])
        self.assertEqual(code, 0)
        self.assertIn("Buy MILK", out)

    def test_edit_updates_only_title(self) -> None:
        self._run(["add", "old", "--body", "body"])
        code, out, _ = self._run(["edit", "1", "--title", "new"])
        self.assertEqual(code, 0)
        self.assertIn("id=1", out)
        notes = storage.load(self.path)
        self.assertEqual(notes[0]["title"], "new")
        self.assertEqual(notes[0]["body"], "body")

    def test_edit_updates_only_body(self) -> None:
        self._run(["add", "title", "--body", "old"])
        code, out, _ = self._run(["edit", "1", "--body", "new"])
        self.assertEqual(code, 0)
        self.assertIn("id=1", out)
        notes = storage.load(self.path)
        self.assertEqual(notes[0]["title"], "title")
        self.assertEqual(notes[0]["body"], "new")

    def test_edit_updates_both_fields(self) -> None:
        self._run(["add", "old-t", "--body", "old-b"])
        code, out, _ = self._run(["edit", "1", "--title", "new-t", "--body", "new-b"])
        self.assertEqual(code, 0)
        self.assertIn("id=1", out)
        notes = storage.load(self.path)
        self.assertEqual(notes[0]["title"], "new-t")
        self.assertEqual(notes[0]["body"], "new-b")

    def test_edit_missing_id_returns_error(self) -> None:
        self._run(["add", "one", "--body", "a"])
        code, out, err = self._run(["edit", "99", "--title", "x"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("99", err)

    def test_edit_without_flags_returns_error(self) -> None:
        self._run(["add", "one", "--body", "a"])
        code, out, err = self._run(["edit", "1"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertNotEqual(err, "")
        notes = storage.load(self.path)
        self.assertEqual(notes[0]["title"], "one")
        self.assertEqual(notes[0]["body"], "a")

    def _add_with_created_at(self, title: str, body: str, created_at: str) -> None:
        existing = storage.load(self.path)
        next_id = max((n["id"] for n in existing), default=0) + 1
        existing.append({
            "id": next_id,
            "title": title,
            "body": body,
            "created_at": created_at,
        })
        storage.save(existing, self.path)

    def test_recent_default_limit_orders_by_created_at_desc(self) -> None:
        base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        for i in range(7):
            ts = (base + timedelta(minutes=i)).isoformat(timespec="seconds")
            self._add_with_created_at(f"note-{i}", f"body-{i}", ts)
        code, out, _ = self._run(["recent"])
        self.assertEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 5)
        timestamps = [line.split("\t")[1] for line in lines]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
        titles = [line.split("\t")[2] for line in lines]
        self.assertEqual(titles, ["note-6", "note-5", "note-4", "note-3", "note-2"])

    def test_recent_custom_limit(self) -> None:
        base = datetime(2026, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        for i in range(6):
            ts = (base + timedelta(minutes=i)).isoformat(timespec="seconds")
            self._add_with_created_at(f"title-{i}", f"body-{i}", ts)
        code, out, _ = self._run(["recent", "--limit", "3"])
        self.assertEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 3)
        for line in lines:
            parts = line.split("\t")
            self.assertEqual(len(parts), 3)
            self.assertRegex(parts[0], r"^\d+$")
            self.assertRegex(parts[1], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_recent_empty_outputs_nothing(self) -> None:
        code, out, err = self._run(["recent"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_recent_invalid_limit_zero(self) -> None:
        self._run(["add", "one", "--body", "a"])
        before = storage.load(self.path)
        with open(self.path, "rb") as f:
            before_bytes = f.read()
        code, out, err = self._run(["recent", "--limit", "0"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertNotEqual(err, "")
        after = storage.load(self.path)
        self.assertEqual(before, after)
        with open(self.path, "rb") as f:
            self.assertEqual(before_bytes, f.read())

    def test_recent_invalid_limit_negative(self) -> None:
        self._run(["add", "one", "--body", "a"])
        before = storage.load(self.path)
        with open(self.path, "rb") as f:
            before_bytes = f.read()
        code, out, err = self._run(["recent", "--limit", "-3"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertNotEqual(err, "")
        after = storage.load(self.path)
        self.assertEqual(before, after)
        with open(self.path, "rb") as f:
            self.assertEqual(before_bytes, f.read())

    def test_count_empty_store_prints_zero(self) -> None:
        code, out, err = self._run(["count"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "0\n")
        self.assertEqual(err, "")

    def test_count_missing_store_prints_zero(self) -> None:
        self.assertFalse(os.path.exists(self.path))
        code, out, _ = self._run(["count"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "0\n")

    def test_count_single_note_prints_one(self) -> None:
        self._run(["add", "one", "--body", "a"])
        code, out, _ = self._run(["count"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "1\n")

    def test_count_three_notes_prints_three(self) -> None:
        self._run(["add", "one", "--body", "a"])
        self._run(["add", "two", "--body", "b"])
        self._run(["add", "three", "--body", "c"])
        code, out, _ = self._run(["count"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "3\n")

    def test_count_output_is_bare_integer_without_text(self) -> None:
        self._run(["add", "one", "--body", "a"])
        self._run(["add", "two", "--body", "b"])
        _, out, _ = self._run(["count"])
        self.assertEqual(out.strip(), "2")
        self.assertNotIn("Total", out)

    def test_count_does_not_mutate_store(self) -> None:
        self._run(["add", "one", "--body", "a"])
        self._run(["add", "two", "--body", "b"])
        with open(self.path, "rb") as f:
            before_bytes = f.read()
        code, _, _ = self._run(["count"])
        self.assertEqual(code, 0)
        with open(self.path, "rb") as f:
            self.assertEqual(before_bytes, f.read())

    def test_count_does_not_create_store_when_missing(self) -> None:
        self.assertFalse(os.path.exists(self.path))
        code, _, _ = self._run(["count"])
        self.assertEqual(code, 0)
        self.assertFalse(os.path.exists(self.path))

    def test_since_includes_note_created_on_exact_date(self) -> None:
        self._add_with_created_at("entry", "x", "2026-05-01T23:00:00+00:00")
        code, out, _ = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        self.assertIn("entry", out)

    def test_since_excludes_earlier_includes_later(self) -> None:
        self._add_with_created_at("older", "x", "2026-04-30T10:00:00+00:00")
        self._add_with_created_at("newer", "y", "2026-05-02T10:00:00+00:00")
        code, out, _ = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        self.assertIn("newer", out)
        self.assertNotIn("older", out)

    def test_since_orders_matches_by_created_at_desc(self) -> None:
        self._add_with_created_at("day-one", "x", "2026-05-01T10:00:00+00:00")
        self._add_with_created_at("day-three", "y", "2026-05-03T10:00:00+00:00")
        self._add_with_created_at("day-two", "z", "2026-05-02T10:00:00+00:00")
        code, out, _ = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 3)
        titles = [line.split("\t")[2] for line in lines]
        self.assertEqual(titles, ["day-three", "day-two", "day-one"])

    def test_since_line_format_matches_list(self) -> None:
        self._add_with_created_at("first", "x", "2026-05-01T08:00:00+00:00")
        self._add_with_created_at("second", "y", "2026-05-04T08:00:00+00:00")
        code, out, _ = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 2)
        for line in lines:
            parts = line.split("\t")
            self.assertEqual(len(parts), 3)
            self.assertRegex(parts[0], r"^\d+$")
            self.assertRegex(parts[1], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertEqual(lines[0], "2\t2026-05-04T08:00:00+00:00\tsecond")

    def test_since_invalid_date_format_is_error(self) -> None:
        self._add_with_created_at("one", "x", "2026-05-02T08:00:00+00:00")
        code, out, err = self._run(["since", "2026/05/01"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("date", err.lower())

    def test_since_impossible_calendar_date_is_error(self) -> None:
        self._add_with_created_at("one", "x", "2026-05-02T08:00:00+00:00")
        code, out, err = self._run(["since", "2026-13-40"])
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("date", err.lower())

    def test_since_no_matches_outputs_nothing(self) -> None:
        self._add_with_created_at("older", "x", "2026-04-30T08:00:00+00:00")
        code, out, err = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_since_empty_store_outputs_nothing(self) -> None:
        self.assertFalse(os.path.exists(self.path))
        code, out, err = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_since_does_not_mutate_store(self) -> None:
        self._add_with_created_at("one", "a", "2026-05-01T08:00:00+00:00")
        self._add_with_created_at("two", "b", "2026-05-03T08:00:00+00:00")
        with open(self.path, "rb") as f:
            before_bytes = f.read()
        code, _, _ = self._run(["since", "2026-05-01"])
        self.assertEqual(code, 0)
        with open(self.path, "rb") as f:
            self.assertEqual(before_bytes, f.read())


if __name__ == "__main__":
    unittest.main()
