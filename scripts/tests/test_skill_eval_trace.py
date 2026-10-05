from __future__ import annotations

import sys
import unittest
from pathlib import Path

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from skill_eval.trace import parse_trace  # noqa: E402

_FIXTURES_DIR = _AUDITING_DIR / "skill_eval" / "fixtures" / "trace"

KNOWN = {"pr-description"}


class ClaudeActivationTests(unittest.TestCase):
    """Fixtures captured live: `claude --model haiku ... --allowedTools
    Read,Glob,Grep,Bash,Skill` against a home with only pr-description
    installed. See the T1 deliverable for the exact commands."""

    def test_skill_tool_call_is_attributed_to_the_installed_skill(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-activate.jsonl", "claude", KNOWN)
        self.assertTrue(rec.ok)
        self.assertEqual(rec.activated, ["pr-description"])
        self.assertEqual(rec.first_activated, "pr-description")
        self.assertEqual(rec.activation_signals["pr-description"], "skill_tool")

    def test_init_event_skills_list_becomes_visible_skills(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-activate.jsonl", "claude", KNOWN)
        self.assertIsInstance(rec.visible_skills, list)
        self.assertIn("pr-description", rec.visible_skills)
        # The real init event also listed vendor built-ins alongside the one
        # installed skill (DESIGN.md T-A: "20 alongside one installed
        # skill"); visible_skills must carry all of them, not just ours.
        self.assertGreater(len(rec.visible_skills), 1)

    def test_result_event_supplies_cost_and_final_text(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-activate.jsonl", "claude", KNOWN)
        self.assertIsNotNone(rec.cost_usd)
        self.assertGreater(rec.cost_usd, 0)
        self.assertIn("Branch:", rec.text)

    def test_non_activating_prompt_yields_no_activation(self):
        """The parser can fail to find an activation: this trace never calls
        the Skill tool, so it must report none, not a false positive."""
        rec = parse_trace(_FIXTURES_DIR / "claude-no-activate.jsonl", "claude", KNOWN)
        self.assertTrue(rec.ok)
        self.assertEqual(rec.activated, [])
        self.assertIsNone(rec.first_activated)
        self.assertEqual(rec.tool_calls, 0)


class CodexActivationTests(unittest.TestCase):
    """Fixtures captured live: `codex exec -m gpt-5.6-luna -c
    model_reasoning_effort=low -c service_tier=default -s
    danger-full-access` against a home with only pr-description installed."""

    def test_command_read_of_skill_md_is_attributed(self):
        rec = parse_trace(_FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN)
        self.assertTrue(rec.ok)
        self.assertIn("pr-description", rec.activated)
        self.assertEqual(rec.activation_signals["pr-description"], "command_read")
        self.assertTrue(any(p.endswith("pr-description/SKILL.md") for p in rec.files_read))

    def test_codex_reports_tokens_not_cost(self):
        rec = parse_trace(_FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN)
        self.assertIsNone(rec.cost_usd)
        self.assertIsInstance(rec.tokens, dict)
        self.assertIsNotNone(rec.tokens.get("input"))

    def test_codex_visible_skills_is_not_reported(self):
        rec = parse_trace(_FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN)
        self.assertIsNone(rec.visible_skills)

    def test_non_activating_prompt_yields_no_activation(self):
        rec = parse_trace(_FIXTURES_DIR / "codex-no-activate.jsonl", "codex", KNOWN)
        self.assertTrue(rec.ok)
        self.assertEqual(rec.activated, [])
        self.assertEqual(rec.files_read, [])


class FailureModeTests(unittest.TestCase):
    """Never score a failed arm as a clean non-activation (the defect named
    in DESIGN.md: the prior harness scored a 73-byte auth error as clean)."""

    def test_claude_auth_error_is_not_ok(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-auth-error.synthetic.jsonl", "claude", KNOWN)
        self.assertFalse(rec.ok)
        self.assertTrue(rec.error)
        self.assertEqual(rec.activated, [])

    def test_codex_auth_error_is_not_ok(self):
        rec = parse_trace(_FIXTURES_DIR / "codex-auth-error.synthetic.jsonl", "codex", KNOWN)
        self.assertFalse(rec.ok)
        self.assertTrue(rec.error)

    def test_claude_trace_missing_a_result_event_is_not_ok(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-no-result.synthetic.jsonl", "claude", KNOWN)
        self.assertFalse(rec.ok)
        self.assertIn("no result event", rec.error)

    def test_codex_trace_missing_a_completion_event_is_not_ok(self):
        rec = parse_trace(_FIXTURES_DIR / "codex-no-result.synthetic.jsonl", "codex", KNOWN)
        self.assertFalse(rec.ok)

    def test_codex_agent_message_without_turn_completed_is_not_ok(self):
        """R1 finding I4, verified live with [turn.started, agent_message]:
        a codex run that produced an agent_message but never reached
        turn.completed was previously scored `ok=True`. turn.completed is
        now required regardless of whether an agent_message exists."""
        rec = parse_trace(
            _FIXTURES_DIR / "codex-agent-message-no-turn-completed.synthetic.jsonl",
            "codex", KNOWN,
        )
        self.assertFalse(rec.ok)
        self.assertIn("turn.completed", rec.error)

    def test_parse_trace_exit_code_nonzero_marks_not_ok(self):
        """R1 finding I4: an optional `exit_code` lets a caller fold the CLI
        process's own exit status into the record, independent of what the
        event stream claims."""
        rec = parse_trace(
            _FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN, exit_code=1,
        )
        self.assertFalse(rec.ok)

    def test_parse_trace_exit_code_negative_marks_not_ok(self):
        rec = parse_trace(
            _FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN, exit_code=-1,
        )
        self.assertFalse(rec.ok)

    def test_parse_trace_exit_code_zero_does_not_override_ok(self):
        rec = parse_trace(
            _FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN, exit_code=0,
        )
        self.assertTrue(rec.ok)


class StructuredOutputTests(unittest.TestCase):
    """R2 finding (Critical): with `--json-schema`, claude answers through a
    `StructuredOutput` tool_use, so counting it as a real tool call voided
    every judge/generator verdict live (record.tool_calls == 0 is the T-B
    gate both check). Fixture captured live: `complete("claude", ...,
    json_schema=...)` against a judge-style pairwise prompt."""

    def test_structured_output_tool_use_is_not_counted_as_a_tool_call(self):
        rec = parse_trace(
            _FIXTURES_DIR / "claude-structured-output.jsonl", "claude", KNOWN,
        )
        self.assertTrue(rec.ok)
        self.assertEqual(rec.tool_calls, 0)

    def test_final_text_comes_from_structured_output_and_is_valid_json(self):
        import json as _json
        rec = parse_trace(
            _FIXTURES_DIR / "claude-structured-output.jsonl", "claude", KNOWN,
        )
        parsed = _json.loads(rec.text)
        self.assertEqual(parsed["winner"], "1")
        self.assertIn("reason", parsed)

    def test_structured_output_is_not_reported_as_activation(self):
        rec = parse_trace(
            _FIXTURES_DIR / "claude-structured-output.jsonl", "claude", KNOWN,
        )
        self.assertEqual(rec.activated, [])


class ClaudeBashReadVerbTests(unittest.TestCase):
    """R2 finding (Minor): a claude `Bash ls .../SKILL.md` used to count as a
    read regardless of verb; the same read-verb rule codex already had must
    apply to claude's Bash tool too."""

    def _claude_bash_trace(self, tmp_path, command):
        import json
        lines = [
            json.dumps({"type": "system", "subtype": "init", "skills": ["pr-description"]}),
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": command}},
            ]}}),
            json.dumps({"type": "result", "is_error": False, "result": "done",
                        "total_cost_usd": 0.01}),
        ]
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_non_reading_bash_command_naming_the_path_does_not_activate(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_bash_trace(Path(tmp), "ls skills/pr-description/SKILL.md")
            rec = parse_trace(path, "claude", KNOWN)
            self.assertEqual(rec.activated, [])

    def test_read_verb_bash_command_still_activates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_bash_trace(Path(tmp), "cat skills/pr-description/SKILL.md")
            rec = parse_trace(path, "claude", KNOWN)
            self.assertEqual(rec.activated, ["pr-description"])
            self.assertEqual(rec.activation_signals["pr-description"], "file_read")

    def test_read_verb_elsewhere_in_pipeline_does_not_activate(self):
        """The path is `grep`'s argument, not `head`'s: a read verb present
        ANYWHERE in the command line must not be enough (the old
        `_READ_VERB_RE.search(cmd)` behaviour)."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_bash_trace(
                Path(tmp), "grep -l TODO skills/pr-description/SKILL.md | head",
            )
            rec = parse_trace(path, "claude", KNOWN)
            self.assertEqual(rec.activated, [])

    def test_codex_read_verb_elsewhere_in_pipeline_does_not_activate(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            lines = [
                json.dumps({"type": "thread.started", "thread_id": "t"}),
                json.dumps({"type": "turn.started"}),
                json.dumps({"type": "item.completed", "item": {
                    "id": "item_0", "type": "command_execution",
                    "command": "grep -l TODO skills/pr-description/SKILL.md | head",
                    "status": "completed", "exit_code": 0,
                }}),
                json.dumps({"type": "item.completed", "item": {
                    "id": "final", "type": "agent_message", "text": "done"}}),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
            ]
            path = Path(tmp) / "trace.jsonl"
            path.write_text("\n".join(lines), encoding="utf-8")
            rec = parse_trace(path, "codex", KNOWN)
            self.assertEqual(rec.activated, [])

    def test_codex_bash_dash_lc_wrapper_is_unwrapped_for_the_read_verb_check(self):
        """codex wraps its shell commands as `/bin/bash -lc "<script>"`
        (fixtures/trace/codex-activate.jsonl); the read-verb segmentation
        must see through that one layer, not treat `/bin/bash` itself as the
        (non-reading) command."""
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmd = '/bin/bash -lc "sed -n \'1,10p\' skills/pr-description/SKILL.md"'
            lines = [
                json.dumps({"type": "thread.started", "thread_id": "t"}),
                json.dumps({"type": "turn.started"}),
                json.dumps({"type": "item.completed", "item": {
                    "id": "item_0", "type": "command_execution", "command": cmd,
                    "status": "completed", "exit_code": 0,
                }}),
                json.dumps({"type": "item.completed", "item": {
                    "id": "final", "type": "agent_message", "text": "done"}}),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
            ]
            path = Path(tmp) / "trace.jsonl"
            path.write_text("\n".join(lines), encoding="utf-8")
            rec = parse_trace(path, "codex", KNOWN)
            self.assertEqual(rec.activated, ["pr-description"])


class OutsideReadsTests(unittest.TestCase):
    """R2 finding (Important): a shell-capable arm can still read an
    absolute path outside its own home and cwd (no OS sandbox in this
    container). `parse_trace(..., roots=...)` must surface that."""

    def _claude_cat_trace(self, tmp_path, command):
        import json
        lines = [
            json.dumps({"type": "system", "subtype": "init", "skills": []}),
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": command}},
            ]}}),
            json.dumps({"type": "result", "is_error": False, "result": "done",
                        "total_cost_usd": 0.01}),
        ]
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_read_of_a_path_outside_every_root_is_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            path = self._claude_cat_trace(tmp_path, "cat /workspace/skills/x/SKILL.md")
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertIn("/workspace/skills/x/SKILL.md", rec.outside_reads)

    def test_read_of_a_path_under_the_cwd_root_is_not_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            in_cwd = cwd / "notes.txt"
            path = self._claude_cat_trace(tmp_path, f"cat {in_cwd}")
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertEqual(rec.outside_reads, [])

    def test_roots_none_leaves_outside_reads_empty(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            path = self._claude_cat_trace(tmp_path, "cat /workspace/skills/x/SKILL.md")
            rec = parse_trace(path, "claude", [])
            self.assertEqual(rec.outside_reads, [])

    def test_allowlisted_system_paths_are_not_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            path = self._claude_cat_trace(tmp_path, "cat /etc/os-release")
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertEqual(rec.outside_reads, [])

    def test_outside_reads_are_deduplicated_in_order(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            lines = [
                json.dumps({"type": "system", "subtype": "init", "skills": []}),
                json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Bash",
                     "input": {"command": "cat /workspace/a.txt"}},
                ]}}),
                json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Read",
                     "input": {"file_path": "/workspace/b.txt"}},
                ]}}),
                json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Bash",
                     "input": {"command": "cat /workspace/a.txt"}},
                ]}}),
                json.dumps({"type": "result", "is_error": False, "result": "done",
                            "total_cost_usd": 0.01}),
            ]
            path = tmp_path / "trace.jsonl"
            path.write_text("\n".join(lines), encoding="utf-8")
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertEqual(rec.outside_reads, ["/workspace/a.txt", "/workspace/b.txt"])

    def test_codex_command_execution_path_outside_roots_is_recorded(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            lines = [
                json.dumps({"type": "thread.started", "thread_id": "t"}),
                json.dumps({"type": "turn.started"}),
                json.dumps({"type": "item.completed", "item": {
                    "id": "item_0", "type": "command_execution",
                    "command": "cat /workspace/CLAUDE.md",
                    "status": "completed", "exit_code": 0,
                }}),
                json.dumps({"type": "item.completed", "item": {
                    "id": "final", "type": "agent_message", "text": "done"}}),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
            ]
            path = tmp_path / "trace.jsonl"
            path.write_text("\n".join(lines), encoding="utf-8")
            rec = parse_trace(path, "codex", [], roots=[home, cwd])
            self.assertIn("/workspace/CLAUDE.md", rec.outside_reads)

    def test_tilde_path_is_expanded_against_the_first_root_as_home(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            (home / "skills").mkdir()
            path = self._claude_cat_trace(tmp_path, "cat ~/skills/pr-description/SKILL.md")
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertEqual(rec.outside_reads, [])  # expands to under `home`

    def test_tilde_path_with_no_known_home_is_flagged_as_is(self):
        """`roots=[]` (given, but empty) means there is no root this module
        can treat as HOME, so a `~` token is recorded literally rather than
        guessed at."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            path = self._claude_cat_trace(tmp_path, "cat ~/.ssh/id_rsa")
            rec = parse_trace(path, "claude", [], roots=[])
            self.assertIn("~/.ssh/id_rsa", rec.outside_reads)


class AuthRegexScopeTests(unittest.TestCase):
    """R1 finding I5: the auth/quota regex must not scan every run's final
    text unconditionally -- a legitimate long answer that merely mentions
    "401 Unauthorized" must not be misclassified. I16: a mutation that
    disables `_AUTH_ERROR_RE` entirely must break at least one test; these
    fixtures fail ONLY through the regex path (short reply, zero tool
    calls, is_error not set)."""

    def test_short_tool_free_reply_matching_the_regex_is_marked_not_ok(self):
        rec = parse_trace(
            _FIXTURES_DIR / "claude-auth-text-only-via-regex.synthetic.jsonl",
            "claude", KNOWN,
        )
        self.assertFalse(rec.ok)
        self.assertIn("rate limit", rec.error.lower())

    def test_long_reply_that_merely_mentions_401_is_not_marked_failed(self):
        rec = parse_trace(
            _FIXTURES_DIR / "claude-long-reply-mentions-401.synthetic.jsonl",
            "claude", KNOWN,
        )
        self.assertTrue(rec.ok)
        self.assertEqual(rec.error, "")


class MultiSkillAndNamespaceTests(unittest.TestCase):
    """Synthetic: the prior harness detected only one hardcoded skill name
    and never stripped a plugin namespace prefix. These are regression tests
    for both defects, built from event shapes observed in the real fixtures
    above (not invented wholesale)."""

    def _claude_trace(self, tmp_path, tool_calls):
        import json
        lines = [json.dumps({"type": "system", "subtype": "init", "skills": ["a", "b"]})]
        for name, inp in tool_calls:
            lines.append(json.dumps({
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]},
            }))
        lines.append(json.dumps({"type": "result", "is_error": False, "result": "done",
                                  "total_cost_usd": 0.01}))
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_multiple_skills_are_all_attributed_in_order(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_trace(Path(tmp), [
                ("Skill", {"skill": "a"}),
                ("Skill", {"skill": "b"}),
            ])
            rec = parse_trace(path, "claude", {"a", "b"})
            self.assertEqual(rec.activated, ["a", "b"])

    def test_namespaced_skill_is_never_credited_to_a_bare_known_name(self):
        """R1 finding C3: the earlier version of this function stripped any
        `prefix:` before matching, so `anthropic-skills:foo` with
        known={"foo"} silently credited an organisation-provisioned skill to
        the library skill of the same bare name (verified live). A
        namespaced name is matched against known_skills in full; when it is
        not literally there, it is reported as `builtin:<full name>`, prefix
        included, never stripped down to the bare name."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_trace(
                Path(tmp), [("Skill", {"skill": "anthropic-skills:foo"})],
            )
            rec = parse_trace(path, "claude", {"foo"})
            self.assertEqual(rec.activated, ["builtin:anthropic-skills:foo"])
            self.assertNotIn("foo", rec.activated)

    def test_namespaced_skill_matches_only_when_the_full_name_is_known(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_trace(
                Path(tmp), [("Skill", {"skill": "anthropic-skills:foo"})],
            )
            rec = parse_trace(path, "claude", {"anthropic-skills:foo"})
            self.assertEqual(rec.activated, ["anthropic-skills:foo"])

    def test_skill_not_in_known_skills_is_labelled_builtin(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_trace(Path(tmp), [("Skill", {"skill": "code-review"})])
            rec = parse_trace(path, "claude", {"pr-description"})
            self.assertEqual(rec.activated, ["builtin:code-review"])

    def test_claude_read_tool_use_naming_a_skill_md_is_file_read_activation(self):
        """R1 finding I16: removing claude Read/Bash file_read detection
        entirely broke no existing test. This exercises that path directly:
        a Read tool_use naming `skills/<name>/SKILL.md` must activate via
        the `file_read` signal, not just the `Skill` tool."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._claude_trace(Path(tmp), [
                ("Read", {"file_path": "/tmp/homes/arm/skills/pr-description/SKILL.md"}),
            ])
            rec = parse_trace(path, "claude", {"pr-description"})
            self.assertEqual(rec.activated, ["pr-description"])
            self.assertEqual(rec.activation_signals["pr-description"], "file_read")
            self.assertIn("skills/pr-description/SKILL.md", rec.files_read)


class ToolCallCountingTests(unittest.TestCase):
    """R1 finding I6: tool_calls must count every tool-use-shaped block
    (claude: anything whose type ends in `tool_use`, including
    `server_tool_use`; codex: every item.completed that is not
    agent_message/reasoning), not just the ones this module knows how to
    inspect for activation."""

    def test_claude_server_tool_use_block_is_counted(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            lines = [
                json.dumps({"type": "system", "subtype": "init", "skills": []}),
                json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "server_tool_use", "name": "web_search", "input": {}},
                ]}}),
                json.dumps({"type": "result", "is_error": False, "result": "done",
                            "total_cost_usd": 0.01}),
            ]
            path = Path(tmp) / "trace.jsonl"
            path.write_text("\n".join(lines), encoding="utf-8")
            rec = parse_trace(path, "claude", [])
            self.assertEqual(rec.tool_calls, 1)

    def test_codex_non_command_item_is_counted(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            lines = [
                json.dumps({"type": "thread.started", "thread_id": "t"}),
                json.dumps({"type": "turn.started"}),
                json.dumps({"type": "item.completed",
                            "item": {"id": "item_0", "type": "file_change"}}),
                json.dumps({"type": "item.completed",
                            "item": {"id": "item_1", "type": "reasoning", "text": "..."}}),
                json.dumps({"type": "item.completed",
                            "item": {"id": "item_2", "type": "agent_message", "text": "ok"}}),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
            ]
            path = Path(tmp) / "trace.jsonl"
            path.write_text("\n".join(lines), encoding="utf-8")
            rec = parse_trace(path, "codex", [])
            # file_change counts; reasoning and agent_message do not.
            self.assertEqual(rec.tool_calls, 1)


class CodexReadLikeCommandTests(unittest.TestCase):
    """R1 finding I7, all verified live before this fix:
    - `grep -l x skills/*/SKILL.md` gave `builtin:*` (a glob character read
      as a skill name).
    - `ls skills/foo/SKILL.md skills/bar/SKILL.md` activated both (a
      non-reading command naming the path).
    - a command with status `failed` still counted as activation.
    - a codex built-in under `skills/.system/<name>/SKILL.md` was never
      detected/labelled.
    """

    def _codex_trace(self, tmp_path, commands):
        import json
        lines = [
            json.dumps({"type": "thread.started", "thread_id": "t"}),
            json.dumps({"type": "turn.started"}),
        ]
        for i, (status, exit_code, cmd) in enumerate(commands):
            lines.append(json.dumps({"type": "item.completed", "item": {
                "id": f"item_{i}", "type": "command_execution", "command": cmd,
                "status": status, "exit_code": exit_code,
            }}))
        lines.append(json.dumps({"type": "item.completed", "item": {
            "id": "final", "type": "agent_message", "text": "done"}}))
        lines.append(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}))
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_glob_character_in_command_is_not_read_as_a_skill_name(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._codex_trace(Path(tmp), [
                ("completed", 0, "grep -l x skills/*/SKILL.md"),
            ])
            rec = parse_trace(path, "codex", {"pr-description"})
            self.assertEqual(rec.activated, [])

    def test_non_reading_command_naming_the_path_does_not_activate(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._codex_trace(Path(tmp), [
                ("completed", 0, "ls skills/foo/SKILL.md skills/bar/SKILL.md"),
            ])
            rec = parse_trace(path, "codex", {"foo", "bar"})
            self.assertEqual(rec.activated, [])

    def test_failed_command_does_not_activate(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._codex_trace(Path(tmp), [
                ("failed", 1, "cat skills/pr-description/SKILL.md"),
            ])
            rec = parse_trace(path, "codex", {"pr-description"})
            self.assertEqual(rec.activated, [])

    def test_read_like_command_still_activates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._codex_trace(Path(tmp), [
                ("completed", 0, "sed -n '1,10p' skills/pr-description/SKILL.md"),
            ])
            rec = parse_trace(path, "codex", {"pr-description"})
            self.assertEqual(rec.activated, ["pr-description"])
            self.assertEqual(rec.activation_signals["pr-description"], "command_read")

    def test_system_segment_is_labelled_builtin_regardless_of_known_skills(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = self._codex_trace(Path(tmp), [
                ("completed", 0, "cat skills/.system/skill-creator/SKILL.md"),
            ])
            rec = parse_trace(path, "codex", {"skill-creator"})
            self.assertEqual(rec.activated, ["builtin:skill-creator"])


class VisibleToolsTests(unittest.TestCase):
    """R3 finding I1 (blocker): `TraceRecord.visible_tools` was declared but
    never populated, so `activation.py`'s tools-mismatch contamination check
    always compared against `None`. Driven off the real fixture, not a
    hand-built record, since that fixture's init event is what a live
    `claude --tools ... --allowedTools ...` capture actually produced."""

    def test_init_event_tools_list_becomes_visible_tools(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-activate.jsonl", "claude", KNOWN)
        self.assertIsInstance(rec.visible_tools, list)
        for name in ("Read", "Glob", "Grep", "Bash", "Skill"):
            self.assertIn(name, rec.visible_tools)

    def test_codex_visible_tools_is_not_reported(self):
        """Codex has no init event carrying a tools list, the same way it
        has no visible_skills."""
        rec = parse_trace(_FIXTURES_DIR / "codex-activate.jsonl", "codex", KNOWN)
        self.assertIsNone(rec.visible_tools)

    def test_no_init_event_leaves_visible_tools_none(self):
        rec = parse_trace(_FIXTURES_DIR / "claude-no-result.synthetic.jsonl", "claude", KNOWN)
        self.assertIsNone(rec.visible_tools)


class OutsideReadShellUnwrapTests(unittest.TestCase):
    """R3 finding C1 (blocker): codex commands arrive wrapped as `/bin/bash
    -lc "<script>"`; the old outside-read collector ran a single
    `shlex.split` over the WHOLE wrapped string, so `/bin/bash`, `-lc`, and
    the entire quoted script were one opaque token and neither inner `cat`
    target was ever recorded (outside_reads == [] for a command that in fact
    read both the repo's CLAUDE.md and a credentials file)."""

    def _codex_command_trace(self, tmp_path, command):
        import json
        lines = [
            json.dumps({"type": "thread.started", "thread_id": "t"}),
            json.dumps({"type": "turn.started"}),
            json.dumps({"type": "item.completed", "item": {
                "id": "item_0", "type": "command_execution", "command": command,
                "status": "completed", "exit_code": 0,
            }}),
            json.dumps({"type": "item.completed", "item": {
                "id": "final", "type": "agent_message", "text": "done"}}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
        ]
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_both_reads_behind_a_bash_lc_wrapper_are_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            cmd = ('/bin/bash -lc "cat /workspace/CLAUDE.md; '
                   'cat /home/vscode/.claude/.credentials.json"')
            path = self._codex_command_trace(tmp_path, cmd)
            rec = parse_trace(path, "codex", [], roots=[home, cwd])
            self.assertIn("/workspace/CLAUDE.md", rec.outside_reads)
            self.assertIn("/home/vscode/.claude/.credentials.json", rec.outside_reads)

    def test_unwrapped_form_of_the_same_command_is_still_recorded(self):
        """Regression guard: the unwrapped shape must keep working the same
        way it always did -- the fix must not depend on the wrapper being
        present."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            path = self._codex_command_trace(tmp_path, "cat /workspace/CLAUDE.md")
            rec = parse_trace(path, "codex", [], roots=[home, cwd])
            self.assertIn("/workspace/CLAUDE.md", rec.outside_reads)


class OutsideReadRelativeTraversalTests(unittest.TestCase):
    """R3 finding I6: a relative traversal (`cd ../../../../workspace &&
    cat CLAUDE.md`) escaped detection entirely (outside_reads == [])."""

    def _claude_bash_trace(self, tmp_path, command):
        import json
        lines = [
            json.dumps({"type": "system", "subtype": "init", "skills": []}),
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": command}},
            ]}}),
            json.dumps({"type": "result", "is_error": False, "result": "done",
                        "total_cost_usd": 0.01}),
        ]
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _claude_read_trace(self, tmp_path, file_path):
        import json
        lines = [
            json.dumps({"type": "system", "subtype": "init", "skills": []}),
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": file_path}},
            ]}}),
            json.dumps({"type": "result", "is_error": False, "result": "done",
                        "total_cost_usd": 0.01}),
        ]
        path = tmp_path / "trace.jsonl"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_cd_then_relative_cat_traversal_is_recorded(self):
        """The exact example from the finding: `cd` up several levels out of
        the cwd, then `cat` a bare filename. The traversal target itself
        (`../../../../workspace`, a relative path-like token because it
        starts with `.`) must now resolve against the arm cwd and land in
        outside_reads, whereas before the fix this was `[]`."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd" / "arm" / "deep" / "nested"
            home.mkdir()
            cwd.mkdir(parents=True)
            path = self._claude_bash_trace(
                tmp_path, "cd ../../../../workspace && cat CLAUDE.md",
            )
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertNotEqual(rec.outside_reads, [])
            self.assertTrue(any(r.endswith("/workspace") for r in rec.outside_reads))

    def test_relative_read_file_path_resolves_against_cwd(self):
        """A Read tool_use's `file_path` can itself be a relative traversal
        with no `cd` involved at all -- resolved directly against the cwd
        root (roots[1])."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd" / "arm" / "deep" / "nested"
            home.mkdir()
            cwd.mkdir(parents=True)
            path = self._claude_read_trace(
                tmp_path, "../../../../workspace/CLAUDE.md",
            )
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertTrue(any(r.endswith("workspace/CLAUDE.md") for r in rec.outside_reads))

    def test_relative_token_with_no_cwd_root_is_left_unresolved(self):
        """Best-effort limit, documented on `_command_path_candidates`: with
        no cwd root at all (`roots=[]`), a relative token is never guessed
        at and simply is not recorded."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            path = self._claude_bash_trace(
                tmp_path, "cd ../../../../workspace && cat CLAUDE.md",
            )
            rec = parse_trace(path, "claude", [], roots=[])
            self.assertEqual(rec.outside_reads, [])

    def test_relative_path_still_under_cwd_after_cd_is_not_flagged(self):
        """A `cd` into a subdirectory that stays under the cwd root must not
        be reported: the traversal-escape signal is specifically about
        leaving the arm's own roots."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            home = tmp_path / "home"
            cwd = tmp_path / "cwd"
            home.mkdir()
            cwd.mkdir()
            (cwd / "sub").mkdir()
            path = self._claude_bash_trace(tmp_path, "cd sub && cat notes.txt")
            rec = parse_trace(path, "claude", [], roots=[home, cwd])
            self.assertEqual(rec.outside_reads, [])


class RejectedClaudeActivationTests(unittest.TestCase):
    def test_explicit_tool_error_cannot_credit_activation(self):
        import json
        import tempfile
        for name, inp in [("Skill", {"skill": "a"}),
                          ("Read", {"file_path": "/tmp/home/skills/a/SKILL.md"}),
                          ("Bash", {"command": "cat /tmp/home/skills/a/SKILL.md"})]:
            for failed in (False, True):
                with self.subTest(name=name, failed=failed), tempfile.TemporaryDirectory() as directory:
                    events = [
                        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "call-1", "name": name, "input": inp}]}},
                        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "call-1", "is_error": failed, "content": "result"}]}},
                        {"type": "result", "is_error": False, "result": "done"}
                    ]
                    path = Path(directory) / "trace.jsonl"
                    path.write_text("\n".join(json.dumps(ev) for ev in events))
                    record = parse_trace(path, "claude", ["a"])
                    self.assertEqual(record.activated, [] if failed else ["a"])
                    self.assertEqual(record.tool_calls, 1)
                    if failed:
                        self.assertEqual(record.files_read, [])


if __name__ == "__main__":
    unittest.main()
