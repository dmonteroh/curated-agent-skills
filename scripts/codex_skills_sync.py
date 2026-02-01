#!/usr/bin/env python3
from __future__ import annotations

"""
codex-skills-sync

Sync selected skills from this repo into a Codex skills directory (default: ~/.codex/skills).

Safe-by-default:
- Never deletes anything unless --prune is explicitly provided.
- Never overwrites an existing installed skill unless --force is provided.
- Provides interactive prompts when flags are not supplied.

Exit codes:
- 0: success
- 1: usage/validation error
- 2: partial failure (some skills failed)
"""

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"


def eprint(*args: object, end: str = "\n") -> None:
    print(*args, file=sys.stderr, end=end)


def is_tty() -> bool:
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def default_dest() -> Path:
    # Codex default home is typically ~/.codex/skills
    return Path("~/.codex/skills").expanduser()


def skill_dirs(repo_root: Path) -> list[Path]:
    out: list[Path] = []
    for entry in sorted(repo_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name in {"scripts"}:
            continue
        if (entry / "SKILL.md").is_file():
            out.append(entry)
    return out


def skill_names(repo_root: Path) -> list[str]:
    return [p.name for p in skill_dirs(repo_root)]


def parse_selection(sel: str, items: list[str]) -> list[str]:
    """
    Parse a selection string.
    Supported:
    - 'all' or '*'
    - comma-separated names
    - comma-separated indices: '1,4,8'
    - ranges: '1-5'
    Mixed allowed; 'all'/'*' wins.
    """
    sel = (sel or "").strip()
    if not sel:
        return []
    if sel.lower() in {"all", "*"}:
        return list(items)

    chosen: set[str] = set()
    tokens = [t.strip() for t in sel.split(",") if t.strip()]
    for t in tokens:
        if "-" in t and t.replace("-", "").isdigit():
            a_s, b_s = [x.strip() for x in t.split("-", 1)]
            if not a_s.isdigit() or not b_s.isdigit():
                raise ValueError(f"invalid range: {t}")
            a = int(a_s)
            b = int(b_s)
            lo, hi = (a, b) if a <= b else (b, a)
            if lo < 1 or hi > len(items):
                raise ValueError(f"range out of bounds: {t}")
            for i in range(lo, hi + 1):
                chosen.add(items[i - 1])
            continue

        if t.isdigit():
            i = int(t)
            if i < 1 or i > len(items):
                raise ValueError(f"index out of bounds: {t}")
            chosen.add(items[i - 1])
            continue

        if t not in items:
            raise ValueError(f"unknown skill: {t}")
        chosen.add(t)

    return [s for s in items if s in chosen]


def prompt(line: str) -> str:
    # stderr for prompts so stdout stays pipe-friendly
    eprint(line, end="")
    return sys.stdin.readline().strip()


def prompt_dest(default: Path) -> Path:
    ans = prompt(f"Install directory [{default}]: ").strip()
    return Path(ans).expanduser() if ans else default


def prompt_selection(items: list[str]) -> list[str]:
    eprint("Select skills to install:")
    for i, name in enumerate(items, start=1):
        eprint(f"  {i:>3}) {name}")
    eprint("")
    eprint("Enter selection:")
    eprint("- all (or *)")
    eprint("- comma-separated indices: 1,4,7")
    eprint("- ranges: 1-5")
    eprint("- names: react-pro,svelte-pro")
    ans = prompt("> ").strip()
    return parse_selection(ans, items)


@dataclass(frozen=True)
class CopyPlan:
    src: Path
    dest: Path


def plan_copies(repo_root: Path, dest_root: Path, names: Iterable[str]) -> list[CopyPlan]:
    plans: list[CopyPlan] = []
    for name in names:
        src = repo_root / name
        if not (src / "SKILL.md").is_file():
            raise ValueError(f"not a skill directory: {src}")
        plans.append(CopyPlan(src=src, dest=dest_root / name))
    return plans


def copy_skill(plan: CopyPlan, *, force: bool, backup: bool, dry_run: bool) -> str:
    """
    Returns one of: installed, skipped
    """
    dst = plan.dest
    if dst.exists():
        if not force:
            return "skipped"
        if backup:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            backup_path = dst.with_name(dst.name + f".bak-{ts}")
            if not dry_run:
                dst.rename(backup_path)
        else:
            if not dry_run:
                shutil.rmtree(dst)

    if not dry_run:
        shutil.copytree(plan.src, dst)
    return "installed"


def list_installed(dest_root: Path) -> list[str]:
    if not dest_root.exists():
        return []
    out: list[str] = []
    for entry in sorted(dest_root.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").is_file():
            out.append(entry.name)
    return out


def prune(dest_root: Path, keep: set[str], *, dry_run: bool) -> list[Path]:
    removed: list[Path] = []
    for name in list_installed(dest_root):
        if name in keep:
            continue
        p = dest_root / name
        removed.append(p)
        if not dry_run:
            shutil.rmtree(p)
    return removed


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="codex-skills-sync",
        description="Sync selected skills from this repo into a Codex skills directory.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "--dest",
        help="Destination skills directory (default: ~/.codex/skills).",
        default=None,
    )
    parser.add_argument(
        "--select",
        help="Selection string: all|*|comma-separated names|indices|ranges.",
        default=None,
    )
    parser.add_argument("--all", action="store_true", help="Install all skills.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installed skills (default: do not overwrite).",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="When overwriting with --force, delete the existing skill instead of renaming to a timestamped backup.",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove installed skills in --dest that are not part of the selected set (dangerous; default off).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing anything.")
    parser.add_argument("--list", action="store_true", help="List skills in this repo and exit.")
    parser.add_argument(
        "--list-installed",
        action="store_true",
        help="List skills currently installed in --dest and exit.",
    )
    args = parser.parse_args(argv)

    repo_skills = skill_names(REPO_ROOT)
    if args.list:
        for s in repo_skills:
            print(s)
        return 0

    dest_root = Path(args.dest).expanduser() if args.dest else default_dest()
    if args.list_installed:
        for s in list_installed(dest_root):
            print(s)
        return 0

    if not repo_skills:
        eprint("error: no skills found in repo (no folders with SKILL.md).")
        return 1

    # Selection precedence: --all > --select > interactive prompt
    if args.all:
        selected = list(repo_skills)
    elif args.select:
        try:
            selected = parse_selection(args.select, repo_skills)
        except ValueError as e:
            eprint(f"error: {e}")
            return 1
    else:
        if not sys.stdin.isatty():
            eprint("error: no selection provided and stdin is not a TTY. Use --all or --select.")
            return 1
        dest_root = prompt_dest(dest_root)
        try:
            selected = prompt_selection(repo_skills)
        except ValueError as e:
            eprint(f"error: {e}")
            return 1

    if not selected:
        eprint("error: no skills selected.")
        return 1

    force = args.force
    backup = not args.no_backup
    dry_run = args.dry_run

    if not dest_root.exists():
        if sys.stdin.isatty() and args.dest is None and args.select is None and not args.all:
            ans = prompt(f"Create install directory {dest_root}? [y/N]: ").strip().lower()
            if ans not in {"y", "yes"}:
                eprint("aborted")
                return 1
        if not dry_run:
            dest_root.mkdir(parents=True, exist_ok=True)

    plans = plan_copies(REPO_ROOT, dest_root, selected)

    # Human-facing summary to stderr so stdout stays pipe-friendly.
    eprint(f"repo: {REPO_ROOT}")
    eprint(f"dest: {dest_root}")
    eprint(f"selected: {len(selected)} skill(s)")
    if dry_run:
        eprint("mode: dry-run")

    failures = 0
    installed: list[str] = []
    skipped: list[str] = []

    for p in plans:
        name = p.src.name
        try:
            if dry_run:
                exists = p.dest.exists()
                if exists and not force:
                    eprint(f"SKIP  {name} (already exists; use --force to overwrite)")
                else:
                    eprint(f"INSTALL {name} -> {p.dest}")
            res = copy_skill(p, force=force, backup=backup, dry_run=dry_run)
            if res == "installed":
                installed.append(name)
            else:
                skipped.append(name)
        except Exception as e:
            failures += 1
            eprint(f"error: failed to install {name}: {e}")

    removed: list[Path] = []
    if args.prune:
        removed = prune(dest_root, keep=set(selected), dry_run=dry_run)

    if is_tty():
        if installed:
            eprint("installed:")
            for s in installed:
                eprint(f"- {s}")
        if skipped:
            eprint("skipped (already exists; use --force to overwrite):")
            for s in skipped:
                eprint(f"- {s}")
        if removed:
            eprint("pruned:")
            for p in removed:
                eprint(f"- {p}")

    # stdout: stable, machine-friendly summary
    print("installed=" + str(len(installed)))
    print("skipped=" + str(len(skipped)))
    print("failed=" + str(failures))
    print("pruned=" + str(len(removed)))

    if failures:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
