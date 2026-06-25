#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 7 -- THEOREM verification (read-only, no new run).

Records, per family, the EXACT affine relationship K_comp = N_eff*(raw MI) - KT_penalty that
closes the D2 relational line as a falsification (pre_registration.md 2026-06-25 step-7 entry):
  (b) K_comp is an AFFINE transform of raw MI -- NOT a distinct estimator:
      OLS K_comp ~ a + b*MI gives slope b == N_eff (b/N_eff ~ 1.02-1.06), R^2 0.987-0.994,
      Spearman(rawMI, K_comp) +0.99; the decomposition is exact to <= 7e-12 per pair.
  (c) PENALTY CORRECTION: the intercept a ~ -720 (not the briefed -200*log2 N ~ -2100): the
      21x21 joint is ~62% EMPTY, so KT charges only for the realized support.
  (e) R2-edge convergence ILLUSORY: long-range Spearman(K_MI, K_comp) == Spearman(rawMI, rawMI-APC),
      and the residual after removing raw MI from BOTH arms is NEGATIVE (-0.15 / -0.45).

Reuses the SAME apparatus (estimators_whole) so the K_comp here is bit-identical to the recorded
null-probe K_comp. Raw MI is the canonical Shannon plug-in. APC-MIp (K_MI) reused from saved npz.
Read-only on data/pfam/ (saved matrices + saved MIp). numpy + math.lgamma only; ASCII-only.
"""
import sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, "scripts")
from run_d2_family2 import reweight, PF, SEP, LONG
from r2_edge import eligible_pairs
from r1_null_probe import estimators_whole

FAMS = ["PF13354", "PF00026", "PF00348"]


def rank(x):
    return np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)


def spearman(x, y):
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def ols(x, y):
    Z = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(Z, y, rcond=None)
    yhat = Z @ beta
    r2 = 1.0 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return float(beta[0]), float(beta[1]), float(r2)


def rank_resid(y, x):
    ry = rank(y); Z = np.column_stack([np.ones(len(ry)), rank(x)])
    return ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]


def run():
    for acc in FAMS:
        M = np.load(f"{PF}/pilotS_{acc}_matrix.npy"); N, L = M.shape
        w_seq, _ = reweight(M)
        Wsum = float(w_seq.astype(np.float64).sum())
        E = eligible_pairs(list(range(L)), SEP); nE = len(E)
        byi = defaultdict(list)
        for k, (i, j) in enumerate(E):
            byi[i].append((j, k))
        mi, kc = estimators_whole(M, w_seq, byi, nE)
        sp = spearman(mi, kc)
        a, b, r2 = ols(mi, kc)
        print(f"\n===== {acc}  (N_eff={Wsum:.1f}, nE={nE}) =====")
        print(f"  (b) THEOREM  Spearman(rawMI,K_comp)={sp:+.4f}  OLS K_comp={a:+.1f}+{b:.1f}*MI  "
              f"R^2={r2:.4f}  b/N_eff={b/Wsum:.3f}")
        print(f"  (c) PENALTY  intercept a={a:+.1f}  vs  -200*log2(N_eff)={-200*np.log2(Wsum):+.1f}  "
              f"(ratio {a/(-200*np.log2(Wsum)):.3f})")
        # (e) R2-edge illusory: needs saved APC-MIp; PF00348 has no pilot_coupling npz (R1-only family)
        try:
            kmi = np.load(f"{PF}/pilot_coupling_{acc}.npz")["MIp"]
            kmiE = np.array([kmi[i, j] for (i, j) in E])
            ii = np.array([e[0] for e in E]); jj = np.array([e[1] for e in E])
            m = np.where((jj - ii) >= LONG)[0]
            head = spearman(kmiE[m], kc[m])
            res = float(np.corrcoef(rank_resid(kmiE[m], mi[m]), rank_resid(kc[m], mi[m]))[0, 1])
            print(f"  (e) R2-EDGE  long-range Spearman(K_MI,K_comp)={head:+.4f}  "
                  f"== Spearman(K_MI,rawMI)={spearman(kmiE[m], mi[m]):+.4f};  "
                  f"residual(K_MI|raw vs K_comp|raw)={res:+.4f} (NEGATIVE -> no second paradigm)")
        except FileNotFoundError:
            print(f"  (e) R2-EDGE  [no saved APC-MIp for {acc} (R1-only family); see PF13354/PF00026]")


if __name__ == "__main__":
    run()
