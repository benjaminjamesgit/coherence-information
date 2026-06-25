#!/usr/bin/env python3
"""D-cal -- v0.7.3 cross-domain step 1 PHASE 2: synthetic transfer-machinery CALIBRATION.

Pre-registered 2026-06-25 (pre_registration.md "v0.7.3 CROSS-DOMAIN step 1 / D-cal PRE-REGISTRATION")
with the dated READOUT-FIX AMENDMENT (across-latent null ENSEMBLE; the build-time smoke test found the
original block-bootstrap-over-TIME models only negligible within-latent sampling noise, not the
across-latent variability that IS the null -- one null latent pair drew P=0.62 by chance). Construction
unchanged except H grown 2->4 triples for power; readout = compare REAL vs NULL transfer DISTRIBUTIONS
over an across-latent ensemble.

FLAT/pairwise transfer measure ONLY; SYNTHETIC only; NO real-domain data, NO flow object. Reuses
cit/data/hsmm_d1.py for the latent regime path + canonical cit/information.py for raw MI. numpy +
math.lgamma only; outputs -> data/ (gitignored). ASCII-only.
"""
import sys, json
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
from cit.data.hsmm_d1 import generate_stream, N_STATES
from cit.information import coherence_weighted_mutual_information, pmf_from_counts

# ---- LOCKED constants (pre_registration.md 2026-06-25 D-cal entry + readout-fix amendment) ----
K = 8
T = 50_000
P_FEATS = list(range(6))                                  # 6 features, 15 pairwise-coupled pairs
H_TRIPLES = [(6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17)]   # 4 pure-3rd-order triples, 12 H-pairs
F = 18
A1, A2 = 12, 10                                           # disjoint encoder alphabet sizes (both >= K)
MASS = 0.7
EMIT_SEED_1, EMIT_SEED_2 = 10001, 20002
LATENT_SEEDS = list(range(7000, 7012))                    # 12 latents -> 12 real pairs + 132 null cross-pairs

P_PAIRS = list(combinations(P_FEATS, 2))                  # 15
H_PAIRS = [p for t in H_TRIPLES for p in combinations(t, 2)]   # 12
ALL_PAIRS = list(combinations(range(F), 2))               # 153


def latent_features(seed):
    """Shared latent feature array L (T,F); all features MARGINALLY UNIFORM by construction."""
    states, _ = generate_stream(seed, T)
    rng = np.random.default_rng(seed * 100003 + 7)
    L = np.zeros((T, F), dtype=np.int64)
    b = rng.integers(0, K, T)
    q = rng.uniform(0.2, 0.95, size=len(P_FEATS))
    for idx, i in enumerate(P_FEATS):
        L[:, i] = np.where(rng.random(T) < q[idx], b, rng.integers(0, K, T))
    for (a, bb, c) in H_TRIPLES:
        fa = rng.integers(0, K, T); fb = rng.integers(0, K, T)
        M = rng.integers(0, K, N_STATES)
        L[:, a] = fa; L[:, bb] = fb; L[:, c] = (fa + fb + M[states]) % K
    return states, L, q


def make_encoder(A, table_seed):
    rng = np.random.default_rng(table_seed)
    return np.stack([rng.permutation(A)[:K] for _ in range(F)]), A


def encode(L, enc, noise_seed):
    pi, A = enc
    rng = np.random.default_rng(noise_seed)
    O = np.zeros_like(L)
    for f in range(F):
        prim = pi[f][L[:, f]]
        keep = rng.random(T) < MASS
        other = rng.integers(0, A - 1, T)
        other = other + (other >= prim)
        O[:, f] = np.where(keep, prim, other)
    return O, A


def raw_mi(x, y, Ax, Ay):
    counts = np.bincount(x.astype(np.int64) * Ay + y.astype(np.int64),
                         minlength=Ax * Ay).reshape(Ax, Ay).astype(np.float64)
    return coherence_weighted_mutual_information(pmf_from_counts(counts), np.ones(Ax))


def coupling_vector(O, A, pairs):
    return np.array([raw_mi(O[:, i], O[:, j], A, A) for (i, j) in pairs])


def rank(x):
    return np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)


def spearman(x, y):
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def transfer(O1, A1_, O2, A2_, pairs):
    return spearman(coupling_vector(O1, A1_, pairs), coupling_vector(O2, A2_, pairs))


def feat_marginal_tv(Oa, Ob, A):
    tvs = []
    for f in range(F):
        pa = np.bincount(Oa[:, f], minlength=A) / Oa.shape[0]
        pb = np.bincount(Ob[:, f], minlength=A) / Ob.shape[0]
        tvs.append(0.5 * np.abs(pa - pb).sum())
    return float(max(tvs))


def cond_entropy_rate(O, A):
    H = []
    for f in range(F):
        x = O[:, f]
        j = np.bincount(x[:-1] * A + x[1:], minlength=A * A).reshape(A, A).astype(float)
        tot = j.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            p = np.where(j > 0, j / np.maximum(j.sum(1, keepdims=True), 1e-12), 0.0)
            hc = -(j / tot * np.where(p > 0, np.log2(np.maximum(p, 1e-12)), 0.0)).sum()
        H.append(hc)
    return np.array(H)


def construction_sanity(seed):
    states, L, q = latent_features(seed)
    p_mi = coupling_vector(L, K, P_PAIRS)
    h_mi = coupling_vector(L, K, H_PAIRS)
    rec = []
    for (a, bb, c) in H_TRIPLES:
        joint = (L[:, a] * K + L[:, bb]) * K + L[:, c]
        rec.append(round(raw_mi(joint, states, K ** 3, N_STATES), 4))
    return {"q": [round(x, 3) for x in q], "P_pairs_MI_min": float(p_mi.min()),
            "P_pairs_MI_max": float(p_mi.max()), "H_pairs_MI_max": float(h_mi.max()),
            "triple_regime_MI": rec}


def run():
    enc1 = make_encoder(A1, EMIT_SEED_1)
    enc2 = make_encoder(A2, EMIT_SEED_2)
    print("=== D-cal: synthetic transfer-machinery calibration (across-latent ensemble) ===", flush=True)
    print(f"K={K} F={F} T={T} A1={A1} A2={A2} MASS={MASS}; P-pairs={len(P_PAIRS)} H-pairs={len(H_PAIRS)} "
          f"latents={len(LATENT_SEEDS)}", flush=True)

    san = construction_sanity(LATENT_SEEDS[0])
    print(f"\n[construction] q={san['q']}", flush=True)
    print(f"[construction] latent P-pairs MI min={san['P_pairs_MI_min']:.4f} max={san['P_pairs_MI_max']:.4f} (graded, >0.02)", flush=True)
    print(f"[construction] latent H-pairs MI max={san['H_pairs_MI_max']:.5f} (must be ~0, <0.01)", flush=True)
    print(f"[construction] I(triple;regime)={san['triple_regime_MI']} bits (must be >0.5)", flush=True)

    # cache encoder outputs per latent (enc1 noise depends only on the latent feeding enc1; same for enc2)
    E1, E2 = {}, {}
    for s in LATENT_SEEDS:
        _, L, _ = latent_features(s)
        E1[s] = encode(L, enc1, EMIT_SEED_1 * 7 + s)
        E2[s] = encode(L, enc2, EMIT_SEED_2 * 7 + s)
    print(f"\n[ensemble] encoded {len(LATENT_SEEDS)} latents", flush=True)

    real_P = [transfer(*E1[s], *E2[s], P_PAIRS) for s in LATENT_SEEDS]
    real_H = [transfer(*E1[s], *E2[s], H_PAIRS) for s in LATENT_SEEDS]
    null_P = [transfer(*E1[si], *E2[sj], P_PAIRS) for si in LATENT_SEEDS for sj in LATENT_SEEDS if si != sj]
    null_H = [transfer(*E1[si], *E2[sj], H_PAIRS) for si in LATENT_SEEDS for sj in LATENT_SEEDS if si != sj]
    rP, rH, nP, nH = map(np.array, (real_P, real_H, null_P, null_H))

    print(f"\n[REAL  P] mean={rP.mean():+.3f} min={rP.min():+.3f} p2.5={np.percentile(rP,2.5):+.3f}", flush=True)
    print(f"[NULL  P] mean={nP.mean():+.3f} std={nP.std():.3f} p95={np.percentile(nP,95):+.3f} (n={len(nP)})", flush=True)
    print(f"[REAL  H] mean={rH.mean():+.3f} std={rH.std():.3f} | [NULL H] mean={nH.mean():+.3f} std={nH.std():.3f} "
          f"p5={np.percentile(nH,5):+.3f} p95={np.percentile(nH,95):+.3f}", flush=True)

    # generic-statistic equality (enc2 real seed vs enc2 null/independent-latent seed)
    s0 = LATENT_SEEDS[0]
    tv = feat_marginal_tv(E2[s0][0], E2[LATENT_SEEDS[1]][0], A2)
    her, hen = cond_entropy_rate(E2[s0][0], A2), cond_entropy_rate(E2[LATENT_SEEDS[1]][0], A2)
    erd = float(np.max(np.abs(her - hen) / np.maximum(her, 1e-9)))
    print(f"\n[generic-stat equality, enc2] max marginal TV={tv:.4f} (<0.02?)  entropy-rate rel-diff={erd:.4f} (<0.02?)", flush=True)

    # ---- FORK (pre-committed thresholds) ----
    P_pass = (np.percentile(rP, 2.5) > 0.5) and (rP.min() > np.percentile(nP, 95)) and (rP.mean() > nP.mean() + 0.5)
    H_indist = (abs(rH.mean() - nH.mean()) < 0.15) and (np.percentile(nH, 5) <= rH.mean() <= np.percentile(nH, 95))
    H_pass = H_indist and ((rP.mean() - rH.mean()) > 0.5)
    null_pass = (abs(nP.mean()) < 0.2) and (abs(nH.mean()) < 0.2) and (tv < 0.02) and (erd < 0.02)
    san_pass = (san["H_pairs_MI_max"] < 0.01) and (san["P_pairs_MI_min"] > 0.02) \
        and all(r > 0.5 for r in san["triple_regime_MI"])
    verdict = ("MACHINERY VALIDATED + flow-object target set (transmit H: real_H >> null_H)"
               if (P_pass and H_pass and null_pass and san_pass)
               else ("MACHINERY BROKEN (P positive control fails)" if not P_pass else "FORK: inspect readouts"))
    print(f"\n=== FORK ===", flush=True)
    print(f"  (a) P positive control PASS = {P_pass}  [real_P p2.5={np.percentile(rP,2.5):+.3f}>0.5, "
          f"min={rP.min():+.3f}>null p95={np.percentile(nP,95):+.3f}, sep={rP.mean()-nP.mean():+.3f}]", flush=True)
    print(f"  (b) H gap (flat measure BLIND) PASS = {H_pass}  [|rH-nH|={abs(rH.mean()-nH.mean()):.3f}<0.15, "
          f"real_P-real_H={rP.mean()-rH.mean():+.3f}>0.5]", flush=True)
    print(f"  (c) null rejection + generic equality PASS = {null_pass}", flush=True)
    print(f"  construction sanity PASS = {san_pass}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    out = {"construction": san,
           "real_P": rP.tolist(), "real_H": rH.tolist(), "null_P": nP.tolist(), "null_H": nH.tolist(),
           "summary": {"real_P_mean": rP.mean(), "real_P_p2.5": np.percentile(rP, 2.5),
                       "null_P_mean": nP.mean(), "null_P_p95": np.percentile(nP, 95),
                       "real_H_mean": rH.mean(), "null_H_mean": nH.mean(),
                       "real_P_minus_real_H": rP.mean() - rH.mean()},
           "generic_equality": {"marginal_tv": tv, "entropy_rate_reldiff": erd},
           "fork": {"P_pass": bool(P_pass), "H_pass": bool(H_pass), "null_pass": bool(null_pass),
                    "construction_pass": bool(san_pass), "verdict": verdict}}
    json.dump(out, open("data/dcal_verdict.json", "w"), indent=2, default=float)
    print("\nsaved data/dcal_verdict.json", flush=True)


if __name__ == "__main__":
    run()
