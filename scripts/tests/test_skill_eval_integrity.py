import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from skill_eval import integrity  # noqa: E402

_FIXTURES = _AUDITING_DIR / "skill_eval" / "fixtures" / "integrity"
_HOLDOUT_SRC = _FIXTURES / "holdout_source.json"
_HOLDOUT_SRC_SHORT = _FIXTURES / "holdout_source_short.json"
_ASSERTIONS_SRC = _FIXTURES / "assertions_source.json"
_FIXTURE_SKILLS_DIR = _FIXTURES / "skills"
_FIXTURE_TRIGGER_DIR = _FIXTURES / "trigger-cases"


class TempDirMixin:
    def make_tmp(self) -> Path:
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)


class SealUnsealRoundTripTests(TempDirMixin, unittest.TestCase):
    def test_round_trip_holdout(self):
        sealed_dir = self.make_tmp()
        dest = integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        self.assertTrue(dest.exists())

        data = integrity.unseal(dest)
        self.assertEqual(data["skill"], "demo-skill")
        self.assertEqual(data["kind"], "holdout")
        self.assertTrue(data["canary"].startswith("SKILL-EVAL-CANARY-"))
        self.assertEqual(data["payload"]["canary"], data["canary"])
        prompts = [c["prompt"] for c in data["payload"]["cases"]]
        self.assertIn(
            "draft a rollback plan before the migration window closes tonight for payments",
            prompts,
        )

    def test_round_trip_assertions(self):
        sealed_dir = self.make_tmp()
        dest = integrity.seal(_ASSERTIONS_SRC, "demo-skill", "assertions", sealed_dir=sealed_dir)
        data = integrity.unseal(dest)
        self.assertEqual(data["kind"], "assertions")
        self.assertEqual(data["payload"]["assertions"][0]["id"], "a1")

    def test_header_readable_without_decoding_payload(self):
        sealed_dir = self.make_tmp()
        dest = integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        header = integrity.read_header(dest)
        self.assertEqual(header["skill"], "demo-skill")
        self.assertEqual(header["kind"], "holdout")
        self.assertIn("sha256", header)
        self.assertIn("canary", header)

    def test_invalid_holdout_shape_rejected(self):
        sealed_dir = self.make_tmp()
        bad_src = self.make_tmp() / "bad.json"
        bad_src.write_text(json.dumps({"cases": [{"prompt": "x"}]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            integrity.seal(bad_src, "demo-skill", "holdout", sealed_dir=sealed_dir)

    def test_invalid_assertions_shape_rejected(self):
        sealed_dir = self.make_tmp()
        bad_src = self.make_tmp() / "bad.json"
        bad_src.write_text(json.dumps({"assertions": [{"id": "a1"}]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            integrity.seal(bad_src, "demo-skill", "assertions", sealed_dir=sealed_dir)


class TamperDetectionTests(TempDirMixin, unittest.TestCase):
    def test_flipped_payload_byte_fails_sha256_check(self):
        sealed_dir = self.make_tmp()
        dest = integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        lines = dest.read_text(encoding="utf-8").splitlines()
        header_line, b64_line = lines[0], lines[1]
        # Flip one base64 character so the decoded plaintext (and therefore
        # its sha256) differs from the header's recorded sha256.
        chars = list(b64_line)
        for i, ch in enumerate(chars):
            if ch != "A":
                chars[i] = "A"
                break
        tampered_b64 = "".join(chars)
        dest.write_text(header_line + "\n" + tampered_b64 + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            integrity.unseal(dest)

    def test_tampered_header_sha256_field_fails(self):
        sealed_dir = self.make_tmp()
        dest = integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        lines = dest.read_text(encoding="utf-8").splitlines()
        header = json.loads(lines[0])
        header["sha256"] = "0" * 64
        dest.write_text(json.dumps(header) + "\n" + lines[1] + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            integrity.unseal(dest)


class OverwriteRefusalTests(TempDirMixin, unittest.TestCase):
    def test_seal_refuses_to_overwrite_without_force(self):
        sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        with self.assertRaises(FileExistsError):
            integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)

    def test_seal_overwrites_with_force(self):
        sealed_dir = self.make_tmp()
        first = integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        first_canary = integrity.read_header(first)["canary"]
        second = integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir,
                                 force=True)
        second_canary = integrity.read_header(second)["canary"]
        self.assertEqual(first, second)
        self.assertNotEqual(first_canary, second_canary)


class CanaryScanTests(TempDirMixin, unittest.TestCase):
    def test_canary_planted_in_skill_is_found(self):
        sealed_dir = self.make_tmp()
        sealed = integrity.seal(_HOLDOUT_SRC, "leaky-skill", "holdout", sealed_dir=sealed_dir)
        canary = integrity.read_header(sealed)["canary"]

        skills_dir = self.make_tmp()
        skill_dir = skills_dir / "leaky-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: leaky-skill\ndescription: test\n---\n\nSecret note: {canary}\n",
            encoding="utf-8",
        )
        empty_trigger_dir = self.make_tmp()

        findings = integrity.scan("leaky-skill", skills_dir=skills_dir, sealed_dir=sealed_dir,
                                   trigger_dir=empty_trigger_dir)
        canary_findings = [f for f in findings if f.code == "canary-leak"]
        self.assertTrue(canary_findings, "expected a canary-leak finding")
        self.assertTrue(all(f.severity == "error" for f in canary_findings))

    def test_clean_skill_gives_no_canary_finding(self):
        sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC, "leaky-skill", "holdout", sealed_dir=sealed_dir)

        skills_dir = self.make_tmp()
        skill_dir = skills_dir / "clean-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: clean-skill\ndescription: test\n---\n\nNothing to see here.\n",
            encoding="utf-8",
        )
        empty_trigger_dir = self.make_tmp()

        findings = integrity.scan("clean-skill", skills_dir=skills_dir, sealed_dir=sealed_dir,
                                   trigger_dir=empty_trigger_dir)
        self.assertFalse([f for f in findings if f.code == "canary-leak"])


class TokenRunBoundaryTests(TempDirMixin, unittest.TestCase):
    """Proves the n=8 boundary both ways with the checked-in fixtures.

    scripts/auditing/skill_eval/fixtures/integrity/skills/skill-with-leak
    shares a 10-token run with the sealed holdout prompt (>= 8: error).
    .../skill-clean-boundary shares only 7 tokens (< 8: no error), by design.
    """

    def setUp(self):
        self.sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC, "skill-with-leak", "holdout", sealed_dir=self.sealed_dir)
        integrity.seal(_HOLDOUT_SRC, "skill-clean-boundary", "holdout", sealed_dir=self.sealed_dir)

    def test_eight_token_run_is_an_error(self):
        findings = integrity.scan(
            "skill-with-leak", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=self.sealed_dir, trigger_dir=_FIXTURE_TRIGGER_DIR,
        )
        holdout_hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(holdout_hits, "expected a holdout-leak error at n=8")
        self.assertTrue(all(f.severity == "error" for f in holdout_hits))

    def test_seven_token_run_is_not_an_error(self):
        findings = integrity.scan(
            "skill-clean-boundary", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=self.sealed_dir, trigger_dir=_FIXTURE_TRIGGER_DIR,
        )
        holdout_hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertFalse(holdout_hits, "a 7-token shared run must not trigger at n=8")

    def test_no_overlap_skill_is_clean(self):
        findings = integrity.scan(
            "skill-no-overlap", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=self.sealed_dir, trigger_dir=_FIXTURE_TRIGGER_DIR,
        )
        self.assertFalse([f for f in findings if f.severity == "error"])


class TriggerCaseScanTests(unittest.TestCase):
    def test_own_trigger_case_prompt_is_warn_not_error(self):
        empty_sealed = tempfile.TemporaryDirectory()
        self.addCleanup(empty_sealed.cleanup)
        findings = integrity.scan(
            "skill-with-leak", n=6, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=Path(empty_sealed.name), trigger_dir=_FIXTURE_TRIGGER_DIR,
        )
        own_trigger_hits = [f for f in findings if f.code == "trigger-case-echo"]
        self.assertTrue(own_trigger_hits)
        self.assertTrue(all(f.severity == "warn" for f in own_trigger_hits))

    def test_load_all_trigger_prompts_uses_cases_load_cases(self):
        """integrity.py no longer has its own parser (review finding: minor);
        load_all_trigger_prompts goes through cases.load_cases, which also
        handles single-quoted and bare prompts the old regex parser missed."""
        trigger_dir = tempfile.TemporaryDirectory()
        self.addCleanup(trigger_dir.cleanup)
        (Path(trigger_dir.name) / "demo.md").write_text(
            "# Trigger Cases: demo\n\n"
            "## Positive (should activate)\n"
            '- prompt: "Please help me plan a migration rollback"\n'
            "  expect_activate: yes\n\n"
            "- prompt: 'Single quoted prompt about a rollback plan'\n"
            "  expect_activate: yes\n\n"
            "## Negative (should not activate)\n"
            "- prompt: Bare unquoted prompt, no quotes at all\n"
            "  expect_activate: no\n",
            encoding="utf-8",
        )
        rows = integrity.load_all_trigger_prompts(Path(trigger_dir.name))
        prompts = {r["prompt"]: r["expect"] for r in rows}
        self.assertEqual(prompts["Please help me plan a migration rollback"], True)
        self.assertEqual(prompts["Single quoted prompt about a rollback plan"], True)
        self.assertEqual(prompts["Bare unquoted prompt, no quotes at all"], False)


class DiffParsingTests(unittest.TestCase):
    def test_counts_added_lines_only(self):
        diff_text = (
            "diff --git a/skills/foo/SKILL.md b/skills/foo/SKILL.md\n"
            "index 1111111..2222222 100644\n"
            "--- a/skills/foo/SKILL.md\n"
            "+++ b/skills/foo/SKILL.md\n"
            "@@ -3,2 +3,3 @@\n"
            "-old line one\n"
            "-old line two\n"
            "+new line one\n"
            "+new line two\n"
            "+new line three\n"
        )
        added = integrity.parse_added_lines(diff_text)
        self.assertEqual(added, ["new line one", "new line two", "new line three"])

    def test_ignores_plus_plus_plus_header(self):
        diff_text = "+++ b/skills/foo/SKILL.md\n+actual added line\n"
        added = integrity.parse_added_lines(diff_text)
        self.assertEqual(added, ["actual added line"])

    def test_empty_diff_gives_no_added_lines(self):
        self.assertEqual(integrity.parse_added_lines(""), [])

    def test_diff_scan_finds_leak_in_added_lines(self):
        """diff_scan reuses _scan_text on parsed added lines; verify the glue
        by calling the internal text-scan path with a synthetic added-lines
        blob instead of invoking git (no subprocess in tests)."""
        sealed_dir = tempfile.TemporaryDirectory()
        self.addCleanup(sealed_dir.cleanup)
        integrity.seal(_HOLDOUT_SRC, "some-skill", "holdout", sealed_dir=Path(sealed_dir.name))
        materials = integrity.build_materials(
            n=8, skill_for_sealed="some-skill", sealed_dir=Path(sealed_dir.name),
            trigger_dir=Path(tempfile.mkdtemp()),
        )
        diff_text = (
            "+++ b/skills/some-skill/SKILL.md\n"
            "+you should draft a rollback plan before the migration window closes tonight\n"
        )
        added_lines = integrity.parse_added_lines(diff_text)
        findings = integrity._scan_text(
            label="skills/some-skill/<added-lines vs base>",
            text="\n".join(added_lines), scanned_skill="some-skill",
            materials=materials, n=8,
        )
        self.assertTrue([f for f in findings if f.code == "holdout-leak"])


class SealDirListShowTests(TempDirMixin, unittest.TestCase):
    def test_list_sealed_reports_header_fields(self):
        sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC, "demo-skill", "holdout", sealed_dir=sealed_dir)
        rows = integrity.list_sealed(sealed_dir=sealed_dir)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["skill"], "demo-skill")
        self.assertEqual(rows[0]["kind"], "holdout")

    def test_list_sealed_empty_dir(self):
        sealed_dir = self.make_tmp()
        self.assertEqual(integrity.list_sealed(sealed_dir=sealed_dir), [])


class ShortMaterialFloorTests(TempDirMixin, unittest.TestCase):
    """I8: a holdout prompt shorter than n=8 tokens must still be indexed,
    at min(n, len(tokens)) with a floor of 3, so a 5-token prompt matches on
    a 5-token contiguous run instead of producing no n-grams at all."""

    def setUp(self):
        self.sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC_SHORT, "skill-short-leak", "holdout",
                        sealed_dir=self.sealed_dir)
        integrity.seal(_HOLDOUT_SRC_SHORT, "skill-short-scattered", "holdout",
                        sealed_dir=self.sealed_dir)

    def test_five_token_prompt_pasted_verbatim_is_an_error(self):
        findings = integrity.scan(
            "skill-short-leak", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=self.sealed_dir, trigger_dir=self.make_tmp(),
        )
        holdout_hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(holdout_hits, "a 5-token holdout prompt pasted verbatim must be caught")
        self.assertTrue(all(f.severity == "error" for f in holdout_hits))

    def test_five_token_prompt_scattered_is_not_an_error(self):
        findings = integrity.scan(
            "skill-short-scattered", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=self.sealed_dir, trigger_dir=self.make_tmp(),
        )
        holdout_hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertFalse(holdout_hits,
                          "the same words in scattered order must not trigger a leak finding")


class SuffixAgnosticScanTests(TempDirMixin, unittest.TestCase):
    """I9: scan must check every UTF-8 text file under skills/<skill>/, not
    just an 8-suffix allowlist, since vendors.build_home copies the whole
    skill directory into an arm."""

    def test_leak_in_csv_reference_file_is_found(self):
        sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC, "skill-with-extras", "holdout", sealed_dir=sealed_dir)
        findings = integrity.scan(
            "skill-with-extras", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(hits, "a leak inside references/cases.csv must be caught")
        self.assertTrue(any("cases.csv" in f.path for f in hits))

    def test_binary_file_in_skill_dir_is_skipped_without_crashing(self):
        skills_dir = self.make_tmp()
        skill_dir = skills_dir / "skill-with-binary"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: skill-with-binary\ndescription: test\n---\n\nNothing here.\n",
            encoding="utf-8",
        )
        (skill_dir / "logo.bin").write_bytes(b"\x89PNG\x00\x01\x02\xff\xfe")
        sealed_dir = self.make_tmp()
        # Should not raise despite the binary, extensionless-suffix file.
        findings = integrity.scan(
            "skill-with-binary", skills_dir=skills_dir, sealed_dir=sealed_dir,
            trigger_dir=self.make_tmp(),
        )
        self.assertEqual(findings, [])


class ForeignSealedMaterialTests(TempDirMixin, unittest.TestCase):
    """I10: skill X must be checked against every sealed set in the library,
    not only its own -- another skill's sealed holdout pasted into X is an
    error too, since sealed material is never legitimate in any skill."""

    def test_another_skills_holdout_pasted_into_this_skill_is_an_error(self):
        sealed_dir = self.make_tmp()
        # Sealed under a DIFFERENT skill than the one we scan.
        integrity.seal(_HOLDOUT_SRC, "other-skill", "holdout", sealed_dir=sealed_dir)

        findings = integrity.scan(
            "skill-foreign-leak", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(hits, "another skill's sealed holdout pasted into this skill must error")
        self.assertTrue(all(f.severity == "error" for f in hits))
        self.assertTrue(any("other-skill" in f.message for f in hits))

    def test_no_sealed_material_at_all_is_clean(self):
        sealed_dir = self.make_tmp()  # empty
        findings = integrity.scan(
            "skill-foreign-leak", n=8, skills_dir=_FIXTURE_SKILLS_DIR,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        self.assertFalse([f for f in findings if f.severity == "error"])


class DedupKeyTests(TempDirMixin, unittest.TestCase):
    """Minor finding: the dedup key used a 40-char ref_id prefix, so two
    distinct materials sharing that prefix collapsed into one finding. The
    key must be (kind, owner, full-material-id) instead."""

    def test_two_materials_sharing_a_40_char_prefix_both_get_reported(self):
        prefix40 = "alpha bravo charlie delta echo foxtrot golf hotel"[:40]
        p1 = prefix40 + "one two three four five six seven eight"
        p2 = prefix40 + "nine ten eleven twelve thirteen fourteen fifteen"
        self.assertEqual(p1[:40], p2[:40])  # the old bug's collision condition

        src = self.make_tmp() / "dup.json"
        src.write_text(json.dumps({"cases": [
            {"prompt": p1, "expect": True, "tags": []},
            {"prompt": p2, "expect": True, "tags": []},
        ]}), encoding="utf-8")

        sealed_dir = self.make_tmp()
        integrity.seal(src, "dup-owner", "holdout", sealed_dir=sealed_dir)

        skills_dir = self.make_tmp()
        skill_dir = skills_dir / "dup-owner"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: dup-owner\ndescription: test\n---\n\n{p1}\n\n{p2}\n",
            encoding="utf-8",
        )

        findings = integrity.scan(
            "dup-owner", n=8, skills_dir=skills_dir, sealed_dir=sealed_dir,
            trigger_dir=self.make_tmp(),
        )
        hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertEqual(len(hits), 2, f"expected both distinct materials reported, got {hits}")


class AddedLinesDoublePlusTests(unittest.TestCase):
    """Minor finding: an added line whose content begins with `++` was
    dropped because it looked like a `+++` file header. Headers are only
    valid before a section's first `@@` hunk marker."""

    def test_added_line_starting_with_plus_plus_after_hunk_marker_is_kept(self):
        diff_text = (
            "diff --git a/skills/foo/SKILL.md b/skills/foo/SKILL.md\n"
            "--- a/skills/foo/SKILL.md\n"
            "+++ b/skills/foo/SKILL.md\n"
            "@@ -1,0 +1,2 @@\n"
            "+regular added line\n"
            "+++ this line's content genuinely starts with two plus signs\n"
        )
        added = integrity.parse_added_lines(diff_text)
        self.assertIn("regular added line", added)
        self.assertIn(
            "++ this line's content genuinely starts with two plus signs", added
        )

    def test_multi_file_diff_treats_each_section_header_separately(self):
        diff_text = (
            "diff --git a/skills/a/SKILL.md b/skills/a/SKILL.md\n"
            "--- a/skills/a/SKILL.md\n"
            "+++ b/skills/a/SKILL.md\n"
            "@@ -1,0 +1,1 @@\n"
            "+first file line\n"
            "diff --git a/skills/a/other.md b/skills/a/other.md\n"
            "--- a/skills/a/other.md\n"
            "+++ b/skills/a/other.md\n"
            "@@ -1,0 +1,1 @@\n"
            "+second file line\n"
        )
        added = integrity.parse_added_lines(diff_text)
        self.assertEqual(added, ["first file line", "second file line"])


class GitHelperMockedTests(TempDirMixin, unittest.TestCase):
    """diff_scan must never crash on a bad ref or shell out in tests; the
    git helper is mocked here per the review's constraint."""

    def test_bad_ref_yields_an_error_finding_not_a_traceback(self):
        repo_root = self.make_tmp()
        sealed_dir = self.make_tmp()

        def fake_git(args, cwd):
            if args[0] == "diff":
                raise integrity.GitError(
                    "git diff --no-color --no-ext-diff --unified=0 nope-ref -- "
                    "skills/some-skill/ failed: unknown revision 'nope-ref'"
                )
            raise AssertionError(f"unexpected git call in this test: {args}")

        with mock.patch.object(integrity, "_git", side_effect=fake_git):
            findings = integrity.diff_scan(
                "some-skill", "nope-ref", skills_dir=self.make_tmp(),
                sealed_dir=sealed_dir, trigger_dir=self.make_tmp(), repo_root=repo_root,
            )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "error")
        self.assertEqual(findings[0].code, "bad-git-ref")

    def test_untracked_and_gitignored_files_are_scanned(self):
        repo_root = self.make_tmp()
        skill_dir = repo_root / "skills" / "diffed-skill"
        skill_dir.mkdir(parents=True)
        # This file would be excluded by --exclude-standard if it matched a
        # .gitignore rule; diff_scan must see it regardless (I9).
        leaked = skill_dir / "scratch-notes.md"
        leaked.write_text(
            "draft a rollback plan before the migration window closes tonight for payments\n",
            encoding="utf-8",
        )

        sealed_dir = self.make_tmp()
        integrity.seal(_HOLDOUT_SRC, "diffed-skill", "holdout", sealed_dir=sealed_dir)

        calls = []

        def fake_git(args, cwd):
            calls.append(args)
            if args[0] == "diff":
                return ""
            if args[0] == "ls-files":
                self.assertNotIn("--exclude-standard", args)
                return "skills/diffed-skill/scratch-notes.md\n"
            raise AssertionError(f"unexpected git call: {args}")

        with mock.patch.object(integrity, "_git", side_effect=fake_git):
            findings = integrity.diff_scan(
                "diffed-skill", "HEAD", skills_dir=repo_root / "skills",
                sealed_dir=sealed_dir, trigger_dir=self.make_tmp(), repo_root=repo_root,
            )
        self.assertTrue([f for f in findings if f.code == "holdout-leak"])
        self.assertTrue(any(c[0] == "diff" for c in calls))
        self.assertTrue(any(c[0] == "ls-files" for c in calls))


class HoldoutTextNeverInMessageTests(TempDirMixin, unittest.TestCase):
    """Round-3 finding: scan()/diff-scan must never print holdout or
    assertion text (not even the first 40 characters) in a finding message
    -- only a material id / sha256 prefix. The skill-side matched snippet is
    fine to show, since that text is already public in the skill file."""

    def test_holdout_leak_message_never_contains_the_holdout_prompt_text(self):
        # The skill-side matched snippet legitimately shows text that
        # already appears in the skill (it's just the matched run), so this
        # fixture is built so the matched run sits in the *middle* of the
        # holdout prompt, well past its first 40 characters: only the
        # matched run may legitimately appear in the message, and the
        # first-40-chars prefix (what the old code printed as `ref_id`)
        # must never appear at all, since it was never pasted into the
        # skill.
        prefix = "zzzzzzzzzzone zzzzzzzzzztwo zzzzzzzzzzthree zzzzzzzzzzfour"
        matched_run = "keepalpha keepbravo keepcharlie keepdelta keepecho keepfoxtrot keepgolf keephotel"
        suffix = "zzzzzzzzzzfive zzzzzzzzzzsix"
        holdout_prompt = f"{prefix} {matched_run} {suffix}"
        self.assertNotIn("keep", holdout_prompt[:40])  # sanity: prefix crowds out the run

        sealed_dir = self.make_tmp()
        src = self.make_tmp() / "holdout.json"
        src.write_text(
            json.dumps({"cases": [{"prompt": holdout_prompt, "expect": True, "tags": []}]}),
            encoding="utf-8",
        )
        integrity.seal(src, "skill-msg-leak", "holdout", sealed_dir=sealed_dir)

        skills_root = self.make_tmp()
        skill_dir = skills_root / "skill-msg-leak"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: skill-msg-leak\ndescription: test\n---\n\n"
            f"Some unrelated notes. {matched_run} more unrelated notes.\n",
            encoding="utf-8",
        )

        findings = integrity.scan(
            "skill-msg-leak", n=8, skills_dir=skills_root,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        holdout_hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(holdout_hits)
        for f in holdout_hits:
            self.assertNotIn(holdout_prompt[:40], f.message)
            self.assertNotIn(prefix, f.message)
            self.assertNotIn(suffix, f.message)
            # a material id / sha256 prefix must be present instead
            self.assertIn("sha256:", f.message)

    def test_assertions_leak_message_never_contains_the_assertion_text(self):
        sealed_dir = self.make_tmp()
        integrity.seal(_ASSERTIONS_SRC, "skill-with-leak", "assertions", sealed_dir=sealed_dir)

        skills_dir = self.make_tmp()
        skill_dir = skills_dir / "skill-with-leak"
        skill_dir.mkdir()
        assertions_payload = json.loads(_ASSERTIONS_SRC.read_text(encoding="utf-8"))
        a_text = assertions_payload["assertions"][0]["text"]
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: skill-with-leak\ndescription: test\n---\n\n{a_text}\n",
            encoding="utf-8",
        )

        findings = integrity.scan(
            "skill-with-leak", n=3, skills_dir=skills_dir,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        assertion_hits = [f for f in findings if f.code == "assertions-leak"]
        self.assertTrue(assertion_hits, "expected an assertions-leak finding")
        for f in assertion_hits:
            self.assertNotIn(a_text, f.message)
            self.assertIn("sha256:", f.message)


class ShortMaterialSkippedVisiblyTests(TempDirMixin, unittest.TestCase):
    """Round-3 finding: material under FLOOR_N tokens was skipped silently.
    scan() must now emit one info finding per such material, naming only its
    id -- never the material text -- and FLOOR_N must be pinned at exactly 3
    (a mutation to FLOOR_N=1 must make a 2-token material match, which these
    tests catch)."""

    def _seal_holdout(self, sealed_dir, skill, prompt):
        src = self.make_tmp() / "holdout.json"
        src.write_text(json.dumps({"cases": [{"prompt": prompt, "expect": True, "tags": []}]}),
                        encoding="utf-8")
        integrity.seal(src, skill, "holdout", sealed_dir=sealed_dir)

    def _skill_dir(self, skills_root, skill, body):
        skill_dir = skills_root / skill
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: test\n---\n\n{body}\n", encoding="utf-8",
        )
        return skill_dir

    def test_three_token_material_is_indexed_and_matches_at_the_floor(self):
        # FLOOR_N == 3: a 3-token material must be indexed and caught when
        # pasted verbatim. If FLOOR_N were mutated to 1, this still passes
        # (a stronger floor only shrinks what's indexed), so this test
        # alone doesn't pin the mutation -- paired with the 2-token test
        # below, it does: a mutation to FLOOR_N=1 doesn't change 3-token
        # behaviour, but does change 2-token behaviour.
        sealed_dir = self.make_tmp()
        self._seal_holdout(sealed_dir, "skill-floor-three", "alpha bravo charlie")
        skills_root = self.make_tmp()
        self._skill_dir(skills_root, "skill-floor-three", "Some notes: alpha bravo charlie here.")

        findings = integrity.scan(
            "skill-floor-three", n=8, skills_dir=skills_root,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(hits, "a 3-token holdout material pasted verbatim must be caught")

    def test_two_token_material_never_matches_and_is_reported_as_skipped(self):
        # Pins FLOOR_N == 3 against a mutation to FLOOR_N == 1: at FLOOR_N=1
        # a 2-token material would get indexed (eff_n=2) and this pasted
        # copy would then match, flipping this assertion.
        sealed_dir = self.make_tmp()
        self._seal_holdout(sealed_dir, "skill-floor-two", "alpha bravo")
        skills_root = self.make_tmp()
        self._skill_dir(skills_root, "skill-floor-two", "Some notes: alpha bravo here.")

        findings = integrity.scan(
            "skill-floor-two", n=8, skills_dir=skills_root,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertFalse(hits, "a 2-token material is below FLOOR_N and must never match")

        skipped = [f for f in findings if f.code == "material-too-short"]
        self.assertTrue(skipped, "a too-short material must be reported, not silently dropped")
        for f in skipped:
            self.assertEqual(f.severity, "info")
            self.assertNotIn("alpha bravo", f.message)
            self.assertIn("sha256:", f.message)


class DefaultNBoundaryTests(TempDirMixin, unittest.TestCase):
    """Round-3 finding: DEFAULT_N == 8 was left unpinned (a mutation to 16
    left the tests green). Builds a >16-token holdout material with an
    8-token shared run against the scanned skill and calls scan() WITHOUT
    passing n, so it exercises the real default. At n=8 (correct) the run
    matches; at a mutated n=16 the same 8-token run would need indexing at
    16 tokens and would be missed."""

    def test_eight_token_run_is_an_error_at_the_real_default_n(self):
        words = [f"tok{i}" for i in range(1, 21)]  # 20 distinct tokens
        holdout_prompt = " ".join(words)
        shared_run = " ".join(words[4:12])  # tok5..tok12, exactly 8 tokens

        sealed_dir = self.make_tmp()
        src = self.make_tmp() / "holdout.json"
        src.write_text(
            json.dumps({"cases": [{"prompt": holdout_prompt, "expect": True, "tags": []}]}),
            encoding="utf-8",
        )
        integrity.seal(src, "skill-default-n", "holdout", sealed_dir=sealed_dir)

        skills_root = self.make_tmp()
        skill_dir = skills_root / "skill-default-n"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: skill-default-n\ndescription: test\n---\n\n"
            f"Unrelated preamble text. {shared_run} unrelated trailing text.\n",
            encoding="utf-8",
        )

        # No `n=` passed: exercises integrity.DEFAULT_N directly.
        findings = integrity.scan(
            "skill-default-n", skills_dir=skills_root,
            sealed_dir=sealed_dir, trigger_dir=self.make_tmp(),
        )
        hits = [f for f in findings if f.code == "holdout-leak"]
        self.assertTrue(
            hits,
            "an 8-token shared run must be an error at the real DEFAULT_N=8; "
            "if DEFAULT_N were 16 this run (shorter than 16) would be missed",
        )


class CorruptSealedFileTests(TempDirMixin, unittest.TestCase):
    """Minor finding: a corrupt sealed file must become an error Finding,
    never a raised exception that kills the whole scan."""

    def test_corrupt_sealed_file_becomes_a_finding_not_a_crash(self):
        sealed_dir = self.make_tmp()
        dest = integrity.seal(_HOLDOUT_SRC, "some-owner", "holdout", sealed_dir=sealed_dir)
        lines = dest.read_text(encoding="utf-8").splitlines()
        header_line, b64_line = lines[0], lines[1]
        chars = list(b64_line)
        for i, ch in enumerate(chars):
            if ch != "A":
                chars[i] = "A"
                break
        dest.write_text(header_line + "\n" + "".join(chars) + "\n", encoding="utf-8")

        skills_dir = self.make_tmp()
        skill_dir = skills_dir / "clean-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: clean-skill\ndescription: test\n---\n\nNothing special.\n",
            encoding="utf-8",
        )

        findings = integrity.scan(
            "clean-skill", skills_dir=skills_dir, sealed_dir=sealed_dir,
            trigger_dir=self.make_tmp(),
        )
        corrupt = [f for f in findings if f.code == "corrupt-sealed-file"]
        self.assertTrue(corrupt)
        self.assertTrue(all(f.severity == "error" for f in corrupt))

    def test_cli_scan_prints_clean_message_and_exits_2_on_operational_error(self):
        findings = [integrity.Finding("error", "corrupt-sealed-file", "boom", "some/path")]
        failed = integrity._operational_failure(findings, command="scan")
        self.assertEqual(failed, 2)
        findings_clean = [integrity.Finding("error", "holdout-leak", "leak", "some/path")]
        self.assertIsNone(integrity._operational_failure(findings_clean, command="scan"))


if __name__ == "__main__":
    unittest.main()
