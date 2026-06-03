import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mc import MCResult, rate_mc


class McRateCapTests(unittest.TestCase):
    def test_rate_mc_defaults_to_uncapped_base2_rate(self):
        result = MCResult(
            sinr_linear=np.array([0.0, 1.0, 3.0, 255.0]),
            no_active_count=0,
            n_iters=4,
        )

        self.assertAlmostEqual(
            rate_mc(result),
            float(np.mean(np.log2(1.0 + result.sinr_linear))),
        )

    def test_rate_mc_can_match_truncated_analytical_rate_integral(self):
        result = MCResult(
            sinr_linear=np.array([0.0, 1.0, 3.0, 255.0]),
            no_active_count=0,
            n_iters=4,
        )

        self.assertAlmostEqual(
            rate_mc(result, sinr_cap=3.0),
            float(np.mean(np.log2(1.0 + np.minimum(result.sinr_linear, 3.0)))),
        )


if __name__ == "__main__":
    unittest.main()
