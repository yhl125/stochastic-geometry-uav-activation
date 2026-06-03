import ast
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import params as P


class EquationFormulaGuardTests(unittest.TestCase):
    def _analytical_function_source(self, name: str) -> str:
        analytical_path = Path("src/analytical.py")
        source = analytical_path.read_text()
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return ast.get_source_segment(source, node) or ""
        self.fail(f"Function not found: {name}")

    def test_eq26_literal_and_simplified_forms_are_identical(self):
        for lam_u in (2e-6, 1e-5, 5e-5):
            for p_act in (0.2, 0.6, 1.0):
                rate = 0.57
                literal = (lam_u * p_act * rate) / (
                    lam_u * (p_act * (P.P_U_W + P.P_OP_W) + P.P_PROP_W)
                )
                simplified = (
                    p_act * rate / (p_act * (P.P_U_W + P.P_OP_W) + P.P_PROP_W)
                )
                self.assertAlmostEqual(literal, simplified)

    def test_core_rate_implementations_remain_base2(self):
        mc = Path("src/mc.py").read_text()

        for function_name in ("average_rate", "average_rate_bounded"):
            with self.subTest(function_name=function_name):
                self.assertIn(
                    "return integral / math.log(2.0)",
                    self._analytical_function_source(function_name),
                )
        self.assertIn("np.log2(1.0 + sinr)", mc)


if __name__ == "__main__":
    unittest.main()
