class TestCaseData:
    __test__ = False
    def __init__(self, f_code='', asth='', aps=0, cops=0, lops=0, tops=0, entropy_lops_tops=None):
        self.f_code = f_code
        self.asth = asth
        self.aps = aps
        self.cops = cops
        self.lops = lops
        self.tops = tops
        self.entropy_lops_tops = entropy_lops_tops
