"""Lean-traceable formula kernels for the UAV activation reproduction.

This module does not make the Python simulator formally verified. It keeps
small symbolic formula kernels in one place and records which Lean theorem or
spec boundary audits each kernel.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

LEAN_VERIFIED = "lean_verified"
UNVERIFIED = "unverified"

STATUS_LABELS = frozenset({
    LEAN_VERIFIED,
    UNVERIFIED,
})

STATUS_DESCRIPTIONS = {
    LEAN_VERIFIED: (
        "Lean proves a local formula, algebraic identity, support condition, "
        "denominator condition, or log-base equivalence for the equation."
    ),
    UNVERIFIED: (
        "The full paper equation is not formally verified in Lean within the "
        "project scope. Either the higher-difficulty stochastic-geometry "
        "integral (PGFL/Slivnyak-based) is declared only as a typed opaque "
        "interface, or the equation is only partially formalized: a tractable "
        "sub-identity is proved but a key intermediate step is assumed rather "
        "than proved. In both cases the value is computed numerically in Python."
    ),
}


@dataclass(frozen=True)
class FormulaTrace:
    paper_eq: str
    python_names: tuple[str, ...]
    lean_items: tuple[str, ...]
    status: str
    assumptions: tuple[str, ...]
    notes: str


def friis_reference_gain(
    gt: float,
    gr: float,
    wavelength_m: float,
    d0_m: float = 1.0,
) -> float:
    return gt * gr * (wavelength_m / (4.0 * math.pi * d0_m)) ** 2


def elevation_angle_degrees(x_horiz_m: float, h_m: float) -> float:
    if x_horiz_m <= 0.0:
        return 90.0
    return math.degrees(math.atan(h_m / x_horiz_m))


def los_probability(x_horiz_m: float, h_m: float, c1: float, c2: float) -> float:
    theta_deg = elevation_angle_degrees(x_horiz_m, h_m)
    return 1.0 / (1.0 + c1 * math.exp(-c2 * (theta_deg - c1)))


def nlos_probability(x_horiz_m: float, h_m: float, c1: float, c2: float) -> float:
    return 1.0 - los_probability(x_horiz_m, h_m, c1, c2)


def los_probability_array(
    x_horiz_m: np.ndarray,
    h_m: float,
    c1: float,
    c2: float,
) -> np.ndarray:
    safe_x = np.where(x_horiz_m > 0.0, x_horiz_m, 1e-12)
    theta_deg = np.degrees(np.arctan(h_m / safe_x))
    return 1.0 / (1.0 + c1 * np.exp(-c2 * (theta_deg - c1)))


def horizontal_nearest_pdf(x_horiz_m: float, lam_a: float) -> float:
    if x_horiz_m < 0.0:
        return 0.0
    return 2.0 * math.pi * lam_a * x_horiz_m * math.exp(
        -math.pi * lam_a * x_horiz_m * x_horiz_m
    )


def horizontal_distance_from_3d(r_m: float, h_m: float) -> float:
    return math.sqrt(max(r_m * r_m - h_m * h_m, 0.0))


def horizontal_distance_jacobian(r_m: float, h_m: float) -> float:
    return r_m / math.sqrt(r_m * r_m - h_m * h_m)


def distance_3d_pdf(r_m: float, lam_a: float, h_m: float) -> float:
    if r_m < h_m:
        return 0.0
    return 2.0 * math.pi * lam_a * r_m * math.exp(
        -math.pi * lam_a * (r_m * r_m - h_m * h_m)
    )


def rayleigh_laplace_kernel(a: float) -> float:
    return 1.0 / (1.0 + a)


def interferer_state_average(p_los: float, a_los: float, a_nlos: float) -> float:
    return (
        p_los * rayleigh_laplace_kernel(a_los)
        + (1.0 - p_los) * rayleigh_laplace_kernel(a_nlos)
    )


def serving_mixture(p_los: float, los_term: float, nlos_term: float) -> float:
    return p_los * los_term + (1.0 - p_los) * nlos_term


def s_parameter(beta: float, r_m: float, alpha: float, rho: float, p_u_w: float) -> float:
    return beta * r_m ** alpha / (rho * p_u_w)


def rate_log2(sinr: float) -> float:
    return math.log2(1.0 + sinr)


def average_rate_tail_integrand(coverage_probability_value: float, t: float) -> float:
    return coverage_probability_value / (1.0 + t)


def area_spectral_efficiency(lambda_u: float, p_act: float, rate_bps_per_hz: float) -> float:
    return lambda_u * p_act * rate_bps_per_hz


def hover_propulsion_power(p0_w: float, pi_w: float) -> float:
    return p0_w + pi_w


def total_power_density(
    lambda_u: float,
    p_act: float,
    p_u_w: float,
    p_op_w: float,
    p_prop_w: float,
) -> float:
    return lambda_u * (p_act * (p_u_w + p_op_w) + p_prop_w)


def energy_efficiency_simplified(
    p_act: float,
    rate_bps_per_hz: float,
    p_u_w: float,
    p_op_w: float,
    p_prop_w: float,
) -> float:
    return p_act * rate_bps_per_hz / (p_act * (p_u_w + p_op_w) + p_prop_w)


FORMULA_REGISTRY: dict[str, FormulaTrace] = {
    "Eq.1": FormulaTrace(
        "Eq.1",
        ("friis_reference_gain",),
        ("eq1_friis_matches_paper_ref",),
        LEAN_VERIFIED,
        ("d0_m != 0",),
        "Local Friis RHS check.",
    ),
    "Eq.2": FormulaTrace(
        "Eq.2",
        ("elevation_angle_degrees", "los_probability", "nlos_probability"),
        (
            "eq2_elevation_angle_matches_paper_ref_on_positive_horizontal_distance",
            "eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance",
            "eq2_nlos_probability_is_one_minus_los",
            "eq2_nlos_probability_matches_paper_ref_on_positive_horizontal_distance",
        ),
        LEAN_VERIFIED,
        ("x_horiz_m > 0 for paper RHS",),
        "Python keeps an endpoint convention at x=0.",
    ),
    "Eq.6": FormulaTrace(
        "Eq.6",
        ("horizontal_nearest_pdf",),
        ("eq6_horizontal_pdf_matches_paper_ref_on_support", "eq6_horizontal_pdf_zero_off_support"),
        LEAN_VERIFIED,
        ("x_horiz_m >= 0",),
        "PPP derivation is out of scope.",
    ),
    "Eq.7": FormulaTrace(
        "Eq.7",
        ("horizontal_distance_from_3d", "horizontal_distance_jacobian"),
        ("eq7_jacobian",),
        LEAN_VERIFIED,
        ("h_m > 0", "r_m > h_m for Jacobian formula"),
        "Transform helper is used by Python; Jacobian formula is the Lean-checked Eq.7 item.",
    ),
    "Eq.8": FormulaTrace(
        "Eq.8",
        ("distance_3d_pdf",),
        ("eq8_distance_pdf_matches_paper_ref_on_support", "eq8_distance_pdf_zero_off_support"),
        LEAN_VERIFIED,
        ("r_m >= h_m",),
        "Serving-distance law derivation is out of scope.",
    ),
    "Eq.15": FormulaTrace(
        "Eq.15",
        ("rayleigh_laplace_kernel",),
        ("eq15_definition_matches_paper_ref", "eq15_rayleigh_laplace_identity"),
        LEAN_VERIFIED,
        ("a >= 0 for integral identity",),
        "Local exponential integral identity, not a full probability framework.",
    ),
    "Eq.16": FormulaTrace(
        "Eq.16",
        ("interferer_state_average",),
        ("eq16_mixture_matches_paper_ref",),
        LEAN_VERIFIED,
        ("0 <= p_los <= 1",),
        "Interferer mixture over Rayleigh kernels.",
    ),
    "Eq.17": FormulaTrace(
        "Eq.17",
        ("laplace_interference",),
        ("laplaceInterference",),
        UNVERIFIED,
        (),
        "PGFL and Slivnyak derivation remain out of scope.",
    ),
    "Eq.18": FormulaTrace(
        "Eq.18",
        ("serving_mixture", "s_parameter"),
        ("eq18_serving_mixture_matches_paper_ref", "eq18_s_parameter_matches_paper_ref"),
        LEAN_VERIFIED,
        ("rho * p_u_w != 0",),
        "Conditional coverage also depends on Eq.17 spec.",
    ),
    "Eq.19": FormulaTrace(
        "Eq.19",
        ("coverage_probability",),
        ("coverageProbability",),
        UNVERIFIED,
        (),
        "Full coverage derivation remains out of scope.",
    ),
    "Eq.20": FormulaTrace(
        "Eq.20",
        ("rate_log2",),
        ("eq20_log2_matches_paper_ref",),
        LEAN_VERIFIED,
        ("1 + sinr > 0",),
        "Floating-point log accuracy is not proved.",
    ),
    "Eq.21": FormulaTrace(
        "Eq.21",
        ("average_rate_tail_integrand",),
        (
            "eq21_rate_tail_integral_identity",
            "Eq21HamdiChangeOfVariables",
            "eq21_hamdi_identity_from_change_of_variables",
        ),
        UNVERIFIED,
        ("t >= 0",),
        "Partially formalized: the layer-cake/CCDF sub-identity is proved, but "
        "the final Hamdi change of variables it relies on is assumed (a typed "
        "structure of hypotheses), not proved -- so the full rate identity is "
        "unverified.",
    ),
    "Eq.22": FormulaTrace(
        "Eq.22",
        ("average_rate",),
        ("averageRate",),
        UNVERIFIED,
        (),
        "SciPy quadrature correctness remains in Python methodology.",
    ),
    "Eq.23": FormulaTrace(
        "Eq.23",
        ("area_spectral_efficiency",),
        ("eq23_ase_activation_matches_paper_ref",),
        LEAN_VERIFIED,
        (),
        "Activation density algebra.",
    ),
    "Eq.24": FormulaTrace(
        "Eq.24",
        ("hover_propulsion_power",),
        ("eq24_hover_power_matches_paper_ref",),
        LEAN_VERIFIED,
        (),
        "Hover simplification at V=0.",
    ),
    "Eq.25": FormulaTrace(
        "Eq.25",
        ("total_power_density",),
        ("eq25_total_power_matches_paper_ref",),
        LEAN_VERIFIED,
        ("lambda_u != 0 for downstream cancellation",),
        "Total power density algebra.",
    ),
    "Eq.26": FormulaTrace(
        "Eq.26",
        ("energy_efficiency_simplified",),
        ("eq26_lambda_u_cancels_to_paper_ref", "eq26_simplified_definition_matches_paper_ref"),
        LEAN_VERIFIED,
        ("lambda_u != 0", "denominator != 0"),
        "Cancellation theorem, not a numerical guarantee.",
    ),
    "Eq.27": FormulaTrace(
        "Eq.27",
        ("laplace_interference_bounded", "coverage_probability_bounded", "average_rate_bounded"),
        ("laplaceInterferenceBounded", "coverageProbabilityBounded", "averageRateBounded"),
        UNVERIFIED,
        (),
        "Bounded Laplace/coverage/rate are named specs; bounded PGFL derivation remains out of scope.",
    ),
}
