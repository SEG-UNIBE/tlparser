"""Helpers for working with logic formula normalization."""

from __future__ import annotations

import re
from typing import Dict, Tuple

_TOKEN_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"-->", re.IGNORECASE), "->"),
    (re.compile(r"\bnot\b", re.IGNORECASE), "!"),
    (re.compile(r"\band\b", re.IGNORECASE), "&"),
    (re.compile(r"\bor\b", re.IGNORECASE), "|"),
)


def normalize_formula_tokens(formula: str) -> str:
    """Return formula with lexical synonyms rewritten to Spot/PyMC conventions."""
    normalized = formula
    for pattern, replacement in _TOKEN_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
    normalized = re.sub(r"!\s+", "!", normalized)
    normalized = re.sub(r"\s*(&|\||->)\s*", r" \1 ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_comparison_ops(formula_str: str) -> tuple[Dict[str, int], str]:
    """Replace comparison operator tokens and return counts plus amended string."""
    patterns = {
        "eq": re.compile(r"=="),
        "leq": re.compile(r"<="),
        "geq": re.compile(r">="),
        "neq": re.compile(r"!="),
        "lt": re.compile(r"(?<!<)<(?![=<])"),
        "gt": re.compile(r"(?<!>)>(?![=>])"),
    }

    formula_tmp = re.sub("-->", "__IMPLIES__", formula_str)
    counts = {key: len(pattern.findall(formula_tmp)) for key, pattern in patterns.items()}

    def replace_comparisons(match: re.Match[str]) -> str:
        expression = match.group().replace(" ", "")
        expression = re.sub(r"-", "n", expression)
        if "<=" in expression:
            return expression.replace("<=", "_leq_")
        if ">=" in expression:
            return expression.replace(">=", "_geq_")
        if "==" in expression:
            return expression.replace("==", "_eq_")
        if "!=" in expression:
            return expression.replace("!=", "_neq_")
        if "<" in expression:
            return expression.replace("<", "_lt_")
        if ">" in expression:
            return expression.replace(">", "_gt_")
        return expression

    modified_string = re.sub(
        r"\b[\w.]+ *[<>!=]=? *-?\w+\b",
        replace_comparisons,
        formula_str,
    )
    modified_string = re.sub(r"(\d+(\.\d+)?)", r"n\1", modified_string)
    return counts, modified_string
