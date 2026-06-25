#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 4 PHASE 2 -- R1-EDGE: does estimator-induced edge-w predict
PHYLOGENY-CORRECTED coupling PERSISTENCE? (pre-registered 2026-06-25, pre_registration.md.)

PERSISTENCE (phylo-decorrelated): cut the fixed tree iq_{acc}.treefile into K=8 phylogenetically-
INDEPENDENT subclades (greedy top-down, midpoint-rooted); within each subclade reweight (80%-id,
within-clade, the locked reweight) and compute RAW MI per eligible pair via CANONICAL
cit/information.py; persistence(i,j) = MEDIAN across subclades. Edge-w is induced from WHOLE-SET
APC-MIp / K_comp (phylo-confounded); persistence is cross-independent-subclade (phylo-decorrelated)
-- they differ exactly on the phylo confound, so high-w AND persistent = real constraint.

STATISTIC (R1 spec guard = PER-ESTIMATOR validity): for each of K_MI- and K_comp-induced w,
Spearman(w, persistence) + the partial controlling conservation-product AND burial-product
(precision-matrix, as R2-edge); bootstrap CI resampling pairs (B=1000, seed 0). PASS iff the
LONG-RANGE partial > 0 with 95% CI excluding 0. Context = Spearman(whole-set MIp, persistence).

Reuse saved matrices + saved MIp/K_comp + the fixed trees; numpy + math.lgamma only; no MIp/K_comp
recompute. Outputs -> data/pfam/ (gitignored). NOT committed (Phase 1 docs/pre-reg only).
"""
import sys, math, json, re
from collections import defaultdict
import numpy as np
from Bio import Phylo

sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, conservation, map_pdb, STATES, PF, SEP, LONG, spear
from r2_edge import partial_multi, eligible_pairs
from cit.information import coherence_weighted_mutual_information as cwmi

BETA = 4.0
K = 8                  # number of phylogenetically-independent subclades (pinned)
MIN_CLADE = 25         # merge subclades smaller than this (pinned)
B = 1000               # bootstrap resamples (pinned)
BOOT_SEED = 0
ONES21 = np.ones(STATES)


def sigma(x):
    return 1.0 / (1.0 + np.exp(-x))


def leaf_row(name):
    return int(re.sub(r"^[A-Za-z]+", "", name))


def cut_into_subclades(acc, M):
    """Greedy top-down K-partition of the midpoint-rooted iq tree; merge subclades < MIN_CLADE rows
    into the nearest (tree-distance) remaining subclade. Returns list of row-index arrays + sizes."""
    tree = Phylo.read(f"{PF}/iq_{acc}.treefile", "newick")
    tree.root_at_midpoint()
    groups = [tree.root]
    while len(groups) < K:
        cand = [g for g in groups if len(g.clades) >= 2]
        if not cand:
            break
        cand.sort(key=lambda g: (-len(g.get_terminals()),
                                 min(leaf_row(t.name) for t in g.get_terminals())))
        g = cand[0]
        groups.remove(g)
        groups.extend(g.clades)
    rows = [sorted(leaf_row(t.name) for t in g.get_terminals()) for g in groups]
    # merge tiny subclades into the nearest by tree distance
    keep_g, keep_rows = [], []
    small = [(g, r) for g, r in zip(groups, rows) if len(r) < MIN_CLADE]
    big = [(g, r) for g, r in zip(groups, rows) if len(r) >= MIN_CLADE]
    keep_g = [g for g, _ in big]
    keep_rows = [list(r) for _, r in big]
    for gs, rs in small:
        dists = [tree.distance(gs, gb) for gb in keep_g]
        t = int(np.argmin(dists))
        keep_rows[t] = sorted(keep_rows[t] + rs)
    sizes = [len(r) for r in keep_rows]
    return [np.array(r) for r in keep_rows], sizes


def raw_mi_on_E(Msub, E, byi):
    """RAW MI (bits) per eligible pair via CANONICAL cwmi(joint, ones21); within-clade reweight."""
    N, L = Msub.shape
    w, _ = reweight(Msub)
    wv = w.astype(np.float64)
    Wsum = wv.sum()
    OH = np.zeros((N, L, STATES))
    for a in range(STATES):
        OH[:, :, a] = (Msub == a)
    OHflat = OH.reshape(N, L * STATES)
    out = np.zeros(len(E))
    for i, js in byi.items():
        Wi = OH[:, i, :] * wv[:, None]
        F = (Wi.T @ OHflat).reshape(STATES, L, STATES) / Wsum   # F[a,j,b] = p(X_i=a, X_j=b)
        for j, k in js:
            out[k] = cwmi(F[:, j, :], ONES21, base=2.0)
    return out


def induced_w(rho):
    z = (rho - rho.mean()) / rho.std()
    return sigma(BETA * z)


def boot_partial_ci(x, y, Zs, idx_pool, rng):
    vals = []
    n = len(idx_pool)
    for _ in range(B):
        s = rng.integers(0, n, n)
        sub = idx_pool[s]
        vals.append(partial_multi(x[sub], y[sub], [z[sub] for z in Zs]))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def run(acc, pdb, chain):
    print(f"\n===== R1-EDGE {acc} ({pdb}:{chain}) =====", flush=True)
    M = np.load(f"{PF}/pilotS_{acc}_matrix.npy")
    N, L = M.shape
    K_MI = np.load(f"{PF}/pilot_coupling_{acc}.npz")["MIp"]         # whole-set APC-MIp, REUSED
    K_comp = np.load(f"{PF}/r2_edge_{acc}.npz")["K_comp"]           # whole-set K_comp, REUSED
    cons = conservation(M)
    _, _, _, bur = map_pdb(M, pdb, chain)

    E = eligible_pairs(list(range(L)), SEP)
    nE = len(E)
    byi = defaultdict(list)
    for k, (i, j) in enumerate(E):
        byi[i].append((j, k))
    ii = np.array([e[0] for e in E])
    jj = np.array([e[1] for e in E])
    longmask = (jj - ii) >= LONG

    # ---- persistence = median over K phylo-independent subclades of within-clade raw MI ----
    subs, sizes = cut_into_subclades(acc, M)
    print(f"L={L} N={N}; K_eff={len(subs)} subclades sizes={sizes}", flush=True)
    mats = []
    for s, rows in enumerate(subs):
        mi = raw_mi_on_E(M[rows], E, byi)
        mats.append(mi)
        print(f"  subclade {s} (n={len(rows)}) raw-MI done", flush=True)
    stack = np.vstack(mats)
    persistence = np.median(stack, axis=0)
    persist_var = np.var(stack, axis=0)

    # ---- induced edge-w from whole-set estimators ----
    w_mi = induced_w(np.array([K_MI[i, j] for (i, j) in E]))
    w_cp = induced_w(np.array([K_comp[i, j] for (i, j) in E]))

    # ---- confound subset: mapped eligible pairs with conservation-prod + burial-prod defined ----
    burdef = np.isfinite(bur)
    consp = np.array([cons[i] * cons[j] for (i, j) in E])
    burp = np.array([bur[i] * bur[j] for (i, j) in E])
    cdef = burdef[ii] & burdef[jj]                                  # burial defined both ends
    rng = np.random.default_rng(BOOT_SEED)

    def stats_for(wv, label):
        sp_all = spear(wv, persistence)
        sp_long = spear(wv[longmask], persistence[longmask])
        out = {"estimator": label, "spear_all": sp_all, "spear_long": sp_long}
        for tag, mask in (("all", cdef), ("long", cdef & longmask)):
            idx = np.where(mask)[0]
            x, y = wv[idx], persistence[idx]
            Zs = [consp[idx], burp[idx]]
            par = partial_multi(x, y, Zs)
            lo, hi = boot_partial_ci(wv, persistence, [consp, burp], idx, rng)
            out[f"partial_{tag}"] = par
            out[f"partial_{tag}_ci"] = [lo, hi]
            out[f"n_{tag}"] = int(len(idx))
        out["PASS"] = bool(out["partial_long"] > 0 and out["partial_long_ci"][0] > 0)
        print(f"  {label}: Spearman all={sp_all:+.3f} long={sp_long:+.3f} | "
              f"partial(all|cons,bur)={out['partial_all']:+.3f} CI[{out['partial_all_ci'][0]:+.3f},{out['partial_all_ci'][1]:+.3f}] "
              f"| partial(long)={out['partial_long']:+.3f} CI[{out['partial_long_ci'][0]:+.3f},{out['partial_long_ci'][1]:+.3f}] "
              f"-> {'PASS' if out['PASS'] else 'FAIL'}", flush=True)
        return out

    s_mi = stats_for(w_mi, "K_MI")
    s_cp = stats_for(w_cp, "K_comp")

    # ---- context: does the phylo correction bite? whole-set MIp vs persistence ----
    miw = np.array([K_MI[i, j] for (i, j) in E])
    ctx_all = spear(miw, persistence)
    ctx_long = spear(miw[longmask], persistence[longmask])
    print(f"  CONTEXT Spearman(whole-set MIp, persistence): all={ctx_all:+.3f} long={ctx_long:+.3f} "
          f"(lower => phylo correction bites more)", flush=True)

    res = {"acc": acc, "L": L, "N": N, "nE": nE, "K_eff": len(subs), "clade_sizes": sizes,
           "K_MI": s_mi, "K_comp": s_cp, "ctx_MIp_persist_all": ctx_all, "ctx_MIp_persist_long": ctx_long,
           "persist_var_median": float(np.median(persist_var))}
    json.dump(res, open(f"{PF}/r1_edge_{acc}.json", "w"), indent=2, default=float)
    np.savez(f"{PF}/r1_edge_{acc}.npz", persistence=persistence, persist_var=persist_var,
             w_mi=w_mi, w_cp=w_cp, ii=ii, jj=jj)
    return res


if __name__ == "__main__":
    rs = [run("PF13354", "1djc", "A"), run("PF00026", "4y9w", "A")]
    print("\n===== R1-EDGE SUMMARY (per-estimator, per-family) =====")
    for r in rs:
        print(f"{r['acc']}: K_MI {'PASS' if r['K_MI']['PASS'] else 'FAIL'} "
              f"(long partial {r['K_MI']['partial_long']:+.3f} CI{r['K_MI']['partial_long_ci']}) | "
              f"K_comp {'PASS' if r['K_comp']['PASS'] else 'FAIL'} "
              f"(long partial {r['K_comp']['partial_long']:+.3f} CI{r['K_comp']['partial_long_ci']})")
    json.dump({"families": rs}, open(f"{PF}/r1_edge_verdict.json", "w"), indent=2, default=float)
    print(f"saved {PF}/r1_edge_verdict.json")
