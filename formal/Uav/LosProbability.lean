import Uav.PaperRefs

namespace Uav

noncomputable section

def elevationAngleDegrees (H x : ℝ) : ℝ :=
  Real.arctan (H / x) * 180 / Real.pi

def losProbabilityFormula (C1 C2 H x : ℝ) : ℝ :=
  1 / (1 + C1 * Real.exp (-C2 * (elevationAngleDegrees H x - C1)))

def nlosProbabilityFormula (C1 C2 H x : ℝ) : ℝ :=
  1 - losProbabilityFormula C1 C2 H x

theorem eq2_elevation_angle_matches_paper_ref_on_positive_horizontal_distance
    (H x : ℝ) (hx : 0 < x) :
    elevationAngleDegrees H x =
      paperEq2ElevationAngleDegreesRhs H x := by
  have _ : x ≠ 0 := ne_of_gt hx
  rfl

theorem eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance
    (C1 C2 H x : ℝ) (hx : 0 < x) :
    losProbabilityFormula C1 C2 H x =
      paperEq2LosProbabilityRhs C1 C2 H x := by
  unfold losProbabilityFormula paperEq2LosProbabilityRhs
  rw [eq2_elevation_angle_matches_paper_ref_on_positive_horizontal_distance H x hx]

theorem eq2_nlos_probability_is_one_minus_los
    (C1 C2 H x : ℝ) :
    nlosProbabilityFormula C1 C2 H x =
      1 - losProbabilityFormula C1 C2 H x := by
  rfl

theorem eq2_nlos_probability_matches_paper_ref_on_positive_horizontal_distance
    (C1 C2 H x : ℝ) (hx : 0 < x) :
    nlosProbabilityFormula C1 C2 H x =
      paperEq2NlosProbabilityRhs C1 C2 H x := by
  unfold nlosProbabilityFormula paperEq2NlosProbabilityRhs
  rw [eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance C1 C2 H x hx]

end

end Uav
