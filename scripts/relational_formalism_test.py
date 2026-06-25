#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 3 PHASE 2 -- adversarial stress-test S1-S8 of the corrected
relational coherence-weighted functional (pre-registered 2026-06-25, pre_registration.md;
derivation design/relational_formalism.md).

    I_w_rel = sum_{(i,j) in E, |i-j|>=SEP} w(i,j) * I(X_i; X_j)

with I the RAW pairwise mutual information computed via the CANONICAL cit/information.py routines
at w = ones (NO hardcoded-ones reimplementation -- the step-2 tautology trap). Tested at w != 1,
not only w == 1. Reuses each family's saved matrix + saved APC-MIp (REUSED for the induced w and
the S7 base-evidence; never recomputed). numpy + math.lgamma only; DENSE (no DCA). Two families.
Outputs -> data/pfam/ (gitignored). NOT committed (Phase 1 docs/pre-reg only).
"""
import sys, math, json
import numpy as np

sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, STATES, PF
from cit.information import (
    coherence_weighted_mutual_information as cwmi,
    coherence_weighted_entropy as cwe,
    shannon_entropy,
)

SEP = 5
RNG_SEED = 0            # random-w control (verification determinism; NOT a locked science constant)
BETA = 4.0             # LOCKED induced-w sensitivity
LN2 = math.log(2.0)
AA = "ACDEFGHIKLMNPQRSTVWY"
DAYHOFF = [set("C"), set("AGPST"), set("DENQ"), set("RHK"), set("ILMV"), set("FWY")]  # gap (20) fixed


def sigma(x):
    return 1.0 / (1.0 + np.exp(-x))


def raw_I_matrix(M, w):
    """Symmetric LxL matrix of RAW pairwise MI (BITS). Each entry is taken from the CANONICAL
    cit/information.py routine cwmi(joint_ij, ones21): the matmul builds only the reweighted joint
    DISTRIBUTION; the MI VALUE comes from canonical code (no inline MI formula)."""
    N, L = M.shape
    wv = w.astype(np.float64)
    Wsum = wv.sum()
    OH = np.zeros((N, L, STATES))
    for a in range(STATES):
        OH[:, :, a] = (M == a)
    OHflat = OH.reshape(N, L * STATES)
    ones21 = np.ones(STATES)
    I = np.zeros((L, L))
    for i in range(L):
        Wi = OH[:, i, :] * wv[:, None]
        F = (Wi.T @ OHflat).reshape(STATES, L, STATES) / Wsum   # F[a, j, b] = p(X_i=a, X_j=b)
        for j in range(i + 1, L):
            joint = F[:, j, :]                                  # 21x21 pmf, sums to 1
            I[i, j] = I[j, i] = cwmi(joint, ones21, base=2.0)   # canonical MI, bits
    return I


def merged_node_beta(M, w, i, j):
    """beta = CANONICAL single-source H_w on the merged 441-joint node (= H(X_i, X_j) at w=ones):
    the quantity the RETRACTED edge-w object would weight. Plus H(X_i), H(X_j) for the contrast."""
    wv = w.astype(np.float64)
    Wsum = wv.sum()
    fi = np.array([(wv * (M[:, i] == a)).sum() for a in range(STATES)]) / Wsum
    fj = np.array([(wv * (M[:, j] == a)).sum() for a in range(STATES)]) / Wsum
    jcnt = np.zeros((STATES, STATES))
    for a in range(STATES):
        sel = M[:, i] == a
        if sel.any():
            jcnt[a] = np.bincount(M[sel, j], weights=wv[sel], minlength=STATES)
    fij = (jcnt / Wsum).ravel()                                 # 441 pmf
    Hjoint = cwe(fij, np.ones(STATES * STATES), base=2.0)       # canonical H_w, w=ones
    return Hjoint, shannon_entropy(fi, base=2.0), shannon_entropy(fj, base=2.0)


def eligible_edges(L, sep):
    return [(i, j) for i in range(L) for j in range(i + 1, L) if (j - i) >= sep]


def i_w_rel(w_edges, I_edges):
    return float(np.dot(np.asarray(w_edges, float), np.asarray(I_edges, float)))


def induced_w(rho_edges):
    z = (rho_edges - rho_edges.mean()) / rho_edges.std()
    return sigma(BETA * z)


def relabel_within_dayhoff():
    """Bijection on the 21 symbols: cyclic shift within each Dayhoff class; gap + singleton fixed."""
    perm = np.arange(STATES)
    for cls in DAYHOFF:
        idx = [AA.index(c) for c in sorted(cls)]
        if len(idx) > 1:
            for a, b in zip(idx, idx[1:] + idx[:1]):
                perm[a] = b
    return perm


def run(acc):
    print(f"\n===== relational-functional stress-test {acc} =====", flush=True)
    M = np.load(f"{PF}/pilotS_{acc}_matrix.npy")
    N, L = M.shape
    w_seq, Meff = reweight(M)
    MIp = np.load(f"{PF}/pilot_coupling_{acc}.npz")["MIp"]       # APC-MIp, nats, REUSED (never recomputed)
    print(f"L={L} N={N} Meff={Meff:.1f}; building raw-I matrix via canonical cwmi...", flush=True)
    I = raw_I_matrix(M, w_seq)

    E = eligible_edges(L, SEP)
    nE = len(E)
    ii = np.array([e[0] for e in E])
    jj = np.array([e[1] for e in E])
    eidx = {e: k for k, e in enumerate(E)}
    I_e = I[ii, jj]
    MIp_e = MIp[ii, jj]
    sumI = float(I_e.sum())

    rng = np.random.default_rng(RNG_SEED)
    w_one = np.ones(nE)
    w_rand = rng.uniform(0.0, 1.0, nE)
    w_ind = induced_w(MIp_e)                                     # induced from marginal-relative APC-MIp

    # ---- S1 SHANNON RECOVERY (real) + non-trivial weight response ----
    iwr_one = i_w_rel(w_one, I_e)
    iwr_rand = i_w_rel(w_rand, I_e)
    iwr_ind = i_w_rel(w_ind, I_e)

    def handsum(wv):
        t = 0.0
        for k in range(nE):
            t += float(wv[k]) * float(I_e[k])
        return t

    s1_recov = abs(iwr_one - sumI)
    s1_hand_rand = abs(iwr_rand - handsum(w_rand))
    s1_hand_ind = abs(iwr_ind - handsum(w_ind))
    s1_resp_rand = abs(iwr_rand - sumI)
    s1_resp_ind = abs(iwr_ind - sumI)
    S1 = (s1_recov < 1e-9 and s1_hand_rand < 1e-9 and s1_hand_ind < 1e-9
          and s1_resp_rand > 1e-9 and s1_resp_ind > 1e-9)

    # ---- S2 NON-COLLAPSE (relational alpha vs merged-node beta) ----
    order = np.argsort(I_e)
    low = [E[k] for k in order[:3]]
    high = [E[k] for k in order[-3:]]
    s2 = []
    for (i, j) in low + high:
        Iij = float(I[i, j])
        Hjoint, Hi, Hj = merged_node_beta(M, w_seq, i, j)
        alpha = float(w_ind[eidx[(i, j)]]) * Iij
        s2.append({"pair": [int(i), int(j)], "band": "low" if (i, j) in low else "high",
                   "I_bits": Iij, "w_ind": float(w_ind[eidx[(i, j)]]), "alpha_wI": alpha,
                   "beta_Hjoint": float(Hjoint), "Hi_plus_Hj": float(Hi + Hj),
                   "alpha_over_beta": alpha / float(Hjoint)})
    low_rows = [r for r in s2 if r["band"] == "low"]
    S2 = (max(r["alpha_over_beta"] for r in low_rows) < 0.20
          and min(r["beta_Hjoint"] for r in low_rows) > 1.0)

    # ---- S3 HANDSHAKE / OVERLAP (sum_i c_i == 2 I_w_rel) ----
    def handshake_resid(wv):
        c = np.zeros(L)
        np.add.at(c, ii, wv * I_e)
        np.add.at(c, jj, wv * I_e)
        return abs(float(c.sum()) - 2.0 * i_w_rel(wv, I_e))

    s3_one, s3_rand, s3_ind = handshake_resid(w_one), handshake_resid(w_rand), handshake_resid(w_ind)
    S3 = max(s3_one, s3_rand, s3_ind) < 1e-9

    # ---- S4 MONOTONICITY (single-weight perturbation = exactly delta * I) ----
    delta = 1e-3
    smp = rng.choice(nE, size=min(500, nE), replace=False)
    base_iwr = i_w_rel(w_ind, I_e)
    s4_maxerr = 0.0
    s4_inv = 0
    for k in smp:
        wp = w_ind.copy()
        wp[k] = min(1.0, w_ind[k] + delta)
        applied = wp[k] - w_ind[k]
        diff = i_w_rel(wp, I_e) - base_iwr
        s4_maxerr = max(s4_maxerr, abs(diff - applied * float(I_e[k])))
        if diff < -1e-12:
            s4_inv += 1
    S4 = (s4_maxerr < 1e-9 and s4_inv == 0)

    # ---- S5 BOUNDEDNESS (C_rel in [0,1]; ==1 at w==1) ----
    c_one = iwr_one / sumI
    c_rand = iwr_rand / sumI
    c_ind = iwr_ind / sumI
    S5 = (abs(c_one - 1.0) < 1e-9 and 0.0 <= c_rand <= 1.0 and 0.0 <= c_ind <= 1.0)

    # ---- S6 RELABEL / DOMAIN-TRANSLATION INVARIANCE (recompute I via canonical on relabeled alphabet) ----
    perm = relabel_within_dayhoff()
    Mr = perm[M]
    w_seq_r, _ = reweight(Mr)
    Ir_e = raw_I_matrix(Mr, w_seq_r)[ii, jj]
    s6 = abs(i_w_rel(w_ind, Ir_e) - i_w_rel(w_ind, I_e))        # SAME w, I recomputed on relabel
    S6 = s6 < 1e-9

    # ---- S7 BASE-CHOICE EVIDENCE (informs c3; NO pass/fail) ----
    sum_I_bits = sumI
    sum_MIp_bits = float(MIp_e.sum()) / LN2
    n_neg_MIp = int((MIp_e < 0).sum())

    # ---- S8 NORMALIZER EVIDENCE (informs c1; NO pass/fail) ----
    C_sumI = iwr_ind / sumI
    C_perE = iwr_ind / nE
    C_max = iwr_ind / float(I_e.max())

    print(f"S1 recovery|dIwr-sumI|={s1_recov:.2e} hand(rand/ind)={s1_hand_rand:.2e}/{s1_hand_ind:.2e} "
          f"resp(rand/ind)={s1_resp_rand:.3f}/{s1_resp_ind:.3f} -> {'PASS' if S1 else 'FAIL'}", flush=True)
    for r in s2:
        print(f"S2 {r['band']:>4} pair{tuple(r['pair'])}: I={r['I_bits']:.3f}b w={r['w_ind']:.3f} "
              f"alpha=w*I={r['alpha_wI']:.4f}b  beta=Hjoint={r['beta_Hjoint']:.3f}b (Hi+Hj={r['Hi_plus_Hj']:.3f}) "
              f"alpha/beta={r['alpha_over_beta']:.4f}", flush=True)
    print(f"S2 non-collapse -> {'PASS' if S2 else 'FAIL'} (low-band alpha/beta<0.20 AND beta>1b)", flush=True)
    print(f"S3 handshake resid one/rand/ind = {s3_one:.2e}/{s3_rand:.2e}/{s3_ind:.2e} -> {'PASS' if S3 else 'FAIL'}", flush=True)
    print(f"S4 monotonicity max|err|={s4_maxerr:.2e} inversions={s4_inv}/{len(smp)} -> {'PASS' if S4 else 'FAIL'}", flush=True)
    print(f"S5 boundedness C_rel one/rand/ind = {c_one:.6f}/{c_rand:.4f}/{c_ind:.4f} -> {'PASS' if S5 else 'FAIL'}", flush=True)
    print(f"S6 relabel-invariance |dIwr|={s6:.2e} -> {'PASS' if S6 else 'FAIL'}", flush=True)
    print(f"S7 base evidence: sum I (raw, bits)={sum_I_bits:.2f} >=0 | sum MIp (bits)={sum_MIp_bits:.2f} "
          f"| negative-MIp edges = {n_neg_MIp}/{nE}", flush=True)
    print(f"S8 normalizer evidence (induced w): C[sum I]={C_sumI:.4f}  C[/|E|]={C_perE:.3e} b/edge  "
          f"C[/max I]={C_max:.3f}", flush=True)

    gap_closed = S1 and S2 and S3 and S4 and S5 and S6
    print(f"VERDICT(family) S1-S6 -> {'GAP CLOSED' if gap_closed else 'NOT CLOSED'}", flush=True)

    res = {"acc": acc, "L": L, "N": N, "Meff": Meff, "nE": nE,
           "S1_shannon_recovery": bool(S1), "s1_recov": s1_recov,
           "s1_hand_rand": s1_hand_rand, "s1_hand_ind": s1_hand_ind,
           "s1_resp_rand": s1_resp_rand, "s1_resp_ind": s1_resp_ind,
           "S2_non_collapse": bool(S2), "s2_rows": s2,
           "S3_handshake": bool(S3), "s3_one": s3_one, "s3_rand": s3_rand, "s3_ind": s3_ind,
           "S4_monotonicity": bool(S4), "s4_maxerr": s4_maxerr, "s4_inversions": s4_inv,
           "S5_boundedness": bool(S5), "c_one": c_one, "c_rand": c_rand, "c_ind": c_ind,
           "S6_relabel_invariance": bool(S6), "s6_dIwr": s6,
           "S7_sum_I_bits": sum_I_bits, "S7_sum_MIp_bits": sum_MIp_bits, "S7_n_neg_MIp": n_neg_MIp,
           "S8_C_sumI": C_sumI, "S8_C_perE": C_perE, "S8_C_max": C_max,
           "GAP_CLOSED_family": bool(gap_closed)}
    json.dump(res, open(f"{PF}/relational_formalism_test_{acc}.json", "w"), indent=2, default=float)
    return res


if __name__ == "__main__":
    rs = [run("PF13354"), run("PF00026")]
    both = all(r["GAP_CLOSED_family"] for r in rs)
    print(f"\n===== STRESS-TEST VERDICT = {'GAP CLOSED' if both else 'NOT CLOSED'} "
          f"(S1-S6 on BOTH families) =====")
    json.dump({"families": rs, "GAP_CLOSED_both": bool(both)},
              open(f"{PF}/relational_formalism_test_verdict.json", "w"), indent=2, default=float)
    print(f"saved {PF}/relational_formalism_test_verdict.json")
