import Mathlib

namespace Uav

noncomputable section

def log2 (x : ℝ) : ℝ :=
  Real.log x / Real.log 2

def activeDensity (lambda_u p_act : ℝ) : ℝ :=
  lambda_u * p_act

def friisRho (Gt Gr wavelength d0 : ℝ) : ℝ :=
  Gt * Gr * (wavelength / (4 * Real.pi * d0)) ^ 2

def hoverPropulsionPower (P0 Pi : ℝ) : ℝ :=
  P0 + Pi

def ase (lambda_a rate : ℝ) : ℝ :=
  lambda_a * rate

def totalPowerArea (lambda_u p_act Pu Pop Pprop : ℝ) : ℝ :=
  lambda_u * (p_act * (Pu + Pop) + Pprop)

def energyEfficiencyLiteral
    (lambda_u p_act rate Pu Pop Pprop : ℝ) : ℝ :=
  (lambda_u * p_act * rate) /
    (lambda_u * (p_act * (Pu + Pop) + Pprop))

def energyEfficiencySimplified
    (p_act rate Pu Pop Pprop : ℝ) : ℝ :=
  (p_act * rate) / (p_act * (Pu + Pop) + Pprop)

def rateLog2FromSinr (sinr : ℝ) : ℝ :=
  log2 (1 + sinr)

def rateLnFromSinr (sinr : ℝ) : ℝ :=
  Real.log (1 + sinr)

def naturalPlotFromLog2Rate (rate : ℝ) : ℝ :=
  rate * Real.log 2

end

end Uav
