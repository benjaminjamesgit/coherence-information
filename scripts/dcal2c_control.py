#!/usr/bin/env python3
"""D-cal-2c CONTROL -- v0.7.3 step 2c PHASE 1: the fixed-strength control.

Tests whether the recorded D-cal-2-topo "escape" (higher-order AUROC ~0.98) transmits the
latent-specific STRENGTH PROFILE (the coupling-strength multiset) or the higher-order
TOPOLOGY / wiring. The dcal2 construction plants K_H DISJOINT triangles per latent, so every
latent's W_HO graph is K_H disjoint K3 subgraphs -- ISOMORPHIC across the ensemble. The only
latent-specific coordinate-free content is then the edge-strength multiset (a function of r).

Control: FIX the strength profiles (q, r) across ALL latents (vary only the triple/pair
ASSIGNMENT, which is washed out by permutation invariance) and recompute:
  - HIGHER-ORDER:  triangle_min + H0_barcode AUROC   EXPECT ~chance if the escape rode strengths
  - PAIRWISE:      spectrum AUROC                     topology (stays 1.0) vs strengths (collapses)
Also asserts the ISOMORPHISM (h_feats rows disjoint -> disjoint triangles) and that strengths
are now identical across latents.

Synthetic only; numpy + canonical cit/information.py (reused via dcal2). Coordinate-free invariants
only. Reuses the LOCKED dcal2 / dcal2_topo machinery by overriding only the strength draws.
Usage: python scripts/dcal2c_control.py [smoke|run]
"""
import sys, json
import numpy as np

sys.path.insert(0, ".")
import scripts.dcal2 as d
import scripts.dcal2_topo as topo
from cit.data.hsmm_d1 import generate_stream, N_STATES

F, K, K_P, K_H = d.F, d.K, d.K_P, d.K_H
Q_FIXED = np.linspace(0.35, 0.92, K_P)   # fixed pairwise strength profile (was rng.uniform per latent)
R_FIXED = np.linspace(0.35, 0.92, K_H)   # fixed higher-order strength profile


def latent_features_fixed(seed, T):
    """dcal2.latent_features with FIXED q, r across latents; only the assignment varies.

    The rng stream is advanced by discarded q/r draws so the plant-loop sample realization is
    bit-identical to the original except for the strength VALUES used in the keep-thresholds.
    """
    states, _ = generate_stream(seed, T)
    rng = np.random.default_rng(seed * 100003 + 7)
    L = np.zeros((T, F), dtype=np.int64)
    perm = rng.permutation(F)
    p_feats = perm[:2 * K_P].reshape(K_P, 2)
    h_feats = perm[2 * K_P:2 * K_P + 3 * K_H].reshape(K_H, 3)
    q = rng.uniform(0.30, 0.95, size=K_P); q[:] = Q_FIXED   # advance stream, then fix
    r = rng.uniform(0.30, 0.95, size=K_H); r[:] = R_FIXED
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


def latent_features_split(seed, T, plant_salt):
    """Same assignment (perm) + FIXED strengths as latent_features_fixed, but an INDEPENDENT
    plant realization (regime path + plant RNG salted by plant_salt). Used by the realization-broken
    control: if the fixed-strength residual is the SHARED latent realization, encoding two DIFFERENT
    realizations of the same latent as the 'real' pair must drop the AUROC to chance.
    """
    states, _ = generate_stream(seed + 1000 * plant_salt, T)   # independent regime path
    rng = np.random.default_rng(seed * 100003 + 7)
    perm = rng.permutation(F)                                   # assignment fixed to the seed
    p_feats = perm[:2 * K_P].reshape(K_P, 2)
    h_feats = perm[2 * K_P:2 * K_P + 3 * K_H].reshape(K_H, 3)
    q, r = Q_FIXED, R_FIXED
    L = np.zeros((T, F), dtype=np.int64)
    prng = np.random.default_rng(seed * 100003 + 7 + 777 * plant_salt)   # independent plant stream
    for m, (i, j) in enumerate(p_feats):
        b = prng.integers(0, K, T)
        L[:, i] = np.where(prng.random(T) < q[m], b, prng.integers(0, K, T))
        L[:, j] = np.where(prng.random(T) < q[m], b, prng.integers(0, K, T))
    for t, (a, bb, c) in enumerate(h_feats):
        fa = prng.integers(0, K, T); fb = prng.integers(0, K, T)
        M = prng.integers(0, K, N_STATES)
        planted = (fa + fb + M[states]) % K
        L[:, a] = fa; L[:, bb] = fb
        L[:, c] = np.where(prng.random(T) < r[t], planted, prng.integers(0, K, T))
    return states, L, p_feats, h_feats, q, r


def assignment(seed):
    rng = np.random.default_rng(seed * 100003 + 7)
    perm = rng.permutation(F)
    return perm[:2 * K_P].reshape(K_P, 2), perm[2 * K_P:2 * K_P + 3 * K_H].reshape(K_H, 3)


def realbreak_main(mode):
    """Realization-broken control: real pair = two INDEPENDENT realizations of the same latent."""
    T = 10_000 if mode == "realbreak_smoke" else 50_000
    seeds = d.LATENT_SEEDS[:6] if mode == "realbreak_smoke" else d.LATENT_SEEDS
    enc1 = d.make_encoder(d.A1, d.EMIT_SEED_1); enc2 = d.make_encoder(d.A2, d.EMIT_SEED_2)
    print(f"=== D-cal-2c REALIZATION-BROKEN [{mode}]  T={T} latents={len(seeds)} ===", flush=True)
    print(f"  real pair = enc1(realization salt=1) vs enc2(realization salt=2) of the SAME latent", flush=True)
    W1h, W2h = {}, {}
    for s in seeds:
        _, La, _, _, _, _ = latent_features_split(s, T, 1)
        _, Lb, _, _, _, _ = latent_features_split(s, T, 2)
        W1h[s] = d.w_ho_matrix(*d.encode(La, enc1, d.EMIT_SEED_1 * 7 + s))
        W2h[s] = d.w_ho_matrix(*d.encode(Lb, enc2, d.EMIT_SEED_2 * 7 + s))
        print(f"  computed seed {s}", flush=True)
    tmin = auroc_of(lambda W: topo.triangle_dist(W, "min"), W1h, W2h, seeds)
    h0 = auroc_of(topo.h0_barcode, W1h, W2h, seeds)
    print(f"\n[HIGHER-ORDER triangle_min] AUROC={tmin[0]:.3f} (real {tmin[1]:.3f}/null {tmin[2]:.3f})", flush=True)
    print(f"[HIGHER-ORDER H0_barcode ] AUROC={h0[0]:.3f} (real {h0[1]:.3f}/null {h0[2]:.3f})", flush=True)
    ho_best = max(tmin[0], h0[0])
    print(f"\n=== VERDICT ===", flush=True)
    print(f"  best={ho_best:.3f} -> {'CHANCE: the fixed-strength residual WAS the shared latent realization' if ho_best <= 0.65 else 'still separates: residual NOT (only) shared realization'}", flush=True)
    out = {"mode": mode, "T": T, "ho_triangle_min_AUROC": tmin[0], "ho_h0_barcode_AUROC": h0[0], "ho_best": ho_best}
    json.dump(out, open(f"data/dcal2c_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal2c_{mode}.json", flush=True)
    return out


def auroc_of(invfn, W1, W2, seeds):
    I1 = {s: invfn(W1[s]) for s in seeds}; I2 = {s: invfn(W2[s]) for s in seeds}
    rd = [topo.l2(I1[s], I2[s]) for s in seeds]
    nd = [topo.l2(I1[a], I2[b]) for a in seeds for b in seeds if a != b]
    return topo.auroc(rd, nd), float(np.mean(rd)), float(np.mean(nd))


def main(mode):
    T = 10_000 if mode == "smoke" else 50_000
    seeds = d.LATENT_SEEDS[:6] if mode == "smoke" else d.LATENT_SEEDS
    enc1 = d.make_encoder(d.A1, d.EMIT_SEED_1); enc2 = d.make_encoder(d.A2, d.EMIT_SEED_2)
    print(f"=== D-cal-2c CONTROL [{mode}]  F={F} T={T} K_P={K_P} K_H={K_H} latents={len(seeds)} ===", flush=True)
    print(f"  FIXED q={np.round(Q_FIXED,3).tolist()}", flush=True)
    print(f"  FIXED r={np.round(R_FIXED,3).tolist()}", flush=True)

    # ---- structural checks: isomorphism + fixed strengths ----
    iso_ok = True
    for s in seeds:
        _, h_feats = assignment(s)
        flat = h_feats.reshape(-1)
        iso_ok &= (len(set(flat.tolist())) == flat.size)   # disjoint triple features -> disjoint K3s
    assign_varies = len({tuple(assignment(s)[1].reshape(-1).tolist()) for s in seeds}) == len(seeds)
    print(f"[isomorphism] every latent HO topology = {K_H} disjoint triangles (h_feats disjoint): {iso_ok}", flush=True)
    print(f"[assignment] triple assignment differs across all latents: {assign_varies}", flush=True)
    print(f"[fixed-strength] q,r identical across latents by construction (Q_FIXED/R_FIXED).", flush=True)

    # ---- encode the ensemble + cache pairwise spectra and HO matrices ----
    W1h, W2h, SP1p, SP2p = {}, {}, {}, {}
    for s in seeds:
        _, L, _, _, _, _ = latent_features_fixed(s, T)
        O1 = d.encode(L, enc1, d.EMIT_SEED_1 * 7 + s)
        O2 = d.encode(L, enc2, d.EMIT_SEED_2 * 7 + s)
        W1h[s] = d.w_ho_matrix(*O1); W2h[s] = d.w_ho_matrix(*O2)
        SP1p[s] = d.spectrum(d.mi_matrix(*O1)); SP2p[s] = d.spectrum(d.mi_matrix(*O2))
        print(f"  computed seed {s}", flush=True)

    # ---- HIGHER-ORDER coordinate-free invariants under FIXED strengths ----
    tmin = auroc_of(lambda W: topo.triangle_dist(W, "min"), W1h, W2h, seeds)
    h0 = auroc_of(topo.h0_barcode, W1h, W2h, seeds)
    # ---- PAIRWISE spectrum under FIXED strengths ----
    rdp = [topo.l2(SP1p[s], SP2p[s]) for s in seeds]
    ndp = [topo.l2(SP1p[a], SP2p[b]) for a in seeds for b in seeds if a != b]
    auc_pair = topo.auroc(rdp, ndp)

    print(f"\n--- CONTROL RESULT (fixed strengths; reference = varying-strength escape) ---", flush=True)
    print(f"[HIGHER-ORDER triangle_min] AUROC={tmin[0]:.3f} (real {tmin[1]:.3f}/null {tmin[2]:.3f})   [escape ref 0.978]", flush=True)
    print(f"[HIGHER-ORDER H0_barcode ] AUROC={h0[0]:.3f} (real {h0[1]:.3f}/null {h0[2]:.3f})   [escape ref 0.983]", flush=True)
    print(f"[PAIRWISE      spectrum  ] AUROC={auc_pair:.3f} (real {np.mean(rdp):.4f}/null {np.mean(ndp):.4f})   [escape ref 1.000]", flush=True)

    ho_best = max(tmin[0], h0[0])
    ho_chance = ho_best <= 0.65
    pair_collapsed = auc_pair <= 0.65
    print(f"\n=== VERDICT ===", flush=True)
    print(f"  HIGHER-ORDER best={ho_best:.3f} -> {'CHANCE (escape rode the STRENGTH profile, NOT topology)' if ho_chance else 'still separates (shared-realization channel?)'}", flush=True)
    print(f"  PAIRWISE={auc_pair:.3f} -> {'COLLAPSED (spectrum read STRENGTHS, not topology)' if pair_collapsed else 'HELD (spectrum reads pairwise TOPOLOGY -- stronger)'}", flush=True)

    out = {"mode": mode, "T": T, "iso_ok": iso_ok, "assign_varies": assign_varies,
           "ho_triangle_min_AUROC": tmin[0], "ho_h0_barcode_AUROC": h0[0], "pairwise_spectrum_AUROC": auc_pair,
           "ho_best": ho_best, "ho_chance": ho_chance, "pair_collapsed": pair_collapsed,
           "q_fixed": Q_FIXED.tolist(), "r_fixed": R_FIXED.tolist()}
    json.dump(out, open(f"data/dcal2c_control_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal2c_control_{mode}.json", flush=True)
    return out


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "run"
    (realbreak_main if m.startswith("realbreak") else main)(m)
