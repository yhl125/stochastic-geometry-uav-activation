"""Paper-figure methodology choices.

This module is intentionally dependency-free so tests can validate figure
method choices without importing SciPy-heavy numerical code.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Union


BetaSetting = Union[float, tuple[float, ...], None]


class RateScale(Enum):
    LOG2 = "log2"
    NATURAL_LOG = "natural_log"


@dataclass(frozen=True)
class FigureMethod:
    fig: int
    metric: str
    equations: tuple[str, ...]
    xlim: tuple[float, float]
    x_values: tuple[float, ...]
    analytical_x_values: tuple[float, ...] | None = None
    mc_x_values: tuple[float, ...] | None = None
    equation_x_values: tuple[float, ...] | None = None
    beta_db: BetaSetting = None
    formula_rate_scale: RateScale | None = None
    plot_rate_scale: RateScale | None = None
    bounded_radius_m: float | None = None
    rate_t_max: float | None = None
    unbounded_beta_db: float | None = None
    notes: str = ""

    @property
    def plot_multiplier(self) -> float:
        """Multiplier from formula rate units to published plot units."""
        if self.formula_rate_scale is None or self.plot_rate_scale is None:
            return 1.0
        if self.formula_rate_scale == self.plot_rate_scale:
            return 1.0
        if (self.formula_rate_scale == RateScale.LOG2
                and self.plot_rate_scale == RateScale.NATURAL_LOG):
            return math.log(2.0)
        if (self.formula_rate_scale == RateScale.NATURAL_LOG
                and self.plot_rate_scale == RateScale.LOG2):
            return 1.0 / math.log(2.0)
        raise ValueError(
            f"unsupported rate-scale conversion: "
            f"{self.formula_rate_scale} -> {self.plot_rate_scale}"
        )


def _linspace(start: float, stop: float, count: int) -> tuple[float, ...]:
    if count < 2:
        return (float(start),)
    step = (stop - start) / (count - 1)
    return tuple(float(start + i * step) for i in range(count))


def _without_origin(values: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(value for value in values if value > 0.0)


FIGURE_METHODS: dict[int, FigureMethod] = {
    2: FigureMethod(
        fig=2,
        metric="coverage",
        equations=("Eq.19", "Eq.27"),
        xlim=(-10.0, 20.0),
        x_values=_linspace(-10.0, 20.0, 31),
        bounded_radius_m=10.0e3,
        notes="Analytical Eq.19 uses the Table-1 10 km finite-radius limit so MC and analytical share the same simulation window.",
    ),
    3: FigureMethod(
        fig=3,
        metric="coverage",
        equations=("Eq.19", "Eq.27"),
        xlim=(0.0, 1.0),
        x_values=_without_origin(_linspace(0.0, 1.0, 21)),
        beta_db=3.0,
        unbounded_beta_db=5.5,
        notes="Bounded benchmarks use the printed beta=3 dB; the published unbounded/fixed benchmark levels visually align with beta≈5.5 dB.",
    ),
    4: FigureMethod(
        fig=4,
        metric="coverage",
        equations=("Eq.19",),
        xlim=(0.0, 1.0),
        x_values=_without_origin(_linspace(0.0, 1.0, 41)),
        beta_db=(-5.0, 0.0, 5.0),
        notes="Analytical no-shadowing curves plus sigma=4 dB shadowing MC overlay; p_act=0 is omitted from computed curves.",
    ),
    5: FigureMethod(
        fig=5,
        metric="coverage",
        equations=("Eq.19",),
        xlim=(0.0, 1.0),
        x_values=_without_origin(_linspace(0.0, 1.0, 21)),
        beta_db=2.0,
        notes="Published Fig.5 values/crossings align with beta≈2 dB rather than the Table-1 default; p_act=0 is omitted from computed curves.",
    ),
    6: FigureMethod(
        fig=6,
        metric="coverage",
        equations=("Eq.19",),
        xlim=(0.0, 200.0),
        x_values=_linspace(0.0, 200.0, 41),
        beta_db=2.0,
        notes="Published Fig.6 values/crossings align with beta≈2 dB; altitude sweep includes the visible paper x-axis origin.",
    ),
    7: FigureMethod(
        fig=7,
        metric="coverage",
        equations=("Eq.19",),
        xlim=(0.0, 50.0),
        x_values=_without_origin(_linspace(0.0, 50.0, 51)),
        beta_db=2.0,
        notes="Published Fig.7 values/crossings align with beta≈2 dB; axis includes origin but density=0 is omitted from computed curves.",
    ),
    8: FigureMethod(
        fig=8,
        metric="rate",
        equations=("Eq.22", "Eq.27"),
        xlim=(0.0, 1.0),
        x_values=_without_origin(_linspace(0.0, 1.0, 51)),
        analytical_x_values=_without_origin(_linspace(0.0, 1.0, 51)),
        mc_x_values=_without_origin(_linspace(0.0, 1.0, 21)),
        formula_rate_scale=RateScale.LOG2,
        plot_rate_scale=RateScale.LOG2,
        bounded_radius_m=10.0e3,
        rate_t_max=100.0,
        notes="Published Fig.8 matches bounded Eq.27 at the 10 km Table-1 radius and a shared t_max=100 rate cap for analytical and MC.",
    ),
    9: FigureMethod(
        fig=9,
        metric="rate",
        equations=("Eq.22",),
        xlim=(0.0, 1.0),
        x_values=_without_origin(_linspace(0.0, 1.0, 101)),
        formula_rate_scale=RateScale.LOG2,
        plot_rate_scale=RateScale.NATURAL_LOG,
        notes="Eq.22 is log2; published Fig.9 scale matches ln(1+SINR); p_act=0 is omitted from computed curves.",
    ),
    10: FigureMethod(
        fig=10,
        metric="rate",
        equations=("Eq.22",),
        xlim=(0.0, 200.0),
        x_values=_linspace(0.0, 200.0, 41),
        formula_rate_scale=RateScale.LOG2,
        plot_rate_scale=RateScale.NATURAL_LOG,
        notes="Altitude sweep includes origin; published scale matches natural log.",
    ),
    11: FigureMethod(
        fig=11,
        metric="rate",
        equations=("Eq.22",),
        xlim=(0.0, 50.0),
        x_values=_without_origin(_linspace(0.0, 50.0, 26)),
        formula_rate_scale=RateScale.LOG2,
        plot_rate_scale=RateScale.NATURAL_LOG,
        notes="Axis includes origin; density=0 is omitted from computed curves; published scale matches natural log.",
    ),
    12: FigureMethod(
        fig=12,
        metric="energy_efficiency",
        equations=("Eq.22", "Eq.23", "Eq.25", "Eq.26"),
        xlim=(0.0, 50.0),
        x_values=tuple(float(x) / 2.0 for x in range(5, 105, 5)),
        equation_x_values=tuple(float(x) / 2.0 for x in range(5, 105, 5)),
        formula_rate_scale=RateScale.LOG2,
        plot_rate_scale=RateScale.NATURAL_LOG,
        notes="EE uses Eq.26; axis includes origin but density=0 is omitted; 2.5/km² grid captures the published 0-5 initial shape.",
    ),
}
