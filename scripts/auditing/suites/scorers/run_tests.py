"""Run a fixture's unittest suite against the collected artifacts.

    run_tests.py WORKSPACE

Prints JSON {tests_run, failures, errors}; exit 0 when the suite passes.
"""
import json
import re
import subprocess
import sys

proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                      cwd=sys.argv[1], capture_output=True, text=True, timeout=50)
out = proc.stderr
ran = re.search(r"Ran (\d+) test", out)
fails = re.search(r"failures=(\d+)", out)
errs = re.search(r"errors=(\d+)", out)
print(json.dumps({"tests_run": int(ran.group(1)) if ran else 0,
                  "failures": int(fails.group(1)) if fails else 0,
                  "errors": int(errs.group(1)) if errs else 0}))
sys.exit(0 if proc.returncode == 0 and ran and int(ran.group(1)) > 0 else 1)
