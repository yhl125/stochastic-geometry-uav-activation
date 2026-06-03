import Uav.PaperRefs

namespace Uav

noncomputable section

def horizontalNearestPdf (lambda_a x : ℝ) : ℝ :=
  if 0 ≤ x then paperEq6HorizontalNearestPdfRhs lambda_a x else 0

def distance3dFromHorizontal (H x : ℝ) : ℝ :=
  Real.sqrt (x ^ 2 + H ^ 2)

def horizontalFromDistance3d (H r : ℝ) : ℝ :=
  Real.sqrt (r ^ 2 - H ^ 2)

def distance3dPdf (lambda_a H r : ℝ) : ℝ :=
  if H ≤ r then paperEq8Distance3dPdfRhs lambda_a H r else 0

theorem eq6_horizontal_pdf_matches_paper_ref_on_support
    (lambda_a x : ℝ) (hx : 0 ≤ x) :
    horizontalNearestPdf lambda_a x =
      paperEq6HorizontalNearestPdfRhs lambda_a x := by
  simp [horizontalNearestPdf, hx]

theorem eq6_horizontal_pdf_zero_off_support
    (lambda_a x : ℝ) (hx : x < 0) :
    horizontalNearestPdf lambda_a x = 0 := by
  simp [horizontalNearestPdf, not_le_of_gt hx]

theorem eq7_jacobian
    {H r : ℝ} (hH : 0 < H) (hr : H < r) :
    deriv (fun y : ℝ => horizontalFromDistance3d H y) r =
      r / Real.sqrt (r ^ 2 - H ^ 2) := by
  have hr_pos : 0 < r := lt_trans hH hr
  have hsq_lt : H ^ 2 < r ^ 2 := by
    rw [sq_lt_sq, abs_of_pos hH, abs_of_pos hr_pos]
    exact hr
  have harg_pos : 0 < r ^ 2 - H ^ 2 := sub_pos.mpr hsq_lt
  have harg_ne : r ^ 2 - H ^ 2 ≠ 0 := ne_of_gt harg_pos
  have hinner :
      HasDerivAt (fun y : ℝ => y ^ 2 - H ^ 2) (2 * r) r := by
    simpa using ((hasDerivAt_id' r).pow 2).sub_const (H ^ 2)
  have hderiv :
      HasDerivAt (fun y : ℝ => horizontalFromDistance3d H y)
        ((2 * r) / (2 * Real.sqrt (r ^ 2 - H ^ 2))) r := by
    simpa [horizontalFromDistance3d] using hinner.sqrt harg_ne
  rw [hderiv.deriv]
  field_simp [Real.sqrt_ne_zero harg_pos.le |>.mpr harg_ne]

theorem eq8_distance_pdf_matches_paper_ref_on_support
    (lambda_a H r : ℝ) (hr : H ≤ r) :
    distance3dPdf lambda_a H r =
      paperEq8Distance3dPdfRhs lambda_a H r := by
  simp [distance3dPdf, hr]

theorem eq8_distance_pdf_zero_off_support
    (lambda_a H r : ℝ) (hr : r < H) :
    distance3dPdf lambda_a H r = 0 := by
  simp [distance3dPdf, not_le_of_gt hr]

end

end Uav
