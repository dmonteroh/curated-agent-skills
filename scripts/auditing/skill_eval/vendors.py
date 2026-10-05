"""Arm isolation: bare homes, environment checks, and agent execution.

Every claim this module makes about the CLI surface was checked against the
installed binaries in this container (claude 2.1.280, codex-cli 0.156.0), not
assumed from documentation or the prior harness. See the T1 deliverable for
the probed facts; the load-bearing ones are repeated as comments below the
call sites that depend on them.

This guards T-A from DESIGN.md sec 2: every arm, judge, and generator runs in
a home that holds only credentials, a config this package generates, and the
skills the run names, under a cwd outside the repository. It must never
reproduce the prior harness's defects: copying the real `~/.codex/config.toml`
(it carries `[mcp_servers.laya-mcp]` and per-project trust entries into every
arm, confirmed by inspecting the real file in this container), detecting only
one skill, or scoring an auth-error trace as clean (that last one is
`trace.py`'s job; this module never inspects trace *content*).
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterable

from .common import (
    REPO_ROOT,
    RUNS_DIR,
    SCRATCH_ROOT,
    VENDORS,
    Finding,
    replace_description,
    run_id,
    sha256_file,
    skill_dir,
    utc_now,
)
from .common import TraceRecord
from .trace import parse_trace

# claude: probed via `claude --model haiku ...`, DEFAULT_MODELS is a request
# default, not a floor; codex: probed via `codex exec -m gpt-5.6-luna ...`.
DEFAULT_MODELS = {"claude": "sonnet", "codex": "gpt-5.6-terra"}

# Whitelist of claude tools an activation arm gets, used for BOTH --tools and
# --allowedTools (R2 finding: a denylist fails open -- see the comment on
# `_build_argv` below). Measured live on claude 2.1.280: `claude --tools
# CLAUDE_ARM_TOOLS --allowedTools CLAUDE_ARM_TOOLS ...` produced an init event
# whose `tools` list was exactly these five, in this order, for 16 of 16 runs.
CLAUDE_ARM_TOOLS = "Read,Glob,Grep,Bash,Skill"
# Task comparisons permit the normal editing tools in both arms.
CLAUDE_TASK_TOOLS = CLAUDE_ARM_TOOLS + ",Edit,Write,NotebookEdit"

# R3 finding O2 (blocker): `effort` reached `_build_argv` unchecked. Claude:
# `claude --help` documents "--effort <level> ... (low, medium, high, xhigh,
# max)". Codex: `codex exec --help` does not document
# `model_reasoning_effort`'s accepted values at all -- confirmed live by an
# invalid-value probe (`codex exec --json -c model_reasoning_effort=bogus -c
# service_tier=default --skip-git-repo-check -s read-only -`), whose
# `turn.failed` error was: "[ReasoningEffortParam] [reasoning.effort]
# [invalid_enum_value] Invalid value: 'bogus'. Supported values are: 'none',
# 'minimal', 'low', 'medium', 'high', 'xhigh', and 'max'." Codex accepts two
# values ("none", "minimal") claude's own --help does not list, so the two
# vendors get separate sets rather than one shared one.
CLAUDE_EFFORT_VALUES = frozenset({"low", "medium", "high", "xhigh", "max"})
CODEX_EFFORT_VALUES = frozenset({"none", "minimal", "low", "medium", "high", "xhigh", "max"})

# Prevents the claude.ai org-skill/plugin sync from writing into the arm
# home mid-run. Measured on claude 2.1.280: with `--strict-mcp-config` but
# no `--settings` guard, the sync wrote `<config dir>/skills/synced/` and
# `plugins/synced/` in 3 of 6 control runs; adding this setting stopped the
# sync in a separate 16-run probe, 16 of 16, and activation still worked in
# every one. See the comment on `_build_argv` for the full account.
CLAUDE_SYNC_GUARD = json.dumps({"syncClaudeAiSkills": False, "syncClaudeAiPlugins": False})

# Observed, not measured: a static fallback used only when
# `RUNS_DIR/builtins/` has nothing cached yet for a vendor -- otherwise a
# fresh SCRATCH_ROOT gives `env check` a clean pass on a real built-in
# collision. Measured: `env check --skills code-review` with no cache
# present reports no collision at all, although `code-review` is a real
# claude built-in. Labelled with the exact versions observed, and
# superseded once a real `builtin_baseline()` run exists for that
# vendor+model.
KNOWN_BUILTINS = {
    # claude 2.1.280: the init event's `skills` list minus the one installed
    # skill. Re-captured live in R2 (probe/listagents, probe/disallow1,
    # probe/setA*): 18 names, not 20 -- `artifact-diagramming` and
    # `artifact-capabilities` were in the R1 capture but did not appear in
    # any of these R2 runs, so they are dropped rather than carried forward
    # unverified.
    "claude": (
        "deep-research", "design", "design-sync", "dataviz",
        "update-config", "verify", "debug", "code-review", "simplify",
        "batch", "fewer-permission-prompts", "doctor", "loop", "schedule",
        "claude-api", "workflow-authoring", "run", "run-skill-generator",
    ),
    # codex 0.156.0: skills/.system/<name> observed after one trivial run.
    "codex": (
        "imagegen", "openai-docs", "plugin-creator", "review-agent",
        "skill-creator", "skill-installer",
    ),
}

# ---------------------------------------------------------------------------
# Home construction
# ---------------------------------------------------------------------------

# Case-insensitive: `verify_environment` must catch a lowercase `claude.md`
# as readily as the canonical spelling. Kept in one place so `build_home`
# (which never writes any of these into a generated home) and
# `verify_environment` (which searches for them) can't drift apart.
# `claude.local.md` added per R1 finding I2: it loads the same way
# CLAUDE.md/AGENTS.md do and was missing from the original list.
INSTRUCTION_FILENAMES = frozenset(
    {"claude.md", "claude.local.md", "agents.md", "gemini.md", ".cursorrules",
     "copilot-instructions.md"}
)

# Tool-config directories (R1 finding I2): each can carry MCP servers,
# hooks, or trusted-project entries the same way an instruction file carries
# a bootstrap. Checked in the cwd and every ancestor, same as
# INSTRUCTION_FILENAMES, and also inside a generated home (a home is never
# supposed to have a nested project config of its own).
_CONFIG_DIRNAMES = frozenset({".claude", ".agents", ".codex"})
_CONFIG_FILENAMES = frozenset({".mcp.json"})
# R3 finding (~366): the cwd scan compared `entry.name in _CONFIG_DIRNAMES`
# directly, which missed a differently-cased directory (`.Claude`,
# `.CODEX`); INSTRUCTION_FILENAMES was already matched case-insensitively,
# so config dirs get the same treatment. Precomputed once so both the cwd
# scan and `prepare_workspace`'s fixture-source refusal share it.
_CONFIG_DIRNAMES_LOWER = frozenset(d.lower() for d in _CONFIG_DIRNAMES)

# Memory stores carry state from the operator's own sessions (DESIGN.md
# T-A). `build_home` never creates any of these; `verify_environment` treats
# their presence in a generated home as a sign the home was not built by this
# module, or was contaminated after the fact.
_MEMORY_MARKERS = {
    "claude": ("memory", "projects", "session-env"),
    "codex": ("memories", "memories_1.sqlite", "history.jsonl"),
}

# Environment allowlist (R1 finding C1): everything an arm process may
# inherit from the orchestrator's own environment, beyond what this module
# sets on purpose (HOME, CLAUDE_CONFIG_DIR/CODEX_HOME). Probed live: claude
# still authenticates with HOME=<arm home> plus CLAUDE_CONFIG_DIR set, and
# codex with HOME and CODEX_HOME both pointing at the arm home -- neither
# needs anything else from the parent process's environment to run. Without
# this allowlist, `os.environ.copy()` handed every arm the orchestrator's own
# CLAUDE_CODE_MESSAGING_TOKEN/_SOCKET/_SESSION_ID, which is how the first
# fixtures' arms ended up able to call SendMessage/ListAgents against the
# parent session (confirmed: those tools and a messaging_socket_path were in
# the captured init event before this fix).
_ENV_ALLOWLIST_EXACT = frozenset({"PATH", "LANG", "TERM", "TMPDIR"})
_ENV_ALLOWLIST_PREFIXES = ("LC_",)
# Set by `_build_env` itself, never inherited -- `verify_arm_env` allows them.
_ENV_SET_ON_PURPOSE = frozenset({"HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME"})
# Any variable in one of these families that is NOT in _ENV_SET_ON_PURPOSE is
# a leak: an orchestrator/vendor/MCP variable that should never have reached
# an arm (CLAUDE_CODE_*, CLAUDE_EFFORT, CLAUDECODE, ANTHROPIC_*, CODEX_HOME
# under some OTHER value, OPENAI_*, MCP_*, ...).
_LEAK_FAMILY_RE = re.compile(r"^(CLAUDE|ANTHROPIC|CODEX|OPENAI|MCP)")


def _build_env(vendor: str, home: Path) -> dict:
    """Build one arm's process environment from the allowlist above.

    Never `os.environ.copy()`: see the allowlist's comment for what that
    leaked (R1 finding C1).
    """
    env = {
        k: v for k, v in os.environ.items()
        if k in _ENV_ALLOWLIST_EXACT or k.startswith(_ENV_ALLOWLIST_PREFIXES)
    }
    env["HOME"] = str(home)
    if vendor == "claude":
        env["CLAUDE_CONFIG_DIR"] = str(home)
    elif vendor == "codex":
        env["CODEX_HOME"] = str(home)
    return env


def verify_arm_env(env: dict) -> list[Finding]:
    """Pure check over an already-built env dict (R1 finding C1).

    No CLAUDE*/ANTHROPIC*/CODEX*/OPENAI*/MCP* variable may survive except
    the ones this package sets on purpose (`_ENV_SET_ON_PURPOSE`). Takes a
    plain dict, not a vendor or a home, so it can be unit-tested against a
    hand-built env without spawning anything.
    """
    findings: list[Finding] = []
    for key in env:
        if key in _ENV_SET_ON_PURPOSE:
            continue
        if _LEAK_FAMILY_RE.match(key):
            findings.append(Finding(
                "error", "leaked-orchestrator-env-var",
                f"{key} was inherited from the orchestrator's environment; "
                "an arm must only see the allowlisted vars plus HOME/"
                "CLAUDE_CONFIG_DIR/CODEX_HOME", key,
            ))
    return findings


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _codex_config_toml() -> str:
    """A generated config.toml, never a copy of the real one.

    The real `~/.codex/config.toml` in this container carries
    `[mcp_servers.laya-mcp]` and `[projects."/workspace"]` (and half a dozen
    other paths) with `trust_level = "trusted"` -- both handed straight to an
    arm by the prior harness's `vendor_home()`. This one carries neither: no
    `mcp_servers` table at all, and a single trust entry for the root every
    `neutral_cwd()` lives under, so an arm's own working directory is usable
    without dragging in the operator's project list.
    """
    trust_root = _toml_string(str(SCRATCH_ROOT))
    return (
        'personality = "pragmatic"\n'
        'service_tier = "default"\n'
        "\n"
        f"[projects.{trust_root}]\n"
        'trust_level = "trusted"\n'
    )


def _require_under_scratch_root(home: Path, caller: str) -> Path:
    """Refuse any path that does not resolve under SCRATCH_ROOT.

    R2 finding (Important): `build_home` wiped whatever path it was given --
    `env check --home ~/.claude` would have deleted the operator's real
    Claude home. `home` may not exist yet, so this resolves against its
    nearest existing ancestor rather than requiring the path itself to exist.
    """
    home = Path(home)
    resolved = home
    if not resolved.exists():
        # Walk up to the nearest existing ancestor to resolve symlinks in
        # the parts that do exist, without requiring `home` itself to exist.
        existing = resolved
        remainder: list[str] = []
        while not existing.exists() and existing != existing.parent:
            remainder.append(existing.name)
            existing = existing.parent
        resolved = existing.resolve().joinpath(*reversed(remainder))
    else:
        resolved = resolved.resolve()
    try:
        resolved.relative_to(SCRATCH_ROOT.resolve())
    except ValueError:
        raise ValueError(
            f"{caller}: refusing to touch {home} -- it does not resolve under "
            f"SCRATCH_ROOT ({SCRATCH_ROOT}); this guard exists because {caller} "
            "deletes the path it is given"
        )
    return home


def build_home(vendor: str, home: Path, skills: dict[str, Path],
                description_overrides: dict[str, str] | None = None) -> dict:
    """Wipe and rebuild `home` as a bare, single-purpose agent home.

    Copies credentials only (`~/.claude/.credentials.json` or
    `~/.codex/auth.json`), a generated `config.toml` for codex (never a copy
    of the real one -- see `_codex_config_toml`), and the named skills.
    Returns a manifest recording a sha256 of every installed SKILL.md, so a
    caller can prove later which exact skill text an arm ran against.

    Refuses (`ValueError`) any `home` that does not resolve under
    SCRATCH_ROOT -- see `_require_under_scratch_root`.
    """
    if vendor not in VENDORS:
        raise ValueError(f"build_home: unknown vendor {vendor!r}")
    home = _require_under_scratch_root(home, "build_home")
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True)
    # Credential copies must not be group/other-readable (R1 minor finding:
    # observed at 0755 under SCRATCH_ROOT/homes before this fix).
    os.chmod(home, 0o700)

    if vendor == "claude":
        src = Path.home() / ".claude" / ".credentials.json"
        if src.exists():
            dest = home / ".credentials.json"
            shutil.copy2(src, dest)
            os.chmod(dest, 0o600)
    else:  # codex
        src = Path.home() / ".codex" / "auth.json"
        if src.exists():
            dest = home / "auth.json"
            shutil.copy2(src, dest)
            os.chmod(dest, 0o600)
        config_path = home / "config.toml"
        config_path.write_text(_codex_config_toml(), encoding="utf-8")
        os.chmod(config_path, 0o600)

    description_overrides = description_overrides or {}
    manifest_skills: dict[str, str] = {}
    if skills:
        skills_root = home / "skills"
        skills_root.mkdir(parents=True, exist_ok=True)
        for name, src_dir in skills.items():
            dest_dir = skills_root / name
            shutil.copytree(Path(src_dir), dest_dir)
            skill_md = dest_dir / "SKILL.md"
            if name in description_overrides:
                text = skill_md.read_text(encoding="utf-8")
                skill_md.write_text(
                    replace_description(text, description_overrides[name]), encoding="utf-8"
                )
            manifest_skills[name] = sha256_file(skill_md)

    return {
        "vendor": vendor,
        "home": str(home),
        "skills": manifest_skills,
        "created_at": utc_now(),
    }


def neutral_cwd(label: str) -> Path:
    """A fresh, empty working directory under SCRATCH_ROOT, outside the repo."""
    d = SCRATCH_ROOT / "cwd" / run_id(label)
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Workspace fixtures (R3 deliverable)
# ---------------------------------------------------------------------------

# Fixed, arbitrary commit timestamp (R3 spec: "commit dates fixed ... so the
# content is deterministic"). The value itself carries no meaning; only that
# it never changes between builds.
_GIT_FIXTURE_DATE = "2024-01-01T00:00:00+00:00"


def _git_fixture_env() -> dict:
    """Environment for the git calls `prepare_workspace("git", ...)` makes.

    Built from the same allowlist `_build_env` uses (DESIGN.md sec 2 T-A:
    "git runs through argv lists with the allowlisted env"), plus the
    author/committer identity and fixed dates git needs to produce identical
    commits on every build. `HOME` is pointed at SCRATCH_ROOT (never the
    operator's real home) so a stray `~/.gitconfig` can never leak in --
    `GIT_CONFIG_NOSYSTEM` drops the system config the same way.
    """
    env = {
        k: v for k, v in os.environ.items()
        if k in _ENV_ALLOWLIST_EXACT or k.startswith(_ENV_ALLOWLIST_PREFIXES)
    }
    env["HOME"] = str(SCRATCH_ROOT)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_AUTHOR_NAME"] = "Skill Eval"
    env["GIT_AUTHOR_EMAIL"] = "skill-eval@example.invalid"
    env["GIT_COMMITTER_NAME"] = "Skill Eval"
    env["GIT_COMMITTER_EMAIL"] = "skill-eval@example.invalid"
    env["GIT_AUTHOR_DATE"] = _GIT_FIXTURE_DATE
    env["GIT_COMMITTER_DATE"] = _GIT_FIXTURE_DATE
    return env


def _run_git(args: list[str], cwd: Path, env: dict) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), env=env, check=True,
                    capture_output=True, text=True)


def _build_git_fixture(cwd: Path) -> None:
    """A neutral two-branch git repo, built fresh in `cwd` on every call.

    `main`: a README and one commit. `feature/update`, checked out: one
    small code-file commit on top. Local identity only (never global), fixed
    author/committer dates (see `_git_fixture_env`), and -- deliberately --
    no instruction file (CLAUDE.md/AGENTS.md/...) or tool-config file/dir of
    any kind, so a `prepare_workspace("git")` cwd always passes
    `verify_environment`'s scan on its own.
    """
    env = _git_fixture_env()
    _run_git(["init", "-q", "-b", "main"], cwd, env)
    _run_git(["config", "user.name", "Skill Eval"], cwd, env)
    _run_git(["config", "user.email", "skill-eval@example.invalid"], cwd, env)
    (cwd / "README.md").write_text(
        "# sample-project\n\nA small fixture repository used to give an "
        "activation arm something concrete to look at.\n",
        encoding="utf-8",
    )
    _run_git(["add", "README.md"], cwd, env)
    _run_git(["commit", "-q", "-m", "Initial commit", "--no-gpg-sign"], cwd, env)

    _run_git(["checkout", "-q", "-b", "feature/update"], cwd, env)
    src_dir = cwd / "src"
    src_dir.mkdir()
    (src_dir / "util.py").write_text(
        "def add(a, b):\n    return a + b\n", encoding="utf-8",
    )
    _run_git(["add", "src/util.py"], cwd, env)
    _run_git(["commit", "-q", "-m", "Add a small utility function", "--no-gpg-sign"], cwd, env)


def _refuse_instruction_or_config_source(src: Path) -> None:
    """Refuse (ValueError) a `prepare_workspace` directory source that
    carries an instruction file or a tool-config dir/file anywhere under it
    (skipping `.git`), the same class of material `verify_environment`
    refuses in a live cwd."""
    if not src.is_dir():
        raise ValueError(f"prepare_workspace: fixture source {src} is not a directory")
    for p in src.rglob("*"):
        rel_parts = p.relative_to(src).parts
        if rel_parts and rel_parts[0] == ".git":
            continue
        if p.is_file() and p.name.lower() in INSTRUCTION_FILENAMES:
            raise ValueError(
                f"prepare_workspace: refusing fixture source with an instruction file: {p}"
            )
        if p.is_dir() and p.name.lower() in _CONFIG_DIRNAMES_LOWER:
            raise ValueError(
                f"prepare_workspace: refusing fixture source with a tool-config directory: {p}"
            )
        if p.is_file() and p.name in _CONFIG_FILENAMES:
            raise ValueError(
                f"prepare_workspace: refusing fixture source with a tool-config file: {p}"
            )


def _fixture_fingerprint(root: Path) -> str:
    """sha256 over sorted (relative path, content) pairs under `root`,
    excluding `.git` internals -- deterministic regardless of filesystem
    iteration order, so two independently built fixtures with the same
    content hash identically (used to confirm an A/B run shares one
    condition, per DESIGN.md sec 3)."""
    entries: list[tuple[str, bytes]] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(root).parts
        if rel_parts and rel_parts[0] == ".git":
            continue
        entries.append((str(p.relative_to(root)), p.read_bytes()))
    entries.sort(key=lambda e: e[0])
    h = hashlib.sha256()
    for rel, content in entries:
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(content)
        h.update(b"\x00")
    return h.hexdigest()


def prepare_workspace(cwd: Path, kind: str = "git") -> str:
    """Fill a fresh arm cwd before `verify_environment` runs. See DESIGN.md
    sec 3. `kind`: "empty" leaves `cwd` untouched (already fresh from
    `neutral_cwd`); "git" builds `_build_git_fixture`; anything else is
    treated as a source directory whose contents are copied in, after
    `_refuse_instruction_or_config_source` clears it. Returns
    `_fixture_fingerprint(cwd)`.
    """
    cwd = Path(cwd)
    if kind == "empty":
        pass
    elif kind == "git":
        _build_git_fixture(cwd)
    else:
        src = Path(kind)
        _refuse_instruction_or_config_source(src)
        for entry in src.iterdir():
            dest = cwd / entry.name
            if entry.is_dir():
                shutil.copytree(entry, dest)
            else:
                shutil.copy2(entry, dest)
    return _fixture_fingerprint(cwd)


def cleanup_home(home: Path) -> None:
    """Remove an arm home tree, including its credential copy.

    `build_home` already wipes `home` at the start of every call, so this is
    for a caller (`complete()`, `builtin_baseline()`) that wants the
    credential copy gone as soon as the run that needed it is over, rather
    than left under SCRATCH_ROOT/homes until the next build. Best-effort:
    a home that is already gone, or was never created, is not an error.

    Refuses (`ValueError`) any `home` that does not resolve under
    SCRATCH_ROOT -- same guard as `build_home`; see
    `_require_under_scratch_root`.
    """
    home = _require_under_scratch_root(home, "cleanup_home")
    shutil.rmtree(home, ignore_errors=True)


# ---------------------------------------------------------------------------
# Pre-flight isolation checks
# ---------------------------------------------------------------------------


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _scan_instruction_files(cwd: Path) -> list[Finding]:
    """Walk cwd and every ancestor up to `/`, case-insensitively.

    Flags an instruction file (CLAUDE.md and friends) and, per R1 finding
    I2, a tool-config directory or file that can carry the same kind of
    bootstrap: `.claude/`, `.agents/`, `.codex/`, `.mcp.json`.
    """
    findings: list[Finding] = []
    d = cwd.resolve()
    seen: set[Path] = set()
    while d not in seen:
        seen.add(d)
        try:
            entries = list(d.iterdir())
        except OSError:
            entries = []
        for entry in entries:
            lname = entry.name.lower()
            if entry.is_file() and lname in INSTRUCTION_FILENAMES:
                findings.append(Finding(
                    "error", "instruction-file-in-cwd",
                    f"instruction file visible from cwd: {entry}", str(entry),
                ))
            elif entry.is_dir() and lname in _CONFIG_DIRNAMES_LOWER:
                findings.append(Finding(
                    "error", "config-dir-in-cwd",
                    f"tool-config directory visible from cwd: {entry}", str(entry),
                ))
            elif entry.is_file() and entry.name in _CONFIG_FILENAMES:
                findings.append(Finding(
                    "error", "config-file-in-cwd",
                    f"tool-config file visible from cwd: {entry}", str(entry),
                ))
        if d.parent == d:
            break
        d = d.parent
    return findings


def _scan_below_cwd(cwd: Path) -> list[Finding]:
    """Recurse strictly BELOW cwd (skipping `.git`) for the same instruction
    files and tool-config dirs/files `_scan_instruction_files` checks at and
    above cwd (R3 finding: `verify_environment` never looked below cwd at
    all, even though `prepare_workspace`'s directory-source `kind` now
    copies arbitrary fixture trees in, which can nest content below the top
    level). `_CONFIG_DIRNAMES` is matched case-insensitively here too, same
    as `_scan_instruction_files`.
    """
    findings: list[Finding] = []
    root = cwd.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        current = Path(dirpath)
        if current == root:
            continue  # the top level is already covered by _scan_instruction_files
        for name in list(dirnames):
            if name.lower() in _CONFIG_DIRNAMES_LOWER:
                entry = current / name
                findings.append(Finding(
                    "error", "config-dir-in-cwd",
                    f"tool-config directory visible below cwd: {entry}", str(entry),
                ))
                dirnames.remove(name)  # already flagged; no need to descend further
        for name in filenames:
            lname = name.lower()
            entry = current / name
            if lname in INSTRUCTION_FILENAMES:
                findings.append(Finding(
                    "error", "instruction-file-in-cwd",
                    f"instruction file visible below cwd: {entry}", str(entry),
                ))
            elif name in _CONFIG_FILENAMES:
                findings.append(Finding(
                    "error", "config-file-in-cwd",
                    f"tool-config file visible below cwd: {entry}", str(entry),
                ))
    return findings


def _check_cwd_under_scratch_root(cwd: Path) -> list[Finding]:
    """Codex trusts only SCRATCH_ROOT (see `_codex_config_toml`'s single
    trust entry); a cwd outside it would run untrusted, or not at all."""
    if not _is_within(cwd, SCRATCH_ROOT):
        return [Finding(
            "error", "cwd-outside-scratch-root",
            f"cwd {cwd} is not under SCRATCH_ROOT ({SCRATCH_ROOT}); "
            "codex's generated config.toml trusts only SCRATCH_ROOT", str(cwd),
        )]
    return []


def _check_home_skills(home: Path, expected_skills: set[str]) -> list[Finding]:
    skills_root = home / "skills"
    installed = {p.name for p in skills_root.iterdir() if p.is_dir()} if skills_root.exists() else set()
    findings: list[Finding] = []
    # A reused home a codex run has already touched seeds skills/.system on
    # its own (R1 minor finding); that is expected codex behaviour, not
    # contamination, so it is reported as info and excluded from the
    # mismatch comparison rather than failing every reused codex home.
    if ".system" in installed:
        findings.append(Finding(
            "info", "codex-system-skills-present",
            f"codex seeded {skills_root / '.system'}; ignored in the skills comparison",
            str(skills_root / ".system"),
        ))
        installed = installed - {".system"}
    if installed != set(expected_skills):
        findings.append(Finding(
            "error", "home-skills-mismatch",
            f"home skills {sorted(installed)} != expected {sorted(expected_skills)}",
            str(skills_root),
        ))
    return findings


def _check_codex_mcp(vendor: str, home: Path) -> list[Finding]:
    if vendor != "codex":
        return []
    config_path = home / "config.toml"
    if config_path.exists() and "mcp_servers" in config_path.read_text(encoding="utf-8"):
        return [Finding(
            "error", "codex-config-declares-mcp-servers",
            "home config.toml declares mcp_servers; arms must run tool-free", str(config_path),
        )]
    return []


def _check_claude_settings(vendor: str, home: Path) -> list[Finding]:
    """`build_home` never writes a claude `settings.json` (R1 finding I2), so
    any presence at all -- hooks or not -- means the home was not built
    cleanly. Presence is flagged unconditionally rather than against a fixed
    list of key names (`enabledPlugins`, `env`, `apiKeyHelper`, ...) drawn
    from memory; `hooks` gets its own, more specific finding because it is
    the one key this module previously checked for by name."""
    if vendor != "claude":
        return []
    settings_path = home / "settings.json"
    if not settings_path.exists():
        return []
    findings = [Finding(
        "error", "claude-settings-json-in-home",
        "home settings.json exists but build_home never writes one; a clean "
        "home carries no hooks, enabledPlugins, env, apiKeyHelper, or any "
        "other setting from outside this package", str(settings_path),
    )]
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except ValueError:
        data = None
    if isinstance(data, dict) and data.get("hooks"):
        findings.append(Finding(
            "error", "claude-settings-has-hooks",
            "home settings.json declares hooks; arms must run hook-free", str(settings_path),
        ))
    return findings


def _check_home_instruction_files(home: Path) -> list[Finding]:
    """CLAUDE.md/AGENTS.md inside the home itself (R1 finding I2): `build_home`
    never writes either, so their presence means something else populated the
    home before or after this module ran."""
    findings: list[Finding] = []
    for name in ("CLAUDE.md", "AGENTS.md"):
        p = home / name
        if p.exists():
            findings.append(Finding(
                "error", "instruction-file-in-home",
                f"a bootstrap file was copied into the home: {p}", str(p),
            ))
    return findings


def _check_home_plugins_and_mcp(vendor: str, home: Path) -> list[Finding]:
    """A `plugins/` dir, or a `.claude.json` declaring `mcpServers`, in the
    home (R1 finding I2): both are tools an arm should not have, the same
    class of leak `_check_codex_mcp` guards against for codex's config.toml.
    """
    findings: list[Finding] = []
    if vendor == "claude":
        plugins_dir = home / "plugins"
        if plugins_dir.exists():
            findings.append(Finding(
                "error", "plugins-dir-in-home",
                f"a plugins/ directory was copied into the home: {plugins_dir}",
                str(plugins_dir),
            ))
        claude_json = home / ".claude.json"
        if claude_json.exists():
            try:
                data = json.loads(claude_json.read_text(encoding="utf-8"))
            except ValueError:
                data = None
            if isinstance(data, dict) and data.get("mcpServers"):
                findings.append(Finding(
                    "error", "claude-json-declares-mcp-servers",
                    f".claude.json declares mcpServers: {claude_json}", str(claude_json),
                ))
    return findings


def _check_memory_store(vendor: str, home: Path) -> list[Finding]:
    findings = []
    for marker in _MEMORY_MARKERS.get(vendor, ()):
        p = home / marker
        if p.exists():
            findings.append(Finding(
                "error", "memory-store-in-home",
                f"a memory store carried operator state into the home: {p}", str(p),
            ))
    return findings


def _check_builtin_collisions(vendor: str, expected_skills: set[str]) -> list[Finding]:
    """Warn when an expected skill name shadows a built-in.

    Reads whatever `builtin_baseline()` has already cached for this vendor,
    across any model. When nothing is cached yet -- a fresh SCRATCH_ROOT, or
    one `env check` before any `builtin_baseline()` call -- this fell back to
    warning about nothing at all (R1 finding I16, verified: `env check
    --skills code-review` passed clean with no cache, even though
    `code-review` is a real claude built-in). `KNOWN_BUILTINS` is the
    fallback for exactly that gap; a real cached baseline still wins when one
    exists, since it reflects what THIS container's CLI actually reports.
    """
    seen: set[str] = set()
    builtins_dir = RUNS_DIR / "builtins"
    if builtins_dir.exists():
        for f in builtins_dir.glob(f"{vendor}-*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                continue
            seen.update(data.get("skills") or [])
    if not seen:
        seen.update(KNOWN_BUILTINS.get(vendor, ()))
    collisions = sorted(set(expected_skills) & seen)
    return [
        Finding("warn", "expected-skill-collides-with-builtin",
                f"'{name}' is also a vendor built-in; activation can land on either", name)
        for name in collisions
    ]


def verify_environment(vendor: str, home: Path, cwd: Path,
                        expected_skills: set[str]) -> list[Finding]:
    """Pre-flight isolation check. See DESIGN.md sec 3 for the exact list."""
    home = Path(home)
    cwd = Path(cwd)
    findings: list[Finding] = []
    if _is_within(cwd, REPO_ROOT):
        findings.append(Finding(
            "error", "cwd-inside-repo",
            f"cwd {cwd} is inside the repository ({REPO_ROOT}); arms must run outside it",
            str(cwd),
        ))
    findings.extend(_check_cwd_under_scratch_root(cwd))
    findings.extend(_scan_instruction_files(cwd))
    findings.extend(_scan_below_cwd(cwd))
    findings.extend(_check_home_skills(home, expected_skills))
    findings.extend(_check_codex_mcp(vendor, home))
    findings.extend(_check_claude_settings(vendor, home))
    findings.extend(_check_home_instruction_files(home))
    findings.extend(_check_home_plugins_and_mcp(vendor, home))
    findings.extend(_check_memory_store(vendor, home))
    findings.extend(_check_builtin_collisions(vendor, expected_skills))
    return findings


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def _build_argv(vendor: str, home: Path, cwd: Path, model: str, effort: str,
                 tools: str, extra_flags: list[str] | None) -> tuple[list[str], dict]:
    """Shared argv/env builder for `exec_agent` and `complete`.

    Never returns a shell string: every caller passes this argv straight to
    `subprocess.run` as a list, so nothing here is ever shell-interpolated.
    Credentials live in `home`'s files, referenced only by the
    CLAUDE_CONFIG_DIR / CODEX_HOME directory paths -- never by value -- so
    `cmd` (the argv this returns) never carries a secret. The prompt itself
    never appears in this argv for either vendor: claude takes no prompt
    argument at all (it reads stdin), and codex's prompt argument is the
    literal `-`, meaning "read stdin" -- see `exec_agent`.

    The environment comes from `_build_env` (the allowlist), never
    `os.environ.copy()` -- see that function's comment (R1 finding C1).
    """
    env = _build_env(vendor, home)
    if vendor == "claude":
        argv = [
            "claude", "--print", "--output-format", "stream-json", "--verbose",
            "--model", model, "--effort", effort,
            "--permission-mode", "dontAsk", "--no-session-persistence",
            # Probed live (R1 finding C2): `--strict-mcp-config` with no
            # `--mcp-config` given ignores every other MCP source (user,
            # project, managed). It stops `mcp_servers` and the
            # `agents-md@builtin` plugin from appearing.
            "--strict-mcp-config",
            # `--strict-mcp-config` alone does not disable the claude.ai
            # org-skill/plugin sync. Measured on claude 2.1.280, across a
            # 6-run control set with `--strict-mcp-config` but no
            # `--settings` guard: the sync wrote `<config dir>/skills/synced/`
            # and `plugins/synced/` mid-run in 3 of 6 runs. Adding this
            # `--settings` value stopped the sync across a separate 16-run
            # probe, 16 of 16, and activation still worked in every one. No
            # environment variable disables the sync, and `--bare` drops
            # authentication and the installed skills, so this flag is the
            # only working guard and is applied to every claude call, for
            # both tools="activation" and tools="none" calls.
            "--settings", CLAUDE_SYNC_GUARD,
        ]
        if tools == "none":
            # Probed: `claude --help` documents `--tools <tools...>` as
            # "Use \"\" to disable all tools". Confirmed live: an empty
            # --tools value with no credentials still reaches the auth
            # check (i.e. argument parsing accepts it) rather than erroring
            # on the empty list. `--disable-slash-commands` ("Disable all
            # skills" per --help) is added only here: a judge/generator
            # (the only caller of tools="none", via `complete()`) must see
            # zero skills, but an activation arm (tools="activation") must
            # keep exactly the skills it was given.
            argv += ["--tools", "", "--disable-slash-commands"]
        else:
            # R2 finding (Important): a denylist fails open. `--disallowedTools`
            # with an unknown/misspelled name prints NO warning at all --
            # probed live by passing `--disallowedTools BogusToolXyz`, which
            # produced empty stderr and left every other tool, including
            # ListAgents/SendMessage, reachable. Live runs with the old
            # denylist (Edit,Write,NotebookEdit,Agent,Task,WebFetch,WebSearch)
            # confirmed arms kept ListAgents and SendMessage, and a live
            # ListAgents call reported the other concurrent arms as peers (R2
            # probe/listagents). The fix is a whitelist, not a longer
            # denylist: `--tools CLAUDE_ARM_TOOLS` together with the same
            # `--allowedTools` value. R2 measured the init event's `tools`
            # list as exactly these five, in this order, in 16 of 16 runs.
            whitelist = CLAUDE_TASK_TOOLS if tools == "task" else CLAUDE_ARM_TOOLS
            argv += ["--tools", whitelist, "--allowedTools", whitelist]
        if extra_flags:
            argv += extra_flags
        return argv, env

    if vendor == "codex":
        # tools="none" (judges/generators, via `complete()`) gets read-only
        # sandboxing per DESIGN.md sec 3: every command fails in this
        # container under `-s read-only`, which is the point -- a judge or
        # generator trace with a command_execution at all is void regardless.
        # tools="activation" keeps `danger-full-access`, since an arm must be
        # able to read its own skills/ tree. Web search: `codex exec --help`
        # has no `--search`/web-search flag at all (only the interactive
        # `codex --help` does, as an opt-in), and no `-c` key under
        # `codex features list` is enabled by default either
        # (`web_search_request`/`web_search_cached` both show `deprecated
        # false`) -- confirmed live with a trivial prompt that a
        # tools="none" run never invokes a web_search tool. So there is
        # nothing to additionally disable here; this comment is the record
        # DESIGN.md's "web search disabled" channel asked for (R1 finding I1).
        sandbox = "read-only" if tools == "none" else "danger-full-access"
        argv = [
            "codex", "exec", "--json", "-m", model,
            "-c", f"model_reasoning_effort={effort}",
            "-c", "service_tier=default",
            "-C", str(cwd), "--skip-git-repo-check", "-s", sandbox,
        ]
        if extra_flags:
            argv += extra_flags
        # `codex exec --help` documents that instructions are read from
        # stdin when no prompt argument is given, or when `-` is passed
        # explicitly. Passing `-`, with the prompt sent via
        # subprocess.run(..., input=prompt), writes the prompt and closes
        # stdin (EOF) -- no wrapper sentence, no prompt file in the arm's
        # cwd, nothing that changes the probe's wording or adds an extra
        # command_execution to the trace.
        argv += ["-"]
        return argv, env

    raise ValueError(f"unknown vendor {vendor!r}")


def exec_agent(vendor: str, home: Path, cwd: Path, prompt: str, trace_out: Path, *,
                model: str | None = None, effort: str = "medium", timeout: int = 600,
                tools: str = "activation", extra_flags: list[str] | None = None) -> dict:
    """Run one agent, writing its raw trace to `trace_out`.

    The prompt goes on stdin for both vendors: claude reads it directly with
    `--print`; codex takes `-` as its PROMPT argument, which (per `codex exec
    --help`) reads instructions from stdin. `subprocess.run(argv,
    input=prompt, ...)` writes the prompt and then closes stdin (EOF), which
    is what unblocks codex -- passing no prompt argument at all left codex
    waiting on stdin indefinitely in this container's non-interactive shell
    (confirmed: a call with nothing piped hung to the timeout). Nothing here
    wraps or rephrases the prompt, and no file is written into the arm's
    cwd for it: wording is exactly what an activation test measures, so nothing
    may add or reword any of it on the way to the CLI.

    `extra_flags` is an additive hook beyond DESIGN.md's sketched signature,
    used only by `complete()` to carry `--json-schema` / `--output-schema`
    through without duplicating this function's argv/env construction.

    Returns {exit_code, duration_s, trace_path, stderr_path, cmd}; `cmd`
    never contains a credential (see `_build_argv`).
    """
    if vendor not in VENDORS:
        raise ValueError(f"exec_agent: unknown vendor {vendor!r}")
    valid_efforts = CLAUDE_EFFORT_VALUES if vendor == "claude" else CODEX_EFFORT_VALUES
    if effort not in valid_efforts:
        raise ValueError(
            f"exec_agent: unknown {vendor} effort {effort!r}; expected one of "
            f"{sorted(valid_efforts)}"
        )
    home = Path(home)
    cwd = Path(cwd)
    trace_out = Path(trace_out)
    cwd.mkdir(parents=True, exist_ok=True)
    trace_out.parent.mkdir(parents=True, exist_ok=True)
    stderr_path = trace_out.parent / (trace_out.name + ".err")

    model = model or DEFAULT_MODELS[vendor]
    argv, env = _build_argv(vendor, home, cwd, model, effort, tools, extra_flags)
    # Belt-and-suspenders (R1 finding C1): `_build_env` already constructs
    # `env` from the allowlist, so this should never fire; it catches a
    # future edit to `_build_argv`/`_build_env` that reintroduces a leak
    # before it ever reaches a real subprocess.
    env_findings = [f for f in verify_arm_env(env) if f.severity == "error"]
    if env_findings:
        raise RuntimeError(
            "exec_agent: refusing to run with a leaked environment: "
            + "; ".join(f"{f.code}={f.path}" for f in env_findings)
        )

    start = time.monotonic()
    exit_code: int | None = None
    with trace_out.open("w", encoding="utf-8") as tf, stderr_path.open("w", encoding="utf-8") as ef:
        # input=prompt writes the prompt to the child's stdin and then
        # closes it (EOF) -- this is what makes codex's `-` PROMPT argument
        # return instead of hanging on "Reading additional input from
        # stdin...".
        run_kwargs = dict(cwd=str(cwd), env=env, stdout=tf, stderr=ef, timeout=timeout,
                          text=True, input=prompt)
        try:
            proc = subprocess.run(argv, **run_kwargs)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            exit_code = -1
            ef.write(f"\n[skill_eval] timed out after {timeout}s\n")

    return {
        "exit_code": exit_code,
        "duration_s": time.monotonic() - start,
        "trace_path": str(trace_out),
        "stderr_path": str(stderr_path),
        "cmd": argv,
    }


def complete(vendor: str, prompt: str, *, model: str | None = None,
             json_schema: dict | None = None, label: str = "complete",
             timeout: int = 300, effort: str = "medium") -> tuple[str, TraceRecord]:
    """One isolated single-shot call for judges and generators.

    Fresh bare home with NO skills, fresh neutral cwd, `tools="none"`.
    Callers (judge.py) must check `record.tool_calls == 0`; a call that used
    tools is void, per DESIGN.md T-B.
    """
    if vendor not in VENDORS:
        raise ValueError(f"complete: unknown vendor {vendor!r}")
    rid = run_id(label)
    home = SCRATCH_ROOT / "homes" / f"{vendor}-{rid}"
    build_home(vendor, home, {})
    cwd = neutral_cwd(label)
    try:
        # R3 finding I9 (blocker): `complete()` built a fresh home/cwd but
        # never ran the same pre-flight isolation check an activation arm
        # gets, so a judge or generator could run in a home/cwd
        # `verify_environment` would have refused. Expected skills: none --
        # `complete()`'s home is always built with `{}` above.
        findings = verify_environment(vendor, home, cwd, set())
        errors = [f for f in findings if f.severity == "error"]
        if errors:
            raise RuntimeError(
                "complete: refusing to run in a contaminated environment: "
                + "; ".join(f"{f.code}={f.path}" for f in errors)
            )

        trace_out = RUNS_DIR / "complete" / f"{rid}.jsonl"
        extra_flags = None
        if json_schema is not None:
            if vendor == "claude":
                extra_flags = ["--json-schema", json.dumps(json_schema)]
            else:
                schema_path = cwd / ".skill-eval-schema.json"
                schema_path.write_text(json.dumps(json_schema), encoding="utf-8")
                extra_flags = ["--output-schema", str(schema_path)]

        result = exec_agent(vendor, home, cwd, prompt, trace_out, model=model,
                             effort=effort, timeout=timeout, tools="none",
                             extra_flags=extra_flags)
        record = parse_trace(Path(result["trace_path"]), vendor, known_skills=[],
                              exit_code=result.get("exit_code"))
    finally:
        cleanup_home(home)
        shutil.rmtree(cwd, ignore_errors=True)
    return record.text, record


# cli_version() result cache: one subprocess call per vendor per process.
_CLI_VERSION_CACHE: dict[str, str] = {}

# A version-looking token (N.N.N, at least two dots), matched out of
# `claude --version` ("2.1.280 (Claude Code)") and `codex --version`
# ("codex-cli 0.156.0") alike, so both vendors are parsed the same way.
_VERSION_RE = re.compile(r"\d+(?:\.\d+){1,3}")


def cli_version(vendor: str) -> str:
    """The installed CLI's version string, probed once and cached.

    Runs `<cli> --version` a single time per vendor per process. Returns
    "unknown" on any failure (missing binary, non-zero exit, unparsable
    output, timeout) rather than raising -- a caller that keys a cache file
    on this value must still get a stable, safe answer when the CLI is
    unavailable.
    """
    if vendor not in VENDORS:
        raise ValueError(f"cli_version: unknown vendor {vendor!r}")
    if vendor in _CLI_VERSION_CACHE:
        return _CLI_VERSION_CACHE[vendor]
    result = "unknown"
    try:
        proc = subprocess.run([vendor, "--version"], capture_output=True, text=True, timeout=15)
        text = f"{proc.stdout}\n{proc.stderr}"
        m = _VERSION_RE.search(text)
        if proc.returncode == 0 and m:
            result = m.group(0)
    except (OSError, subprocess.SubprocessError):
        pass
    _CLI_VERSION_CACHE[vendor] = result
    return result


def baseline_cache_path(vendor: str, model: str | None = None) -> Path:
    """The cache path `builtin_baseline` reads and writes for `vendor` and
    `model` -- exposed so a caller (activation.py's dry-run cost/probe
    accounting) can check whether a baseline is already cached without
    duplicating the `{vendor}-{model}-{version}.json` naming here (R3
    finding, minor). Never touches the filesystem itself; `cli_version`
    calls the CLI once and caches its own result per process.
    """
    if vendor not in VENDORS:
        raise ValueError(f"baseline_cache_path: unknown vendor {vendor!r}")
    model = model or DEFAULT_MODELS[vendor]
    version = cli_version(vendor)
    return RUNS_DIR / "builtins" / f"{vendor}-{model}-{version}.json"


def builtin_baseline(vendor: str, model: str | None = None) -> list[str]:
    """Skills visible with nothing installed, cached under RUNS_DIR/builtins/.

    claude: read straight off the init event's `skills` list. codex: run one
    trivial call so the CLI seeds `<home>/skills/.system`, then list it --
    the CLI does not report visible skills in its event stream the way
    claude's init event does.

    R2 finding (Important): this used to cache `[]` from a failed or
    unauthenticated probe (an auth failure looks like "no builtins" forever
    after), cache a leaked `anthropic-skills:*` name as an allowed baseline
    entry, run its probe without the sync guard (fixed at the call site by
    `exec_agent`/`_build_argv` now always adding it), and key its cache file
    on vendor+model alone, so a CLI upgrade silently kept serving a stale
    baseline. Fixed here: caching requires a genuinely `ok` probe that
    produced a real (non-None) skills list; any namespaced name (containing
    ":") is dropped before caching, since a namespaced name is always a
    vendor/org built-in, never a library skill this baseline should admit;
    and the cache key includes `cli_version(vendor)`.
    """
    if vendor not in VENDORS:
        raise ValueError(f"builtin_baseline: unknown vendor {vendor!r}")
    model = model or DEFAULT_MODELS[vendor]
    version = cli_version(vendor)
    cache_path = baseline_cache_path(vendor, model)
    cache_dir = cache_path.parent
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(data.get("skills"), list):
                return list(data["skills"])
        except (ValueError, OSError):
            pass

    rid = run_id(f"builtins-{vendor}")
    home = SCRATCH_ROOT / "homes" / f"builtins-{rid}"
    build_home(vendor, home, {})
    cwd = neutral_cwd(f"builtins-{vendor}")
    trace_out = cache_dir / f"{vendor}-{model}-{version}.probe.jsonl"
    try:
        result = exec_agent(vendor, home, cwd, "Say OK and do nothing else.", trace_out,
                             model=model, timeout=120, tools="activation")
        record = parse_trace(trace_out, vendor, known_skills=[], exit_code=result.get("exit_code"))

        if vendor == "claude":
            skills = list(record.visible_skills) if record.visible_skills is not None else None
        else:
            system_dir = home / "skills" / ".system"
            skills = (sorted(p.name for p in system_dir.iterdir() if p.is_dir())
                      if system_dir.exists() else None)
    finally:
        cleanup_home(home)

    cacheable = record.ok and skills is not None
    if not cacheable:
        # Never cache a failed/unauthenticated/empty-signal probe: a `[]`
        # from a probe that never actually got an init event would poison
        # every later contamination check with a false "nothing is a
        # built-in" baseline.
        return list(skills or [])

    skills = [s for s in skills if ":" not in s]
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"vendor": vendor, "model": model, "cli_version": version,
                    "skills": skills, "captured_at": utc_now()},
                   indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return skills


# ---------------------------------------------------------------------------
# CLI: `env check`, `env builtins`
# ---------------------------------------------------------------------------


def _cmd_check(args: argparse.Namespace) -> int:
    names = [s.strip() for s in args.skills.split(",") if s.strip()]
    skills = {name: skill_dir(name) for name in names}
    manifest = build_home(args.vendor, args.home, skills)
    findings = verify_environment(args.vendor, args.home, args.cwd, set(names))
    for f in findings:
        print(f"{f.severity:5} {f.code:35} {f.message}")
    print(json.dumps(
        {"manifest": manifest, "findings": [dataclasses.asdict(f) for f in findings]},
        indent=2, sort_keys=True,
    ))
    return 1 if any(f.severity == "error" for f in findings) else 0


def _cmd_builtins(args: argparse.Namespace) -> int:
    skills = builtin_baseline(args.vendor, args.model)
    print(json.dumps(
        {"vendor": args.vendor, "model": args.model or DEFAULT_MODELS[args.vendor], "skills": skills},
        indent=2, sort_keys=True,
    ))
    return 0


def add_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "env", help="build isolated agent homes and check them for contamination",
    )
    sub = parser.add_subparsers(dest="env_command", required=True)

    check = sub.add_parser(
        "check", help="build a home with the named skills and run the pre-flight isolation check",
    )
    check.add_argument("--vendor", required=True, choices=VENDORS)
    check.add_argument("--home", required=True, type=Path)
    check.add_argument("--cwd", required=True, type=Path)
    check.add_argument("--skills", default="", help="comma-separated skill names under skills/")
    check.set_defaults(func=_cmd_check)

    builtins_p = sub.add_parser(
        "builtins", help="print (recording if uncached) the builtin-skill baseline for a vendor",
    )
    builtins_p.add_argument("--vendor", required=True, choices=VENDORS)
    builtins_p.add_argument("--model", default=None)
    builtins_p.set_defaults(func=_cmd_builtins)
