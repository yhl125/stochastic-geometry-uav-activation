"""Table 1 parameters in SI units.

Source: Selim 2025, Sci. Rep. 15:37356, Table 1.
"""
from __future__ import annotations

import math

import formulas as formula_kernels

SPEED_OF_LIGHT_M_S: float = 2.99792458e8
F_C_HZ: float = 2.0e9
LAMBDA_WAVE_M: float = SPEED_OF_LIGHT_M_S / F_C_HZ  # ≈ 0.1499 m

G_TX_LINEAR: float = 1.0   # 0 dBi
G_RX_LINEAR: float = 1.0   # 0 dBi

RHO: float = formula_kernels.friis_reference_gain(G_TX_LINEAR, G_RX_LINEAR, LAMBDA_WAVE_M)

H_ALT_M: float = 120.0

P_U_W: float = 1.0       # 30 dBm
P_OP_W: float = 0.1
P_0_W: float = 14.75
P_I_W: float = 41.54
P_PROP_W: float = formula_kernels.hover_propulsion_power(P_0_W, P_I_W)   # 56.29 W per UAV (hover, V=0)

N0_DBM: float = -104.0
N0_W: float = 10.0 ** ((N0_DBM - 30.0) / 10.0)  # ≈ 3.981e-14 W

ALPHA_LOS: float = 2.1
ALPHA_NLOS: float = 3.5

C1: float = 10.0
C2: float = 0.1

LAMBDA_U_DEFAULT_PER_M2: float = 1.0e-5   # 10 UAVs / km²
BETA_DEFAULT_LINEAR: float = 1.0          # 0 dB

SIM_DISK_RADIUS_M: float = 1.0e4          # 10 km — Table 1 "Simulation Area Radius"
# Note: at 10 km, MC interferer truncation makes MC overshoot the true
# unbounded-plane analytical (Eq. 22) by ~15% for high-density / high-p_act
# conditions. Paper claims "perfect match" between MC and analytical without
# documenting how that was achieved; we follow Table 1 literally and report
# the deviation in our writeup. See diagnose_rate.py for the disk-size sweep
# that proves MC@100km converges to my unbounded analytical (within MC SE).
MC_ITERS_FINAL: int = 10_000
MC_ITERS_DEV: int = 2_000
MC_ITERS_SMOKE: int = 200


def db_to_linear(x_db: float) -> float:
    return 10.0 ** (x_db / 10.0)


def linear_to_db(x_lin: float) -> float:
    return 10.0 * math.log10(x_lin)
