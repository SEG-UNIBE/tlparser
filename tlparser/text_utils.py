from __future__ import annotations

import re
from typing import Match

_DOT_PLACEHOLDER = "<DOT>"
_TIME_ABBREV_RE = re.compile(r"\b(?:a|p)\.m\.", re.IGNORECASE)
_MULTI_DOT_ABBREV_RE = re.compile(r"\b(?:[A-Za-z]\.){2,}")
_COMMON_ABBREV_RE = re.compile(
    r"\b(?:Mr|Mrs|Ms|Mmes|Dr|Prof|Sr|Jr|St|Mt|No|Fig|Eq|Sec|Dept|Inc|Ltd|vs|etc|cf|approx|resp|Jan|Feb|Mar|Apr|Aug|Sep|Sept|Oct|Nov|Dec)\.",
    re.IGNORECASE,
)
_NUMERIC_DOTTED_RE = re.compile(r"\b\d+(?:\.\d+)+\.?")
_SENTENCE_BOUNDARY_RE = re.compile(r"[.!?;:]+(?=(?:\s|$|[\"'\)\]]))")


def _replace_dots(match: Match[str]) -> str:
    text = match.group(0)
    if not text:
        return text

    trailing_dot = ""
    if text.endswith(".") and match.end() == len(match.string):
        trailing_dot = "."
        text = text[:-1]

    masked = text.replace(".", _DOT_PLACEHOLDER)
    return masked + trailing_dot


def _replace_time_abbrev(match: Match[str]) -> str:
    text = match.group(0)
    if not text:
        return text

    next_segment = match.string[match.end() :]
    next_char = ""
    if next_segment:
        idx = 0
        while idx < len(next_segment):
            ch = next_segment[idx]
            if ch.isspace():
                idx += 1
                continue
            if ch in {'"', "'", ")", "]"} and idx + 1 < len(next_segment):
                idx += 1
                continue
            next_char = ch
            break

    keep_trailing = match.end() == len(match.string)
    if next_char and next_char.isupper():
        keep_trailing = True

    core = text[:-1].replace(".", _DOT_PLACEHOLDER)
    return core + ("." if keep_trailing else "")


def _mask_non_sentence_dots(text: str) -> str:
    masked = _TIME_ABBREV_RE.sub(_replace_time_abbrev, text)
    masked = _MULTI_DOT_ABBREV_RE.sub(_replace_dots, masked)
    masked = _COMMON_ABBREV_RE.sub(_replace_dots, masked)
    masked = _NUMERIC_DOTTED_RE.sub(_replace_dots, masked)
    return masked


def count_sentences(text: str) -> int:
    if not text:
        return 0

    masked = _mask_non_sentence_dots(text)
    segments = []
    start = 0
    for match in _SENTENCE_BOUNDARY_RE.finditer(masked):
        end = match.end()
        segment = masked[start:end]
        if segment.strip():
            segments.append(segment)
        start = end

    if start < len(masked):
        tail = masked[start:]
        if tail.strip():
            segments.append(tail)

    eligible = 0
    for segment in segments:
        plain_segment = segment.replace(_DOT_PLACEHOLDER, ".")
        words = re.findall(r"[A-Za-z0-9']+", plain_segment)
        if len(words) >= 3:
            eligible += 1

    return eligible
