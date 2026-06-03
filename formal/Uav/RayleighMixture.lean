import Uav.PaperRefs

namespace Uav

noncomputable section

theorem eq15_rayleigh_laplace_identity
    (a : ℝ) (h_nonneg : 0 ≤ a) :
    (∫ x : ℝ in Set.Ioi 0, Real.exp (-(1 + a) * x)) =
      paperEq15RayleighLaplaceRhs a := by
  have h_neg : -(1 + a) < 0 := by linarith
  rw [integral_exp_mul_Ioi h_neg, paperEq15RayleighLaplaceRhs,
      mul_zero, Real.exp_zero, neg_div_neg_eq]

def fadingLaplaceRayleigh (a : ℝ) : ℝ :=
  1 / (1 + a)

def losNlosInterfererAverage
    (pLos aLos aNlos : ℝ) : ℝ :=
  pLos / (1 + aLos) + (1 - pLos) / (1 + aNlos)

def servingCoverageMixture
    (pLos losTerm nlosTerm : ℝ) : ℝ :=
  pLos * losTerm + (1 - pLos) * nlosTerm

theorem eq15_definition_matches_paper_ref
    (a : ℝ) :
    fadingLaplaceRayleigh a = paperEq15RayleighLaplaceRhs a := by
  unfold fadingLaplaceRayleigh paperEq15RayleighLaplaceRhs
  rfl

theorem eq16_mixture_matches_paper_ref
    (pLos aLos aNlos : ℝ) :
    losNlosInterfererAverage pLos aLos aNlos =
      paperEq16InterfererAverageRhs pLos aLos aNlos := by
  unfold losNlosInterfererAverage paperEq16InterfererAverageRhs
  ring

theorem eq18_serving_mixture_matches_paper_ref
    (pLos losTerm nlosTerm : ℝ) :
    servingCoverageMixture pLos losTerm nlosTerm =
      paperEq18ServingMixtureRhs pLos losTerm nlosTerm := by
  unfold servingCoverageMixture paperEq18ServingMixtureRhs
  ring

end

end Uav
