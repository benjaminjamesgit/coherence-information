"""Merge the per-seed decoupling-control runs into the locked nine-cell verdict.

Each results/decoupling_control/seed_<s>.json was produced by run_decoupling_control.py for a
single seed, so it carries that seed's per-crossing Delta (deltas[c] == [Delta_s]) and twin
Spearman (twin_sanity[c]). This collects all seeds' Deltas and reruns the CANONICAL metric
(crossing_assignment -> concordance_verdict) so the aggregate is identical to a single
all-seeds compute_decoupling_run, just sharded across processes.
"""
import glob
import json
import math

import numpy as np

from cit.metacoherence import crossing_assignment, concordance_verdict, CROSSING_REFS

files = sorted(glob.glob("results/decoupling_control/seed_*.json"))
per = [json.load(open(f)) for f in files]
seeds = sorted(p["seeds"][0] for p in per)

deltas = {c: [p["deltas"][c][0] for p in per] for c in CROSSING_REFS}


def _median_finite(vals):
    v = [x for x in vals if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return float(np.median(v)) if v else float("nan")


twin = {c: _median_finite([p["twin_sanity"][c] for p in per]) for c in CROSSING_REFS}
assign = {c: crossing_assignment(deltas[c]) for c in CROSSING_REFS}

out = concordance_verdict(assign["K3b"], assign["K2b"])
out["n_seeds"] = len(seeds)
out["seeds"] = seeds
out["deltas"] = deltas
out["twin_sanity"] = twin
print(json.dumps(out, indent=2, default=str))
