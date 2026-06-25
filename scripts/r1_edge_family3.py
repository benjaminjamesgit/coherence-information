#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 5 PHASE 2 -- clean-tree THIRD-family R1-EDGE replication (PF00348),
with the UPGRADED statistics pre-registered in pre_registration.md (2026-06-25 step-5):
  - persistence = cross-subclade median raw MI (K=8 cut of iq_PF00348.treefile, canonical MI);
  - PARTIAL via the SEPARATED control (conservation_i, conservation_j, burial_i, burial_j -- distinct);
  - POSITION-BLOCK bootstrap CI (resample positions; pair multiplicity cnt_i*cnt_j; B=1000, seed 0);
  - conservation-orthogonality Spearman(w, cons-product); context Spearman(whole-set MIp, persistence);
  - conservation-PRODUCT null-w under BOTH the product and the separated control (leak confirmation).
Reuses the persistence machinery from r1_edge.py + the pinned pipeline (mip_matrix, k_comp_matrix,
reweight, conservation, map_pdb). Raw MI strictly via canonical cit/information.py; numpy + math.lgamma.
PF00348 MIp/K_comp are this family's OWN whole-set estimators (computed here, not the locked pilots).
Outputs -> data/pfam/ (gitignored). NOT committed (Phase-1-only commit discipline).
"""
import sys, math, json
from collections import defaultdict
import numpy as np

sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, conservation, map_pdb, mip_matrix, PF, SEP, LONG, spear
from r2_edge import k_comp_matrix, eligible_pairs
from r1_edge import cut_into_subclades, raw_mi_on_E, induced_w

B = 1000
BOOT_SEED = 0


def fast_rank(a):
    """Average ranks (ties averaged), vectorized -- O(n log n)."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    sa = a[order]
    pos = np.arange(len(a), dtype=float)
    diff = np.r_[True, sa[1:] != sa[:-1]]
    grp = np.cumsum(diff) - 1
    mean_rank = (np.bincount(grp, weights=pos) / np.bincount(grp))[grp]
    out = np.empty(len(a), float)
    out[order] = mean_rank
    return out


def partial_sep(x, y, covs):
    """Spearman partial corr of x,y controlling covs, via OLS-residual regression on ranks (fast_rank).
    Robust to collinear covariates -- the prior pinv form returned garbage when a cov is collinear
    with x (the step-5 +0.903 cons-product-null artifact, diagnosed step 6); residualizing on ranks
    partials correctly. Identical to pinv for well-conditioned controls (the load-bearing cells)."""
    rx = fast_rank(x); ry = fast_rank(y)
    Z = np.column_stack([np.ones(len(rx))] + [fast_rank(c) for c in covs])
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    if ex.std() == 0 or ey.std() == 0:
        return float("nan")
    return float(np.corrcoef(ex, ey)[0, 1])


def posblock_ci(x, y, covs, ipos, jpos, L, B=B, seed=BOOT_SEED):
    """Position-block bootstrap: resample L positions; pair multiplicity cnt_i*cnt_j; 95% CI of partial."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        cnt = np.bincount(rng.integers(0, L, L), minlength=L)
        m = cnt[ipos] * cnt[jpos]
        sel = m > 0
        if sel.sum() < 10:
            continue
        idx = np.repeat(np.where(sel)[0], m[sel])
        vals.append(partial_sep(x[idx], y[idx], [c[idx] for c in covs]))
    v = np.array(vals)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def run(acc="PF00348", pdb="8a7c", chain="A"):
    print(f"\n===== R1-EDGE (third family) {acc} ({pdb}:{chain}) =====", flush=True)
    M = np.load(f"{PF}/pilotS_{acc}_matrix.npy")
    N, L = M.shape
    w_seq, Meff = reweight(M)
    print(f"L={L} N={N} Meff={Meff:.1f}; building whole-set APC-MIp + KT/MDL K_comp ...", flush=True)
    MIp = mip_matrix(M, w_seq)
    K_comp = k_comp_matrix(M, w_seq)
    cons = conservation(M)
    _, _, _, bur = map_pdb(M, pdb, chain)
    ndef = int(np.isfinite(bur).sum())
    print(f"burial mapped {ndef}/{L}; computing persistence (K=8 subclade median raw MI) ...", flush=True)

    E = eligible_pairs(list(range(L)), SEP)
    ii = np.array([e[0] for e in E]); jj = np.array([e[1] for e in E])
    byi = defaultdict(list)
    for k, (i, j) in enumerate(E):
        byi[i].append((j, k))
    subs, sizes = cut_into_subclades(acc, M)
    print(f"K_eff={len(subs)} subclades sizes={sizes}", flush=True)
    mats = [raw_mi_on_E(M[rows], E, byi) for rows in subs]
    persistence = np.median(np.vstack(mats), axis=0)

    longmask = (jj - ii) >= LONG
    ci = cons[ii]; cj = cons[jj]; bi = bur[ii]; bj = bur[jj]
    consprod = ci * cj; burp = bi * bj
    cdef = np.isfinite(bi) & np.isfinite(bj)             # burial-defined mapped subset
    SEPcovs = [ci, cj, bi, bj]
    PRODcovs = [consprod, burp]

    w_mi = induced_w(MIp[ii, jj])
    w_cp = induced_w(K_comp[ii, jj])
    w_null = induced_w(consprod)                          # conservation-product null-w (zero coupling info)

    def cell(w, label):
        sp_all = spear(w, persistence); sp_long = spear(w[longmask], persistence[longmask])
        ortho = spear(w, consprod)
        out = {"estimator": label, "spear_all": sp_all, "spear_long": sp_long, "ortho_cons": ortho}
        for tag, mask in (("all", cdef), ("long", cdef & longmask)):
            idx = np.where(mask)[0]
            sep = partial_sep(w[idx], persistence[idx], [c[idx] for c in SEPcovs])
            prod = partial_sep(w[idx], persistence[idx], [c[idx] for c in PRODcovs])
            out[f"sep_{tag}"] = sep; out[f"prod_{tag}"] = prod; out[f"n_{tag}"] = int(len(idx))
        lo, hi = posblock_ci(w[cdef & longmask], persistence[cdef & longmask],
                             [c[cdef & longmask] for c in SEPcovs], ii[cdef & longmask], jj[cdef & longmask], L)
        out["sep_long_posblock_ci"] = [lo, hi]
        out["PASS"] = bool(out["sep_long"] > 0 and lo > 0)
        print(f"  {label}: Spearman all={sp_all:+.3f} long={sp_long:+.3f} | ortho(w,cons-prod)={ortho:+.3f}\n"
              f"      separated partial all={out['sep_all']:+.3f} long={out['sep_long']:+.3f} "
              f"posblock-CI[{lo:+.3f},{hi:+.3f}]  (product partial long={out['prod_long']:+.3f}) -> "
              f"{'PASS' if out['PASS'] else 'FAIL'}", flush=True)
        return out

    s_mi = cell(w_mi, "K_MI")
    s_cp = cell(w_cp, "K_comp")

    # context + conservation-null leak confirmation
    ctx_all = spear(MIp[ii, jj], persistence); ctx_long = spear(MIp[ii, jj][longmask], persistence[longmask])
    nl = cdef & longmask; nidx = np.where(nl)[0]
    null_sep = partial_sep(w_null[nidx], persistence[nidx], [c[nidx] for c in SEPcovs])
    null_prod = partial_sep(w_null[nidx], persistence[nidx], [c[nidx] for c in PRODcovs])
    print(f"  CONTEXT Spearman(whole-set MIp, persistence): all={ctx_all:+.3f} long={ctx_long:+.3f}", flush=True)
    print(f"  CONS-PRODUCT NULL-w (long): product-control partial={null_prod:+.3f} (leak) vs "
          f"separated-control partial={null_sep:+.3f} (caught)", flush=True)

    gen = s_mi["PASS"] and s_cp["PASS"]
    print(f"  R1-EDGE GENERALIZES on {acc}: K_MI {'PASS' if s_mi['PASS'] else 'FAIL'} "
          f"(load-bearing) + K_comp {'PASS' if s_cp['PASS'] else 'FAIL'} (corroborating) -> "
          f"{'YES' if gen else 'NO'}", flush=True)

    res = {"acc": acc, "pdb": pdb, "chain": chain, "L": L, "N": N, "Meff": Meff,
           "burial_mapped": ndef, "K_eff": len(subs), "clade_sizes": sizes,
           "K_MI": s_mi, "K_comp": s_cp, "ctx_MIp_persist_all": ctx_all, "ctx_MIp_persist_long": ctx_long,
           "null_prod_long": null_prod, "null_sep_long": null_sep, "GENERALIZES": gen}
    json.dump(res, open(f"{PF}/r1_edge_family3_{acc}.json", "w"), indent=2, default=float)
    np.savez(f"{PF}/r1_edge_family3_{acc}.npz", persistence=persistence, w_mi=w_mi, w_cp=w_cp,
             MIp=MIp, K_comp=K_comp, ii=ii, jj=jj, cons=cons, bur=bur)
    print(f"saved {PF}/r1_edge_family3_{acc}.json", flush=True)
    return res


if __name__ == "__main__":
    run()
