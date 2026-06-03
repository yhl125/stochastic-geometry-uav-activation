# UAV Activation Lean Formula Checks

This directory contains Lean 4 formula checks for the UAV activation paper
reproduction. Phase 1 proves algebra/log/unit transformations and records
larger probability and stochastic-geometry results as explicit assumptions.
The generated `outputs/reports/lean_trace_check.md` report verifies that the
Lean names recorded in the Python formula registry elaborate through `#check`
after importing `Uav`.

## Assumption Boundary

Phase 1 does not prove HPPP thinning, Slivnyak's theorem, the PGFL,
the full Hamdi change of variables, or numerical quadrature correctness.
It names those facts explicitly where needed and proves downstream formula
composition. Phase 2 adds the Eq. 21 layer-cake theorem for the
expectation-to-rate-tail step; the final SINR-domain substitution remains
the explicit `Eq21HamdiChangeOfVariables` boundary.

## Coverage and Rate Spec Boundary

`Uav.CoverageSpec` uses `opaque` declarations for the Eq. 17, Eq. 19,
Eq. 22, and Eq. 27 integral-level functions. Eq. 27 is represented as the
bounded Laplace interface plus the bounded coverage and bounded rate
interfaces that consume it. Phase 1 does not prove PGFL, Slivnyak, the full
Hamdi substitution, or quadrature correctness. It only fixes the typed
interface and proves local algebra such as the Eq. 18 `s` parameter.

## Paper Anchors

Each Lean item maps to a paper equation (encoded in the item name) and the
Python callsite that consumes the audited kernel.

| Lean item | Python callsite |
|---|---|
| `eq1_friis_matches_paper_ref` | `src/formulas.py` `friis_reference_gain`; runtime delegate `src/params.py` `RHO` |
| `eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance` | `src/formulas.py` `los_probability`; runtime delegates `src/channel.py` `los_probability_scalar` and `los_probability_array`; Lean excludes `x = 0` because the paper's `atan(H/x)` is undefined there |
| `eq6_horizontal_pdf_matches_paper_ref_on_support` | No direct Python callsite; intermediate horizontal-distance identity used to derive Eq. 8 |
| `eq6_horizontal_pdf_zero_off_support` | Total Lean PDF definition is zero for `x < 0` |
| `eq7_jacobian` | `src/formulas.py` `horizontal_distance_from_3d` and `horizontal_distance_jacobian`; runtime use inside `src/analytical.py` coverage integrands |
| `eq8_distance_pdf_matches_paper_ref_on_support` | `src/formulas.py` `distance_3d_pdf`; runtime use inside `src/analytical.py` outer coverage integrals |
| `eq8_distance_pdf_zero_off_support` | Total Lean PDF definition is zero for `r < H` |
| `eq15_rayleigh_laplace_identity` | `src/formulas.py` `rayleigh_laplace_kernel`; runtime use through `interferer_state_average` in `src/analytical.py` |
| `eq16_mixture_matches_paper_ref` | `src/formulas.py` `interferer_state_average`; runtime use inside unbounded and bounded Laplace integrands |
| `eq18_serving_mixture_matches_paper_ref` | `src/formulas.py` `serving_mixture`; runtime use inside unbounded and bounded conditional coverage kernels |
| `eq18_s_parameter_matches_paper_ref` | `src/formulas.py` `s_parameter`; runtime use inside unbounded and bounded conditional coverage kernels |
| `eq20_log2_matches_paper_ref` | `src/formulas.py` `rate_log2`; analytical Eq. 22 paths keep `1 / math.log(2.0)` scale; MC uses `src/mc.py` `rate_mc` |
| `eq21_rate_tail_integral_identity` | `src/formulas.py` `average_rate_tail_integrand`; Eq. 22 paths in `src/analytical.py` consume the CCDF integrand |
| `eq21_hamdi_identity_from_change_of_variables` | `src/formulas.py` `average_rate_tail_integrand`; `src/analytical.py` keeps the `1 / math.log(2.0)` scale |
| `eq23_ase_activation_matches_paper_ref` | `src/formulas.py` `area_spectral_efficiency`; Eq. 26 note in `src/analytical.py` documents `lambda_u * p_act` |
| `eq24_hover_power_matches_paper_ref` | `src/formulas.py` `hover_propulsion_power`; runtime delegate `src/params.py` `P_PROP_W` |
| `eq25_total_power_matches_paper_ref` | `src/formulas.py` `total_power_density`; Eq. 26 runtime uses the cancelled form |
| `eq26_lambda_u_cancels_to_paper_ref` | `src/formulas.py` `energy_efficiency_simplified`; runtime use in `src/analytical.py` `energy_efficiency` |
| `laplaceInterference` spec | `src/analytical.py` `laplace_interference` |
| `coverageProbability` spec | `src/analytical.py` `coverage_probability` |
| `averageRate` spec | `src/analytical.py` `average_rate` |
| `laplaceInterferenceBounded` spec | `src/analytical.py` `laplace_interference_bounded` |
| `coverageProbabilityBounded` spec | `src/analytical.py` `coverage_probability_bounded` |
| `averageRateBounded` spec | `src/analytical.py` `average_rate_bounded` |

## Equation Status

| Equation | Lean status |
|---|---|
| Eq. 1 | Complete formula-reference theorem |
| Eq. 2 | Complete formula-reference theorem on `0 < x`; `x = 0` is intentionally excluded because the paper's `atan(H/x)` is undefined in ordinary math |
| Eq. 6 | Piecewise total PDF definition: equals the paper RHS on support `0 ≤ x`, zero off support `x < 0`; HPPP derivation out of scope |
| Eq. 7 | Complete Jacobian derivative theorem under `0 < H` and `H < r` |
| Eq. 8 | Piecewise total PDF definition: equals the paper RHS on support `H ≤ r`, zero off support `r < H`; normalization derivation out of scope |
| Eq. 15 | Phase 2 half-line exponential integral theorem |
| Eq. 16 | Complete mixture algebra theorem |
| Eq. 17 | Phase 1 `opaque` interface (status `unverified`) |
| Eq. 18 | Complete mixture and `s` parameter theorem |
| Eq. 19 | Phase 1 `opaque` interface (status `unverified`) |
| Eq. 20 | Complete log-base theorem |
| Eq. 21-22 | Eq. 21 layer-cake theorem proved for the rate-tail identity; full Hamdi SINR-domain change of variables and Eq. 22 nested coverage integral remain explicit spec boundaries |
| Eq. 23-26 | Complete algebra theorem set |
| Eq. 27 | Phase 1 `opaque` bounded Laplace/coverage/rate interfaces (status `unverified`) |
