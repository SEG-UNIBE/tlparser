from unittest import TestCase

from tlparser.stats import Stats
from tlparser.stats_ext import SpotAnalyzer
from test_case_data import TestCaseDataExt


EXTENDED_CASES = (
    TestCaseDataExt(
        f_code="G p",
        aps=1,
        syntactic_safety=True,
        is_stutter_invariant_formula=True,
        manna_pnueli_class_contains="Safety",
    ),
    TestCaseDataExt(
        f_code="F G s",
        aps=1,
        syntactic_safety=False,
        is_stutter_invariant_formula=True,
        manna_pnueli_class_contains="persistence reactivity",
    ),
    TestCaseDataExt(
        f_code="G (req --> F ack)",
        aps=2,
        syntactic_safety=False,
        is_stutter_invariant_formula=True,
        manna_pnueli_class_contains="recurrence reactivity",
    ),
    TestCaseDataExt(
        f_code="G (not(crit1 & crit2))",
        aps=2,
        syntactic_safety=True,
        is_stutter_invariant_formula=True,
        manna_pnueli_class_contains="Safety",
    ),
    TestCaseDataExt(
        f_code="GFa --> GFb",
        aps=2,
        syntactic_safety=False,
        is_stutter_invariant_formula=True,
        manna_pnueli_class_contains="reactivity",
    ),
    TestCaseDataExt(
        f_code="X p",
        aps=1,
        syntactic_safety=True,
        is_stutter_invariant_formula=False,
        manna_pnueli_class_contains="guarantee safety obligation persistence recurrence reactivity",
    ),
    TestCaseDataExt(
        f_code="F X p",
        aps=1,
        syntactic_safety=False,
        is_stutter_invariant_formula=False,
        manna_pnueli_class_contains="guarantee obligation persistence recurrence reactivity",
    ),
)


class TestStatsExtended(TestCase):
    def setUp(self):
        # These tests rely on real Spot tooling; they skip automatically when unavailable.
        self.data = EXTENDED_CASES
        self.analyzer = SpotAnalyzer()
        self._stats_cache: dict[str, Stats] = {}

    class _NullAnalyzer:
        def __init__(self):
            self.calls: list[str] = []

        def classify(self, formula: str):
            self.calls.append(formula)
            return None

    def _get_stats(self, case: TestCaseDataExt) -> Stats:
        cached = self._stats_cache.get(case.f_code)
        if cached is not None:
            return cached

        stats = Stats(case.f_code, extended=True, spot_analyzer=self.analyzer)
        if stats.spot is None:
            self.skipTest(
                "Spot CLI tools not available. Install Spot or disable extended tests."
            )
        self._stats_cache[case.f_code] = stats
        return stats

    def test_formula_in_spot_result(self):
        for case in self.data:
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                self.assertEqual(case.f_code, stats.spot.get("formula"), case.f_code)

    def test_spot_reports_tgba_analysis(self):
        for case in self.data:
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                self.assertIn("tgba_analysis", stats.spot, case.f_code)

    def test_spot_respects_syntactic_safety(self):
        for case in self.data:
            if case.syntactic_safety is None:
                continue
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                self.assertEqual(case.syntactic_safety, stats.spot.get("syntactic_safety"), case.f_code)

    def test_spot_respects_stutter_invariance(self):
        for case in self.data:
            if case.is_stutter_invariant_formula is None:
                continue
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                self.assertEqual(
                    case.is_stutter_invariant_formula,
                    stats.spot.get("is_stutter_invariant_formula"),
                    case.f_code,
                )

    def test_spot_reports_manna_pnueli_class(self):
        for case in self.data:
            if case.manna_pnueli_class_contains is None:
                continue
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                actual_class = stats.spot.get("manna_pnueli_class", "") or ""
                self.assertIn(case.manna_pnueli_class_contains.lower(), actual_class.lower(), case.f_code)

    def test_aggregated_ap_matches_expectation(self):
        for case in self.data:
            if case.aps is None:
                continue
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                self.assertEqual(case.aps, stats.agg["aps"], case.f_code)

    def test_spot_formula_translation(self):
        expected_substrings = {
            "G (req --> F ack)": "req -> F ack",
            "G (not(crit1 & crit2))": "!(crit1 & crit2)",
            "GFa --> GFb": "GFa -> GFb",
        }
        for case in self.data:
            with self.subTest(formula=case.f_code):
                stats = self._get_stats(case)
                spot_formula = stats.spot.get("spot_formula")
                self.assertIsNotNone(spot_formula, case.f_code)
                expected = expected_substrings.get(case.f_code)
                if expected is None:
                    self.assertEqual(case.f_code, spot_formula, case.f_code)
                else:
                    self.assertIn(expected, spot_formula, case.f_code)

    def _get_null_analyzer_results(self):
        analyzer = self._NullAnalyzer()
        stats_by_case: dict[str, Stats] = {}
        for case in self.data:
            stats_by_case[case.f_code] = Stats(
                case.f_code,
                extended=True,
                spot_analyzer=analyzer,
            )
        return analyzer, stats_by_case

    def test_null_analyzer_records_calls(self):
        analyzer, _ = self._get_null_analyzer_results()
        for case in self.data:
            with self.subTest(formula=case.f_code):
                self.assertIn(case.f_code, analyzer.calls, case.f_code)

    def test_null_analyzer_returns_no_spot_stats(self):
        _, stats_by_case = self._get_null_analyzer_results()
        for case in self.data:
            with self.subTest(formula=case.f_code):
                self.assertIsNone(stats_by_case[case.f_code].spot, case.f_code)

    def test_null_analyzer_keeps_ap_counts(self):
        _, stats_by_case = self._get_null_analyzer_results()
        for case in self.data:
            if case.aps is None:
                continue
            with self.subTest(formula=case.f_code):
                self.assertEqual(case.aps, stats_by_case[case.f_code].agg["aps"], case.f_code)
