#!/usr/bin/env python3
"""D-cal-2-TOPO -- v0.7.3 cross-domain step 2b: a RICHER coordinate-free invariant suite (numpy-only topology).

Pre-registered 2026-06-25 (pre_registration.md "v0.7.3 CROSS-DOMAIN step 2b / D-cal-2-TOPO PRE-REGISTRATION").
Can a richer coordinate-free (permutation-invariant) invariant of the W_HO weighted graph close the
0.684 -> 1.000 gap (ESCAPE) or do all coordinate-free invariants cap near the spectral floor (correspondence
horn HOLDS for higher-order)? NUMPY-ONLY (no persistent-homology library). Reuses the LOCKED D-cal-2 construction.

Usage: python scripts/dcal2_topo.py [smoke|run]
"""
import sys, json
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
import scripts.dcal2 as d   # locked construction: latent_features, make_encoder, encode, w_ho_matrix, spectrum, K, F, A1, A2, EMIT_SEED_*, LATENT_SEEDS

F = d.F
IU = np.triu_indices(F, 1)
NBINS = 50
TOPN = 3 * d.K_H   # top-18 triangle entries


# ---------- coordinate-free topological invariants of a symmetric weight matrix W (zero diagonal) ----------
def _norm(v):
    m = np.max(np.abs(v))
    return v / m if m > 0 else v


def h0_barcode(W):
    """single-linkage merge heights: union-find over edges sorted by DESCENDING weight."""
    w = W[IU]
    order = np.argsort(-w)
    ii, jj = IU[0][order], IU[1][order]
    parent = np.arange(F)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    heights = []
    for e in range(len(order)):
        a, b = find(ii[e]), find(jj[e])
        if a != b:
            parent[a] = b; heights.append(w[order[e]])
            if len(heights) == F - 1:
                break
    heights = np.array(sorted(heights, reverse=True) + [0.0] * (F - 1 - len(heights)))
    return _norm(heights)


def betti1_curve(W):
    """beta1(t) = E(t) - F + C(t) over a normalized threshold grid."""
    w = W[IU]; mx = w.max() if w.size and w.max() > 0 else 1.0
    wn = w / mx
    curve = np.empty(NBINS)
    for b, t in enumerate(np.linspace(0.0, 1.0, NBINS)):
        mask = wn >= t
        E = int(mask.sum())
        # components via union-find on the thresholded edges
        parent = np.arange(F)

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for a, bb in zip(IU[0][mask], IU[1][mask]):
            ra, rb = find(a), find(bb)
            if ra != rb:
                parent[ra] = rb
        C = len({find(x) for x in range(F)})
        curve[b] = E - F + C
    return _norm(curve)


def triangle_dist(W, kind="min"):
    """sorted (descending) top-N of the per-triple min (or geom-mean) of its three W edges."""
    vals = []
    for i, j, k in combinations(range(F), 3):
        e = (W[i, j], W[i, k], W[j, k])
        vals.append(min(e) if kind == "min" else (e[0] * e[1] * e[2]) ** (1.0 / 3.0))
    vals = np.sort(np.array(vals))[::-1][:TOPN]
    return _norm(vals)


def mat_corr(W):
    """matrix-with-correspondence vector (Frobenius-normalized upper-tri) -- the 1.0 CEILING baseline."""
    v = W[IU]
    return v / (np.linalg.norm(v) + 1e-12)


INVARIANTS = {
    "H0_barcode": h0_barcode,
    "betti1_curve": betti1_curve,
    "triangle_min": lambda W: triangle_dist(W, "min"),
    "triangle_geo": lambda W: triangle_dist(W, "geo"),
}


def auroc(real_d, null_d):
    r = np.asarray(real_d)[:, None]; n = np.asarray(null_d)[None, :]
    return float((np.sum(n > r) + 0.5 * np.sum(n == r)) / (r.size * n.size))


def l2(a, b):
    return float(np.linalg.norm(a - b))


def main(mode):
    T = 10_000 if mode == "smoke" else 50_000
    seeds = d.LATENT_SEEDS[:6] if mode == "smoke" else d.LATENT_SEEDS
    enc1 = d.make_encoder(d.A1, d.EMIT_SEED_1); enc2 = d.make_encoder(d.A2, d.EMIT_SEED_2)
    print(f"=== D-cal-2-TOPO [{mode}]  F={F} T={T} latents={len(seeds)}  invariants={list(INVARIANTS)} ===", flush=True)

    # encode + cache W_HO per latent per encoder
    W1, W2 = {}, {}
    for s in seeds:
        _, L, _, _, _, _ = d.latent_features(s, T)
        W1[s] = d.w_ho_matrix(*d.encode(L, enc1, d.EMIT_SEED_1 * 7 + s))
        W2[s] = d.w_ho_matrix(*d.encode(L, enc2, d.EMIT_SEED_2 * 7 + s))
        print(f"  W_HO seed {s}", flush=True)

    # baselines (context): spectrum floor + matrix-with-correspondence ceiling
    def auroc_of(fn):
        I1 = {s: fn(W1[s]) for s in seeds}; I2 = {s: fn(W2[s]) for s in seeds}
        rd = [l2(I1[s], I2[s]) for s in seeds]
        nd = [l2(I1[a], I2[b]) for a in seeds for b in seeds if a != b]
        return auroc(rd, nd), float(np.mean(rd)), float(np.mean(nd))
    spec_auc = auroc_of(d.spectrum)
    mat_auc = auroc_of(mat_corr)
    print(f"\n[baseline FLOOR ] coordinate-free SPECTRUM        AUROC={spec_auc[0]:.3f} (real {spec_auc[1]:.3f}/null {spec_auc[2]:.3f})", flush=True)
    print(f"[baseline CEILING] MATRIX with correspondence    AUROC={mat_auc[0]:.3f} (real {mat_auc[1]:.3f}/null {mat_auc[2]:.3f})", flush=True)

    # the topological invariant suite
    print("\n[coordinate-free TOPOLOGICAL invariants]", flush=True)
    results = {}
    for name, fn in INVARIANTS.items():
        a, rm, nm = auroc_of(fn)
        results[name] = a
        print(f"  {name:16s} AUROC={a:.3f} (real {rm:.3f}/null {nm:.3f})", flush=True)
    best_name = max(results, key=results.get); best = results[best_name]

    # (c) permutation-invariance of each invariant
    s0 = seeds[0]; _, L0, _, _, _, _ = d.latent_features(s0, T)
    O = d.encode(L0, enc2, d.EMIT_SEED_2 * 7 + s0)
    pp = np.random.default_rng(123).permutation(F)
    Wp = d.w_ho_matrix(O[0][:, pp], O[1])
    W0 = d.w_ho_matrix(*O)
    perm = {name: l2(fn(W0), fn(Wp)) for name, fn in INVARIANTS.items()}
    print(f"\n[perm-invariance] max L2 over invariants = {max(perm.values()):.2e} (<1e-9?)", flush=True)

    # ---- FORK ----
    if best > 0.90:
        branch = f"ESCAPE -- {best_name} AUROC={best:.3f} > 0.90: higher-order transmits COORDINATE-FREE (pincer dodged)"
    elif best <= 0.72:
        branch = f"CORRESPONDENCE-HORN HOLDS -- best ({best_name}) AUROC={best:.3f} <= 0.72, near the spectral floor"
    else:
        branch = f"INTERMEDIATE -- best ({best_name}) AUROC={best:.3f} in (0.72,0.90]: partial coordinate-free recovery"
    print(f"\n=== FORK ===\n  spectrum floor {spec_auc[0]:.3f} | matrix-corr ceiling {mat_auc[0]:.3f} | best coordinate-free {best:.3f} ({best_name})", flush=True)
    print(f"  perm-invariance PASS = {max(perm.values()) < 1e-9}", flush=True)
    print(f"  -> {branch}", flush=True)

    out = {"mode": mode, "T": T, "spectrum_floor": spec_auc[0], "matrix_corr_ceiling": mat_auc[0],
           "topo": results, "best": best, "best_name": best_name, "branch": branch,
           "perm_max_l2": max(perm.values())}
    json.dump(out, open(f"data/dcal2_topo_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal2_topo_{mode}.json", flush=True)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "run")
