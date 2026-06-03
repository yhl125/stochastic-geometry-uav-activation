"""Closed-form expressions evaluated via scipy.integrate.quad.

Implements:
  - Eq. 17: Laplace transform of the aggregate interference.
  - Eq. 19: unconditional coverage probability P_c(β, λ_a).
  - Eq. 22: average achievable rate R(λ_a) = (1/ln2)·∫ P_c(t)/(1+t) dt.
  - Eq. 26: energy efficiency EE = p_act·R / (p_act·(P_u+P_op) + P_prop).
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Tuple

import numpy as np
from scipy.integrate import quad

from channel import los_probability_scalar
import formulas as formula_kernels
from params import (
    ALPHA_LOS,
    ALPHA_NLOS,
    C1,
    C2,
    H_ALT_M,
    N0_W,
    P_OP_W,
    P_PROP_W,
    P_U_W,
    RHO,
)

_QUAD_KWARGS = dict(epsabs=1e-9, epsrel=1e-6, limit=200)
# Looser tolerance for the *inner* Laplace integral when used inside the rate
# triple integral. We're integrating P_c(t)/(1+t) over t, so high precision
# on each individual P_c(t) is wasted — coarser inner tolerance speeds
# rate evaluation by ~3x while keeping rate accurate to <0.5%.
_QUAD_KWARGS_FAST = dict(epsabs=1e-7, epsrel=1e-4, limit=80)

# Upper cap for the interferer-distance inner integral (Eq. 17). The integrand
# decays as xk^(1-α_NLoS) ~ xk^(-2.5) for large xk, so the integral converges
# but scipy.integrate.quad's [a, inf] adaptive transform can become unstable
# at small s. Empirically, capping at 100 km — well beyond the 10 km disk of
# the MC sim — gives <1e-6 relative error vs np.inf.
_INNER_X_MAX_M: float = 1.0e5


def _A_j(s: float, xk: float, alpha_j: float,
         rho: float = RHO, p_u: float = P_U_W,
         h_m: float = H_ALT_M) -> float:
    return s * rho * p_u * (xk * xk + h_m * h_m) ** (-alpha_j / 2.0)


def laplace_interference(s: float, x0_horiz: float, lam_a: float,
                         h_m: float = H_ALT_M,
                         x_max: float = _INNER_X_MAX_M,
                         fast: bool = False) -> float:
    """Eq. 17 — Laplace transform of I_agg at offset s, conditioned on serving
    horizontal distance x0_horiz = ||X_0||. Active density is λ_a = λ_u·p_act.
    """
    if lam_a <= 0.0:
        return 1.0

    def integrand(xk: float) -> float:
        p_los = los_probability_scalar(xk, h_m=h_m)
        a_los = _A_j(s, xk, ALPHA_LOS, h_m=h_m)
        a_nlos = _A_j(s, xk, ALPHA_NLOS, h_m=h_m)
        bracket = formula_kernels.interferer_state_average(p_los, a_los, a_nlos)
        return (1.0 - bracket) * xk

    kw = _QUAD_KWARGS_FAST if fast else _QUAD_KWARGS
    integral, _ = quad(integrand, x0_horiz, x_max, **kw)
    return math.exp(-2.0 * math.pi * lam_a * integral)


def _cond_coverage_given_r(beta: float, r: float, lam_a: float,
                           h_m: float = H_ALT_M,
                           rho: float = RHO, p_u: float = P_U_W,
                           n0: float = N0_W,
                           fast: bool = False) -> float:
    """Eq. 18 — P(SINR > β | R = r), averaged over LoS/NLoS of serving link."""
    x0 = formula_kernels.horizontal_distance_from_3d(r, h_m)
    p_los_r = los_probability_scalar(x0, h_m=h_m)

    s_los = formula_kernels.s_parameter(beta, r, ALPHA_LOS, rho, p_u)
    s_nlos = formula_kernels.s_parameter(beta, r, ALPHA_NLOS, rho, p_u)

    los_term = (math.exp(-s_los * n0)
                * laplace_interference(s_los, x0, lam_a, h_m=h_m, fast=fast))
    nlos_term = (math.exp(-s_nlos * n0)
                 * laplace_interference(s_nlos, x0, lam_a, h_m=h_m, fast=fast))
    return formula_kernels.serving_mixture(p_los_r, los_term, nlos_term)


def coverage_probability(beta: float, lam_a: float,
                         h_m: float = H_ALT_M,
                         r_max_m: float | None = None,
                         fast: bool = False) -> float:
    """Eq. 19 — unconditional coverage probability."""
    if lam_a <= 0.0:
        return 0.0

    if r_max_m is None:
        # f_R(r) decays as exp(-π λ_a r²); 6σ-equivalent in nearest-neighbor
        # statistics. Take 6/√(πλ_a) above H so we cover ~all of the pdf mass.
        r_max_m = h_m + 6.0 / math.sqrt(math.pi * lam_a)

    def outer(r: float) -> float:
        cond = _cond_coverage_given_r(beta, r, lam_a, h_m=h_m, fast=fast)
        pdf = formula_kernels.distance_3d_pdf(r, lam_a, h_m)
        return cond * pdf

    kw = _QUAD_KWARGS_FAST if fast else _QUAD_KWARGS
    integral, _ = quad(outer, h_m, r_max_m, **kw)
    return integral


def average_rate(lam_a: float,
                 h_m: float = H_ALT_M,
                 t_max: float = 100.0) -> float:
    """Eq. 22 — average achievable rate via the CCDF trick.

    Inner P_c(t) uses fast tolerance: each individual evaluation is less
    precise, but the outer t integral averages out the noise. Total relative
    error vs the strict (slow) variant is <0.5% on Table-1 parameters
    (verified against the strict-tolerance reference).
    """
    if lam_a <= 0.0:
        return 0.0

    def integrand(t: float) -> float:
        return formula_kernels.average_rate_tail_integrand(
            coverage_probability(t, lam_a, h_m=h_m, fast=True),
            t,
        )

    integral, _ = quad(integrand, 0.0, t_max,
                       epsabs=1e-5, epsrel=1e-3, limit=80)
    return integral / math.log(2.0)


def laplace_interference_bounded(s: float, x0_horiz: float, lam_a: float,
                                 R0_m: float,
                                 h_m: float = H_ALT_M,
                                 fast: bool = False) -> float:
    """Eq. 27 — Laplace transform with bounded interferer radius R_0.

    Same integrand as Eq. 17, but the outer interferer-distance integral is
    truncated at R_0 rather than ∞. This corresponds to the paper's
    "Distance-threshold activation" benchmark and, empirically, gives results
    closer to the paper's Fig 8 visual values than the unbounded formulation.
    """
    if lam_a <= 0.0 or x0_horiz >= R0_m:
        return 1.0

    def integrand(xk: float) -> float:
        p_los = los_probability_scalar(xk, h_m=h_m)
        a_los = _A_j(s, xk, ALPHA_LOS, h_m=h_m)
        a_nlos = _A_j(s, xk, ALPHA_NLOS, h_m=h_m)
        bracket = formula_kernels.interferer_state_average(p_los, a_los, a_nlos)
        return (1.0 - bracket) * xk

    kw = _QUAD_KWARGS_FAST if fast else _QUAD_KWARGS
    integral, _ = quad(integrand, x0_horiz, R0_m, **kw)
    return math.exp(-2.0 * math.pi * lam_a * integral)


def coverage_probability_bounded(beta: float, lam_a: float, R0_m: float,
                                 h_m: float = H_ALT_M,
                                 fast: bool = False) -> float:
    """Eq. 19 evaluated with the Eq. 27 bounded Laplace transform.

    Outer serving-distance integral is also capped at sqrt(H^2 + R_0^2)
    because the serving UAV must lie within the bounded deployment disk.
    """
    if lam_a <= 0.0:
        return 0.0
    r_upper = math.sqrt(h_m * h_m + R0_m * R0_m)

    def outer(r: float) -> float:
        x0 = formula_kernels.horizontal_distance_from_3d(r, h_m)
        p_los_r = los_probability_scalar(x0, h_m=h_m)
        s_los = formula_kernels.s_parameter(beta, r, ALPHA_LOS, RHO, P_U_W)
        s_nlos = formula_kernels.s_parameter(beta, r, ALPHA_NLOS, RHO, P_U_W)
        los_term = (math.exp(-s_los * N0_W)
                    * laplace_interference_bounded(s_los, x0, lam_a, R0_m,
                                                   h_m=h_m, fast=fast))
        nlos_term = (math.exp(-s_nlos * N0_W)
                     * laplace_interference_bounded(s_nlos, x0, lam_a, R0_m,
                                                    h_m=h_m, fast=fast))
        cond = formula_kernels.serving_mixture(p_los_r, los_term, nlos_term)
        pdf = formula_kernels.distance_3d_pdf(r, lam_a, h_m)
        return cond * pdf

    kw = _QUAD_KWARGS_FAST if fast else _QUAD_KWARGS
    integral, _ = quad(outer, h_m, r_upper, **kw)
    return integral


def average_rate_bounded(lam_a: float, R0_m: float,
                         h_m: float = H_ALT_M,
                         t_max: float = 100.0) -> float:
    """Eq. 22 with Eq. 27 bounded coverage. Slightly higher R than the
    unbounded variant because far interferers are excluded.
    """
    if lam_a <= 0.0:
        return 0.0

    def integrand(t: float) -> float:
        return formula_kernels.average_rate_tail_integrand(
            coverage_probability_bounded(t, lam_a, R0_m, h_m=h_m, fast=True),
            t,
        )

    integral, _ = quad(integrand, 0.0, t_max,
                       epsabs=1e-5, epsrel=1e-3, limit=80)
    return integral / math.log(2.0)


def energy_efficiency(lam_u: float, p_act: float,
                      rate_bps_per_hz: float | None = None,
                      h_m: float = H_ALT_M,
                      p_u: float = P_U_W, p_op: float = P_OP_W,
                      p_prop: float = P_PROP_W) -> float:
    """Eq. 26 — EE = (p_act · R) / (p_act·(P_u+P_op) + P_prop).

    Note: The λ_u factor cancels between numerator (𝒜 = λ_a·R = λ_u·p_act·R)
    and denominator (Eq. 25 has λ_u as outer factor); λ_u enters EE only
    *implicitly* through R(λ_a).
    """
    lam_a = lam_u * p_act
    if rate_bps_per_hz is None:
        rate_bps_per_hz = average_rate(lam_a, h_m=h_m)
    return formula_kernels.energy_efficiency_simplified(
        p_act,
        rate_bps_per_hz,
        p_u,
        p_op,
        p_prop,
    )
