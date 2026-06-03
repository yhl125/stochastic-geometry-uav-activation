# Stochastic-Geometry Analysis of UAV-Assisted Networks with Probabilistic UAV Activation — Reproduction

A term-project reproduction of

> M. M. Selim, "Stochastic geometry analysis of UAV-assisted networks with
> probabilistic UAV activation," *Scientific Reports* **15**:37356 (2025).
> DOI: [10.1038/s41598-025-21343-5](https://doi.org/10.1038/s41598-025-21343-5).

It reproduces the paper's representative performance curves (coverage
probability, average achievable rate, area spectral efficiency, energy
efficiency, and a bounded-radius variant) in Python, and adds a **Lean-assisted
formula audit layer**: a machine-readable registry that links each paper
equation to its Python kernel, to a Lean 4 theorem or specification, to a
verification status, and to its support/denominator assumptions.

This is a small **Layer-1 (Verification)** case study, *not* an end-to-end
verified simulator and *not* a new analytical result. The honest scope and
non-goals are described below and encoded in the verification-status taxonomy.

## Layout

```
src/            Python reproduction
  formulas.py     Lean-traceable formula kernels + FORMULA_REGISTRY (the bridge)
  params.py       Table-1 parameters in SI units
  channel.py      LoS/NLoS helpers (delegate to the kernels)
  analytical.py   SciPy-quadrature evaluation of the Eq. 17/19/22/26/27 integrals
  mc.py           Monte-Carlo simulator (HPPP -> Bernoulli thinning -> SINR)
  figures.py      figure orchestration
  run.py          CLI entry point (regenerates the figures)
  figure_methodology.py, figure_provenance.py   plotting choices + provenance
  diagnose_rate.py   diagnostic for the finite-disk MC/analytical rate gap
formal/         Lean 4 development (formula-reference theorems + spec boundaries)
tests/          unittest suite (formula, registry, provenance, Lean guards)
scripts/        lean_check.sh (build + sorry/axiom guard + #check trace), helpers
outputs/
  figures/        committed figure outputs (Figs. 2-12) + their CSVs
  reports/        generated Lean #check report and build log
```

## Reproduce

Python is managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run python -m unittest discover -s tests                    # test suite
uv run python src/run.py --iters 10000 --out outputs/figures   # regenerate figures
```

The Lean checks (build, `sorry`/`admit`/`axiom` guard, and the `#check` trace
that elaborates every registry Lean name) are run by:

```bash
bash scripts/lean_check.sh
```

The Lean toolchain is pinned to `leanprover/lean4:v4.29.1` with Mathlib
`v4.29.1` (`formal/lean-toolchain`); the first build fetches and compiles
Mathlib.

## Verification status taxonomy

Each registry entry (`src/formulas.py`) carries one of two statuses:

| Status | Meaning |
|---|---|
| `lean_verified` | Lean proves a local formula, algebraic identity, support/denominator condition, or log-base equivalence for the equation. |
| `unverified` | The full equation is not formally verified in Lean within scope — either the hard PGFL/Slivnyak integral is declared only as a typed `opaque` interface, or the equation is only partially formalized (a sub-identity is proved but a key intermediate step is assumed, as in Eq. 21's Hamdi change of variables). The value is computed numerically in Python. |

The Monte-Carlo, quadrature, and plotting layer is validated by the Python test
suite and documented in the report's methodology appendix — it is a numerical
layer, not an equation status.

## Documentation

The verification-status taxonomy, the equation→code→proof registry, and the
figure provenance live in the code: `src/formulas.py` (the `FORMULA_REGISTRY`),
`src/figure_provenance.py`, and `src/figure_methodology.py`. The generated Lean
`#check` report for the registered Lean items is at
[`outputs/reports/lean_trace_check.md`](outputs/reports/lean_trace_check.md).

