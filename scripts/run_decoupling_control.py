"""CI / local verdict job for the v0.7.0 decoupling control (pre-reg 2026-06-23).

Runs the A1 decoupling control -- crosses the two MODELING functionals onto the byte stream
(K3b, K2b; cit.proxies.crossing) and asks, via the twin-excluded nine-cell concordance
(cit.metacoherence.decoupling_control_verdict), whether D1's A1 {K1,K5}|{K2,K3,K4} split tracks
coding PHILOSOPHY or stream REPRESENTATION. HEAVY at locked T (K3b ~ tens of minutes/seed ->
~20h over the 20-seed ensemble), so it is NOT run inline -- run here, locally or in CI
(workflow_dispatch), ideally sharding seeds across processes and merging the per-seed w-vectors.

Per the locked pre-reg the verdict is one of PHILOSOPHY (the split tracks philosophy -> D1 R2 is
adjudicable), REPRESENTATION_ARTIFACT (the split tracks encoding), PROXY_SPECIFIC_SPLIT (the two
crossings disagree -- weight per the K2b-carries-more-model-change caveat), or INCONCLUSIVE; the
outcome is recorded honestly in either direction. The locked decision is the 18/20 sign-count x
two-band magnitude; the 20-seed Delta 90% interval is a reported corroborator, not the decision.

Usage
-----
    # the locked control: full T, the 20-seed replicate ensemble (overnight)
    python scripts/run_decoupling_control.py --T 50000
    # a single-seed shard (run 20 in parallel, then merge per_seed_w for the verdict)
    python scripts/run_decoupling_control.py --T 50000 --seeds 7000
    # a fast smoke run
    python scripts/run_decoupling_control.py --T 400 --seeds 7000,7001
"""

import argparse
import json

from cit.data.hsmm_d1 import REPLICATE_SEEDS
from cit.metacoherence import compute_decoupling_run

_ASSIGN_KEYS = ("label", "confidence", "n_M", "n_B", "n_seeds",
                "median_delta", "ci90", "ci90_excludes_zero")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--T", type=int, default=None, help="stream length (default: locked 50000)")
    ap.add_argument("--seeds", default=",".join(str(s) for s in REPLICATE_SEEDS),
                    help="comma-separated D1 replicate seeds (default: the locked 7000..7019)")
    args = ap.parse_args()

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    run = compute_decoupling_run(seeds=seeds, T=args.T)
    v = run["verdict"]

    out = {
        "T": args.T,
        "seeds": run["seeds"],
        "verdict": v["verdict"],
        "confidence": v["confidence"],
        "lean": v["lean"],
        "assignments": {c: {k: a[k] for k in _ASSIGN_KEYS} for c, a in v["assignments"].items()},
        "twin_sanity": v["twin_sanity"],
        "deltas": v["deltas"],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
