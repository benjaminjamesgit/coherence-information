"""CI / local verdict job for the D1 metacoherence grid (v0.7.0 slice 3b).

Computes the (proxies x ablations) grid on a D1 stream and prints the property-recovery
cross-tab + R2 (cross-philosophy median Spearman of the induced w-vectors). This is the
gated deliverable for the full verdict: the full locked-T grid INCLUDING A2 Shapley is a
multi-hour local/CI artifact (K3/K5 A2 ~hours/cell, like the v0.5 K3 Shapley local gate),
so it is NOT run inline -- run it here, in CI (workflow_dispatch) or locally.

The inline A1-column preview already records the honest interim result (the complementary-
recovery seam: R2 < 0.6 on A1). This job's open question is the A2 rescue -- whether
Shapley aligns the proxies as the source expected. D1 is CHARACTERIZED, not pass/failed.

Usage
-----
    # feasible A1 column at locked T (still slow: K5 A1 ~37 min)
    python scripts/run_metacoherence_grid.py --T 50000 --ablations A1
    # the full verdict (A2 incl.; hours -- local / workflow_dispatch only)
    python scripts/run_metacoherence_grid.py --T 50000 --ablations A1,A2,A3
    # a fast smoke run
    python scripts/run_metacoherence_grid.py --T 8000 --proxies K1,K2 --ablations A1,A3
"""

import argparse
import json

from cit.metacoherence import (
    compute_grid, cross_philosophy_r2, build_cross_tab, PROXIES,
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--T", type=int, default=None, help="stream length (default: locked 50000)")
    ap.add_argument("--seed", type=int, default=7000, help="D1 replicate seed")
    ap.add_argument("--proxies", default=",".join(PROXIES), help="comma-separated, e.g. K1,K2,K5")
    ap.add_argument("--ablations", default="A1", help="comma-separated, e.g. A1,A2,A3")
    args = ap.parse_args()

    proxies = tuple(p.strip() for p in args.proxies.split(",") if p.strip())
    ablations = tuple(a.strip() for a in args.ablations.split(",") if a.strip())

    grid = compute_grid(proxies=proxies, ablations=ablations, seed=args.seed, T=args.T)
    tab = build_cross_tab(grid)
    r2 = cross_philosophy_r2(grid)

    out = {
        "seed": args.seed,
        "T": args.T,
        "cells": list(grid),
        "cross_tab": tab,
        "r2_median": r2["median"],
        "r2_n_valid": r2["n_valid"],
        "r2_n_pairs": r2["n_pairs"],
        "pair_spearman": r2["pair_rhos"],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
