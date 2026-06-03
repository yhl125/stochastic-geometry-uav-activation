"""Diagnose Fig 8 systematic offset: compare fast vs strict tolerance, and check
MC with larger disk radius.
"""
from __future__ import annotations

import math
import time

import numpy as np
from scipy.integrate import quad

import params as P
from analytical import _cond_coverage_given_r, coverage_probability
from mc import simulate_sinr, rate_mc


def strict_average_rate(lam_a: float,
                        h_m: float = P.H_ALT_M,
                        t_max: float = 1000.0) -> float:
    """Reproduce average_rate but with STRICT tolerance throughout."""
    if lam_a <= 0.0:
        return 0.0

    def integrand(t: float) -> float:
        return coverage_probability(t, lam_a, h_m=h_m, fast=False) / (1.0 + t)

    integral, _ = quad(integrand, 0.0, t_max,
                       epsabs=1e-8, epsrel=1e-6, limit=200)
    return integral / math.log(2.0)


def test_strict_vs_fast() -> None:
    """Check fast-tolerance vs strict-tolerance for several (λ_u, p_act) pairs."""
    from analytical import average_rate
    print("=== strict vs fast comparison ===")
    cases = [
        (2e-6, 1.0, "λ_u=2, p_act=1.0"),
        (5e-6, 1.0, "λ_u=5, p_act=1.0"),
        (10e-6, 1.0, "λ_u=10, p_act=1.0"),
        (5e-6, 0.5, "λ_u=10, p_act=0.5"),
        (4e-6, 1.0, "λ_u=10, p_act=0.4 (peak)"),
    ]
    for lam_a, _, label in cases:
        t0 = time.time()
        r_fast = average_rate(lam_a)
        t1 = time.time()
        r_strict = strict_average_rate(lam_a, t_max=1000.0)
        t2 = time.time()
        diff_pct = (r_strict - r_fast) / r_fast * 100.0
        print(f"  {label:35s}  fast={r_fast:.4f}({t1-t0:.1f}s)  "
              f"strict={r_strict:.4f}({t2-t1:.1f}s)  diff={diff_pct:+.2f}%")


def test_disk_size() -> None:
    """Check whether MC rate depends on simulation disk radius."""
    from mc import simulate_sinr, rate_mc
    print("\n=== MC vs disk radius (λ_u=10/km², p_act=1.0, β=0dB) ===")
    lam_u = 10e-6
    p_act = 1.0
    for radius_km in [10, 15, 20, 30]:
        t0 = time.time()
        res = simulate_sinr(lam_u, p_act, n_iters=2000, seed=0,
                            disk_r=radius_km * 1000.0)
        rate = rate_mc(res)
        t1 = time.time()
        print(f"  disk={radius_km:3d} km  rate_mc={rate:.4f}  [{t1-t0:.1f}s]")


if __name__ == "__main__":
    test_strict_vs_fast()
    test_disk_size()
