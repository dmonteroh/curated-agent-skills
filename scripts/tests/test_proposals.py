from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDITING_DIR = REPO_ROOT / "scripts" / "auditing"
sys.path.insert(0, str(AUDITING_DIR))

import proposals  # noqa: E402

OPEN_ITEMS_SCAFFOLD = """# Open items and settled calls

## Parity register

Unrelated section.
"""

REMOVALS_TWO_ITEMS = """REMOVAL PROPOSALS (none executed):

1. `SKILL.md`, `## Alpha` section (whole section) - restates `references/extra.md`. Loss: the inline copy.
2. `references/extra.md` (whole file) - cited nowhere. Loss: nothing reachable.
"""


def _run_cli(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(AUDITING_DIR / "proposals.py"), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )


def rulings_path(root: Path) -> Path:
    return root / "scripts" / "auditing" / "logs" / "removal-rulings.md"


def read_rulings(root: Path) -> str:
    path = rulings_path(root)
    return path.read_text(encoding="utf-8") if path.exists() else ""


def make_scaffold(tmp: Path) -> Path:
    """A minimal git repo with one skill and the auditing surface apply needs."""
    root = tmp / "repo"
    (root / "skills" / "demo-skill" / "references").mkdir(parents=True)
    (root / "skills" / "other-skill").mkdir(parents=True)
    (root / "scripts" / "auditing" / "logs").mkdir(parents=True)
    (root / "scripts" / "auditing" / "trigger-cases").mkdir(parents=True)
    (root / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# demo-skill\n\n## Alpha\n\nBody.\n", encoding="utf-8"
    )
    (root / "skills" / "demo-skill" / "references" / "extra.md").write_text("extra\n", encoding="utf-8")
    (root / "skills" / "other-skill" / "SKILL.md").write_text("# other-skill\n", encoding="utf-8")
    (root / "scripts" / "auditing" / "OPEN_ITEMS.md").write_text(OPEN_ITEMS_SCAFFOLD, encoding="utf-8")
    shutil.copy(AUDITING_DIR / "apply-prompt.md", root / "scripts" / "auditing" / "apply-prompt.md")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "scaffold"],
        cwd=root,
        check=True,
    )
    return root


def write_run_artifacts(root: Path, skill: str, removals: str | None, flag: str = "1") -> None:
    logs = root / "scripts" / "auditing" / "logs"
    (logs / f"{skill}.synthesis.verdict").write_text(
        f"OUTCOME=CHANGED\nDIFFERENTIATION=STRONG\nREMOVAL_PROPOSALS={flag}\n", encoding="utf-8"
    )
    if removals is not None:
        (logs / f"{skill}.synthesis.removals").write_text(removals, encoding="utf-8")


def record(root: Path):
    return _run_cli(
        ["--repo-root", str(root), "record", "--logs-dir", str(root / "scripts" / "auditing" / "logs")]
    )


def ledger_path(root: Path) -> Path:
    return root / "scripts" / "auditing" / "PROPOSALS.md"


def set_ruling(root: Path, entry_id: str, ruling: str) -> None:
    path = ledger_path(root)
    entries = proposals.parse_ledger(path)
    hit = False
    for entry in entries:
        if entry.entry_id == entry_id:
            entry.ruling = ruling
            hit = True
    assert hit, f"no entry {entry_id}"
    proposals.write_ledger(path, entries)


def make_stub(root: Path, body: str) -> str:
    stub = root / "stub-writer.sh"
    stub.write_text("#!/usr/bin/env bash\nset -eu\ncat >/dev/null\n" + body, encoding="utf-8")
    stub.chmod(0o755)
    return str(stub)


class SplitItemsTest(unittest.TestCase):
    def test_numbered_block_splits_and_strips_markers(self):
        items = proposals.split_items(REMOVALS_TWO_ITEMS)
        self.assertEqual(len(items), 2)
        self.assertTrue(items[0].startswith("`SKILL.md`"))
        self.assertTrue(items[1].startswith("`references/extra.md`"))

    def test_ids_stable_under_renumbering(self):
        items = proposals.split_items(REMOVALS_TWO_ITEMS)
        renumbered = "1. " + items[1]
        self.assertEqual(
            proposals.normalized_hash("s", proposals.split_items(renumbered)[0]),
            proposals.normalized_hash("s", items[1]),
        )

    def test_unnumbered_text_is_one_item(self):
        self.assertEqual(proposals.split_items("whole thing,\ntwo lines"), ["whole thing,\ntwo lines"])

    def test_out_of_sequence_number_is_body_not_item(self):
        text = "1. first item mentions\n2038 deadline\n2. second item"
        self.assertEqual(len(proposals.split_items(text)), 2)
        # an indented enumeration inside an item does not start a new one
        nested = "1. first\n  1. nested\n2. second"
        self.assertEqual(len(proposals.split_items(nested)), 2)


class RecordTest(unittest.TestCase):
    def test_record_appends_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_scaffold(Path(d))
            write_run_artifacts(root, "demo-skill", REMOVALS_TWO_ITEMS)
            proc = record(root)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            entries = proposals.parse_ledger(ledger_path(root))
            self.assertEqual(len(entries), 2)
            self.assertTrue(all(e.ruling == "pending" for e in entries))
            again = record(root)
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertIn("0 recorded, 2 already known", again.stdout)
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 2)

    def test_record_skips_zero_flag_and_warns_on_missing_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_scaffold(Path(d))
            write_run_artifacts(root, "demo-skill", REMOVALS_TWO_ITEMS, flag="0")
            write_run_artifacts(root, "other-skill", None, flag="1")
            proc = record(root)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proposals.parse_ledger(ledger_path(root)), [])
            self.assertIn("other-skill", proc.stderr)
            self.assertIn("sidecar", proc.stderr)

    def test_record_skips_ids_already_ruled_in_the_rulings_record(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_scaffold(Path(d))
            items = proposals.split_items(REMOVALS_TWO_ITEMS)
            ruled = proposals.normalized_hash("demo-skill", items[0])
            rulings_path(root).write_text(
                proposals.RULINGS_HEADER
                + f"| 2026-01-01 | `demo-skill` | old `id:{ruled}` | **Declined.** |\n",
                encoding="utf-8",
            )
            write_run_artifacts(root, "demo-skill", REMOVALS_TWO_ITEMS)
            proc = record(root)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            entries = proposals.parse_ledger(ledger_path(root))
            self.assertEqual([e.entry_id for e in entries], [proposals.normalized_hash("demo-skill", items[1])])


class LintTest(unittest.TestCase):
    def _recorded_root(self, d):
        root = make_scaffold(Path(d))
        write_run_artifacts(root, "demo-skill", REMOVALS_TWO_ITEMS)
        self.assertEqual(record(root).returncode, 0)
        return root

    def test_misspelled_ruling_and_edited_text_both_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            entries[0].ruling = "aproved"
            entries[1].text = entries[1].text + " tampered"
            proposals.write_ledger(ledger_path(root), entries)
            proc = _run_cli(["--repo-root", str(root), "lint"])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("'aproved' is not one of: pending | approved | declined", proc.stderr)
            self.assertIn("checksum", proc.stderr)

    def test_ruling_note_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "declined — keep it, load-bearing")
            proc = _run_cli(["--repo-root", str(root), "lint"])
            self.assertEqual(proc.returncode, 0, proc.stderr)


class ApplyTest(unittest.TestCase):
    def _recorded_root(self, d):
        root = make_scaffold(Path(d))
        write_run_artifacts(root, "demo-skill", REMOVALS_TWO_ITEMS)
        assert record(root).returncode == 0
        return root

    def _apply(self, root, stub_body, extra=()):
        stub = make_stub(root, stub_body)
        return _run_cli(
            ["--repo-root", str(root), "apply", "--dispatch-cmd", stub, "--no-audit", *extra]
        )

    def test_nothing_ruled_is_a_noop_and_safe_to_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            for _ in range(2):
                proc = _run_cli(["--repo-root", str(root), "apply", "--no-audit"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("nothing to apply", proc.stdout)
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 2)

    def test_approved_entry_executes_stamps_and_clears(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            target = next(e for e in entries if e.text.startswith("`references/extra.md`"))
            set_ruling(root, target.entry_id, "approved — cut it")
            proc = self._apply(
                root,
                'rm skills/demo-skill/references/extra.md\necho "APPLIED: skills/demo-skill/references/extra.md"\n',
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            remaining = proposals.parse_ledger(ledger_path(root))
            self.assertEqual([e.entry_id for e in remaining], [e.entry_id for e in entries if e is not target])
            rulings = read_rulings(root)
            self.assertIn(f"`id:{target.entry_id}`", rulings)
            self.assertIn("**Approved, executed", rulings)
            self.assertIn("cut it", rulings)
            # run twice: the ruled entry is gone, so a rerun has nothing to do
            again = _run_cli(["--repo-root", str(root), "apply", "--no-audit"])
            self.assertEqual(again.returncode, 0)
            self.assertIn("nothing to apply", again.stdout)

    def test_approved_entry_on_an_already_dirty_file_is_still_verified(self):
        # The synthesis pass leaves the skill file modified and uncommitted;
        # apply's diff detection must still see the writer's further edit.
        # Regression: 2026-08-17, three landed removals were reported as
        # "changed nothing" because path-set comparison is blind to new
        # edits on an already-dirty file.
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            skill_md = root / "skills" / "demo-skill" / "SKILL.md"
            skill_md.write_text(
                skill_md.read_text(encoding="utf-8") + "\nsynthesis edit\n", encoding="utf-8"
            )
            entries = proposals.parse_ledger(ledger_path(root))
            target = next(e for e in entries if e.text.startswith("`SKILL.md`"))
            set_ruling(root, target.entry_id, "approved")
            proc = self._apply(
                root,
                'printf "# demo-skill\\n\\nsynthesis edit\\n" > skills/demo-skill/SKILL.md\n'
                'echo "APPLIED: skills/demo-skill/SKILL.md"\n',
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            remaining_ids = [e.entry_id for e in proposals.parse_ledger(ledger_path(root))]
            self.assertNotIn(target.entry_id, remaining_ids)
            rulings = read_rulings(root)
            self.assertIn(f"`id:{target.entry_id}`", rulings)

    def test_rulings_record_is_created_when_missing(self):
        # It is gitignored, so a fresh clone has no record: the first ruling
        # must scaffold it rather than fail.
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            self.assertFalse(rulings_path(root).exists())
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "declined")
            proc = self._apply(root, 'echo "APPLIED: nothing"\n')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rulings = read_rulings(root)
            self.assertIn("| Date | Skill | Proposal | Ruling |", rulings)
            self.assertIn(f"`id:{entries[0].entry_id}`", rulings)

    def test_declined_entry_records_without_dispatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "declined — still needed")
            marker = root / "dispatch-was-called"
            proc = self._apply(root, f'touch "{marker}"\necho "APPLIED: nothing"\n')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse(marker.exists())
            rulings = read_rulings(root)
            self.assertIn("**Declined.** still needed", rulings)
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 1)

    def test_any_lint_error_blocks_every_action(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "approved")
            set_ruling(root, entries[1].entry_id, "aproved")
            marker = root / "dispatch-was-called"
            proc = self._apply(root, f'touch "{marker}"\necho "APPLIED: x"\n')
            self.assertEqual(proc.returncode, 1)
            self.assertIn("nothing was applied", proc.stderr)
            self.assertFalse(marker.exists())
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 2)

    def test_out_of_scope_edit_fails_verification_and_keeps_entry(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "approved")
            proc = self._apply(
                root,
                'echo contaminated >> skills/other-skill/SKILL.md\necho "APPLIED: skills/other-skill/SKILL.md"\n',
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("out-of-scope", proc.stderr)
            self.assertIn("skills/other-skill/SKILL.md", proc.stderr)
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 2)

    def test_no_diff_without_blocked_marker_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "approved")
            proc = self._apply(root, 'echo "APPLIED: nothing really"\n')
            self.assertEqual(proc.returncode, 1)
            self.assertIn("changed nothing", proc.stderr)
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 2)

    def test_apply_blocked_marker_is_reported_and_entry_kept(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            set_ruling(root, entries[0].entry_id, "approved")
            proc = self._apply(root, 'echo "APPLY-BLOCKED: target already gone"\n')
            self.assertEqual(proc.returncode, 1)
            self.assertIn("APPLY-BLOCKED: target already gone", proc.stderr)
            self.assertEqual(len(proposals.parse_ledger(ledger_path(root))), 2)

    def test_writer_prompt_carries_proposal_and_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._recorded_root(d)
            entries = proposals.parse_ledger(ledger_path(root))
            target = entries[0]
            set_ruling(root, target.entry_id, "approved")
            captured = root.parent / "captured-prompt.txt"
            stub = root / "stub-writer.sh"
            stub.write_text(
                "#!/usr/bin/env bash\nset -eu\n"
                f'cat >"{captured}"\n'
                "rm skills/demo-skill/references/extra.md\n"
                'echo "APPLIED: skills/demo-skill/references/extra.md"\n',
                encoding="utf-8",
            )
            stub.chmod(0o755)
            proc = _run_cli(["--repo-root", str(root), "apply", "--dispatch-cmd", str(stub), "--no-audit"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            prompt = captured.read_text(encoding="utf-8")
            self.assertIn(target.text, prompt)
            self.assertIn("skills/demo-skill", prompt)
            self.assertNotIn("PROPOSAL_TEXT", prompt)
            self.assertNotIn("SKILL_DIRECTORY", prompt)


class DefaultDispatchTest(unittest.TestCase):
    def test_default_dispatch_argv_carries_the_bootstrap_exemption(self):
        argv = proposals.default_dispatch_argv(AUDITING_DIR / "run_parallel_skill_reviews.sh")
        self.assertEqual(argv[0], "claude")
        self.assertIn("--append-system-prompt", argv)
        self.assertIn(proposals.DISPATCH_BOOTSTRAP_EXEMPTION, argv)


class LedgerRoundTripTest(unittest.TestCase):
    def test_fenced_text_containing_backtick_fences_survives(self):
        entry = proposals.Entry(
            "a" * 12, "demo-skill", "2026-08-17", "pending", "", "before\n```\nfenced\n```\nafter"
        )
        entry.checksum = proposals.text_checksum(entry.text)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "PROPOSALS.md"
            proposals.write_ledger(path, [entry])
            parsed = proposals.parse_ledger(path)
            self.assertEqual(parsed[0].text, entry.text)

    def test_damaged_ledger_is_a_parse_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "PROPOSALS.md"
            path.write_text("## proposal zzz — broken\n", encoding="utf-8")
            with self.assertRaises(proposals.LedgerError):
                proposals.parse_ledger(path)


if __name__ == "__main__":
    unittest.main()
