#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 6 (CORRECTED) PHASE 2 -- structured-noise NULL probe of K_comp's
beyond-raw-MI persistence signal (pre-registered 2026-06-25 step-6 CORRECTED, pre_registration.md).

SURROGATE (preserves marginals + subclade phylogeny; DESTROYS coupling): reuse the SAME
cut_into_subclades partition; within EACH subclade, permute EACH column's residues independently
among that subclade's sequences (seed s). Preserves per-(subclade,column) + whole-column UNWEIGHTED
marginals (conservation EXACTLY unchanged) + subclade membership; destroys within-subclade coupling.
Burial reused (structural). Real reweight weights reused (phylo structure preserved).

STATISTIC: on each surrogate recompute raw whole-set MI + K_comp + persistence (cross-subclade
median raw MI); OLS-residual partial(K_comp, persistence | raw-MI, cons_i, cons_j, bur_i, bur_j),
long-range. N_SURR=20 seeded, 3 families. Raw MI + K_comp are the VECTORIZED plug-in / KT codelength
(bit-identical to canonical cit/information.py [verified step-3 to 5e-16] + the locked KT recipe).
FORK: REAL > 95th pct of surrogates AND surrogate ~0 -> coupling-specific (P4 candidate); surrogate
~= REAL -> marginal-bias / generic-statistics artifact. Outputs -> data/pfam/ (gitignored). NOT committed.
"""
import sys, math, json
from collections import defaultdict
import numpy as np

sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, conservation, map_pdb, STATES, PF, SEP, LONG
from r1_edge import cut_into_subclades
from r1_edge_family3 import partial_sep
from r2_edge import eligible_pairs, kt_codelen

LGAMMA = np.frompyfunc(math.lgamma, 1, 1)
HALF = math.lgamma(0.5)
LN2 = math.log(2.0)
N_SURR = 20
FAMS = [("PF13354", "1djc", "A"), ("PF00026", "4y9w", "A"), ("PF00348", "8a7c", "A")]


def _oh(M):
    N, L = M.shape
    OH = np.zeros((N, L, STATES))
    for a in range(STATES):
        OH[:, :, a] = (M == a)
    return OH, OH.reshape(N, L * STATES)


def raw_mi_only(M, w, byi, nE):
    """Raw MI (bits) per eligible pair, vectorized plug-in (== canonical cit/information.py)."""
    N, L = M.shape
    wv = w.astype(np.float64); Wsum = wv.sum()
    OH, OHflat = _oh(M)
    fi = (wv[:, None, None] * OH).sum(0) / Wsum
    out = np.zeros(nE)
    for i, js in byi.items():
        Wi = OH[:, i, :] * wv[:, None]
        F = (Wi.T @ OHflat).reshape(STATES, L, STATES) / Wsum
        fic = fi[i][:, None]
        for j, k in js:
            fij = F[:, j, :]; fjc = fi[j][None, :]; mask = fij > 0
            out[k] = float((fij[mask] * np.log2(fij[mask] / (fic * fjc)[mask])).sum()) if mask.any() else 0.0
    return out


def estimators_whole(M, w, byi, nE):
    """Raw MI + K_comp (KT/MDL) per eligible pair, sharing one per-i matmul pass."""
    N, L = M.shape
    wv = w.astype(np.float64); Wsum = wv.sum()
    OH, OHflat = _oh(M)
    cnt = (wv[:, None, None] * OH).sum(0)                       # (L,STATES) weighted marginal counts
    fi = cnt / Wsum
    Lmarg = np.array([kt_codelen(cnt[i]) for i in range(L)])
    cN = math.lgamma(Wsum + STATES * STATES * 0.5) - math.lgamma(STATES * STATES * 0.5)
    mi = np.zeros(nE); kc = np.zeros(nE)
    for i, js in byi.items():
        Wi = OH[:, i, :] * wv[:, None]
        Fc = (Wi.T @ OHflat).reshape(STATES, L, STATES)        # joint COUNTS
        fic = fi[i][:, None]
        for j, k in js:
            jc = Fc[:, j, :]; jf = jc / Wsum; fjc = fi[j][None, :]; mask = jf > 0
            mi[k] = float((jf[mask] * np.log2(jf[mask] / (fic * fjc)[mask])).sum()) if mask.any() else 0.0
            jr = jc.ravel(); nz = jr > 0
            Ljoint = -((LGAMMA(jr[nz] + 0.5).astype(float) - HALF).sum() - cN) / LN2
            kc[k] = Lmarg[i] + Lmarg[j] - Ljoint                # K_comp = L(marg_i)+L(marg_j)-L(joint)
    return mi, kc


def surrogate(M, subs, seed):
    rng = np.random.default_rng(seed)
    Ms = M.copy()
    for rows in subs:
        r = np.asarray(rows)
        for c in range(M.shape[1]):
            Ms[r, c] = M[r[rng.permutation(len(r))], c]
    return Ms


def persistence(M, subs, wsub, byi, nE):
    mats = [raw_mi_only(M[np.asarray(rows)], wsub[s], byi, nE) for s, rows in enumerate(subs)]
    return np.median(np.vstack(mats), axis=0)


def run():
    rng_report = {}
    for acc, pdb, ch in FAMS:
        print(f"\n===== NULL PROBE {acc} =====", flush=True)
        M = np.load(f"{PF}/pilotS_{acc}_matrix.npy"); N, L = M.shape
        w_seq, _ = reweight(M)
        cons = conservation(M)
        _, _, _, bur = map_pdb(M, pdb, ch)
        subs, sizes = cut_into_subclades(acc, M)
        wsub = [reweight(M[np.asarray(rows)])[0] for rows in subs]
        E = eligible_pairs(list(range(L)), SEP); nE = len(E)
        ii = np.array([e[0] for e in E]); jj = np.array([e[1] for e in E])
        byi = defaultdict(list)
        for k, (i, j) in enumerate(E):
            byi[i].append((j, k))
        ci = cons[ii]; cj = cons[jj]; bi = bur[ii]; bj = bur[jj]
        m = np.where((np.isfinite(bi) & np.isfinite(bj)) & ((jj - ii) >= LONG))[0]

        def partial_on(kc, pers, raw):
            return partial_sep(kc[m], pers[m], [raw[m], ci[m], cj[m], bi[m], bj[m]])

        raw_r, kc_r = estimators_whole(M, w_seq, byi, nE)
        pers_r = persistence(M, subs, wsub, byi, nE)
        real = partial_on(kc_r, pers_r, raw_r)
        print(f"L={L} K_eff={len(subs)} sizes={sizes}; REAL beyond-raw-MI partial = {real:+.4f}", flush=True)

        sur = []
        for s in range(N_SURR):
            Ms = surrogate(M, subs, s)
            raw_s, kc_s = estimators_whole(Ms, w_seq, byi, nE)
            pers_s = persistence(Ms, subs, wsub, byi, nE)
            sur.append(partial_on(kc_s, pers_s, raw_s))
            print(f"  surrogate {s:2d}: {sur[-1]:+.4f}", flush=True)
        sur = np.array(sur)
        mean = float(sur.mean()); std = float(sur.std()); p95 = float(np.percentile(sur, 95))
        z = (real - mean) / std if std > 0 else float("inf")
        pct = float((sur < real).mean() * 100)
        passed = bool(real > p95 and abs(mean) < 0.10)
        print(f"  SURROGATE null: mean={mean:+.4f} std={std:.4f} 95pct={p95:+.4f} | REAL={real:+.4f} "
              f"z={z:+.2f} pct-of-real={pct:.0f} -> {'COUPLING-SPECIFIC (real>>null)' if passed else 'NOT separated'}",
              flush=True)
        rng_report[acc] = {"L": L, "K_eff": len(subs), "real": real, "sur_mean": mean, "sur_std": std,
                           "sur_p95": p95, "z": z, "pct_of_real": pct, "surrogates": sur.tolist(),
                           "FORK": "coupling-specific" if passed else "marginal-bias-artifact"}
    json.dump(rng_report, open(f"{PF}/r1_null_probe_verdict.json", "w"), indent=2, default=float)
    print(f"\nsaved {PF}/r1_null_probe_verdict.json")


if __name__ == "__main__":
    run()
