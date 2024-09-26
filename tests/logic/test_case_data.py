class TestCaseData:
    __test__ = False
    def __init__(self, f_code='', ast_height='', aps=0, cops=0, lops=0, tops=0):
        self.f_code = f_code
        self.ast_height = ast_height
        self.aps = aps
        self.cops = cops
        self.lops = lops
        self.tops = tops
