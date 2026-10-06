"""Build the git-repository fixtures the task suites in this directory use.

Fixtures are generated, not tracked: a nested `.git` cannot live inside this
repository. Run before `performance run` with any suite here:

    python3 scripts/auditing/suites/build_fixtures.py

Each fixture is rebuilt from scratch under `fixtures/<name>/` with fixed
author identity and dates, so its content fingerprint is stable.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "fixtures"
ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.com",
    "GIT_COMMITTER_NAME": "Dev", "GIT_COMMITTER_EMAIL": "dev@example.com",
    "GIT_AUTHOR_DATE": "2026-01-05T10:00:00Z", "GIT_COMMITTER_DATE": "2026-01-05T10:00:00Z",
}


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, env=ENV, check=True, capture_output=True)


def write(repo: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def commit(repo: Path, files: dict[str, str], message: str) -> None:
    write(repo, files)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--no-gpg-sign", "-m", message)


def new_repo(name: str) -> Path:
    repo = ROOT / name
    shutil.rmtree(repo, ignore_errors=True)
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Dev")
    git(repo, "config", "user.email", "dev@example.com")
    git(repo, "config", "commit.gpgsign", "false")
    return repo


# --- shared app used by the review and PR fixtures --------------------------

APP_BASE = {
    "README.md": "# accounts\n\nSmall account service. Run tests with `python3 -m unittest discover -s tests`.\n",
    "accounts/__init__.py": "",
    "accounts/db.py": (
        "import sqlite3\n\n\n"
        "def connect(path=':memory:'):\n"
        "    conn = sqlite3.connect(path)\n"
        "    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, name TEXT)')\n"
        "    return conn\n"
    ),
    "accounts/users.py": (
        "def get_user(conn, user_id):\n"
        "    row = conn.execute('SELECT id, email, name FROM users WHERE id = ?', (user_id,)).fetchone()\n"
        "    return None if row is None else {'id': row[0], 'email': row[1], 'name': row[2]}\n"
    ),
    "tests/__init__.py": "",
    "tests/test_users.py": (
        "import unittest\n\nfrom accounts.db import connect\nfrom accounts.users import get_user\n\n\n"
        "class GetUserTest(unittest.TestCase):\n"
        "    def test_missing_user_is_none(self):\n"
        "        self.assertIsNone(get_user(connect(), 1))\n\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n"
    ),
}


def review_search() -> None:
    """A branch adding user search and listing with three real defects:
    SQL built by string formatting, an off-by-one page slice, and a crash on
    users without a name."""
    repo = new_repo("review-search")
    commit(repo, APP_BASE, "feat: add user lookup")
    git(repo, "checkout", "-q", "-b", "feature/user-search")
    commit(repo, {
        "accounts/users.py": APP_BASE["accounts/users.py"] + (
            "\n\n"
            "def find_by_email(conn, email):\n"
            "    query = f\"SELECT id, email, name FROM users WHERE email = '{email}'\"\n"
            "    return [{'id': r[0], 'email': r[1], 'name': r[2]} for r in conn.execute(query)]\n"
            "\n\n"
            "def page(items, page_number, page_size=10):\n"
            "    \"\"\"Return one page of items; page_number starts at 1.\"\"\"\n"
            "    start = page_number * page_size\n"
            "    return items[start:start + page_size]\n"
            "\n\n"
            "def display_name(user):\n"
            "    return user['name'].strip().title()\n"
        ),
        "tests/test_search.py": (
            "import unittest\n\nfrom accounts.db import connect\nfrom accounts.users import find_by_email\n\n\n"
            "class FindTest(unittest.TestCase):\n"
            "    def test_no_match(self):\n"
            "        self.assertEqual(find_by_email(connect(), 'a@example.com'), [])\n"
        ),
    }, "feat: add user search, paging and display names")


def review_retry() -> None:
    """A branch adding an HTTP retry helper whose loop retries
    non-idempotent POSTs, swallows the final exception, and sleeps a
    constant instead of backing off; the tests only cover success."""
    repo = new_repo("review-retry")
    commit(repo, {
        "README.md": "# fetcher\n\nTiny HTTP client wrapper.\n",
        "fetcher/__init__.py": "",
        "fetcher/client.py": (
            "import urllib.request\n\n\n"
            "def send(method, url, body=None, opener=urllib.request.urlopen):\n"
            "    req = urllib.request.Request(url, data=body, method=method)\n"
            "    with opener(req, timeout=10) as resp:\n"
            "        return resp.status, resp.read()\n"
        ),
        "tests/__init__.py": "",
    }, "feat: add send helper")
    git(repo, "checkout", "-q", "-b", "feature/retries")
    commit(repo, {
        "fetcher/retry.py": (
            "import time\n\nfrom fetcher.client import send\n\n\n"
            "def send_with_retry(method, url, body=None, attempts=5, opener=None):\n"
            "    \"\"\"Send a request, retrying on any error.\"\"\"\n"
            "    kwargs = {} if opener is None else {'opener': opener}\n"
            "    for attempt in range(attempts):\n"
            "        try:\n"
            "            return send(method, url, body, **kwargs)\n"
            "        except Exception:\n"
            "            time.sleep(1)\n"
            "    return None\n"
        ),
        "tests/test_retry.py": (
            "import unittest\n\nfrom fetcher.retry import send_with_retry\n\n\n"
            "class _Resp:\n    status = 200\n    def read(self):\n        return b'ok'\n"
            "    def __enter__(self):\n        return self\n    def __exit__(self, *a):\n        return False\n\n\n"
            "class RetryTest(unittest.TestCase):\n"
            "    def test_success(self):\n"
            "        self.assertEqual(send_with_retry('GET', 'http://x', opener=lambda r, timeout: _Resp()), (200, b'ok'))\n"
        ),
    }, "feat: retry failed requests")


def pr_ratelimit() -> None:
    """A branch adding per-client rate limiting with a configurable limit
    (default 60 per minute), a 429 response, and tests; plus a brief."""
    repo = new_repo("pr-ratelimit")
    commit(repo, {
        "README.md": "# api\n\nMinimal request handler. Tests: `python3 -m unittest discover -s tests`.\n",
        "api/__init__.py": "",
        "api/handler.py": (
            "def handle(request):\n"
            "    return {'status': 200, 'body': 'hello ' + request.get('client', 'anonymous')}\n"
        ),
        "tests/__init__.py": "",
    }, "feat: add request handler")
    git(repo, "checkout", "-q", "-b", "feature/rate-limit")
    commit(repo, {
        "docs/briefs/rate-limit.md": (
            "# Brief: rate limiting\n\n"
            "Support asked for protection after one integration sent 4,000 requests in a minute and slowed every "
            "other customer. Limit each client to a configurable number of requests per minute. Over the limit, "
            "answer 429 with a Retry-After header. Do not limit health checks.\n"
        ),
        "api/ratelimit.py": (
            "import os\nimport time\n\n"
            "DEFAULT_LIMIT = int(os.environ.get('API_RATE_LIMIT_PER_MINUTE', '60'))\n\n\n"
            "class RateLimiter:\n"
            "    def __init__(self, limit=DEFAULT_LIMIT, clock=time.monotonic):\n"
            "        self.limit, self.clock, self.windows = limit, clock, {}\n\n"
            "    def allow(self, client):\n"
            "        now = self.clock()\n"
            "        start, count = self.windows.get(client, (now, 0))\n"
            "        if now - start >= 60:\n"
            "            start, count = now, 0\n"
            "        if count >= self.limit:\n"
            "            return False, int(60 - (now - start)) + 1\n"
            "        self.windows[client] = (start, count + 1)\n"
            "        return True, 0\n"
        ),
        "api/handler.py": (
            "from api.ratelimit import RateLimiter\n\n"
            "LIMITER = RateLimiter()\n\n\n"
            "def handle(request, limiter=LIMITER):\n"
            "    if request.get('path') != '/health':\n"
            "        ok, retry_after = limiter.allow(request.get('client', 'anonymous'))\n"
            "        if not ok:\n"
            "            return {'status': 429, 'headers': {'Retry-After': str(retry_after)}, 'body': 'slow down'}\n"
            "    return {'status': 200, 'body': 'hello ' + request.get('client', 'anonymous')}\n"
        ),
        "tests/test_ratelimit.py": (
            "import unittest\n\nfrom api.handler import handle\nfrom api.ratelimit import RateLimiter\n\n\n"
            "class RateLimitTest(unittest.TestCase):\n"
            "    def test_over_limit_gets_429(self):\n"
            "        lim = RateLimiter(limit=2, clock=lambda: 0.0)\n"
            "        for _ in range(2):\n"
            "            self.assertEqual(handle({'client': 'a'}, lim)['status'], 200)\n"
            "        self.assertEqual(handle({'client': 'a'}, lim)['status'], 429)\n\n"
            "    def test_health_never_limited(self):\n"
            "        lim = RateLimiter(limit=0, clock=lambda: 0.0)\n"
            "        self.assertEqual(handle({'client': 'a', 'path': '/health'}, lim)['status'], 200)\n"
        ),
        "README.md": (
            "# api\n\nMinimal request handler. Tests: `python3 -m unittest discover -s tests`.\n\n"
            "Rate limit: `API_RATE_LIMIT_PER_MINUTE` (default 60) per client; `/health` is exempt.\n"
        ),
    }, "feat: rate limit clients per minute")


def pr_renamefix() -> None:
    """A branch with two commits: a bug fix (timezone-naive timestamps
    compared with aware ones) and a rename of a public function with a
    deprecated alias kept. No brief."""
    repo = new_repo("pr-renamefix")
    commit(repo, {
        "README.md": "# events\n\nEvent window helpers.\n",
        "events/__init__.py": "",
        "events/window.py": (
            "from datetime import datetime, timedelta\n\n\n"
            "def is_recent(ts, hours=24):\n"
            "    return datetime.now() - ts < timedelta(hours=hours)\n"
        ),
        "tests/__init__.py": "",
    }, "feat: add recency helper")
    git(repo, "checkout", "-q", "-b", "fix/aware-timestamps")
    commit(repo, {
        "events/window.py": (
            "from datetime import datetime, timedelta, timezone\n\n\n"
            "def is_recent(ts, hours=24):\n"
            "    if ts.tzinfo is None:\n"
            "        ts = ts.replace(tzinfo=timezone.utc)\n"
            "    return datetime.now(timezone.utc) - ts < timedelta(hours=hours)\n"
        ),
        "tests/test_window.py": (
            "import unittest\nfrom datetime import datetime, timezone\n\nfrom events.window import is_recent\n\n\n"
            "class RecentTest(unittest.TestCase):\n"
            "    def test_aware_timestamp(self):\n"
            "        self.assertTrue(is_recent(datetime.now(timezone.utc)))\n"
        ),
    }, "fix: accept timezone-aware timestamps in is_recent")
    commit(repo, {
        "events/window.py": (
            "import warnings\nfrom datetime import datetime, timedelta, timezone\n\n\n"
            "def within_hours(ts, hours=24):\n"
            "    if ts.tzinfo is None:\n"
            "        ts = ts.replace(tzinfo=timezone.utc)\n"
            "    return datetime.now(timezone.utc) - ts < timedelta(hours=hours)\n\n\n"
            "def is_recent(ts, hours=24):\n"
            "    warnings.warn('is_recent is deprecated; use within_hours', DeprecationWarning, stacklevel=2)\n"
            "    return within_hours(ts, hours)\n"
        ),
    }, "refactor: rename is_recent to within_hours, keep deprecated alias")


# --- commit fixtures: uncommitted work in a conventional-commit repo --------

def commit_mixed() -> None:
    """Two unrelated uncommitted changes: a parser bug fix and a README
    typo; history uses conventional commits."""
    repo = new_repo("commit-mixed")
    commit(repo, {
        "README.md": "# csvtool\n\nParse CSV files into dictionaries. Seperators other than commas are suported.\n",
        "csvtool/__init__.py": "",
        "csvtool/parse.py": (
            "def parse_line(line, sep=','):\n"
            "    return line.rstrip('\\n').split(sep)\n\n\n"
            "def parse(text, sep=','):\n"
            "    lines = text.splitlines()\n"
            "    header = parse_line(lines[0], sep)\n"
            "    return [dict(zip(header, parse_line(l, sep))) for l in lines[1:-1]]\n"
        ),
    }, "feat(parse): parse csv text into dicts")
    commit(repo, {"csvtool/cli.py": "import sys\n\nfrom csvtool.parse import parse\n\nprint(parse(sys.stdin.read()))\n"},
           "feat(cli): read csv from stdin")
    write(repo, {
        "README.md": "# csvtool\n\nParse CSV files into dictionaries. Separators other than commas are supported.\n",
        "csvtool/parse.py": (
            "def parse_line(line, sep=','):\n"
            "    return line.rstrip('\\n').split(sep)\n\n\n"
            "def parse(text, sep=','):\n"
            "    lines = text.splitlines()\n"
            "    header = parse_line(lines[0], sep)\n"
            "    return [dict(zip(header, parse_line(l, sep))) for l in lines[1:] if l.strip()]\n"
        ),
    })


def commit_feature() -> None:
    """One coherent uncommitted feature (a --sep flag plus its test and docs)
    and one stray local file that should not be committed."""
    repo = new_repo("commit-feature")
    commit(repo, {
        "README.md": "# csvtool\n\nParse CSV from stdin: `python3 -m csvtool.cli < data.csv`.\n",
        ".gitignore": "__pycache__/\n",
        "csvtool/__init__.py": "",
        "csvtool/parse.py": (
            "def parse(text, sep=','):\n"
            "    lines = [l for l in text.splitlines() if l.strip()]\n"
            "    header = lines[0].split(sep)\n"
            "    return [dict(zip(header, l.split(sep))) for l in lines[1:]]\n"
        ),
        "csvtool/cli.py": "import sys\n\nfrom csvtool.parse import parse\n\nprint(parse(sys.stdin.read()))\n",
    }, "feat(parse): parse csv text into dicts")
    write(repo, {
        "csvtool/cli.py": (
            "import argparse\nimport sys\n\nfrom csvtool.parse import parse\n\n\n"
            "def main(argv=None):\n"
            "    ap = argparse.ArgumentParser()\n"
            "    ap.add_argument('--sep', default=',', help='field separator')\n"
            "    args = ap.parse_args(argv)\n"
            "    print(parse(sys.stdin.read(), sep=args.sep))\n\n\n"
            "if __name__ == '__main__':\n    main()\n"
        ),
        "tests/__init__.py": "",
        "tests/test_cli.py": (
            "import io\nimport unittest\nfrom contextlib import redirect_stdout\nfrom unittest import mock\n\n"
            "from csvtool.cli import main\n\n\n"
            "class CliTest(unittest.TestCase):\n"
            "    def test_custom_separator(self):\n"
            "        out = io.StringIO()\n"
            "        with mock.patch('sys.stdin', io.StringIO('a;b\\n1;2\\n')), redirect_stdout(out):\n"
            "            main(['--sep', ';'])\n"
            "        self.assertIn(\"'a': '1'\", out.getvalue())\n"
        ),
        "README.md": (
            "# csvtool\n\nParse CSV from stdin: `python3 -m csvtool.cli < data.csv`.\n\n"
            "Use `--sep ';'` for semicolon-separated files.\n"
        ),
        "debug-output.txt": "[{'a': '1'}]\nscratch run, delete me\n",
    })


# --- debugging fixtures: a failing suite whose message hides the cause ------

def debug_shared_default() -> None:
    """A test fails only when the whole suite runs: a mutable default list
    in build_report accumulates lines across calls."""
    repo = new_repo("debug-shared-default")
    commit(repo, {
        "README.md": "# reports\n\nRun tests: `python3 -m unittest discover -s tests`.\n",
        "reports/__init__.py": "",
        "reports/build.py": (
            "def build_report(items, lines=[]):\n"
            "    for item in items:\n"
            "        lines.append(f\"- {item['name']}: {item['qty']}\")\n"
            "    return '\\n'.join(lines)\n"
        ),
        "tests/__init__.py": "",
        "tests/test_a_summary.py": (
            "import unittest\n\nfrom reports.build import build_report\n\n\n"
            "class SummaryTest(unittest.TestCase):\n"
            "    def test_summary_mentions_item(self):\n"
            "        self.assertIn('bolts', build_report([{'name': 'bolts', 'qty': 3}]))\n"
        ),
        "tests/test_b_report.py": (
            "import unittest\n\nfrom reports.build import build_report\n\n\n"
            "class ReportTest(unittest.TestCase):\n"
            "    def test_exact_report(self):\n"
            "        self.assertEqual(build_report([{'name': 'nuts', 'qty': 2}]), '- nuts: 2')\n"
        ),
    }, "feat: build inventory reports")


def debug_float_total() -> None:
    """An invoice total check fails with a confusing message: prices are
    summed as floats and compared for equality; the cause is float
    rounding, not the discount logic the message points at."""
    repo = new_repo("debug-float-total")
    commit(repo, {
        "README.md": "# invoices\n\nRun tests: `python3 -m unittest discover -s tests`.\n",
        "invoices/__init__.py": "",
        "invoices/total.py": (
            "def apply_discount(amount, percent):\n"
            "    return amount * (100 - percent) / 100\n\n\n"
            "def invoice_total(prices, discount_percent=0):\n"
            "    subtotal = 0.0\n"
            "    for p in prices:\n"
            "        subtotal += p\n"
            "    total = apply_discount(subtotal, discount_percent)\n"
            "    if total != round(total, 2):\n"
            "        raise ValueError(f'discount produced an invalid total: {total}')\n"
            "    return total\n"
        ),
        "tests/__init__.py": "",
        "tests/test_total.py": (
            "import unittest\n\nfrom invoices.total import invoice_total\n\n\n"
            "class TotalTest(unittest.TestCase):\n"
            "    def test_three_items(self):\n"
            "        self.assertEqual(invoice_total([0.10, 0.20, 0.30]), 0.60)\n\n"
            "    def test_discount(self):\n"
            "        self.assertEqual(invoice_total([10.00, 5.00], discount_percent=10), 13.50)\n"
        ),
    }, "feat: compute invoice totals")


# --- testing fixtures: an untested module; the scorer mutates it -----------

MUTANTS = Path(__file__).resolve().parent / "scorers" / "mutants"


def _untested_module(name: str, readme: str) -> None:
    spec = json.loads((MUTANTS / f"{name}.json").read_text(encoding="utf-8"))
    repo = new_repo(name)
    package = spec["path"].split("/")[0]
    commit(repo, {"README.md": readme, f"{package}/__init__.py": "", spec["path"]: spec["original"]},
           "feat: initial version")


def testing_discount() -> None:
    _untested_module("testing-discount", "# pricing\n\nOrder totals with volume discounts. Tests use unittest: "
                                         "`python3 -m unittest discover -s tests`.\n")


def testing_slug() -> None:
    _untested_module("testing-slug", "# text\n\nText helpers. Tests use unittest: "
                                     "`python3 -m unittest discover -s tests`.\n")


BUILDERS = [review_search, review_retry, pr_ratelimit, pr_renamefix,
            commit_mixed, commit_feature, debug_shared_default, debug_float_total,
            testing_discount, testing_slug]


if __name__ == "__main__":
    for build in BUILDERS:
        build()
        print(f"built {build.__name__}")
