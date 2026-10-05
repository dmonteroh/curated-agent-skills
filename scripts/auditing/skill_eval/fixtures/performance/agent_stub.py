#!/usr/bin/env python3
"""Emit synthetic vendor events for local CLI integration tests."""
import json
import os
import sys
from pathlib import Path

if "--version" in sys.argv:
    print("fixture-client 0.0.0")
    raise SystemExit(0)

vendor = Path(sys.argv[0]).name
home = Path(os.environ["HOME"])
config = Path(os.environ["CLAUDE_CONFIG_DIR" if vendor == "claude" else "CODEX_HOME"])
assert home == config
assert "PARENT_SECRET" not in os.environ
assert "CLAUDE_CODE_MESSAGING_TOKEN" not in os.environ
prompt = sys.stdin.read()
skills = sorted(p.parent.name for p in (home / "skills").glob("*/SKILL.md"))
judge_call = "Requirement:" in prompt or "Option 1:" in prompt
if "Requirement:" in prompt:
    answer = {"verdict": "pass", "quote": "stable helpful note", "reason": "Useful."}
    if "ordinary note" in prompt:
        answer = {"verdict": "fail", "quote": "NO RELEVANT CONTENT", "reason": "Missing."}
elif "Option 1:" in prompt:
    first = prompt.find("stable helpful note") < prompt.find("ordinary note")
    answer = {"winner": "1" if first else "2", "reason": "More useful."}
else:
    answer = "OK" if "Say OK" in prompt else "stable helpful note" if skills else "ordinary note"


def emit(event):
    print(json.dumps(event))


if vendor == "claude":
    emit({"type": "system", "subtype": "init", "skills": skills,
          "tools": sys.argv[sys.argv.index("--tools") + 1].split(",") if not judge_call else []})
    if skills:
        emit({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "call-1", "name": "Skill", "input": {"skill": skills[0]}}
        ]}})
    event = {"type": "result", "is_error": False, "total_cost_usd": 0.01,
             "result": json.dumps(answer) if isinstance(answer, dict) else answer}
    if isinstance(answer, dict):
        event["structured_output"] = answer
    emit(event)
else:
    if skills:
        emit({"type": "item.completed", "item": {"id": "read-1", "type": "command_execution",
              "command": "cat " + str(home / "skills" / skills[0] / "SKILL.md"),
              "status": "completed", "exit_code": 0}})
    emit({"type": "item.completed", "item": {"id": "answer-1", "type": "agent_message",
          "text": json.dumps(answer) if isinstance(answer, dict) else answer}})
    emit({"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 2}})
