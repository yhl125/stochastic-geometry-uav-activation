"""Figure generators for the four locked reproduction targets.

Each generator returns the curve data as numpy arrays and saves a CSV + PNG.
Figures correspond to:
  - Fig. 2:  coverage vs SINR threshold β, curves over p_act ∈ {0.1, 0.5, 0.9}.
  - Fig. 4:  coverage vs p_act, curves over β ∈ {-5, 0, 5} dB.
  - Fig. 8:  rate vs p_act, curves over λ_u ∈ {2, 5, 10}/km².
  - Fig. 12: EE vs λ_u, curves over p_act ∈ {0.2, 0.6, 1.0}.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import params as P
from analytical import (
    coverage_probability,
    coverage_probability_bounded,
    average_rate,
    average_rate_bounded,
    energy_efficiency,
)
from figure_methodology import FIGURE_METHODS

# Paper Fig 8 analytical curves match Eq.22 with the Eq.27-style bounded
# interferer limit at R_0 = 10 km (= Table 1 simulation area radius). Fig 9-12
# keep the unbounded Eq.22 shape; their published y-scale is empirically closer
# to the natural-log integral, so figure_methodology.py applies that scale only
# at the plotting layer.
from mc import coverage_mc, rate_mc, simulate_sinr


@dataclass
class FigureOutputs:
    outputs_dir: Path
    iters: int
    seed: int
    save_csv: bool = True
    save_png: bool = True

    def __post_init__(self) -> None:
        self.outputs_dir.mkdir(parents=True, exist_ok=True)


def _save_curve_csv(path: Path, header: list[str],
                    columns: list[np.ndarray]) -> None:
    arr = np.column_stack(columns)
    np.savetxt(path, arr, delimiter=",",
               header=",".join(header), comments="", fmt="%.6g")


def _method_x(fig: int) -> np.ndarray:
    return np.array(FIGURE_METHODS[fig].x_values, dtype=float)


def _beta_linear(fig: int) -> float:
    beta_db = FIGURE_METHODS[fig].beta_db
    if not isinstance(beta_db, float):
        raise ValueError(f"Fig. {fig} does not have a scalar beta setting")
    return 10.0 ** (beta_db / 10.0)


def _altitude_for_integral(h_m: float) -> float:
    # H=0 is a visible paper-axis endpoint. Use a tiny positive value to avoid
    # the singular lower integration bound while preserving the plotted limit.
    return max(float(h_m), 1.0e-6)


def _plot_rate(fig: int, rate_log2: float) -> float:
    return rate_log2 * FIGURE_METHODS[fig].plot_multiplier


def _condition_seed(base_seed: int, fig: int, *indices: int) -> int:
    seed = int(base_seed) + fig * 100_000
    for position, value in enumerate(indices, start=1):
        seed += position * 10_000 + int(value) * 1_009
    return seed


def _left_anchored_xy(x: np.ndarray, y: np.ndarray,
                      x_left: float) -> tuple[np.ndarray, np.ndarray]:
    """Add a plot-only left-edge anchor without changing computed grid data."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) == 0 or x[0] <= x_left:
        return x, y

    if len(x) >= 2 and x[1] != x[0]:
        slope = (y[1] - y[0]) / (x[1] - x[0])
        y_left = y[0] - slope * (x[0] - x_left)
    else:
        y_left = y[0]
    if not np.isfinite(y_left):
        y_left = y[0]
    y_left = max(0.0, float(y_left))
    return np.concatenate(([x_left], x)), np.concatenate(([y_left], y))


def _plot_line(ax: plt.Axes, fig: int, x: np.ndarray, y: np.ndarray,
               **kwargs):
    x_plot, y_plot = _left_anchored_xy(x, y, FIGURE_METHODS[fig].xlim[0])
    return ax.plot(x_plot, y_plot, **kwargs)


def _pad_array(values: np.ndarray, length: int) -> np.ndarray:
    out = np.full(length, np.nan)
    out[: len(values)] = values
    return out


_PAPER_COLORS = ["#0072BD", "#D95319", "#EDB120"]  # MATLAB default trio
_PAPER_MARKERS = ["o", "s", "^"]


def figure_2(opts: FigureOutputs) -> None:
    """Coverage vs SINR threshold β for p_act ∈ {0.1, 0.5, 0.9}."""
    print("=== Fig. 2: coverage vs β ===")
    method = FIGURE_METHODS[2]
    betas_db = _method_x(2)
    betas_lin = 10.0 ** (betas_db / 10.0)
    p_acts = [0.1, 0.5, 0.9]
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2

    fig, ax = plt.subplots(figsize=(6.5, 4.5))

    csv_cols = [betas_db]
    csv_hdr = ["beta_dB"]

    for p_idx, (color, marker, p) in enumerate(zip(_PAPER_COLORS,
                                                   _PAPER_MARKERS, p_acts)):
        t0 = time.time()
        mc_res = simulate_sinr(
            lam_u, p, n_iters=opts.iters,
            seed=_condition_seed(opts.seed, 2, p_idx),
        )
        cov_mc = np.array([coverage_mc(mc_res, b) for b in betas_lin])
        t1 = time.time()
        lam_a = lam_u * p
        cov_an = np.array([
            coverage_probability_bounded(
                b, lam_a, float(method.bounded_radius_m)
            )
            for b in betas_lin
        ])
        t2 = time.time()
        print(f"  p_act={p:.1f}: MC {t1-t0:.1f}s, analytical {t2-t1:.1f}s, "
              f"no-active {mc_res.no_active_count}/{mc_res.n_iters}")

        ax.plot(betas_db, cov_an, color=color, linewidth=1.5,
                label=f"Analytical $p_{{act}} = {p}$")
        ax.plot(betas_db, cov_mc, color=color, linestyle="", marker=marker,
                markersize=5, markerfacecolor="none", markeredgewidth=1.2,
                label=f"MC $p_{{act}} = {p}$")
        csv_cols += [cov_an, cov_mc]
        csv_hdr += [f"P_c_analytical_p{p}", f"P_c_mc_p{p}"]

    ax.set_xlabel(r"SINR Threshold $\beta$ (dB)")
    ax.set_ylabel(r"Coverage Probability $P_c$")
    ax.set_title("Coverage Probability vs SINR Threshold "
                 "(Different Activation Probability)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(-10.0, 20.0)
    ax.set_ylim(0.0, 0.6)

    if opts.save_png:
        png = opts.outputs_dir / "fig2_coverage_vs_threshold.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig2_coverage_vs_threshold.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_3(opts: FigureOutputs) -> None:
    """Coverage vs p_act for proposed (bounded R_0={3,5,10,20}km, unbounded) +
    fixed-p_act benchmarks (p_act=0.5, 1.0, unbounded), all analytical.

    Paper Fig 3 y-axis label embeds "β=3 dB". β=3dB gives bounded-curve
    peak heights matching paper visual (R_0=3km peak 0.27, R_0=5km 0.26,
    R_0=10km 0.25, R_0=20km 0.24 vs paper ~0.27, 0.25, 0.22, 0.20).
    """
    print("=== Fig. 3: coverage vs p_act (schemes) ===")
    method = FIGURE_METHODS[3]
    p_acts = _method_x(3)
    beta_lin = _beta_linear(3)
    beta_unbounded_db = method.unbounded_beta_db
    beta_unbounded_lin = (
        10.0 ** (beta_unbounded_db / 10.0)
        if beta_unbounded_db is not None else beta_lin
    )
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    csv_cols = [p_acts]
    csv_hdr = ["p_act"]

    R0_list_km = [3.0, 5.0, 10.0, 20.0]
    bounded_colors = ["#0072BD", "#D95319", "#EDB120", "#7E2F8E"]
    for color, R0_km in zip(bounded_colors, R0_list_km):
        R0_m = R0_km * 1.0e3
        cov_b = np.zeros_like(p_acts)
        t0 = time.time()
        for i, p in enumerate(p_acts):
            cov_b[i] = coverage_probability_bounded(beta_lin, lam_u * p, R0_m)
        print(f"  bounded R_0={R0_km:.0f}km: {time.time()-t0:.1f}s, "
              f"peak {cov_b.max():.3f} @ p_act={p_acts[cov_b.argmax()]:.2f}")
        _plot_line(ax, 3, p_acts, cov_b, color=color, linewidth=1.5,
                   marker="o", markersize=4, markerfacecolor="none",
                   markeredgewidth=1.0,
                   label=f"Distance-threshold, $R_0={R0_km:.0f}$ km")
        csv_cols.append(cov_b)
        csv_hdr.append(f"P_c_bounded_R0_{int(R0_km)}km")

    cov_unb = np.zeros_like(p_acts)
    t0 = time.time()
    for i, p in enumerate(p_acts):
        cov_unb[i] = coverage_probability(beta_unbounded_lin, lam_u * p)
    print(f"  unbounded: {time.time()-t0:.1f}s, "
          f"peak {cov_unb.max():.3f} @ p_act={p_acts[cov_unb.argmax()]:.2f}")
    _plot_line(ax, 3, p_acts, cov_unb, color="#77AC30", linewidth=1.6,
               linestyle="--", label="Proposed (unbounded)")
    csv_cols.append(cov_unb)
    csv_hdr.append("P_c_unbounded")

    cov_fixed_05 = float(coverage_probability(beta_unbounded_lin, lam_u * 0.5))
    cov_fixed_10 = float(coverage_probability(beta_unbounded_lin, lam_u * 1.0))
    print(f"  fixed p_act=0.5 (unbounded): P_c={cov_fixed_05:.3f}")
    print(f"  fixed p_act=1.0 (unbounded): P_c={cov_fixed_10:.3f}")
    ax.axhline(cov_fixed_05, color="black", linestyle=":", linewidth=1.2,
               label=f"Fixed $p_{{act}}=0.5$ (unbounded), $P_c={cov_fixed_05:.3f}$")
    ax.axhline(cov_fixed_10, color="gray", linestyle="-.", linewidth=1.2,
               label=f"Fixed $p_{{act}}=1.0$ (unbounded), $P_c={cov_fixed_10:.3f}$")
    csv_cols.append(np.full_like(p_acts, cov_fixed_05))
    csv_hdr.append("P_c_fixed_p_act_0.5")
    csv_cols.append(np.full_like(p_acts, cov_fixed_10))
    csv_hdr.append("P_c_fixed_p_act_1.0")

    ax.set_xlabel(r"Activation probability $p_{act}$")
    ax.set_ylabel(r"Coverage probability $P_c$ ($\beta=+3$ dB)")
    ax.set_title("Coverage Probability for Different Proposed and Benchmark Schemes",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=7)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.arange(0.0, 1.05, 0.1))
    ax.set_ylim(0.0, 0.4)

    if opts.save_png:
        png = opts.outputs_dir / "fig3_coverage_vs_pact_schemes.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig3_coverage_vs_pact_schemes.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_4(opts: FigureOutputs) -> None:
    """Coverage vs p_act for β ∈ {-5, 0, 5} dB.

    Paper Fig 4: analytical line = no shadowing (Eq. 19), MC dots = σ=4 dB
    log-normal shadowing overlay (per-link i.i.d.).
    """
    print("=== Fig. 4: coverage vs p_act (with σ=4dB shadowing MC) ===")
    p_acts = _method_x(4)
    betas_db = [-5.0, 0.0, 5.0]
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2
    sigma_db = 4.0

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [p_acts]
    csv_hdr = ["p_act"]

    cov_an_by_beta = {bdb: np.zeros_like(p_acts) for bdb in betas_db}
    cov_mc_by_beta = {bdb: np.zeros_like(p_acts) for bdb in betas_db}
    t0 = time.time()
    for p_idx, p in enumerate(p_acts):
        mc_res = simulate_sinr(
            lam_u, p, n_iters=opts.iters,
            seed=_condition_seed(opts.seed, 4, p_idx),
            sigma_shadow_db=sigma_db,
        )
        for bdb in betas_db:
            b_lin = 10.0 ** (bdb / 10.0)
            cov_mc_by_beta[bdb][p_idx] = coverage_mc(mc_res, b_lin)
            cov_an_by_beta[bdb][p_idx] = coverage_probability(b_lin, lam_u * p)

    for color, marker, bdb in zip(_PAPER_COLORS, _PAPER_MARKERS, betas_db):
        cov_mc = cov_mc_by_beta[bdb]
        cov_an = cov_an_by_beta[bdb]
        i_peak_an = int(np.argmax(cov_an))
        print(f"  β={bdb:+.0f}dB: {time.time()-t0:.1f}s, "
              f"analytical peak @ p_act={p_acts[i_peak_an]:.2f} "
              f"(P_c_no-shad={cov_an[i_peak_an]:.3f}, "
              f"P_c_shad-MC peak={cov_mc.max():.3f})")

        _plot_line(ax, 4, p_acts, cov_an, color=color, linewidth=1.5,
                   label=f"No shadowing, $\\beta = {bdb:+.0f}$ dB")
        ax.plot(p_acts, cov_mc, color=color, linestyle="", marker=marker,
                markersize=4, markerfacecolor="none", markeredgewidth=1.1,
                label=f"Shadowing $\\sigma=4$ dB (MC), $\\beta = {bdb:+.0f}$ dB")
        csv_cols += [cov_an, cov_mc]
        csv_hdr += [f"P_c_analytical_no_shadowing_b{bdb:+.0f}dB",
                    f"P_c_mc_shadowing_4dB_b{bdb:+.0f}dB"]

    ax.set_xlabel(r"Activation probability $p_{act}$")
    ax.set_ylabel(r"Coverage probability $P_c$")
    ax.set_title("Coverage Probability vs. Activation Probability "
                 "(With and w/o Shadowing)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.arange(0.0, 1.05, 0.1))
    ax.set_ylim(0.0, 0.6)

    if opts.save_png:
        png = opts.outputs_dir / "fig4_coverage_vs_pact.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig4_coverage_vs_pact.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_5(opts: FigureOutputs) -> None:
    """Coverage vs p_act for H ∈ {40, 80, 120} m, analytical only.

    Published curves align with β≈2dB even though Table 1 lists a 0dB default.
    """
    print("=== Fig. 5: coverage vs p_act (H sweep, β=2dB) ===")
    p_acts = _method_x(5)
    altitudes_m = [40.0, 80.0, 120.0]
    beta_lin = _beta_linear(5)
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [p_acts]
    csv_hdr = ["p_act"]

    for color, marker, h_m in zip(_PAPER_COLORS, _PAPER_MARKERS, altitudes_m):
        cov_an = np.zeros_like(p_acts)
        t0 = time.time()
        for i, p in enumerate(p_acts):
            cov_an[i] = coverage_probability(beta_lin, lam_u * p, h_m=h_m)
        i_peak = int(np.argmax(cov_an))
        print(f"  H={h_m:.0f}m: {time.time()-t0:.1f}s, "
              f"peak @ p_act={p_acts[i_peak]:.2f} (P_c={cov_an[i_peak]:.3f})")
        _plot_line(ax, 5, p_acts, cov_an, color=color, linewidth=1.5,
                   marker=marker, markersize=5, markerfacecolor="none",
                   markeredgewidth=1.1, label=f"$H = {h_m:.0f}$ m")
        csv_cols.append(cov_an)
        csv_hdr.append(f"P_c_H_{int(h_m)}m")

    ax.set_xlabel(r"Activation probability $p_{act}$")
    ax.set_ylabel(r"Coverage probability $P_c$")
    ax.set_title("Analytical Coverage Probability vs. Activation Probability "
                 "(Different Altitude)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.arange(0.0, 1.05, 0.1))
    ax.set_ylim(0.0, 0.4)

    if opts.save_png:
        png = opts.outputs_dir / "fig5_coverage_vs_pact_altitude.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig5_coverage_vs_pact_altitude.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_6(opts: FigureOutputs) -> None:
    """Coverage vs UAV altitude H for p_act ∈ {0.2, 0.6, 1.0}, analytical only.

    Published curves align with β≈2dB even though Table 1 lists a 0dB default."""
    print("=== Fig. 6: coverage vs H (β=2dB) ===")
    altitudes_m = _method_x(6)
    p_acts = [0.2, 0.6, 1.0]
    beta_lin = _beta_linear(6)
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [altitudes_m]
    csv_hdr = ["H_m"]

    for color, marker, p in zip(_PAPER_COLORS, _PAPER_MARKERS, p_acts):
        cov_an = np.zeros_like(altitudes_m)
        t0 = time.time()
        for i, h_m in enumerate(altitudes_m):
            cov_an[i] = coverage_probability(beta_lin, lam_u * p,
                                             h_m=_altitude_for_integral(h_m))
        i_peak = int(np.argmax(cov_an))
        print(f"  p_act={p:.1f}: {time.time()-t0:.1f}s, "
              f"peak @ H={altitudes_m[i_peak]:.0f}m (P_c={cov_an[i_peak]:.3f})")
        ax.plot(altitudes_m, cov_an, color=color, linewidth=1.5,
                marker=marker, markersize=5, markerfacecolor="none",
                markeredgewidth=1.1, label=f"$p_{{act}}={p}$")
        csv_cols.append(cov_an)
        csv_hdr.append(f"P_c_p_act_{p}")

    ax.set_xlabel(r"UAV altitude $H$ (m)")
    ax.set_ylabel(r"Coverage probability $P_c$")
    ax.set_title("Coverage Probability vs. UAV Altitude (Different Activation)",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_xlim(0.0, 200.0)
    ax.set_xticks(np.arange(0, 220, 20))
    ax.set_ylim(0.0, 0.4)

    if opts.save_png:
        png = opts.outputs_dir / "fig6_coverage_vs_altitude.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig6_coverage_vs_altitude.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_7(opts: FigureOutputs) -> None:
    """Coverage vs UAV density λ_u for p_act ∈ {0.2, 0.6, 1.0}, analytical only.

    Published curves align with β≈2dB even though Table 1 lists a 0dB default."""
    print("=== Fig. 7: coverage vs λ_u (β=2dB) ===")
    densities_per_km2 = _method_x(7)
    p_acts = [0.2, 0.6, 1.0]
    beta_lin = _beta_linear(7)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [densities_per_km2]
    csv_hdr = ["lambda_u_per_km2"]

    for color, marker, p in zip(_PAPER_COLORS, _PAPER_MARKERS, p_acts):
        cov_an = np.zeros_like(densities_per_km2)
        t0 = time.time()
        for i, d in enumerate(densities_per_km2):
            lam_u = d * 1.0e-6
            cov_an[i] = coverage_probability(beta_lin, lam_u * p)
        i_peak = int(np.argmax(cov_an))
        print(f"  p_act={p:.1f}: {time.time()-t0:.1f}s, "
              f"peak @ λ_u={densities_per_km2[i_peak]:.0f}/km² "
              f"(P_c={cov_an[i_peak]:.3f})")
        _plot_line(ax, 7, densities_per_km2, cov_an, color=color,
                   linewidth=1.5, marker=marker, markersize=5,
                   markerfacecolor="none", markeredgewidth=1.1,
                   label=f"$p_{{act}}={p}$")
        csv_cols.append(cov_an)
        csv_hdr.append(f"P_c_p_act_{p}")

    ax.set_xlabel(r"UAV density $\lambda_u$ (UAVs/km²)")
    ax.set_ylabel(r"Coverage probability $P_c$")
    ax.set_title("Coverage Probability vs. UAV Density (Different Activation)",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_xlim(0.0, 50.0)
    ax.set_xticks(np.arange(0, 55, 5))
    ax.set_ylim(0.0, 0.4)

    if opts.save_png:
        png = opts.outputs_dir / "fig7_coverage_vs_density.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig7_coverage_vs_density.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_8(opts: FigureOutputs) -> None:
    """Rate vs p_act for λ_u ∈ {2, 5, 10}/km²."""
    print("=== Fig. 8: rate vs p_act ===")
    method = FIGURE_METHODS[8]
    p_acts_an = np.array(method.analytical_x_values, dtype=float)
    p_acts_mc = np.array(method.mc_x_values, dtype=float)
    densities_per_km2 = [2.0, 5.0, 10.0]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_len = max(len(p_acts_an), len(p_acts_mc))
    csv_cols = [_pad_array(p_acts_an, csv_len), _pad_array(p_acts_mc, csv_len)]
    csv_hdr = ["p_act_analytical", "p_act_mc"]

    rate_cap = float(method.rate_t_max) if method.rate_t_max is not None else None
    for d_idx, (color, marker, d_km2) in enumerate(
        zip(_PAPER_COLORS, _PAPER_MARKERS, densities_per_km2)
    ):
        lam_u = d_km2 * 1.0e-6
        rate_mc_arr = np.zeros_like(p_acts_mc)
        rate_an_arr = np.zeros_like(p_acts_an)
        t0 = time.time()
        for i, p in enumerate(p_acts_mc):
            mc_res = simulate_sinr(
                lam_u, p, n_iters=opts.iters,
                seed=_condition_seed(opts.seed, 8, d_idx, i),
            )
            rate_mc_arr[i] = rate_mc(mc_res, sinr_cap=rate_cap)
        for i, p in enumerate(p_acts_an):
            rate_an_arr[i] = average_rate_bounded(
                lam_u * p, float(method.bounded_radius_m),
                t_max=float(method.rate_t_max),
            )
        print(f"  λ_u={d_km2:.0f}/km²: {time.time()-t0:.1f}s")
        _plot_line(ax, 8, p_acts_an, rate_an_arr, color=color, linewidth=1.8,
                   label=f"Analytical, $\\lambda_u={d_km2:.0f}$/km²")
        ax.plot(p_acts_mc, rate_mc_arr, color=color, linestyle="", marker=marker,
                markersize=5, markerfacecolor="none", markeredgewidth=1.2,
                label=f"MC, $\\lambda_u={d_km2:.0f}$/km²")
        csv_cols += [_pad_array(rate_an_arr, csv_len), _pad_array(rate_mc_arr, csv_len)]
        csv_hdr += [f"R_analytical_d{int(d_km2)}",
                    f"R_mc_d{int(d_km2)}"]

    ax.set_xlabel(r"Activation probability $p_{act}$")
    ax.set_ylabel(r"Average Achievable Rate $\mathcal{R}$ (bps/Hz)")
    ax.set_title("Average Rate vs. Activation Probability "
                 "(Different UAV Density)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8, ncol=2)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.arange(0.0, 1.05, 0.1))
    ax.set_ylim(0.3, 1.2)

    if opts.save_png:
        png = opts.outputs_dir / "fig8_rate_vs_pact.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig8_rate_vs_pact.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_9(opts: FigureOutputs) -> None:
    """Rate vs p_act for H ∈ {40, 80, 120} m, analytical only.

    Rate uses Eq.22 CCDF integration; Table 1 defaults apply otherwise."""
    print("=== Fig. 9: rate vs p_act (H sweep) ===")
    p_acts = _method_x(9)
    altitudes_m = [40.0, 80.0, 120.0]
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [p_acts]
    csv_hdr = ["p_act"]

    for color, marker, h_m in zip(_PAPER_COLORS, _PAPER_MARKERS, altitudes_m):
        rate_an = np.zeros_like(p_acts)
        t0 = time.time()
        for i, p in enumerate(p_acts):
            rate_an[i] = _plot_rate(9, average_rate(lam_u * p, h_m=h_m))
        print(f"  H={h_m:.0f}m: {time.time()-t0:.1f}s, "
              f"peak R={rate_an.max():.3f} @ p_act={p_acts[rate_an.argmax()]:.2f}")
        _plot_line(ax, 9, p_acts, rate_an, color=color, linewidth=1.5,
                   marker=marker, markersize=5, markerfacecolor="none",
                   markeredgewidth=1.1, label=f"$H = {h_m:.0f}$ m")
        csv_cols.append(rate_an)
        csv_hdr.append(f"R_H_{int(h_m)}m")

    ax.set_xlabel(r"Activation probability $p_{act}$")
    ax.set_ylabel(r"Average Achievable Rate $\mathcal{R}$ (bps/Hz)")
    ax.set_title("Average Rate vs. Activation Probability (Different UAV Altitude)",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.arange(0.0, 1.05, 0.1))
    ax.set_ylim(0.0, 0.7)

    if opts.save_png:
        png = opts.outputs_dir / "fig9_rate_vs_pact_altitude.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig9_rate_vs_pact_altitude.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_10(opts: FigureOutputs) -> None:
    """Rate vs H for p_act ∈ {0.2, 0.6, 1.0}, analytical only.

    Rate uses Eq.22 CCDF integration; Table 1 defaults apply otherwise."""
    print("=== Fig. 10: rate vs H ===")
    altitudes_m = _method_x(10)
    p_acts = [0.2, 0.6, 1.0]
    lam_u = P.LAMBDA_U_DEFAULT_PER_M2

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [altitudes_m]
    csv_hdr = ["H_m"]

    for color, marker, p in zip(_PAPER_COLORS, _PAPER_MARKERS, p_acts):
        rate_an = np.zeros_like(altitudes_m)
        t0 = time.time()
        for i, h_m in enumerate(altitudes_m):
            rate_an[i] = _plot_rate(
                10,
                average_rate(lam_u * p, h_m=_altitude_for_integral(h_m)),
            )
        print(f"  p_act={p:.1f}: {time.time()-t0:.1f}s, "
              f"peak R={rate_an.max():.3f} @ H={altitudes_m[rate_an.argmax()]:.0f}m")
        ax.plot(altitudes_m, rate_an, color=color, linewidth=1.5,
                marker=marker, markersize=5, markerfacecolor="none",
                markeredgewidth=1.1, label=f"$p_{{act}}={p}$")
        csv_cols.append(rate_an)
        csv_hdr.append(f"R_p_act_{p}")

    ax.set_xlabel(r"UAV altitude $H$ (m)")
    ax.set_ylabel(r"Average Achievable Rate $\mathcal{R}$ (bps/Hz)")
    ax.set_title("Average Rate vs. UAV Altitude (Different Activation)",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim(0.0, 200.0)
    ax.set_xticks(np.arange(0, 220, 20))
    ax.set_ylim(0.0, 0.7)

    if opts.save_png:
        png = opts.outputs_dir / "fig10_rate_vs_altitude.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig10_rate_vs_altitude.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_11(opts: FigureOutputs) -> None:
    """Rate vs UAV density λ_u for p_act ∈ {0.2, 0.6, 1.0}, analytical only.

    Rate uses Eq.22 CCDF integration; Table 1 defaults apply otherwise.

    KEY: Compare (λ_u=10, p_act=1.0) result with Fig 8's same-point value to
    verify whether paper's Fig 8/11 internal inconsistency is reproduced or
    resolved by our unbounded analytical.
    """
    print("=== Fig. 11: rate vs λ_u ===")
    densities_per_km2 = _method_x(11)
    p_acts = [0.2, 0.6, 1.0]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [densities_per_km2]
    csv_hdr = ["lambda_u_per_km2"]

    for color, marker, p in zip(_PAPER_COLORS, _PAPER_MARKERS, p_acts):
        rate_an = np.zeros_like(densities_per_km2)
        t0 = time.time()
        for i, d in enumerate(densities_per_km2):
            lam_u = d * 1.0e-6
            rate_an[i] = _plot_rate(11, average_rate(lam_u * p))
        print(f"  p_act={p:.1f}: {time.time()-t0:.1f}s, "
              f"peak R={rate_an.max():.3f} @ "
              f"λ_u={densities_per_km2[rate_an.argmax()]:.0f}/km²; "
              f"R(λ_u=10/km²)={rate_an[densities_per_km2.tolist().index(10.0) if 10.0 in densities_per_km2 else int(np.argmin(abs(densities_per_km2-10)))]:.3f}")
        _plot_line(ax, 11, densities_per_km2, rate_an, color=color,
                   linewidth=1.5, marker=marker, markersize=5,
                   markerfacecolor="none", markeredgewidth=1.1,
                   label=f"$p_{{act}}={p}$")
        csv_cols.append(rate_an)
        csv_hdr.append(f"R_p_act_{p}")

    ax.set_xlabel(r"UAV density $\lambda_u$ (UAVs/km²)")
    ax.set_ylabel(r"Average Achievable Rate $\mathcal{R}$ (bps/Hz)")
    ax.set_title("Average Rate vs. UAV Density (Different Activation)",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_xlim(0.0, 50.0)
    ax.set_xticks(np.arange(0, 55, 5))
    ax.set_ylim(0.2, 0.7)

    if opts.save_png:
        png = opts.outputs_dir / "fig11_rate_vs_density.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig11_rate_vs_density.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")


def figure_12(opts: FigureOutputs) -> None:
    """Energy efficiency vs λ_u for p_act ∈ {0.2, 0.6, 1.0}.

    Analytical-only by default (rate computation is the slow inner loop)."""
    print("=== Fig. 12: EE vs λ_u ===")
    densities_per_km2 = _method_x(12)
    p_acts = [0.2, 0.6, 1.0]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    csv_cols = [densities_per_km2]
    csv_hdr = ["lambda_u_per_km2"]

    for color, marker, p in zip(_PAPER_COLORS, _PAPER_MARKERS, p_acts):
        ee_arr = np.zeros_like(densities_per_km2)
        t0 = time.time()
        for i, d in enumerate(densities_per_km2):
            lam_u = d * 1.0e-6
            r = _plot_rate(12, average_rate(lam_u * p))
            ee_arr[i] = energy_efficiency(lam_u, p, rate_bps_per_hz=r)
        print(f"  p_act={p:.1f}: {time.time()-t0:.1f}s, "
              f"EE range [{ee_arr.min():.3g}, {ee_arr.max():.3g}]")
        _plot_line(ax, 12, densities_per_km2, ee_arr, color=color,
                   linewidth=1.8, marker=marker, markersize=5,
                   markerfacecolor="none", markeredgewidth=1.2,
                   label=f"$p_{{act}} = {p}$")
        csv_cols.append(ee_arr)
        csv_hdr.append(f"EE_analytical_p{p}")

    ax.set_xlabel(r"UAV density $\lambda_u$ (UAVs/km²)")
    ax.set_ylabel(r"Energy Efficiency (bit/Hz/Joule)")
    ax.set_title("Energy Efficiency vs. UAV Density "
                 "(Different Activation)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_xlim(0.0, 50.0)
    ax.set_xticks(np.arange(0, 55, 5))
    ax.set_ylim(0.0, 0.012)

    if opts.save_png:
        png = opts.outputs_dir / "fig12_ee_vs_density.png"
        fig.tight_layout()
        fig.savefig(png, dpi=200)
        print(f"  saved: {png}")
    plt.close(fig)
    if opts.save_csv:
        csv = opts.outputs_dir / "fig12_ee_vs_density.csv"
        _save_curve_csv(csv, csv_hdr, csv_cols)
        print(f"  saved: {csv}")
