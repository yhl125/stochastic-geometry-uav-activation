import math
import sys
import unittest
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import formulas


class FormulaCharacterizationTests(unittest.TestCase):
    def test_eq1_friis_reference_gain_matches_literal_formula(self):
        got = formulas.friis_reference_gain(1.0, 1.0, 0.149896229)
        expected = 1.0 * 1.0 * (0.149896229 / (4.0 * math.pi)) ** 2
        self.assertAlmostEqual(expected, got)

    def test_eq2_los_probability_scalar_and_array_match_literal_formula(self):
        xs = np.array([0.0, 1.0, 50.0, 200.0])
        h_m = 120.0
        c1 = 10.0
        c2 = 0.1

        scalar_expected = []
        for x in xs:
            theta = 90.0 if x <= 0.0 else math.degrees(math.atan(h_m / float(x)))
            scalar_expected.append(1.0 / (1.0 + c1 * math.exp(-c2 * (theta - c1))))
        scalar_got = [formulas.los_probability(float(x), h_m, c1, c2) for x in xs]
        assert_allclose(scalar_expected, scalar_got, rtol=0.0, atol=1e-15)

        safe_x = np.where(xs > 0.0, xs, 1e-12)
        array_expected = 1.0 / (
            1.0 + c1 * np.exp(-c2 * (np.degrees(np.arctan(h_m / safe_x)) - c1))
        )
        assert_allclose(
            array_expected,
            formulas.los_probability_array(xs, h_m, c1, c2),
            rtol=0.0,
            atol=1e-15,
        )

    def test_distance_and_rayleigh_kernels_match_literal_formulas(self):
        lam_a = 1e-5
        h_m = 120.0
        r_m = 150.0
        x_m = 90.0
        a = 0.42

        self.assertAlmostEqual(
            2.0 * math.pi * lam_a * x_m * math.exp(-math.pi * lam_a * x_m * x_m),
            formulas.horizontal_nearest_pdf(x_m, lam_a),
        )
        self.assertAlmostEqual(
            math.sqrt(r_m * r_m - h_m * h_m),
            formulas.horizontal_distance_from_3d(r_m, h_m),
        )
        self.assertAlmostEqual(
            r_m / math.sqrt(r_m * r_m - h_m * h_m),
            formulas.horizontal_distance_jacobian(r_m, h_m),
        )
        self.assertAlmostEqual(
            2.0 * math.pi * lam_a * r_m * math.exp(
                -math.pi * lam_a * (r_m * r_m - h_m * h_m)
            ),
            formulas.distance_3d_pdf(r_m, lam_a, h_m),
        )
        self.assertAlmostEqual(1.0 / (1.0 + a), formulas.rayleigh_laplace_kernel(a))

    def test_mixture_s_rate_and_power_kernels_match_literal_formulas(self):
        p_los = 0.73
        a_los = 0.2
        a_nlos = 0.8
        los_term = 0.91
        nlos_term = 0.37

        self.assertAlmostEqual(
            p_los / (1.0 + a_los) + (1.0 - p_los) / (1.0 + a_nlos),
            formulas.interferer_state_average(p_los, a_los, a_nlos),
        )
        self.assertAlmostEqual(
            p_los * los_term + (1.0 - p_los) * nlos_term,
            formulas.serving_mixture(p_los, los_term, nlos_term),
        )
        self.assertAlmostEqual(
            3.0 * 150.0 ** 2.1 / (0.00014 * 1.0),
            formulas.s_parameter(3.0, 150.0, 2.1, 0.00014, 1.0),
        )
        self.assertAlmostEqual(math.log2(1.0 + 4.0), formulas.rate_log2(4.0))
        self.assertAlmostEqual(0.6 / 1.7, formulas.average_rate_tail_integrand(0.6, 0.7))
        self.assertAlmostEqual(
            1e-5 * 0.6 * 0.57,
            formulas.area_spectral_efficiency(1e-5, 0.6, 0.57),
        )
        self.assertAlmostEqual(14.75 + 41.54, formulas.hover_propulsion_power(14.75, 41.54))
        self.assertAlmostEqual(
            1e-5 * (0.6 * (1.0 + 0.1) + 56.29),
            formulas.total_power_density(1e-5, 0.6, 1.0, 0.1, 56.29),
        )
        self.assertAlmostEqual(
            0.6 * 0.57 / (0.6 * (1.0 + 0.1) + 56.29),
            formulas.energy_efficiency_simplified(0.6, 0.57, 1.0, 0.1, 56.29),
        )


if __name__ == "__main__":
    unittest.main()
