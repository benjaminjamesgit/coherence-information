#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 2 -- edge-w FORMAL-ADMISSIBILITY check (pre-registered 2026-06-25).

VERIFICATION (pre-fixed criteria, not a hypothesis test) that edge-valued w = CIT per-symbol w on
the JOINT pair-symbol over the 441 product alphabet is an EXTENSION of the H_w/I_w machinery, not a
fork. Checks A-F (see pre_registration.md / design/relational_edge_w.md). numpy + math.lgamma only.
REUSES each family's saved matrix + the saved full-alphabet APC-MIp baseline (pilot_coupling_{acc}.npz);
recomputes the estimator ONLY for the coarse alphabet (C), the relabeled alphabet (E), and the
bootstrap resamples (F). Outputs -> data/pfam/ (gitignored). NOT committed (Phase-2 HARD STOP).

KEY RISK: pair-features OVERLAP (each position in L-1 pairs; the representation is NOT a partition).
"""
import sys, math, json, numpy as np
sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, rank, spear, PF

BETA = 4.0; SEP = 5; STATES = 21; GAP = 20
AA = "ACDEFGHIKLMNPQRSTVWY"
LGAMMA = np.frompyfunc(math.lgamma, 1, 1)
LN2 = math.log(2.0)

# Dayhoff-6 classes (gap = its own 7th class)
DAYHOFF = [set("C"), set("AGPST"), set("DENQ"), set("RHK"), set("ILMV"), set("FWY")]
def dayhoff_map():
    m = np.full(STATES, 6, dtype=np.int64)  # default -> gap-class 6
    for ci, cls in enumerate(DAYHOFF):
        for aa in cls:
            m[AA.index(aa)] = ci
    m[GAP] = 6
    return m  # 21 -> {0..6}

def within_class_relabel():
    """A deterministic permutation of the 21 symbols that is WITHIN-Dayhoff-class (gap fixed)."""
    perm = np.arange(STATES)
    for cls in DAYHOFF:
        idx = sorted(AA.index(a) for a in cls)
        if len(idx) > 1:
            perm[idx] = np.roll(idx, 1)  # cyclic shift within the class
    return perm  # gap (20) maps to itself

def kt_codelen_vec(counts):
    """KT (Dirichlet-1/2) stochastic-complexity codelength (bits). counts: effective counts."""
    counts = np.asarray(counts, float); N = counts.sum(); A = counts.size
    half = math.lgamma(0.5)
    terms = LGAMMA(counts + 0.5).astype(float) - half          # zero-count -> 0
    logP = float(terms.sum()) - (math.lgamma(N + A * 0.5) - math.lgamma(A * 0.5))
    return -logP / LN2

def estimators(M, w, A):
    """Return (MIp, Kcomp) for alphabet size A, sharing one per-i matmul pass. Counts are
    w-reweighted (effective). MIp APC-corrected; Kcomp = L_KT(marg_i)+L_KT(marg_j)-L_KT(joint)."""
    N, L = M.shape; wv = w.astype(np.float64); Wsum = wv.sum()
    OH = np.zeros((N, L, A))
    for a in range(A): OH[:, :, a] = (M == a)
    fi = (wv[:, None, None] * OH).sum(axis=0) / Wsum            # L x A marginal freq
    margcnt = fi * Wsum
    Lmarg = np.array([kt_codelen_vec(margcnt[i]) for i in range(L)])
    OHflat = OH.reshape(N, L * A)
    MI = np.zeros((L, L)); Kc = np.zeros((L, L))
    half = math.lgamma(0.5); cN = math.lgamma(Wsum + A * A * 0.5) - math.lgamma(A * A * 0.5)
    for i in range(L):
        Wi = OH[:, i, :] * wv[:, None]
        Fc = (Wi.T @ OHflat).reshape(A, L, A)                   # weighted joint COUNTS (a,j,b)
        Ff = Fc / Wsum
        fic = fi[i][:, None]
        for j in range(i + 1, L):
            fij = Ff[:, j, :]; fjc = fi[j][None, :]; mask = fij > 0
            MI[i, j] = MI[j, i] = float((fij[mask] * np.log(fij[mask] / (fic * fjc)[mask])).sum()) if mask.any() else 0.0
            jc = Fc[:, j, :].ravel()
            terms = LGAMMA(jc[jc > 0] + 0.5).astype(float) - half
            Ljoint = -(float(terms.sum()) - cN) / LN2
            Kc[i, j] = Kc[j, i] = Lmarg[i] + Lmarg[j] - Ljoint
    iu = np.triu_indices(L, 1); mi_i = MI.sum(axis=1) / (L - 1); mi_all = MI[iu].mean()
    MIp = MI - np.outer(mi_i, mi_i) / mi_all; np.fill_diagonal(MIp, 0.0)
    return MIp, Kc

def eligible(L):
    return [(i, j) for i in range(L) for j in range(i + 1, L) if abs(i - j) >= SEP]

def vec(K, pairs):
    return np.array([K[i, j] for (i, j) in pairs])

def prov_w(cvec):
    z = (cvec - cvec.mean()) / (cvec.std() if cvec.std() > 0 else 1.0)
    return 1.0 / (1.0 + np.exp(-BETA * z))

# ---- check B: Shannon recovery (estimator-independent) ----
def shannon_recovery(M, w, pairs):
    Wsum = w.sum(); worst_H = 0.0; worst_I = 0.0
    for (i, j) in pairs:
        P = np.zeros((STATES, STATES))
        np.add.at(P, (M[:, i], M[:, j]), w); P /= Wsum
        p = P.ravel(); m = p > 0
        H = float(-(p[m] * np.log(p[m])).sum())
        Hw = float((p[m] * np.ones_like(p[m]) * (-np.log(p[m]))).sum())     # w==1 over 441
        pi = P.sum(1); pj = P.sum(0)
        num = P[P > 0]; ii, jj = np.where(P > 0)
        I = float((num * np.log(num / (pi[ii] * pj[jj]))).sum())
        Iw = float((num * np.ones_like(num) * np.log(num / (pi[ii] * pj[jj]))).sum())  # w==1 over X_i
        worst_H = max(worst_H, abs(Hw - H)); worst_I = max(worst_I, abs(Iw - I))
    return worst_H, worst_I

def run_family(acc, do_boot, nboot=100):
    M = np.load(f"{PF}/pilotS_{acc}_matrix.npy"); N, L = M.shape
    K_MI_saved = np.load(f"{PF}/pilot_coupling_{acc}.npz")["MIp"]
    w, Meff = reweight(M)
    pairs = eligible(L); res = {"acc": acc, "L": L, "N": N, "Meff": Meff, "n_pairs": len(pairs)}
    print(f"\n===== ADMISSIBILITY {acc}  L={L} N={N} Meff={Meff:.1f} =====", flush=True)

    # baseline estimators (K_MI = REUSED saved; K_comp computed; full-alphabet recompute is a
    # one-time sanity tie-in only, NOT a baseline replacement)
    MIp_rec, Kc_base = estimators(M, w, STATES)
    sane = spear(vec(K_MI_saved, pairs), vec(MIp_rec, pairs))
    res["sanity_recompute_vs_saved_MIp_spearman"] = sane
    print(f"[sanity] recomputed full MIp vs SAVED MIp Spearman = {sane:.6f} (expect ~1.0)", flush=True)
    base = {"K_MI": K_MI_saved, "K_comp": Kc_base}
    rec_base = {"K_MI": MIp_rec, "K_comp": Kc_base}   # same-code reference for E/F exactness

    # (A) BOUNDEDNESS + (D) MONOTONICITY
    res["A_boundedness"] = {}; res["D_monotonicity"] = {}
    for nm, K in base.items():
        cvec = vec(K, pairs); wv = prov_w(cvec)
        res["A_boundedness"][nm] = {"min": float(wv.min()), "max": float(wv.max()),
                                    "PASS": bool(wv.min() >= 0.0 and wv.max() <= 1.0)}
        sp = spear(cvec, wv); inv = int(round((1 - sp) * len(cvec)))  # rank inversions proxy
        res["D_monotonicity"][nm] = {"spearman_Chat_w": sp, "PASS": bool(abs(sp - 1.0) < 1e-9)}
        print(f"(A) {nm}: w in [{wv.min():.4f},{wv.max():.4f}] PASS={res['A_boundedness'][nm]['PASS']} | "
              f"(D) Spearman(C_hat,w)={sp:.6f} PASS={res['D_monotonicity'][nm]['PASS']}", flush=True)

    # (B) SHANNON RECOVERY (sample pairs across MIp percentiles)
    order = sorted(pairs, key=lambda p: K_MI_saved[p])
    sample = [order[int(q * (len(order) - 1))] for q in np.linspace(0, 1, 25)]
    wH, wI = shannon_recovery(M, w, sample)
    res["B_shannon"] = {"max_abs_dH": wH, "max_abs_dI": wI, "PASS": bool(wH < 1e-9 and wI < 1e-9)}
    print(f"(B) Shannon recovery: max|H_w-H|={wH:.2e}  max|I_w-I|={wI:.2e}  PASS={res['B_shannon']['PASS']}", flush=True)

    # (C) COARSE-GRAINING (Dayhoff-6 + gap = 7 symbols)
    dmap = dayhoff_map(); Mc = dmap[M]
    MIp_c, Kc_c = estimators(Mc, w, 7)
    res["C_coarse"] = {}
    for nm, Kc_coarse in (("K_MI", MIp_c), ("K_comp", Kc_c)):
        sp = spear(vec(base[nm], pairs), vec(Kc_coarse, pairs))
        res["C_coarse"][nm] = {"spearman_full_vs_coarse": sp, "PASS": bool(sp >= 0.7)}
        print(f"(C) {nm}: Spearman(full, Dayhoff-6) = {sp:.4f}  PASS={res['C_coarse'][nm]['PASS']}", flush=True)

    # (E) RELABEL INVARIANCE (within-Dayhoff-class permutation; count-based -> exact)
    perm = within_class_relabel(); Mr = perm[M]
    MIp_r, Kc_r = estimators(Mr, w, STATES)
    res["E_relabel"] = {}
    for nm, Kr in (("K_MI", MIp_r), ("K_comp", Kc_r)):
        sp = spear(vec(rec_base[nm], pairs), vec(Kr, pairs))   # same-code reference -> clean 1.0
        res["E_relabel"][nm] = {"spearman_orig_vs_relabel": sp, "PASS": bool(abs(sp - 1.0) < 1e-9)}
        print(f"(E) {nm}: Spearman(orig, within-class relabel) = {sp:.9f}  PASS={res['E_relabel'][nm]['PASS']}", flush=True)

    # (F) RESAMPLING STABILITY (100 ortholog bootstraps) -- heavy; gated
    if do_boot:
        rng = np.random.default_rng(0); sp_mi = []; sp_kc = []
        for b in range(nboot):
            idx = rng.integers(0, N, N); Mb = M[idx]; wb, _ = reweight(Mb)
            MIp_b, Kc_b = estimators(Mb, wb, STATES)
            sp_mi.append(spear(vec(rec_base["K_MI"], pairs), vec(MIp_b, pairs)))
            sp_kc.append(spear(vec(rec_base["K_comp"], pairs), vec(Kc_b, pairs)))
            if (b + 1) % 10 == 0:
                print(f"(F) {acc} boot {b+1}/{nboot}: meanS K_MI={np.mean(sp_mi):.3f} K_comp={np.mean(sp_kc):.3f}", flush=True)
        res["F_stability"] = {"K_MI": {"mean_spearman": float(np.mean(sp_mi)), "PASS": bool(np.mean(sp_mi) >= 0.8)},
                              "K_comp": {"mean_spearman": float(np.mean(sp_kc)), "PASS": bool(np.mean(sp_kc) >= 0.8)},
                              "nboot": nboot}
        print(f"(F) {acc} stability: K_MI mean Spearman={np.mean(sp_mi):.3f} K_comp={np.mean(sp_kc):.3f}", flush=True)

    json.dump(res, open(f"{PF}/admissibility_{acc}.json", "w"), indent=2, default=float)
    print(f"[saved] {PF}/admissibility_{acc}.json", flush=True)
    return res

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ae"   # 'ae' = A-E fast; 'all' = + bootstrap F
    do_boot = (mode == "all")
    for acc in ("PF13354", "PF00026"):
        run_family(acc, do_boot)
