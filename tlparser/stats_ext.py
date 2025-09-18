"""Helpers for extended statistics based on Spot tooling."""

from __future__ import annotations

import re
from typing import Any, List, Optional


class SpotAnalyzer:
    """Lazily perform Spot-powered analysis and collect diagnostics."""

    def __init__(self) -> None:
        self._available: Optional[bool] = None
        self._diagnostics: List[str] = []
        self._classify = None
        self._token_patterns = (
            (re.compile(r"-->", re.IGNORECASE), "->"),
            (re.compile(r"\bnot\b", re.IGNORECASE), "!"),
            (re.compile(r"\band\b", re.IGNORECASE), "&"),
            (re.compile(r"\bor\b", re.IGNORECASE), "|"),
        )

    @property
    def diagnostics(self) -> List[str]:
        """Return accumulated warnings without exposing internal storage."""
        return list(self._diagnostics)

    def _record_warning(self, message: str) -> None:
        if message not in self._diagnostics:
            self._diagnostics.append(message)

    def _ensure_initialized(self) -> bool:
        if self._available is not None:
            return self._available

        try:
            from tlparser import spot_tools  # Local import to avoid mandatory dependency
        except Exception as exc:  # pragma: no cover - environment dependent
            self._record_warning(
                "[tlparser] Spot extensions unavailable (spot_tools import failed); "
                f"extended digest columns will be empty. Details: {exc}"
            )
            self._available = False
            return False

        classify_func = getattr(spot_tools, "classify_ltl_property", None)
        spot_status_fn = getattr(spot_tools, "spot_status", None)

        if classify_func is None or spot_status_fn is None:
            self._record_warning(
                "[tlparser] Spot extensions unavailable (missing Spot helper functions); "
                "extended digest columns will be empty."
            )
            self._available = False
            return False

        status_map = spot_status_fn()
        missing = [name for name, info in status_map.items() if not info.get("path")]

        if missing:
            missing_str = ", ".join(sorted(set(missing)))
            self._record_warning(
                "[tlparser] Spot CLI tools not found (missing: "
                f"{missing_str}); extended digest columns will be empty."
            )
            self._available = False
            return False

        self._classify = classify_func
        self._available = True
        return True

    def classify(self, formula: str) -> Optional[dict[str, Any]]:
        """Return Spot-derived statistics for the given formula if possible."""
        if not formula:
            return None

        if not self._ensure_initialized():
            return None

        assert self._classify is not None  # For type checkers
        spot_formula = self._to_spot_syntax(formula)
        try:
            result = self._classify(spot_formula)
            if isinstance(result, dict):
                original_spot = result.get("formula", spot_formula)
                result["spot_formula"] = original_spot
                result["formula"] = formula
            return result
        except FileNotFoundError:
            self._record_warning(
                "[tlparser] Required Spot CLI tool missing during classification; "
                "extended digest columns will be empty."
            )
            self._available = False
        except Exception as exc:  # pragma: no cover - external tool behaviour
            self._record_warning(
                f"[tlparser] Spot classification failed for '{formula}': {exc}; "
                "extended digest columns will be empty for this formula."
            )
        return None

    def _to_spot_syntax(self, formula: str) -> str:
        """Translate friendly syntax (not/and/or/-->) to Spot-compatible operators."""
        translated = formula
        for pattern, replacement in self._token_patterns:
            translated = pattern.sub(replacement, translated)

        # Collapse whitespace after unary negation to avoid '! p' forms Spot dislikes
        translated = re.sub(r"!\s+", "!", translated)

        # Normalise spacing around binary operators for readability
        translated = re.sub(r"\s*(&|\||->)\s*", r" \1 ", translated)
        translated = re.sub(r"\s+", " ", translated).strip()
        return translated
