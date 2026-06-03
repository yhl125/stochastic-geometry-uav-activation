import Uav.Basic
import Uav.PaperRefs

namespace Uav

noncomputable section

theorem eq1_friis_matches_paper_ref
    (Gt Gr wavelength d0 : ℝ) :
    friisRho Gt Gr wavelength d0 =
      paperEq1FriisRhs Gt Gr wavelength d0 := by
  rfl

theorem eq23_ase_activation_matches_paper_ref
    (lambda_u p_act rate : ℝ) :
    ase (activeDensity lambda_u p_act) rate =
      paperEq23AseRhs lambda_u p_act rate := by
  rfl

theorem eq24_hover_power_matches_paper_ref
    (P0 Pi : ℝ) :
    hoverPropulsionPower P0 Pi =
      paperEq24HoverPowerRhs P0 Pi := by
  rfl

theorem eq25_total_power_matches_paper_ref
    (lambda_u p_act Pu Pop Pprop : ℝ) :
    totalPowerArea lambda_u p_act Pu Pop Pprop =
      paperEq25TotalPowerRhs lambda_u p_act Pu Pop Pprop := by
  unfold totalPowerArea paperEq25TotalPowerRhs
  ring

theorem eq26_lambda_u_cancels_to_paper_ref
    (lambda_u p_act rate Pu Pop Pprop : ℝ)
    (h_lambda_u : lambda_u ≠ 0)
    (h_den : p_act * (Pu + Pop) + Pprop ≠ 0) :
    energyEfficiencyLiteral lambda_u p_act rate Pu Pop Pprop =
      paperEq26EnergyEfficiencyRhs p_act rate Pu Pop Pprop := by
  unfold energyEfficiencyLiteral paperEq26EnergyEfficiencyRhs
  have h_scaled_den :
      lambda_u * (p_act * (Pu + Pop) + Pprop) ≠ 0 :=
    mul_ne_zero h_lambda_u h_den
  field_simp [h_den, h_scaled_den]

theorem eq26_simplified_definition_matches_paper_ref
    (p_act rate Pu Pop Pprop : ℝ) :
    energyEfficiencySimplified p_act rate Pu Pop Pprop =
      paperEq26EnergyEfficiencyRhs p_act rate Pu Pop Pprop := by
  rfl

end

end Uav
