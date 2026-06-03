import Mathlib

namespace Uav

noncomputable section

def paperEq1FriisRhs (Gt Gr wavelength d0 : ℝ) : ℝ :=
  Gt * Gr * (wavelength / (4 * Real.pi * d0)) ^ 2

def paperEq2ElevationAngleDegreesRhs (H x : ℝ) : ℝ :=
  Real.arctan (H / x) * 180 / Real.pi

def paperEq2LosProbabilityRhs (C1 C2 H x : ℝ) : ℝ :=
  1 / (1 + C1 *
    Real.exp (-C2 * (paperEq2ElevationAngleDegreesRhs H x - C1)))

def paperEq2NlosProbabilityRhs (C1 C2 H x : ℝ) : ℝ :=
  1 - paperEq2LosProbabilityRhs C1 C2 H x

def paperEq6HorizontalNearestPdfRhs (lambda_a x : ℝ) : ℝ :=
  2 * Real.pi * lambda_a * x * Real.exp (-Real.pi * lambda_a * x ^ 2)

def paperEq8Distance3dPdfRhs (lambda_a H r : ℝ) : ℝ :=
  2 * Real.pi * lambda_a * r *
    Real.exp (-Real.pi * lambda_a * (r ^ 2 - H ^ 2))

def paperEq15RayleighLaplaceRhs (a : ℝ) : ℝ :=
  1 / (1 + a)

def paperEq16InterfererAverageRhs
    (pLos aLos aNlos : ℝ) : ℝ :=
  pLos / (1 + aLos) + (1 - pLos) / (1 + aNlos)

def paperEq18ServingMixtureRhs
    (pLos losTerm nlosTerm : ℝ) : ℝ :=
  pLos * losTerm + (1 - pLos) * nlosTerm

def paperEq18SParameterRhs
    (beta r alpha rho Pu : ℝ) : ℝ :=
  beta * r ^ alpha / (rho * Pu)

def paperEq20RateRhs (sinr : ℝ) : ℝ :=
  Real.log (1 + sinr) / Real.log 2

def paperEq21HamdiRhs (ccdf : ℝ → ℝ) : ℝ :=
  (1 / Real.log 2) * ∫ t in Set.Ioi (0 : ℝ), ccdf t / (1 + t)

def paperEq23AseRhs (lambda_u p_act rate : ℝ) : ℝ :=
  (lambda_u * p_act) * rate

def paperEq24HoverPowerRhs (P0 Pi : ℝ) : ℝ :=
  P0 + Pi

def paperEq25TotalPowerRhs
    (lambda_u p_act Pu Pop Pprop : ℝ) : ℝ :=
  lambda_u * p_act * (Pu + Pop) + lambda_u * Pprop

def paperEq26EnergyEfficiencyRhs
    (p_act rate Pu Pop Pprop : ℝ) : ℝ :=
  p_act * rate / (p_act * (Pu + Pop) + Pprop)

end

end Uav
