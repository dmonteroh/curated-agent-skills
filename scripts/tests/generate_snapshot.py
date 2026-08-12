#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import audit_skills as audit  # noqa: E402

SNAPSHOT_PATH = Path(__file__).resolve().parent / "data" / "audit_snapshot.json"


def build_snapshot() -> list[dict[str, object]]:
    snapshot: list[dict[str, object]] = []
    for entry in sorted(audit.SKILLS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name in audit.SKIP_DIRS:
            continue
        if not (entry / "SKILL.md").is_file():
            continue
        issues, warnings = audit.scan_skill(entry, token_checks=False)
        snapshot.append({"name": entry.name, "issues": issues, "warnings": warnings})
    return snapshot


def main() -> int:
    snapshot = build_snapshot()
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {SNAPSHOT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
