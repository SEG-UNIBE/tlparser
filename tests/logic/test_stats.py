from unittest import TestCase

from tlparser.config import Configuration
from tlparser.utils import Utils
from tlparser.stats import Stats
from test_case_data import TestCaseData


class TestStats(TestCase):
    def setUp(self):

        self.data = {
            TestCaseData(f_code='p --> q', ast_height=1, aps=2, cops=0, lops=1, tops=0),
            TestCaseData(f_code='p == 0 --> q', ast_height=1, aps=2, cops=1, lops=1, tops=0),
            TestCaseData(f_code='G((x and (u == 9) and (i < 3)) --> G(not y or x))', ast_height=5, aps=4, cops=2, lops=5, tops=2),
            TestCaseData(f_code='G(Number_of_FCTs <= 7)', ast_height=1, aps=1, cops=1, lops=0, tops=1),
            TestCaseData(f_code='G(Number_of_FCTs >= seven)', ast_height=1, aps=1, cops=1, lops=0, tops=1),
        }

class TestInit(TestStats):

    # def test_json_import(self):
    #     config = Configuration.from_json('config.unittest.json')
    #     config = Configuration(
    #         file_data_in=json_file, 
    #         folder_data_out=working_dir,
    #         only_with_status=DEFAULT_STATI)
    #     util = Utils(config)
    #     formulas = util.read_formulas_from_json()
    #     self.assertGreater(len(formulas), 0)

    def test_ast(self):
            for case in self.data:
                f = Stats(case.f_code)
                self.assertEqual(case.ast_height, f.AST_height, case.f_code)

    def test_aps(self):
        for case in self.data:
            f = Stats(case.f_code)
            self.assertEqual(case.aps, f.agg['aps'], case.f_code)

    def test_cops(self):
        for case in self.data:
            f = Stats(case.f_code)
            self.assertEqual(case.cops, f.agg['cops'], case.f_code)

    def test_lops(self):
        for case in self.data:
            f = Stats(case.f_code)
            self.assertEqual(case.lops, f.agg['lops'], case.f_code)

    def test_tops(self):
        for case in self.data:
            f = Stats(case.f_code)
            self.assertEqual(case.tops, f.agg['tops'], case.f_code)

