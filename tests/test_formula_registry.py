import importlib
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class FormulaRegistryTests(unittest.TestCase):
    # The four higher-difficulty integrals declared only as opaque Lean
    # interfaces (PGFL/Slivnyak-based); their kernels live in analytical.py.
    # Everything else (including Eq.21, which has a proved sub-identity plus an
    # assumed change-of-variables structure) is backed by theorem/structure
    # declarations and a kernel in formulas.py.
    OPAQUE_INTERFACE_EQS = frozenset({"Eq.17", "Eq.19", "Eq.22", "Eq.27"})

    def _formulas(self):
        return importlib.import_module("formulas")

    def _lean_text(self) -> str:
        return "\n".join(path.read_text() for path in (ROOT / "formal").rglob("*.lean"))

    def _has_lean_decl(self, lean_text: str, kind: str, name: str) -> bool:
        return re.search(rf"(?m)^\s*{kind}\s+{re.escape(name)}\b", lean_text) is not None

    def test_registry_contains_expected_equations(self):
        formulas = self._formulas()
        expected = {
            "Eq.1",
            "Eq.2",
            "Eq.6",
            "Eq.7",
            "Eq.8",
            "Eq.15",
            "Eq.16",
            "Eq.17",
            "Eq.18",
            "Eq.19",
            "Eq.20",
            "Eq.21",
            "Eq.22",
            "Eq.23",
            "Eq.24",
            "Eq.25",
            "Eq.26",
            "Eq.27",
        }
        self.assertEqual(expected, set(formulas.FORMULA_REGISTRY))

    def test_registry_status_vocabulary_is_machine_readable(self):
        formulas = self._formulas()

        self.assertEqual("lean_verified", formulas.LEAN_VERIFIED)
        self.assertEqual("unverified", formulas.UNVERIFIED)
        self.assertEqual(
            {
                formulas.LEAN_VERIFIED,
                formulas.UNVERIFIED,
            },
            formulas.STATUS_LABELS,
        )

    def test_boundary_equation_statuses_are_explicit(self):
        formulas = self._formulas()
        registry = formulas.FORMULA_REGISTRY

        for eq in ("Eq.17", "Eq.19", "Eq.21", "Eq.22", "Eq.27"):
            with self.subTest(eq=eq):
                self.assertEqual(formulas.UNVERIFIED, registry[eq].status)

        for eq in (
            "Eq.1",
            "Eq.2",
            "Eq.6",
            "Eq.7",
            "Eq.8",
            "Eq.15",
            "Eq.16",
            "Eq.18",
            "Eq.20",
            "Eq.23",
            "Eq.24",
            "Eq.25",
            "Eq.26",
        ):
            with self.subTest(eq=eq):
                self.assertEqual(formulas.LEAN_VERIFIED, registry[eq].status)

    def test_registry_entries_have_trace_fields(self):
        formulas = self._formulas()
        for paper_eq, entry in formulas.FORMULA_REGISTRY.items():
            with self.subTest(paper_eq=paper_eq):
                self.assertEqual(paper_eq, entry.paper_eq)
                self.assertIsInstance(entry.python_names, tuple)
                self.assertTrue(entry.python_names)
                self.assertIsInstance(entry.lean_items, tuple)
                self.assertTrue(entry.lean_items)
                self.assertIn(entry.status, formulas.STATUS_LABELS)
                self.assertIsInstance(entry.assumptions, tuple)
                self.assertIsInstance(entry.notes, str)

    def test_registry_python_names_exist_for_executable_kernels(self):
        formulas = self._formulas()
        for entry in formulas.FORMULA_REGISTRY.values():
            if entry.paper_eq not in self.OPAQUE_INTERFACE_EQS:
                for python_name in entry.python_names:
                    with self.subTest(paper_eq=entry.paper_eq, python_name=python_name):
                        self.assertTrue(hasattr(formulas, python_name))

    def test_spec_boundary_python_names_exist_in_analytical_module(self):
        formulas = self._formulas()
        analytical = importlib.import_module("analytical")
        for entry in formulas.FORMULA_REGISTRY.values():
            if entry.paper_eq in self.OPAQUE_INTERFACE_EQS:
                for python_name in entry.python_names:
                    with self.subTest(paper_eq=entry.paper_eq, python_name=python_name):
                        self.assertTrue(hasattr(analytical, python_name))

    def test_registry_lean_items_have_status_appropriate_declarations(self):
        formulas = self._formulas()
        lean_text = self._lean_text()
        for entry in formulas.FORMULA_REGISTRY.values():
            for lean_item in entry.lean_items:
                with self.subTest(paper_eq=entry.paper_eq, lean_item=lean_item):
                    if entry.paper_eq in self.OPAQUE_INTERFACE_EQS:
                        self.assertTrue(
                            self._has_lean_decl(lean_text, "opaque", lean_item),
                            f"{entry.paper_eq} should be declared with the Lean "
                            f"`opaque` keyword: {lean_item}",
                        )
                    else:
                        self.assertTrue(
                            self._has_lean_decl(lean_text, "theorem", lean_item)
                            or self._has_lean_decl(lean_text, "structure", lean_item),
                            f"{entry.paper_eq} should reference a theorem or structure: {lean_item}",
                        )

    def test_script_mode_cli_still_imports(self):
        result = subprocess.run(
            [str(ROOT / ".venv/bin/python"), str(ROOT / "src/run.py"), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_channel_delegates_los_probability_to_formula_kernel(self):
        channel = importlib.import_module("channel")

        original = channel.formula_kernels.los_probability
        try:
            calls = []

            def fake_los_probability(x_horiz_m, h_m, c1, c2):
                calls.append((x_horiz_m, h_m, c1, c2))
                return 0.123

            channel.formula_kernels.los_probability = fake_los_probability
            self.assertEqual(
                0.123,
                channel.los_probability_scalar(7.0, h_m=120.0, c1=10.0, c2=0.1),
            )
            self.assertEqual([(7.0, 120.0, 10.0, 0.1)], calls)
        finally:
            channel.formula_kernels.los_probability = original

    def test_analytical_uses_formula_kernel_calls(self):
        import ast

        tree = ast.parse((ROOT / "src/analytical.py").read_text())
        called_attrs = {
            node.func.attr
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "formula_kernels"
            )
        }
        for name in {
            "average_rate_tail_integrand",
            "distance_3d_pdf",
            "horizontal_distance_from_3d",
            "interferer_state_average",
            "serving_mixture",
            "s_parameter",
            "energy_efficiency_simplified",
        }:
            self.assertIn(name, called_attrs)

    def test_s_parameter_callsite_arguments_preserve_intended_scope(self):
        import ast

        source = (ROOT / "src/analytical.py").read_text()
        tree = ast.parse(source)

        def function_node(name):
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    return node
            self.fail(f"Function not found: {name}")

        def s_parameter_args(name):
            calls = []
            for node in ast.walk(function_node(name)):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "formula_kernels"
                    and node.func.attr == "s_parameter"
                ):
                    calls.append(tuple(ast.unparse(arg) for arg in node.args))
            return set(calls)

        self.assertEqual(
            {
                ("beta", "r", "ALPHA_LOS", "rho", "p_u"),
                ("beta", "r", "ALPHA_NLOS", "rho", "p_u"),
            },
            s_parameter_args("_cond_coverage_given_r"),
        )
        self.assertEqual(
            {
                ("beta", "r", "ALPHA_LOS", "RHO", "P_U_W"),
                ("beta", "r", "ALPHA_NLOS", "RHO", "P_U_W"),
            },
            s_parameter_args("coverage_probability_bounded"),
        )

    def test_support_behavior_matches_lean_scope(self):
        formulas = self._formulas()
        self.assertEqual(0.0, formulas.horizontal_nearest_pdf(-1.0, 1e-5))
        self.assertEqual(0.0, formulas.distance_3d_pdf(100.0, 1e-5, 120.0))
        self.assertEqual(0.0, formulas.horizontal_distance_from_3d(100.0, 120.0))
        self.assertGreater(formulas.horizontal_nearest_pdf(1.0, 1e-5), 0.0)
        self.assertGreater(formulas.distance_3d_pdf(121.0, 1e-5, 120.0), 0.0)
        self.assertGreater(formulas.horizontal_distance_from_3d(121.0, 120.0), 0.0)

    def test_energy_efficiency_matches_literal_eq26(self):
        formulas = self._formulas()
        for lam_u in (2e-6, 1e-5, 5e-5):
            for p_act in (0.2, 0.6, 1.0):
                rate = 0.57
                literal = formulas.area_spectral_efficiency(
                    lam_u,
                    p_act,
                    rate,
                ) / formulas.total_power_density(lam_u, p_act, 1.0, 0.1, 56.29)
                simplified = formulas.energy_efficiency_simplified(
                    p_act,
                    rate,
                    1.0,
                    0.1,
                    56.29,
                )
                self.assertAlmostEqual(literal, simplified)


if __name__ == "__main__":
    unittest.main()
