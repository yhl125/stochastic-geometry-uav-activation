"""CLI orchestrator for the four reproduction figures.

Example:
    # Smoke (200 iters) - fast, regress catch
    uv run python src/run.py --iters 200 --out outputs/smoke
    # Dev (2k iters)
    uv run python src/run.py --iters 2000 --out outputs/dev
    # Final (10k iters, paper-equivalent)
    uv run python src/run.py --iters 10000 --out outputs/figures
    # Single figure
    uv run python src/run.py --iters 2000 --only fig2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import params as P
from figures import (
    FigureOutputs,
    figure_2,
    figure_3,
    figure_4,
    figure_5,
    figure_6,
    figure_7,
    figure_8,
    figure_9,
    figure_10,
    figure_11,
    figure_12,
)


_FIGURE_FNS = {
    "fig2": figure_2,
    "fig3": figure_3,
    "fig4": figure_4,
    "fig5": figure_5,
    "fig6": figure_6,
    "fig7": figure_7,
    "fig8": figure_8,
    "fig9": figure_9,
    "fig10": figure_10,
    "fig11": figure_11,
    "fig12": figure_12,
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Reproduce Selim 2025 figures.")
    p.add_argument("--iters", type=int, default=P.MC_ITERS_FINAL,
                   help=f"MC iterations per condition (default: {P.MC_ITERS_FINAL})")
    p.add_argument("--seed", type=int, default=0,
                   help="RNG seed (default: 0)")
    p.add_argument("--out", type=Path,
                   default=Path("../outputs/run"),
                   help="output directory (default: ../outputs/run)")
    p.add_argument("--only", nargs="+", choices=list(_FIGURE_FNS.keys()),
                   default=list(_FIGURE_FNS.keys()),
                   help="subset of figures to generate")
    args = p.parse_args(argv)

    opts = FigureOutputs(outputs_dir=args.out.resolve(),
                         iters=args.iters, seed=args.seed)
    print(f"output directory: {opts.outputs_dir}")
    print(f"iterations:       {opts.iters}")
    print(f"seed:             {opts.seed}")
    print(f"figures:          {args.only}")
    print("-" * 60)

    for name in args.only:
        _FIGURE_FNS[name](opts)
        print()

    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
