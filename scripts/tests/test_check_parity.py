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


def _build_checklist_text(
    *,
    headings: list[str],
    rows: list[str],
    removal_region: str | None = None,
    verdict_region: str | None = None,
) -> str:
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
        "## Verdicts",
        "",
        verdict_region if verdict_region is not None else _verdict_enum_region(),
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


_VERDICT_SPEC = check_parity.PROSE_FAMILIES["verdict-enum"]
_VERDICT_DECLARED = sorted(_VERDICT_SPEC["declared"])
_VERDICT_FLAGS = _VERDICT_SPEC["flag_anchors"]


def _status_lines(*, omit: tuple[str, ...] = (), omit_flags: tuple[str, ...] = ()) -> str:
    tokens = [t for t in _VERDICT_DECLARED if t not in omit]
    lines = [f"- `--status {t}`" for t in tokens]
    flags = [f for f in _VERDICT_FLAGS if f not in omit_flags]
    if flags:
        lines.append("Alongside those, the call always carries " + " and ".join(f"`{f}`" for f in flags) + ".")
    return "\n".join(lines)


def _verdict_enum_region(**kwargs) -> str:
    return "\n".join(
        ["<!-- parity:verdict-enum:start -->", _status_lines(**kwargs), "<!-- parity:verdict-enum:end -->"]
    )


def _with_verdict_enum(text: str, **kwargs) -> str:
    return text.rstrip("\n") + "\n\n" + _verdict_enum_region(**kwargs) + "\n"


def _synthesis_fixture(*, heading: str = "## Output", **kwargs) -> str:
    return f"# Synthesis prompt\n\nIntro text.\n\n{heading}\n\n{_status_lines(**kwargs)}\n"


def _shell_case_fixture(tokens: tuple[str, ...] = tuple(_VERDICT_DECLARED)) -> str:
    alternation = "|".join(tokens)
    return (
        "#!/usr/bin/env bash\n"
        "# <!-- parity:verdict-enum:start -->\n"
        'case "$status" in\n'
        f"  {alternation})\n"
        "    ;;\n"
        "  *)\n"
        "    ;;\n"
        "esac\n"
        "# <!-- parity:verdict-enum:end -->\n"
    )


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
            self._paths[name].write_text(_with_verdict_enum(_removal_authority_region()), encoding="utf-8")
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
        self._write("PROCESS_DOC_PATH", _with_verdict_enum(_removal_authority_region(omit=("delete:own-heading",))))
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("PARITY FAIL: removal-authority", out)
        self.assertIn("member SUBAGENT_REVIEW_PROCESS.md \"Removal authority\": missing ['delete:own-heading']", out)
        self.assertNotIn("SKILL_REVIEW_CHECKLIST.md §4:", out)
        self.assertNotIn("reviewer-prompt.md delete/propose block:", out)

    def test_missing_propose_key_reddens_only_that_key_for_that_member(self):
        self._write(
            "REVIEWER_PROMPT_PATH", _with_verdict_enum(_removal_authority_region(omit=("propose:activation-cues",)))
        )
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
        self._write("PROCESS_DOC_PATH", _with_verdict_enum(text))
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
        self._write("REVIEWER_PROMPT_PATH", _with_verdict_enum(text))
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


class MarkerRegexWideningTest(unittest.TestCase):
    def test_bare_marker_matches(self):
        self.assertIsNotNone(check_parity.MARKER_RE.match("<!-- parity:x:start -->"))

    def test_hash_space_prefixed_marker_matches(self):
        self.assertIsNotNone(check_parity.MARKER_RE.match("# <!-- parity:x:start -->"))

    def test_hash_prefixed_marker_with_no_space_matches(self):
        self.assertIsNotNone(check_parity.MARKER_RE.match("#<!-- parity:x:end -->"))

    def test_indented_marker_is_rejected(self):
        self.assertIsNone(check_parity.MARKER_RE.match("  <!-- parity:x:start -->"))

    def test_indented_hash_prefixed_marker_is_rejected(self):
        self.assertIsNone(check_parity.MARKER_RE.match("  # <!-- parity:x:start -->"))


class VerdictEnumFamilyTest(unittest.TestCase):
    """Covers the verdict-enum family's own extraction shapes, entirely
    against temp-file fixtures for all five members."""

    def setUp(self):
        self._orig = {
            name: getattr(check_parity, name)
            for name in (
                "CHECKLIST_PATH",
                "PROCESS_DOC_PATH",
                "REVIEWER_PROMPT_PATH",
                "SYNTHESIS_PROMPT_PATH",
                "RESULT_TOOL_PATH",
            )
        }
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp = Path(self._tmpdir.name)
        self._paths = {
            "CHECKLIST_PATH": tmp / "checklist.md",
            "PROCESS_DOC_PATH": tmp / "process.md",
            "REVIEWER_PROMPT_PATH": tmp / "reviewer.md",
            "SYNTHESIS_PROMPT_PATH": tmp / "synthesis.md",
            "RESULT_TOOL_PATH": tmp / "review-result.sh",
        }
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        rows = _rows_for(sorted(audit_skills.list_check_names()))
        self._paths["CHECKLIST_PATH"].write_text(
            _build_checklist_text(headings=headings, rows=rows), encoding="utf-8"
        )
        for name in ("PROCESS_DOC_PATH", "REVIEWER_PROMPT_PATH"):
            self._paths[name].write_text(_with_verdict_enum(_removal_authority_region()), encoding="utf-8")
        self._paths["SYNTHESIS_PROMPT_PATH"].write_text(_synthesis_fixture(), encoding="utf-8")
        self._paths["RESULT_TOOL_PATH"].write_text(_shell_case_fixture(), encoding="utf-8")
        for name, path in self._paths.items():
            setattr(check_parity, name, path)

    def tearDown(self):
        for name, path in self._orig.items():
            setattr(check_parity, name, path)
        self._tmpdir.cleanup()

    def _write(self, const_name: str, text: str) -> None:
        self._paths[const_name].write_text(text, encoding="utf-8")

    def _run(self) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = check_parity.main()
        return rc, buf.getvalue()

    def test_baseline_all_five_members_valid_exits_zero(self):
        rc, out = self._run()
        self.assertEqual(rc, 0)
        self.assertIn("verdict-enum", out)

    def test_drop_questions_from_checklist_member_reddens_only_that_member(self):
        headings = list(audit_skills.CANONICAL_HEADINGS.values())
        rows = _rows_for(sorted(audit_skills.list_check_names()))
        self._write(
            "CHECKLIST_PATH",
            _build_checklist_text(headings=headings, rows=rows, verdict_region=_verdict_enum_region(omit=("questions",))),
        )
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("PARITY FAIL: verdict-enum", out)
        self.assertIn("member SKILL_REVIEW_CHECKLIST.md \"Verdicts\": missing ['questions']", out)
        self.assertNotIn("SUBAGENT_REVIEW_PROCESS.md \"Verdicts\":", out)
        self.assertNotIn("reviewer-prompt.md Output block:", out)

    def test_drop_changed_from_process_doc_member_reddens_only_that_member(self):
        self._write(
            "PROCESS_DOC_PATH", _with_verdict_enum(_removal_authority_region(), omit=("changed",))
        )
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("member SUBAGENT_REVIEW_PROCESS.md \"Verdicts\": missing ['changed']", out)

    def test_review_status_prose_line_all_three_missing_and_both_flags_missing(self):
        verdict_block = (
            "<!-- parity:verdict-enum:start -->\n"
            "REVIEW_STATUS: NO-CHANGE\n"
            "REVIEW_STATUS: CHANGED\n"
            "QUESTIONS\n"
            "<!-- parity:verdict-enum:end -->"
        )
        self._write("PROCESS_DOC_PATH", _removal_authority_region() + "\n\n" + verdict_block + "\n")
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn(
            "member SUBAGENT_REVIEW_PROCESS.md \"Verdicts\": "
            "missing ['changed', 'no-change', 'questions'] "
            "missing-flags ['--differentiation', '--removals']",
            out,
        )

    def test_missing_removals_flag_reported_for_reviewer_prompt_member(self):
        self._write(
            "REVIEWER_PROMPT_PATH", _with_verdict_enum(_removal_authority_region(), omit_flags=("--removals",))
        )
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("member reviewer-prompt.md Output block: missing-flags ['--removals']", out)

    def test_shell_fourth_token_reported_unexpected(self):
        self._write(
            "RESULT_TOOL_PATH", _shell_case_fixture(tokens=("no-change", "changed", "questions", "blocked"))
        )
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("member review-result.sh --status enum: unexpected ['blocked']", out)

    def test_shell_renamed_token_reports_missing_and_unexpected(self):
        self._write("RESULT_TOOL_PATH", _shell_case_fixture(tokens=("no-change", "amended", "questions")))
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn("member review-result.sh --status enum: missing ['changed'] unexpected ['amended']", out)

    def test_empty_region_all_three_tokens_missing(self):
        self._write(
            "RESULT_TOOL_PATH",
            "#!/usr/bin/env bash\n# <!-- parity:verdict-enum:start -->\n# <!-- parity:verdict-enum:end -->\n",
        )
        rc, out = self._run()
        self.assertEqual(rc, 1)
        self.assertIn(
            "member review-result.sh --status enum: missing ['changed', 'no-change', 'questions']", out
        )

    def test_deleted_end_marker_exits_2_not_reported_as_parity(self):
        self._write(
            "RESULT_TOOL_PATH",
            '#!/usr/bin/env bash\n# <!-- parity:verdict-enum:start -->\ncase "$status" in\n  no-change)\n    ;;\nesac\n',
        )
        rc, out = self._run()
        self.assertEqual(rc, 2)
        self.assertIn("PARITY EXTRACTION ERROR", out)
        self.assertNotIn("parity: ok", out)
        self.assertNotIn("PARITY FAIL", out)

    def test_synthesis_output_heading_renamed_exits_2_not_a_silent_skip(self):
        self._write("SYNTHESIS_PROMPT_PATH", _synthesis_fixture(heading="## Outputs"))
        rc, out = self._run()
        self.assertEqual(rc, 2)
        self.assertIn("PARITY EXTRACTION ERROR", out)
        self.assertNotIn("parity: ok", out)


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
