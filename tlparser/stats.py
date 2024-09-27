from pyModelChecking import CTLS
import re
import pprint

class Stats:
    def __init__(self, formula_str):
        self.formula_raw = formula_str
        self.formula_parsable = None
        self.formula_parsed = None
        
        # Group: Comparison operators
        self.cops = {
            'eq': 0,  # Equal
            'neq': 0,  # Not equal
            'gt': 0,  # Greater than
            'geq': 0,  # Greater than or equal
            'lt': 0,  # Less than
            'leq': 0  # Less than or equal
        }
        
        # Group: Temporal operators
        self.tops = {
            'A': 0,  # For all
            'E': 0,  # Exists
            'X': 0,  # Next
            'F': 0,  # Finally
            'G': 0,  # Globally
            'U': 0,  # Until
            'R': 0   # Release
        }
        
        # Group: Logical operators
        self.lops = {
            'impl': 0,  # Implication
            'and': 0,   # And
            'or': 0,    # Or
            'not': 0    # Not
        }
        
        # Other properties
        self.asth = 0
        self.ap = set()  # Atomic propositions (e.g., 'x > 5')

        if len(self.formula_raw) > 0:
            # Replace comparison operators
            self.cops, self.formula_parsable = self.analyse_comparison_ops(self.formula_raw)
            
            # Parse the formula
            p = CTLS.Parser()
            self.formula_parsed = p(self.formula_parsable)
            self.analyze_formula(self.formula_parsed)
            self.agg = self.update_aggregates()

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
            self.asth = node.height

        # print(f"Node:\t\t{node}")
        # print(f"Symbol:\t\t{node.symbols[0]}")  if hasattr(node, '_subformula') else print(f"Symbol:\t\tAP")
        # print(f"Subform:\t{node._subformula}") if hasattr(node, '_subformula') else print(f"Subform:\tAP")
        # print()

        if isinstance(node, CTLS.AtomicProposition):
            self.ap.add(str(node))
            return  # Atomic propositions don't have further nesting
        
        if isinstance(node, CTLS.Imply):
            self.lops['impl'] += 1
        if isinstance(node, CTLS.And):
            self.lops['and'] += len(node._subformula) - 1
        if isinstance(node, CTLS.Or):
            self.lops['or'] += len(node._subformula) - 1
        if isinstance(node, CTLS.Not):
            self.lops['not'] += 1
            
        if isinstance(node, CTLS.X):
            self.tops['X'] += 1
        if isinstance(node, CTLS.F):
            self.tops['F'] += 1
        if isinstance(node, CTLS.G):
            self.tops['G'] += 1
        if isinstance(node, CTLS.U):
            self.tops['U'] += 1
        if isinstance(node, CTLS.R):
            self.tops['R'] += 1
        if isinstance(node, CTLS.A):
            self.tops['A'] += 1
        if isinstance(node, CTLS.E):
            self.tops['E'] += 1

        # Recursively analyze subformulas
        if hasattr(node, '_subformula'):
            for subformula in node._subformula:
                self.analyze_formula(subformula, level + 1)
        else:
            raise ValueError("Unknown node type")

    def update_aggregates(self):
        return {
            'aps': len(self.ap),
            'cops': sum(self.cops.values()),
            'lops': sum(self.lops.values()),
            'tops': sum(self.tops.values())
        }

    def get_stats(self):
        return {key: value for key, value in vars(self).items() if key not in ['']}

    def __str__(self):
        return pprint.pformat(self.get_stats(), indent=2)
