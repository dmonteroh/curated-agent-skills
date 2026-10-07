"""usage scan over synthetic transcripts in both vendors' saved formats."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "auditing"))
from skill_eval import usage  # noqa: E402


def claude_lines():
    def assistant(*blocks):
        return {"type": "assistant", "cwd": "/repo", "timestamp": "t", "message": {"content": list(blocks)}}

    def result(tid, error=False):
        return {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "is_error": error}]}}

    tool = lambda tid, name, **inp: {"type": "tool_use", "id": tid, "name": name, "input": inp}
    return [
        {"type": "user", "cwd": "/repo", "timestamp": "t0", "message": {"content": "Earlier question."}},
        {"type": "user", "message": {"content": "Add tests for the parser please."}},
        assistant(tool("t1", "Skill", skill="testing")),
        assistant(tool("t2", "Write", file_path="/repo/tests/test_parser.py", content="x")),
        assistant(tool("t3", "Bash", command="python3 -m pytest tests")), result("t3", error=True),
        assistant(tool("t4", "Edit", file_path="/repo/tests/test_parser.py", old_string="a", new_string="b")),
        assistant(tool("t5", "Bash", command="bash /h/skills/testing/scripts/test.sh")), result("t5"),
    ]


def codex_lines():
    exec_call = lambda cid, cmd: {"type": "response_item", "payload": {
        "type": "custom_tool_call", "name": "exec", "call_id": cid,
        "input": 'const r = await tools.exec_command(' + json.dumps({"cmd": cmd}) + ');'}}
    output = lambda cid, code: {"type": "response_item", "payload": {
        "type": "custom_tool_call_output", "call_id": cid,
        "output": [{"type": "input_text", "text": "Script completed"},
                   {"type": "input_text", "text": json.dumps({"exit_code": code})}]}}
    return [
        {"type": "session_meta", "payload": {"cwd": "/proj", "timestamp": "t0"}},
        {"type": "response_item", "payload": {"type": "message", "role": "user",
                                              "content": [{"type": "input_text", "text": "Write tests for slug.py"}]}},
        exec_call("c1", "sed -n '1,200p' /h/.codex/skills/testing/SKILL.md"), output("c1", 0),
        exec_call("c2", "python3 -m unittest discover"), output("c2", 1),
        {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "call_id": "c3",
                                              "input": 'const patch = "*** Begin Patch\\n*** Update File: tests/test_slug.py\\n@@";'}},
        exec_call("c4", "ls"),
    ]


class UsageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "claude/proj").mkdir(parents=True)
        (self.root / "codex/2026").mkdir(parents=True)
        (self.root / "claude/proj/s1.jsonl").write_text("".join(json.dumps(e) + "\n" for e in claude_lines()))
        (self.root / "claude/proj/s2.jsonl").write_text(json.dumps(
            {"type": "user", "message": {"content": "Unrelated."}}) + "\n")
        (self.root / "codex/2026/r1.jsonl").write_text("".join(json.dumps(e) + "\n" for e in codex_lines()))

    def scan(self):
        return usage.scan("testing", [self.root / "claude"], [self.root / "codex"],
                          path_pattern=r"test", command_pattern=r"pytest|unittest")

    def test_claude_session_after_load(self):
        claude = next(s for s in self.scan() if s["vendor"] == "claude" and s["loaded"])
        self.assertEqual(claude["load_signal"], "skill_tool")
        self.assertEqual(claude["request"], "Add tests for the parser please.")
        self.assertEqual(claude["requests_before_load"], 2)
        self.assertEqual(claude["files_edited"], ["/repo/tests/test_parser.py"])
        self.assertEqual((claude["commands"], claude["failed_commands"], claude["commands_with_outcome"]), (2, 1, 2))
        self.assertEqual(claude["skill_script_runs"], 1)
        self.assertEqual(claude["matched_commands_failed"], 1)
        self.assertEqual(claude["matched_edit_after_failed_command"], 1)
        self.assertEqual(claude["cwd"], "/repo")

    def test_codex_session_with_embedded_commands_patches_and_unknown_outcomes(self):
        codex = next(s for s in self.scan() if s["vendor"] == "codex")
        self.assertTrue(codex["loaded"])
        self.assertEqual(codex["load_signal"], "command_read")
        self.assertEqual(codex["request"], "Write tests for slug.py")
        self.assertEqual(codex["files_edited"], ["tests/test_slug.py"])
        self.assertEqual(codex["commands"], 3)
        self.assertEqual((codex["failed_commands"], codex["commands_with_outcome"]), (1, 2))
        self.assertEqual(codex["matched_edit_after_failed_command"], 1)
        self.assertEqual(codex["cwd"], "/proj")

    def test_sessions_without_a_load_are_counted_not_reported(self):
        sessions = self.scan()
        self.assertEqual(sum(1 for s in sessions if s["vendor"] == "claude"), 2)
        out = self.root / "report"
        usage.write_report("testing", sessions, out, {"path": "test", "command": "pytest"})
        self.assertEqual(len((out / "sessions.jsonl").read_text().splitlines()), 2)
        notes = (out / "usage-notes.txt").read_text()
        self.assertIn("Add tests for the parser please.", notes)
        self.assertNotIn("Unrelated.", notes)
        summary = (out / "summary.md").read_text()
        self.assertIn("| claude | 2 | 1 |", summary)

    def test_a_read_of_another_skill_is_not_a_load(self):
        lines = codex_lines()
        lines[2] = {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "call_id": "c1",
                    "input": 'tools.exec_command({"cmd": "cat /h/skills/testing-extra/SKILL.md"})'}}
        (self.root / "codex/2026/r1.jsonl").write_text("".join(json.dumps(e) + "\n" for e in lines))
        codex = next(s for s in self.scan() if s["vendor"] == "codex")
        self.assertFalse(codex["loaded"])


if __name__ == "__main__":
    unittest.main()
