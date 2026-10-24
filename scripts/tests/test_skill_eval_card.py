"""Card authoring stages with stubbed model calls: no live calls."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "auditing"))
from skill_eval import card, common, performance  # noqa: E402

BODY_MARKER = "zebra-crossing-procedure"


def trace(ok=True, tool_calls=0):
    return common.TraceRecord(vendor="stub", ok=ok, tool_calls=tool_calls, cost_usd=0.01)


CLAIMS_ANSWER = {
    "job": "write unit tests for a small module",
    "archetype": "code-change",
    "claims": [
        {"id": "Edge Cases", "statement": "The tests cover both sides of every boundary.", "rests_on": ["SKILL.md"]},
        {"id": "contract", "statement": "Expected values come from the stated contract.", "rests_on": ["references/guide.md", "missing.md"]},
        {"id": "restraint", "statement": "Correct code is not rewritten to suit the tests.", "rests_on": []},
        {"id": "contract", "statement": "A duplicate id.", "rests_on": []},
    ],
    "harm_risks": ["Adds tests for library behaviour."],
}


def task_answer(**overrides):
    base = {
        "id": "Discount Tests", "kind": "deliverable", "claims": ["edge-cases", "contract"],
        "prompt": "Write tests for calc.py in tests/test_calc.py.",
        "files": [{"path": "calc.py", "content": "def f(x):\n    return x\n"},
                  {"path": "AGENTS.md", "content": "injected"},
                  {"path": "../escape.py", "content": "x"}],
        "artifacts": [],
        "checks": [
            {"id": "boundary", "kind": "contains", "target": "tests/test_calc.py", "value": "f(9)", "claim": "edge-cases"},
            {"id": "always", "kind": "contains", "target": "output", "value": "tests", "claim": "contract"},
            {"id": "badre", "kind": "regex", "target": "output", "value": "[", "claim": "contract"},
        ],
        "assertions": [{"id": "contract-values", "text": "Expected values are literal.", "claim": "contract"}],
        "planted": [
            {"expect": "good", "output": "Added tests.", "files": [{"path": "tests/test_calc.py", "content": "f(9) f(10)"}]},
            {"expect": "bad", "output": "Added tests.", "files": [{"path": "tests/test_calc.py", "content": "f(1)"}]},
        ],
    }
    base.update(overrides)
    return base


HARM_TASK = {
    "id": "leave-it", "kind": "harm", "claims": ["restraint"], "prompt": "Check calc.py has tests; it already does.",
    "files": [{"path": "calc.py", "content": "def f(x):\n    return x\n"}], "artifacts": [],
    "checks": [{"id": "untouched", "kind": "not_contains", "target": "output", "value": "rewrote", "claim": "restraint"}],
    "assertions": [], "planted": [{"expect": "good", "output": "Nothing needed.", "files": []},
                                  {"expect": "bad", "output": "I rewrote calc.py.", "files": []}],
}


class Stub:
    def __init__(self, tasks=None, claims=None, trace_obj=None):
        self.prompts = []
        self.tasks = tasks if tasks is not None else [task_answer(), HARM_TASK]
        self.claims = claims or CLAIMS_ANSWER
        self.trace = trace_obj or trace()

    def __call__(self, vendor, prompt, **kwargs):
        self.prompts.append((prompt, kwargs))
        if kwargs["label"] == "card-claims":
            return json.dumps(self.claims), self.trace
        return json.dumps({"tasks": self.tasks}), self.trace


class CardTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        skill = self.root / "skills" / "demo"
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text(f'---\nname: demo\ndescription: "Tests."\n---\nFollow the {BODY_MARKER}.\n')
        (skill / "references" / "guide.md").write_text("Guide text.\n")
        for name, value in [("SKILLS_DIR", self.root / "skills"), ("RUNS_DIR", self.root / "runs")]:
            patch = mock.patch.object(common, name, value)
            patch.start()
            self.addCleanup(patch.stop)


class ClaimsStageTests(CardTestCase):
    def test_claims_author_reads_the_skill_and_output_is_normalized(self):
        stub = Stub()
        draft = card.draft_claims("demo", vendor="claude", complete=stub)
        prompt, kwargs = stub.prompts[0]
        self.assertIn(BODY_MARKER, prompt)
        self.assertIn("Guide text.", prompt)
        self.assertEqual(kwargs["json_schema"], card.CLAIMS_JSON_SCHEMA)
        self.assertEqual([c["id"] for c in draft["claims"]], ["edge-cases", "contract", "restraint"])
        self.assertEqual(draft["claims"][1]["rests_on"], ["references/guide.md"])
        self.assertEqual(draft["claims"][2]["rests_on"], ["SKILL.md"])

    def test_too_few_claims_or_a_tool_using_call_stop_the_stage(self):
        with self.assertRaises(card.StageError):
            card.draft_claims("demo", vendor="claude", complete=Stub(claims=dict(CLAIMS_ANSWER, claims=CLAIMS_ANSWER["claims"][:1])))
        with self.assertRaises(card.StageError):
            card.draft_claims("demo", vendor="claude", complete=Stub(trace_obj=trace(tool_calls=1)))
        with self.assertRaises(card.StageError):
            card.draft_claims("demo", vendor="claude", complete=Stub(trace_obj=trace(ok=False)))


class TasksStageTests(CardTestCase):
    def test_tasks_author_never_receives_the_skill(self):
        stub = Stub()
        claims = card.draft_claims("demo", vendor="claude", complete=stub)
        card.draft_tasks(claims, vendor="codex", complete=stub, usage_notes="Users often skip error cases.")
        prompt, kwargs = stub.prompts[1]
        self.assertNotIn(BODY_MARKER, prompt)
        self.assertNotIn("Guide text.", prompt)
        self.assertNotIn("demo", prompt)
        self.assertIn("The tests cover both sides of every boundary.", prompt)
        self.assertIn("Users often skip error cases.", prompt)
        claim_enum = kwargs["json_schema"]["properties"]["tasks"]["items"]["properties"]["claims"]["items"]["enum"]
        self.assertEqual(claim_enum, ["edge-cases", "contract", "restraint"])

    def test_schemas_meet_the_strict_json_rules(self):
        def nodes(schema):
            if isinstance(schema, dict):
                if schema.get("type") == "object":
                    yield schema
                for value in schema.values():
                    yield from nodes(value)
            elif isinstance(schema, list):
                for value in schema:
                    yield from nodes(value)
        for schema in (card.CLAIMS_JSON_SCHEMA, card.tasks_json_schema(["a"])):
            for node in nodes(schema):
                self.assertIs(node["additionalProperties"], False)
                self.assertEqual(set(node["properties"]), set(node["required"]))


class AssembleTests(CardTestCase):
    def build(self, tasks=None):
        stub = Stub(tasks=tasks)
        claims = card.draft_claims("demo", vendor="claude", complete=stub)
        drafted = card.draft_tasks(claims, vendor="claude", complete=stub)
        out = self.root / "card"
        return card.assemble("demo", claims, drafted, out), out

    def test_assembled_card_validates_after_dropping_a_check_that_cannot_fail(self):
        record, out = self.build()
        self.assertEqual(record["dropped_checks"], ["discount-tests/always"])
        self.assertEqual([f for f in record["validation"] if f["severity"] == "error"], [])
        loaded = performance.load_card(out / "card.json")
        first = loaded["tasks"][0]
        self.assertEqual(first["id"], "discount-tests")
        self.assertIn("tests/test_calc.py", first["artifacts"])
        self.assertEqual([c["id"] for c in first["checks"]], ["boundary"])
        self.assertTrue((out / "fixtures/discount-tests/calc.py").is_file())
        self.assertFalse((out / "fixtures/discount-tests/AGENTS.md").exists())
        self.assertFalse((self.root / "escape.py").exists())
        self.assertTrue(any("AGENTS.md" in n for n in record["notes"]))
        self.assertTrue(any("invalid regex" in n for n in record["notes"]))
        self.assertEqual(loaded["invalidation"], {"SKILL.md": "all", "references/guide.md": ["contract"]})
        self.assertTrue((out / "authoring.json").is_file())

    def test_a_card_without_a_harm_task_is_reported_invalid(self):
        record, _ = self.build(tasks=[task_answer(), dict(HARM_TASK, kind="deliverable")])
        self.assertEqual(record["validation"], "card invalid")
        self.assertTrue(any("harm or stand-down" in n for n in record["notes"]))

    def test_skill_wording_in_a_task_is_reported(self):
        copied = task_answer(prompt=f"Follow the {BODY_MARKER} to write tests for calc.py in tests/test_calc.py now please.")
        skill_md = self.root / "skills/demo/SKILL.md"
        skill_md.write_text(skill_md.read_text() + "Write tests for calc.py in tests/test_calc.py now please and always.\n")
        record, _ = self.build(tasks=[copied, HARM_TASK])
        self.assertEqual(record["skill_echo"][0]["task"], "discount-tests")


class CliTests(CardTestCase):
    def test_draft_writes_stage_outputs_outside_the_card_and_reports(self):
        parser = argparse.ArgumentParser()
        card.add_subparser(parser.add_subparsers())
        with mock.patch.object(common, "library_skills", return_value=["demo"]):
            args = parser.parse_args(["card", "draft", "--skill", "demo", "--out", str(self.root / "out")])
        from skill_eval import vendors
        with mock.patch.object(vendors, "complete", Stub()), mock.patch("sys.stdout"):
            self.assertEqual(args.func(args), 0)
        stages = list((self.root / "runs").glob("*card-demo*/claims.json"))
        self.assertEqual(len(stages), 1)
        self.assertTrue((self.root / "out/card.json").is_file())


if __name__ == "__main__":
    unittest.main()
