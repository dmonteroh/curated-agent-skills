#!/usr/bin/env python3
"""skill-eval: task quality, activation, corpus linting, integrity, and blind judging.

Usage: scripts/auditing/skill-eval.py <command> [<subcommand>] [options]
Run with -h after any command for its options. Design: skill_eval/DESIGN.md.
"""
import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# command -> module; each module exposes add_subparser(subparsers)
MODULES = {
    "performance": "skill_eval.performance",
    "card": "skill_eval.card",
    "activation": "skill_eval.activation",
    "cases": "skill_eval.cases",
    "integrity": "skill_eval.integrity",
    "judge": "skill_eval.judge",
    "env": "skill_eval.vendors",
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="skill-eval", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    from skill_eval import __version__
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    broken = {}
    for name, modname in MODULES.items():
        try:
            importlib.import_module(modname).add_subparser(sub)
        except Exception as exc:  # a broken module must not take the others down
            broken[name] = f"{type(exc).__name__}: {exc}"
            sub.add_parser(name, help=f"unavailable ({broken[name]})")
    args = parser.parse_args(argv)
    if args.command in broken:
        print(f"skill-eval: '{args.command}' is unavailable: {broken[args.command]}", file=sys.stderr)
        return 2
    try:
        return int(args.func(args) or 0)
    except KeyboardInterrupt:
        print("skill-eval: interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
