from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(TESTS_DIR))

import audit_skills as audit  # noqa: E402
import generate_snapshot  # noqa: E402

MINIMAL_FRONTMATTER = (
    "---\n"
    "name: {name}\n"
    "description: test skill\n"
    "metadata:\n"
    "  category: testing\n"
    "---\n\n"
)

SNAPSHOT_PATH = TESTS_DIR / "data" / "audit_snapshot.json"


def _write_skill(
    root: Path,
    name: str,
    skill_md: str,
    references: dict[str, str] | None = None,
    resources: dict[str, str] | None = None,
) -> Path:
    dirpath = root / name
    dirpath.mkdir(parents=True)
    (dirpath / "SKILL.md").write_text(skill_md, encoding="utf-8")
    for sub, files in (("references", references or {}), ("resources", resources or {})):
        if not files:
            continue
        subdir = dirpath / sub
        subdir.mkdir()
        for fname, content in files.items():
            (subdir / fname).write_text(content, encoding="utf-8")
    return dirpath


class RepoRootSkillPathRegexTest(unittest.TestCase):
    def test_ac1_reference_only_repo_root_path_reported(self):
        """A repo-root skill path reachable only through references/ is still reported.

        Reproduces the false negative that motivated the check (`scan_skill` read
        SKILL.md alone, so `skills/refactor-clean/scripts/scan_hotspots.sh` in
        `references/analysis-and-hotspots.md` went undetected). Pinned as a fixture:
        the live occurrence was corrected in `7e039e9`, and asserting on a defect
        still being present in the tree makes the test fail as the corpus improves.
        """
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
                references={
                    "analysis-and-hotspots.md": (
                        "- Use `skills/sample/scripts/scan_hotspots.sh` for a quick inventory.\n"
                    )
                },
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            matches = [i for i in issues if i.startswith("repo_root_skill_path:")]
            self.assertEqual(len(matches), 1)
            self.assertEqual(
                matches[0],
                "repo_root_skill_path:references/analysis-and-hotspots.md:"
                "skills/sample/scripts/scan_hotspots.sh",
            )

    def test_ac2_documented_install_paths_not_reported(self):
        install_paths = [
            "~/.codex/skills/testing/SKILL.md",
            "~/.claude/skills/testing/SKILL.md",
            ".codex/skills/testing/SKILL.md",
            ".claude/skills/testing/SKILL.md",
        ]
        for path in install_paths:
            with self.subTest(path=path):
                self.assertEqual(list(audit.REPO_ROOT_SKILL_PATH_RE.finditer(path)), [])

    def test_ac3_uppercase_folder_reported(self):
        got = [m.group(0) for m in audit.REPO_ROOT_SKILL_PATH_RE.finditer("skills/Testing/SKILL.md")]
        self.assertEqual(got, ["skills/Testing/SKILL.md"])

    def test_ac3_underscore_folder_reported(self):
        got = [m.group(0) for m in audit.REPO_ROOT_SKILL_PATH_RE.finditer("skills/my_skill/scripts/x.sh")]
        self.assertEqual(got, ["skills/my_skill/scripts/x.sh"])

    def test_ac3_parent_relative_prefix_preserved(self):
        got = [
            m.group(0)
            for m in audit.REPO_ROOT_SKILL_PATH_RE.finditer("../skills/refactor-clean/scripts/x.sh")
        ]
        self.assertEqual(got, ["../skills/refactor-clean/scripts/x.sh"])

    def test_ac3_trailing_sentence_period_excluded(self):
        got = [
            m.group(0)
            for m in audit.REPO_ROOT_SKILL_PATH_RE.finditer("See skills/refactor-clean/scripts/x.sh.")
        ]
        self.assertEqual(got, ["skills/refactor-clean/scripts/x.sh"])

    def test_ac3_prose_not_reported(self):
        got = list(audit.REPO_ROOT_SKILL_PATH_RE.finditer("Agent skills/tools/registry are evolving"))
        self.assertEqual(got, [])


class SkillTextsAttributionTest(unittest.TestCase):
    def test_ac4_reads_skill_md_then_sorted_references_then_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
                references={"b.md": "Nothing here.\n", "a.md": "Nothing here.\n"},
                resources={"z.md": "Nothing here.\n"},
            )
            pairs, unreadable = audit._skill_texts(dirpath)
            self.assertEqual(unreadable, [])
            self.assertEqual(
                [rel for rel, _ in pairs],
                ["SKILL.md", "references/a.md", "references/b.md", "resources/z.md"],
            )

    def test_ac4_repo_root_finding_names_source_file_sorted_comma_joined(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample")
                + "## Workflow\n`skills/sample/scripts/z.sh`\n",
                references={"a.md": "`skills/sample/scripts/a.sh`\n"},
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            match = next(i for i in issues if i.startswith("repo_root_skill_path:"))
            self.assertEqual(
                match,
                "repo_root_skill_path:"
                "SKILL.md:skills/sample/scripts/z.sh,"
                "references/a.md:skills/sample/scripts/a.sh",
            )

    def test_ac4_missing_local_refs_names_source_file_sorted_comma_joined(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample")
                + "## Workflow\nSee `references/missing.md`.\n",
                references={"a.md": "See `references/also-missing.md`.\n"},
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            match = next(i for i in issues if i.startswith("missing_local_refs:"))
            self.assertEqual(
                match,
                "missing_local_refs:"
                "SKILL.md:references/missing.md,"
                "references/a.md:references/also-missing.md",
            )


class SkillInternalPrefixFilterTest(unittest.TestCase):
    def test_ac5_project_layout_paths_in_references_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
                references={
                    "a.md": (
                        "See `docs/adr/README.md`, `conductor/product.md`, "
                        "and `tracks/x/spec.md`.\n"
                    )
                },
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            self.assertFalse(any(i.startswith("missing_local_refs:") for i in issues))

    def test_ac5_skill_internal_prefix_still_checked_in_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
                references={"a.md": "See `references/missing.md` and `scripts/missing.sh`.\n"},
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            match = next(i for i in issues if i.startswith("missing_local_refs:"))
            self.assertEqual(
                match,
                "missing_local_refs:"
                "references/a.md:references/missing.md,"
                "references/a.md:scripts/missing.sh",
            )

    def test_ac5_skill_md_missing_local_refs_behavior_unfiltered(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nSee `docs/adr/README.md`.\n",
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            match = next(i for i in issues if i.startswith("missing_local_refs:"))
            self.assertEqual(match, "missing_local_refs:SKILL.md:docs/adr/README.md")


class UnreadableSkillFileTest(unittest.TestCase):
    def test_broken_symlink_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
                references={"a.md": "Nothing here.\n"},
            )
            (dirpath / "references" / "broken.md").symlink_to(
                dirpath / "references" / "missing-target.md"
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            match = next(i for i in issues if i.startswith("unreadable_skill_file:"))
            self.assertEqual(match, "unreadable_skill_file:references/broken.md:FileNotFoundError")

    def test_non_utf8_file_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
                references={"a.md": "Nothing here.\n"},
            )
            (dirpath / "references" / "binary.md").write_bytes(b"\xff\xfe\x00\x01bad")
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            match = next(i for i in issues if i.startswith("unreadable_skill_file:"))
            self.assertEqual(match, "unreadable_skill_file:references/binary.md:UnicodeDecodeError")

    def test_unreadable_file_does_not_abort_other_checks_on_same_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample")
                + "## Workflow\n`skills/sample/scripts/z.sh`\n",
            )
            (dirpath / "references").mkdir()
            (dirpath / "references" / "broken.md").symlink_to(
                dirpath / "references" / "missing-target.md"
            )
            issues, _ = audit.scan_skill(dirpath, token_checks=False)
            self.assertTrue(any(i.startswith("repo_root_skill_path:") for i in issues))
            self.assertTrue(any(i.startswith("unreadable_skill_file:") for i in issues))

    def test_non_utf8_skill_md_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = _write_skill(
                Path(tmp),
                "sample",
                MINIMAL_FRONTMATTER.format(name="sample") + "## Workflow\nDo it.\n",
            )
            (dirpath / "SKILL.md").write_bytes(b"\xff\xfe\x00\x01bad")
            issues, warnings = audit.scan_skill(dirpath, token_checks=False)
            self.assertEqual(issues, ["unreadable_skill_file:SKILL.md:UnicodeDecodeError"])
            self.assertEqual(warnings, [])

    def test_broken_symlink_skill_md_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirpath = Path(tmp) / "sample"
            dirpath.mkdir()
            (dirpath / "SKILL.md").symlink_to(dirpath / "missing-target.md")
            issues, warnings = audit.scan_skill(dirpath, token_checks=False)
            self.assertEqual(issues, ["unreadable_skill_file:SKILL.md:FileNotFoundError"])
            self.assertEqual(warnings, [])


class MainSkipsBrokenSymlinkSkillMdTest(unittest.TestCase):
    def test_broken_symlink_skill_md_excluded_from_main_without_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(
                root,
                "good-skill",
                MINIMAL_FRONTMATTER.format(name="good-skill") + "## Workflow\nDo it.\n",
            )
            bad_dir = root / "bad-skill"
            bad_dir.mkdir()
            (bad_dir / "SKILL.md").symlink_to(bad_dir / "missing-target.md")

            original_skills_root = audit.SKILLS_ROOT
            audit.SKILLS_ROOT = root
            try:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    exit_code = audit.main(["--no-token-checks"])
            finally:
                audit.SKILLS_ROOT = original_skills_root

            self.assertEqual(exit_code, 0)
            self.assertIn("skills: 1", out.getvalue())


class StripRefNoiseTest(unittest.TestCase):
    def test_ac1_code_spans_removed(self):
        self.assertEqual(
            audit._strip_ref_noise("check `quality-gates.md` first"), "check   first"
        )

    def test_ac1_markdown_links_keep_link_text(self):
        self.assertEqual(
            audit._strip_ref_noise("see [the README](references/README.md) for more"),
            "see the README for more",
        )

    def test_ac1_urls_removed(self):
        self.assertEqual(
            audit._strip_ref_noise("visit https://example.com/docs for detail"),
            "visit   for detail",
        )

    def test_ac1_bare_paths_removed(self):
        self.assertEqual(audit._strip_ref_noise("edit a/b/c.py now"), "edit   now")

    def test_ac1_filenames_removed(self):
        self.assertEqual(audit._strip_ref_noise("open quality-gates.md now"), "open   now")


class HeadingsRestatedNoiseAndScopeTest(unittest.TestCase):
    def test_ac1_backticked_filename_in_prose_no_longer_matches(self):
        lines = [
            "## Quality gates",
            "",
            "Before finalizing, check `quality-gates.md` for the latest guidance.",
        ]
        self.assertEqual(audit._headings_restated(lines), [])

    def test_ac1_noise_stripped_from_heading_too(self):
        lines = [
            "## Check `quality-gates.md`",
            "",
            "Check quality gates before finalizing.",
        ]
        self.assertEqual(audit._headings_restated(lines), [])

    def test_ac2_h3_heading_restated_is_now_scanned(self):
        lines = [
            "### Extract or render",
            "",
            "Extract or render the pages as needed.",
        ]
        self.assertEqual(audit._headings_restated(lines), ["Extract or render"])

    def test_ac2_h4_stays_out_of_scope(self):
        lines = [
            "#### Extract or render",
            "",
            "Extract or render the pages as needed.",
        ]
        self.assertEqual(audit._headings_restated(lines), [])

    def test_ac4_fourteen_word_window_still_matches_at_the_boundary(self):
        lines = [
            "## Emit and report",
            "",
            "one two three four five six seven eight nine ten eleven twelve emit report",
        ]
        self.assertEqual(audit._headings_restated(lines), ["Emit and report"])

    def test_ac4_past_the_fourteen_word_window_no_longer_matches(self):
        lines = [
            "## Emit and report",
            "",
            "one two three four five six seven eight nine ten eleven twelve thirteen emit report",
        ]
        self.assertEqual(audit._headings_restated(lines), [])

    def test_ac4_two_significant_word_gate_still_enforced(self):
        lines = ["## Workflow", "", "Workflow steps follow below."]
        self.assertEqual(audit._headings_restated(lines), [])

    def test_ac4_stopword_filter_still_applied(self):
        lines = [
            "## The Workflow",
            "",
            "The workflow below covers everything you need.",
        ]
        self.assertEqual(audit._headings_restated(lines), [])


class GoldenSnapshotTest(unittest.TestCase):
    def test_ac7_scan_skill_matches_recorded_snapshot_for_all_skills(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        actual = generate_snapshot.build_snapshot()

        expected_names = [s["name"] for s in snapshot]
        actual_names = [s["name"] for s in actual]
        if actual_names != expected_names:
            added = sorted(set(actual_names) - set(expected_names))
            removed = sorted(set(expected_names) - set(actual_names))
            self.fail(
                "skill roster changed vs. snapshot: "
                f"added={added} removed={removed} "
                f"expected_count={len(expected_names)} actual_count={len(actual_names)}"
            )

        expected_by_name = {s["name"]: s for s in snapshot}
        actual_by_name = {s["name"]: s for s in actual}
        for name, expected in expected_by_name.items():
            with self.subTest(skill=name):
                self.maxDiff = None
                self.assertEqual(actual_by_name[name], expected, msg=f"skill={name}")


if __name__ == "__main__":
    unittest.main()
