#!/usr/bin/env python3
"""Proves the fixtures can fail. One mutation per rule removes that rule's
detection, then the suite runs against the mutated copy. A rule whose mutant
still passes has no real coverage, and the check reports it.

Usage: python3 scripts/tests/mutation_check.py
Exit:  0 every mutant killed, 1 a mutant survived, 2 setup error.

Requirements: Python 3.10+, standard library only. Rerun after any change to
writing_lint.py or the fixtures. A surviving mutant means a test that certifies the
gap it hides.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent

# rule -> (find, replace). Each removes exactly one rule's ability to fire.
MUTATIONS: dict[str, tuple[str, str]] = {
    "L01": ('if count > self.caps["sentence_hard"]:', "if False:"),
    "A01": ('elif count > self.caps["sentence_soft"]:', 'elif count > 10**9:'),
    "L02": ('for m in re.finditer(r";", text):', 'for m in re.finditer(r"(?!x)x", text):'),
    "L03/A10": ('if self.dash_policy != "allow":', 'if False:'),
    "L04": ("PHRASAL_VERBS = [", "PHRASAL_VERBS = [] and ["),
    "L05": ("HYPE_BLOCKING = [", "HYPE_BLOCKING = [] and ["),
    "L06": ("HEDGES = [", "HEDGES = [] and ["),
    "L07": ("FILLER_BLOCKING = [", "FILLER_BLOCKING = [] and ["),
    "L08": ("VERBAL_TICS = [", "VERBAL_TICS = [] and ["),
    "L09": ("COMPLIANCE_ANNOUNCEMENTS = [", "COMPLIANCE_ANNOUNCEMENTS = [] and ["),
    "L10": ('if count > self.caps["paragraph_hard"]:', 'if count > 10**9:'),
    "L12": ("for canonical, alternates in self.glossary.items():", "for canonical, alternates in {}.items():"),
    "L13": ("for regex in (CONFORMANCE_CLAIM_RE, CONFORMANCE_CLAIM_RE2):", "for regex in ():"),
    "L14": ("VAGUE_ATTRIBUTION = [", "VAGUE_ATTRIBUTION = [] and ["),
    "E01": ('errors.append(Violation("", lineno, m.start() + 1, "E01", m.group(0)))', "pass"),
    # Absorbed 2026-08-26 from reaktor-copywriter and prose-de-slopping.
    "L15/frames": ("for regex in CONTRASTIVE_RES:", "for regex in ():"),
    "L15/pair": ("            if same_frame or pronoun_subject:", "            if False:"),
    "L16/phrases": ("SIGNPOSTING = [", "SIGNPOSTING = [] and ["),
    "L16/frame": ("                if SIGNPOST_FRAME_RE.match(sentence.strip().lstrip(\"*_-# \")):",
                  "                if False:"),
    "L17": ("UNEVIDENCED_SUPERLATIVE = [", "UNEVIDENCED_SUPERLATIVE = [] and ["),
    "L20": ("UNEVIDENCED_VERDICT = [", "UNEVIDENCED_VERDICT = [] and ["),
    "L18": ("for m in EMOJI_RE.finditer(text):", "for m in ():"),
    "A11": ('if unit.kind == "paragraph" and len(sentences) >= 2 and sentences[0][1].rstrip().endswith("?"):',
            "if False:"),
    "A13": ("if len(labelled) >= BOLD_LABEL_MIN:", "if False:"),
    "A14": ("COPULA_AVOIDANCE = [", "COPULA_AVOIDANCE = [] and ["),
    "A15": ("STACK_NOUNS = {", "STACK_NOUNS = set() and {"),
    "A16": ("if PARTICIPLE_TAIL_RE.search(sentence):", "if False:"),
    "A17": ("for m in FALSE_RANGE_RE.finditer(text):", "for m in ():"),
    "A18": ('if tail and tail[-1][1].rstrip().endswith("?"):', "if False:"),
    "A19": ("POSITIVE_CLOSE = [", "POSITIVE_CLOSE = [] and ["),
    "A20": ("            if len(distinct) >= TIER2_CLUSTER_MIN:", "            if False:"),
    "A08/literal-sense": ("            if skipped and any(a <= offset < b for a, b in skipped):",
                          "            if False:"),
    "A02": ("for m in PASSIVE_RE.finditer(text):", "for m in ():"),
    "A03": ("for m in COMPOUND_TENSE_RE.finditer(text):", "for m in ():"),
    "A05": ("for m in NOMINALIZATION_RE.finditer(text):", "for m in ():"),
    "A06": ("RHYTHM_SD_FLOOR = 5.0", "RHYTHM_SD_FLOOR = 0.0"),
    "A07": ("if unit.kind == \"paragraph\":\n            for i in range(len(openers) - 2):",
            "if False:\n            for i in range(len(openers) - 2):"),
    "A08": ("HYPE_ADVISORY = [", "HYPE_ADVISORY = [] and ["),
    "A09": ('FILLER_ADVISORY = ["in terms of"', 'FILLER_ADVISORY = [] and ["in terms of"'),
    "suppression": ("if violation.rule in suppress_line.get(violation.line, set()):",
                    "if False:"),
    "source_suppression": ("        suppress_line, suppress_file, errors = collect_suppressions(\n"
                           "            lines, SUPPRESS_PLAIN_RE, _is_own_line_comment(style)\n"
                           "        )",
                           "        suppress_line, suppress_file, errors = {}, set(), []"),
    "hedge_threshold": ("if len(distinct) >= HEDGE_STACK_THRESHOLD:", "if len(distinct) >= 2:"),
    "exclusions": ("if QUOTE_RE.match(raw):  # quoted material is never linted", "if False:"),
    "source_comments": ("    style = EXT_STYLE.get(Path(path).suffix.lower())", "    style = None"),
    "fenced_comments": ("        if code_comments:", "        if False:"),
    "string_masking": ("        masked = STRING_RE.sub(lambda m: \" \" * len(m.group(0)), raw)", "        masked = raw"),
    "shebang_guard": ("            if style == \"hash\" and raw[idx:idx + 2] == \"#!\":", "            if False:"),
    # Parsing guards. Each had a fixture and no proof the fixture could fail.
    "inline_code_masking": ("    for m in re.finditer(r\"`[^`]*`\", line):", "    for m in ():"),
    "frontmatter_exclusion": ('    in_frontmatter = bool(lines) and lines[0].strip() == "---"',
                              "    in_frontmatter = False"),
    "sentence_boundary_guards": ("                if last not in ABBREVIATIONS and not digit_boundary:",
                                 "                if True:"),
    "kept_as_is_exemption": ("        kept_line = bool(self.KEPT_AS_IS_RE.match(unit.text))",
                             "        kept_line = False"),
    "assigned_string_guard": ("        m = ASSIGNED_STRING_RE.search(raw)", "        m = None"),
}


def main() -> int:
    source = (SCRIPTS / "writing_lint.py").read_text()
    survivors: list[str] = []

    for rule, (find, replace) in MUTATIONS.items():
        if source.count(find) != 1:
            print(f"SETUP ERROR {rule}: anchor found {source.count(find)} times")
            survivors.append(f"{rule} (bad anchor)")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(SCRIPTS, root / "scripts")
            (root / "scripts" / "writing_lint.py").write_text(source.replace(find, replace))
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "scripts/tests"],
                cwd=root, capture_output=True, text=True,
            )
        killed = result.returncode != 0
        print(f"{'killed ' if killed else 'SURVIVED'} {rule}")
        if not killed:
            survivors.append(rule)

    print(f"\n{len(MUTATIONS) - len(survivors)}/{len(MUTATIONS)} mutants killed")
    if survivors:
        print("surviving mutants (no test covers these): " + ", ".join(survivors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
