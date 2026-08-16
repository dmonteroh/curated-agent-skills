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


def _build_checklist_text(*, headings: list[str], rows: list[str], removal_region: str | None = None) -> str:
    heading_line = ", ".join(f"`{h}`" for h in headings)
    lines = [
        "## 1. Discovery contract",
        "",
        "<!-- parity:canonical-headings:start -->",
        f"Use its canonical heading: {heading_line}.",
        "<!-- parity:canonical-headings:end -->",
        "",
        "## 4. Subtraction",
        "",
        removal_region if removal_region is not None else _removal_authority_region(),
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


_ANCHORS = check_parity.PROSE_FAMILIES["removal-authority"]["anchors"]
_DELETE_KEYS = [k for k in _ANCHORS if k.startswith("delete:")]
_PROPOSE_KEYS = [k for k in _ANCHORS if k.startswith("propose:")]


def _removal_authority_region(*, omit: tuple[str, ...] = (), duplicate: tuple[str, ...] = ()) -> str:
    delete_lines = []
    for key in _DELETE_KEYS:
        if key in omit:
            continue
        delete_lines.append(f"- {_ANCHORS[key]}")
        if key in duplicate:
            delete_lines.append(f"- {_ANCHORS[key]}")
    propose_phrases = [_ANCHORS[key] for key in _PROPOSE_KEYS if key not in omit]
    for key in duplicate:
        if key in _PROPOSE_KEYS:
            propose_phrases.append(_ANCHORS[key])
    sentence = "Propose, never execute: " + ", ".join(propose_phrases) + "." if propose_phrases else "Propose, never execute: nothing."
    lines = [
        "<!-- parity:removal-authority:start -->",
        *delete_lines,
        sentence,
        "<!-- parity:removal-authority:end -->",
    ]
    return "\n".join(lines)


class ProseFamilyTest(unittest.TestCase):
    def setUp(self):
        self._orig = {
            name: getattr(check_parity, name)
            for name in ("CHECKLIST_PATH", "PROCESS_DOC_PATH", "REVIEWER_PROMPT_PATH")
        }
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp = Path(self._tmpdir.name)
        self._paths = {
            "CHECKLIST_PATH": tmp / "checklist.md",
            "PROCESS_DOC_PATH": tmp / "process.md",
            "REVIEWER_PROMPT_PATH": tmp / "reviewer.md",
        }
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        rows = _rows_for(sorted(audit_skills.list_check_names()))
        self._paths["CHECKLIST_PATH"].write_text(
            _build_checklist_text(headings=headings, rows=rows), encoding="utf-8"
        )
        for name in ("PROCESS_DOC_PATH", "REVIEWER_PROMPT_PATH"):
            self._paths[name].write_text(_removal_authority_region(), encoding="utf-8")
        for name, path in self._paths.items():
            setattr(check_parity, name, path)

    def tearDown(self):
        for name, path in self._orig.items():
            setattr(check_parity, name, path)
        self._tmpdir.cleanup()

    def _write(self, const_name: str, text: str) -> None:
        self._paths[const_name].write_text(text, encoding="utf-8")

    def _write_checklist_removal_region(self, removal_region: str) -> None:
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        rows = _rows_for(sorted(audit_skills.list_check_names()))
        self._write(
            "CHECKLIST_PATH",
            _build_checklist_text(headings=headings, rows=rows, removal_region=removal_region),
        )

    def _run(self) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = check_parity.main()
        return rc, buf.getvalue()

    def test_baseline_all_members_valid_exits_zero(self):
        rc, out = self._run()
        self.assertEqual(rc, 0)
        self.assertIn("removal-authority", out)

    def test_missing_delete_key_reddens_only_that_key_for_that_member(self):
        self._write("PROCESS_DOC_PATH", _removal_authority_region(omit=("delete:own-heading",)))
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("PARITY FAIL: removal-authority", out)
        self.assertIn("member SUBAGENT_REVIEW_PROCESS.md \"Removal authority\": missing ['delete:own-heading']", out)
        self.assertNotIn("SKILL_REVIEW_CHECKLIST.md §4:", out)
        self.assertNotIn("reviewer-prompt.md delete/propose block:", out)

    def test_missing_propose_key_reddens_only_that_key_for_that_member(self):
        self._write("REVIEWER_PROMPT_PATH", _removal_authority_region(omit=("propose:activation-cues",)))
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("member reviewer-prompt.md delete/propose block: missing ['propose:activation-cues']", out)

    def test_duplicated_delete_key_reported_as_drift(self):
        self._write_checklist_removal_region(_removal_authority_region(duplicate=("delete:frontmatter-description",)))
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("duplicated ['delete:frontmatter-description']", out)

    def test_canonical_bullet_count_drift_fails_checklist_member_only(self):
        self._write_checklist_removal_region(_removal_authority_region(omit=("delete:own-heading",)))
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("bullet count 4 != expected 5", out)

    def test_empty_region_all_nine_keys_missing(self):
        text = "<!-- parity:removal-authority:start -->\n<!-- parity:removal-authority:end -->\n"
        self._write("PROCESS_DOC_PATH", text)
        rc, out = self._run()
        self.assertEqual(rc, 1)
        for key in _ANCHORS:
            self.assertIn(key, out)

    def test_markers_around_unrelated_block_all_nine_keys_missing(self):
        text = (
            "Something unrelated.\n"
            "<!-- parity:removal-authority:start -->\n"
            "This paragraph carries none of the anchor phrases.\n"
            "<!-- parity:removal-authority:end -->\n"
        )
        self._write("REVIEWER_PROMPT_PATH", text)
        rc, out = self._run()
        self.assertEqual(rc, 1)
        for key in _ANCHORS:
            self.assertIn(key, out)

    def test_deleted_end_marker_exits_2_no_parity_verdict(self):
        text = "<!-- parity:removal-authority:start -->\n- own heading\n"
        self._write("PROCESS_DOC_PATH", text)
        rc, out = self._run()
        self.assertEqual(rc, 2)
        self.assertIn("PARITY EXTRACTION ERROR", out)
        self.assertNotIn("parity: ok", out)
        self.assertNotIn("PARITY FAIL", out)


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
