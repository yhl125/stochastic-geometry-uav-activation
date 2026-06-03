"""Monte Carlo simulator: HPPP candidates → Bernoulli thinning → SINR at typical user (origin).

Implements the system model from Selim 2025 §System Model:
  - Candidate UAVs as HPPP with intensity λ_u in a 2-D disk of radius R_sim.
  - Each candidate independently activated with probability p_act.
  - Constant altitude H, nearest-active-UAV serving association (3-D distance).
  - Al-Hourani LoS sigmoid per link, i.i.d. across links.
  - Rayleigh fading g ~ Exp(1) per link, i.i.d.
  - Path gain ρ · R^(-α_j), with α_j ∈ {α_LoS, α_NLoS}.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from channel import los_probability_array
from params import (
    ALPHA_LOS,
    ALPHA_NLOS,
    H_ALT_M,
    N0_W,
    P_U_W,
    RHO,
    SIM_DISK_RADIUS_M,
)


@dataclass
class MCResult:
    sinr_linear: np.ndarray         # length n_iters; 0 where no active UAV
    no_active_count: int
    n_iters: int


def _sample_active_positions(lam_u: float,
                             p_act: float,
                             disk_r: float,
                             rng: np.random.Generator) -> np.ndarray:
    """Sample one realization of the active-UAV PPP in a disk of radius disk_r.

    Composition: candidate intensity λ_u, Bernoulli thinning at probability
    p_act, so effective active intensity is λ_u · p_act. We sample candidates
    first and then thin (equivalent in distribution).
    """
    area_m2 = np.pi * disk_r ** 2
    mean_count = lam_u * area_m2
    n_cand = rng.poisson(mean_count)
    if n_cand == 0:
        return np.empty((0, 2))
    radii = disk_r * np.sqrt(rng.uniform(size=n_cand))
    angles = 2.0 * np.pi * rng.uniform(size=n_cand)
    cands = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])
    active_mask = rng.uniform(size=n_cand) < p_act
    return cands[active_mask]


def simulate_sinr(lam_u: float,
                  p_act: float,
                  n_iters: int,
                  seed: int = 0,
                  disk_r: float = SIM_DISK_RADIUS_M,
                  h_m: float = H_ALT_M,
                  p_u: float = P_U_W,
                  rho: float = RHO,
                  n0: float = N0_W,
                  alpha_los: float = ALPHA_LOS,
                  alpha_nlos: float = ALPHA_NLOS,
                  sigma_shadow_db: float = 0.0) -> MCResult:
    """Generate n_iters SINR samples for a typical user at the origin.

    sigma_shadow_db > 0 enables per-link i.i.d. log-normal shadowing with
    standard deviation sigma_shadow_db (in dB), applied multiplicatively to
    the received power on every link (serving + interferers). Used for Fig 4
    shadowing MC overlay.
    """
    rng = np.random.default_rng(seed)
    sinr = np.zeros(n_iters)
    no_active = 0
    sigma_nat = sigma_shadow_db * np.log(10.0) / 10.0  # convert dB→natural log

    for i in range(n_iters):
        positions = _sample_active_positions(lam_u, p_act, disk_r, rng)
        n_active = positions.shape[0]
        if n_active == 0:
            no_active += 1
            continue

        horizontal = np.linalg.norm(positions, axis=1)
        dist_3d = np.sqrt(horizontal ** 2 + h_m ** 2)
        serving_idx = int(np.argmin(dist_3d))

        p_los = los_probability_array(horizontal, h_m=h_m)
        los_states = rng.uniform(size=n_active) < p_los
        alphas = np.where(los_states, alpha_los, alpha_nlos)

        fading = rng.exponential(scale=1.0, size=n_active)
        received = p_u * fading * rho * dist_3d ** (-alphas)

        if sigma_nat > 0.0:
            log_shadow = rng.normal(loc=0.0, scale=sigma_nat, size=n_active)
            received *= np.exp(log_shadow)

        signal = received[serving_idx]
        interference = received.sum() - signal
        sinr[i] = signal / (interference + n0)

    return MCResult(sinr_linear=sinr,
                    no_active_count=no_active,
                    n_iters=n_iters)


def coverage_mc(result: MCResult, beta_linear: float) -> float:
    """Coverage probability at threshold β (linear)."""
    return float(np.mean(result.sinr_linear > beta_linear))


def rate_mc(result: MCResult, sinr_cap: float | None = None) -> float:
    """Average achievable rate E[log2(1 + SINR)] in bps/Hz.

    ``sinr_cap`` matches numerical rate integrals that evaluate the CCDF only
    over ``t in [0, t_max]``. The default remains the uncapped Eq. 20 MC rate.
    """
    sinr = result.sinr_linear
    if sinr_cap is not None:
        sinr = np.minimum(sinr, sinr_cap)
    return float(np.mean(np.log2(1.0 + sinr)))
