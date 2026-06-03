import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from figures import _left_anchored_xy


class PlotLeftAnchorTests(unittest.TestCase):
    def test_adds_extrapolated_nonzero_anchor_at_visible_axis_origin(self):
        x = np.array([0.05, 0.10, 0.15])
        y = np.array([0.12, 0.16, 0.19])

        anchored_x, anchored_y = _left_anchored_xy(x, y, 0.0)

        self.assertEqual(anchored_x[0], 0.0)
        self.assertAlmostEqual(anchored_y[0], 0.08)
        np.testing.assert_allclose(anchored_x[1:], x)
        np.testing.assert_allclose(anchored_y[1:], y)

    def test_does_not_duplicate_anchor_when_curve_already_starts_at_axis_origin(self):
        x = np.array([0.0, 5.0, 10.0])
        y = np.array([0.1, 0.2, 0.3])

        anchored_x, anchored_y = _left_anchored_xy(x, y, 0.0)

        np.testing.assert_allclose(anchored_x, x)
        np.testing.assert_allclose(anchored_y, y)


if __name__ == "__main__":
    unittest.main()
