from pyModelChecking import CTLS
import re
import pprint

class Stats:
    def __init__(self, formula_str):
        self.formula_raw = formula_str
        self.formula_parsable = None
        self.formula_parsed = None
        self.ap = set()
        self.impl_n = 0
        self.and_n = 0
        self.or_n = 0
        self.not_n = 0
        self.A_n = 0
        self.E_n = 0
        self.X_n = 0
        self.F_n = 0
        self.G_n = 0
        self.U_n = 0
        self.R_n = 0
        self.nesting = 0
        self.AST_height = 0

        # Replace comparison operators
        self.cops, self.formula_parsable = self.analyse_comparison_ops(self.formula_raw)

        # Parse the formula
        p = CTLS.Parser()
        self.formula_parsed = p(self.formula_parsable)
        self.analyze_formula(self.formula_parsed)

        self.update_aggregates()

    def analyse_comparison_ops(self, formula_str):
        # Patterns for comparison operators
        patterns = {
            'eq': re.compile(r'=='),
            'leq': re.compile(r'<='),
            'geq': re.compile(r'>='),
            'neq': re.compile(r'!='),
            'lt': re.compile(r'(?<!<)<(?![=<])'),  # Ensure it does not match <=
            'gt': re.compile(r'(?<!>)>(?![=>])'),  # Ensure it does not match >=
        }

        # Count occurrences of each operator
        formula_tmp = re.sub('-->', '__IMPLIES__', formula_str)
        counts = {key: len(pattern.findall(formula_tmp)) for key, pattern in patterns.items()}

        # Sub-function to replace comparison operators
        def replace_comparisons(match):
            expression = match.group().replace(' ', '')
            expression = re.sub(r'-', 'n', expression)
            if '<=' in expression:
                return expression.replace('<=', '_leq_')
            elif '>=' in expression:
                return expression.replace('>=', '_geq_')
            elif '==' in expression:
                return expression.replace('==', '_eq_')
            elif '!=' in expression:
                return expression.replace('!=', '_neq_')
            elif '<' in expression:
                return expression.replace('<', '_lt_')
            elif ' > ' in expression:
                return expression.replace('>', '_gt_')

        # Replace comparison operators (allowing for any amount of space)
        modified_string = re.sub(r'\b[\w\.]+ *[<>!=]=? *-?\w+\b', replace_comparisons, formula_str)

        return counts, modified_string

    def analyze_formula(self, node, level=0):
        if level == 0:
            self.AST_height = node.height
        self.nesting = max(self.nesting, level)

        # print(f"Node:\t\t{node}")
        # print(f"Symbol:\t\t{node.symbols[0]}")  if hasattr(node, '_subformula') else print(f"Symbol:\t\tAP")
        # print(f"Subform:\t{node._subformula}") if hasattr(node, '_subformula') else print(f"Subform:\tAP")
        # print()

        if isinstance(node, CTLS.AtomicProposition):
            self.ap.add(str(node))
            return  # Atomic propositions don't have further nesting
        if isinstance(node, CTLS.Imply):
            self.impl_n += 1
        if isinstance(node, CTLS.And):
            self.and_n += len(node._subformula) - 1
        if isinstance(node, CTLS.Or):
            self.or_n += len(node._subformula) - 1
        if isinstance(node, CTLS.Not):
            self.not_n += 1
        if isinstance(node, CTLS.X):
            self.X_n += 1
        if isinstance(node, CTLS.F):
            self.F_n += 1
        if isinstance(node, CTLS.G):
            self.G_n += 1
        if isinstance(node, CTLS.U):
            self.U_n += 1
        if isinstance(node, CTLS.R):
            self.R_n += 1
        if isinstance(node, CTLS.A):
            self.A_n += 1
        if isinstance(node, CTLS.E):
            self.E_n += 1

        # Recursively analyze subformulas
        if hasattr(node, '_subformula'):
            for subformula in node._subformula:
                self.analyze_formula(subformula, level + 1)
        else:
            raise ValueError("Unknown node type")

    def update_aggregates(self):
        self.agg = {"ap": len(self.ap),
                    "lops": self.impl_n + self.and_n + self.or_n + self.not_n,
                    "tops": self.A_n + self.E_n + self.X_n + self.F_n + self.G_n + self.U_n + self.R_n,
                    "cops": sum(self.cops.values())}

    def get_stats(self):
        return {key: value for key, value in vars(self).items() if key not in ['']}

    def __str__(self):
        return pprint.pformat(self.get_stats(), indent=2)
