import Uav.Basic
import Uav.PaperRefs

namespace Uav

noncomputable section

opaque losProbability : ℝ → ℝ → ℝ
opaque laplaceInterference : ℝ → ℝ → ℝ → ℝ
opaque laplaceInterferenceBounded : ℝ → ℝ → ℝ → ℝ → ℝ
opaque coverageProbability : ℝ → ℝ → ℝ
opaque coverageProbabilityBounded : ℝ → ℝ → ℝ → ℝ
opaque averageRate : ℝ → ℝ
opaque averageRateBounded : ℝ → ℝ → ℝ

def sParameter (beta r alpha rho Pu : ℝ) : ℝ :=
  beta * r ^ alpha / (rho * Pu)

theorem eq18_s_parameter_matches_paper_ref
    (beta r alpha rho Pu : ℝ) :
    sParameter beta r alpha rho Pu =
      paperEq18SParameterRhs beta r alpha rho Pu := by
  unfold sParameter paperEq18SParameterRhs
  rfl

end

end Uav
