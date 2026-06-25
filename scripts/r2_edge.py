#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 1 -- R2-EDGE premise (pre-registered 2026-06-25, pre_registration.md).
Convergence of TWO genuinely-distinct DENSE edge estimators (NO sparse/DCA):
  K_MI   = APC-corrected MIp (statistical / Shannon plug-in)        -- REUSED from the saved .npz.
  K_comp = MDL/compression edge coupling (algorithmic): per pair (i,j), the description-length
           SAVING of coding the JOINT pair-symbol vs coding i,j INDEPENDENTLY, via the KT
           (Krichevsky-Trofimov / Dirichlet-1/2) stochastic-complexity codelength on the
           deterministically-RECOMPUTED 80%-id reweighted effective counts. Marginal-relative
           (joint-vs-independent = the marginal baseline); the KT complexity penalty on the
           441-symbol joint vs 21-symbol marginals is what makes it ALGORITHMICALLY distinct from
           the plug-in MI. numpy + math.lgamma only. NO MIp recompute.

Reuses run_d2_family2's locked method (reweight / conservation / map_pdb / contacts / rank / spear)
so nothing about the substrate pipeline changes. Outputs -> data/pfam/ (gitignored). NOT committed.
DCA / inverse-covariance EXCLUDED as the Pearlian cut the corpus critiques (see pre-reg).
"""
import sys, math, json, numpy as np
sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, conservation, map_pdb, contacts, rank, spear, PF, STATES

SEP = 5; LONG = 12
LGAMMA = np.vectorize(math.lgamma)
HALF = math.lgamma(0.5)

def kt_codelen(counts):
    """KT stochastic-complexity codelength (bits) of a multinomial with effective counts."""
    counts = np.asarray(counts, float); N = counts.sum(); A = len(counts)
    logP = float((LGAMMA(counts + 0.5) - HALF).sum()) - (math.lgamma(N + A * 0.5) - math.lgamma(A * 0.5))
    return -logP / math.log(2.0)

def k_comp_matrix(M, weights):
    N, L = M.shape; w = weights.astype(float)
    cnt = np.zeros((L, STATES))
    for a in range(STATES):
        cnt[:, a] = (w[:, None] * (M == a)).sum(0)
    Lmarg = np.array([kt_codelen(cnt[i]) for i in range(L)])
    K = np.zeros((L, L))
    js_all = M.astype(np.int64) * STATES  # for joint index
    for i in range(L):
        ci = js_all[:, i]
        for j in range(i + 1, L):
            jc = np.bincount(ci + M[:, j], weights=w, minlength=STATES * STATES)
            K[i, j] = K[j, i] = Lmarg[i] + Lmarg[j] - kt_codelen(jc)
    return K

def partial_multi(x, y, Zs):
    """Spearman partial corr of x,y controlling for covariates in Zs (precision-matrix form)."""
    rows = [rank(np.asarray(x, float)), rank(np.asarray(y, float))] + [rank(np.asarray(z, float)) for z in Zs]
    R = np.corrcoef(np.vstack(rows)); P = np.linalg.pinv(R)
    return float(-P[0, 1] / math.sqrt(P[0, 0] * P[1, 1]))

def eligible_pairs(idxs, sep):
    out = []
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            i, j = idxs[a], idxs[b]
            if abs(i - j) >= sep: out.append((i, j))
    return out

def run(acc, pdb, chain):
    print(f"\n===== R2-EDGE {acc} ({pdb}:{chain}) =====", flush=True)
    M = np.load(f"{PF}/pilotS_{acc}_matrix.npy"); N, L = M.shape
    d = np.load(f"{PF}/pilot_coupling_{acc}.npz"); K_MI = d["MIp"]            # REUSED, no recompute
    cons = conservation(M)                                                   # cheap, deterministic
    w, Meff = reweight(M)                                                    # locked reweight, not MIp
    print(f"L={L} N={N} Meff={Meff:.1f}; computing K_comp (KT MDL edge coupling)...", flush=True)
    K_comp = k_comp_matrix(M, w)
    col2pdb, coords, chid, bur = map_pdb(M, pdb, chain)
    mapped, cpair, cdeg = contacts(col2pdb, coords, L)

    # (c)(i) Spearman over ALL eligible pairs + long-range
    allp = eligible_pairs(list(range(L)), SEP)
    longp = [(i, j) for (i, j) in allp if abs(i - j) >= LONG]
    mi_all = np.array([K_MI[i, j] for (i, j) in allp]); cp_all = np.array([K_comp[i, j] for (i, j) in allp])
    mi_lng = np.array([K_MI[i, j] for (i, j) in longp]); cp_lng = np.array([K_comp[i, j] for (i, j) in longp])
    sp_all = spear(mi_all, cp_all); sp_lng = spear(mi_lng, cp_lng)
    print(f"(i)  Spearman(K_MI,K_comp): all |i-j|>=5 = {sp_all:+.3f} ({len(allp)} pairs) | long |i-j|>=12 = {sp_lng:+.3f} ({len(longp)})", flush=True)

    # (ii)(iii) top-L over MAPPED eligible pairs; consensus contact precision
    mp = eligible_pairs(mapped, SEP); Ltop = len(mapped)
    top_mi = set(sorted(mp, key=lambda p: -K_MI[p])[:Ltop])
    top_cp = set(sorted(mp, key=lambda p: -K_comp[p])[:Ltop])
    consensus = top_mi & top_cp
    jac = len(consensus) / len(top_mi | top_cp) if (top_mi | top_cp) else float("nan")
    def prec(S): return np.mean([1.0 if p in cpair else 0.0 for p in S]) if S else float("nan")
    p_mi, p_cp, p_cons = prec(top_mi), prec(top_cp), prec(consensus)
    base = len(cpair) / len(mp) if mp else float("nan")
    print(f"(ii) top-L Jaccard = {jac:.3f} (|consensus|={len(consensus)} of L={Ltop})", flush=True)
    print(f"(iii) contact precision: K_MI-topL={p_mi:.3f}  K_comp-topL={p_cp:.3f}  CONSENSUS={p_cons:.3f}  (base={base:.3f})", flush=True)

    # (iv) confound control over mapped eligible pairs with burial+conservation defined
    burdef = [c for c in mapped if np.isfinite(bur[c])]
    mpb = eligible_pairs(burdef, SEP); mpb_long = [(i, j) for (i, j) in mpb if abs(i - j) >= LONG]
    def arrs(P):
        return (np.array([K_MI[i, j] for (i, j) in P]), np.array([K_comp[i, j] for (i, j) in P]),
                np.array([cons[i] * cons[j] for (i, j) in P]), np.array([bur[i] * bur[j] for (i, j) in P]))
    mi_b, cp_b, consp, burp = arrs(mpb)
    raw_b = spear(mi_b, cp_b); par_b = partial_multi(mi_b, cp_b, [consp, burp])
    mi_bl, cp_bl, conspl, burpl = arrs(mpb_long)
    raw_bl = spear(mi_bl, cp_bl); par_bl = partial_multi(mi_bl, cp_bl, [conspl, burpl])
    print(f"(iv) mapped+burial pairs: raw Spearman={raw_b:+.3f} partial(|cons-prod,burial-prod)={par_b:+.3f}  | "
          f"long-range raw={raw_bl:+.3f} partial={par_bl:+.3f}", flush=True)

    # PASS (per family): long-range Spearman>=0.5 AND consensus precision>=each alone AND survives control
    c1 = sp_lng >= 0.5
    c2 = (p_cons >= p_mi) and (p_cons >= p_cp)
    c3 = (par_b > 0) or (sp_lng >= 0.5)   # survives partial OR long-range holds (pre-reg (d))
    res = {"acc": acc, "L": L, "Meff": Meff, "spear_all": sp_all, "spear_long": sp_lng,
           "jaccard": jac, "prec_mi": p_mi, "prec_comp": p_cp, "prec_consensus": p_cons, "base": base,
           "iv_raw": raw_b, "iv_partial": par_b, "iv_long_raw": raw_bl, "iv_long_partial": par_bl,
           "c1_long_spear_ge_0.5": bool(c1), "c2_consensus_precision": bool(c2),
           "c3_survives_control": bool(c3), "R2_EDGE_PASS_family": bool(c1 and c2 and c3)}
    print(f"PASS(family): c1(long>=0.5)={c1} c2(consensus>=each)={c2} c3(survives)={c3} -> {res['R2_EDGE_PASS_family']}", flush=True)
    json.dump(res, open(f"{PF}/r2_edge_{acc}.json", "w"), indent=2, default=float)
    np.savez(f"{PF}/r2_edge_{acc}.npz", K_comp=K_comp, mapped=np.array(mapped))
    return res

if __name__ == "__main__":
    rs = [run("PF13354", "1djc", "A"), run("PF00026", "4y9w", "A")]
    both = all(r["R2_EDGE_PASS_family"] for r in rs)
    print(f"\n===== R2-EDGE VERDICT = {'PASS' if both else 'FAIL'} (keys on BOTH families) =====")
    json.dump({"families": rs, "R2_EDGE_PASS_both": bool(both)}, open(f"{PF}/r2_edge_verdict.json", "w"), indent=2, default=float)
    print(f"saved {PF}/r2_edge_verdict.json")
