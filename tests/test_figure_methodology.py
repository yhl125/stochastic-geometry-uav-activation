import math
import unittest

from src.figure_methodology import FIGURE_METHODS, RateScale


class FigureMethodologyTests(unittest.TestCase):
    def test_all_paper_figures_have_explicit_methods(self):
        self.assertEqual(set(FIGURE_METHODS), set(range(2, 13)))

    def test_coverage_figures_use_documented_thresholds_and_equations(self):
        self.assertEqual(FIGURE_METHODS[2].equations, ("Eq.19", "Eq.27"))
        self.assertEqual(FIGURE_METHODS[2].bounded_radius_m, 10_000.0)
        self.assertEqual(FIGURE_METHODS[2].beta_db, None)
        self.assertEqual(FIGURE_METHODS[3].equations, ("Eq.19", "Eq.27"))
        self.assertEqual(FIGURE_METHODS[3].beta_db, 3.0)
        self.assertEqual(FIGURE_METHODS[3].unbounded_beta_db, 5.5)
        self.assertEqual(FIGURE_METHODS[4].equations, ("Eq.19",))
        self.assertEqual(FIGURE_METHODS[4].beta_db, (-5.0, 0.0, 5.0))
        for fig in (5, 6, 7):
            self.assertEqual(FIGURE_METHODS[fig].equations, ("Eq.19",))
            self.assertEqual(FIGURE_METHODS[fig].beta_db, 2.0)

    def test_rate_and_ee_figures_separate_formula_units_from_published_plot_scale(self):
        for fig in (8, 9, 10, 11, 12):
            self.assertIn("Eq.22", FIGURE_METHODS[fig].equations)
            self.assertEqual(FIGURE_METHODS[fig].formula_rate_scale, RateScale.LOG2)

        self.assertEqual(FIGURE_METHODS[8].plot_rate_scale, RateScale.LOG2)
        for fig in (9, 10, 11, 12):
            self.assertEqual(FIGURE_METHODS[fig].plot_rate_scale, RateScale.NATURAL_LOG)
            self.assertAlmostEqual(FIGURE_METHODS[fig].plot_multiplier, math.log(2.0))

    def test_axes_keep_visible_origin_while_degenerate_sweeps_start_after_zero(self):
        for fig in (6, 10):
            self.assertEqual(FIGURE_METHODS[fig].xlim, (0.0, 200.0))
            self.assertEqual(FIGURE_METHODS[fig].x_values[0], 0.0)

        for fig in (7, 11, 12):
            self.assertEqual(FIGURE_METHODS[fig].xlim, (0.0, 50.0))
            self.assertGreater(FIGURE_METHODS[fig].x_values[0], 0.0)

        for fig in (3, 4, 5, 9):
            self.assertEqual(FIGURE_METHODS[fig].xlim, (0.0, 1.0))
            self.assertGreater(FIGURE_METHODS[fig].x_values[0], 0.0)

    def test_fig8_uses_finer_analytical_grid_than_mc_grid(self):
        fig8 = FIGURE_METHODS[8]

        self.assertEqual(fig8.bounded_radius_m, 10_000.0)
        self.assertEqual(fig8.rate_t_max, 100.0)
        self.assertEqual(len(fig8.analytical_x_values), 50)
        self.assertEqual(len(fig8.mc_x_values), 20)
        self.assertGreater(fig8.analytical_x_values[0], 0.0)
        self.assertEqual(fig8.analytical_x_values[-1], 1.0)
        self.assertGreater(fig8.mc_x_values[0], 0.0)
        self.assertEqual(fig8.mc_x_values[-1], 1.0)

    def test_fig12_keeps_equation_grid_separate_from_visible_paper_grid(self):
        fig12 = FIGURE_METHODS[12]

        expected = tuple(float(x) / 2.0 for x in range(5, 105, 5))
        self.assertEqual(fig12.equation_x_values, expected)
        self.assertEqual(fig12.x_values, expected)

    def test_rate_sweep_grids_follow_published_figure_density(self):
        self.assertEqual(len(FIGURE_METHODS[9].x_values), 100)
        self.assertEqual(len(FIGURE_METHODS[10].x_values), 41)
        self.assertEqual(len(FIGURE_METHODS[11].x_values), 25)


if __name__ == "__main__":
    unittest.main()
