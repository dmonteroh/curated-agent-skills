"""Fixtures for writing_lint.py. Every rule gets one that fires it, and one clean
document that must stay silent. Run: python3 -m unittest discover -s scripts/tests
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import writing_lint  # noqa: E402


def lint(text, glossary=None):
    linter = writing_lint.Linter(glossary or {})
    violations, words = writing_lint.lint_text(text, "t.md", linter)
    return violations, words


def rules_fired(text, **kwargs):
    return {v.rule for v in lint(text, **kwargs)[0]}


CLEAN = """---
name: sample
---

# Migration plan

The payments service writes to one table today. This plan moves it to two, without downtime.

Step one builds the new table beside the old one. A trigger keeps both in step while the backfill runs, which takes about four hours on current volumes. Nothing reads the new table yet.

Step two switches reads over behind a flag. If the checksum comparison fails, the flag goes back and no data moved.

- Run the backfill from the replica, not the primary.
- Compare checksums per partition before the cutover.
- Keep the reverse trigger until you drop the old table.

> The team lead said: "we have been burned by a single global count before, so please do it per partition."

```python
# a seamless, robust, cutting-edge comment that must never be linted
x = 1;
```

See the [runbook](https://example.com/seamless-robust-guide) for the rollback steps.
"""


class TestBlockingRules(unittest.TestCase):
    def test_L01_sentence_over_cap(self):
        long_sentence = "The service " + "writes one more row to the audit table and " * 6 + "stops."
        self.assertIn("L01", rules_fired(long_sentence))

    def test_L02_semicolon(self):
        self.assertIn("L02", rules_fired("The job finished; the report is ready."))

    def test_L03_dash_policy_shipped_advisory(self):
        """Shipped as advisory. A fork changes the module constant. There is no config file."""
        text = "The job finished — the report is ready."
        self.assertNotIn("L03", rules_fired(text))
        self.assertIn("A10", rules_fired(text))
        for policy, present, absent in (("forbid", "L03", "A10"), ("allow", None, "L03")):
            original = writing_lint.DASH_POLICY
            writing_lint.DASH_POLICY = policy
            try:
                fired = rules_fired(text)
            finally:
                writing_lint.DASH_POLICY = original
            if present:
                self.assertIn(present, fired)
            self.assertNotIn(absent, fired)

    def test_L04_phrasal_verb(self):
        self.assertIn("L04", rules_fired("Spin up a worker before the queue drains."))

    def test_L05_hype_adjective(self):
        self.assertIn("L05", rules_fired("The migration is seamless and best-in-class."))

    def test_L06_hedge_stack(self):
        self.assertIn("L06", rules_fired("The request may have possibly perhaps failed."))

    def test_L06_single_hedge_is_kept(self):
        self.assertNotIn("L06", rules_fired("The request may have failed."))

    def test_L06_threshold_is_three_not_two(self):
        # Two distinct hedges in one sentence is ordinary careful writing, and
        # every prose statement of this rule says three.
        self.assertNotIn("L06", rules_fired("The request may have possibly failed."))
        self.assertEqual(3, writing_lint.HEDGE_STACK_THRESHOLD)

    def test_L06_spares_numeric_precision_qualifiers(self):
        # approximately qualifies the number, not the author's confidence, and
        # rule 1 protects it. Listing it as a hedge left no legal exit.
        self.assertNotIn("L06", rules_fired("Approximately 30 users may be affected."))
        for word in ("approximately", "roughly", "more or less"):
            self.assertNotIn(word, writing_lint.HEDGES)

    def test_L07_filler_phrase(self):
        self.assertIn("L07", rules_fired("We restarted the pod in order to clear the cache."))

    def test_L08_verbal_tic(self):
        self.assertIn("L08", rules_fired("Great question. The cache is cold."))

    def test_L09_compliance_announcement(self):
        self.assertIn("L09", rules_fired("To be concise, the cache is cold."))

    def test_L10_paragraph_over_cap(self):
        para = " ".join(f"Sentence number {n} is here." for n in range(12))
        self.assertIn("L10", rules_fired(para))

    def test_L12_glossary_alternate(self):
        glossary = {"worker": ["agent", "runner"]}
        fired = lint("The runner picks up the job.", glossary=glossary)[0]
        self.assertIn("L12", {v.rule for v in fired})
        self.assertIn("worker", next(v.detail for v in fired if v.rule == "L12"))

    def test_L13_conformance_claim(self):
        self.assertIn("L13", rules_fired("This document is compliant with ASD-STE100."))
        self.assertIn("L13", rules_fired("The output is STE-compliant."))

    def test_L14_vague_attribution(self):
        self.assertIn("L14", rules_fired("Studies show the cache helps."))

    def test_E01_suppression_without_reason(self):
        self.assertIn("E01", rules_fired("<!-- writing-lint: allow L02 -->\nThe job finished; done."))


class TestAdvisoryRules(unittest.TestCase):
    def test_A01_soft_cap(self):
        text = "The migration " + "moves one more table across the boundary and " * 3 + "stops."
        fired = rules_fired(text)
        self.assertIn("A01", fired)
        self.assertNotIn("L01", fired)

    def test_kept_as_is_inventory_is_exempt_from_the_caps(self):
        # The output contract demands the trailer, and a thorough one enumerates
        # more than 35 words. Measured in cf3: a Kept as-is line fired L01 on a
        # deliverable that was otherwise clean. Inventory, not prose.
        items = ", ".join(f"the {n}-minute threshold for stage {n}" for n in range(12))
        fired = rules_fired("Kept as-is: " + items + ".")
        self.assertNotIn("L01", fired)
        self.assertNotIn("A01", fired)
        self.assertIn("L01", rules_fired("Kept nothing: " + items + "."))
        # Only the caps are exempt: any other rule still fires on the trailer.
        self.assertIn("L05", rules_fired("Kept as-is: the seamless rollout claim."))

    def test_A02_passive_voice(self):
        self.assertIn("A02", rules_fired("The file is deleted."))

    def test_A03_compound_tense(self):
        self.assertIn("A03", rules_fired("We have received the report."))

    def test_A05_nominalization(self):
        self.assertIn("A05", rules_fired("The worker performs an analysis of the log."))

    def test_A06_uniform_rhythm(self):
        flat = " ".join(["The worker reads the queue item now." for _ in range(20)])
        self.assertIn("A06", rules_fired(flat))

    def test_A06_silent_on_varied_rhythm(self):
        self.assertNotIn("A06", rules_fired(CLEAN))

    def test_A07_repeated_opener(self):
        text = "Workers read the queue. Workers write the result. Workers exit."
        self.assertIn("A07", rules_fired(text))

    def test_A08_soft_hype(self):
        self.assertIn("A08", rules_fired("The design is robust."))

    def test_A09_soft_filler(self):
        self.assertIn("A09", rules_fired("The delay is large in terms of latency."))

    def test_A10_dash_notice_default(self):
        self.assertIn("A10", rules_fired("The job finished — the report is ready."))


class TestAbsorbedStructuralRules(unittest.TestCase):
    """The 2026-08-26 import from reaktor-copywriter and prose-de-slopping."""

    def test_L15_comma_joined_pivot(self):
        self.assertIn("L15", rules_fired("This isn't about speed, it's about correctness."))

    def test_L15_not_only_but_also(self):
        self.assertIn("L15", rules_fired("The gateway is not only faster but also cheaper."))

    def test_L15_cross_sentence_pivot(self):
        self.assertIn("L15", rules_fired("You're not surrounded by bugs. You're surrounded by races."))

    def test_L15_leaves_an_ordinary_negation_alone(self):
        self.assertNotIn("L15", rules_fired("The backfill is not finished. The report lands on Tuesday."))

    def test_L16_signposting(self):
        self.assertIn("L16", rules_fired("Let me break this down for you."))

    def test_L16_catches_the_frame_not_only_the_phrase(self):
        for text in ("Here's what's left, plainly.", "Here's what I found.",
                     "Here's the short version.", "Let's unpack that."):
            self.assertIn("L16", rules_fired(text), text)

    def test_L16_spares_a_frame_that_says_something(self):
        self.assertNotIn("L16", rules_fired(
            "Here's the migration script, which drops the audit table and rebuilds the index."))

    def test_L16_one_announcement_is_one_violation(self):
        fired = [v for v in lint("Let me break this down.")[0] if v.rule == "L16"]
        self.assertEqual(1, len(fired))

    def test_L20_unevidenced_verdict(self):
        for text in ("That's the carve-out working as designed.",
                     "The fix is working as intended.",
                     "It behaves as expected under load."):
            self.assertIn("L20", rules_fired(text), text)

    def test_L20_spares_a_factual_report(self):
        self.assertNotIn("L20", rules_fired("The migration finished and the table was dropped."))

    def test_L17_unevidenced_superlative(self):
        self.assertIn("L17", rules_fired("The premier option is the read replica."))

    def test_L18_emoji_anywhere(self):
        for text in ("The build passed \U0001F389 today.", "# Results \U0001F680", "- Latency dropped \u2705"):
            self.assertIn("L18", rules_fired(text), text)

    def test_L18_spares_data_markers(self):
        self.assertNotIn("L18", rules_fired("The arrow \u2192 and the check \u2713 mark the rows."))

    def test_A11_rhetorical_question_opener(self):
        text = "Why does the loop check twice? Because the call can consume the deadline."
        self.assertIn("A11", rules_fired(text))

    def test_A13_bold_label_cluster(self):
        text = "- **Latency:** dropped\n- **Throughput:** doubled\n- **Cost:** unchanged\n"
        self.assertIn("A13", rules_fired(text))

    def test_A13_needs_a_cluster_not_one_bullet(self):
        self.assertNotIn("A13", rules_fired("- **Latency:** dropped to 40ms\n"))

    def test_A14_copula_avoidance(self):
        self.assertIn("A14", rules_fired("The trigger serves as the safety net."))

    def test_A15_noun_stack(self):
        for text in ("We bought an enterprise digital transformation platform.",
                     "The vendor sells a customer engagement optimization framework.",
                     "It is a cloud-native microservice orchestration layer.",
                     "Their enterprise data governance strategy is unclear."):
            self.assertIn("A15", rules_fired(text), text)

    def test_A15_spares_ordinary_technical_compounds(self):
        self.assertNotIn("A15", rules_fired("The integration test suite runs on every push."))
        self.assertNotIn("A15", rules_fired("We regenerate the content table generator output."))

    def test_A16_pseudo_analysis_tail(self):
        self.assertIn("A16", rules_fired("The team shipped the gateway, underscoring the value of the work."))

    def test_A16_spares_an_ordinary_participle(self):
        self.assertNotIn("A16", rules_fired("The team shipped it, keeping the old path alive for a week."))

    def test_A17_false_range(self):
        self.assertIn("A17", rules_fired("Support runs from onboarding to retirement."))

    def test_A18_engagement_close(self):
        self.assertIn("A18", rules_fired("The migration finished. What will you build with it?"))

    def test_A20_cluster_needs_two_distinct(self):
        self.assertIn("A20", rules_fired("The team will harness the platform to foster growth."))
        self.assertNotIn("A20", rules_fired("We navigate the release calendar every week."))

    def test_A20_counts_distinct_not_repeats(self):
        self.assertNotIn("A20", rules_fired("We harness the queue and harness the pool."))

    def test_A08_load_bearing_metaphor(self):
        self.assertIn("A08", rules_fired("The gate is the load-bearing half of the skill."))

    def test_A08_spares_the_construction_sense(self):
        self.assertNotIn("A08", rules_fired("The contractor replaced the load-bearing wall."))
        self.assertNotIn("A08", rules_fired("Check the load-bearing structural beam first."))
        self.assertIn("A08", rules_fired("The load-bearing structure of his argument fails."))

    def test_A08_spares_the_literal_landscape(self):
        self.assertNotIn("A08", rules_fired("Check a phone held in landscape."))
        self.assertNotIn("A08", rules_fired("Test the landscape orientation first."))
        self.assertIn("A08", rules_fired("The competitive landscape has to be scoped."))

    def test_A19_positive_conclusion(self):
        for closer in ("Exciting times ahead for the team.",
                       "The future looks bright for this team.",
                       "The possibilities are endless.",
                       "Watch this space.",
                       "Only time will tell whether it holds.",
                       "Onwards and upwards."):
            self.assertIn("A19", rules_fired("The migration finished.\n\n" + closer), closer)

    def test_A19_spares_a_factual_close(self):
        self.assertNotIn("A19", rules_fired("The migration finished on Tuesday.\n\nThe old table was dropped."))


class TestExclusions(unittest.TestCase):
    def test_clean_document_is_silent(self):
        violations, words = lint(CLEAN)
        self.assertEqual([], [f"{v.rule} {v.span!r} line {v.line}" for v in violations])
        self.assertGreater(words, 80)

    def test_fenced_code_excluded(self):
        self.assertEqual(set(), rules_fired("```\nseamless; robust\n```"))

    def test_inline_code_excluded(self):
        self.assertEqual(set(), rules_fired("Call `spin up seamless;` from the shell."))

    def test_blockquote_excluded(self):
        self.assertEqual(set(), rules_fired("> Great question. It is seamless; truly."))

    def test_frontmatter_excluded(self):
        self.assertEqual(set(), rules_fired("---\ndescription: seamless; robust\n---\n"))

    def test_link_target_excluded_but_label_linted(self):
        fired = rules_fired("Read the [seamless guide](https://example.com/robust-seamless).")
        self.assertIn("L05", fired)
        self.assertEqual([], lint("Read the [x](https://example.com/seamless).")[0])

    def test_html_comment_excluded(self):
        self.assertEqual(set(), rules_fired("<!-- seamless; robust -->"))


class TestSuppression(unittest.TestCase):
    def test_own_line_suppression_applies_to_next_line(self):
        text = "<!-- writing-lint: allow L02 the SQL fragment needs it -->\nThe job finished; done."
        self.assertNotIn("L02", rules_fired(text))

    def test_own_line_suppression_does_not_leak_further(self):
        text = ("<!-- writing-lint: allow L02 the SQL fragment needs it -->\n"
                "The job finished; done.\n\nThe next one failed; also done.")
        self.assertIn("L02", rules_fired(text))

    def test_inline_suppression(self):
        self.assertNotIn("L02", rules_fired("The job finished; done. <!-- writing-lint: allow L02 needed here -->"))

    def test_disable_file(self):
        text = "<!-- writing-lint: disable-file L05 vendor copy quoted verbatim -->\nThe product is seamless."
        self.assertNotIn("L05", rules_fired(text))


class TestSentenceSplitting(unittest.TestCase):
    def test_abbreviation_does_not_split(self):
        spans = writing_lint.split_sentences("Use the flag, e.g. the retry flag, before the run.")
        self.assertEqual(1, len(spans))

    def test_decimal_does_not_split(self):
        spans = writing_lint.split_sentences("The budget is 1.5 seconds per call.")
        self.assertEqual(1, len(spans))

    def test_real_boundary_splits(self):
        spans = writing_lint.split_sentences("Open the file. Read line three.")
        self.assertEqual(2, len(spans))


class TestPositions(unittest.TestCase):
    def test_line_and_column_point_at_the_span(self):
        text = "# Title\n\nThe rollout was seamless.\n"
        hit = next(v for v in lint(text)[0] if v.rule == "L05")
        self.assertEqual(3, hit.line)
        self.assertEqual("seamless", hit.span)
        self.assertEqual("seamless", text.splitlines()[hit.line - 1][hit.col - 1:hit.col - 1 + len(hit.span)])


class TestCli(unittest.TestCase):
    def _run(self, argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        if stdin is not None:
            sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = writing_lint.main(argv)
        finally:
            sys.stdin = old
        return code, out.getvalue(), err.getvalue()

    def test_exit_zero_on_clean(self):
        code, out, _ = self._run(["-"], stdin=CLEAN)
        self.assertEqual(0, code)
        self.assertIn("0 blocking", out)

    def test_exit_one_on_blocking(self):
        code, _, _ = self._run(["-"], stdin="The rollout was seamless.")
        self.assertEqual(1, code)

    def test_exit_zero_on_advisory_only(self):
        code, out, _ = self._run(["-"], stdin="The design is robust.")
        self.assertEqual(0, code)
        self.assertIn("advisory", out)

    def test_exit_two_on_missing_path(self):
        code, _, err = self._run(["/nonexistent/does-not-exist.md"])
        self.assertEqual(2, code)
        self.assertIn("error", err)

    def test_exit_two_without_paths(self):
        self.assertEqual(2, self._run([])[0])

    def test_json_shape(self):
        code, out, _ = self._run(["--format", "json", "-"], stdin="The rollout was seamless.")
        payload = json.loads(out)
        self.assertEqual(1, code)
        self.assertEqual(2, payload["version"])
        self.assertEqual(1, payload["summary"]["blocking"])
        self.assertIn("blocking_per_1k", payload["summary"])
        self.assertEqual("L05", payload["violations"][0]["rule"])
        self.assertIn("fix", payload["violations"][0])

    def test_profile_flag_is_deprecated_not_fatal(self):
        # 15% of 223 traced invocations passed a profile that does not exist,
        # and each one exited 2 with nothing linted. The flag is now ignored:
        # any value, real or invented, must produce a normal lint run.
        for name in ("documentation", "pr_body", "strict", "conversation"):
            code, out, err = self._run(["--profile", name, "-"], stdin="The rollout was seamless.")
            self.assertEqual(1, code, name)
            self.assertIn("L05", out, name)
            self.assertIn("deprecated", err, name)
        code, _, err = self._run(["-"], stdin=CLEAN)
        self.assertEqual(0, code)
        self.assertNotIn("deprecated", err)

    def test_list_rules_covers_every_emitted_rule(self):
        code, out, _ = self._run(["--list-rules"])
        listed = {line.split("\t")[0] for line in out.splitlines() if line[:1] in "LAE" and "\t" in line}
        self.assertEqual(0, code)
        self.assertEqual(set(writing_lint.RULES), listed)

    def test_stats(self):
        code, out, _ = self._run(["--stats", "-"], stdin=CLEAN)
        self.assertEqual(0, code)
        self.assertIn("sentences=", out)

    def test_glossary_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"worker": ["runner"]}, fh)
            path = fh.name
        code, out, _ = self._run(["--glossary", path, "-"], stdin="The runner picks up the job.")
        self.assertEqual(1, code)
        self.assertIn("L12", out)


PY_SOURCE = '''#!/usr/bin/env python3
"""Spins up a seamless worker; it is best-in-class."""

BANNED = "# this seamless string is not a comment"


def go():
    # In order to retry, kick off the loop.
    return 1  # this may possibly perhaps be wrong
'''

JS_SOURCE = """/* A seamless, cutting-edge gateway.
   It leverages nothing. */
const x = 1; // in order to pass
"""


class TestSourceComments(unittest.TestCase):
    def _lint_as(self, text, name):
        linter = writing_lint.Linter({})
        return writing_lint.lint_text(text, name, linter)[0]

    def test_python_comments_and_docstring_are_linted(self):
        fired = {v.rule for v in self._lint_as(PY_SOURCE, "m.py")}
        self.assertIn("L04", fired)   # spins up / kick off  # writing-lint: allow L04 the fixture's own catch, named
        self.assertIn("L05", fired)   # seamless / best-in-class
        self.assertIn("L07", fired)   # in order to  # writing-lint: allow L07 the fixture's own catch, named
        self.assertIn("L06", fired)   # may possibly
        self.assertIn("L02", fired)   # semicolon in the docstring

    def test_string_literal_is_not_read_as_a_comment(self):
        hits = [v for v in self._lint_as(PY_SOURCE, "m.py")
                if v.rule == "L05" and v.line == 4]
        self.assertEqual([], hits)

    def test_shebang_produces_no_unit(self):
        units = writing_lint.extract_comments(PY_SOURCE.splitlines(), "hash")
        self.assertEqual([], [u for u in units if u.positions and u.positions[0][0] == 1])

    # Built without a literal triple quote, which the line lexer would read in
    # THIS file's own raw source.
    TQ = "\x22\x22\x22"

    def test_assigned_triple_quoted_string_is_data_not_docstring(self):
        # A test file's fixture documents are assigned strings. Reading them as
        # docstrings linted this suite's own fixtures as prose: 11 false
        # blocking hits before the guard.
        src = f"FIXTURE = {self.TQ}\nThe rollout was seamless. Truly.\n{self.TQ}\n# a real comment\n"
        fired = {v.rule for v in self._lint_as(src, "m.py")}
        self.assertNotIn("L05", fired)

    def test_directive_inside_assigned_string_does_not_leak(self):
        src = (f"FIX = {self.TQ}\n# writing-lint: allow L05\n{self.TQ}\n"
               "# The seamless pipeline.\n")
        fired = {v.rule for v in self._lint_as(src, "m.py")}
        self.assertIn("L05", fired)      # the fixture directive suppressed nothing
        self.assertNotIn("E01", fired)   # and its missing reason is not an error

    def test_block_and_line_comments_in_c_style(self):
        fired = {v.rule for v in self._lint_as(JS_SOURCE, "g.js")}
        self.assertIn("L05", fired)
        self.assertIn("L07", fired)

    def test_code_outside_comments_is_not_linted(self):
        spans = [v.span for v in self._lint_as("x = 1  # fine\ny = seamless_value\n", "m.py")]
        self.assertEqual([], spans)

    def test_fenced_block_opt_in_for_markdown(self):
        md = "Text here.\n\n```python\n# A seamless helper.\nx = 1\n```\n"
        linter = writing_lint.Linter({})
        without = writing_lint.lint_text(md, "d.md", linter)[0]
        with_flag = writing_lint.lint_text(md, "d.md", linter, code_comments=True)[0]
        self.assertEqual([], without)
        self.assertIn("L05", {v.rule for v in with_flag})

    def test_fenced_block_line_numbers_point_at_the_file(self):
        md = "Text here.\n\n```python\n# A seamless helper.\nx = 1\n```\n"
        linter = writing_lint.Linter({})
        hit = next(v for v in writing_lint.lint_text(md, "d.md", linter, code_comments=True)[0])
        self.assertEqual(4, hit.line)


PY_SUPPRESSED = """# writing-lint: allow L05 the vendor's own wording, quoted
# The seamless pipeline.
x = 1  # the robust path  # writing-lint: allow A08 domain term
"""

PY_NO_REASON = """# writing-lint: allow L05
# The seamless pipeline.
"""


class TestSourceSuppression(unittest.TestCase):
    def _lint_as(self, text, name):
        linter = writing_lint.Linter({})
        return writing_lint.lint_text(text, name, linter)[0]

    def test_own_line_directive_covers_the_next_comment(self):
        self.assertEqual([], [v.rule for v in self._lint_as(PY_SUPPRESSED, "m.py") if v.rule == "L05"])

    def test_inline_directive_covers_its_own_line(self):
        self.assertEqual([], [v.rule for v in self._lint_as(PY_SUPPRESSED, "m.py") if v.rule == "A08"])

    def test_directive_without_a_reason_is_itself_a_violation(self):
        fired = {v.rule for v in self._lint_as(PY_NO_REASON, "m.py")}
        self.assertIn("E01", fired)
        self.assertIn("L05", fired)

    def test_disable_file_works_in_source(self):
        text = "# writing-lint: disable-file L05 vendor copy reproduced verbatim\n# A seamless pipeline.\n"
        self.assertNotIn("L05", {v.rule for v in self._lint_as(text, "m.py")})

    def test_markdown_directive_still_works(self):
        text = "<!-- writing-lint: allow L05 quoted -->\nThe seamless pipeline.\n"
        self.assertNotIn("L05", {v.rule for v in self._lint_as(text, "d.md")})

    def test_suppression_does_not_leak_past_its_target(self):
        text = "# writing-lint: allow L05 quoted\n# The seamless pipeline.\n# Another seamless claim.\n"
        self.assertIn("L05", {v.rule for v in self._lint_as(text, "m.py")})


# Keep this guard at the end of the file. It once sat mid-file, and a direct
# `python3 test_writing_lint.py` run silently executed only the classes defined
# above it while discovery ran them all.
if __name__ == "__main__":
    unittest.main()
