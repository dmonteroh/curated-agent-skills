"""Classify a codex-review log's text into a discriminated outcome.

Every function here takes log text and returns a value; none touches the
filesystem, the network, or a subprocess. Importing this module has no
side effects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    NO_CHANGE = "NO-CHANGE"
    CHANGED = "CHANGED"
    QUESTIONS = "QUESTIONS"
    MALFORMED = "MALFORMED"
    INFRA_FAILURE = "INFRA-FAILURE"


@dataclass(frozen=True)
class Classification:
    outcome: Outcome
    differentiation: str | None = None
    removal_proposals: str | None = None


_RETRY_BANNER = re.compile(
    r"^stream error: unexpected status [45]\d\d\b.*; retrying \d+/\d+ in ",
    re.MULTILINE,
)
_TERMINAL_BANNER = re.compile(
    r"^ERROR: unexpected status [45]\d\d\b",
    re.MULTILINE,
)
_RAW_STATUS_LINE = re.compile(r"^REVIEW_STATUS: (NO-CHANGE|CHANGED)$", re.MULTILINE)
_RAW_QUESTIONS_LINE = re.compile(r"^QUESTIONS$", re.MULTILINE)


def _is_infra_failure(log_text: str) -> bool:
    banner_ends = [m.end() for m in _RETRY_BANNER.finditer(log_text)]
    banner_ends += [m.end() for m in _TERMINAL_BANNER.finditer(log_text)]
    if not banner_ends:
        return False
    last_banner_end = max(banner_ends)
    newline_pos = log_text.find("\n", last_banner_end)
    tail = log_text[newline_pos + 1 :] if newline_pos != -1 else ""
    if _RAW_STATUS_LINE.search(tail):
        return False
    if _RAW_QUESTIONS_LINE.search(tail):
        return False
    return True


_MARKUP_PREFIX = re.compile(r"^(?:#+\s*|[-*]\s+|\*+)")
_MARKUP_SUFFIX = re.compile(r"\*+$")


def _strip_markup(line: str) -> str:
    stripped = line.strip()
    previous = None
    while previous != stripped:
        previous = stripped
        stripped = _MARKUP_PREFIX.sub("", stripped, count=1).strip()
    return _MARKUP_SUFFIX.sub("", stripped).strip()


_LABEL_SEPARATOR = re.compile(r"^\s*:{0,2}\s*")


def _match_label(line: str, label: str) -> str | None:
    stripped = _strip_markup(line)
    folded = stripped.replace("_", " ").lower()
    if not folded.startswith(label):
        return None
    rest = stripped[len(label) :]
    m = _LABEL_SEPARATOR.match(rest)
    return rest[m.end() :] if m else rest


def _find_status(log_text: str) -> Outcome | None:
    last: Outcome | None = None
    for line in log_text.splitlines():
        rest = _match_label(line, "review status")
        if rest is None:
            continue
        verdict = rest.strip().upper()
        if verdict == "NO-CHANGE":
            last = Outcome.NO_CHANGE
        elif verdict == "CHANGED":
            last = Outcome.CHANGED
    return last


def _has_questions(log_text: str) -> bool:
    for line in log_text.splitlines():
        rest = _match_label(line, "questions")
        if rest is not None and rest.strip() == "":
            return True
    return False


_DIFFERENTIATION_VALUE = re.compile(r"^(STRONG|WEAK)\b", re.IGNORECASE)


def _find_differentiation(log_text: str) -> str | None:
    last: str | None = None
    for line in log_text.splitlines():
        rest = _match_label(line, "differentiation")
        if rest is None:
            continue
        m = _DIFFERENTIATION_VALUE.match(rest.strip())
        if m:
            last = m.group(1).upper()
    return last


def _is_terminator(line: str) -> bool:
    folded = _strip_markup(line).replace("_", " ").lower()
    return (
        folded.startswith("review status")
        or folded.startswith("differentiation")
        or folded.startswith("questions")
        or folded.startswith("verification run")
    )


def _collect_removal_blocks(log_text: str) -> tuple[bool, list[str]]:
    lines = log_text.splitlines()
    located = False
    blocks: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        rest = _match_label(lines[i], "removal proposals")
        if rest is None:
            i += 1
            continue
        located = True
        collected: list[str] = []
        first = rest.strip()
        if first:
            collected.append(first)
        i += 1
        while i < n and not _is_terminator(lines[i]) and _match_label(lines[i], "removal proposals") is None:
            piece = lines[i].strip()
            if piece:
                collected.append(piece)
            i += 1
        blocks.append(" ".join(collected))
    return located, blocks


def _collapse_repeated_tokens(tokens: list[str]) -> list[str]:
    n = len(tokens)
    for period in range(1, n):
        if n % period != 0:
            continue
        unit = tokens[:period]
        if unit * (n // period) == tokens:
            return unit
    return tokens


def _find_removal_proposals(log_text: str) -> tuple[bool, str | None]:
    located, blocks = _collect_removal_blocks(log_text)
    if not located:
        return False, None
    combined = " ".join(block for block in blocks if block)
    tokens = _collapse_repeated_tokens(combined.split())
    joined = " ".join(tokens)
    cleaned = re.sub(r"[ \t.\-]+", " ", joined).strip()
    if cleaned == "" or cleaned.lower() == "none":
        return True, None
    return True, joined


def classify(log_text: str) -> Classification:
    if _is_infra_failure(log_text):
        return Classification(outcome=Outcome.INFRA_FAILURE)

    status_outcome = _find_status(log_text)
    if status_outcome is not None:
        differentiation = _find_differentiation(log_text)
        located, proposals = _find_removal_proposals(log_text)
        if not located:
            return Classification(outcome=Outcome.MALFORMED, differentiation=differentiation)
        return Classification(
            outcome=status_outcome,
            differentiation=differentiation,
            removal_proposals=proposals,
        )

    if _has_questions(log_text):
        differentiation = _find_differentiation(log_text)
        _, proposals = _find_removal_proposals(log_text)
        return Classification(
            outcome=Outcome.QUESTIONS,
            differentiation=differentiation,
            removal_proposals=proposals,
        )

    return Classification(outcome=Outcome.MALFORMED)
