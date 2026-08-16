from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(TESTS_DIR))

import audit_skills  # noqa: E402
import check_parity  # noqa: E402

SNAPSHOT_PATH = TESTS_DIR / "data" / "audit_snapshot.json"


def _build_checklist_text(*, headings: list[str], rows: list[str]) -> str:
    heading_line = ", ".join(f"`{h}`" for h in headings)
    lines = [
        "## 1. Discovery contract",
        "",
        "<!-- parity:canonical-headings:start -->",
        f"Use its canonical heading: {heading_line}.",
        "<!-- parity:canonical-headings:end -->",
        "",
        "## 12. Mechanical check index",
        "",
        "<!-- parity:check-names:start -->",
        "| Check name | Section | Citation |",
        "| --- | --- | --- |",
        *rows,
        "<!-- parity:check-names:end -->",
        "",
    ]
    return "\n".join(lines)


def _rows_for(names: list[str]) -> list[str]:
    return [f"| `{name}` | §1 | citation |" for name in names]


class ListCheckNamesTest(unittest.TestCase):
    def test_sorted_deduplicated_and_matches_declared_count(self):
        names = audit_skills.list_check_names()
        self.assertEqual(names, tuple(sorted(set(names))))
        self.assertEqual(len(names), 21)


class ListChecksCliTest(unittest.TestCase):
    def test_prints_sorted_names_and_exits_zero_without_extra_output(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "audit_skills.py"), "--list-checks"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.splitlines(), list(audit_skills.list_check_names()))
        self.assertEqual(proc.stderr, "")


class RealTreeParityTest(unittest.TestCase):
    def test_real_checklist_and_registry_are_in_parity(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check_parity.main()
        self.assertEqual(rc, 0)


class RegionExtractionTest(unittest.TestCase):
    def test_missing_start_marker_raises(self):
        text = "no markers here\n<!-- parity:canonical-headings:end -->\n"
        with self.assertRaises(check_parity.ParityExtractionError) as ctx:
            check_parity._region_lines(text, "canonical-headings")
        self.assertEqual(ctx.exception.family_id, "canonical-headings")

    def test_missing_end_marker_raises(self):
        text = "<!-- parity:canonical-headings:start -->\nUse `Workflow`.\n"
        with self.assertRaises(check_parity.ParityExtractionError):
            check_parity._region_lines(text, "canonical-headings")

    def test_duplicate_start_marker_raises(self):
        text = (
            "<!-- parity:canonical-headings:start -->\n"
            "Use `Workflow`.\n"
            "<!-- parity:canonical-headings:start -->\n"
            "<!-- parity:canonical-headings:end -->\n"
        )
        with self.assertRaises(check_parity.ParityExtractionError):
            check_parity._region_lines(text, "canonical-headings")

    def test_end_before_start_raises(self):
        text = (
            "<!-- parity:canonical-headings:end -->\n"
            "<!-- parity:canonical-headings:start -->\n"
        )
        with self.assertRaises(check_parity.ParityExtractionError):
            check_parity._region_lines(text, "canonical-headings")

    def test_empty_region_raises_zero_extracted_members(self):
        text = "<!-- parity:canonical-headings:start -->\n\n<!-- parity:canonical-headings:end -->\n"
        with self.assertRaises(check_parity.ParityExtractionError):
            check_parity.check_family3(text)


class MainMalformedRegionTest(unittest.TestCase):
    def setUp(self):
        self._orig_checklist_path = check_parity.CHECKLIST_PATH
        self._tmpdir = tempfile.TemporaryDirectory()
        self._tmp_path = Path(self._tmpdir.name) / "fixture_checklist.md"

    def tearDown(self):
        check_parity.CHECKLIST_PATH = self._orig_checklist_path
        self._tmpdir.cleanup()

    def _run(self, text: str) -> int:
        self._tmp_path.write_text(text, encoding="utf-8")
        check_parity.CHECKLIST_PATH = self._tmp_path
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            return check_parity.main()

    def test_missing_marker_exits_2_not_reported_as_parity(self):
        text = "no markers anywhere\n"
        rc = self._run(text)
        self.assertEqual(rc, 2)


class DriftedFixtureMainTest(unittest.TestCase):
    """Proves exit 1 + both-sides naming on synthetic fixtures, never touching
    scripts/auditing/SKILL_REVIEW_CHECKLIST.md or scripts/audit_skills.py."""

    def setUp(self):
        self._orig_checklist_path = check_parity.CHECKLIST_PATH
        self._tmpdir = tempfile.TemporaryDirectory()
        self._tmp_path = Path(self._tmpdir.name) / "fixture_checklist.md"

    def tearDown(self):
        check_parity.CHECKLIST_PATH = self._orig_checklist_path
        self._tmpdir.cleanup()

    def _write_and_run(self, text: str) -> tuple[int, str]:
        self._tmp_path.write_text(text, encoding="utf-8")
        check_parity.CHECKLIST_PATH = self._tmp_path
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check_parity.main()
        return rc, buf.getvalue()

    def test_good_fixture_built_from_the_live_registry_exits_zero(self):
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        rows = _rows_for(sorted(audit_skills.list_check_names()))
        rc, _ = self._write_and_run(_build_checklist_text(headings=headings, rows=rows))
        self.assertEqual(rc, 0)

    def test_family3_drift_exits_1_and_names_both_sides(self):
        headings = [h for h in audit_skills.CANONICAL_HEADINGS.values() if h != "Resources"]
        rows = _rows_for(sorted(audit_skills.list_check_names()))
        rc, out = self._write_and_run(_build_checklist_text(headings=headings, rows=rows))
        self.assertEqual(rc, 1)
        self.assertIn("Resources", out)
        self.assertIn("SKILL_REVIEW_CHECKLIST.md §5 canonical-heading paragraph", out)
        self.assertIn("CANONICAL_HEADINGS in scripts/audit_skills.py", out)

    def test_family4_drift_exits_1_and_names_both_sides(self):
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        names = sorted(audit_skills.list_check_names())
        dropped, remaining = names[0], names[1:]
        rc, out = self._write_and_run(_build_checklist_text(headings=headings, rows=_rows_for(remaining)))
        self.assertEqual(rc, 1)
        self.assertIn(dropped, out)
        self.assertIn("SKILL_REVIEW_CHECKLIST.md §12 table", out)
        self.assertIn("list_check_names() in scripts/audit_skills.py", out)

    def test_unresolved_section_reference_exits_1(self):
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        names = sorted(audit_skills.list_check_names())
        rows = [f"| `{name}` | §99 | citation |" for name in names]
        rc, out = self._write_and_run(_build_checklist_text(headings=headings, rows=rows))
        self.assertEqual(rc, 1)
        self.assertIn("does not exist", out)


class SnapshotCrossCheckTest(unittest.TestCase):
    def test_ac8b_every_observed_check_name_is_declared(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        observed: set[str] = set()
        for skill in snapshot:
            for finding in [*skill.get("issues", []), *skill.get("warnings", [])]:
                observed.add(finding.split(":", 1)[0])
        declared = set(audit_skills.list_check_names())
        missing = observed - declared
        self.assertEqual(missing, set(), f"observed but undeclared: {missing}")


if __name__ == "__main__":
    unittest.main()
