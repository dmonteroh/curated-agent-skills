#!/usr/bin/env python3
"""Controlled-English linter: decides the register violations a rule can decide.

One register, no profiles. The linter reads the text alone and cannot know what
the text is for, so every rule that needed that knowledge lives in SKILL.md as
prose instead: the 20-word procedure cap, one-instruction-per-sentence, and the
reply carve-out are the LLM's to apply. The linter returns violations. The LLM
decides the edit.

Usage:
    python3 scripts/writing_lint.py [OPTIONS] PATH [PATH...]
    python3 scripts/writing_lint.py --glossary terms.json -          # read stdin

Options:
    --glossary FILE    JSON {"canonical term": ["forbidden", "alternates"]}
    --format text|json (default: text)
    --stats            print sentence-length statistics and exit 0
    --list-rules       print every rule id, severity, and fix, then exit 0

Exit codes:
    0  no blocking violations
    1  at least one blocking violation
    2  usage or read error

Requirements: Python 3.10+, standard library only. No network access.

Verify the tool itself:
    python3 -m unittest discover -s scripts/tests

A run is trustworthy only if the fixtures pass: every rule has a fixture that
fires it and the clean fixture that must stay silent.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass, field
from typing import Callable
from pathlib import Path

# --------------------------------------------------------------------------
# Caps. A chosen default with measured provenance: sentence and paragraph
# lengths were measured over eight documents this library treats as good
# writing (six shipped SKILL.md files, the review checklist, and an
# operator-approved brief). Those measured p90 sentence lengths ran 17-29
# words, p95 21-38, and paragraph p95 3-6 sentences. The soft cap sits at the
# measured p90 band and the hard cap above the measured p95, so accepted prose
# passes and an outlier is what fires.
#
# There used to be four profiles. A 97-run trace audit removed them: agents
# passed a nonexistent profile name in 15% of invocations (each one a failed
# gate and a retry), chose between two byte-identical options by coin flip,
# and never once picked the fourth. ASD-STE100's tighter 20-word procedural
# cap survives as SKILL.md rule 12, because knowing a sentence is a procedure
# step takes knowledge of the deliverable that the text alone does not carry.
# --------------------------------------------------------------------------

CAPS: dict[str, int] = {
    "sentence_hard": 35, "sentence_soft": 25, "paragraph_hard": 8, "paragraph_soft": 6,
}

# Document-level rhythm floor. Measured standard deviation of sentence length
# across the same eight documents ran 6.2-12.1 words. Below 5.0 is flatter than
# any of them, which is the cadence that reads as generated.
# Dashes. ASD-STE100 bans the semicolon and permits the em dash, so forbidding one
# is a house preference and not a rule of the standard. Shipped as an advisory
# notice: rule 7 wants asides, and a dash on its own is weak evidence of anything.
# A fork that has decided otherwise sets this to "forbid", or to "allow" to silence it.
DASH_POLICY = "warn"

HEDGE_STACK_THRESHOLD = 3
RHYTHM_SD_FLOOR = 5.0
RHYTHM_MIN_SENTENCES = 15

PHRASAL_VERBS = [
    "spin up", "spins up", "spun up", "spinning up",
    "kick off", "kicks off", "kicked off", "kicking off",
    "dive into", "dives into", "diving into", "dove into",
    "reach out", "reaches out", "reached out", "reaching out",
    "circle back", "circles back", "circled back", "circling back",
    "drill down", "drills down", "drilling down",
    "touch base", "loop in", "loops in", "looped in", "looping in",
    "double down", "doubles down", "doubled down",
    "level up", "levels up", "levelled up", "leveled up",
]

HYPE_BLOCKING = [
    "seamless", "seamlessly", "cutting-edge", "cutting edge", "best-in-class",
    "world-class", "state-of-the-art", "blazing fast", "blazingly fast",
    "effortless", "effortlessly", "game-changing", "game changer",
    "unparalleled", "industry-leading", "best-of-breed", "turnkey",
    "frictionless", "supercharge", "supercharged", "supercharges",
    "next-generation", "paradigm shift", "revolutionize", "revolutionizes",
    "revolutionized", "revolutionary", "synergy", "synergies",
    "move the needle", "delve", "delves", "delved", "tapestry",
]

# The post-2023 abstract register, in two bands, after conorbronsdon/avoid-ai-writing
# (MIT) which tiers its vocabulary by false-positive risk. That source is explicit
# that the "appears 5-20x more often in machine text" claim behind its tier 1 is
# inherited from brandonwise/humanizer and unmeasured, so no frequency claim is
# carried here: these are authored lists, advisory only.
#
# Band one fires per hit. Each is a metaphor or an inflation with little honest
# literal use in this library's registers.
HYPE_ADVISORY = [
    "robust", "powerful", "comprehensive", "innovative", "transformative",
    "pivotal", "holistic", "underscores", "underscore", "unprecedented",
    "vibrant", "meticulous", "meticulously",
    "load-bearing", "align with", "emphasize", "emphasise", "enduring",
    "enhance", "enhances", "garner", "interplay", "intricate", "intricacies",
    "landscape", "showcase", "showcases", "showcasing", "testament",
    "valuable", "realm", "elevate", "embark", "beacon", "leverage",
    "leveraging", "leveraged", "nestled", "thriving", "bustling", "daunting",
    "ever-evolving", "actionable", "impactful", "learnings", "deep dive",
    "paradigm", "tapestry",
]

# Band two is legitimate on its own and only counts in company. Rule A20 fires
# once per paragraph when two or more DISTINCT entries appear in it. This is the
# de-slopping guard implemented rather than quoted: the evidence is the cluster.
# It also recovers words a per-hit rule cannot carry — `harness` and `navigate`
# are literal terms here, and a cluster rule never fires on one of them alone.
TIER2_CLUSTER = [
    "harness", "navigate", "navigating", "foster", "fosters", "unleash",
    "streamline", "empower", "bolster", "spearhead", "resonate", "resonates",
    "facilitate", "facilitates", "underpin", "underpins", "underpinning",
    "underpinnings", "nuanced", "crucial", "multifaceted", "ecosystem",
    "myriad", "plethora", "encompass", "encompasses", "catalyze", "reimagine",
    "galvanize", "augment", "cultivate", "illuminate", "elucidate",
    "juxtapose", "cornerstone", "paramount", "poised", "burgeoning",
    "nascent", "quintessential", "overarching",
]
TIER2_CLUSTER_MIN = 2

# "load bearing" unhyphenated is ordinary English and never matches, because the
# term itself carries the hyphen. This exempts the literal construction sense,
# optionally with one adjective between: "load-bearing structural wall".
# Abstract-capable nouns are left out on purpose, so "the load-bearing structure
# of the argument" still fires.
CONSTRUCTION_NOUNS = (
    "wall", "walls", "beam", "beams", "column", "columns", "joist", "joists",
    "truss", "trusses", "member", "members", "footing", "footings", "slab",
    "slabs", "stud", "studs", "partition", "partitions", "masonry", "lintel",
    "lintels", "pier", "piers", "rafter", "rafters", "girder", "girders",
    "capacity",
)
# Several band-one words have an honest literal sense. A hit inside one of these
# spans is skipped. Extend the table rather than dropping the word: dropping it
# loses the metaphor, which is the half worth catching.
LITERAL_SENSE = {
    "load-bearing": re.compile(
        r"load-bearing\s+(?:\w+\s+)?(?:" + "|".join(CONSTRUCTION_NOUNS) + r")\b", re.I),
    # Screen orientation, not the metaphor. "a phone held in landscape" is
    # literal. "the competitive landscape" is not.
    "landscape": re.compile(
        r"\b(?:in|to|and|or)\s+landscape\b"
        r"|\blandscape\s+(?:orientation|mode|view|layout|shape|aspect)\b"
        r"|\bportrait\s+(?:and|or)\s+landscape\b", re.I),
}

HEDGES = [
    "may", "might", "could", "possibly", "potentially", "perhaps", "somewhat",
    "fairly", "relatively", "arguably", "seemingly", "apparently", "generally",
    "typically", "usually", "often", "sometimes", "likely", "probably",
    "tends to", "tend to", "appears to", "appear to", "seems to", "seem to",
    "in some cases", "to some extent", "kind of", "sort of",
]
# approximately, roughly, and more or less are deliberately absent. They qualify
# a number's precision rather than the author's confidence, so rule 1 protects
# them: deleting one changes what the number claims. Listing them as hedges
# produced a violation with no legal exit.

FILLER_BLOCKING = [
    "in order to", "due to the fact that", "at this point in time",
    "it is important to note that", "it should be noted that",
    "it is worth noting that", "needless to say", "as a matter of fact",
    "for all intents and purposes", "in the event that", "in a timely manner",
    "at the end of the day", "in today's world", "in the world of",
]

FILLER_ADVISORY = ["in terms of", "when it comes to", "the fact that", "with regard to"]

VERBAL_TICS = [
    "great question", "excellent question", "you're absolutely right",
    "you are absolutely right", "i hope this helps", "hope this helps",
    "happy to help", "i'd be happy to", "i would be happy to", "sure thing",
    "honestly?", "to be blunt", "if i'm being honest", "if i'm being direct",
    "my honest take", "my blunt take", "my honest recommendation",
    "here's the thing", "the real question is", "at its core",
    "let's dive in", "without further ado", "short answer:", "short version:",
    "that's a great point", "let me know if", "feel free to",
]

COMPLIANCE_ANNOUNCEMENTS = [
    "to be concise", "to keep it brief", "in the interest of brevity",
    "as requested,", "per your request,", "as you asked", "i've kept this short",
    "keeping this short", "to summarize briefly", "in plain english",
]

# A verdict announced instead of shown. Distinct from hype: the claim is about
# correctness rather than quality, so no adjective list catches it.
UNEVIDENCED_VERDICT = [
    "working as designed", "working as intended", "working as expected",
    "exactly as expected", "exactly as designed", "just as we hoped",
    "does exactly what it says", "behaves as expected", "performing as expected",
    "as intended", "as designed",
]

VAGUE_ATTRIBUTION = [
    "experts say", "experts agree", "studies show", "research shows",
    "it is widely known", "it is well known", "many believe", "some argue",
    "industry reports", "observers note", "critics say", "sources say",
]

# Structural tells. Absorbed 2026-08-26 from reaktor-copywriter (hard rules and
# "What to Avoid") and prose-de-slopping's 35-pattern catalogue. De-slopping's
# guard says the evidence is the cluster and never the item, so the rules that
# cannot be stated as a fixed phrase fire once per document, not once per hit.

# writing-lint: allow L16 the rule's own example, quoted to explain the rule
# The phrase list below cannot generalise: it caught "Here's what's happening"
# and missed "Here's what's left, plainly". The shape is the tell — a sentence
# that is nothing but an announcement frame, carrying no content of its own.
# A long sentence opening the same way is fine, because it says something:
# "Here's the migration script, which drops the audit table and rebuilds it."
# Chosen default of 6 words, measured at 0 hits across 95 shipped skills.
SIGNPOST_FRAME_RE = re.compile(
    r"^(?:here'?s|here is|let me|let's|let us|now let's|what follows is|"
    r"below is|below are)\b", re.I)
SIGNPOST_MAX_WORDS = 6

SIGNPOSTING = [
    "let me break this down", "let's break this down", "here's what's happening",
    "here is what's happening", "what this means is", "the key takeaway",
    "let's unpack", "let me walk you through", "here's how it works",
    "here's what you need to know", "the bottom line is", "in a nutshell",
    "to put it simply", "simply put",
]

# L05 already carries world-class, best-in-class, industry-leading,
# state-of-the-art and unparalleled. These are the ones it does not.
UNEVIDENCED_SUPERLATIVE = [
    "premier", "market-leading", "class-leading", "award-winning", "top-tier",
    "gold standard", "a leading", "the leading", "leading provider",
    "leading platform", "trusted by",
]

COPULA_AVOIDANCE = [
    "serves as", "serve as", "functions as", "function as",
    "acts as", "act as", "boasts", "stands as",
]

# A run of three of these reads as a noun stack: "enterprise digital
# transformation enablement". Authored list, and it stays a list on purpose. A
# generalising detector was tried and measured: a run of non-function words
# carrying a nominalising suffix caught every real stack and fired on 100% of
# this library's accepted documents, 3,491 hits. Without a part-of-speech tagger
# that precision is not reachable, so the rule matches a run of words that are
# ALL in this vocabulary, which is what keeps ordinary technical compounds like
# "integration test suite" out. Measured at 0 hits across 528 accepted documents.
STACK_NOUNS = {
    "enterprise", "digital", "transformation", "enablement", "solution",
    "solutions", "platform", "framework", "frameworks", "capability",
    "capabilities", "optimization", "optimisation", "integration", "innovation",
    "strategy", "strategic", "ecosystem", "architecture", "infrastructure",
    "engagement", "alignment", "delivery", "orchestration", "modernization",
    "modernisation", "acceleration", "empowerment", "governance", "data",
    "customer", "stakeholder", "experience", "insights", "outcomes",
    "initiative", "roadmap", "vision", "mission", "excellence", "leadership",
    "monetization", "personalization", "digitalization", "value", "journey",
    "synergy", "cloud-native", "microservice", "microservices", "layer",
    "intelligence", "automation", "analytics", "scalability", "observability",
    "resilience", "productivity", "efficiency", "collaboration",
}

CONTRASTIVE_RES = (
    re.compile(r"\bnot only\b[^.!?]{1,90}?\bbut\b(?:\s+also\b)?", re.I),
    re.compile(
        r"\b(?:it|this|that|they|these|those|we|you)\s*(?:'s|’s|'re|’re| is| are)?\s*"
        r"(?:is|are)?\s*(?:not|isn't|isn’t|aren't|aren’t)\s+"
        r"(?:just |only |merely |simply |about |really )*[^.!?,;]{2,70},\s*"
        r"(?:it|this|that|they|these|those|we|you)\s*(?:'s|’s|'re|’re| is| are)\b",
        re.I,
    ),
    re.compile(r"\bnot just\b[^.!?,;]{2,70},\s*(?:but\s+|it|this|that|they|we|you)\b", re.I),
)

# Emoji: banned outright, anywhere, in every register. The sources scope their
# bans to headings, bullets, or faces, but those scopes come from marketing copy.
# This skill governs how an agent writes everywhere, so the scope is everywhere.
# Deliberately excluded: arrows (U+2190-21FF), check and ballot marks (U+2713,
# U+2717), and box drawing. All three are data markers in ordinary documents.
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF]"
    "|[\u2705\u274C\u274E\u2757\u2753\u2B50\u2B55\u26A0\u26D4\u2728\u2764]"
    "|\uFE0F"
)

# Both shapes occur in the wild: "**Label:** text" and "**Label**: text".
# A shared opening only signals a pivot when it is the subject. "The" is not.
PIVOT_SUBJECTS = {
    "it", "it's", "it’s", "this", "that", "they", "they're", "they’re",
    "we", "we're", "we’re", "you", "you're", "you’re", "these", "those",
}

BOLD_LABEL_RE = re.compile(r"^\*\*[^*]{1,40}(?:[:：]\s*\*\*|\*\*\s*[:：—-])")
# Not every trailing "-ing" clause: that shape fired on 55.8% of this library's
# own shipped skills. The tell is the pseudo-analytic verb bolted on to simulate
# depth, so the verb is the match.
PSEUDO_ANALYSIS_VERBS = (
    "underscoring", "highlighting", "showcasing", "demonstrating", "reflecting",
    "emphasizing", "emphasising", "signaling", "signalling", "cementing",
    "solidifying", "underlining", "illustrating", "showcasing", "marking",
    "paving", "reinforcing", "affirming", "exemplifying",
)
PARTICIPLE_TAIL_RE = re.compile(
    r",\s+(?:" + "|".join(PSEUDO_ANALYSIS_VERBS) + r")\b[^,]{3,}[.!?]\s*$", re.I)
FALSE_RANGE_RE = re.compile(r"\bfrom\s+([A-Za-z][\w-]*)\s+to\s+([A-Za-z][\w-]*)")
POSITIVE_CLOSE = [
    "exciting times", "bright future", "future looks bright",
    "the future is bright", "look forward to", "looking forward to",
    "the possibilities are", "endless possibilities", "watch this space",
    "stay tuned", "an exciting journey", "exciting journey",
    "this journey together", "onwards and upwards", "the sky is the limit",
    "great things ahead", "big things ahead", "the best is yet to come",
    "happy building", "happy coding", "happy hacking", "only time will tell",
    "continues to thrive", "step in the right direction", "go forth",
]

# Chosen defaults, unmeasured until the corpus pass ranks them.
BOLD_LABEL_MIN = 3           # bold-label bullets before the shape counts as a cluster
STACK_RUN_MIN = 3            # consecutive stack nouns before it counts as a stack

CONFORMANCE_CLAIM_RE = re.compile(
    r"\b(complian(?:t|ce)|complies|conforms?|conformance|in accordance)\b[^.]{0,40}?"
    r"\b(asd[- ]?ste ?100|ste[- ]?100|simplified technical english)\b",
    re.I,
)
CONFORMANCE_CLAIM_RE2 = re.compile(r"\b(ste|asd[- ]?ste ?100)[- ]complian(?:t|ce)\b", re.I)

PASSIVE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(\w+ed|born|done|made|given|taken|"
    r"shown|known|seen|written|built|held|kept|sent|found|put|drawn|thrown|chosen)\b",
    re.I,
)
COMPOUND_TENSE_RE = re.compile(r"\b(have|has|had)\s+(?:been\s+)?(\w+ed|been|done|made|gone|seen|written|taken|given|run|come|become)\b", re.I)
NOMINALIZATION_RE = re.compile(
    r"\b(perform|performs|performed|conduct|conducts|conducted|provide|provides|provided|"
    r"carry out|carries out|make|makes|made|give|gives|undertake|undertakes|achieve|achieves)\s+"
    r"(?:a|an|the)?\s*\w+(?:tion|sion|ment|ance|ence|ysis)\b",
    re.I,
)

FUNCTION_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "of", "in", "on", "at", "to", "for", "with", "from", "by",
    "as", "is", "are", "was", "were", "be", "been", "being", "it", "its", "not",
    "no", "so", "such", "when", "where", "which", "who", "whom", "will", "can",
    "may", "must", "should", "would", "could", "do", "does", "did", "has",
    "have", "had", "all", "any", "each", "every", "one", "two", "three", "into",
    "over", "under", "after", "before", "up", "down", "out", "off", "only",
}

ABBREVIATIONS = {
    "e.g.", "i.e.", "etc.", "vs.", "cf.", "approx.", "no.", "fig.", "al.",
    "dr.", "mr.", "ms.", "mrs.", "st.", "jr.", "sr.", "inc.", "ltd.", "co.",
    "ca.", "ibid.", "p.", "pp.", "vol.",
}

RULES: dict[str, tuple[str, str, str]] = {
    # id: (severity, name, fix)
    "L01": ("blocking", "sentence_over_cap", "Split the sentence. Keep every condition; do not drop a qualifier to fit."),
    "L02": ("blocking", "semicolon", "Write two sentences. ASD-STE100 rule 8.1 bans the semicolon outright."),
    "L03": ("blocking", "dash_policy", "House style forbids this dash. Use a comma, a colon, or a full stop."),
    "L04": ("blocking", "phrasal_verb", "Use the single plain verb: start, begin, read, contact, return."),
    "L05": ("blocking", "hype_adjective", "Delete it, or replace it with the measurement that earns the claim."),
    "L06": ("blocking", "hedge_stack", "Keep the one hedge that carries the author's confidence. Delete the rest. Never promote a hedge to a fact."),
    "L07": ("blocking", "filler_phrase", "Delete, or use the short form: 'to', 'because', 'now'."),
    "L08": ("blocking", "verbal_tic", "Delete. Say the thing instead of framing it."),
    "L09": ("blocking", "compliance_announcement", "Delete. Show the property; never announce compliance with an instruction."),
    "L10": ("blocking", "paragraph_over_cap", "Split the paragraph. One topic per paragraph."),
    "L12": ("blocking", "glossary_alternate", "Use the canonical term. One term, one meaning, every time."),
    "L13": ("blocking", "conformance_claim", "Remove the claim. Conformance needs the official dictionary, which this tool does not carry."),
    "L14": ("blocking", "vague_attribution", "Name the source, or delete the claim."),
    "L15": ("blocking", "contrastive_parallelism", "Rewrite without the negation pivot. State what it is; do not set up what it is not."),
    "L16": ("blocking", "signposting", "Delete. Announcing the content is not the content."),
    "L17": ("blocking", "unevidenced_superlative", "Name the measurement that earns the claim, or delete it."),
    "L20": ("blocking", "unevidenced_verdict", "Say what happened and what was checked. A verdict is not evidence for itself."),
    "L18": ("blocking", "emoji", "Delete the emoji. Say it in words."),
    "E01": ("blocking", "suppression_without_reason", "Write the reason after the rule id: <!-- writing-lint: allow L01 the condition does not survive a split -->"),
    "A01": ("advisory", "sentence_over_soft_cap", "Consider splitting. Above the measured p90 for accepted prose."),
    "A02": ("advisory", "passive_voice", "Name the actor, unless the actor is genuinely unknown or irrelevant."),
    "A03": ("advisory", "compound_tense", "Prefer the simple tense, unless the compound form carries current relevance the simple form loses."),
    "A05": ("advisory", "nominalization", "Use the verb: 'analyze the log', not 'perform an analysis of the log'."),
    "A06": ("advisory", "uniform_rhythm", "Sentence lengths are flatter than any measured sample of accepted prose. Vary them."),
    "A07": ("advisory", "repeated_opener", "Three or more consecutive sentences open with the same word."),
    "A08": ("advisory", "soft_hype", "Context-dependent hype. Keep it only if it carries information here."),
    "A09": ("advisory", "soft_filler", "Usually deletable without loss."),
    "A10": ("advisory", "dash_notice", "A dash here is a house preference, not a rule of the standard. Advisory on purpose."),
    "A11": ("advisory", "rhetorical_question_opener", "Open with the answer. A question you immediately answer asks nothing."),
    "A13": ("advisory", "bold_label_list", "Bullets shaped '- **Label:** sentence' throughout. Write prose, or drop the labels."),
    "A14": ("advisory", "copula_avoidance", "Use 'is' or 'has'."),
    "A15": ("advisory", "noun_stack", "Break the noun run with a verb or a preposition."),
    "A16": ("advisory", "participle_tail", "An '-ing' tail bolted on to a complete sentence adds no analysis. Cut it or make it a clause."),
    "A17": ("advisory", "false_range", "'from X to Y' across items that share no scale. Name them as a list."),
    "A18": ("advisory", "engagement_close", "The document ends on a question that asks nothing. End on the last fact."),
    "A20": ("advisory", "abstract_register_cluster", "Two or more words from the post-2023 abstract register in one paragraph. Each is fine alone; together they read as generated."),
    "A19": ("advisory", "positive_conclusion", "An upbeat send-off in place of a last fact. Cut it."),
}


@dataclass
class Violation:
    path: str
    line: int
    col: int
    rule: str
    span: str
    detail: str = ""

    @property
    def severity(self) -> str:
        return RULES[self.rule][0]

    @property
    def name(self) -> str:
        return RULES[self.rule][1]

    @property
    def fix(self) -> str:
        return RULES[self.rule][2]

    def as_dict(self) -> dict:
        return {
            "path": self.path, "line": self.line, "col": self.col,
            "rule": self.rule, "name": self.name, "severity": self.severity,
            "span": self.span, "detail": self.detail, "fix": self.fix,
        }


@dataclass
class Unit:
    """One linted span of prose, with a per-character map back to file position."""

    kind: str  # paragraph | list_item | heading | table_cell
    text: str
    positions: list[tuple[int, int]] = field(default_factory=list)

    def at(self, index: int) -> tuple[int, int]:
        if not self.positions:
            return (1, 1)
        index = min(index, len(self.positions) - 1)
        return self.positions[index]


# --------------------------------------------------------------------------
# Parsing: markdown in, prose units out. Everything a rewrite must never touch
# is excluded here rather than guarded rule by rule.
# --------------------------------------------------------------------------

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*)$")
LIST_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")
QUOTE_RE = re.compile(r"^\s{0,3}>")
TABLE_RE = re.compile(r"^\s*\|")
SUPPRESS_RE = re.compile(r"<!--\s*writing-lint:\s*(allow|disable-file)\s+([A-Z]\d{2})\s*(.*?)\s*-->", re.I)
# Source files carry the same directive inside an ordinary comment, with no
# HTML wrapper: `# writing-lint: allow L05 the vendor's own wording`.
SUPPRESS_PLAIN_RE = re.compile(r"writing-lint:\s*(allow|disable-file)\s+([A-Z]\d{2})[ \t]*(.*?)\s*$", re.I)


def collect_suppressions(
    lines: list[str], pattern: "re.Pattern[str]", own_line: "Callable[[str], bool]"
) -> tuple[dict[int, set[str]], set[str], list[Violation]]:
    """Suppression directives out of any file. Shared by markdown and source.

    A directive on a line of its own applies to the next content line. One
    trailing other content applies to its own line. A directive with no reason
    is itself a violation, which is what keeps a suppression readable in a diff.
    """

    per_line: dict[int, set[str]] = {}
    file_wide: set[str] = set()
    errors: list[Violation] = []
    pending: set[str] = set()

    for lineno, raw in enumerate(lines, start=1):
        matched = False
        for m in pattern.finditer(raw):
            matched = True
            kind, rule, reason = m.group(1).lower(), m.group(2).upper(), m.group(3).strip()
            if not reason:
                errors.append(Violation("", lineno, m.start() + 1, "E01", m.group(0)))
                continue
            if rule not in RULES:
                continue
            if kind == "disable-file":
                file_wide.add(rule)
            elif own_line(raw):
                pending.add(rule)
            else:
                per_line.setdefault(lineno, set()).add(rule)
        if not matched and raw.strip() and pending:
            per_line.setdefault(lineno, set()).update(pending)
            pending = set()

    return per_line, file_wide, errors


def _mask(line: str) -> str:
    """Blank out code spans, link targets, and comments. Keep every offset."""

    out = list(line)

    def blank(start: int, end: int) -> None:
        for i in range(start, min(end, len(out))):
            out[i] = " "

    for m in re.finditer(r"`[^`]*`", line):
        blank(m.start(), m.end())
    for m in re.finditer(r"\]\(([^)]*)\)", line):
        blank(m.start(), m.end())
    for m in re.finditer(r"<!--.*?-->", line):
        blank(m.start(), m.end())
    for m in re.finditer(r"https?://\S+", line):
        blank(m.start(), m.end())
    return "".join(out)


EXT_STYLE = {
    ".py": "hash", ".sh": "hash", ".bash": "hash", ".rb": "hash", ".yaml": "hash",
    ".yml": "hash", ".toml": "hash", ".tf": "hash",
    ".js": "slash", ".ts": "slash", ".tsx": "slash", ".jsx": "slash", ".go": "slash",
    ".java": "slash", ".c": "slash", ".h": "slash", ".cpp": "slash", ".rs": "slash",
    ".sql": "dash", ".lua": "dash",
}
FENCE_LANG = {
    "python": "hash", "py": "hash", "bash": "hash", "sh": "hash", "shell": "hash",
    "ruby": "hash", "yaml": "hash", "toml": "hash", "terraform": "hash",
    "javascript": "slash", "js": "slash", "typescript": "slash", "ts": "slash",
    "go": "slash", "java": "slash", "c": "slash", "cpp": "slash", "rust": "slash",
    "sql": "dash",
}
MARKERS = {"hash": ("#",), "slash": ("//",), "dash": ("--",)}
STRING_RE = re.compile(r"\'[^\']*\'|\"[^\"]*\"")
DOC_QUOTES = ('"""', "\'\'\'")


def _unit(text: str, lineno: int, col: int) -> Unit:
    body = text.strip()
    return Unit("paragraph", body, [(lineno, col + i) for i in range(len(body))])


ASSIGNED_STRING_RE = re.compile(r"=\s*[\(\[]?\s*(\"\"\"|''')")


def assigned_string_lines(lines):
    """Line numbers (1-based) inside triple-quoted strings assigned to a name.

    `CLEAN = \"\"\"...\"\"\"` is data, not a docstring, and a test file full of
    fixture documents otherwise lints its own fixtures as prose — measured at
    11 false blocking hits on this skill's own test file. A line lexer cannot
    parse Python, but an `=` before the opening quotes is decidable from the
    line alone, which is what qualifies the fix to live here.
    """

    inside: set[int] = set()
    closer = ""
    for lineno, raw in enumerate(lines, start=1):
        if closer:
            inside.add(lineno)
            if closer in raw:
                closer = ""
            continue
        m = ASSIGNED_STRING_RE.search(raw)
        if m and raw.count(m.group(1)) == 1:
            closer = m.group(1)
            inside.add(lineno)
    return inside


def extract_comments(lines, style, first_line=1):
    """Comment and docstring text from source lines, as prose units.

    String literals are blanked before the marker search, so a marker inside a
    string is not read as a comment. A marker inside a multi-line string is not
    detected, which is the known limit of a lexer this small. Triple-quoted
    strings assigned to a name are data and are skipped whole.
    """

    units = []
    in_block = False
    in_doc = ""
    markers = MARKERS.get(style, ())
    skip = assigned_string_lines(lines) if style == "hash" else set()

    for offset, raw in enumerate(lines):
        lineno = first_line + offset
        if lineno - first_line + 1 in skip:
            continue
        masked = STRING_RE.sub(lambda m: " " * len(m.group(0)), raw)

        if style == "hash":
            if in_doc:
                end = raw.find(in_doc)
                body = raw[:end] if end >= 0 else raw
                if body.strip():
                    units.append(_unit(body, lineno, len(body) - len(body.lstrip()) + 1))
                if end >= 0:
                    in_doc = ""
                continue
            opened = False
            for quote in DOC_QUOTES:
                idx = raw.find(quote)
                if idx < 0:
                    continue
                rest = raw[idx + 3:]
                close = rest.find(quote)
                body = rest[:close] if close >= 0 else rest
                if body.strip():
                    units.append(_unit(body, lineno, idx + 4 + (len(body) - len(body.lstrip()))))
                if close < 0:
                    in_doc = quote
                opened = True
                break
            if opened:
                continue

        if style == "slash":
            if in_block:
                end = raw.find("*/")
                body = (raw[:end] if end >= 0 else raw).lstrip(" \t*")
                if body.strip():
                    units.append(_unit(body, lineno, len(raw) - len(raw.lstrip()) + 1))
                if end >= 0:
                    in_block = False
                continue
            opener = masked.find("/*")
            if opener >= 0:
                rest = raw[opener + 2:]
                end = rest.find("*/")
                body = (rest[:end] if end >= 0 else rest).lstrip(" \t*")
                if body.strip():
                    units.append(_unit(body, lineno, opener + 3))
                if end < 0:
                    in_block = True
                continue

        for marker in markers:
            idx = masked.find(marker)
            if idx < 0:
                continue
            if style == "hash" and raw[idx:idx + 2] == "#!":
                break
            body = raw[idx + len(marker):]
            if body.strip():
                units.append(_unit(body, lineno, idx + len(marker) + 1))
            break

    return units


def _is_own_line_comment(style: str) -> "Callable[[str], bool]":
    """True when the whole line is a comment, so the directive covers the next line."""

    markers = tuple(MARKERS.get(style, ())) + ("*",) + DOC_QUOTES

    def check(raw: str) -> bool:
        stripped = raw.strip()
        return any(stripped.startswith(m) for m in markers)

    return check


def parse_source(text, style):
    return extract_comments(text.splitlines(), style)


def parse_fenced_comments(text):
    """Comments inside fenced code blocks of a markdown file."""

    units = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        opener = re.match(r"^\s*(?:```|~~~)\s*([A-Za-z0-9+#-]*)", lines[i])
        if not opener:
            i += 1
            continue
        style = FENCE_LANG.get(opener.group(1).lower())
        start = i + 1
        j = start
        while j < len(lines) and not FENCE_RE.match(lines[j]):
            j += 1
        if style:
            units.extend(extract_comments(lines[start:j], style, first_line=start + 1))
        i = j + 1
    return units


def parse(text: str) -> tuple[list[Unit], dict[int, set[str]], set[str], list[Violation]]:
    """Return (units, per-line suppressions, file-wide suppressions, meta errors)."""

    lines = text.splitlines()

    suppress_line, suppress_file, errors = collect_suppressions(
        lines, SUPPRESS_RE, lambda raw: raw.strip().startswith("<!--")
    )
    units: list[Unit] = []
    in_fence = False
    in_frontmatter = bool(lines) and lines[0].strip() == "---"
    para_lines: list[tuple[int, str]] = []

    def flush_paragraph() -> None:
        nonlocal para_lines
        if not para_lines:
            return
        buf, positions = [], []
        for idx, (lineno, raw) in enumerate(para_lines):
            if idx:
                buf.append(" ")
                positions.append((lineno, 1))
            masked = _mask(raw)
            stripped = masked.rstrip()
            lead = len(masked) - len(masked.lstrip())
            for col, ch in enumerate(stripped[lead:], start=lead):
                buf.append(ch)
                positions.append((lineno, col + 1))
        units.append(Unit("paragraph", "".join(buf), positions))
        para_lines = []

    for lineno, raw in enumerate(lines, start=1):
        if in_frontmatter:
            if lineno > 1 and raw.strip() == "---":
                in_frontmatter = False
            continue
        if FENCE_RE.match(raw):
            flush_paragraph()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not raw.strip():
            flush_paragraph()
            continue
        if QUOTE_RE.match(raw):  # quoted material is never linted
            flush_paragraph()
            continue
        if raw.strip().startswith("<!--"):
            continue

        heading = HEADING_RE.match(raw)
        if heading:
            flush_paragraph()
            start = raw.index(heading.group(2)) if heading.group(2) else 0
            masked = _mask(raw)[start:]
            units.append(Unit("heading", masked, [(lineno, start + i + 1) for i in range(len(masked))]))
            continue

        if TABLE_RE.match(raw):
            flush_paragraph()
            masked = _mask(raw)
            units.append(Unit("table_cell", masked, [(lineno, i + 1) for i in range(len(masked))]))
            continue

        item = LIST_RE.match(raw)
        if item:
            flush_paragraph()
            start = len(item.group(1)) + len(raw.lstrip()) - len(item.group(2))
            masked = _mask(raw)[start:]
            units.append(Unit("list_item", masked, [(lineno, start + i + 1) for i in range(len(masked))]))
            continue

        para_lines.append((lineno, raw))

    flush_paragraph()
    return units, suppress_line, suppress_file, errors


def split_sentences(text: str) -> list[tuple[int, str]]:
    """Sentence spans as (start offset, text). Abbreviations do not end a sentence."""

    spans, start, i, n = [], 0, 0, len(text)
    while i < n:
        ch = text[i]
        if ch in ".!?":
            j = i + 1
            while j < n and text[j] in "\"')]":
                j += 1
            if j >= n or text[j] in " \t":
                head = text[start:j]
                last = head.split()[-1].lower() if head.split() else ""
                digit_boundary = (
                    ch == "."
                    and i > 0 and text[i - 1].isdigit()
                    and j < n - 1 and text[j:].lstrip()[:1].isdigit()
                )
                if last not in ABBREVIATIONS and not digit_boundary:
                    spans.append((start, head.strip()))
                    while j < n and text[j] in " \t":
                        j += 1
                    start = j
                i = j
                continue
        i += 1
    if start < n and text[start:].strip():
        spans.append((start, text[start:].strip()))
    return [(s, t) for s, t in spans if t]


WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/_.\-]*")


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------


class Linter:
    def __init__(self, glossary: dict[str, list[str]]) -> None:
        self.caps = dict(CAPS)
        self.dash_policy = DASH_POLICY
        self.glossary = glossary

        def build(rule: str, base: list[str]) -> list[str]:
            return sorted(set(base), key=len, reverse=True)

        self.phrasal = build("L04", PHRASAL_VERBS)
        self.hype = build("L05", HYPE_BLOCKING)
        self.filler = build("L07", FILLER_BLOCKING)
        self.tics = build("L08", VERBAL_TICS)
        self.announce = build("L09", COMPLIANCE_ANNOUNCEMENTS)
        self.attribution = build("L14", VAGUE_ATTRIBUTION)
        self.soft_hype = build("A08", HYPE_ADVISORY)
        self.soft_filler = build("A09", FILLER_ADVISORY)
        self.hedges = build("L06", HEDGES)
        self.signposting = build("L16", SIGNPOSTING)
        self.superlative = build("L17", UNEVIDENCED_SUPERLATIVE)
        self.copula = build("A14", COPULA_AVOIDANCE)
        self.positive_close = build("A19", POSITIVE_CLOSE)
        self.tier2 = build("A20", TIER2_CLUSTER)
        self.verdict = build("L20", UNEVIDENCED_VERDICT)

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _find_terms(text: str, terms: list[str]) -> list[tuple[int, str]]:
        hits, lowered = [], text.lower()
        taken: set[int] = set()
        for term in terms:
            pattern = re.escape(term)
            if term[0].isalnum():
                pattern = r"\b" + pattern
            if term[-1].isalnum():
                pattern = pattern + r"\b"
            for m in re.finditer(pattern, lowered):
                if any(i in taken for i in range(m.start(), m.end())):
                    continue
                taken.update(range(m.start(), m.end()))
                hits.append((m.start(), text[m.start():m.end()]))
        return sorted(hits)

    def _emit(self, out: list[Violation], unit: Unit, offset: int, rule: str, span: str, detail: str = "") -> None:
        line, col = unit.at(offset)
        out.append(Violation("", line, col, rule, re.sub(r"\s+", " ", span).strip(), detail))

    # -- passes -----------------------------------------------------------

    def lint_units(self, units: list[Unit]) -> list[Violation]:
        found: list[Violation] = []
        sentence_lengths: list[int] = []

        for unit in units:
            text = unit.text
            self._word_rules(found, unit, text)

            if unit.kind in {"paragraph", "list_item"}:
                sentences = split_sentences(text)
                self._sentence_rules(found, unit, sentences, sentence_lengths)

            if unit.kind == "paragraph":
                count = len(split_sentences(text))
                if count > self.caps["paragraph_hard"]:
                    self._emit(found, unit, 0, "L10", text[:60], f"{count} sentences, cap {self.caps['paragraph_hard']}")

        self._document_rules(found, units, sentence_lengths)
        return found

    def _word_rules(self, out: list[Violation], unit: Unit, text: str) -> None:
        for offset, span in self._find_terms(text, self.phrasal):
            self._emit(out, unit, offset, "L04", span)
        for offset, span in self._find_terms(text, self.hype):
            self._emit(out, unit, offset, "L05", span)
        for offset, span in self._find_terms(text, self.filler):
            self._emit(out, unit, offset, "L07", span)
        for offset, span in self._find_terms(text, self.tics):
            self._emit(out, unit, offset, "L08", span)
        for offset, span in self._find_terms(text, self.announce):
            self._emit(out, unit, offset, "L09", span)
        for offset, span in self._find_terms(text, self.attribution):
            self._emit(out, unit, offset, "L14", span)
        literal = {term: [m.span() for m in rx.finditer(text)]
                   for term, rx in LITERAL_SENSE.items() if term in text.lower()}
        for offset, span in self._find_terms(text, self.soft_hype):
            skipped = literal.get(span.lower())
            if skipped and any(a <= offset < b for a, b in skipped):
                continue
            self._emit(out, unit, offset, "A08", span)
        for offset, span in self._find_terms(text, self.soft_filler):
            self._emit(out, unit, offset, "A09", span)

        for m in re.finditer(r";", text):
            self._emit(out, unit, m.start(), "L02", ";")

        if self.dash_policy != "allow":
            rule = "L03" if self.dash_policy == "forbid" else "A10"
            for m in re.finditer(r"—|–|(?<= )--(?= )", text):
                self._emit(out, unit, m.start(), rule, m.group(0))

        for canonical, alternates in self.glossary.items():
            for offset, span in self._find_terms(text, sorted(alternates, key=len, reverse=True)):
                self._emit(out, unit, offset, "L12", span, f"canonical term: {canonical}")

        for regex in (CONFORMANCE_CLAIM_RE, CONFORMANCE_CLAIM_RE2):
            for m in regex.finditer(text):
                self._emit(out, unit, m.start(), "L13", m.group(0))

        for offset, span in self._find_terms(text, self.signposting):
            self._emit(out, unit, offset, "L16", span)
        for offset, span in self._find_terms(text, self.superlative):
            self._emit(out, unit, offset, "L17", span)
        for offset, span in self._find_terms(text, self.verdict):
            self._emit(out, unit, offset, "L20", span)
        for offset, span in self._find_terms(text, self.copula):
            self._emit(out, unit, offset, "A14", span)

        for regex in CONTRASTIVE_RES:
            for m in regex.finditer(text):
                self._emit(out, unit, m.start(), "L15", m.group(0)[:70])

        for m in EMOJI_RE.finditer(text):
            self._emit(out, unit, m.start(), "L18", m.group(0))

        for m in FALSE_RANGE_RE.finditer(text):
            self._emit(out, unit, m.start(), "A17", m.group(0))

        words = WORD_RE.findall(text)
        run = 0
        for i, word in enumerate(words):
            if word.lower() in STACK_NOUNS:
                run += 1
                if run == STACK_RUN_MIN:
                    span = " ".join(words[i - STACK_RUN_MIN + 1:i + 1])
                    offset = text.lower().find(span.lower())
                    self._emit(out, unit, max(offset, 0), "A15", span)
            else:
                run = 0

        if unit.kind == "paragraph":
            found_t2 = self._find_terms(text, self.tier2)
            distinct = {span.lower() for _, span in found_t2}
            if len(distinct) >= TIER2_CLUSTER_MIN:
                self._emit(out, unit, found_t2[0][0], "A20", ", ".join(sorted(distinct)),
                           f"{len(distinct)} distinct in one paragraph")

        for m in PASSIVE_RE.finditer(text):
            self._emit(out, unit, m.start(), "A02", m.group(0))
        for m in COMPOUND_TENSE_RE.finditer(text):
            self._emit(out, unit, m.start(), "A03", m.group(0))
        for m in NOMINALIZATION_RE.finditer(text):
            self._emit(out, unit, m.start(), "A05", m.group(0))


    # The output contract's own trailer. It enumerates every preserved hedge,
    # number and condition, so it is an inventory rather than prose, and a
    # thorough one legitimately runs past any sentence cap. Identifiable from
    # the text alone, which is what qualifies the exemption to live here.
    KEPT_AS_IS_RE = re.compile(r"^\s*(?:\*\*)?kept as-is:", re.I)

    def _sentence_rules(
        self, out: list[Violation], unit: Unit, sentences: list[tuple[int, str]], lengths: list[int]
    ) -> None:
        kept_line = bool(self.KEPT_AS_IS_RE.match(unit.text))
        openers: list[str] = []
        for offset, sentence in sentences:
            count = word_count(sentence)
            lengths.append(count)
            if kept_line:
                pass
            elif count > self.caps["sentence_hard"]:
                self._emit(out, unit, offset, "L01", sentence[:60], f"{count} words, cap {self.caps['sentence_hard']}")
            elif count > self.caps["sentence_soft"]:
                self._emit(out, unit, offset, "A01", sentence[:60], f"{count} words, soft cap {self.caps['sentence_soft']}")

            hits = self._find_terms(sentence, self.hedges)
            distinct = {span.lower() for _, span in hits}
            # Three, not two: every prose statement of this rule says three, and
            # two distinct hedges in one sentence is ordinary careful writing.
            if len(distinct) >= HEDGE_STACK_THRESHOLD:
                self._emit(out, unit, offset, "L06", ", ".join(sorted(distinct)), f"{len(distinct)} hedges in one sentence")

            # Fires only when the phrase list did not already catch this sentence,
            # so one announcement is one violation.
            if count <= SIGNPOST_MAX_WORDS and not self._find_terms(sentence, self.signposting):
                if SIGNPOST_FRAME_RE.match(sentence.strip().lstrip("*_-# ")):
                    self._emit(out, unit, offset, "L16", sentence[:60])

            if PARTICIPLE_TAIL_RE.search(sentence):
                self._emit(out, unit, offset, "A16", sentence[-50:])

            words = WORD_RE.findall(sentence)
            openers.append(words[0].lower() if words else "")

        # A question answered by the sentence after it asked nothing.
        if unit.kind == "paragraph" and len(sentences) >= 2 and sentences[0][1].rstrip().endswith("?"):
            self._emit(out, unit, sentences[0][0], "A11", sentences[0][1][:60])

        self._contrastive_pair(out, unit, sentences)

        if unit.kind == "paragraph":
            for i in range(len(openers) - 2):
                first = openers[i]
                if first and first not in FUNCTION_WORDS and openers[i + 1] == first == openers[i + 2]:
                    self._emit(out, unit, sentences[i][0], "A07", first)
                    break

    COPULA_NEGATION_RE = re.compile(
        r"\b(?:is not|isn't|isn’t|are not|aren't|aren’t|was not|wasn't|were not|"
        r"weren't|do not|don't|does not|doesn't)\b|(?:'s|’s|'re|’re)\s+not\b", re.I)

    def _contrastive_pair(self, out: list[Violation], unit: Unit, sentences) -> None:
        # writing-lint: allow L15 the rule's own example, quoted to define the shape
        """"You're not surrounded by idiots. You're surrounded by stress."

        The same pivot as the comma-joined frames, split across a full stop.
        Kept tight on purpose: same opening word, both sentences short, a copula
        negation in the first and none in the second.
        """
        for (offset, first), (_, second) in zip(sentences, sentences[1:]):
            if not self.COPULA_NEGATION_RE.search(first):
                continue
            if self.COPULA_NEGATION_RE.search(second):
                continue
            a, b = WORD_RE.findall(first), WORD_RE.findall(second)
            if not a or not b or len(a) > 10 or len(b) > 10:
                continue
            # Two ways to be sure it is a pivot and not two ordinary sentences
            # that happen to share an article. Either the openings match once the
            # negation is removed, or the shared opening is a subject pronoun.
            stripped = [w for w in a if w.lower() not in {"not", "n't"}]
            same_frame = len(stripped) >= 2 and len(b) >= 2 and \
                [w.lower() for w in stripped[:2]] == [w.lower() for w in b[:2]]
            pronoun_subject = a[0].lower() == b[0].lower() and a[0].lower() in PIVOT_SUBJECTS
            if same_frame or pronoun_subject:
                self._emit(out, unit, offset, "L15", f"{first[:34]} / {second[:34]}")

    def _document_rules(self, out: list[Violation], units: list[Unit], lengths: list[int]) -> None:
        total_words = sum(word_count(u.text) for u in units)
        first = units[0] if units else Unit("paragraph", "", [(1, 1)])

        # Cluster rules. De-slopping's guard is that the evidence is never the
        # item, so these fire once per document rather than once per hit.
        bullets = [u for u in units if u.kind == "list_item"]
        labelled = [u for u in bullets if BOLD_LABEL_RE.match(u.text.strip())]
        if len(labelled) >= BOLD_LABEL_MIN:
            self._emit(out, labelled[0], 0, "A13", labelled[0].text[:60],
                       f"{len(labelled)} bold-label bullets")

        paragraphs = [u for u in units if u.kind == "paragraph"]
        if paragraphs:
            last = paragraphs[-1]
            tail = split_sentences(last.text)
            if tail and tail[-1][1].rstrip().endswith("?"):
                self._emit(out, last, tail[-1][0], "A18", tail[-1][1][:60])
            for offset, span in self._find_terms(last.text, self.positive_close):
                self._emit(out, last, offset, "A19", span)

        if len(lengths) >= RHYTHM_MIN_SENTENCES:
            sd = statistics.pstdev(lengths)
            if sd < RHYTHM_SD_FLOOR:
                unit = units[0] if units else Unit("paragraph", "", [(1, 1)])
                self._emit(out, unit, 0, "A06", f"sd={sd:.1f}", f"{len(lengths)} sentences, sd floor {RHYTHM_SD_FLOOR}")


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def lint_text(
    text: str, path: str, linter: Linter, *, code_comments: bool = False
) -> tuple[list[Violation], int]:
    style = EXT_STYLE.get(Path(path).suffix.lower())
    if style:
        units = parse_source(text, style)
        lines = text.splitlines()
        if style == "hash":
            # A directive inside an assigned fixture string is data, not an
            # instruction to this linter, and must not enter the suppression
            # table or fire E01.
            inside = assigned_string_lines(lines)
            lines = ["" if i + 1 in inside else l for i, l in enumerate(lines)]
        suppress_line, suppress_file, errors = collect_suppressions(
            lines, SUPPRESS_PLAIN_RE, _is_own_line_comment(style)
        )
    else:
        units, suppress_line, suppress_file, errors = parse(text)
        if code_comments:
            units = units + parse_fenced_comments(text)
    found = errors + linter.lint_units(units)
    kept = []
    for violation in found:
        violation.path = path
        if violation.rule in suppress_file:
            continue
        if violation.rule in suppress_line.get(violation.line, set()):
            continue
        kept.append(violation)
    words = sum(word_count(u.text) for u in units)
    kept.sort(key=lambda v: (v.line, v.col, v.rule))
    return kept, words


def render_text(violations: list[Violation], summary: dict) -> str:
    lines = []
    for v in violations:
        detail = f"  [{v.detail}]" if v.detail else ""
        lines.append(f"{v.path}:{v.line}:{v.col}  {v.rule}  {v.name}  \"{v.span}\"{detail}")
        lines.append(f"    fix: {v.fix}")
    lines.append(
        f"\n{summary['blocking']} blocking, {summary['advisory']} advisory over "
        f"{summary['words']} words ({summary['blocking_per_1k']} blocking per 1,000 words)."
    )
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="writing_lint", add_help=True)
    parser.add_argument("paths", nargs="*")
    # Deprecated and ignored, but still accepted: rejecting it would recreate
    # the exit-2 retry loop that profile names caused, and an agent following a
    # stale instruction must not lose its gate run to that.
    parser.add_argument("--profile", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--glossary")
    parser.add_argument("--format", default="text", choices=["text", "json"])
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--code-comments", action="store_true",
                        help="also lint comments inside fenced code blocks of a markdown file")
    parser.add_argument("--list-rules", action="store_true")
    args = parser.parse_args(argv)

    if args.profile is not None:
        print("note: --profile is deprecated and ignored; the register is one set of rules", file=sys.stderr)

    if args.list_rules:
        for rule, (severity, name, fix) in sorted(RULES.items()):
            print(f"{rule}\t{severity}\t{name}\t{fix}")
        print("suppress: <!-- writing-lint: allow L01 reason --> (own line = next line; inline = that line); "
              "<!-- writing-lint: disable-file L05 reason -->")
        return 0

    if not args.paths:
        print("error: no input paths (use - for stdin)", file=sys.stderr)
        return 2

    glossary: dict[str, list[str]] = {}
    if args.glossary:
        try:
            raw = json.loads(Path(args.glossary).read_text())
            glossary = {str(k): [str(x) for x in v] for k, v in raw.items()}
        except (OSError, ValueError, AttributeError) as exc:
            print(f"error: glossary: {exc}", file=sys.stderr)
            return 2

    linter = Linter(glossary)
    all_violations: list[Violation] = []
    total_words = 0
    all_lengths: list[int] = []

    for path in args.paths:
        try:
            text = sys.stdin.read() if path == "-" else Path(path).read_text()
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        violations, words = lint_text(
            text, "<stdin>" if path == "-" else path, linter, code_comments=args.code_comments
        )
        all_violations.extend(violations)
        total_words += words
        if args.stats:
            for unit in parse(text)[0]:
                if unit.kind in {"paragraph", "list_item"}:
                    all_lengths.extend(word_count(s) for _, s in split_sentences(unit.text))

    if args.stats:
        if not all_lengths:
            print("no sentences found")
            return 0
        ordered = sorted(all_lengths)
        pick = lambda p: ordered[min(len(ordered) - 1, round(p * (len(ordered) - 1)))]
        print(
            f"sentences={len(ordered)} mean={statistics.mean(ordered):.1f} "
            f"sd={statistics.pstdev(ordered):.1f} p50={pick(0.5)} p90={pick(0.9)} "
            f"p95={pick(0.95)} max={ordered[-1]}"
        )
        return 0

    blocking = [v for v in all_violations if v.severity == "blocking"]
    advisory = [v for v in all_violations if v.severity == "advisory"]
    summary = {
        "words": total_words,
        "blocking": len(blocking),
        "advisory": len(advisory),
        "blocking_per_1k": round(len(blocking) * 1000 / total_words, 2) if total_words else 0.0,
    }

    if args.format == "json":
        print(json.dumps({
            "version": 2,
            "summary": summary,
            "violations": [v.as_dict() for v in all_violations],
        }, indent=2))
    else:
        print(render_text(all_violations, summary))

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
