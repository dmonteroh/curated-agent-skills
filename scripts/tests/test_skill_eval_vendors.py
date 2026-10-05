from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from skill_eval import vendors  # noqa: E402
from skill_eval.common import Finding  # noqa: E402

_FIXTURE_SKILL = _AUDITING_DIR.parent.parent / "skills" / "pr-description"


class BuildHomeTests(unittest.TestCase):
    """No subprocess, no network: build_home only ever copies files."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        # build_home refuses any home outside SCRATCH_ROOT. Every home these
        # tests build lives under self.tmp_path; patch the module's guard
        # rail to match, so build_home's isolation check accepts them.
        self._scratch_patch = mock.patch.object(vendors, "SCRATCH_ROOT", self.tmp_path)
        self._scratch_patch.start()
        self.addCleanup(self._scratch_patch.stop)
        # Fake credential sources so the test never touches a real home.
        fake_home = self.tmp_path / "fakehome"
        (fake_home / ".claude").mkdir(parents=True)
        (fake_home / ".claude" / ".credentials.json").write_text('{"token": "fake"}')
        (fake_home / ".codex").mkdir(parents=True)
        (fake_home / ".codex" / "auth.json").write_text('{"token": "fake"}')
        self._home_patch = mock.patch.object(Path, "home", return_value=fake_home)
        self._home_patch.start()
        self.addCleanup(self._home_patch.stop)

    def test_claude_home_gets_only_credentials_file(self):
        home = self.tmp_path / "arm"
        vendors.build_home("claude", home, {})
        self.assertTrue((home / ".credentials.json").exists())
        self.assertFalse((home / "config.toml").exists())
        self.assertFalse((home / "auth.json").exists())

    def test_codex_home_gets_auth_and_generated_config(self):
        home = self.tmp_path / "arm"
        vendors.build_home("codex", home, {})
        self.assertTrue((home / "auth.json").exists())
        config_text = (home / "config.toml").read_text()
        self.assertIn('personality = "pragmatic"', config_text)
        self.assertIn('service_tier = "default"', config_text)
        self.assertNotIn("mcp_servers", config_text)
        self.assertIn("trust_level", config_text)

    def test_codex_config_trusts_only_the_scratch_root(self):
        fixture_root = self.tmp_path / "skill-eval-fixture-root"
        home = fixture_root / "arm"
        with mock.patch.object(vendors, "SCRATCH_ROOT", fixture_root):
            vendors.build_home("codex", home, {})
            config_text = (home / "config.toml").read_text()
        self.assertIn(str(fixture_root), config_text)
        # Never the real project list the actual ~/.codex/config.toml in
        # this container carries (confirmed by inspection: /workspace,
        # /home/vscode, several /tmp/ca-eval/* paths).
        self.assertNotIn("/workspace", config_text)

    def test_build_home_refuses_a_path_outside_scratch_root(self):
        """R2 finding (Important): build_home used to wipe whatever path it
        was given -- `env check --home ~/.claude` would have deleted the
        operator's real Claude home. build_home must refuse (ValueError) any
        home that does not resolve under SCRATCH_ROOT."""
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        home = outside / "not-under-scratch-root"
        with self.assertRaises(ValueError):
            vendors.build_home("claude", home, {})
        self.assertFalse(home.exists())

    def test_cleanup_home_refuses_a_path_outside_scratch_root(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        marker = outside / "do-not-delete-me"
        marker.mkdir()
        with self.assertRaises(ValueError):
            vendors.cleanup_home(outside)
        self.assertTrue(marker.exists())

    def test_skills_are_copied_with_description_overrides_applied(self):
        home = self.tmp_path / "arm"
        manifest = vendors.build_home(
            "claude", home, {"pr-description": _FIXTURE_SKILL},
            description_overrides={"pr-description": "a totally different description"},
        )
        installed = home / "skills" / "pr-description" / "SKILL.md"
        self.assertTrue(installed.exists())
        self.assertIn("a totally different description", installed.read_text())
        self.assertIn("pr-description", manifest["skills"])
        self.assertEqual(len(manifest["skills"]["pr-description"]), 64)  # sha256 hex

    def test_build_home_wipes_prior_contents(self):
        home = self.tmp_path / "arm"
        home.mkdir()
        stale = home / "stale-file.txt"
        stale.write_text("leftover from a previous run")
        vendors.build_home("claude", home, {})
        self.assertFalse(stale.exists())

    def test_unknown_vendor_is_rejected(self):
        with self.assertRaises(ValueError):
            vendors.build_home("gpt", self.tmp_path / "arm", {})

    def test_home_directory_is_created_0700(self):
        """R1 minor finding: credential copies sat under SCRATCH_ROOT/homes
        in 0755 dirs before this fix."""
        home = self.tmp_path / "arm"
        vendors.build_home("claude", home, {})
        self.assertEqual(stat.S_IMODE(home.stat().st_mode), 0o700)

    def test_cleanup_home_removes_the_tree(self):
        home = self.tmp_path / "arm"
        vendors.build_home("claude", home, {})
        self.assertTrue(home.exists())
        vendors.cleanup_home(home)
        self.assertFalse(home.exists())

    def test_cleanup_home_on_a_missing_home_is_not_an_error(self):
        vendors.cleanup_home(self.tmp_path / "never-existed")  # must not raise


class VerifyEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        # cwd-outside-scratch-root (R1 finding I2) would otherwise fire on
        # every cwd these tests build, since tempfile.TemporaryDirectory()
        # lands under the system tmp dir, not under SCRATCH_ROOT.
        self._scratch_patch = mock.patch.object(vendors, "SCRATCH_ROOT", self.tmp_path)
        self._scratch_patch.start()
        self.addCleanup(self._scratch_patch.stop)

    def _bare_home(self, vendor="claude", skill_names=()):
        home = self.tmp_path / "home"
        home.mkdir()
        if skill_names:
            skills_dir = home / "skills"
            skills_dir.mkdir()
            for name in skill_names:
                (skills_dir / name).mkdir()
                (skills_dir / name / "SKILL.md").write_text("---\nname: x\ndescription: x\n---\n")
        return home

    def test_clean_home_and_cwd_produce_no_findings(self):
        home = self._bare_home(skill_names=["pr-description"])
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, {"pr-description"})
        self.assertEqual(findings, [])

    def test_cwd_inside_repo_root_is_an_error(self):
        home = self._bare_home()
        findings = vendors.verify_environment("claude", home, vendors.REPO_ROOT, set())
        codes = {f.code for f in findings}
        self.assertIn("cwd-inside-repo", codes)
        self.assertTrue(all(f.severity == "error" for f in findings if f.code == "cwd-inside-repo"))

    def test_lowercase_instruction_file_in_an_ancestor_is_caught(self):
        """Case-insensitive, and walked up through every ancestor, not just
        the cwd itself."""
        home = self._bare_home()
        ancestor = self.tmp_path / "project"
        cwd = ancestor / "nested" / "deeper"
        cwd.mkdir(parents=True)
        (ancestor / "claude.md").write_text("be helpful")  # lowercase, two levels up
        findings = vendors.verify_environment("claude", home, cwd, set())
        matches = [f for f in findings if f.code == "instruction-file-in-cwd"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].severity, "error")
        self.assertTrue(matches[0].path.endswith("claude.md"))

    def test_instruction_file_directly_in_cwd_is_caught(self):
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        (cwd / "AGENTS.md").write_text("rules")
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("instruction-file-in-cwd", codes)

    def test_home_skill_mismatch_is_an_error(self):
        home = self._bare_home(skill_names=["pr-description"])
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, {"writing-style"})
        codes = {f.code for f in findings}
        self.assertIn("home-skills-mismatch", codes)

    def test_codex_config_declaring_mcp_servers_is_an_error(self):
        home = self._bare_home(vendor="codex")
        (home / "config.toml").write_text('[mcp_servers.laya-mcp]\nurl = "https://x"\n')
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("codex", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("codex-config-declares-mcp-servers", codes)

    def test_claude_settings_with_hooks_is_an_error(self):
        home = self._bare_home()
        (home / "settings.json").write_text(json.dumps({"hooks": {"PreToolUse": []}}))
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("claude-settings-has-hooks", codes)

    def test_memory_store_in_home_is_an_error(self):
        home = self._bare_home(vendor="codex")
        (home / "memories").mkdir()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("codex", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("memory-store-in-home", codes)

    def test_cwd_outside_scratch_root_is_an_error(self):
        """R1 finding I2: codex's generated config.toml trusts only
        SCRATCH_ROOT, so a cwd outside it is unusable, not merely unwise."""
        home = self._bare_home()
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        findings = vendors.verify_environment("claude", home, outside, set())
        codes = {f.code for f in findings}
        self.assertIn("cwd-outside-scratch-root", codes)

    def test_claude_local_md_is_caught(self):
        """R1 finding I2: CLAUDE.local.md was missing from the original
        instruction-filename list."""
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        (cwd / "CLAUDE.local.md").write_text("local overrides")
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("instruction-file-in-cwd", codes)

    def test_dot_claude_dir_in_an_ancestor_is_caught(self):
        home = self._bare_home()
        ancestor = self.tmp_path / "project"
        cwd = ancestor / "nested"
        cwd.mkdir(parents=True)
        (ancestor / ".claude").mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("config-dir-in-cwd", codes)

    def test_dot_codex_dir_in_cwd_is_caught(self):
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        (cwd / ".codex").mkdir()
        findings = vendors.verify_environment("codex", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("config-dir-in-cwd", codes)

    def test_dot_agents_dir_in_cwd_is_caught(self):
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        (cwd / ".agents").mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("config-dir-in-cwd", codes)

    def test_mcp_json_in_cwd_is_caught(self):
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        (cwd / ".mcp.json").write_text("{}")
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("config-file-in-cwd", codes)

    def test_claude_md_inside_home_is_caught(self):
        home = self._bare_home()
        (home / "CLAUDE.md").write_text("be helpful")
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("instruction-file-in-home", codes)

    def test_agents_md_inside_home_is_caught(self):
        home = self._bare_home()
        (home / "AGENTS.md").write_text("be helpful")
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("instruction-file-in-home", codes)

    def test_instruction_file_nested_below_cwd_is_caught(self):
        """R3 finding: `prepare_workspace`'s directory-source `kind` copies
        arbitrary fixture trees into cwd, which can nest content below the
        top level; verify_environment must not stop at the immediate cwd
        listing."""
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        nested = cwd / "src" / "deep"
        nested.mkdir(parents=True)
        (nested / "AGENTS.md").write_text("rules")
        findings = vendors.verify_environment("claude", home, cwd, set())
        matches = [f for f in findings if f.code == "instruction-file-in-cwd"]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0].path.endswith("AGENTS.md"))

    def test_config_dir_nested_below_cwd_is_caught_case_insensitively(self):
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        nested = cwd / "src"
        nested.mkdir(parents=True)
        (nested / ".Claude").mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("config-dir-in-cwd", codes)

    def test_mcp_json_nested_below_cwd_is_caught(self):
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        nested = cwd / "pkg"
        nested.mkdir(parents=True)
        (nested / ".mcp.json").write_text("{}")
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("config-file-in-cwd", codes)

    def test_git_internals_below_cwd_are_never_descended_into(self):
        """A real git fixture's `.git/` tree is full of files that are not
        evaluation-relevant; the below-cwd scan must skip it entirely, not
        just avoid matching a name inside it by chance."""
        home = self._bare_home()
        cwd = self.tmp_path / "cwd"
        git_hooks = cwd / ".git" / "hooks"
        git_hooks.mkdir(parents=True)
        (git_hooks / "AGENTS.md").write_text("not a real instruction file")
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertNotIn("instruction-file-in-cwd", codes)

    def test_plugins_dir_in_home_is_caught(self):
        home = self._bare_home()
        (home / "plugins").mkdir()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("plugins-dir-in-home", codes)

    def test_claude_json_with_mcp_servers_in_home_is_caught(self):
        home = self._bare_home()
        (home / ".claude.json").write_text(json.dumps({"mcpServers": {"laya-mcp": {}}}))
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("claude-json-declares-mcp-servers", codes)

    def test_any_settings_json_in_home_is_flagged_even_without_hooks(self):
        """R1 finding I2: build_home never writes settings.json at all, so
        presence of one with an unrecognised key (enabledPlugins here, not
        hooks) must still be flagged, without needing a hardcoded key list."""
        home = self._bare_home()
        (home / "settings.json").write_text(json.dumps({"enabledPlugins": ["agents-md@builtin"]}))
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("claude", home, cwd, set())
        codes = {f.code for f in findings}
        self.assertIn("claude-settings-json-in-home", codes)

    def test_claude_memory_markers_are_each_individually_caught(self):
        """R1 finding I2 mutation evidence: emptying the claude memory-marker
        tuple must break a test. Each of the three markers is checked on its
        own, not just the codex ones."""
        for marker in ("memory", "projects", "session-env"):
            with self.subTest(marker=marker):
                home = self._bare_home()
                (home / marker).mkdir()
                cwd = self.tmp_path / "cwd"
                cwd.mkdir()
                findings = vendors.verify_environment("claude", home, cwd, set())
                codes = {f.code for f in findings}
                self.assertIn("memory-store-in-home", codes)
                shutil.rmtree(self.tmp_path)
                self.tmp_path.mkdir()

    def test_dot_system_is_ignored_and_reported_as_info(self):
        """R1 minor finding: a reused home a codex run already touched seeds
        skills/.system on its own; that must read as info, not an error, and
        must not be compared against expected_skills."""
        home = self._bare_home(vendor="codex", skill_names=["pr-description", ".system"])
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        findings = vendors.verify_environment("codex", home, cwd, {"pr-description"})
        by_code = {f.code: f for f in findings}
        self.assertIn("codex-system-skills-present", by_code)
        self.assertEqual(by_code["codex-system-skills-present"].severity, "info")
        self.assertNotIn("home-skills-mismatch", by_code)

    def test_builtin_collision_falls_back_to_known_builtins_with_no_cache(self):
        """R1 finding I16: with no cached builtin_baseline() at all, `env
        check --skills code-review` previously passed clean even though
        code-review is a real claude built-in (verified live)."""
        home = self._bare_home(skill_names=["code-review"])
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        with mock.patch.object(vendors, "RUNS_DIR", self.tmp_path / "runs-with-no-cache"):
            findings = vendors.verify_environment("claude", home, cwd, {"code-review"})
        matches = [f for f in findings if f.code == "expected-skill-collides-with-builtin"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].path, "code-review")

    def test_builtin_collision_is_a_warning_not_an_error(self):
        home = self._bare_home(skill_names=["code-review"])
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        with mock.patch.object(vendors, "RUNS_DIR", self.tmp_path / "runs"):
            builtins_dir = self.tmp_path / "runs" / "builtins"
            builtins_dir.mkdir(parents=True)
            (builtins_dir / "claude-sonnet.json").write_text(
                json.dumps({"skills": ["code-review", "verify"]})
            )
            findings = vendors.verify_environment("claude", home, cwd, {"code-review"})
        matches = [f for f in findings if f.code == "expected-skill-collides-with-builtin"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].severity, "warn")


class ExecAgentArgvTests(unittest.TestCase):
    """exec_agent must never shell out through a string, and must never put
    a credential in the returned cmd. Verified by intercepting
    subprocess.run rather than running a real CLI."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

    def test_claude_argv_is_a_list_and_prompt_goes_on_stdin(self):
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            captured["kwargs"] = kwargs
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent(
                "claude", home, cwd, "top secret prompt text", trace_out, tools="activation",
            )
        self.assertIsInstance(captured["argv"], list)
        self.assertTrue(all(isinstance(a, str) for a in captured["argv"]))
        self.assertEqual(captured["kwargs"].get("input"), "top secret prompt text")
        self.assertNotIn("top secret prompt text", captured["argv"])
        self.assertNotIn("top secret prompt text", json.dumps(result["cmd"]))
        self.assertIn("Skill", " ".join(result["cmd"]))

    def test_claude_tools_none_uses_empty_tools_flag(self):
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            vendors.exec_agent("claude", home, cwd, "hi", trace_out, tools="none")
        self.assertIn("--tools", captured["argv"])
        idx = captured["argv"].index("--tools")
        self.assertEqual(captured["argv"][idx + 1], "")

    def test_codex_prompt_goes_on_stdin_via_dash_argument(self):
        """`-` tells codex to read the prompt from stdin (codex exec --help);
        subprocess.run(..., input=prompt) writes it and closes stdin. No
        wrapper sentence, no prompt file, and the prompt text itself never
        appears in argv -- only in the `input` kwarg."""
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            captured["kwargs"] = kwargs
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            vendors.exec_agent(
                "codex", home, cwd, "a very secret codex prompt", trace_out, tools="activation",
            )
        self.assertIn("-", captured["argv"])
        self.assertEqual(captured["argv"][-1], "-")
        self.assertEqual(captured["kwargs"].get("input"), "a very secret codex prompt")
        self.assertNotIn("a very secret codex prompt", json.dumps(captured["argv"]))
        self.assertFalse((cwd / ".skill-eval-prompt.txt").exists())
        self.assertEqual(list(cwd.iterdir()), [])

    def test_credentials_are_never_in_the_returned_cmd(self):
        """R2 finding (Minor): the original version of this test only
        checked for the credential file's CONTENT string in `cmd`, never for
        its PATH -- a mutation that appended `home / ".credentials.json"`
        (the path, not its content) to `cmd` would have passed unnoticed.
        Strengthened to check both. Demonstrated by mutation: temporarily
        adding `argv.append(str(home / ".credentials.json"))` to
        `exec_agent` (never committed) makes this fail, both before and
        after this change."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        home.mkdir()
        cred_path = home / ".credentials.json"
        cred_path.write_text('{"secret": "do-not-leak-me"}')
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent("claude", home, cwd, "hi", trace_out)
        cmd_json = json.dumps(result["cmd"])
        self.assertNotIn("do-not-leak-me", cmd_json)
        self.assertNotIn(str(cred_path), cmd_json)
        self.assertNotIn(".credentials.json", cmd_json)

    def test_claude_activation_uses_a_whitelist_not_a_denylist(self):
        """R2 finding (Important): a denylist fails open -- `claude --help`
        prints no warning for an unknown `--disallowedTools` name, and a live
        probe (R2 probe/listagents) showed ListAgents/SendMessage still
        reachable under the old denylist. The fix is `--tools
        CLAUDE_ARM_TOOLS` together with the same `--allowedTools` value, and
        `--disallowedTools` must not appear at all."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent("claude", home, cwd, "hi", trace_out, tools="activation")
        self.assertNotIn("--disallowedTools", result["cmd"])
        self.assertIn("--tools", result["cmd"])
        tools_idx = result["cmd"].index("--tools")
        self.assertEqual(result["cmd"][tools_idx + 1], vendors.CLAUDE_ARM_TOOLS)
        self.assertIn("--allowedTools", result["cmd"])
        allowed_idx = result["cmd"].index("--allowedTools")
        self.assertEqual(result["cmd"][allowed_idx + 1], vendors.CLAUDE_ARM_TOOLS)

    def test_claude_always_gets_strict_mcp_config(self):
        """R1 finding C2: --strict-mcp-config must be present for every
        claude call, both tools="activation" and tools="none"."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            r1 = vendors.exec_agent("claude", home, cwd, "hi", trace_out / "a", tools="activation")
            r2 = vendors.exec_agent("claude", home, cwd, "hi", trace_out / "b", tools="none")
        self.assertIn("--strict-mcp-config", r1["cmd"])
        self.assertIn("--strict-mcp-config", r2["cmd"])

    def test_claude_always_gets_the_sync_guard_settings(self):
        """R2 finding (Critical): --strict-mcp-config alone does not stop the
        claude.ai org-skill sync (measured: 3 of 6 control runs still wrote
        skills/synced/ mid-run). --settings CLAUDE_SYNC_GUARD must be present
        for every claude call, both tools="activation" and tools="none"."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            r1 = vendors.exec_agent("claude", home, cwd, "hi", trace_out / "a", tools="activation")
            r2 = vendors.exec_agent("claude", home, cwd, "hi", trace_out / "b", tools="none")
        for result in (r1, r2):
            self.assertIn("--settings", result["cmd"])
            idx = result["cmd"].index("--settings")
            self.assertEqual(result["cmd"][idx + 1], vendors.CLAUDE_SYNC_GUARD)

    def test_claude_tools_none_also_disables_slash_commands(self):
        """R1 finding C2: tools="none" (judges/generators) must additionally
        pass --disable-slash-commands, which `claude --help` documents as
        "Disable all skills"."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            r_none = vendors.exec_agent("claude", home, cwd, "hi", trace_out / "a", tools="none")
            r_activation = vendors.exec_agent(
                "claude", home, cwd, "hi", trace_out / "b", tools="activation",
            )
        self.assertIn("--disable-slash-commands", r_none["cmd"])
        self.assertNotIn("--disable-slash-commands", r_activation["cmd"])

    def test_codex_tools_none_uses_read_only_sandbox(self):
        """R1 finding I1: tools="none" (the only caller is complete(), for
        judges/generators) must run codex under -s read-only, not the
        danger-full-access every activation arm gets."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            r_none = vendors.exec_agent("codex", home, cwd, "hi", trace_out / "a", tools="none")
            r_activation = vendors.exec_agent(
                "codex", home, cwd, "hi", trace_out / "b", tools="activation",
            )
        idx_none = r_none["cmd"].index("-s")
        idx_act = r_activation["cmd"].index("-s")
        self.assertEqual(r_none["cmd"][idx_none + 1], "read-only")
        self.assertEqual(r_activation["cmd"][idx_act + 1], "danger-full-access")

    def test_claude_sync_guard_settings_are_exactly_false_for_both_keys(self):
        """R3 mutation survivor: a mutant that flips `syncClaudeAiSkills` to
        `True` kept `test_claude_always_gets_the_sync_guard_settings` green,
        because that test compares the emitted --settings value against the
        very same `vendors.CLAUDE_SYNC_GUARD` constant the mutation also
        edits, so both sides moved together. Assert the parsed JSON values
        directly against literal booleans instead."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent("claude", home, cwd, "hi", trace_out, tools="activation")
        idx = result["cmd"].index("--settings")
        settings = json.loads(result["cmd"][idx + 1])
        self.assertIs(settings["syncClaudeAiSkills"], False)
        self.assertIs(settings["syncClaudeAiPlugins"], False)

    def test_claude_tool_whitelist_is_exactly_these_five_names(self):
        """R3 mutation survivor: a mutant that appends `SendMessage` to
        `CLAUDE_ARM_TOOLS` kept `test_claude_activation_uses_a_whitelist_not_a_denylist`
        green for the same reason as the sync-guard mutant above -- the old
        test compared against the same constant the mutation edits. Assert
        the literal whitelist."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent("claude", home, cwd, "hi", trace_out, tools="activation")
        idx = result["cmd"].index("--tools")
        names = result["cmd"][idx + 1].split(",")
        self.assertEqual(names, ["Read", "Glob", "Grep", "Bash", "Skill"])
        allowed_idx = result["cmd"].index("--allowedTools")
        self.assertEqual(result["cmd"][allowed_idx + 1].split(","), names)

    def test_exec_agent_rejects_an_invalid_claude_effort(self):
        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with self.assertRaises(ValueError):
            vendors.exec_agent("claude", home, cwd, "hi", trace_out, effort="ultra")

    def test_exec_agent_rejects_an_invalid_codex_effort(self):
        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with self.assertRaises(ValueError):
            vendors.exec_agent("codex", home, cwd, "hi", trace_out, effort="ultra")

    def test_exec_agent_accepts_codex_only_effort_values(self):
        """codex accepts `none`/`minimal`, which claude's own --help does not
        list; the two vendors must not share one effort set."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            for effort in ("none", "minimal"):
                with self.subTest(effort=effort):
                    vendors.exec_agent("codex", home, cwd, "hi", trace_out, effort=effort)
        with self.assertRaises(ValueError):
            vendors.exec_agent("claude", home, cwd, "hi", trace_out, effort="none")

    def test_exec_agent_claude_effort_reaches_argv(self):
        """O2: --effort <level> must reach the claude argv exactly."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent("claude", home, cwd, "hi", trace_out, effort="low")
        idx = result["cmd"].index("--effort")
        self.assertEqual(result["cmd"][idx + 1], "low")

    def test_exec_agent_codex_effort_reaches_argv(self):
        """O2: `-c model_reasoning_effort=<level>` must reach the codex argv
        exactly."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            result = vendors.exec_agent("codex", home, cwd, "hi", trace_out, effort="low")
        self.assertIn("model_reasoning_effort=low", result["cmd"])

    def test_env_is_built_from_the_allowlist_not_os_environ_copy(self):
        """R1 finding C1: an arm must not inherit the orchestrator's own
        environment. Verified against a pollutant set modelled on the exact
        variables the finding named as having leaked."""
        pollutants = {
            "CLAUDE_CODE_MESSAGING_TOKEN": "secret-token",
            "CLAUDE_CODE_MESSAGING_SOCKET": "/tmp/some.sock",
            "CLAUDE_CODE_SESSION_ID": "orchestrator-session",
            "CLAUDE_CODE_CHILD_SESSION": "1",
            "CLAUDECODE": "1",
            "CLAUDE_EFFORT": "high",
            "ANTHROPIC_API_KEY": "sk-do-not-leak",
            "OPENAI_API_KEY": "sk-also-do-not-leak",
            "MCP_SOME_SERVER_URL": "https://example.invalid",
            "CODEX_HOME": "/home/vscode/.codex",
            "HOME": "/home/vscode",
        }

        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        home = self.tmp_path / "home"
        cwd = self.tmp_path / "cwd"
        trace_out = self.tmp_path / "trace.jsonl"
        with mock.patch.dict(os.environ, pollutants, clear=False), \
                mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run) as run_mock:
            vendors.exec_agent("claude", home, cwd, "hi", trace_out, tools="activation")
        seen_env = run_mock.call_args.kwargs["env"]
        for key in pollutants:
            if key == "HOME":
                self.assertEqual(seen_env["HOME"], str(home))  # overridden, not inherited
                continue
            self.assertNotIn(key, seen_env, f"{key} leaked into the arm environment")
        self.assertEqual(seen_env.get("CLAUDE_CONFIG_DIR"), str(home))


class EnvAllowlistTests(unittest.TestCase):
    """`verify_arm_env` (R1 finding C1) is a pure function over a dict, with
    no vendor, home, or subprocess involved."""

    def test_clean_env_from_build_env_produces_no_findings(self):
        home = Path("/tmp/skill-eval-fixture-home")
        env = vendors._build_env("claude", home)
        self.assertEqual(vendors.verify_arm_env(env), [])

    def test_leaked_messaging_and_session_vars_are_errors(self):
        env = {
            "PATH": "/usr/bin", "HOME": "/tmp/arm",
            "CLAUDE_CONFIG_DIR": "/tmp/arm",
            "CLAUDE_CODE_MESSAGING_TOKEN": "leaked",
            "CLAUDE_CODE_SESSION_ID": "leaked",
            "ANTHROPIC_API_KEY": "leaked",
            "MCP_FOO": "leaked",
        }
        findings = vendors.verify_arm_env(env)
        codes_and_paths = {(f.code, f.path) for f in findings}
        self.assertIn(("leaked-orchestrator-env-var", "CLAUDE_CODE_MESSAGING_TOKEN"), codes_and_paths)
        self.assertIn(("leaked-orchestrator-env-var", "CLAUDE_CODE_SESSION_ID"), codes_and_paths)
        self.assertIn(("leaked-orchestrator-env-var", "ANTHROPIC_API_KEY"), codes_and_paths)
        self.assertIn(("leaked-orchestrator-env-var", "MCP_FOO"), codes_and_paths)
        self.assertTrue(all(f.severity == "error" for f in findings))

    def test_vars_set_on_purpose_are_not_flagged(self):
        env = {"PATH": "/usr/bin", "HOME": "/tmp/arm",
               "CLAUDE_CONFIG_DIR": "/tmp/arm", "CODEX_HOME": "/tmp/arm"}
        self.assertEqual(vendors.verify_arm_env(env), [])

    def test_exec_agent_refuses_to_run_with_a_leaked_env(self):
        """Belt-and-suspenders: even if `_build_argv` regressed, exec_agent
        itself must refuse rather than spawn a polluted arm."""
        def fake_run(argv, **kwargs):
            return mock.Mock(returncode=0)

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        home = Path(tmp.name) / "home"
        cwd = Path(tmp.name) / "cwd"
        trace_out = Path(tmp.name) / "trace.jsonl"
        bad_argv = mock.Mock(return_value=(
            ["claude"], {"PATH": "/usr/bin", "ANTHROPIC_API_KEY": "leak"},
        ))
        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run), \
                mock.patch("skill_eval.vendors._build_argv", bad_argv):
            with self.assertRaises(RuntimeError):
                vendors.exec_agent("claude", home, cwd, "hi", trace_out, tools="activation")


class CompleteAndBuiltinBaselineTests(unittest.TestCase):
    """complete() and builtin_baseline() driven entirely through a
    monkeypatched exec_agent; never a real subprocess."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self._scratch_patch = mock.patch.object(vendors, "SCRATCH_ROOT", self.tmp_path / "scratch")
        self._runs_patch = mock.patch.object(vendors, "RUNS_DIR", self.tmp_path / "runs")
        self._scratch_patch.start()
        self._runs_patch.start()
        self.addCleanup(self._scratch_patch.stop)
        self.addCleanup(self._runs_patch.stop)
        fake_home = self.tmp_path / "fakehome"
        (fake_home / ".claude").mkdir(parents=True)
        (fake_home / ".claude" / ".credentials.json").write_text('{}')
        self._home_patch = mock.patch.object(Path, "home", return_value=fake_home)
        self._home_patch.start()
        self.addCleanup(self._home_patch.stop)

    def _write_claude_trace(self, path, text="hello", tool_calls=0):
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [json.dumps({"type": "system", "subtype": "init", "skills": []})]
        for _ in range(tool_calls):
            events.append(json.dumps({
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]},
            }))
        events.append(json.dumps({"type": "result", "is_error": False, "result": text,
                                   "total_cost_usd": 0.001}))
        path.write_text("\n".join(events), encoding="utf-8")

    def test_complete_raises_when_preflight_finds_an_instruction_file(self):
        """I9: `complete()` never called verify_environment at all. Test
        with SCRATCH_ROOT patched under a dir holding a CLAUDE.md, so the
        ancestor scan `verify_environment` already runs must fire and
        `complete()` must abort before ever spawning exec_agent."""
        poisoned_root = self.tmp_path / "poisoned"
        poisoned_root.mkdir()
        (poisoned_root / "CLAUDE.md").write_text("be helpful")
        scratch = poisoned_root / "scratch"
        with mock.patch.object(vendors, "SCRATCH_ROOT", scratch):
            with self.assertRaises(RuntimeError):
                vendors.complete("claude", "hi")

    def test_complete_calls_exec_agent_when_the_environment_is_clean(self):
        """The positive side of the I9 fix: a clean home/cwd must still let
        `complete()` reach exec_agent -- the pre-flight check must not
        become a blanket refusal."""
        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            self._write_claude_trace(Path(trace_out), text="fine")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent):
            text, record = vendors.complete("claude", "hi")
        self.assertEqual(text, "fine")

    def test_complete_passes_effort_through_to_claude_argv(self):
        """O2: stubbed subprocess.run, checking that `--effort low` reaches
        argv through complete()."""
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            return mock.Mock(returncode=0)

        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            vendors.complete("claude", "hi", effort="low")
        self.assertIn("--effort", captured["argv"])
        idx = captured["argv"].index("--effort")
        self.assertEqual(captured["argv"][idx + 1], "low")

    def test_complete_passes_effort_through_to_codex_argv(self):
        """O2: stubbed subprocess.run, checking that
        `model_reasoning_effort=low` reaches argv through complete()."""
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            return mock.Mock(returncode=0)

        with mock.patch("skill_eval.vendors.subprocess.run", side_effect=fake_run):
            vendors.complete("codex", "hi", effort="low")
        self.assertIn("model_reasoning_effort=low", captured["argv"])

    def test_complete_returns_text_and_a_zero_tool_call_record(self):
        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            self._write_claude_trace(Path(trace_out), text="the answer")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent):
            text, record = vendors.complete("claude", "what is 2+2?")
        self.assertEqual(text, "the answer")
        self.assertEqual(record.tool_calls, 0)

    def test_complete_builds_a_bare_home_with_no_skills(self):
        seen_skills = {}

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            seen_skills["skills"] = sorted(p.name for p in (Path(home) / "skills").glob("*")) \
                if (Path(home) / "skills").exists() else []
            self._write_claude_trace(Path(trace_out))
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent):
            vendors.complete("claude", "irrelevant prompt")
        self.assertEqual(seen_skills["skills"], [])

    def test_builtin_baseline_is_cached_after_first_call(self):
        call_count = {"n": 0}

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            path = Path(trace_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            events = [json.dumps({"type": "system", "subtype": "init",
                                   "skills": ["code-review", "verify"]}),
                      json.dumps({"type": "result", "is_error": False, "result": "OK"})]
            path.write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(path),
                    "stderr_path": str(path) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent), \
                mock.patch.object(vendors, "cli_version", return_value="9.9.9"):
            first = vendors.builtin_baseline("claude", model="sonnet")
            second = vendors.builtin_baseline("claude", model="sonnet")
        self.assertEqual(first, ["code-review", "verify"])
        self.assertEqual(second, first)
        self.assertEqual(call_count["n"], 1)  # second call served from cache

    def test_builtin_baseline_cache_key_includes_cli_version(self):
        """R2 finding (Important): the cache key used to ignore the CLI
        version, so a CLI upgrade silently kept serving a stale baseline."""
        cache_dir = vendors.RUNS_DIR / "builtins"

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            path = Path(trace_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            events = [json.dumps({"type": "system", "subtype": "init", "skills": ["verify"]}),
                      json.dumps({"type": "result", "is_error": False, "result": "OK"})]
            path.write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(path),
                    "stderr_path": str(path) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent), \
                mock.patch.object(vendors, "cli_version", return_value="2.1.280"):
            vendors.builtin_baseline("claude", model="sonnet")
        self.assertTrue((cache_dir / "claude-sonnet-2.1.280.json").exists())

    def test_builtin_baseline_does_not_cache_a_probe_with_no_init_event(self):
        """R2 finding (Important): a probe that never produced an init event
        (auth failure, crash before the init event, or any other reason
        `visible_skills` stayed None) must not be cached -- caching `[]` from
        a failed probe poisoned every later contamination check with a false
        'nothing is a built-in' baseline. This replaces
        test_builtin_baseline_cache_path, which accepted exactly that."""
        cache_dir = vendors.RUNS_DIR / "builtins"
        call_count = {"n": 0}

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            path = Path(trace_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            # No "system"/"init" event at all: visible_skills stays None.
            path.write_text(json.dumps({"type": "result", "is_error": False, "result": "OK"}),
                             encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(path),
                    "stderr_path": str(path) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent), \
                mock.patch.object(vendors, "cli_version", return_value="9.9.9"):
            first = vendors.builtin_baseline("claude", model="sonnet")
            second = vendors.builtin_baseline("claude", model="sonnet")
        self.assertEqual(first, [])
        self.assertEqual(second, [])
        self.assertFalse((cache_dir / "claude-sonnet-9.9.9.json").exists())
        # Never cached, so every call re-probes.
        self.assertEqual(call_count["n"], 2)

    def test_builtin_baseline_drops_namespaced_names_before_caching(self):
        """R2 finding (Important): a leaked `anthropic-skills:*` name must
        never be cached as an allowed baseline entry."""
        cache_dir = vendors.RUNS_DIR / "builtins"

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            path = Path(trace_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            events = [json.dumps({"type": "system", "subtype": "init",
                                   "skills": ["verify", "anthropic-skills:writing-style"]}),
                      json.dumps({"type": "result", "is_error": False, "result": "OK"})]
            path.write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(path),
                    "stderr_path": str(path) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent), \
                mock.patch.object(vendors, "cli_version", return_value="9.9.9"):
            skills = vendors.builtin_baseline("claude", model="sonnet")
        self.assertEqual(skills, ["verify"])
        cached = json.loads((cache_dir / "claude-sonnet-9.9.9.json").read_text())
        self.assertEqual(cached["skills"], ["verify"])

    def test_builtin_baseline_does_not_cache_a_not_ok_probe(self):
        """R2 finding (Important): an auth/quota failure must not poison the
        cache with `[]`, even when an init event happened to be present."""
        cache_dir = vendors.RUNS_DIR / "builtins"

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            path = Path(trace_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            events = [json.dumps({"type": "system", "subtype": "init", "skills": []}),
                      json.dumps({"type": "result", "is_error": True, "result": "not logged in"})]
            path.write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(path),
                    "stderr_path": str(path) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent), \
                mock.patch.object(vendors, "cli_version", return_value="9.9.9"):
            vendors.builtin_baseline("claude", model="sonnet")
        self.assertFalse((cache_dir / "claude-sonnet-9.9.9.json").exists())

    def test_baseline_cache_path_matches_what_builtin_baseline_writes(self):
        cache_dir = vendors.RUNS_DIR / "builtins"

        def fake_exec_agent(vendor, home, cwd, prompt, trace_out, **kwargs):
            path = Path(trace_out)
            path.parent.mkdir(parents=True, exist_ok=True)
            events = [json.dumps({"type": "system", "subtype": "init", "skills": ["verify"]}),
                      json.dumps({"type": "result", "is_error": False, "result": "OK"})]
            path.write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(path),
                    "stderr_path": str(path) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec_agent), \
                mock.patch.object(vendors, "cli_version", return_value="2.1.280"):
            expected_path = vendors.baseline_cache_path("claude", "sonnet")
            vendors.builtin_baseline("claude", model="sonnet")
        self.assertTrue(expected_path.exists())
        self.assertEqual(expected_path, cache_dir / "claude-sonnet-2.1.280.json")


class BaselineCachePathTests(unittest.TestCase):
    """`baseline_cache_path` is a pure path computation: no filesystem
    access of its own (`cli_version` caches its own subprocess call)."""

    def test_filename_shape_and_default_model(self):
        with mock.patch.object(vendors, "cli_version", return_value="2.1.280"):
            path = vendors.baseline_cache_path("claude", "sonnet")
        self.assertEqual(path.name, "claude-sonnet-2.1.280.json")
        self.assertEqual(path.parent.name, "builtins")

    def test_default_model_is_used_when_none_given(self):
        with mock.patch.object(vendors, "cli_version", return_value="0.156.0"):
            path = vendors.baseline_cache_path("codex")
        expected_model = vendors.DEFAULT_MODELS["codex"]
        self.assertEqual(path.name, f"codex-{expected_model}-0.156.0.json")

    def test_unknown_vendor_is_rejected(self):
        with self.assertRaises(ValueError):
            vendors.baseline_cache_path("gpt")


class PrepareWorkspaceTests(unittest.TestCase):
    """`prepare_workspace` isn't stubbed here: `kind="git"` shells out to a
    real, local `git` binary (no network), and `kind="empty"`/a directory
    source are pure filesystem operations. See DESIGN.md sec 3."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

    def _git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                               text=True, check=True).stdout

    def test_empty_kind_leaves_cwd_empty(self):
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        sha = vendors.prepare_workspace(cwd, "empty")
        self.assertEqual(list(cwd.iterdir()), [])
        self.assertEqual(len(sha), 64)  # sha256 hex, even over an empty tree

    def test_git_kind_builds_main_and_feature_update_branches(self):
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        vendors.prepare_workspace(cwd, "git")
        self.assertTrue((cwd / ".git").is_dir())
        branches = self._git(cwd, "branch", "--format=%(refname:short)").split()
        self.assertIn("main", branches)
        self.assertIn("feature/update", branches)
        current = self._git(cwd, "branch", "--show-current").strip()
        self.assertEqual(current, "feature/update")  # feature/update checked out
        log_main = self._git(cwd, "log", "--oneline", "main").splitlines()
        log_feature = self._git(cwd, "log", "--oneline", "feature/update").splitlines()
        self.assertEqual(len(log_main), 1)      # main: one commit
        self.assertEqual(len(log_feature), 2)   # feature/update: main's commit + one more

    def test_git_kind_carries_no_instruction_or_config_files(self):
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        vendors.prepare_workspace(cwd, "git")
        for p in cwd.rglob("*"):
            if ".git" in p.relative_to(cwd).parts:
                continue
            self.assertNotIn(p.name.lower(), vendors.INSTRUCTION_FILENAMES)
            self.assertNotIn(p.name.lower(), vendors._CONFIG_DIRNAMES_LOWER)
            self.assertNotIn(p.name, vendors._CONFIG_FILENAMES)

    def test_git_kind_uses_the_documented_local_identity(self):
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        vendors.prepare_workspace(cwd, "git")
        log = self._git(cwd, "log", "--all", "--format=%an|%ae")
        lines = [l for l in log.splitlines() if l]
        self.assertEqual(len(lines), 2)
        for line in lines:
            name, email = line.split("|")
            self.assertEqual(name, "Skill Eval")
            self.assertEqual(email, "skill-eval@example.invalid")

    def test_git_kind_commit_dates_are_fixed_and_identical_across_builds(self):
        cwd1 = self.tmp_path / "cwd1"
        cwd1.mkdir()
        cwd2 = self.tmp_path / "cwd2"
        cwd2.mkdir()
        vendors.prepare_workspace(cwd1, "git")
        vendors.prepare_workspace(cwd2, "git")
        dates1 = self._git(cwd1, "log", "--all", "--format=%ad", "--date=iso-strict")
        dates2 = self._git(cwd2, "log", "--all", "--format=%ad", "--date=iso-strict")
        self.assertEqual(dates1, dates2)

    def test_git_kind_passes_verify_environment_on_its_own(self):
        """A `prepare_workspace("git")` cwd must never itself trip the
        instruction-file / tool-config scan `verify_environment` runs."""
        home = self.tmp_path / "home"
        home.mkdir()
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        with mock.patch.object(vendors, "SCRATCH_ROOT", self.tmp_path):
            vendors.prepare_workspace(cwd, "git")
            findings = vendors.verify_environment("claude", home, cwd, set())
        self.assertEqual(findings, [])

    def test_git_kind_fingerprint_is_deterministic_across_independent_builds(self):
        cwd1 = self.tmp_path / "cwd1"
        cwd1.mkdir()
        cwd2 = self.tmp_path / "cwd2"
        cwd2.mkdir()
        sha1 = vendors.prepare_workspace(cwd1, "git")
        sha2 = vendors.prepare_workspace(cwd2, "git")
        self.assertEqual(sha1, sha2)
        self.assertEqual(len(sha1), 64)

    def test_dir_kind_copies_a_clean_fixture_in(self):
        src = self.tmp_path / "fixture"
        (src / "notes").mkdir(parents=True)
        (src / "notes" / "a.txt").write_text("hello")
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        sha = vendors.prepare_workspace(cwd, str(src))
        self.assertEqual((cwd / "notes" / "a.txt").read_text(), "hello")
        self.assertEqual(len(sha), 64)

    def test_dir_kind_refuses_a_source_with_an_instruction_file(self):
        src = self.tmp_path / "fixture"
        src.mkdir()
        (src / "CLAUDE.md").write_text("be helpful")
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        with self.assertRaises(ValueError):
            vendors.prepare_workspace(cwd, str(src))
        self.assertEqual(list(cwd.iterdir()), [])

    def test_dir_kind_refuses_a_source_with_a_nested_config_dir(self):
        src = self.tmp_path / "fixture"
        (src / "nested" / ".claude").mkdir(parents=True)
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        with self.assertRaises(ValueError):
            vendors.prepare_workspace(cwd, str(src))

    def test_dir_kind_refuses_a_source_with_an_mcp_json(self):
        src = self.tmp_path / "fixture"
        src.mkdir()
        (src / ".mcp.json").write_text("{}")
        cwd = self.tmp_path / "cwd"
        cwd.mkdir()
        with self.assertRaises(ValueError):
            vendors.prepare_workspace(cwd, str(src))


if __name__ == "__main__":
    unittest.main()
