#!/usr/bin/env python3
"""D-cal-3 -- v0.7.3 step 2c PHASE 2: the WIRING test (does higher-order TOPOLOGY transmit coordinate-free
when the strength channel is CLOSED, nominal AND realized?).

Pre-registered 2026-06-25 (pre_registration.md "v0.7.3 CROSS-DOMAIN step 2c PHASE 2 / D-cal-3 PRE-REGISTRATION").
Step 2c showed the coordinate-free "escape" rode the coupling-STRENGTH DISTRIBUTION (nominal + realized via the
shared latent realization), NOT the wiring, and the dcal2 topologies were ISOMORPHIC (6 disjoint triangles). D-cal-3
CLOSES the strength channel with a DETERMINISTIC coupling c=(fa+fb)%K (population II = log2 K identical for every
hyperedge -> realized weight multiset matched at the realized level) and VARIES the topology NON-isomorphically
(per-latent random source-sharing motifs: disjoint / chained / star). Only the WIRING then varies coordinate-free.

Synthetic calibration only; numpy + canonical cit/information.py (reused via dcal2); coordinate-free
(permutation-invariant) invariants only; across-latent ENSEMBLE null. NO real-domain data, NO metacoherence claim.
Usage: python scripts/dcal3.py [smoke|run]
"""
import sys, json
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
import scripts.dcal2 as d
import scripts.dcal2_topo as topo

F, K, A1, A2, MASS = d.F, d.K, d.A1, d.A2, d.MASS
assert K == 8, "D-cal-3 GF(8) orthogonal-source construction requires K=8"
K_H = 6                       # fixed number of synergistic triples per latent
M_GLOBAL = 8                  # the 8 GF(8) multipliers {0..7} -> 8 pairwise-orthogonal global sources
N_USED_LO, N_USED_HI = 6, 8   # sources used per latent (6 triangles over 6-8 sources -> diverse non-iso graphs)
GLOBAL_SRC_SEED = 90001       # shared base-shuffle (sources temporally iid -> full entropy rate, matched)
EMIT_SEED_1, EMIT_SEED_2 = d.EMIT_SEED_1, d.EMIT_SEED_2
LATENT_SEEDS = d.LATENT_SEEDS
IU = np.triu_indices(F, 1)


# ---------------- GF(8) orthogonal global sources (EXACT closure of the strength channel) ----------------
# Step-2c lesson + two smoke-amends: a deterministic coupling fixes the POPULATION II (= log2 K) but the
# finite-sample II ESTIMATE leaks via the source-pair realization -- per-latent sources leak (shared
# realization, triangle_min 0.87); GLOBAL random sources leak MORE (stable per-pair weights fingerprint the
# wiring, 0.95). The realized weight multiset is ENTANGLED with the wiring UNLESS every coupling has EXACTLY
# equal weight. That requires EXACTLY-uniform source-pair joints = ORTHOGONAL sources. GF(8) gives them:
# source_p = u XOR (alpha_p . v) over GF(8) with alpha_p the 7 distinct nonzero elements; for ANY pair the
# 2x2 map [[1,alpha_p],[1,alpha_q]] has det alpha_p XOR alpha_q != 0 -> invertible -> (B_p,B_q) EXACTLY
# uniform on GF(8)^2 -> II(B_p;B_q;B_p XOR B_q) = exactly 3 bits for EVERY pair. All triangles interchangeable
# -> triangle_min multiset identical across latents -> strength channel CLOSED (even through the encoder);
# only the WIRING (overlap of which sources feed which sinks) varies.
def _gf8_tables():
    exp = np.zeros(14, dtype=np.int64); log = np.zeros(8, dtype=np.int64)
    x = 1
    for i in range(7):
        exp[i] = x; log[x] = i
        x <<= 1
        if x & 0x8:
            x ^= 0x0B                                       # reduce mod x^3 + x + 1
    exp[7:] = exp[:7]
    return exp, log


_EXP, _LOG = _gf8_tables()


def _gf8_mul(a, b):
    a, b = np.broadcast_arrays(np.asarray(a, dtype=np.int64), np.asarray(b, dtype=np.int64))
    out = np.zeros(a.shape, dtype=np.int64)
    m = (a != 0) & (b != 0)
    out[m] = _EXP[(_LOG[a[m]] + _LOG[b[m]]) % 7]
    return out


def global_sources(T):
    """7 pairwise-orthogonal GF(8) source streams of length Teff=(T//64)*64. The balanced (u,v) base is
    SHUFFLED (shared seed) so each combo appears exactly Teff/64 times (EXACT pairwise balance preserved)
    but the temporal order is iid -> sources have full entropy rate (matches the iid noise features)."""
    Teff = (T // 64) * 64
    idx = np.tile(np.arange(64), Teff // 64)
    np.random.default_rng(GLOBAL_SRC_SEED).shuffle(idx)    # shared shuffle -> temporally iid, still balanced
    u = (idx // 8).astype(np.int64); v = (idx % 8).astype(np.int64)
    alphas = np.arange(0, M_GLOBAL, dtype=np.int64)        # GF(8) multipliers {0..7}; det(p,q)=alpha_p^alpha_q!=0
    return np.stack([u ^ _gf8_mul(alpha, v) for alpha in alphas], axis=1)   # (Teff, M_GLOBAL)


def _make_wiring_raw(seed, attempt):
    """Per-latent hypergraph over the GLOBAL source pool: K_H distinct SINKS, each fed by 2 GLOBAL source
    indices; n_used (N_USED_LO..N_USED_HI) sources -> the 6 triangles spread over the sources with varying
    overlap (the source-graph = 6 distinct source-pairs). Varying n_used + random pairing -> non-isomorphic."""
    rng = np.random.default_rng(seed * 911 + 13 + attempt * 1_000_003)
    feats = rng.permutation(F)
    sinks = feats[:K_H]
    n_used = int(rng.integers(N_USED_LO, N_USED_HI + 1))
    used_idx = rng.permutation(M_GLOBAL)[:n_used]
    src_feat = {int(used_idx[i]): int(feats[K_H + i]) for i in range(n_used)}
    triples, seen = [], set()
    for t in range(K_H):
        for _try in range(300):
            pq = tuple(sorted(int(x) for x in rng.choice(used_idx, size=2, replace=False)))
            if pq not in seen:
                seen.add(pq); break
        triples.append((pq[0], pq[1], int(sinks[t])))
    return triples, src_feat, n_used


def _abstract_adj(triples, src_feat):
    """Clean (noise-free) W_HO adjacency of a wiring: 3-cliques per triangle (binary)."""
    A = [set() for _ in range(F)]
    for (p, q, c) in triples:
        a, b = src_feat[p], src_feat[q]
        for (i, j) in [(a, b), (a, c), (b, c)]:
            A[i].add(j); A[j].add(i)
    return A


def _wl_signature(A, rounds=4):
    """Weisfeiler-Leman color-refinement hash of the abstract graph -- a strong, permutation-invariant
    ISOMORPHISM invariant INDEPENDENT of the 5 tested readouts (used only to select ground-truth-distinct
    wirings; WL-distinct => non-isomorphic). Deterministic, numpy-free integer hashing."""
    colors = [len(A[i]) for i in range(F)]                 # init by degree
    for _ in range(rounds):
        raw = [(colors[i], tuple(sorted(colors[j] for j in A[i]))) for i in range(F)]
        order = {c: k for k, c in enumerate(sorted(set(raw)))}
        colors = [order[c] for c in raw]
    return tuple(sorted(colors))


_RESOLVED = None


def _resolve():
    """Resolve, ONCE, a mutually NON-ISOMORPHIC wiring per LATENT_SEEDS via the WL signature (ground-truth
    structure, NOT a tested invariant -> no selection bias toward spectrum/motif). Deterministic."""
    global _RESOLVED
    if _RESOLVED is not None:
        return _RESOLVED
    resolved, sigs = {}, []
    for s in LATENT_SEEDS:
        chosen = None
        for attempt in range(6000):
            tr, sf, nu = _make_wiring_raw(s, attempt)
            sig = _wl_signature(_abstract_adj(tr, sf))
            if sig not in sigs:
                chosen = (tr, sf, nu, sig); break
        if chosen is None:
            chosen = (tr, sf, nu, sig)                      # give up (should not happen)
        resolved[s] = chosen[:3]; sigs.append(chosen[3])
    _RESOLVED = resolved
    return resolved


def make_wiring(seed):
    return _resolve()[seed]


def latent_features_d3(seed, T, B=None):
    """Sources = GF(8) orthogonal GLOBAL pool B (shared across latents); sink = B_p XOR B_q (GF(8) add;
    II = exactly 3 bits). Length follows B (Teff=(T//64)*64). Noise features uniform iid per latent."""
    if B is None:
        B = global_sources(T)
    Teff = B.shape[0]
    rng = np.random.default_rng(seed * 100003 + 7)
    L = rng.integers(0, K, size=(Teff, F)).astype(np.int64)   # noise features uniform iid
    triples, src_feat, n_used = make_wiring(seed)
    for (p, q, c) in triples:
        L[:, src_feat[p]] = B[:, p]
        L[:, src_feat[q]] = B[:, q]
        L[:, c] = B[:, p] ^ B[:, q]                        # GF(8) synergy -> sink (exactly II=3 bits)
    return L, triples, n_used


# ---------------- coordinate-free MOTIF census of the thresholded W_HO graph ----------------
def motif_census(W, q=0.5):
    """Permutation-invariant small-subgraph census of the binary graph W>=q*max(W)."""
    w = W[IU]; mx = w.max() if w.size else 0.0
    out = np.zeros(2 * F + 3)
    if mx <= 0:
        return out
    A = (W >= q * mx).astype(np.float64)
    np.fill_diagonal(A, 0.0)
    deg = A.sum(1)
    n_edges = float(A.sum() / 2.0)
    n_tri = float(np.trace(A @ A @ A) / 6.0)
    n_wedge = float(np.sum(deg * (deg - 1.0) / 2.0))
    # components via union-find
    parent = np.arange(F)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i, j in zip(*np.where(np.triu(A, 1) > 0)):
        ri, rj = find(int(i)), find(int(j))
        if ri != rj:
            parent[ri] = rj
    sizes = np.bincount([find(x) for x in range(F)], minlength=F).astype(np.float64)
    deg_sorted = np.sort(deg)[::-1]
    size_sorted = np.sort(sizes)[::-1]
    out[:F] = deg_sorted
    out[F:2 * F] = size_sorted
    out[2 * F:] = [n_edges, n_tri, n_wedge]
    m = np.max(np.abs(out))
    return out / m if m > 0 else out


def auroc_of(invfn, W1, W2, seeds):
    I1 = {s: invfn(W1[s]) for s in seeds}; I2 = {s: invfn(W2[s]) for s in seeds}
    rd = [topo.l2(I1[s], I2[s]) for s in seeds]
    nd = [topo.l2(I1[a], I2[b]) for a in seeds for b in seeds if a != b]
    return topo.auroc(rd, nd), float(np.mean(rd)), float(np.mean(nd))


INVARIANTS = {
    "motif_census": motif_census,
    "H0_barcode": topo.h0_barcode,
    "spectrum": d.spectrum,
    "triangle_geo": lambda W: topo.triangle_dist(W, "geo"),
    "betti1_curve": topo.betti1_curve,
}


def main(mode):
    T = 10_000 if mode == "smoke" else 50_000
    seeds = LATENT_SEEDS[:6] if mode == "smoke" else LATENT_SEEDS
    enc1 = d.make_encoder(A1, EMIT_SEED_1); enc2 = d.make_encoder(A2, EMIT_SEED_2)
    print(f"=== D-cal-3 WIRING TEST [{mode}]  F={F} K={K} K_H={K_H} T={T} latents={len(seeds)} ===", flush=True)

    B = global_sources(T)                                  # shared source pool (once)

    # ---- (i) non-isomorphism (ground-truth WL signature of the abstract wiring) ----
    wl_sigs, npools = {}, {}
    for s in seeds:
        tr, sf, nu = make_wiring(s)
        wl_sigs[s] = _wl_signature(_abstract_adj(tr, sf)); npools[s] = nu
    iso_pairs = sum(1 for a in seeds for b in seeds if a < b and wl_sigs[a] == wl_sigs[b])
    print(f"[i non-iso] WL-distinct wirings: {len(set(wl_sigs.values()))}/{len(seeds)} "
          f"(isomorphic pairs={iso_pairs}); n_used per latent={[npools[s] for s in seeds]}", flush=True)
    tr0, sf0, npool0 = make_wiring(seeds[0])
    L0, _, _ = latent_features_d3(seeds[0], T, B)
    iis = [d.raw_mi((L0[:, sf0[p]] * K + L0[:, sf0[q]]).astype(np.int64), L0[:, c], K * K, K) for (p, q, c) in tr0]
    print(f"[sanity] latent0 n_used={npool0} triples(globalP,globalQ,sinkFeat)={tr0}", flush=True)
    print(f"[sanity] sink determinacy I((srcP,srcQ);sink)={np.round(iis,3).tolist()} bits (== log2K={np.log2(K):.3f})", flush=True)

    # ---- encode the ensemble + cache W_HO ----
    W1, W2 = {}, {}
    for s in seeds:
        L, _, _ = latent_features_d3(s, T, B)
        W1[s] = d.w_ho_matrix(*d.encode(L, enc1, EMIT_SEED_1 * 7 + s))
        W2[s] = d.w_ho_matrix(*d.encode(L, enc2, EMIT_SEED_2 * 7 + s))
        print(f"  W_HO seed {s}", flush=True)

    # ---- baselines: triangle_min (strength reader -> CLOSURE gate) + matrix-corr (ceiling) ----
    tmin = auroc_of(lambda W: topo.triangle_dist(W, "min"), W1, W2, seeds)
    mat = auroc_of(topo.mat_corr, W1, W2, seeds)
    print(f"\n[ii CLOSURE  ] triangle_min (strength reader) AUROC={tmin[0]:.3f} (real {tmin[1]:.3f}/null {tmin[2]:.3f})  [want ~chance <=0.65]", flush=True)
    print(f"[ceiling     ] matrix WITH correspondence    AUROC={mat[0]:.3f} (real {mat[1]:.3f}/null {mat[2]:.3f})", flush=True)

    # ---- the coordinate-free TOPOLOGY invariants ----
    print("\n[coordinate-free TOPOLOGY invariants (strength closed -> these read WIRING)]", flush=True)
    results = {}
    for name, fn in INVARIANTS.items():
        a, rm, nm = auroc_of(fn, W1, W2, seeds)
        results[name] = a
        print(f"  {name:14s} AUROC={a:.3f} (real {rm:.3f}/null {nm:.3f})", flush=True)
    best_name = max(results, key=results.get); best = results[best_name]

    # ---- (iii) perm-invariance ----
    s0 = seeds[0]; L, _, _ = latent_features_d3(s0, T, B)
    O = d.encode(L, enc2, EMIT_SEED_2 * 7 + s0)
    pp = np.random.default_rng(123).permutation(F)
    W0 = d.w_ho_matrix(*O); Wp = d.w_ho_matrix(O[0][:, pp], O[1])
    perm = {name: topo.l2(fn(W0), fn(Wp)) for name, fn in {**INVARIANTS, "triangle_min": lambda W: topo.triangle_dist(W, "min")}.items()}
    print(f"\n[iii perm-invariance] max L2 over invariants = {max(perm.values()):.2e} (<1e-9?)", flush=True)

    # ---- (iv) generic equality ----
    L1, _, _ = latent_features_d3(seeds[1], T, B)
    e0 = d.encode(L0, enc2, EMIT_SEED_2 * 7 + s0)[0]; e1 = d.encode(L1, enc2, EMIT_SEED_2 * 7 + seeds[1])[0]
    tv = d.feat_marginal_tv(e0, e1, A2)
    her, hen = d.cond_entropy_rate(e0, A2), d.cond_entropy_rate(e1, A2)
    erd = float(np.max(np.abs(her - hen) / np.maximum(her, 1e-9)))
    print(f"[iv generic equality] enc2 marginal TV={tv:.4f} (<0.02?)  entropy-rate rel-diff={erd:.4f} (<0.02?)", flush=True)

    # ---- FORK ----
    closed = tmin[0] <= 0.65
    if best > 0.90 and closed:
        branch = f"ESCAPE -- {best_name} AUROC={best:.3f}>0.90 with strength closed (tmin {tmin[0]:.3f}): the WIRING transmits coordinate-free"
    elif best <= 0.65:
        branch = f"CORRESPONDENCE HORN HOLDS -- best ({best_name}) AUROC={best:.3f}<=0.65: the wiring does NOT transmit coordinate-free"
    elif not closed:
        branch = f"INCONCLUSIVE -- strength channel NOT closed (triangle_min {tmin[0]:.3f}>0.65); AMEND before trusting"
    else:
        branch = f"INTERMEDIATE -- best ({best_name}) AUROC={best:.3f} in (0.65,0.90]"
    print(f"\n=== FORK ===", flush=True)
    print(f"  closure (triangle_min ~chance): {closed} ({tmin[0]:.3f})", flush=True)
    print(f"  ceiling (matrix w/ correspondence): {mat[0]:.3f}", flush=True)
    print(f"  best coordinate-free TOPOLOGY invariant: {best:.3f} ({best_name})", flush=True)
    print(f"  perm-invariance PASS = {max(perm.values()) < 1e-9}", flush=True)
    print(f"  -> {branch}", flush=True)

    out = {"mode": mode, "T": T, "closure_triangle_min": tmin[0], "ceiling_matrix_corr": mat[0],
           "topo": results, "best": best, "best_name": best_name, "branch": branch,
           "perm_max_l2": max(perm.values()), "iso_identical_pairs": iso_pairs,
           "generic": {"tv": tv, "erd": erd}}
    json.dump(out, open(f"data/dcal3_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal3_{mode}.json", flush=True)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "run")
