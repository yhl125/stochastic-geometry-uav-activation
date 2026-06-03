import Uav.Basic
import Uav.PaperRefs

namespace Uav

noncomputable section

open MeasureTheory

def rateRandomFromSinr {Ω : Type*} (sinr : Ω → ℝ) : Ω → ℝ :=
  fun ω => log2 (1 + sinr ω)

def sinrCcdf {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) (sinr : Ω → ℝ) (t : ℝ) : ℝ :=
  μ.real {ω : Ω | t < sinr ω}

structure Eq21HamdiChangeOfVariables {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) (sinr : Ω → ℝ) : Prop where
  sinr_aemeasurable : AEMeasurable sinr μ
  sinr_nonneg : 0 ≤ᵐ[μ] sinr
  rate_integrable : Integrable (rateRandomFromSinr sinr) μ
  rate_nonneg : 0 ≤ᵐ[μ] rateRandomFromSinr sinr
  identity :
    (∫ t in Set.Ioi (0 : ℝ),
        μ.real {ω : Ω | t < rateRandomFromSinr sinr ω}) =
      paperEq21HamdiRhs (sinrCcdf μ sinr)

theorem rateRandomFromSinr_nonneg_ae
    {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) (sinr : Ω → ℝ)
    (h_sinr_nonneg : 0 ≤ᵐ[μ] sinr)
    (hlog2_pos : 0 < Real.log 2) :
    0 ≤ᵐ[μ] rateRandomFromSinr sinr := by
  filter_upwards [h_sinr_nonneg] with ω hω
  simp only [Pi.zero_apply] at hω
  unfold rateRandomFromSinr log2
  exact div_nonneg (Real.log_nonneg (by linarith)) hlog2_pos.le

theorem eq21_rate_tail_integral_identity
    {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) (sinr : Ω → ℝ)
    (h_rate_integrable : Integrable (rateRandomFromSinr sinr) μ)
    (h_rate_nonneg : 0 ≤ᵐ[μ] rateRandomFromSinr sinr) :
    (∫ ω, rateRandomFromSinr sinr ω ∂μ) =
      ∫ t in Set.Ioi (0 : ℝ),
        μ.real {ω : Ω | t < rateRandomFromSinr sinr ω} := by
  exact Integrable.integral_eq_integral_meas_lt h_rate_integrable h_rate_nonneg

theorem eq21_hamdi_identity_from_change_of_variables
    {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) (sinr : Ω → ℝ)
    (h_change : Eq21HamdiChangeOfVariables μ sinr) :
    (∫ ω, rateRandomFromSinr sinr ω ∂μ) =
      paperEq21HamdiRhs (sinrCcdf μ sinr) := by
  rw [eq21_rate_tail_integral_identity μ sinr
    h_change.rate_integrable h_change.rate_nonneg]
  exact h_change.identity

theorem eq20_log2_matches_paper_ref (sinr : ℝ) :
    rateLog2FromSinr sinr = paperEq20RateRhs sinr := by
  unfold rateLog2FromSinr log2 paperEq20RateRhs
  rfl

theorem fig_rate_plot_ln_scale_from_log2
    (rate : ℝ) :
    naturalPlotFromLog2Rate rate = rate * Real.log 2 := by
  rfl

theorem ln_rate_equals_scaled_log2_rate
    (sinr : ℝ)
    (hlog2 : Real.log 2 ≠ 0) :
    naturalPlotFromLog2Rate (rateLog2FromSinr sinr) = rateLnFromSinr sinr := by
  unfold naturalPlotFromLog2Rate rateLog2FromSinr rateLnFromSinr log2
  field_simp [hlog2]

end

end Uav
