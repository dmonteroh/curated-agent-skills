"""Blind pairwise judging, per-assertion grading, and isolated case generation.

Design contract: DESIGN.md §2 T-B and §3 "judge.py". This module never imports
`vendors` or `cases` at module scope (they may not exist yet, or may be
mid-edit by a sibling worker); every function that needs them imports lazily,
so tests can inject stub modules via `sys.modules`, or pass an explicit
callable, regardless of whether the real modules are present.

Stdlib only. No network or subprocess anywhere in this file.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path
from typing import Callable, Iterable

from . import common

# ---------------------------------------------------------------------------
# Redaction (T-B guard: the judge and generator never see which side had the
# skill)
# ---------------------------------------------------------------------------

# Redaction must leave no visible trace: a bracketed marker like [REDACTED],
# or filler text that only shows up on one side, would itself unblind the
# judge (a hyphenated name inserted into filler even produced "Per the the
# guide template" -- a tell of its own, and the redacted side reading more
# "templated" was live-observed to sway a judge's verdict). So there is no
# filler at all: a flagged unit (a whole sentence, or a whole line for a
# heading/list item) is deleted outright, and everything outside a redacted
# span is preserved byte-for-byte, split and rejoined on the exact original
# separators. A text with nothing to redact round-trips unchanged.

# A line that is a markdown heading or a list item: if it names a skill, the
# whole line goes (a lone surviving "- " bullet with everything else deleted
# would itself be a tell).
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")

# Sentences announcing skill use, independent of any particular skill name:
# "I'll use the X skill", "Using the X skill", "per the X skill",
# "loading/invoking/activating ...". Matched per-unit (sentence or line) so
# the whole unit is dropped, not just the trigger phrase.
_ANNOUNCE_RE = re.compile(
    r"\b(?:use|using|load|loading|invoke|invoking|activate|activating)\b[^.!?\n]*\bskill\b"
    r"|\bper\s+the\b[^.!?\n]*\bskill\b",
    re.IGNORECASE,
)

# Vendor self-references (DESIGN.md sec2 T-B): "Claude", "Codex", "Anthropic",
# "OpenAI", "ChatGPT", and "as an AI language model/assistant". Whole-word and
# case-sensitive for the proper nouns, so lowercase common-word collisions
# ("the design draws on anthropic principles") are left alone.
_VENDOR_SELF_REF_RE = re.compile(
    r"\b(?:Claude|Codex|Anthropic|OpenAI|ChatGPT)\b"
    r"|\b[Aa]s an AI (?:language model|assistant)\b"
)

# Any absolute or relative path containing a "/": normalised to its basename
# in BOTH outputs, so a path never distinguishes the arms (DESIGN.md sec2
# T-B "symmetric path normalisation"). Requires at least one full segment
# before the final component, so it catches "skills/x/SKILL.md",
# "../wt/feat-search", and "/workspace/foo.py" without touching a bare
# filename like "app.py" (no slash -> not a path).
_PATH_RE = re.compile(r"(?<![\w./~-])(?:\.{1,2}/|~/|/)?(?:[\w.-]+/)+[\w.-]+")


def _normalize_paths(text: str) -> tuple[str, int]:
    """Replace every path-with-a-slash with its basename, symmetrically."""
    count = 0

    def _repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        return m.group(0).rstrip("/").rsplit("/", 1)[-1]

    return _PATH_RE.sub(_repl, text), count


def _contains_skill_name(unit: str, names: list[str]) -> bool:
    """True when `unit` names one of `names` as a skill (not just contains
    the word by coincidence).

    Hyphenated names (`code-review`) are matched wherever the hyphenated
    token appears, since a compound like that rarely occurs by coincidence in
    unrelated prose. Single-word names (`testing`) are common words, so they
    are matched only where an adjacent "skill" word marks them as the skill
    reference; ordinary prose using the same word survives. `plugin:<name>`
    and `skills/<name>` forms are also recognised (path forms are usually
    already stripped to a basename by `_normalize_paths` before this runs,
    but a plugin: form has no slash to normalise).
    """
    for name in names:
        esc = re.escape(name)
        if re.search(rf"\bplugin:{esc}\b", unit, re.IGNORECASE):
            return True
        if re.search(rf"skills/{esc}\b", unit, re.IGNORECASE):
            return True
        if "-" in name:
            if re.search(rf"(?<![\w-]){esc}(?![\w-])", unit, re.IGNORECASE):
                return True
        else:
            if re.search(rf"\b(?:the\s+)?{esc}\s+skill\b|\bskill\s+{esc}\b", unit, re.IGNORECASE):
                return True
    return False


def _is_flagged_unit(unit: str, names: list[str]) -> bool:
    """True when `unit` (a sentence or a whole heading/list line) names a
    skill, announces skill use, or self-references the judge's own vendor."""
    return (
        _contains_skill_name(unit, names)
        or bool(_ANNOUNCE_RE.search(unit))
        or bool(_VENDOR_SELF_REF_RE.search(unit))
    )


def _split_sentence_spans(line: str) -> list[tuple[int, int]]:
    """Split `line` into (start, end) spans whose text, concatenated in
    order, reconstructs `line` exactly. A span ends after sentence-final
    punctuation plus any following whitespace (so the space between two kept
    sentences is preserved with whichever sentence it trails), or at the end
    of the line."""
    spans = []
    start = 0
    for m in re.finditer(r"[.!?]+(?:\s+|$)", line):
        spans.append((start, m.end()))
        start = m.end()
    if start < len(line):
        spans.append((start, len(line)))
    return spans


def _is_blank_line_part(part: str) -> bool:
    return part.strip() == ""


def _strip_introduced_blank_edges(out_parts: list[str]) -> None:
    """Drop leading/trailing blank-line parts left behind by a deletion
    (minor finding: a deleted heading or opening sentence can leave a bare
    blank line at the very start or end, a small asymmetry between two
    outputs that would otherwise be identical apart from which one had
    something to redact). Mutates `out_parts` in place; callers only invoke
    this when `count > 0`, so a text with nothing flagged never has its
    original leading/trailing blank lines touched."""
    while out_parts and _is_blank_line_part(out_parts[0]):
        out_parts.pop(0)
    while out_parts and _is_blank_line_part(out_parts[-1]):
        out_parts.pop()


def _delete_flagged_units(text: str, names: list[str]) -> tuple[str, int]:
    """Delete whole flagged sentences (ordinary text) or whole flagged lines
    (headings, list items), keeping every other byte of `text` exactly as
    it was. `text.splitlines(keepends=True)` plus `_split_sentence_spans`
    guarantee that when nothing is flagged, the rejoined output is identical
    to the input, since every kept span is a verbatim slice of the original,
    concatenated in original order with nothing inserted.

    When something IS flagged and deleted, a leading or trailing blank line
    the deletion left behind is also stripped (minor finding), since that
    blank line is an artifact of the deletion, not content of the original.
    A text with nothing to redact is returned untouched (`count == 0`), so
    its own leading/trailing blank lines, if any, are never disturbed."""
    count = 0
    out_parts: list[str] = []
    for line in text.splitlines(keepends=True):
        if _HEADING_RE.match(line) or _LIST_ITEM_RE.match(line):
            if _is_flagged_unit(line, names):
                count += 1
                continue
            out_parts.append(line)
            continue
        kept: list[str] = []
        for start, end in _split_sentence_spans(line):
            piece = line[start:end]
            if _is_flagged_unit(piece, names):
                count += 1
            else:
                kept.append(piece)
        out_parts.append("".join(kept))
    if count:
        _strip_introduced_blank_edges(out_parts)
    return "".join(out_parts), count


def redact(text: str, skill_names: Iterable[str]) -> tuple[str, int]:
    """Redact `text` so a blind judge sees no sign of which arm had the
    skill:

    1. Every path containing a "/" is normalised to its basename, in both
       outputs unconditionally, so a path alone never distinguishes them.
    2. Every sentence (or, for a markdown heading/list line, the whole line)
       that names one of `skill_names`, announces skill use, or
       self-references the judge's own vendor (Claude/Codex/Anthropic/
       OpenAI/ChatGPT/"as an AI language model...") is deleted outright.

    Nothing is inserted in its place: text outside a redacted span is
    preserved exactly, so an input with nothing to redact round-trips
    byte-identical, and there is no filler phrase whose mere presence could
    itself unblind the judge.
    """
    # Flag-and-delete runs BEFORE path normalisation, against the
    # unnormalised text: a sentence like "See skills/pr-description/
    # SKILL.md for the template I'm following." names the skill only through
    # its path. Normalising paths first would strip "pr-description" down to
    # "SKILL.md" before the skill-name check ever saw it, leaving the
    # surrounding meta-commentary ("...for the template I'm following")
    # untouched -- live-observed to read as a tell ("Option 1 ... delegates
    # to an external template"). Checking the raw text first, then
    # normalising whatever survives, catches the sentence as flagged and
    # drops it whole.
    names = sorted({n for n in skill_names if n}, key=len, reverse=True)
    text, n_units = _delete_flagged_units(text, names)
    text, n_paths = _normalize_paths(text)
    return text, n_units + n_paths


def _default_skill_names() -> tuple[str, ...]:
    """Every library skill name, plus the vendor's built-in baseline names.

    Used only by the CLI commands, so redaction runs by default over the
    whole library even when the operator names nothing explicit. `vendors`
    may not expose a built-in name list yet (or may be mid-edit), so its
    absence is not an error: it just means no built-in names are added.
    """
    names = set(common.library_skills())
    try:
        from . import vendors
    except ImportError:
        vendors = None
    if vendors is not None:
        builtins = getattr(vendors, "KNOWN_BUILTINS", None)
        if builtins:
            names.update(builtins)
    return tuple(sorted(names))


# ---------------------------------------------------------------------------
# Pairwise blind judging
# ---------------------------------------------------------------------------

# NOTE: these template constants are asserted, verbatim, to be free of the
# words "skill", "arm", "treatment", "control", "baseline" (see
# test_skill_eval_judge.py::test_forbidden_words_absent_from_templates).
PAIRWISE_PROMPT_TEMPLATE = """You are comparing two responses to the same task. Read the task and both responses below, then decide which response better accomplishes the task.

Task:
{prompt}

Option 1:
{option_1}

Option 2:
{option_2}

Respond with strict JSON only, matching this shape:
{{"winner": "1" | "2" | "tie", "reason": "<one sentence>"}}

Choose "tie" only when the two responses are truly equivalent in quality."""

PAIRWISE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "winner": {"type": "string", "enum": ["1", "2", "tie"]},
        "reason": {"type": "string"},
    },
    "required": ["winner", "reason"],
    "additionalProperties": False,
}


def _complete_kwargs(complete: Callable, *, model: str | None, label: str,
                     json_schema: dict, effort: str) -> dict:
    """Build the kwargs for a `complete()` call.

    `vendors.complete()` now takes `effort: str = "medium"` (confirmed
    against the live signature), so `effort` is forwarded unconditionally
    like every other keyword here. Kept as a small helper (rather than
    inlining `{"json_schema": ..., "label": ..., "effort": ...}` at each of
    the four call sites) only to keep `model` optional in one place: passing
    `model=None` explicitly is fine for `vendors.complete` itself, but a
    test stub written before this change may still take a plain
    `model: str | None = None` default and not care either way, so leaving
    `model` out when it's None costs nothing and avoids relying on every
    stub accepting an explicit None.
    """
    kwargs: dict = {"json_schema": json_schema, "label": label, "effort": effort}
    if model is not None:
        kwargs["model"] = model
    return kwargs


def _presentation_orders(repeats: int, rng: random.Random) -> list[str]:
    """Which side ("ab" / "ba") is shown first, shuffled per pair.

    Repeats are grouped into consecutive pairs; within each pair both orders
    are always present (so a flip can still be detected), but which one comes
    first is randomised rather than always starting with "ab". A trailing,
    unpaired repeat (odd `repeats`) gets a random order of its own.
    """
    orders: list[str] = []
    i = 0
    while i < repeats:
        if i + 1 < repeats:
            pair = ["ab", "ba"]
            rng.shuffle(pair)
            orders.extend(pair)
            i += 2
        else:
            orders.append(rng.choice(["ab", "ba"]))
            i += 1
    return orders


def pairwise(prompt: str, out_a: str, out_b: str, *, judge_vendor: str, repeats: int = 2,
            skill_names: Iterable[str] = (), run_dir: Path | None = None,
            complete: Callable | None = None, seed: int | None = None,
            judge_model: str | None = None, effort: str = "medium") -> dict:
    """Blind pairwise comparison of two outputs.

    Both outputs are redacted, then presented under opaque labels ("1"/"2").
    Presentation order is shuffled per pair of repeats with `random.Random`,
    and the seed used is recorded in `run_dir/arm-map.json` so a run is
    reproducible without ever exposing the arm map itself. Each repeat's
    verdict is mapped back to "a"/"b"/"tie" through an arm map that is
    written only to `run_dir/arm-map.json`, never returned or embedded in the
    result besides the already-mapped per-repeat outcome.

    Repeats are paired by consecutive, differently-ordered calls. A verdict
    that flips between the two presentation orders of a pair counts as a tie
    for that pair. A repeat that has no valid partner (its pair-mate is void,
    or it is a trailing unpaired repeat) counts as void on its own too: a
    lone repeat can't show whether the judge flips with order, so it can't be
    trusted alone. The final verdict needs at least one complete, valid pair;
    with none, the verdict is "void". Any call whose trace shows tool use or
    a failure is void and excluded from the tally.
    """
    if complete is None:
        from . import vendors
        complete = vendors.complete

    if seed is None:
        seed = random.SystemRandom().randrange(2**32)
    rng = random.Random(seed)
    orders = _presentation_orders(repeats, rng)

    redacted_a, red_count_a = redact(out_a, skill_names)
    redacted_b, red_count_b = redact(out_b, skill_names)

    repeats_out: list[dict] = []
    arm_map_entries: list[dict] = []

    for i in range(repeats):
        order = orders[i]
        if order == "ab":
            option_1, option_2 = redacted_a, redacted_b
            label_1, label_2 = "a", "b"
        else:
            option_1, option_2 = redacted_b, redacted_a
            label_1, label_2 = "b", "a"

        judge_prompt = PAIRWISE_PROMPT_TEMPLATE.format(prompt=prompt, option_1=option_1, option_2=option_2)
        call_kwargs = _complete_kwargs(complete, model=judge_model, label=f"pairwise-{i}",
                                       json_schema=PAIRWISE_JSON_SCHEMA, effort=effort)
        text, trace = complete(judge_vendor, judge_prompt, **call_kwargs)

        void = (not trace.ok) or (trace.tool_calls > 0)
        raw_winner = None
        mapped = None
        reason = ""
        if not void:
            try:
                data = json.loads(text)
                raw_winner = data.get("winner")
                reason = data.get("reason", "")
            except (json.JSONDecodeError, AttributeError, TypeError):
                void = True

        if not void:
            if raw_winner == "1":
                mapped = label_1
            elif raw_winner == "2":
                mapped = label_2
            elif raw_winner == "tie":
                mapped = "tie"
            else:
                void = True

        repeats_out.append({
            "index": i, "order": order, "void": void,
            "raw_winner": raw_winner, "result": mapped, "reason": reason,
        })
        arm_map_entries.append({"index": i, "order": order, "label_1": label_1, "label_2": label_2})

    # Pair consecutive, differently-ordered, valid repeats to detect flips.
    # An unpaired repeat (its partner is void, missing, or shares its order)
    # counts as void rather than being tallied alone.
    flips = 0
    tallied: list[str] = []
    i = 0
    while i < len(repeats_out):
        r1 = repeats_out[i]
        r2 = repeats_out[i + 1] if i + 1 < len(repeats_out) else None
        paired = r2 is not None and not r1["void"] and not r2["void"] and r1["order"] != r2["order"]
        if paired:
            if r1["result"] != r2["result"]:
                flips += 1
                tallied.append("tie")
            else:
                tallied.append(r1["result"])
            i += 2
        else:
            i += 1

    if tallied:
        counts = {"a": tallied.count("a"), "b": tallied.count("b"), "tie": tallied.count("tie")}
        top = max(counts.values())
        winners = [k for k, v in counts.items() if v == top]
        verdict = winners[0] if len(winners) == 1 else "tie"
    else:
        verdict = "void"

    valid = [r for r in repeats_out if not r["void"]]
    decisive = [r for r in valid if r["raw_winner"] in ("1", "2")]
    position_bias = (
        sum(1 for r in decisive if r["raw_winner"] == "1") / len(decisive) if decisive else None
    )

    result = {
        "verdict": verdict,
        "repeats": repeats_out,
        "flips": flips,
        "position_bias": position_bias,
        "redaction_counts": {"a": red_count_a, "b": red_count_b},
        # DESIGN.md sec2 T-B: a redaction-count mismatch between the two
        # outputs is itself a possible tell (one side had more to redact),
        # so it's surfaced rather than silently absorbed into the blind
        # comparison.
        "redaction_asymmetry": red_count_a != red_count_b,
        # I11: pairwise.json must record which judge produced the verdict --
        # vendor, model, and effort -- not just the verdict itself.
        "judge": {"vendor": judge_vendor, "model": judge_model, "effort": effort},
    }

    if run_dir is not None:
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "arm-map.json").write_text(
            json.dumps({"seed": seed, "repeats": arm_map_entries}, indent=2), encoding="utf-8"
        )

    return result


# ---------------------------------------------------------------------------
# Per-assertion grading with mechanically checked quotations
# ---------------------------------------------------------------------------

GRADE_PROMPT_TEMPLATE = """You are checking whether a piece of output satisfies a specific requirement.

Task:
{prompt}

Output:
{output}

Requirement:
{assertion_text}

Decide whether the output satisfies the requirement. Respond with strict JSON only:
{{"verdict": "pass" | "fail", "quote": "<exact substring copied from the output>", "reason": "<one sentence>"}}

The quote must be copied exactly from the output text above, character for character. Do not paraphrase it. It must be at least three content words or fifteen characters long. If the verdict is "fail", the quote must show what the output did instead of satisfying the requirement; if the output contains nothing relevant to quote, set "quote" to the literal text NO RELEVANT CONTENT instead of copying something unrelated."""

GRADE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fail"]},
        "quote": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "quote", "reason"],
    "additionalProperties": False,
}

_QUOTE_CHAR_MAP = {
    "‘": "'", "’": "'", "“": '"', "”": '"', "′": "'", "″": '"',
}

# Chosen defaults (DESIGN.md §2 T-B): a quotation must be at least 3 content
# words OR 15 characters -- either is enough on its own -- so a one-word or
# one-character "quote" ("a") never passes as supporting evidence.
_MIN_QUOTE_CONTENT_WORDS = 3
_MIN_QUOTE_CHARS = 15

# The judge's explicit way to say a "fail" has nothing to quote, instead of
# copying unrelated text and having it rejected as unsupported.
NO_RELEVANT_CONTENT = "NO RELEVANT CONTENT"


def _normalize_quote_text(s: str) -> str:
    for a, b in _QUOTE_CHAR_MAP.items():
        s = s.replace(a, b)
    return " ".join(s.split()).strip()


def quote_supported(quote: str, output: str) -> bool:
    """True when `quote` is a substring of `output` after normalising
    whitespace and quote characters, and is long enough to mean anything: at
    least 3 content words or 15 characters. An empty quote is never
    supported."""
    q = _normalize_quote_text(quote)
    if not q:
        return False
    long_enough = len(common.content_words(q)) >= _MIN_QUOTE_CONTENT_WORDS or len(q) >= _MIN_QUOTE_CHARS
    if not long_enough:
        return False
    return q in _normalize_quote_text(output)


def _checked_verdict(raw_verdict, quote: str, redacted_output: str) -> str:
    """`pass` needs a supported quotation. `fail` needs one too, or the literal
    NO RELEVANT CONTENT. Anything else is `unsupported`, never a clean result."""
    if raw_verdict == "pass":
        return "pass" if quote_supported(quote, redacted_output) else "unsupported"
    if raw_verdict == "fail":
        if quote.strip() == NO_RELEVANT_CONTENT or quote_supported(quote, redacted_output):
            return "fail"
    return "unsupported"


def _assertion_fields(assertion) -> tuple[str, str]:
    if isinstance(assertion, dict):
        return assertion.get("id", ""), assertion.get("text", "")
    return getattr(assertion, "id", ""), getattr(assertion, "text", "")


def grade(prompt: str, output: str, assertions: list, *, judge_vendor: str,
         skill_names: Iterable[str] = (), complete: Callable | None = None,
         judge_model: str | None = None, effort: str = "medium") -> list[dict]:
    """Grade `output` against each assertion. Never returns `pass` for a
    quotation that isn't actually in the (redacted) output, and never
    returns `fail` unless it is backed by a supported quotation of what the
    output did instead, or the judge's literal NO RELEVANT CONTENT."""
    if complete is None:
        from . import vendors
        complete = vendors.complete

    redacted_output, _ = redact(output, skill_names)
    results: list[dict] = []

    for assertion in assertions:
        a_id, a_text = _assertion_fields(assertion)
        judge_prompt = GRADE_PROMPT_TEMPLATE.format(prompt=prompt, output=redacted_output,
                                                     assertion_text=a_text)
        call_kwargs = _complete_kwargs(complete, model=judge_model, label=f"grade-{a_id}",
                                       json_schema=GRADE_JSON_SCHEMA, effort=effort)
        text, trace = complete(judge_vendor, judge_prompt, **call_kwargs)

        void = (not trace.ok) or (trace.tool_calls > 0)
        verdict, quote, reason = "unsupported", "", ""
        if void:
            reason = "void: judge call used tools or the call failed"
        else:
            try:
                data = json.loads(text)
                raw_verdict = data.get("verdict")
                quote = data.get("quote") or ""
                reason = data.get("reason", "")
            except (json.JSONDecodeError, AttributeError, TypeError):
                raw_verdict = None

            verdict = _checked_verdict(raw_verdict, quote, redacted_output)

        results.append({"id": a_id, "verdict": verdict, "quote": quote, "reason": reason})

    return results


# ---------------------------------------------------------------------------
# Batched grading: every requirement for both outputs, plus the preference,
# in one call per presentation order
# ---------------------------------------------------------------------------

COMPARE_GRADE_PROMPT_TEMPLATE = """You are checking two responses to the same task against a list of requirements, then comparing them.

Task:
{prompt}

Option 1:
{option_1}

Option 2:
{option_2}

Requirements:
{requirements}

For each option, grade every requirement by its id: "pass" when the option satisfies it, "fail" when it does not. Each grade carries a quote copied exactly from that option's own text, character for character, at least three content words or fifteen characters long. Do not paraphrase it. For "fail", the quote shows what the option did instead; if the option contains nothing relevant to quote, set the quote to the literal text NO RELEVANT CONTENT. Then decide which response better accomplishes the task overall.

Respond with strict JSON only, matching this shape:
{{"option_1": [{{"id": "<requirement id>", "verdict": "pass" | "fail", "quote": "<exact substring of option 1>", "reason": "<one sentence>"}}], "option_2": [<the same shape, quoting option 2>], "winner": "1" | "2" | "tie", "reason": "<one sentence>"}}

Choose "tie" only when the two responses are truly equivalent in quality."""

_REQUIREMENT_GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "verdict": {"type": "string", "enum": ["pass", "fail"]},
        "quote": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["id", "verdict", "quote", "reason"],
    "additionalProperties": False,
}

COMPARE_GRADE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "option_1": {"type": "array", "items": _REQUIREMENT_GRADE_SCHEMA},
        "option_2": {"type": "array", "items": _REQUIREMENT_GRADE_SCHEMA},
        "winner": {"type": "string", "enum": ["1", "2", "tie"]},
        "reason": {"type": "string"},
    },
    "required": ["option_1", "option_2", "winner", "reason"],
    "additionalProperties": False,
}


def compare_and_grade(prompt: str, out_a: str, out_b: str, requirements: list, *,
                      judge_vendor: str, skill_names: Iterable[str] = (),
                      complete: Callable | None = None, seed: int | None = None,
                      run_dir: Path | None = None, judge_model: str | None = None,
                      effort: str = "medium") -> dict:
    """Grade both outputs against every requirement and compare them, in two
    calls: one per presentation order. `grade()` plus `pairwise()` cost two
    calls per requirement per output plus two. This costs two in total.

    A requirement's grade for one output counts only when both orders agree
    on it after the mechanical quote check. Disagreement is position bias
    and makes the grade `unsupported`, the same way an order flip makes a
    pairwise verdict a tie. A void call (tools used, call failed, bad JSON)
    makes every grade `unsupported` and the comparison `void`.

    Returns {"grades": {"a": [...], "b": [...]}, "comparison": {...}}. The
    comparison has the shape `pairwise()` returns, so reports and
    `rejudge` read it the same way."""
    if complete is None:
        from . import vendors
        complete = vendors.complete
    if seed is None:
        seed = random.SystemRandom().randrange(2**32)
    rng = random.Random(seed)
    orders = ["ab", "ba"]
    rng.shuffle(orders)
    redacted = {}
    counts = {}
    redacted["a"], counts["a"] = redact(out_a, skill_names)
    redacted["b"], counts["b"] = redact(out_b, skill_names)
    reqs = [_assertion_fields(r) for r in requirements]
    listing = "\n".join(f"- {rid}: {text}" for rid, text in reqs) or "- (none)"

    per_order: list[dict] = []
    for i, order in enumerate(orders):
        labels = ("a", "b") if order == "ab" else ("b", "a")
        judge_prompt = COMPARE_GRADE_PROMPT_TEMPLATE.format(
            prompt=prompt, option_1=redacted[labels[0]], option_2=redacted[labels[1]], requirements=listing)
        call_kwargs = _complete_kwargs(complete, model=judge_model, label=f"compare-grade-{i}",
                                       json_schema=COMPARE_GRADE_JSON_SCHEMA, effort=effort)
        text, trace = complete(judge_vendor, judge_prompt, **call_kwargs)
        void = (not trace.ok) or (trace.tool_calls > 0)
        data = {}
        if not void:
            try:
                data = json.loads(text)
                if not isinstance(data, dict):
                    raise TypeError
            except (json.JSONDecodeError, TypeError):
                void = True
        result = {"index": i, "order": order, "void": void, "raw_winner": None, "result": None,
                  "reason": "", "grades": {"a": {}, "b": {}}}
        if not void:
            raw_winner = data.get("winner")
            mapped = {"1": labels[0], "2": labels[1], "tie": "tie"}.get(raw_winner)
            if mapped is None:
                result["void"] = True
            else:
                result.update(raw_winner=raw_winner, result=mapped, reason=data.get("reason", ""))
                for slot, label in (("option_1", labels[0]), ("option_2", labels[1])):
                    rows = data.get(slot) if isinstance(data.get(slot), list) else []
                    for row in rows:
                        if not isinstance(row, dict) or row.get("id") in result["grades"][label]:
                            continue
                        quote = row.get("quote") or ""
                        result["grades"][label][row.get("id")] = {
                            "verdict": _checked_verdict(row.get("verdict"), quote, redacted[label]),
                            "quote": quote, "reason": row.get("reason", "")}
        per_order.append(result)

    grades = {"a": [], "b": []}
    for label in ("a", "b"):
        for rid, _ in reqs:
            seen = [o["grades"][label].get(rid) for o in per_order]
            if any(o["void"] for o in per_order) or any(g is None for g in seen):
                verdict, reason = "unsupported", "void or missing in a presentation order"
            elif seen[0]["verdict"] != seen[1]["verdict"]:
                verdict, reason = "unsupported", "order-dependent: the two presentation orders disagree"
            else:
                verdict, reason = seen[0]["verdict"], seen[0]["reason"]
            first = next((g for g in seen if g), {})
            grades[label].append({"id": rid, "verdict": verdict, "quote": first.get("quote", ""),
                                  "reason": reason, "by_order": [g["verdict"] if g else None for g in seen]})

    valid = [o for o in per_order if not o["void"]]
    flips = 0
    if len(valid) == 2:
        if valid[0]["result"] != valid[1]["result"]:
            flips, verdict = 1, "tie"
        else:
            verdict = valid[0]["result"]
    else:
        verdict = "void"
    decisive = [o for o in valid if o["raw_winner"] in ("1", "2")]
    comparison = {
        "verdict": verdict,
        "repeats": [{k: o[k] for k in ("index", "order", "void", "raw_winner", "result", "reason")}
                    for o in per_order],
        "flips": flips,
        "position_bias": (sum(o["raw_winner"] == "1" for o in decisive) / len(decisive)) if decisive else None,
        "redaction_counts": counts,
        "redaction_asymmetry": counts["a"] != counts["b"],
        "judge": {"vendor": judge_vendor, "model": judge_model, "effort": effort},
        "grading": "batched",
    }
    if run_dir is not None:
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "arm-map.json").write_text(json.dumps({"seed": seed, "repeats": [
            {"index": i, "order": o, "label_1": o[0], "label_2": o[1]} for i, o in enumerate(orders)]},
            indent=2), encoding="utf-8")
    return {"grades": grades, "comparison": comparison}


# ---------------------------------------------------------------------------
# Isolated generation: paraphrases and new candidate cases
# ---------------------------------------------------------------------------

PARAPHRASE_PROMPT_TEMPLATE = """Rewrite the request below in {k} different ways. Keep the same meaning and intent, but vary the wording, sentence structure, and phrasing substantially. Each rewrite should read like a natural, realistic request a person might type.

Request:
{prompt}

Respond with strict JSON only:
{{"paraphrases": ["<rewrite 1>", "<rewrite 2>"]}}"""

PARAPHRASE_JSON_SCHEMA = {
    "type": "object",
    "properties": {"paraphrases": {"type": "array", "items": {"type": "string"}}},
    "required": ["paraphrases"],
    "additionalProperties": False,
}

CASES_PROMPT_TEMPLATE = """Write realistic user requests related to the following task.

Task:
{job}

Write {n_pos} requests that clearly call for this task to be done. Write {n_neg} requests about a related but different task, which should not be treated as this task. Write {n_near_miss} requests that sound superficially similar but are near-misses that should also not be treated as this task. Write {n_off_register} requests that clearly call for this task but are typed the way people type into a chat box in a hurry: a few words, all lowercase, no punctuation.

Respond with strict JSON only:
{{"positive": ["..."], "negative": ["..."], "near_miss": ["..."], "off_register": ["..."]}}"""

CASES_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "positive": {"type": "array", "items": {"type": "string"}},
        "negative": {"type": "array", "items": {"type": "string"}},
        "near_miss": {"type": "array", "items": {"type": "string"}},
        "off_register": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["positive", "negative", "near_miss", "off_register"],
    "additionalProperties": False,
}

# Chosen default, used only when the cases module doesn't expose its own
# threshold. Mirrors DESIGN.md's cases.py lint rule: a positive sharing a run
# of 4 or more content words with the description is high echo.
DEFAULT_ECHO_RUN_THRESHOLD = 4


def _echo_threshold(cases_mod) -> int:
    for attr in ("ECHO_RUN_THRESHOLD", "HIGH_ECHO_RUN_THRESHOLD", "LONGEST_ECHO_THRESHOLD", "HIGH_ECHO_RUN"):
        val = getattr(cases_mod, attr, None)
        if isinstance(val, int):
            return val
    return DEFAULT_ECHO_RUN_THRESHOLD


def _case_field(case, name, default=None):
    if isinstance(case, dict):
        return case.get(name, default)
    return getattr(case, name, default)


def _failed_call_row(trace, **extra) -> dict:
    # `error` may be supplied explicitly (e.g. a JSON parse error, where the
    # call itself succeeded but its output was unusable) or fall back to
    # `record.error` (a call that failed outright); either way it must land
    # in the row instead of being dropped.
    error = extra.pop("error", None) or getattr(trace, "error", "") or ""
    row = {
        "status": "failed",
        "reason": f"generator call failed: ok={trace.ok} tool_calls={trace.tool_calls}",
        "ok": trace.ok,
        "tool_calls": trace.tool_calls,
        "error": error,
    }
    row.update(extra)
    return row


def generate_paraphrases(cases: list, k: int, *, gen_vendor: str, description: str,
                         complete: Callable | None = None, echo_score: Callable | None = None,
                         longest_echo: Callable | None = None,
                         echo_threshold: int | None = None,
                         gen_model: str | None = None, effort: str = "medium") -> list[dict]:
    """Paraphrase each case's prompt through an isolated generator.

    The generator prompt carries only the existing prompt text; `description`
    is used afterwards only, to compute echo and reject high-echo candidates.
    Echo rejection applies only to positive (`expect=True`) cases: a negative
    or near-miss case is meant to sound close to the topic, so its echo is
    annotated but never used to reject it. Each row carries a `status` of
    "accepted", "rejected", or "failed" (the generator call itself did not
    return usable output; the row records why).
    """
    if complete is None:
        from . import vendors
        complete = vendors.complete
    if echo_score is None or longest_echo is None or echo_threshold is None:
        from . import cases as cases_mod
        if echo_score is None:
            echo_score = cases_mod.echo_score
        if longest_echo is None:
            longest_echo = cases_mod.longest_echo
        if echo_threshold is None:
            echo_threshold = _echo_threshold(cases_mod)

    rows: list[dict] = []

    for case in cases:
        prompt_text = _case_field(case, "prompt", "")
        case_id = _case_field(case, "id", "")
        skill = _case_field(case, "skill", "")
        expect = _case_field(case, "expect", True)

        gen_prompt = PARAPHRASE_PROMPT_TEMPLATE.format(prompt=prompt_text, k=k)
        call_kwargs = _complete_kwargs(complete, model=gen_model, label="paraphrase",
                                       json_schema=PARAPHRASE_JSON_SCHEMA, effort=effort)
        text, trace = complete(gen_vendor, gen_prompt, **call_kwargs)
        if not trace.ok or trace.tool_calls:
            rows.append(_failed_call_row(trace, skill=skill, case_id=case_id))
            continue

        try:
            data = json.loads(text)
            paraphrases = data.get("paraphrases", [])
        except (json.JSONDecodeError, AttributeError, TypeError) as exc:
            # A parse failure on a call that itself succeeded must still
            # show up as a failure, not silently yield zero paraphrases.
            rows.append(_failed_call_row(
                trace, skill=skill, case_id=case_id, error=f"JSON parse error: {exc}",
            ))
            continue

        for p in paraphrases[:k]:
            score = echo_score(p, description)
            run = longest_echo(p, description)
            row = {
                "skill": skill,
                "prompt": p,
                "expect": bool(expect),
                "tags": [f"paraphrase-of:{case_id}"],
                "echo_score": score,
                "longest_echo": run,
            }
            if expect and run >= echo_threshold:
                row["status"] = "rejected"
                row["reason"] = f"longest_echo {run} >= threshold {echo_threshold}"
            else:
                row["status"] = "accepted"
            rows.append(row)

    return rows


def generate_cases(job: str, *, gen_vendor: str, description: str, n_pos: int, n_neg: int,
                   n_near_miss: int, n_off_register: int = 0, complete: Callable | None = None,
                   echo_score: Callable | None = None, longest_echo: Callable | None = None,
                   echo_threshold: int | None = None,
                   gen_model: str | None = None, effort: str = "medium") -> list[dict]:
    """Generate new candidate cases from a one-line job statement only.

    `description` is used afterwards only, to compute echo and reject
    high-echo candidates; it is never placed in the generator prompt. Only
    the positive group is echo-rejected: negative and near-miss requests are
    meant to overlap the topic (that's the point of a near-miss), so their
    echo is annotated but never grounds a rejection. A generator call that
    fails outright yields a single `status: "failed"` row instead of an
    empty list, so the failure is visible rather than silently dropped.
    """
    if complete is None:
        from . import vendors
        complete = vendors.complete
    if echo_score is None or longest_echo is None or echo_threshold is None:
        from . import cases as cases_mod
        if echo_score is None:
            echo_score = cases_mod.echo_score
        if longest_echo is None:
            longest_echo = cases_mod.longest_echo
        if echo_threshold is None:
            echo_threshold = _echo_threshold(cases_mod)

    gen_prompt = CASES_PROMPT_TEMPLATE.format(job=job, n_pos=n_pos, n_neg=n_neg, n_near_miss=n_near_miss,
                                              n_off_register=n_off_register)
    call_kwargs = _complete_kwargs(complete, model=gen_model, label="generate-cases",
                                   json_schema=CASES_JSON_SCHEMA, effort=effort)
    text, trace = complete(gen_vendor, gen_prompt, **call_kwargs)

    if not trace.ok or trace.tool_calls:
        return [_failed_call_row(trace)]

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        # Same fix as generate_paraphrases: a parse failure on an otherwise
        # successful call must be visible, not an empty list.
        return [_failed_call_row(trace, error=f"JSON parse error: {exc}")]

    rows: list[dict] = []
    # apply_reject: only the positive group's echo is grounds for rejection;
    # negative and near_miss are supposed to brush up against the topic.
    groups = [
        ("positive", data.get("positive", []), True, ["generated"], True),
        ("negative", data.get("negative", []), False, ["generated"], False),
        ("near_miss", data.get("near_miss", []), False, ["generated", "near-miss"], False),
        ("off_register", data.get("off_register", [])[:n_off_register], True,
         ["generated", "off-register"], True),
    ]
    for group_name, prompts, expect, tags, apply_reject in groups:
        for p in prompts:
            score = echo_score(p, description)
            run = longest_echo(p, description)
            row = {
                "prompt": p,
                "expect": expect,
                "tags": list(tags),
                "echo_score": score,
                "longest_echo": run,
                "group": group_name,
            }
            if apply_reject and run >= echo_threshold:
                row["status"] = "rejected"
                row["reason"] = f"longest_echo {run} >= threshold {echo_threshold}"
            else:
                row["status"] = "accepted"
            rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# Candidate file writer
# ---------------------------------------------------------------------------


def _format_candidate(row: dict) -> str:
    prompt = row.get("prompt", "").replace("\\", "\\\\").replace('"', '\\"')
    expect = "yes" if row.get("expect", True) else "no"
    tags = row.get("tags") or []
    tag_line = f"\n  tags: [{', '.join(tags)}]" if tags else ""
    echo_bits = f"score={row.get('echo_score', 0):.3f} longest_run={row.get('longest_echo', 0)}"
    reason = row.get("reason")
    note = f" {reason}" if reason else ""
    echo_line = f"\n  <!-- echo: {echo_bits}{note} -->"
    return f'- prompt: "{prompt}"\n  expect_activate: {expect}{tag_line}{echo_line}'


def _format_rejected(row: dict) -> str:
    """Render a rejected candidate in a form `cases.load_cases` cannot parse
    as a case (I10): the parser only turns a stripped line matching
    `- prompt: ...` into a `Case`, regardless of which markdown heading it
    sits under (`## Rejected (do not use)` is not "Positive"/"Negative", but
    every rejected row still carried an explicit `expect_activate:` line, so
    the heading never mattered -- `--include-paraphrases candidates.md`
    loaded every rejected row as a live case). This line deliberately does
    not start with "- prompt:" (or even "- "), so `load_cases` skips it
    outright; verified by `test_write_candidates_round_trip_rejects_only_load_accepted`.
    """
    prompt = row.get("prompt", "")
    expect = "yes" if row.get("expect", True) else "no"
    tags = row.get("tags") or []
    tag_str = f" tags: [{', '.join(tags)}]" if tags else ""
    echo_bits = f"score={row.get('echo_score', 0):.3f} longest_run={row.get('longest_echo', 0)}"
    reason = row.get("reason")
    note = f" -- {reason}" if reason else ""
    return (
        f'REJECTED (would-be expect_activate: {expect}){tag_str} [{echo_bits}{note}]: '
        f'"{prompt}"'
    )


def _format_failed(row: dict) -> str:
    reason = row.get("reason", "unknown failure")
    case_id = row.get("case_id")
    skill = row.get("skill")
    bits = [b for b in (f"case={case_id}" if case_id else None, f"skill={skill}" if skill else None) if b]
    prefix = f"({', '.join(bits)}) " if bits else ""
    return f"- {prefix}{reason}"


def write_candidates(path: Path, skill: str, accepted: list[dict], rejected: list[dict],
                     failed: list[dict] | None = None, generator: dict | None = None) -> Path:
    """Write trigger-case-format markdown, accepted, rejected, and failed
    generator calls in separate sections. Nothing here is written into
    trigger-cases/ automatically.

    Only `## Accepted` rows use the real `- prompt: "..."` trigger-case
    shape. `## Rejected (do not use)` and `## Failed calls` are written in a
    form `cases.load_cases` cannot parse into a `Case` at all (I10): fenced
    off as a code block, and each row using `_format_rejected`/
    `_format_failed`'s non-case-shaped line, so
    `--include-paraphrases candidates.md` (which parses through the same
    `cases.load_cases`) can never load a rejected or failed row as a live
    case, whatever heading it sits under.

    `generator`, when given, is `{"vendor": ..., "model": ..., "effort":
    ...}`: the isolated generator call that produced these candidates
    (I11 -- generate outputs must record vendor/model/effort, the same as
    pairwise.json and grading.json). Written as an HTML comment, which
    `cases.load_cases` ignores (it is neither a heading nor a `- prompt:`
    line), so it never becomes a case.
    """
    path = Path(path)
    lines = [f"# Candidate Trigger Cases: {skill}", ""]
    if generator:
        lines.append(
            f"<!-- generator: vendor={generator.get('vendor', '')} "
            f"model={generator.get('model') or '(default)'} "
            f"effort={generator.get('effort', '')} -->"
        )
        lines.append("")
    lines.extend(["## Accepted", ""])
    if accepted:
        for row in accepted:
            lines.append(_format_candidate(row))
            lines.append("")
    else:
        lines.extend(["(none)", ""])

    lines.extend(["## Rejected (do not use)", "", "```text"])
    if rejected:
        for row in rejected:
            lines.append(_format_rejected(row))
    else:
        lines.append("(none)")
    lines.extend(["```", ""])

    lines.extend(["## Failed calls", "", "```text"])
    if failed:
        for row in failed:
            lines.append(_format_failed(row))
    else:
        lines.append("(none)")
    lines.extend(["```", ""])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _split_names(raw: str) -> tuple[str, ...]:
    return tuple(s.strip() for s in (raw or "").split(",") if s.strip())


def _cmd_pairwise(args) -> int:
    prompt = _read(args.prompt)
    out_a = _read(args.a)
    out_b = _read(args.b)
    # Redaction runs by default over every library skill name and the vendor
    # built-in baseline (DESIGN.md §2 T-B), unioned with any explicit names.
    skill_names = tuple(sorted(set(_split_names(args.skill_names)) | set(_default_skill_names())))

    if args.source_vendor and args.source_vendor == args.judge_vendor:
        print(
            f"warning: --judge-vendor '{args.judge_vendor}' matches --source-vendor "
            f"'{args.source_vendor}'; the judge may share the tested vendor's biases.",
            file=sys.stderr,
        )

    run_dir = common.RUNS_DIR / common.run_id("judge-pairwise")
    run_dir.mkdir(parents=True, exist_ok=True)
    result = pairwise(prompt, out_a, out_b, judge_vendor=args.judge_vendor, repeats=args.repeats,
                      skill_names=skill_names, run_dir=run_dir,
                      judge_model=args.judge_model, effort=args.effort)
    if result.get("redaction_asymmetry"):
        counts = result["redaction_counts"]
        print(
            f"warning: redaction counts differ (a={counts['a']}, b={counts['b']}); "
            "the comparison may not be blind.",
            file=sys.stderr,
        )
    out_path = run_dir / "pairwise.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(str(out_path))
    return 0


def _cmd_grade(args) -> int:
    prompt = _read(args.prompt)
    output = _read(args.output)
    skill_names = tuple(sorted(set(_split_names(args.skill_names)) | set(_default_skill_names())))

    if args.assertions:
        assertions = json.loads(_read(args.assertions))
    else:
        from . import integrity
        data = integrity.unseal(args.sealed)
        assertions = data["payload"]["assertions"]

    results = grade(prompt, output, assertions, judge_vendor=args.judge_vendor, skill_names=skill_names,
                    judge_model=args.judge_model, effort=args.effort)

    run_dir = common.RUNS_DIR / common.run_id("judge-grade")
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / "grading.json"
    # I11: grading.json must record which judge produced these verdicts --
    # vendor, model, and effort -- alongside the per-assertion results.
    payload = {
        "judge": {"vendor": args.judge_vendor, "model": args.judge_model, "effort": args.effort},
        "results": results,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(str(out_path))
    return 0


def _cmd_generate_paraphrases(args) -> int:
    from . import cases as cases_mod

    existing = cases_mod.load_cases(args.skill)
    description = common.read_frontmatter(common.skill_dir(args.skill) / "SKILL.md").get("description", "")
    rows = generate_paraphrases(existing, args.k, gen_vendor=args.gen_vendor, description=description,
                                gen_model=args.gen_model, effort=args.effort)

    accepted = [r for r in rows if r.get("status") == "accepted"]
    rejected = [r for r in rows if r.get("status") == "rejected"]
    failed = [r for r in rows if r.get("status") == "failed"]

    run_dir = common.RUNS_DIR / common.run_id("judge-generate-paraphrases")
    out_path = run_dir / "candidates.md"
    generator_meta = {"vendor": args.gen_vendor, "model": args.gen_model, "effort": args.effort}
    write_candidates(out_path, args.skill, accepted, rejected, failed, generator=generator_meta)
    if failed:
        (run_dir / "failed-calls.json").write_text(json.dumps(failed, indent=2), encoding="utf-8")
    print(str(out_path))
    return 1 if failed else 0


def _generate_for_skill(skill: str, job: str, vendors_models: list[tuple[str, str | None]],
                        args) -> list[dict]:
    """Every generator vendor's rows for one skill, each row tagged with the
    vendor that wrote it (`gen:<vendor>`): prompts a vendor wrote may suit
    that vendor's own phrasing, so the corpus keeps the provenance."""
    description = common.read_frontmatter(common.skill_dir(skill) / "SKILL.md").get("description", "")
    rows: list[dict] = []
    for vendor, model in vendors_models:
        for row in generate_cases(job, gen_vendor=vendor, description=description,
                                  n_pos=args.n_pos, n_neg=args.n_neg, n_near_miss=args.n_near_miss,
                                  n_off_register=args.n_off_register,
                                  gen_model=model, effort=args.effort):
            row["skill"] = skill
            row["gen_vendor"] = vendor
            if row.get("status") != "failed":
                row["tags"] = list(row.get("tags", [])) + [f"gen:{vendor}"]
            rows.append(row)
    return rows


def _cmd_generate_cases(args) -> int:
    import concurrent.futures

    if args.jobs:
        jobs = json.loads(Path(args.jobs).read_text(encoding="utf-8"))
        if args.skill:
            jobs = {k: v for k, v in jobs.items() if k in set(args.skill)}
    elif args.skill and args.job:
        if len(args.skill) != 1:
            print("error: --job takes exactly one --skill; use --jobs for several", file=sys.stderr)
            return 2
        jobs = {args.skill[0]: args.job}
    else:
        print("error: give --skill S --job TEXT, or --jobs FILE.json", file=sys.stderr)
        return 2
    unknown = [s for s in jobs if not (common.skill_dir(s) / "SKILL.md").exists()]
    if unknown:
        print(f"error: no such skill(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    vendors = [v.strip() for v in args.gen_vendor.split(",") if v.strip()]
    models = dict(kv.split("=", 1) for kv in (args.gen_models or "").split(",") if "=" in kv)
    if args.gen_model and len(vendors) == 1:
        models.setdefault(vendors[0], args.gen_model)
    vendors_models = [(v, models.get(v)) for v in vendors]

    run_dir = common.RUNS_DIR / common.run_id("judge-generate-cases")
    run_dir.mkdir(parents=True, exist_ok=True)
    generator_meta = {"vendor": ",".join(vendors),
                      "model": ",".join(f"{v}={m or '(default)'}" for v, m in vendors_models),
                      "effort": args.effort}
    single = len(jobs) == 1 and not args.jobs
    summary: dict[str, dict] = {}
    any_failed = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = {pool.submit(_generate_for_skill, skill, job, vendors_models, args): skill
                   for skill, job in jobs.items()}
        for fut in concurrent.futures.as_completed(futures):
            skill = futures[fut]
            try:
                rows = fut.result()
            except Exception as exc:  # noqa: BLE001 - one skill's failure is recorded, not fatal
                rows = [{"status": "failed", "reason": f"{type(exc).__name__}: {exc}", "skill": skill}]
            accepted = [r for r in rows if r.get("status") == "accepted"]
            rejected = [r for r in rows if r.get("status") == "rejected"]
            failed = [r for r in rows if r.get("status") == "failed"]
            any_failed = any_failed or bool(failed)
            out_path = run_dir / ("candidates.md" if single else f"{skill}.candidates.md")
            write_candidates(out_path, skill, accepted, rejected, failed, generator=generator_meta)
            summary[skill] = {"accepted": len(accepted), "rejected": len(rejected), "failed": len(failed),
                              "candidates": str(out_path)}
            if failed:
                name = "failed-calls.json" if single else f"{skill}.failed-calls.json"
                (run_dir / name).write_text(json.dumps(failed, indent=2), encoding="utf-8")
    (run_dir / "summary.json").write_text(json.dumps({"generator": generator_meta, "skills": summary},
                                                     indent=2, sort_keys=True), encoding="utf-8")
    if single:
        print(str(run_dir / "candidates.md"))
    else:
        print(str(run_dir))
    return 1 if any_failed else 0


def add_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "judge", help="blind pairwise judging, assertion grading, and isolated case generation"
    )
    sub = parser.add_subparsers(dest="judge_command", required=True)

    p_pair = sub.add_parser("pairwise", help="blind pairwise comparison of two outputs")
    p_pair.add_argument("--prompt", required=True, type=Path)
    p_pair.add_argument("--a", required=True, type=Path)
    p_pair.add_argument("--b", required=True, type=Path)
    p_pair.add_argument("--judge-vendor", required=True, help="no default: must be named explicitly")
    p_pair.add_argument("--judge-model", default=None, help="model passed through to the judge call")
    p_pair.add_argument("--effort", default="medium", help="reasoning effort passed through to the judge call")
    p_pair.add_argument("--source-vendor", default=None,
                        help="vendor the outputs came from; warns if it equals --judge-vendor")
    p_pair.add_argument("--repeats", type=int, default=2)
    p_pair.add_argument("--skill-names", default="",
                        help="comma-separated names to redact, in addition to the library default")
    p_pair.set_defaults(func=_cmd_pairwise)

    p_grade = sub.add_parser("grade", help="grade an output against assertions")
    p_grade.add_argument("--prompt", required=True, type=Path)
    p_grade.add_argument("--output", required=True, type=Path)
    grp = p_grade.add_mutually_exclusive_group(required=True)
    grp.add_argument("--assertions", type=Path, help="plain JSON assertions file")
    grp.add_argument("--sealed", type=Path, help="sealed assertions file (integrity.unseal)")
    p_grade.add_argument("--judge-vendor", required=True, help="no default: must be named explicitly")
    p_grade.add_argument("--judge-model", default=None, help="model passed through to the judge call")
    p_grade.add_argument("--effort", default="medium", help="reasoning effort passed through to the judge call")
    p_grade.add_argument("--skill-names", default="",
                         help="comma-separated names to redact, in addition to the library default")
    p_grade.set_defaults(func=_cmd_grade)

    p_gen = sub.add_parser("generate", help="isolated generation of paraphrases or candidate cases")
    gen_sub = p_gen.add_subparsers(dest="generate_command", required=True)

    p_para = gen_sub.add_parser("paraphrases", help="paraphrase a skill's existing trigger cases")
    p_para.add_argument("--skill", required=True)
    p_para.add_argument("--k", type=int, default=2)
    p_para.add_argument("--gen-vendor", required=True, help="no default: must be named explicitly")
    p_para.add_argument("--gen-model", default=None, help="model passed through to the generator call")
    p_para.add_argument("--effort", default="medium", help="reasoning effort passed through to the generator call")
    p_para.set_defaults(func=_cmd_generate_paraphrases)

    p_cases = gen_sub.add_parser("cases", help="generate new candidate trigger cases from a job statement")
    p_cases.add_argument("--skill", action="append", default=[],
                         help="the skill to generate for; with --jobs, limits the batch (repeatable)")
    p_cases.add_argument("--job", default=None, help="one-line job statement for a single --skill")
    p_cases.add_argument("--jobs", default=None,
                         help='JSON {"<skill>": "<one-line job>", ...}: one candidates file per skill')
    p_cases.add_argument("--n-pos", type=int, default=5)
    p_cases.add_argument("--n-neg", type=int, default=5)
    p_cases.add_argument("--n-near-miss", type=int, default=3)
    p_cases.add_argument("--n-off-register", type=int, default=0,
                         help="terse lowercase positives, tagged off-register")
    p_cases.add_argument("--gen-vendor", required=True,
                         help="no default: must be named explicitly; comma-separated for several")
    p_cases.add_argument("--gen-model", default=None, help="model passed through to the generator call")
    p_cases.add_argument("--gen-models", default=None,
                         help="per-vendor models for several generator vendors: claude=sonnet,codex=gpt-5.6-terra")
    p_cases.add_argument("--concurrency", type=int, default=4)
    p_cases.add_argument("--effort", default="medium", help="reasoning effort passed through to the generator call")
    p_cases.set_defaults(func=_cmd_generate_cases)
