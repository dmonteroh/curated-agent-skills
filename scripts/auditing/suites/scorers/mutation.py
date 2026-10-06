"""Score an agent's unit tests by mutation: do they pass on the original
code and fail on deliberately broken versions of it?

    mutation.py WORKSPACE MUTANTS_JSON [--min-kill 0.75]

WORKSPACE holds the collected artifacts (the agent's test file and the
module). MUTANTS_JSON names the module path, its original text, and the
mutants as text replacements. The original is restored from the JSON, so an
agent that edited the module cannot make its tests pass that way; the edit
is reported. Prints JSON metrics; exit 0 when the tests pass on the original
and kill at least --min-kill of the mutants (a chosen default).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("workspace")
ap.add_argument("mutants")
ap.add_argument("--min-kill", type=float, default=0.75)
a = ap.parse_args()
spec = json.loads(Path(a.mutants).read_text(encoding="utf-8"))
src = Path(a.workspace)
module_rel = Path(spec["path"])
edited = (src / module_rel).exists() and (src / module_rel).read_text(encoding="utf-8") != spec["original"]


def run(tree: Path) -> bool:
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                          cwd=tree, capture_output=True, text=True, timeout=20)
    return proc.returncode == 0 and "Ran 0 tests" not in proc.stderr


with tempfile.TemporaryDirectory() as tmp:
    tree = Path(tmp) / "tree"
    shutil.copytree(src, tree)
    for pkg in (module_rel.parent, Path("tests")):
        (tree / pkg).mkdir(parents=True, exist_ok=True)
        (tree / pkg / "__init__.py").touch()
    tests = sorted(p.name for p in (tree / "tests").glob("test*.py"))
    (tree / module_rel).write_text(spec["original"], encoding="utf-8")
    passes = bool(tests) and run(tree)
    killed = []
    if passes:
        for m in spec["mutants"]:
            (tree / module_rel).write_text(spec["original"].replace(m["old"], m["new"]), encoding="utf-8")
            if not run(tree):
                killed.append(m["id"])
total = len(spec["mutants"])
ratio = len(killed) / total if passes else 0.0
print(json.dumps({"test_files": tests, "passes_on_original": passes, "module_edited": edited,
                  "killed": len(killed), "mutants": total, "kill_ratio": ratio,
                  "survived": [m["id"] for m in spec["mutants"] if m["id"] not in killed]}))
sys.exit(0 if passes and ratio >= a.min_kill else 1)
