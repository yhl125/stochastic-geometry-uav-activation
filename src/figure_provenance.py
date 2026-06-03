"""Figure-to-equation provenance for the UAV activation reproduction."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FigureProvenance:
    figure: int
    metric: str
    python_entry_points: tuple[str, ...]
    paper_equations: tuple[str, ...]
    lean_checked_equations: tuple[str, ...]
    boundary_equations: tuple[str, ...]
    notes: str


COVERAGE_KERNELS = ("Eq.2", "Eq.8", "Eq.15", "Eq.16", "Eq.18")
COVERAGE_BOUNDARIES = ("Eq.17", "Eq.19")
BOUNDED_COVERAGE_BOUNDARIES = ("Eq.17", "Eq.19", "Eq.27")
RATE_KERNELS = ("Eq.20",)
RATE_BOUNDARIES = ("Eq.17", "Eq.19", "Eq.21", "Eq.22")
BOUNDED_RATE_BOUNDARIES = ("Eq.17", "Eq.19", "Eq.21", "Eq.22", "Eq.27")
ENERGY_KERNELS = ("Eq.23", "Eq.24", "Eq.25", "Eq.26")


FIGURE_PROVENANCE: dict[int, FigureProvenance] = {
    2: FigureProvenance(
        2,
        "Coverage probability vs SINR threshold",
        (
            "figures.figure_2",
            "analytical.coverage_probability_bounded",
            "mc.simulate_sinr",
        ),
        COVERAGE_KERNELS + BOUNDED_COVERAGE_BOUNDARIES,
        COVERAGE_KERNELS,
        BOUNDED_COVERAGE_BOUNDARIES,
        (
            "Analytical curve uses the bounded Eq.27 path; Monte Carlo points "
            "remain Python numerical validation."
        ),
    ),
    3: FigureProvenance(
        3,
        "Coverage probability vs activation probability for bounded/unbounded schemes",
        (
            "figures.figure_3",
            "analytical.coverage_probability",
            "analytical.coverage_probability_bounded",
        ),
        COVERAGE_KERNELS + BOUNDED_COVERAGE_BOUNDARIES,
        COVERAGE_KERNELS,
        BOUNDED_COVERAGE_BOUNDARIES,
        "Compares bounded R0 schemes with an unbounded coverage reference.",
    ),
    4: FigureProvenance(
        4,
        "Coverage probability vs activation probability",
        ("figures.figure_4", "analytical.coverage_probability", "mc.simulate_sinr"),
        COVERAGE_KERNELS + COVERAGE_BOUNDARIES,
        COVERAGE_KERNELS,
        COVERAGE_BOUNDARIES,
        "Analytical coverage is unbounded; MC markers validate the numerical trend only.",
    ),
    5: FigureProvenance(
        5,
        "Coverage probability vs activation probability under altitude sweeps",
        ("figures.figure_5", "analytical.coverage_probability"),
        COVERAGE_KERNELS + COVERAGE_BOUNDARIES,
        COVERAGE_KERNELS,
        COVERAGE_BOUNDARIES,
        "Altitude enters LoS probability and serving-distance support assumptions.",
    ),
    6: FigureProvenance(
        6,
        "Coverage probability vs altitude",
        ("figures.figure_6", "analytical.coverage_probability"),
        COVERAGE_KERNELS + COVERAGE_BOUNDARIES,
        COVERAGE_KERNELS,
        COVERAGE_BOUNDARIES,
        (
            "The plotted H=0 endpoint is handled by Python methodology, not by "
            "the paper Eq.2 Lean theorem."
        ),
    ),
    7: FigureProvenance(
        7,
        "Coverage probability vs UAV density",
        ("figures.figure_7", "analytical.coverage_probability"),
        COVERAGE_KERNELS + COVERAGE_BOUNDARIES,
        COVERAGE_KERNELS,
        COVERAGE_BOUNDARIES,
        "Density sweeps reuse the same coverage integral boundary.",
    ),
    8: FigureProvenance(
        8,
        "Average achievable rate vs activation probability",
        ("figures.figure_8", "analytical.average_rate_bounded"),
        COVERAGE_KERNELS + RATE_KERNELS + BOUNDED_RATE_BOUNDARIES,
        COVERAGE_KERNELS + RATE_KERNELS,
        BOUNDED_RATE_BOUNDARIES,
        (
            "Rate is evaluated through the bounded Eq.27 path to match the "
            "finite simulation radius."
        ),
    ),
    9: FigureProvenance(
        9,
        "Average achievable rate vs activation probability under altitude sweeps",
        (
            "figures.figure_9",
            "analytical.average_rate",
            "figures._plot_rate",
            "figure_methodology.FIGURE_METHODS",
        ),
        COVERAGE_KERNELS + RATE_KERNELS + RATE_BOUNDARIES,
        COVERAGE_KERNELS + RATE_KERNELS,
        RATE_BOUNDARIES,
        (
            "The plot multiplier converts log2 formula output to the published "
            "natural-log scale as a Python methodology boundary."
        ),
    ),
    10: FigureProvenance(
        10,
        "Average achievable rate vs altitude",
        (
            "figures.figure_10",
            "analytical.average_rate",
            "figures._plot_rate",
            "figure_methodology.FIGURE_METHODS",
        ),
        COVERAGE_KERNELS + RATE_KERNELS + RATE_BOUNDARIES,
        COVERAGE_KERNELS + RATE_KERNELS,
        RATE_BOUNDARIES,
        (
            "The visible H=0 paper-axis endpoint and plot multiplier are handled "
            "as Python methodology boundary choices."
        ),
    ),
    11: FigureProvenance(
        11,
        "Average achievable rate vs UAV density",
        (
            "figures.figure_11",
            "analytical.average_rate",
            "figures._plot_rate",
            "figure_methodology.FIGURE_METHODS",
        ),
        COVERAGE_KERNELS + RATE_KERNELS + RATE_BOUNDARIES,
        COVERAGE_KERNELS + RATE_KERNELS,
        RATE_BOUNDARIES,
        (
            "Unbounded Eq.22 path with Python numerical quadrature; the plot "
            "multiplier is a Python methodology boundary."
        ),
    ),
    12: FigureProvenance(
        12,
        "Energy efficiency vs UAV density",
        (
            "figures.figure_12",
            "analytical.average_rate",
            "figures._plot_rate",
            "figure_methodology.FIGURE_METHODS",
            "analytical.energy_efficiency",
        ),
        COVERAGE_KERNELS + RATE_KERNELS + ENERGY_KERNELS + RATE_BOUNDARIES,
        COVERAGE_KERNELS + RATE_KERNELS + ENERGY_KERNELS,
        RATE_BOUNDARIES,
        (
            "Energy-efficiency algebra is Lean-verified, but Fig.12 passes the "
            "plot multiplier scaled rate into Eq.26 as a Python methodology "
            "boundary."
        ),
    ),
}
