import argparse
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from skill_eval import common, judge  # noqa: E402
from skill_eval import vendors as _real_vendors  # noqa: E402

# ---------------------------------------------------------------------------
# Module-wide guard: no test in this module may ever reach the real
# vendors.complete (which would shell out to a live agent). Every test here
# injects a fake `complete` (directly, or via mock.patch on the real
# attribute path); this guard makes that a hard failure instead of a subtle
# false-pass if one is ever missed, including in a combined run where the
# real `vendors` module is already imported under `skill_eval.vendors`.
# ---------------------------------------------------------------------------


def _forbidden_complete(*args, **kwargs):
    raise AssertionError(
        "test reached the real vendors.complete; inject a fake `complete` instead"
    )


_vendors_guard = None


def setUpModule():
    global _vendors_guard
    _vendors_guard = mock.patch.object(_real_vendors, "complete", _forbidden_complete)
    _vendors_guard.start()


def tearDownModule():
    _vendors_guard.stop()


def _trace(ok=True, tool_calls=0, vendor="stub"):
    return common.TraceRecord(vendor=vendor, ok=ok, tool_calls=tool_calls)


class RedactTests(unittest.TestCase):
    def test_announcement_sentence_is_redacted(self):
        text = "Let me use the testing skill to check coverage here. The rest of the report follows."
        out, n = judge.redact(text, ["testing"])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("testing skill", out.lower())
        self.assertIn("The rest of the report follows.", out)

    def test_hyphenated_name_redacted_even_in_plain_prose(self):
        text = "This is a code-review checklist for the team."
        out, n = judge.redact(text, ["code-review"])
        self.assertEqual(n, 1)
        self.assertNotIn("code-review", out)

    def test_skills_path_redacted(self):
        text = "See skills/code-review/SKILL.md for the rubric."
        out, n = judge.redact(text, ["code-review"])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("skills/code-review", out)

    def test_plugin_namespace_form_redacted(self):
        text = "Loaded via plugin:code-review as expected."
        out, n = judge.redact(text, ["code-review"])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("plugin:code-review", out)

    def test_ordinary_prose_with_common_word_name_survives(self):
        # "testing" is a common word; with no "skill" marker and no path, it
        # must not be touched.
        text = "We spent the sprint testing the new pipeline and it went smoothly."
        out, n = judge.redact(text, ["testing"])
        self.assertEqual(n, 0)
        self.assertEqual(out, text)

    def test_unrelated_prose_untouched_by_hyphenated_scan(self):
        text = "The dashboard shows steady throughput this week."
        out, n = judge.redact(text, ["code-review", "git-workflow"])
        self.assertEqual(n, 0)
        self.assertEqual(out, text)

    def test_no_match_multiline_markdown_round_trips_byte_identical(self):
        # (a) preserve the original text exactly outside redacted spans: a
        # fixture with nothing to redact must come back byte-identical, not
        # merely "similar" -- headings and bullets must not merge, and no
        # separator gets swapped for a different one.
        text = (
            "# Report\n\n"
            "This document summarises the change.\n\n"
            "## Details\n\n"
            "- First bullet point about behavior.\n"
            "- Second bullet point about edge cases.\n\n"
            "Final paragraph with closing remarks.\n"
        )
        out, n = judge.redact(text, ["testing"])
        self.assertEqual(out, text)
        self.assertEqual(n, 0)

    def test_redaction_preserves_markdown_layout_around_deleted_spans(self):
        # (b) delete the whole sentence, or whole line for a heading/list
        # item, that names a skill or announces skill use -- headings and
        # bullets must not merge into "the guide" filler prose, and a
        # hyphenated name must never produce doubled filler like
        # "the the guide".
        text = (
            "# Using the testing skill\n\n"
            "- I'll use the testing skill for this step.\n"
            "- Keep this bullet unrelated to skills.\n\n"
            "Using the testing skill here for the fix. "
            "The rest of the paragraph stays intact.\n"
        )
        out, n = judge.redact(text, ["testing"])
        self.assertGreaterEqual(n, 3)
        self.assertNotIn("the guide", out.lower())
        self.assertNotIn("the the", out.lower())
        self.assertNotIn("# Using the testing skill", out)
        self.assertNotIn("I'll use the testing skill", out)
        # unrelated content on its own line/sentence survives verbatim,
        # with its own markdown structure (the bullet marker) intact.
        self.assertIn("- Keep this bullet unrelated to skills.\n", out)
        self.assertIn("The rest of the paragraph stays intact.\n", out)

    def test_paths_normalised_to_basename_symmetrically_in_both_outputs(self):
        # (c) every absolute or relative path with a "/" becomes its
        # basename in BOTH outputs, so a path never distinguishes the arms.
        out_a = "The plan uses a git worktree at ../wt/feat-search for isolation."
        out_b = "See /workspace/scripts/auditing/skill_eval/judge.py for the change."
        redacted_a, count_a = judge.redact(out_a, [])
        redacted_b, count_b = judge.redact(out_b, [])
        self.assertIn("feat-search", redacted_a)
        self.assertNotIn("../wt/feat-search", redacted_a)
        self.assertGreaterEqual(count_a, 1)
        self.assertIn("judge.py", redacted_b)
        self.assertNotIn("/workspace/scripts/auditing/skill_eval/judge.py", redacted_b)
        self.assertGreaterEqual(count_b, 1)
        # a bare filename with no "/" is not a path and survives untouched.
        out_c = "Edit app.py to add the helper."
        redacted_c, count_c = judge.redact(out_c, [])
        self.assertEqual(redacted_c, out_c)
        self.assertEqual(count_c, 0)

    def test_vendor_self_reference_sentence_deleted(self):
        # (d) vendor self-references are redacted, whole-word and
        # case-sensitive for the proper nouns, deleting the enclosing
        # sentence when it is a self-reference.
        text = "As Claude, I approached this carefully. The fix itself is straightforward."
        out, n = judge.redact(text, [])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("Claude", out)
        self.assertIn("The fix itself is straightforward.", out)

    def test_vendor_self_reference_as_an_ai_phrase_deleted(self):
        text = "As an AI language model, I can't browse the web. Otherwise the plan looks solid."
        out, n = judge.redact(text, [])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("As an AI", out)
        self.assertIn("Otherwise the plan looks solid.", out)

    def test_vendor_name_lowercase_common_word_survives(self):
        # Case-sensitive for the proper nouns: a lowercase collision is
        # ordinary prose, not a self-reference, and must not be touched.
        text = "The design draws on anthropic principles of moral philosophy."
        out, n = judge.redact(text, [])
        self.assertEqual(out, text)
        self.assertEqual(n, 0)

    def test_announcement_sentence_deletion_is_exercised_without_skill_name_match(self):
        # R2's mutation M10 disabled announcement-sentence deletion and
        # nothing failed: this isolates the announce-regex path from the
        # skill-name path by using a skill name that does NOT appear in the
        # announcing sentence, so only _ANNOUNCE_RE can be responsible for
        # the deletion.
        text = "Let me use the specialized skill for this. Coverage looks solid across the board."
        out, n = judge.redact(text, ["testing"])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("specialized skill", out)
        self.assertIn("Coverage looks solid across the board.", out)

    def test_skill_path_sentence_fully_dropped_not_just_path_normalised(self):
        # Order-of-operations regression (live G3 verification): a sentence
        # that names the skill only through its path ("skills/<name>/
        # SKILL.md") must be flagged and dropped whole. If path
        # normalisation ran first, "skills/pr-description/SKILL.md" would
        # shrink to "SKILL.md" before the skill-name check ever saw
        # "pr-description", leaving the surrounding meta-commentary ("...for
        # the template I'm following") behind as a tell.
        text = (
            "I'll use the pr-description skill to draft this. "
            "See skills/pr-description/SKILL.md for the template I'm following.\n\n"
            "## What & Why\nAdds a helper function.\n"
        )
        out, n = judge.redact(text, ["pr-description"])
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("template I'm following", out)
        self.assertNotIn("pr-description", out)
        self.assertIn("## What & Why\nAdds a helper function.\n", out)

    def test_redaction_asymmetry_flagged_when_counts_differ(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        result = judge.pairwise(
            "do the task",
            "I'll use the testing skill here.",
            "Plain output with no mentions.",
            judge_vendor="stub-judge", repeats=1, skill_names=["testing"], complete=fake_complete,
        )
        self.assertTrue(result["redaction_asymmetry"])
        self.assertNotEqual(result["redaction_counts"]["a"], result["redaction_counts"]["b"])

    def test_redaction_symmetry_not_flagged_when_counts_equal(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        result = judge.pairwise(
            "do the task", "Plain output one.", "Plain output two.",
            judge_vendor="stub-judge", repeats=1, skill_names=["testing"], complete=fake_complete,
        )
        self.assertFalse(result["redaction_asymmetry"])
        self.assertEqual(result["redaction_counts"]["a"], result["redaction_counts"]["b"])

    def test_deleted_heading_leaves_no_leading_blank_line(self):
        # Round-3 minor finding: deleting a flagged heading/sentence at the
        # very start (or end) of the text can leave a bare blank line
        # behind -- an artifact of the deletion, not of the original
        # content -- which is itself a small, unwanted asymmetry between a
        # redacted output that had something to redact there and one that
        # didn't.
        text = "# Using the testing skill\n\nThe rest of the report follows normally.\n"
        out, n = judge.redact(text, ["testing"])
        self.assertGreaterEqual(n, 1)
        self.assertFalse(out.startswith("\n"))
        self.assertEqual(out, "The rest of the report follows normally.\n")

    def test_deleted_trailing_sentence_leaves_no_trailing_blank_line(self):
        text = "The report is complete.\n\nUsing the testing skill to wrap up now.\n"
        out, n = judge.redact(text, ["testing"])
        self.assertGreaterEqual(n, 1)
        self.assertFalse(out.endswith("\n\n"))

    def test_original_leading_and_trailing_blank_lines_survive_when_nothing_is_redacted(self):
        # The no-match round trip must stay byte-identical, including any
        # blank lines that were genuinely part of the original text.
        text = "\n\nPlain report with no mentions at all.\n\n"
        out, n = judge.redact(text, ["testing"])
        self.assertEqual(n, 0)
        self.assertEqual(out, text)

    def test_announcement_sentence_leaves_no_placeholder_behind(self):
        text = "Loading the testing skill now. Coverage looks solid across the board."
        out, n = judge.redact(text, ["testing"])
        self.assertGreaterEqual(n, 1)
        self.assertNotRegex(out, r"\[[^\]]*\]")
        self.assertIn("Coverage looks solid across the board.", out)


def _walk_object_nodes(node) -> list[dict]:
    """Every dict in `node`'s tree whose "type" is "object"."""
    found: list[dict] = []
    if isinstance(node, dict):
        if node.get("type") == "object":
            found.append(node)
        for v in node.values():
            found.extend(_walk_object_nodes(v))
    elif isinstance(node, list):
        for v in node:
            found.extend(_walk_object_nodes(v))
    return found


class SchemaAdditionalPropertiesTests(unittest.TestCase):
    def test_every_object_node_forbids_additional_properties_and_requires_every_property(self):
        # Critical (I1): the Codex API rejects any schema without
        # "additionalProperties": false at every object level ("In
        # context=(), 'additionalProperties' is required to be supplied and
        # to be false" -- observed live in R2's fixcheck trace). Codex strict
        # mode also requires every property to be listed in "required".
        schemas = {
            "PAIRWISE_JSON_SCHEMA": judge.PAIRWISE_JSON_SCHEMA,
            "GRADE_JSON_SCHEMA": judge.GRADE_JSON_SCHEMA,
            "PARAPHRASE_JSON_SCHEMA": judge.PARAPHRASE_JSON_SCHEMA,
            "CASES_JSON_SCHEMA": judge.CASES_JSON_SCHEMA,
            "COMPARE_GRADE_JSON_SCHEMA": judge.COMPARE_GRADE_JSON_SCHEMA,
        }
        for name, schema in schemas.items():
            nodes = _walk_object_nodes(schema)
            self.assertTrue(nodes, f"{name}: no object-typed node found")
            for node in nodes:
                self.assertIs(
                    node.get("additionalProperties"), False,
                    f"{name}: object node missing additionalProperties=False: {node}",
                )
                props = set(node.get("properties", {}).keys())
                required = set(node.get("required", []))
                self.assertEqual(
                    props, required,
                    f"{name}: every property must be required: {node}",
                )


class ForbiddenWordsTests(unittest.TestCase):
    def test_forbidden_words_absent_from_templates(self):
        forbidden = re.compile(r"\b(skill|arm|treatment|control|baseline)\b", re.IGNORECASE)
        templates = [
            judge.PAIRWISE_PROMPT_TEMPLATE,
            judge.GRADE_PROMPT_TEMPLATE,
            judge.PARAPHRASE_PROMPT_TEMPLATE,
            judge.CASES_PROMPT_TEMPLATE,
            judge.COMPARE_GRADE_PROMPT_TEMPLATE,
        ]
        for tmpl in templates:
            hits = forbidden.findall(tmpl)
            self.assertEqual(hits, [], f"forbidden word(s) {hits} found in template:\n{tmpl}")


class PairwiseTests(unittest.TestCase):
    def test_order_swap_mapping_is_correct_in_both_directions(self):
        # A judge that always prefers whichever position holds `out_a`'s
        # content (it can see through the labels), regardless of shown
        # order. Mapping should therefore say "a" won both repeats, with no
        # flip, even though the raw "1"/"2" answer differs between orders.
        marker = "AAA_MARKER_TEXT"

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            idx1 = prompt.index("Option 1:")
            idx2 = prompt.index("Option 2:")
            marker_idx = prompt.index(marker)
            winner = "1" if idx1 < marker_idx < idx2 else "2"
            text = json.dumps({"winner": winner, "reason": "prefers marker"})
            return text, _trace()

        result = judge.pairwise(
            "do the task", f"{marker} output", "plain output",
            judge_vendor="stub-judge", repeats=2, skill_names=(), complete=fake_complete,
        )

        self.assertEqual(result["flips"], 0)
        self.assertEqual(result["verdict"], "a")
        orders = {r["order"] for r in result["repeats"]}
        self.assertEqual(orders, {"ab", "ba"})
        for r in result["repeats"]:
            self.assertEqual(r["result"], "a")
        raw_by_order = {r["order"]: r["raw_winner"] for r in result["repeats"]}
        # raw winners differ across orders even though mapped result agrees
        self.assertEqual(raw_by_order["ab"], "1")
        self.assertEqual(raw_by_order["ba"], "2")
        self.assertEqual(result["position_bias"], 0.5)

    def test_flip_yields_a_tie(self):
        # A judge with pure position bias: always picks "1", whatever is
        # shown there. Under alternating order this must register as a flip
        # and the final verdict must be "tie".
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            text = json.dumps({"winner": "1", "reason": "first looked better"})
            return text, _trace()

        result = judge.pairwise(
            "do the task", "output A", "output B",
            judge_vendor="stub-judge", repeats=2, skill_names=(), complete=fake_complete,
        )

        self.assertEqual(result["flips"], 1)
        self.assertEqual(result["verdict"], "tie")

    def test_void_on_tool_use(self):
        calls = {"n": 0}

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            calls["n"] += 1
            if calls["n"] == 1:
                text = json.dumps({"winner": "1", "reason": "ok"})
                return text, _trace(ok=True, tool_calls=1)  # voided: used a tool
            text = json.dumps({"winner": "2", "reason": "ok"})
            return text, _trace(ok=True, tool_calls=0)

        result = judge.pairwise(
            "do the task", "output A", "output B",
            judge_vendor="stub-judge", repeats=2, skill_names=(), complete=fake_complete,
        )

        self.assertTrue(result["repeats"][0]["void"])
        self.assertFalse(result["repeats"][1]["void"])
        # I14: the surviving repeat has no valid partner to pair against (its
        # only possible partner is void), so it can't be tallied alone; with
        # no complete pair, the verdict is void.
        self.assertEqual(result["verdict"], "void")

    def test_odd_trailing_repeat_is_unpaired_and_void(self):
        # repeats=3: the first two form a complete pair, the third is a
        # trailing unpaired repeat and must not be tallied alone.
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        result = judge.pairwise(
            "do the task", "output A", "output B",
            judge_vendor="stub-judge", repeats=3, skill_names=(), complete=fake_complete,
        )

        self.assertEqual(len(result["repeats"]), 3)
        self.assertFalse(any(r["void"] for r in result["repeats"][:2]))
        # verdict is decided from the one complete pair only
        self.assertEqual(result["verdict"], "tie")

    def test_arm_map_written_only_to_run_dir(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            result = judge.pairwise(
                "do the task", "output A", "output B",
                judge_vendor="stub-judge", repeats=2, skill_names=(), run_dir=run_dir,
                complete=fake_complete,
            )
            arm_map_path = run_dir / "arm-map.json"
            self.assertTrue(arm_map_path.exists())
            data = json.loads(arm_map_path.read_text())
            self.assertEqual(len(data["repeats"]), 2)
            # the returned result carries no raw label_1/label_2 mapping table
            self.assertNotIn("label_1", json.dumps(result))

    def test_presentation_order_is_shuffled_per_pair_and_seed_recorded(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            result = judge.pairwise(
                "do the task", "output A", "output B",
                judge_vendor="stub-judge", repeats=4, skill_names=(), run_dir=run_dir,
                complete=fake_complete, seed=12345,
            )
            orders = [r["order"] for r in result["repeats"]]
            # both orders are still present within each pair
            self.assertEqual({orders[0], orders[1]}, {"ab", "ba"})
            self.assertEqual({orders[2], orders[3]}, {"ab", "ba"})

            arm_map = json.loads((run_dir / "arm-map.json").read_text())
            self.assertEqual(arm_map["seed"], 12345)

            # same seed -> same order sequence, so a run is reproducible
            result2 = judge.pairwise(
                "do the task", "output A", "output B",
                judge_vendor="stub-judge", repeats=4, skill_names=(),
                complete=fake_complete, seed=12345,
            )
            orders2 = [r["order"] for r in result2["repeats"]]
            self.assertEqual(orders, orders2)


class GradeTests(unittest.TestCase):
    def test_pass_with_supported_quote(self):
        output = "The plan uses a git worktree at ../wt/feat-search for isolation."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            # `grade()` redacts (and therefore path-normalises) the output
            # before the judge ever sees it, so the judge's quote is copied
            # from the normalised text: "../wt/feat-search" -> "feat-search".
            data = {
                "verdict": "pass",
                "quote": "uses a git worktree at feat-search",
                "reason": "worktree is named explicitly",
            }
            return json.dumps(data), _trace()

        results = judge.grade(
            "plan the change", output,
            [{"id": "worktree-isolation", "text": "Uses a git worktree, not the main tree."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "pass")
        self.assertEqual(results[0]["id"], "worktree-isolation")

    def test_fabricated_quote_is_unsupported_not_pass(self):
        output = "The plan checks out main directly and edits files in place."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            # claims a pass but quotes text that is not actually present
            data = {
                "verdict": "pass",
                "quote": "uses a git worktree for isolation",
                "reason": "fabricated",
            }
            return json.dumps(data), _trace()

        results = judge.grade(
            "plan the change", output,
            [{"id": "worktree-isolation", "text": "Uses a git worktree, not the main tree."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "unsupported")

    def test_empty_quote_is_unsupported(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"verdict": "pass", "quote": "", "reason": "trust me"}), _trace()

        results = judge.grade(
            "plan the change", "some output text",
            [{"id": "a1", "text": "Something checkable."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "unsupported")

    def test_void_grade_call_is_unsupported(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"verdict": "pass", "quote": "x", "reason": "y"}), _trace(tool_calls=2)

        results = judge.grade(
            "plan the change", "x is in here",
            [{"id": "a1", "text": "Something checkable."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "unsupported")

    def test_void_grade_call_is_unsupported_even_with_a_well_supported_quote(self):
        # Round-3 mutation survivor (grade-void-toolcalls): deleting the
        # `trace.tool_calls > 0` half of the void check left the tests
        # green, because the one existing tool-use test used a quote
        # ("x") that also fails the length check on its own. This test uses
        # a quote that is otherwise perfectly valid and present in the
        # output, so only the tool-call void check can be responsible for
        # rejecting it.
        output = "The plan checks out a fresh worktree before editing any files at all."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {
                "verdict": "pass",
                "quote": "checks out a fresh worktree before editing",
                "reason": "worktree confirmed",
            }
            return json.dumps(data), _trace(tool_calls=1)  # a tool was used: must void

        results = judge.grade(
            "plan the change", output,
            [{"id": "worktree-isolation", "text": "Uses a git worktree, not the main tree."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "unsupported")

    def test_quote_supported_normalises_quotes_and_whitespace(self):
        output = 'The agent said "hello   world  right now" today.'
        quote = "“hello world  right now”"
        self.assertTrue(judge.quote_supported(quote, output))
        self.assertFalse(judge.quote_supported("", output))
        self.assertFalse(judge.quote_supported("not present anywhere at all", output))

    def test_one_word_quote_is_never_supported(self):
        # I13: a one-character (or one-word) "quote" must never pass as
        # supporting evidence, regardless of whether it happens to appear.
        output = "a plan that mentions a briefly and moves on"
        self.assertFalse(judge.quote_supported("a", output))

    def test_short_quote_pass_becomes_unsupported(self):
        output = "The team met and agreed on a plan for next steps."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"verdict": "pass", "quote": "a plan", "reason": "short"}), _trace()

        results = judge.grade(
            "plan the change", output,
            [{"id": "a1", "text": "Something checkable."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "unsupported")

    def test_fail_with_supported_quote_of_what_output_did_instead(self):
        output = "The plan checks out main directly and edits files in place without isolation."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {
                "verdict": "fail",
                "quote": "checks out main directly and edits files in place",
                "reason": "no worktree used",
            }
            return json.dumps(data), _trace()

        results = judge.grade(
            "plan the change", output,
            [{"id": "worktree-isolation", "text": "Uses a git worktree, not the main tree."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "fail")

    def test_fail_with_no_relevant_content_literal_is_accepted(self):
        output = "A completely unrelated report about lunch orders."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {"verdict": "fail", "quote": judge.NO_RELEVANT_CONTENT, "reason": "nothing relevant"}
            return json.dumps(data), _trace()

        results = judge.grade(
            "plan the change", output,
            [{"id": "worktree-isolation", "text": "Uses a git worktree, not the main tree."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "fail")

    def test_fail_with_short_or_unsupported_quote_becomes_unsupported(self):
        output = "The plan checks out main directly and edits files in place without isolation."

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {"verdict": "fail", "quote": "bad", "reason": "short and unrelated"}
            return json.dumps(data), _trace()

        results = judge.grade(
            "plan the change", output,
            [{"id": "worktree-isolation", "text": "Uses a git worktree, not the main tree."}],
            judge_vendor="stub-judge", complete=fake_complete,
        )
        self.assertEqual(results[0]["verdict"], "unsupported")


class SealedGradeTests(unittest.TestCase):
    def test_unseal_payload_assertions_round_trip(self):
        # I11: integrity.unseal returns {"header fields...", "payload": {...}},
        # and the assertions list lives at payload["assertions"].
        from skill_eval import integrity

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "assertions.json"
            src.write_text(
                json.dumps({"assertions": [{"id": "a1", "text": "Does X."}]}), encoding="utf-8"
            )
            sealed_dir = tmp / "sealed"
            sealed_file = integrity.seal(src, "some-skill", "assertions", sealed_dir=sealed_dir)

            data = integrity.unseal(sealed_file)
            self.assertEqual(data["payload"]["assertions"], [{"id": "a1", "text": "Does X."}])

    def test_cmd_grade_sealed_uses_payload_assertions(self):
        from skill_eval import integrity

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"verdict": "fail", "quote": judge.NO_RELEVANT_CONTENT, "reason": "n/a"}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt_path = tmp / "prompt.txt"
            prompt_path.write_text("do the task", encoding="utf-8")
            output_path = tmp / "output.txt"
            output_path.write_text("the output text", encoding="utf-8")

            src = tmp / "assertions.json"
            src.write_text(
                json.dumps({"assertions": [{"id": "a1", "text": "Checks something."}]}), encoding="utf-8"
            )
            sealed_dir = tmp / "sealed"
            sealed_file = integrity.seal(src, "some-skill", "assertions", sealed_dir=sealed_dir)

            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "grade", "--prompt", str(prompt_path), "--output", str(output_path),
                "--sealed", str(sealed_file), "--judge-vendor", "stub-judge",
            ])

            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"):
                exit_code = args.func(args)

            self.assertEqual(exit_code, 0)
            run_dirs = list((tmp / "runs").glob("*judge-grade*"))
            self.assertEqual(len(run_dirs), 1)
            payload = json.loads((run_dirs[0] / "grading.json").read_text())
            # I11: grading.json now records the judge vendor/model/effort
            # alongside the per-assertion results.
            self.assertEqual(payload["judge"]["vendor"], "stub-judge")
            results = payload["results"]
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["id"], "a1")
            self.assertEqual(results[0]["verdict"], "fail")


class DefaultSkillNamesTests(unittest.TestCase):
    def test_default_skill_names_includes_library_skills(self):
        expected = set(common.library_skills())
        names = set(judge._default_skill_names())
        self.assertTrue(expected.issubset(names))

    def test_default_skill_names_tolerates_missing_builtin_list(self):
        # vendors.py may not expose KNOWN_BUILTINS yet (or ever); absence
        # must not raise.
        names = judge._default_skill_names()
        self.assertIsInstance(names, tuple)

    def test_cmd_pairwise_default_redacts_library_skill_names(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt_path = tmp / "prompt.txt"
            prompt_path.write_text("do the task", encoding="utf-8")
            a_path = tmp / "a.txt"
            a_path.write_text("I'll use the code-review skill here.", encoding="utf-8")
            b_path = tmp / "b.txt"
            b_path.write_text("Plain output with no mentions.", encoding="utf-8")

            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "pairwise", "--prompt", str(prompt_path), "--a", str(a_path),
                "--b", str(b_path), "--judge-vendor", "stub-judge", "--repeats", "1",
            ])

            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"):
                exit_code = args.func(args)

            self.assertEqual(exit_code, 0)
            run_dirs = list((tmp / "runs").glob("*judge-pairwise*"))
            self.assertEqual(len(run_dirs), 1)
            result = json.loads((run_dirs[0] / "pairwise.json").read_text())
            # "code-review" is a real library skill; it is redacted by
            # default even though --skill-names was never passed.
            self.assertGreater(result["redaction_counts"]["a"], 0)


class GenerateTests(unittest.TestCase):
    def test_description_never_sent_to_paraphrase_generator(self):
        secret_description = "UNGUESSABLE_DESCRIPTION_MARKER_9f3"
        seen_prompts = []

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            seen_prompts.append(prompt)
            return json.dumps({"paraphrases": ["a rewritten version", "another version"]}), _trace()

        def fake_echo_score(prompt, description):
            return 0.1

        def fake_longest_echo(prompt, description):
            return 1

        cases = [{"id": "c1", "skill": "some-skill", "prompt": "help me with the thing", "expect": True}]
        rows = judge.generate_paraphrases(
            cases, 2, gen_vendor="stub-gen", description=secret_description,
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=4,
        )

        self.assertTrue(rows)
        for p in seen_prompts:
            self.assertNotIn(secret_description, p)
        self.assertTrue(all(r["status"] == "accepted" for r in rows))

    def test_description_never_sent_to_case_generator(self):
        secret_description = "UNGUESSABLE_DESCRIPTION_MARKER_JOB"
        seen_prompts = []

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            seen_prompts.append(prompt)
            data = {"positive": ["do the thing please"], "negative": ["unrelated request"],
                    "near_miss": ["something that sounds similar"]}
            return json.dumps(data), _trace()

        def fake_echo_score(prompt, description):
            return 0.05

        def fake_longest_echo(prompt, description):
            return 1

        rows = judge.generate_cases(
            "one line job statement", gen_vendor="stub-gen", description=secret_description,
            n_pos=1, n_neg=1, n_near_miss=1,
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=4,
        )

        self.assertTrue(rows)
        for p in seen_prompts:
            self.assertNotIn(secret_description, p)

    def test_high_echo_candidates_are_rejected(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {"positive": ["echoey prompt"], "negative": [], "near_miss": []}
            return json.dumps(data), _trace()

        def fake_echo_score(prompt, description):
            return 0.9

        def fake_longest_echo(prompt, description):
            return 7  # above the default threshold of 4

        rows = judge.generate_cases(
            "one line job statement", gen_vendor="stub-gen", description="irrelevant here",
            n_pos=1, n_neg=0, n_near_miss=0,
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "rejected")
        self.assertIn("longest_echo", rows[0]["reason"])

    def test_high_echo_negative_and_near_miss_are_not_rejected(self):
        # Minor finding: negative/near-miss requests are meant to overlap
        # the topic, so high echo must not reject them -- only annotate.
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {
                "positive": [],
                "negative": ["echoey negative prompt"],
                "near_miss": ["echoey near miss prompt"],
            }
            return json.dumps(data), _trace()

        def fake_echo_score(prompt, description):
            return 0.9

        def fake_longest_echo(prompt, description):
            return 7  # above threshold, but must not matter for these groups

        rows = judge.generate_cases(
            "one line job statement", gen_vendor="stub-gen", description="irrelevant here",
            n_pos=0, n_neg=1, n_near_miss=1,
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["status"], "accepted")
            self.assertEqual(row["longest_echo"], 7)

    def test_high_echo_negative_paraphrase_is_not_rejected(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"paraphrases": ["an echoey rewrite"]}), _trace()

        def fake_echo_score(prompt, description):
            return 0.9

        def fake_longest_echo(prompt, description):
            return 7

        cases = [{"id": "c1", "skill": "some-skill", "prompt": "unrelated request", "expect": False}]
        rows = judge.generate_paraphrases(
            cases, 1, gen_vendor="stub-gen", description="irrelevant here",
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "accepted")

    def test_high_echo_positive_paraphrase_is_rejected(self):
        # Round-3 mutation survivor (echo-reject-off): deleting
        # `generate_paraphrases`'s `if expect and run >= echo_threshold:`
        # rejection left the tests green, because the only paraphrase-echo
        # test in this class (`test_high_echo_negative_paraphrase_is_not_
        # rejected`) uses a negative case, for which rejection never
        # applies. This exercises the positive-case path directly.
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"paraphrases": ["an echoey rewrite of the positive case"]}), _trace()

        def fake_echo_score(prompt, description):
            return 0.9

        def fake_longest_echo(prompt, description):
            return 7  # above the default threshold of 4

        cases = [{"id": "c1", "skill": "some-skill", "prompt": "help me with the thing", "expect": True}]
        rows = judge.generate_paraphrases(
            cases, 1, gen_vendor="stub-gen", description="irrelevant here",
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "rejected")
        self.assertIn("longest_echo", rows[0]["reason"])

    def test_cases_module_threshold_is_respected_when_present(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            data = {"positive": ["some prompt"], "negative": [], "near_miss": []}
            return json.dumps(data), _trace()

        def fake_echo_score(prompt, description):
            return 0.5

        def fake_longest_echo(prompt, description):
            return 2

        rows = judge.generate_cases(
            "job", gen_vendor="stub-gen", description="desc", n_pos=1, n_neg=0, n_near_miss=0,
            complete=fake_complete, echo_score=fake_echo_score, longest_echo=fake_longest_echo,
            echo_threshold=2,
        )
        self.assertEqual(rows[0]["status"], "rejected")


class GenerateFailureTests(unittest.TestCase):
    def test_generate_paraphrases_records_failed_call(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return "", _trace(ok=False)

        cases = [{"id": "c1", "skill": "some-skill", "prompt": "help me", "expect": True}]
        rows = judge.generate_paraphrases(
            cases, 2, gen_vendor="stub-gen", description="d",
            complete=fake_complete, echo_score=lambda p, d: 0.0, longest_echo=lambda p, d: 0,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "failed")
        self.assertIn("reason", rows[0])
        self.assertEqual(rows[0]["case_id"], "c1")

    def test_failed_call_row_includes_trace_error(self):
        # Minor finding: a failed-call row must carry `record.error`, not
        # drop it.
        trace = common.TraceRecord(vendor="stub", ok=False, error="auth failed: 401")
        row = judge._failed_call_row(trace, skill="s", case_id="c1")
        self.assertEqual(row["error"], "auth failed: 401")

    def test_generate_paraphrases_json_parse_error_is_recorded_not_silent(self):
        # Minor finding: a generator call that succeeds but returns unparsable
        # JSON must surface as a failed row with the parse error, not
        # silently produce zero paraphrases.
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return "not valid json {{{", _trace(ok=True)

        cases = [{"id": "c1", "skill": "some-skill", "prompt": "help me", "expect": True}]
        rows = judge.generate_paraphrases(
            cases, 2, gen_vendor="stub-gen", description="d",
            complete=fake_complete, echo_score=lambda p, d: 0.0, longest_echo=lambda p, d: 0,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "failed")
        self.assertIn("JSON parse error", rows[0]["error"])
        self.assertEqual(rows[0]["case_id"], "c1")

    def test_generate_cases_json_parse_error_is_recorded_not_silent(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return "not valid json {{{", _trace(ok=True)

        rows = judge.generate_cases(
            "job", gen_vendor="stub-gen", description="d", n_pos=1, n_neg=0, n_near_miss=0,
            complete=fake_complete, echo_score=lambda p, d: 0.0, longest_echo=lambda p, d: 0,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "failed")
        self.assertIn("JSON parse error", rows[0]["error"])

    def test_generate_cases_records_failed_call(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return "", _trace(ok=False)

        rows = judge.generate_cases(
            "job", gen_vendor="stub-gen", description="d", n_pos=1, n_neg=0, n_near_miss=0,
            complete=fake_complete, echo_score=lambda p, d: 0.0, longest_echo=lambda p, d: 0,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "failed")

    def test_generate_cases_records_failed_call_on_tool_use(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"positive": [], "negative": [], "near_miss": []}), _trace(tool_calls=1)

        rows = judge.generate_cases(
            "job", gen_vendor="stub-gen", description="d", n_pos=1, n_neg=0, n_near_miss=0,
            complete=fake_complete, echo_score=lambda p, d: 0.0, longest_echo=lambda p, d: 0,
            echo_threshold=4,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "failed")

    def test_write_candidates_lists_failed_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.md"
            judge.write_candidates(
                path, "some-skill", [], [],
                failed=[{"reason": "generator call failed: ok=False tool_calls=0", "case_id": "c1"}],
            )
            text = path.read_text()
        self.assertIn("## Failed calls", text)
        self.assertIn("generator call failed", text)
        self.assertIn("c1", text)

    def test_cmd_generate_cases_exits_nonzero_and_records_failure(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return "", _trace(ok=False)

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "generate", "cases", "--skill", "code-review", "--job", "review a diff",
                "--gen-vendor", "stub-gen", "--n-pos", "1", "--n-neg", "0", "--n-near-miss", "0",
            ])

            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"):
                exit_code = args.func(args)

            self.assertEqual(exit_code, 1)
            run_dirs = list((tmp / "runs").glob("*judge-generate-cases*"))
            self.assertEqual(len(run_dirs), 1)
            text = (run_dirs[0] / "candidates.md").read_text()
            self.assertIn("## Failed calls", text)
            self.assertNotIn("(none)\n\n## Failed calls\n\n(none)", text)
            failed_json = json.loads((run_dirs[0] / "failed-calls.json").read_text())
            self.assertEqual(len(failed_json), 1)


class WriteCandidatesTests(unittest.TestCase):
    def test_writes_accepted_and_rejected_sections(self):
        accepted = [{
            "prompt": "please help", "expect": True, "tags": ["generated"],
            "echo_score": 0.1, "longest_echo": 1,
        }]
        rejected = [{
            "prompt": "too close to the description", "expect": True,
            "tags": ["paraphrase-of:abc123"], "echo_score": 0.9, "longest_echo": 7,
            "reason": "longest_echo 7 >= threshold 4",
        }]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.md"
            judge.write_candidates(path, "some-skill", accepted, rejected)
            text = path.read_text()

        self.assertIn("# Candidate Trigger Cases: some-skill", text)
        self.assertIn("## Accepted", text)
        self.assertIn("## Rejected (do not use)", text)
        self.assertIn("## Failed calls", text)
        self.assertIn("tags: [generated]", text)
        self.assertIn("tags: [paraphrase-of:abc123]", text)
        self.assertIn("longest_echo 7 >= threshold 4", text)


class JudgeAndGeneratorMetadataTests(unittest.TestCase):
    """I11: pairwise.json and grading.json must record the judge vendor,
    model, and effort; generate outputs must record the generator's."""

    def test_pairwise_result_records_judge_vendor_model_and_effort(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        result = judge.pairwise(
            "do the task", "output A", "output B",
            judge_vendor="stub-judge", repeats=1, skill_names=(), complete=fake_complete,
            judge_model="haiku", effort="high",
        )
        self.assertEqual(result["judge"], {"vendor": "stub-judge", "model": "haiku", "effort": "high"})

    def test_cmd_pairwise_writes_judge_metadata_to_pairwise_json(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt_path = tmp / "prompt.txt"
            prompt_path.write_text("do the task", encoding="utf-8")
            a_path = tmp / "a.txt"
            a_path.write_text("output A", encoding="utf-8")
            b_path = tmp / "b.txt"
            b_path.write_text("output B", encoding="utf-8")

            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "pairwise", "--prompt", str(prompt_path), "--a", str(a_path),
                "--b", str(b_path), "--judge-vendor", "stub-judge", "--repeats", "1",
                "--judge-model", "sonnet", "--effort", "low",
            ])

            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"):
                exit_code = args.func(args)

            self.assertEqual(exit_code, 0)
            run_dirs = list((tmp / "runs").glob("*judge-pairwise*"))
            result = json.loads((run_dirs[0] / "pairwise.json").read_text())
            self.assertEqual(
                result["judge"], {"vendor": "stub-judge", "model": "sonnet", "effort": "low"},
            )

    def test_write_candidates_records_generator_metadata_as_a_comment(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.md"
            judge.write_candidates(
                path, "some-skill", [], [],
                generator={"vendor": "stub-gen", "model": "gpt-5.6-luna", "effort": "high"},
            )
            text = path.read_text()

        self.assertIn("generator:", text)
        self.assertIn("vendor=stub-gen", text)
        self.assertIn("model=gpt-5.6-luna", text)
        self.assertIn("effort=high", text)

    def test_cmd_generate_paraphrases_records_generator_metadata(self):
        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            return json.dumps({"paraphrases": []}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "generate", "paraphrases", "--skill", "code-review",
                "--gen-vendor", "stub-gen", "--gen-model", "gpt-5.6-luna", "--effort", "high",
            ])

            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"):
                args.func(args)

            run_dirs = list((tmp / "runs").glob("*judge-generate-paraphrases*"))
            text = (run_dirs[0] / "candidates.md").read_text()
        self.assertIn("vendor=stub-gen", text)
        self.assertIn("model=gpt-5.6-luna", text)
        self.assertIn("effort=high", text)


class WriteCandidatesRoundTripTests(unittest.TestCase):
    """I10: `--include-paraphrases candidates.md` goes through
    `cases.load_cases`, which parses any stripped `- prompt: "..."` line as
    a live case regardless of which heading it sits under. A rejected or
    failed row written in that same shape therefore loaded as a real case.
    This proves the fix end to end: only the accepted rows come back out."""

    def test_round_trip_through_cases_load_cases_loads_only_accepted(self):
        from skill_eval import cases as cases_mod

        accepted = [{
            "prompt": "accepted one", "expect": True, "tags": ["paraphrase-of:abc"],
            "echo_score": 0.1, "longest_echo": 1,
        }]
        rejected = [{
            "prompt": "generates a paste-ready pull request description from task briefs",
            "expect": True, "tags": ["paraphrase-of:abc"], "echo_score": 0.9, "longest_echo": 8,
            "reason": "longest_echo 8 >= threshold 4",
        }]
        failed = [{"reason": "generator call failed: ok=False tool_calls=0", "case_id": "x"}]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.md"
            judge.write_candidates(path, "pr-description", accepted, rejected, failed)

            loaded = cases_mod.load_cases("pr-description", path=path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].prompt, "accepted one")
        loaded_prompts = {c.prompt for c in loaded}
        self.assertNotIn(rejected[0]["prompt"], loaded_prompts)


class CliRegistrationTests(unittest.TestCase):
    def test_add_subparser_registers_judge_command_tree(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command", required=True)
        judge.add_subparser(sub)

        args = parser.parse_args([
            "judge", "pairwise", "--prompt", "p.txt", "--a", "a.txt", "--b", "b.txt",
            "--judge-vendor", "claude",
        ])
        self.assertEqual(args.judge_vendor, "claude")
        self.assertTrue(hasattr(args, "func"))
        # Minor finding: --judge-model and --effort exist with the
        # documented default, without being passed explicitly.
        self.assertIsNone(args.judge_model)
        self.assertEqual(args.effort, "medium")

        args2 = parser.parse_args([
            "judge", "generate", "paraphrases", "--skill", "some-skill", "--gen-vendor", "codex",
        ])
        self.assertTrue(hasattr(args2, "func"))
        self.assertIsNone(args2.gen_model)
        self.assertEqual(args2.effort, "medium")

    def test_pairwise_and_grade_accept_judge_model_and_effort_flags(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command", required=True)
        judge.add_subparser(sub)

        args = parser.parse_args([
            "judge", "pairwise", "--prompt", "p.txt", "--a", "a.txt", "--b", "b.txt",
            "--judge-vendor", "claude", "--judge-model", "haiku", "--effort", "high",
        ])
        self.assertEqual(args.judge_model, "haiku")
        self.assertEqual(args.effort, "high")

        args2 = parser.parse_args([
            "judge", "grade", "--prompt", "p.txt", "--output", "o.txt",
            "--assertions", "a.json", "--judge-vendor", "claude",
            "--judge-model", "sonnet", "--effort", "low",
        ])
        self.assertEqual(args2.judge_model, "sonnet")
        self.assertEqual(args2.effort, "low")

    def test_generate_subcommands_accept_gen_model_and_effort_flags(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command", required=True)
        judge.add_subparser(sub)

        args = parser.parse_args([
            "judge", "generate", "paraphrases", "--skill", "some-skill",
            "--gen-vendor", "codex", "--gen-model", "gpt-5.6-luna", "--effort", "low",
        ])
        self.assertEqual(args.gen_model, "gpt-5.6-luna")
        self.assertEqual(args.effort, "low")

        args2 = parser.parse_args([
            "judge", "generate", "cases", "--skill", "some-skill", "--job", "do a thing",
            "--gen-vendor", "codex", "--gen-model", "gpt-5.6-luna", "--effort", "high",
        ])
        self.assertEqual(args2.gen_model, "gpt-5.6-luna")
        self.assertEqual(args2.effort, "high")


class ModelEffortPassThroughTests(unittest.TestCase):
    def test_judge_model_forwarded_to_complete(self):
        seen = {}

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            seen["model"] = model
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        judge.pairwise(
            "do the task", "output A", "output B",
            judge_vendor="stub-judge", repeats=1, skill_names=(), complete=fake_complete,
            judge_model="haiku",
        )
        self.assertEqual(seen["model"], "haiku")

    def test_effort_always_forwarded_to_complete(self):
        # vendors.complete() takes `effort: str = "medium"` in its live
        # signature, so `_complete_kwargs` forwards it unconditionally
        # rather than gating it behind an `inspect.signature` check for
        # whether the callable declares the parameter.
        def fake_complete_with_effort(vendor, prompt, *, model=None, json_schema=None,
                                      label="complete", timeout=300, effort="medium"):
            return json.dumps({"winner": "tie", "reason": "eq"}), _trace()

        kwargs = judge._complete_kwargs(
            fake_complete_with_effort, model=None, label="x", json_schema={}, effort="high",
        )
        self.assertEqual(kwargs["effort"], "high")

    def test_cli_effort_flag_reaches_the_complete_call(self):
        # End-to-end: --effort on the pairwise CLI command must reach the
        # actual `complete()` call, not just `_complete_kwargs` in
        # isolation.
        seen = {}

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete",
                          timeout=300, effort="medium"):
            seen["effort"] = effort
            return json.dumps({"winner": "tie", "reason": "equivalent"}), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt_path = tmp / "prompt.txt"
            prompt_path.write_text("do the task", encoding="utf-8")
            a_path = tmp / "a.txt"
            a_path.write_text("output A", encoding="utf-8")
            b_path = tmp / "b.txt"
            b_path.write_text("output B", encoding="utf-8")

            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "pairwise", "--prompt", str(prompt_path), "--a", str(a_path),
                "--b", str(b_path), "--judge-vendor", "stub-judge", "--repeats", "1",
                "--effort", "high",
            ])

            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"):
                exit_code = args.func(args)

            self.assertEqual(exit_code, 0)
        self.assertEqual(seen["effort"], "high")

    def test_gen_model_forwarded_to_generator_complete(self):
        seen = {}

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            seen["model"] = model
            return json.dumps({"paraphrases": ["a rewrite"]}), _trace()

        cases = [{"id": "c1", "skill": "s", "prompt": "help", "expect": True}]
        judge.generate_paraphrases(
            cases, 1, gen_vendor="stub-gen", description="d", complete=fake_complete,
            echo_score=lambda p, d: 0.0, longest_echo=lambda p, d: 0, echo_threshold=4,
            gen_model="gpt-5.6-luna",
        )
        self.assertEqual(seen["model"], "gpt-5.6-luna")


if __name__ == "__main__":
    unittest.main()


class BatchGenerateCasesTests(unittest.TestCase):
    """`generate cases --jobs`: one candidates file per skill, rows from
    every generator vendor tagged with the vendor that wrote them, and the
    off-register group tagged and echo-checked like any positive."""

    def test_off_register_group_is_tagged_and_capped(self):
        def fake_complete(vendor, prompt, **kw):
            self.assertIn("all lowercase", prompt)
            data = {"positive": [], "negative": [], "near_miss": [],
                    "off_register": ["fix my flaky test", "flaky test again", "one too many"]}
            return json.dumps(data), _trace()

        rows = judge.generate_cases("job", gen_vendor="stub", description="unrelated words here",
                                    n_pos=0, n_neg=0, n_near_miss=0, n_off_register=2,
                                    complete=fake_complete)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertTrue(row["expect"])
            self.assertEqual(row["tags"], ["generated", "off-register"])

    def test_jobs_file_writes_one_candidates_file_per_skill_with_vendor_tags(self):
        seen = []

        def fake_complete(vendor, prompt, **kw):
            seen.append((vendor, prompt))
            data = {"positive": [f"a {vendor} request about the task"], "negative": ["something else"],
                    "near_miss": [], "off_register": []}
            return json.dumps(data), _trace()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            jobs = tmp / "jobs.json"
            jobs.write_text(json.dumps({"code-review": "look over a change for problems",
                                        "pr-description": "write up a branch for reviewers"}))
            parser = argparse.ArgumentParser()
            sub = parser.add_subparsers(dest="command", required=True)
            judge.add_subparser(sub)
            args = parser.parse_args([
                "judge", "generate", "cases", "--jobs", str(jobs), "--gen-vendor", "claude,codex",
                "--n-pos", "1", "--n-neg", "1", "--n-near-miss", "0",
            ])
            with mock.patch.object(_real_vendors, "complete", fake_complete), \
                 mock.patch.object(common, "RUNS_DIR", tmp / "runs"), \
                 mock.patch("builtins.print"):
                exit_code = args.func(args)
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(seen), 4)
            # The job reaches the generator; the description never does.
            for _, prompt in seen:
                self.assertNotIn("Provides high-signal", prompt)
            run_dir = next((tmp / "runs").glob("*judge-generate-cases*"))
            from skill_eval import cases as cases_mod
            for skill in ("code-review", "pr-description"):
                rows = cases_mod.load_cases(skill, path=run_dir / f"{skill}.candidates.md")
                tags = sorted(t for c in rows for t in c.tags if t.startswith("gen:"))
                self.assertEqual(tags, ["gen:claude", "gen:claude", "gen:codex", "gen:codex"])
            summary = json.loads((run_dir / "summary.json").read_text())
            self.assertEqual(set(summary["skills"]), {"code-review", "pr-description"})


class CompareAndGradeTests(unittest.TestCase):
    """The batched grader: every requirement for both outputs plus the
    preference, in exactly one call per presentation order."""

    GOOD = "The release notes keep the hedge that the fix may not cover every region."
    POOR = "The release is fixed everywhere and nothing else needs attention now."
    REQS = [{"id": "hedge", "text": "Keeps the uncertainty about coverage."},
            {"id": "scope", "text": "Names what is still open."}]

    def _judge(self, behaviour):
        calls = []

        def fake_complete(vendor, prompt, *, model=None, json_schema=None, label="complete", timeout=300, effort="medium"):
            calls.append(prompt)
            one, two = prompt.split("Option 1:\n", 1)[1].split("\n\nOption 2:\n", 1)
            two = two.split("\n\nRequirements:", 1)[0]
            return behaviour(one, two, len(calls)), _trace()
        return calls, fake_complete

    @staticmethod
    def _grades(text, good):
        if good:
            return [{"id": "hedge", "verdict": "pass", "quote": "may not cover every region", "reason": "kept"},
                    {"id": "scope", "verdict": "fail", "quote": "NO RELEVANT CONTENT", "reason": "absent"}]
        return [{"id": "hedge", "verdict": "fail", "quote": "fixed everywhere and nothing else", "reason": "promoted"},
                {"id": "scope", "verdict": "fail", "quote": "NO RELEVANT CONTENT", "reason": "absent"}]

    def test_two_calls_grade_every_requirement_and_map_labels_back(self):
        def honest(one, two, n):
            good_first = "may not cover" in one
            return json.dumps({"option_1": self._grades(one, good_first), "option_2": self._grades(two, not good_first),
                               "winner": "1" if good_first else "2", "reason": "keeps the hedge"})
        calls, fake = self._judge(honest)
        result = judge.compare_and_grade("Write notes.", self.POOR, self.GOOD, self.REQS,
                                         judge_vendor="stub", complete=fake, seed=3)
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0], calls[1])
        self.assertEqual([g["verdict"] for g in result["grades"]["a"]], ["fail", "fail"])
        self.assertEqual([g["verdict"] for g in result["grades"]["b"]], ["pass", "fail"])
        self.assertEqual(result["comparison"]["verdict"], "b")
        self.assertEqual(result["comparison"]["flips"], 0)

    def test_order_dependent_grades_are_unsupported_and_a_flip_is_a_tie(self):
        def first_wins(one, two, n):
            return json.dumps({"option_1": self._grades(one, True) if "may not cover" in one else
                               [{"id": "hedge", "verdict": "pass", "quote": "fixed everywhere and nothing else", "reason": "x"},
                                {"id": "scope", "verdict": "fail", "quote": "NO RELEVANT CONTENT", "reason": "x"}],
                               "option_2": self._grades(two, "may not cover" in two),
                               "winner": "1", "reason": "first"})
        _, fake = self._judge(first_wins)
        result = judge.compare_and_grade("Write notes.", self.POOR, self.GOOD, self.REQS,
                                         judge_vendor="stub", complete=fake, seed=3)
        hedge_a = result["grades"]["a"][0]
        self.assertEqual(hedge_a["verdict"], "unsupported")
        self.assertIn("order-dependent", hedge_a["reason"])
        # The good output passes in either position, so its grade stands.
        self.assertEqual(result["grades"]["b"][0]["verdict"], "pass")
        self.assertEqual(result["grades"]["a"][1]["verdict"], "fail")
        self.assertEqual(result["comparison"]["verdict"], "tie")
        self.assertEqual(result["comparison"]["flips"], 1)

    def test_fabricated_quote_missing_requirement_and_void_call_never_pass(self):
        def sloppy(one, two, n):
            return json.dumps({"option_1": [{"id": "hedge", "verdict": "pass", "quote": "words that never appeared anywhere", "reason": "x"}],
                               "option_2": [{"id": "hedge", "verdict": "pass", "quote": "words that never appeared anywhere", "reason": "x"}],
                               "winner": "tie", "reason": "same"})
        _, fake = self._judge(sloppy)
        result = judge.compare_and_grade("Write notes.", self.POOR, self.GOOD, self.REQS,
                                         judge_vendor="stub", complete=fake, seed=3)
        for label in ("a", "b"):
            self.assertEqual([g["verdict"] for g in result["grades"][label]], ["unsupported", "unsupported"])

        def tool_user(vendor, prompt, **kwargs):
            return json.dumps({"option_1": [], "option_2": [], "winner": "1", "reason": "x"}), _trace(tool_calls=1)
        result = judge.compare_and_grade("Write notes.", self.POOR, self.GOOD, self.REQS,
                                         judge_vendor="stub", complete=tool_user, seed=3)
        self.assertEqual(result["comparison"]["verdict"], "void")
        self.assertTrue(all(g["verdict"] == "unsupported" for g in result["grades"]["a"] + result["grades"]["b"]))

    def test_outputs_are_redacted_before_the_judge_sees_them(self):
        calls, fake = self._judge(lambda one, two, n: json.dumps(
            {"option_1": [], "option_2": [], "winner": "tie", "reason": "x"}))
        judge.compare_and_grade("Write notes.", "Using the demo-skill skill, " + self.GOOD, self.POOR, self.REQS,
                                judge_vendor="stub", complete=fake, skill_names=["demo-skill"], seed=1)
        for prompt in calls:
            self.assertNotIn("demo-skill", prompt)
