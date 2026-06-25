#!/usr/bin/env python3
"""D-cal-2 -- v0.7.3 cross-domain step 2 PHASE 2: the PINCER-ESCAPE test (coordinate-free shape invariant).

Pre-registered 2026-06-25 (pre_registration.md "v0.7.3 CROSS-DOMAIN step 2 / D-cal-2 PRE-REGISTRATION").
Does substrate-specific HIGHER-ORDER structure transmit COORDINATE-FREE (permutation-invariant), beyond
generic statistics? Synthetic calibration only; numpy + canonical cit/information.py; reuses hsmm_d1.py.

INVARIANTS (permutation-invariant): sorted eigenvalue spectrum of (pairwise) the F x F raw-MI matrix and
(higher-order) the F x F interaction-information matrix W_HO[i,j] = max_k max(I(i;j|k) - I(i;j), 0). MATCH =
L2 distance between max-abs-normalized sorted spectra. ENSEMBLE null (across-latent). Separation = AUROC.

Usage: python scripts/dcal2.py [smoke|run]
"""
import sys, json
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
from cit.data.hsmm_d1 import generate_stream, N_STATES
from cit.information import coherence_weighted_mutual_information, pmf_from_counts

# ---- LOCKED constants (pre_registration.md 2026-06-25 D-cal-2 entry) ----
K = 8
F = 30
K_P = 6                                   # pairwise pairs (12 features)
K_H = 6                                   # higher-order triples (18 features)
A1, A2 = 12, 10
MASS = 0.7
EMIT_SEED_1, EMIT_SEED_2 = 10001, 20002
LATENT_SEEDS = list(range(7000, 7012))    # 12 latents


def latent_features(seed, T):
    """Shared latent L (T,F); per-latent VARYING topology + strength profile; all features marginally uniform."""
    states, _ = generate_stream(seed, T)
    rng = np.random.default_rng(seed * 100003 + 7)
    L = np.zeros((T, F), dtype=np.int64)
    perm = rng.permutation(F)
    p_feats = perm[:2 * K_P].reshape(K_P, 2)          # random pairwise assignment
    h_feats = perm[2 * K_P:2 * K_P + 3 * K_H].reshape(K_H, 3)   # random triple assignment
    q = rng.uniform(0.30, 0.95, size=K_P)             # latent-specific pairwise strength profile
    r = rng.uniform(0.30, 0.95, size=K_H)             # latent-specific higher-order strength profile
    for m, (i, j) in enumerate(p_feats):
        b = rng.integers(0, K, T)
        L[:, i] = np.where(rng.random(T) < q[m], b, rng.integers(0, K, T))
        L[:, j] = np.where(rng.random(T) < q[m], b, rng.integers(0, K, T))
    for t, (a, bb, c) in enumerate(h_feats):
        fa = rng.integers(0, K, T); fb = rng.integers(0, K, T)
        M = rng.integers(0, K, N_STATES)
        planted = (fa + fb + M[states]) % K
        L[:, a] = fa; L[:, bb] = fb
        L[:, c] = np.where(rng.random(T) < r[t], planted, rng.integers(0, K, T))
    return states, L, p_feats, h_feats, q, r


def make_encoder(A, table_seed):
    rng = np.random.default_rng(table_seed)
    return np.stack([rng.permutation(A)[:K] for _ in range(F)]), A


def encode(L, enc, noise_seed):
    pi, A = enc
    rng = np.random.default_rng(noise_seed)
    O = np.zeros_like(L)
    for f in range(F):
        prim = pi[f][L[:, f]]
        keep = rng.random(L.shape[0]) < MASS
        other = rng.integers(0, A - 1, L.shape[0])
        other = other + (other >= prim)
        O[:, f] = np.where(keep, prim, other)
    return O, A


def raw_mi(x, y, Ax, Ay):
    counts = np.bincount(x.astype(np.int64) * Ay + y.astype(np.int64),
                         minlength=Ax * Ay).reshape(Ax, Ay).astype(np.float64)
    return coherence_weighted_mutual_information(pmf_from_counts(counts), np.ones(Ax))


def mi_matrix(O, A):
    M = np.zeros((F, F))
    for i, j in combinations(range(F), 2):
        M[i, j] = M[j, i] = raw_mi(O[:, i], O[:, j], A, A)
    return M


def _ii_triple(x, y, z, A):
    """interaction information II(x;y;z) = I(x;y|z) - I(x;y), plug-in from the 3-way joint (bits)."""
    n = np.bincount((x * A + y) * A + z, minlength=A ** 3).reshape(A, A, A).astype(np.float64)
    tot = n.sum(); p = n / tot
    pXY = p.sum(2); pX = p.sum((1, 2)); pY = p.sum((0, 2)); pZ = p.sum((0, 1))
    pXZ = p.sum(1); pYZ = p.sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        mXY = pXY > 0
        IXY = float((pXY[mXY] * np.log2(pXY[mXY] / (pX[:, None] * pY[None, :])[mXY])).sum())
        m3 = p > 0
        num = p[m3]
        den = (pXZ[:, None, :] * pYZ[None, :, :] / np.maximum(pZ[None, None, :], 1e-300))[m3]
        IXY_Z = float((num * np.log2(np.maximum(num, 1e-300) / np.maximum(den, 1e-300))).sum())
    return IXY_Z - IXY


def w_ho_matrix(O, A):
    """W_HO[i,j] = max over k of max(II(i;j;k), 0); II symmetric -> one pass over unordered triples."""
    W = np.zeros((F, F))
    for i, j, k in combinations(range(F), 3):
        ii = max(_ii_triple(O[:, i], O[:, j], O[:, k], A), 0.0)
        if ii > W[i, j]: W[i, j] = W[j, i] = ii
        if ii > W[i, k]: W[i, k] = W[k, i] = ii
        if ii > W[j, k]: W[j, k] = W[k, j] = ii
    return W


def spectrum(Msym):
    ev = np.sort(np.linalg.eigvalsh(Msym))
    mx = np.max(np.abs(ev))
    return ev / mx if mx > 0 else ev


def dist(sp1, sp2):
    return float(np.linalg.norm(sp1 - sp2))


def auroc(real_d, null_d):
    r = np.asarray(real_d)[:, None]; n = np.asarray(null_d)[None, :]
    return float((np.sum(n > r) + 0.5 * np.sum(n == r)) / (r.size * n.size))


def feat_marginal_tv(Oa, Ob, A):
    return float(max(0.5 * np.abs(np.bincount(Oa[:, f], minlength=A) / Oa.shape[0]
                                  - np.bincount(Ob[:, f], minlength=A) / Ob.shape[0]).sum()
                     for f in range(F)))


def cond_entropy_rate(O, A):
    H = []
    for f in range(F):
        x = O[:, f]
        j = np.bincount(x[:-1] * A + x[1:], minlength=A * A).reshape(A, A).astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            p = np.where(j > 0, j / np.maximum(j.sum(1, keepdims=True), 1e-12), 0.0)
            H.append(-(j / j.sum() * np.where(p > 0, np.log2(np.maximum(p, 1e-12)), 0.0)).sum())
    return np.array(H)


def main(mode):
    T = 10_000 if mode == "smoke" else 50_000
    seeds = LATENT_SEEDS[:6] if mode == "smoke" else LATENT_SEEDS
    enc1 = make_encoder(A1, EMIT_SEED_1); enc2 = make_encoder(A2, EMIT_SEED_2)
    print(f"=== D-cal-2 [{mode}]  K={K} F={F} T={T} K_P={K_P} K_H={K_H} A1={A1} A2={A2} latents={len(seeds)} ===", flush=True)

    # ---- construction sanity on the LATENT (alphabet K) ----
    states, L, p_feats, h_feats, q, r = latent_features(seeds[0], T)
    pair_mi = [raw_mi(L[:, i], L[:, j], K, K) for (i, j) in p_feats]
    trip_pair_mi = [raw_mi(L[:, a], L[:, b], K, K) for (a, b, c) in h_feats for (a, b) in [(a, b), (a, c), (b, c)]]
    trip_reg = []
    for (a, bb, c) in h_feats:
        joint = (L[:, a] * K + L[:, bb]) * K + L[:, c]
        trip_reg.append(round(raw_mi(joint, states, K ** 3, N_STATES), 3))
    # W_HO on the latent: pairwise-module pairs vs triple pairs
    who_lat = w_ho_matrix(L, K) if mode == "smoke" else None
    if who_lat is not None:
        wp = max(who_lat[i, j] for (i, j) in p_feats)
        wt = max(who_lat[a, b] for (a, bb, c) in h_feats for (a, b) in [(a, bb), (a, c), (bb, c)])
        print(f"[sanity] W_HO max on pairwise-module pairs={wp:.4f}  on triple pairs={wt:.4f} (triple >> pairwise?)", flush=True)
    print(f"[sanity] q={np.round(q,2).tolist()} r={np.round(r,2).tolist()}", flush=True)
    print(f"[sanity] latent pairwise-module MI min={min(pair_mi):.3f} max={max(pair_mi):.3f} (graded,>0.02)", flush=True)
    print(f"[sanity] latent within-triple pairwise MI max={max(trip_pair_mi):.4f} (~0,<0.01)", flush=True)
    print(f"[sanity] I(triple;regime)={trip_reg} bits (high-r >0.5)", flush=True)
    # topology varies across latents?
    profiles = [tuple(np.round(latent_features(s, T)[4], 2)) for s in seeds[:3]]
    print(f"[sanity] pairwise strength profiles (3 latents) distinct? {len(set(profiles))==len(profiles)}", flush=True)

    # ---- encode the ensemble + invariants ----
    SP1p, SP2p, SP1h, SP2h = {}, {}, {}, {}
    for s in seeds:
        _, Ls, _, _, _, _ = latent_features(s, T)
        O1 = encode(Ls, enc1, EMIT_SEED_1 * 7 + s); O2 = encode(Ls, enc2, EMIT_SEED_2 * 7 + s)
        SP1p[s] = spectrum(mi_matrix(*O1)); SP2p[s] = spectrum(mi_matrix(*O2))
        SP1h[s] = spectrum(w_ho_matrix(*O1)); SP2h[s] = spectrum(w_ho_matrix(*O2))
        print(f"  encoded+invariants seed {s}", flush=True)

    def readout(SP1, SP2, tag):
        real_d = [dist(SP1[s], SP2[s]) for s in seeds]
        null_d = [dist(SP1[si], SP2[sj]) for si in seeds for sj in seeds if si != sj]
        a = auroc(real_d, null_d)
        print(f"[{tag}] real dist mean={np.mean(real_d):.4f} | null dist mean={np.mean(null_d):.4f} "
              f"| AUROC={a:.3f}", flush=True)
        return a, real_d, null_d

    print("", flush=True)
    auc_p, rdp, ndp = readout(SP1p, SP2p, "PAIRWISE")
    auc_h, rdh, ndh = readout(SP1h, SP2h, "HIGHER-ORDER")

    # ---- (c) permutation invariance ----
    s0 = seeds[0]; _, Ls, _, _, _, _ = latent_features(s0, T)
    O2 = encode(Ls, enc2, EMIT_SEED_2 * 7 + s0)
    pp = np.random.default_rng(123).permutation(F)
    O2perm = (O2[0][:, pp], O2[1])
    perm_d = dist(spectrum(mi_matrix(*O2)), spectrum(mi_matrix(*O2perm)))
    print(f"\n[perm-invariance] relabel enc2 features -> pairwise spectrum L2 dist = {perm_d:.2e} (<1e-9?)", flush=True)

    # ---- (d) generic equality ----
    _, L0, _, _, _, _ = latent_features(s0, T); _, L1, _, _, _, _ = latent_features(seeds[1], T)
    e0 = encode(L0, enc2, EMIT_SEED_2 * 7 + s0)[0]; e1 = encode(L1, enc2, EMIT_SEED_2 * 7 + seeds[1])[0]
    tv = feat_marginal_tv(e0, e1, A2)
    her, hen = cond_entropy_rate(e0, A2), cond_entropy_rate(e1, A2)
    erd = float(np.max(np.abs(her - hen) / np.maximum(her, 1e-9)))
    print(f"[generic equality] enc2 marginal TV={tv:.4f} (<0.02?)  entropy-rate rel-diff={erd:.4f} (<0.02?)", flush=True)

    # ---- FORK ----
    P_pass = auc_p > 0.90
    if auc_h > 0.90:
        branch = "ESCAPE EXISTS (higher-order transmits coordinate-free, beyond generic)"
    elif 0.40 <= auc_h <= 0.65:
        branch = "PINCER HOLDS (higher-order does NOT transmit coordinate-free) -- honest descriptive negative"
    else:
        branch = f"INTERMEDIATE (AUROC_HO={auc_h:.3f}) -- partial, no clean branch"
    print(f"\n=== FORK ===", flush=True)
    print(f"  (a) PAIRWISE positive control AUROC={auc_p:.3f} PASS={P_pass} (>0.90)", flush=True)
    print(f"  (b) HIGHER-ORDER AUROC={auc_h:.3f} -> {branch}", flush=True)
    print(f"  (c) perm-invariance dist={perm_d:.1e} PASS={perm_d < 1e-9}", flush=True)
    print(f"  (d) generic equality TV={tv:.4f} erd={erd:.4f} PASS={tv < 0.02 and erd < 0.02}", flush=True)

    out = {"mode": mode, "T": T, "AUROC_pairwise": auc_p, "AUROC_HO": auc_h, "branch": branch,
           "perm_dist": perm_d, "generic": {"tv": tv, "erd": erd},
           "real_dist_pair": rdp, "null_dist_pair_mean": float(np.mean(ndp)),
           "real_dist_HO": rdh, "null_dist_HO_mean": float(np.mean(ndh)),
           "sanity": {"pair_mi_min": min(pair_mi), "pair_mi_max": max(pair_mi),
                      "trip_pair_mi_max": max(trip_pair_mi), "trip_regime_mi": trip_reg}}
    json.dump(out, open(f"data/dcal2_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal2_{mode}.json", flush=True)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "run")
