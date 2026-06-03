# Lean #check Trace Report

This report is generated from `FORMULA_REGISTRY` by elaborating a Lean file
with `#check Uav.<item>` commands through `lake env lean`.

| Paper equation | Status | Lean item | #check |
| --- | --- | --- | --- |
| Eq.1 | `lean_verified` | `eq1_friis_matches_paper_ref` | pass |
| Eq.2 | `lean_verified` | `eq2_elevation_angle_matches_paper_ref_on_positive_horizontal_distance` | pass |
| Eq.2 | `lean_verified` | `eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance` | pass |
| Eq.2 | `lean_verified` | `eq2_nlos_probability_is_one_minus_los` | pass |
| Eq.2 | `lean_verified` | `eq2_nlos_probability_matches_paper_ref_on_positive_horizontal_distance` | pass |
| Eq.6 | `lean_verified` | `eq6_horizontal_pdf_matches_paper_ref_on_support` | pass |
| Eq.6 | `lean_verified` | `eq6_horizontal_pdf_zero_off_support` | pass |
| Eq.7 | `lean_verified` | `eq7_jacobian` | pass |
| Eq.8 | `lean_verified` | `eq8_distance_pdf_matches_paper_ref_on_support` | pass |
| Eq.8 | `lean_verified` | `eq8_distance_pdf_zero_off_support` | pass |
| Eq.15 | `lean_verified` | `eq15_definition_matches_paper_ref` | pass |
| Eq.15 | `lean_verified` | `eq15_rayleigh_laplace_identity` | pass |
| Eq.16 | `lean_verified` | `eq16_mixture_matches_paper_ref` | pass |
| Eq.17 | `unverified` | `laplaceInterference` | pass |
| Eq.18 | `lean_verified` | `eq18_serving_mixture_matches_paper_ref` | pass |
| Eq.18 | `lean_verified` | `eq18_s_parameter_matches_paper_ref` | pass |
| Eq.19 | `unverified` | `coverageProbability` | pass |
| Eq.20 | `lean_verified` | `eq20_log2_matches_paper_ref` | pass |
| Eq.21 | `unverified` | `eq21_rate_tail_integral_identity` | pass |
| Eq.21 | `unverified` | `Eq21HamdiChangeOfVariables` | pass |
| Eq.21 | `unverified` | `eq21_hamdi_identity_from_change_of_variables` | pass |
| Eq.22 | `unverified` | `averageRate` | pass |
| Eq.23 | `lean_verified` | `eq23_ase_activation_matches_paper_ref` | pass |
| Eq.24 | `lean_verified` | `eq24_hover_power_matches_paper_ref` | pass |
| Eq.25 | `lean_verified` | `eq25_total_power_matches_paper_ref` | pass |
| Eq.26 | `lean_verified` | `eq26_lambda_u_cancels_to_paper_ref` | pass |
| Eq.26 | `lean_verified` | `eq26_simplified_definition_matches_paper_ref` | pass |
| Eq.27 | `unverified` | `laplaceInterferenceBounded` | pass |
| Eq.27 | `unverified` | `coverageProbabilityBounded` | pass |
| Eq.27 | `unverified` | `averageRateBounded` | pass |
