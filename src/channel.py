"""Al-Hourani LoS sigmoid (Eq. 2) and link-state helpers."""
from __future__ import annotations

import numpy as np

from params import C1, C2, H_ALT_M
import formulas as formula_kernels


def los_probability_scalar(x_horiz_m: float,
                           h_m: float = H_ALT_M,
                           c1: float = C1,
                           c2: float = C2) -> float:
    """Eq. 2: P_LoS(x), delegated to the Lean-traceable formula kernel."""
    return formula_kernels.los_probability(x_horiz_m, h_m, c1, c2)


def los_probability_array(x_horiz_m: np.ndarray,
                          h_m: float = H_ALT_M,
                          c1: float = C1,
                          c2: float = C2) -> np.ndarray:
    """Vectorized Eq. 2, delegated to the Lean-traceable formula kernel."""
    return formula_kernels.los_probability_array(x_horiz_m, h_m, c1, c2)
