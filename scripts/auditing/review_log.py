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
    MALFORMED = "MALFORMED"
    INFRA_FAILURE = "INFRA-FAILURE"


@dataclass(frozen=True)
class Classification:
    outcome: Outcome


_RETRY_BANNER = re.compile(
    r"^stream error: unexpected status [45]\d\d\b.*; retrying \d+/\d+ in ",
    re.MULTILINE,
)
_TERMINAL_BANNER = re.compile(
    r"^ERROR: unexpected status [45]\d\d\b",
    re.MULTILINE,
)


def _is_infra_failure(log_text: str) -> bool:
    if _RETRY_BANNER.search(log_text):
        return True
    if _TERMINAL_BANNER.search(log_text):
        return True
    return False


def classify(log_text: str) -> Classification:
    if _is_infra_failure(log_text):
        return Classification(outcome=Outcome.INFRA_FAILURE)
    return Classification(outcome=Outcome.MALFORMED)
