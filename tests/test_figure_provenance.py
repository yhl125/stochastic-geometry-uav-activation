import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class FigureProvenanceTests(unittest.TestCase):
    def _provenance(self):
        return importlib.import_module("figure_provenance")

    def test_provenance_covers_figures_2_through_12(self):
        figure_provenance = importlib.import_module("figure_provenance")

        self.assertEqual(
            set(range(2, 13)),
            set(figure_provenance.FIGURE_PROVENANCE),
        )

    def test_all_referenced_equations_exist_in_formula_registry(self):
        formulas = importlib.import_module("formulas")
        figure_provenance = importlib.import_module("figure_provenance")

        known = set(formulas.FORMULA_REGISTRY)
        for fig, row in figure_provenance.FIGURE_PROVENANCE.items():
            with self.subTest(fig=fig):
                self.assertTrue(row.paper_equations)
                self.assertTrue(set(row.paper_equations).issubset(known))
                self.assertTrue(set(row.lean_checked_equations).issubset(known))
                self.assertTrue(set(row.boundary_equations).issubset(known))

    def test_boundary_equations_match_registry_status(self):
        formulas = importlib.import_module("formulas")
        figure_provenance = importlib.import_module("figure_provenance")

        for fig, row in figure_provenance.FIGURE_PROVENANCE.items():
            for eq in row.boundary_equations:
                with self.subTest(fig=fig, eq=eq):
                    self.assertEqual(
                        formulas.UNVERIFIED,
                        formulas.FORMULA_REGISTRY[eq].status,
                    )

    def test_lean_checked_equations_match_registry_status(self):
        formulas = importlib.import_module("formulas")
        figure_provenance = importlib.import_module("figure_provenance")

        for fig, row in figure_provenance.FIGURE_PROVENANCE.items():
            for eq in row.lean_checked_equations:
                with self.subTest(fig=fig, eq=eq):
                    self.assertEqual(
                        formulas.LEAN_VERIFIED,
                        formulas.FORMULA_REGISTRY[eq].status,
                    )

    def test_rate_scaling_methodology_is_recorded_for_scaled_rate_figures(self):
        figure_provenance = self._provenance()

        for fig in range(9, 13):
            row = figure_provenance.FIGURE_PROVENANCE[fig]
            with self.subTest(fig=fig):
                self.assertIn("figures._plot_rate", row.python_entry_points)
                self.assertIn(
                    "figure_methodology.FIGURE_METHODS",
                    row.python_entry_points,
                )
                self.assertIn("plot multiplier", row.notes)
                self.assertIn("Python methodology boundary", row.notes)
