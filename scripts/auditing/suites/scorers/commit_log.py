"""Score the commits an agent made, from the collected `.git/logs/HEAD`.

    commit_log.py WORKSPACE --base N [--min-new K] [--require-type T]

Prints JSON {new_commits, conventional, subjects}. Exit 0 when at least K
new commits exist, every new subject is a Conventional Commits header of at
most 72 characters, and (with --require-type) one of them has type T;
otherwise exit 1. N is the number of commit entries the fixture's reflog
already holds.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEADER = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: \S.*$")

ap = argparse.ArgumentParser()
ap.add_argument("workspace")
ap.add_argument("--base", type=int, required=True)
ap.add_argument("--min-new", type=int, default=1)
ap.add_argument("--require-type", default=None)
a = ap.parse_args()

log = Path(a.workspace, ".git", "logs", "HEAD")
if not log.exists():
    print(json.dumps({"error": "no reflog collected"}))
    sys.exit(1)
subjects = []
for line in log.read_text(encoding="utf-8").splitlines():
    if "\t" not in line:
        continue
    action, _, subject = line.split("\t", 1)[1].partition(": ")
    if action.startswith("commit"):
        subjects.append(subject)
new = subjects[a.base:]
conventional = sum(1 for s in new if HEADER.match(s) and len(s) <= 72)
typed = a.require_type is None or any(s.startswith(a.require_type) for s in new)
print(json.dumps({"new_commits": len(new), "conventional": conventional, "subjects": new}))
sys.exit(0 if len(new) >= a.min_new and conventional == len(new) and typed else 1)
