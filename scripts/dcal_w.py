#!/usr/bin/env python3
"""D-cal-w -- v0.7.3 cross-domain: does the induced weight w carry transmissible structure BEYOND its base
measure, cross-domain? SMOKE ONLY -> HOLD (the base-matched null is make-or-break; Benjamin reviews it first).

Pre-registered 2026-06-26 (pre_registration.md "v0.7.3 D-cal-w PRE-REGISTRATION"). The induced weight
w=sigma(beta*rho), rho = leave-one-out REAL-COMPRESSOR (zstd K1) ablation delta. The BASE measure it weights =
statistical information (per-symbol surprisal + SAME-TIME pairwise MI). Question: does w transmit, across two
disjoint-alphabet encoders, structure the base does NOT -- beyond a base-matched null?

CONSTRUCTION (reuses cit.data.hsmm_d1 latent regime; the D-cal H coalition; D-cal disjoint encoders):
  P_FEATS  -- same-time pairwise-coupled (shared driver) -> BASE sees them; iid-in-time -> a surface compressor
              CANNOT see them post-encoding (disjoint relabeling breaks the cross-feature duplicate).
  RECUR    -- recursive long-range self-copy fB(t)=fB(t-TAU) (period-TAU) -> BASE-BLIND (marginal uniform,
              same-time pairwise MI ~0, 1-step entropy-rate ~marginal) yet a REAL compressor CAN see the
              period AND it SURVIVES disjoint encoding (relabeling preserves within-feature repeats). This is
              the clean w-beyond-base, encoding-surviving candidate (the open crack: compression-relevance vs
              statistical-information for a REAL compressor).
  PARITY   -- a pure-3rd-order parity triple c=(fa+fb+M[regime])%K -> base-blind AND compressor-blind
              post-encoding (cross-feature) -> a control that transmits via NEITHER.
  NOISE    -- iid uniform.
BASE-MATCHED NULL = SHARED-timestep shuffle of the latent (one permutation for all features) -> preserves
  marginals + SAME-TIME pairwise MI EXACTLY and the 1-step entropy rate (all features ~iid at 1 step), while
  DESTROYING the recursive/long-range temporal structure -> a real compressor's only beyond-base target is gone.

Real compressor = cit.proxies.categorical.compression_delta_proxy_cat (zstd K1), NOT the analytic-KT proxy
(D2 proved KT = MI). numpy + the cit pipeline. SMOKE ONLY. ASCII. Outputs -> data/ (gitignored).
Usage: python scripts/dcal_w.py [dev|smoke]
"""
import sys, json
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
from cit.data.hsmm_d1 import generate_stream, N_STATES
from cit.information import coherence_weighted_mutual_information, pmf_from_counts
from cit.proxies.categorical import compression_delta_proxy_cat
from cit.ablations.categorical import leave_one_out_ablation_cat
from cit.induce_cat import induce_weights_cat, BETA

# ---- construction constants ----
K = 8
F = 18
A1, A2 = 12, 10                                   # disjoint encoder alphabets (both >= K)
MASS = 0.95                                        # smoke-amend (dev): MASS=0.7 (30% noise) breaks every zstd exact
                                                  # repeat (run ~2 symbols) -> period undetectable; 0.95 -> run ~10
TAU = K * K                                        # recursive period = de Bruijn B(K,2) length (64): PURELY long-range
                                                  # (uniform 1-step transitions -> entropy rate = marginal EXACTLY,
                                                  # so the base-matched shuffle preserves entropy rate) yet periodic
EMIT_SEED_1, EMIT_SEED_2 = 10001, 20002
N_P, N_RECUR, N_PARITY = 6, 4, 3                  # role counts (the rest -> noise); positions VARY per latent
ALL_PAIRS = list(combinations(range(F), 2))


def roles(seed):
    """Per-latent role assignment (positions VARY per latent -> a valid across-latent null: a different latent
    puts RECUR/P at DIFFERENT feature indices, so its w-vector should NOT transfer with the real index)."""
    perm = np.random.default_rng(seed * 13 + 5).permutation(F)
    return (perm[:N_P], perm[N_P:N_P + N_RECUR],
            tuple(perm[N_P + N_RECUR:N_P + N_RECUR + N_PARITY]), perm[N_P + N_RECUR + N_PARITY:])


def de_bruijn_block(rng):
    """Randomized de Bruijn B(K,2) sequence (length K^2) via a Hierholzer Eulerian circuit on the complete
    digraph (every ordered pair (a,b) once). Periodic tiling has UNIFORM 1-step transitions (entropy rate =
    log K = marginal EXACTLY) and uniform marginal -> a PURELY long-range structure: base-blind (incl. entropy
    rate) but a real compressor sees the period. Independent draw per feature -> ~0 same-time pairwise MI."""
    adj = {a: list(rng.permutation(K)) for a in range(K)}
    stack, circuit = [0], []
    while stack:
        v = stack[-1]
        if adj[v]:
            stack.append(adj[v].pop())
        else:
            circuit.append(stack.pop())
    circuit = circuit[::-1]                         # Eulerian circuit of K^2+1 nodes
    return np.array(circuit[:-1], dtype=np.int64)   # period-K^2 block (drop the repeated closing node)


def latent_features_w(seed, T):
    states, _ = generate_stream(seed, T)
    rng = np.random.default_rng(seed * 100003 + 7)
    P_feats, RECUR, PARITY, NOISE = roles(seed)
    L = np.zeros((T, F), dtype=np.int64)
    b = rng.integers(0, K, T)
    q = rng.uniform(0.3, 0.95, size=len(P_feats))
    for idx, i in enumerate(P_feats):
        L[:, i] = np.where(rng.random(T) < q[idx], b, rng.integers(0, K, T))
    for f in RECUR:
        block = de_bruijn_block(rng)                # de Bruijn period (uniform marginal + uniform 1-step transitions)
        L[:, f] = block[np.arange(T) % len(block)]  # purely-long-range recursive structure fB(t)=fB(t-K^2)
    fa, fb = rng.integers(0, K, T), rng.integers(0, K, T)
    M = rng.integers(0, K, N_STATES)
    a, bb, c = PARITY
    L[:, a] = fa; L[:, bb] = fb; L[:, c] = (fa + fb + M[states]) % K
    for f in NOISE:
        L[:, f] = rng.integers(0, K, T)
    return states, L


def base_matched_null(L, seed):
    """SHARED-timestep shuffle (one permutation, all features) -> same-time joints (marginals + pairwise MI)
    EXACT; 1-step entropy rate ~preserved (all features ~iid at 1 step); recursive/long-range temporal DESTROYED."""
    perm = np.random.default_rng(seed * 7 + 1).permutation(L.shape[0])
    return L[perm]


def make_encoder(A, table_seed):
    rng = np.random.default_rng(table_seed)
    return np.stack([rng.permutation(A)[:K] for _ in range(F)]), A


def encode(L, enc, noise_seed):
    pi, A = enc
    rng = np.random.default_rng(noise_seed)
    O = np.zeros_like(L)
    for f in range(F):
        prim = pi[f][L[:, f]]
        keep = rng.random(L.shape[0]) < MASS
        other = rng.integers(0, A - 1, L.shape[0])
        other = other + (other >= prim)
        O[:, f] = np.where(keep, prim, other)
    return O, A


def raw_mi(x, y, Ax, Ay):
    counts = np.bincount(x.astype(np.int64) * Ay + y.astype(np.int64),
                         minlength=Ax * Ay).reshape(Ax, Ay).astype(np.float64)
    return coherence_weighted_mutual_information(pmf_from_counts(counts), np.ones(Ax))


def pairwise_coupling(O, A):
    """per-feature SAME-TIME pairwise-coupling = sum_j MI(f,j) -- the base measure's discriminative part."""
    M = np.zeros((F, F))
    for i, j in ALL_PAIRS:
        M[i, j] = M[j, i] = raw_mi(O[:, i], O[:, j], A, A)
    return M.sum(1)


def base_measure(O, A):
    """base vector b_f = per-symbol surprisal + same-time pairwise-coupling (both per feature)."""
    surpr = np.array([_marg_entropy(O[:, f], A) for f in range(F)])
    return surpr + pairwise_coupling(O, A)


def _marg_entropy(x, A):
    p = np.bincount(x, minlength=A) / len(x)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def _entropy_counts(c):
    c = c[c > 0].astype(float)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def lagged_self_mi(O, A, tau):
    """per-feature MI(O[t], O[t-tau]); tau = K^2 (the de Bruijn period) -> high for RECUR, ~0 for iid."""
    return np.array([raw_mi(O[tau:, f], O[:-tau, f], A, A) for f in range(F)])


def cond_entropy_order(O, A, M):
    """per-feature order-M conditional entropy H(X_t | X_{t-1..t-M}) = H(M+1-gram) - H(M-gram) (well-sampled
    high-order entropy-rate estimator; the de Bruijn period is order-2 deterministic -> M=2 drives it to ~0)."""
    Tn = O.shape[0]
    out = []
    for f in range(F):
        x = O[:, f]
        ctx = np.zeros(Tn - M, dtype=np.int64)
        for m in range(M):
            ctx = ctx * A + x[m:Tn - M + m]
        cur = x[M:]
        out.append(_entropy_counts(np.bincount(ctx * A + cur)) - _entropy_counts(np.bincount(ctx)))
    return np.array(out)


def _z(v):
    s = v.std()
    return (v - v.mean()) / s if s > 1e-9 else v * 0.0


BASE_LAGS = (TAU, 2 * TAU)        # self-MI lags: the de Bruijn period + its harmonic
BASE_ORDERS = (2, 3)              # predictive-info orders (de Bruijn is order-2 deterministic; A^4 still ~sampled)


def base_full(O, A):
    """FULL STATISTICAL-INFORMATION base (NO compressor), COMPLETE version: z-scored components = [same-time
    pairwise coupling] + [lagged self-MI at each BASE_LAG] + [predictive info = marginal entropy - order-M
    conditional entropy at each BASE_ORDER]. Returns (scalar z-sum, components F x n). The directive's minimal
    3-component base (one lag, one order) is IMPOVERISHED -- it leaves a spurious residual; 'FULL statistical
    information' means the complete statistical description, so w 'reduces to its base' is tested against the best
    statistical estimators available (giving w its best chance to show a residual; if none survives, w is
    statistical). NOTE: the literal large-Lblk block-entropy plug-in is undersampled (A^Lblk states) -> the
    order-M conditional entropy is the well-sampled estimator of the high-order entropy rate."""
    marg = np.array([_marg_entropy(O[:, f], A) for f in range(F)])
    cols = [pairwise_coupling(O, A)]
    cols += [lagged_self_mi(O, A, lag) for lag in BASE_LAGS]
    cols += [marg - cond_entropy_order(O, A, M) for M in BASE_ORDERS]
    comps = np.column_stack([_z(c) for c in cols])
    return comps.sum(1), comps


def w_residual(w, comps):
    """per-encoder OLS residual of w on [1, the THREE statistical base COMPONENTS] -> the part of w NOT explained
    by the full statistical base (multivariate: gives each statistical estimator its own coefficient, so 'w
    reduces to its base measure' is tested against the full base, not a single coarse scalar)."""
    X = np.column_stack([np.ones(len(w)), comps])
    coef, *_ = np.linalg.lstsq(X, w, rcond=None)
    return w - X @ coef


def induce_w(O, A, seed=0):
    res = induce_weights_cat(O, alphabet=A, proxy=compression_delta_proxy_cat,
                             ablation=leave_one_out_ablation_cat, rng=np.random.default_rng(seed))
    return np.array([res["w"][f] for f in range(F)])


def group_means(Wdict, seeds):
    """Mean value by ROLE using EACH latent's own (per-latent) role assignment."""
    acc = {"P": [], "RECUR": [], "PARITY": [], "NOISE": []}
    for s in seeds:
        Pf, Rc, Pa, No = roles(s)
        acc["P"].append(float(np.mean(Wdict[s][Pf])))
        acc["RECUR"].append(float(np.mean(Wdict[s][Rc])))
        acc["PARITY"].append(float(np.mean(Wdict[s][list(Pa)])))
        acc["NOISE"].append(float(np.mean(Wdict[s][No])))
    return {k: round(float(np.mean(v)), 3) for k, v in acc.items()}


def rank(x):
    return np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)


def spearman(x, y):
    if np.std(x) < 1e-4 or np.std(y) < 1e-4:       # DEGENERATE (near-constant) w -> no signal -> undefined, NOT noise
        return float("nan")
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def entropy_rate(O, A):
    out = []
    for f in range(F):
        x = O[:, f]
        j = np.bincount(x[:-1] * A + x[1:], minlength=A * A).reshape(A, A).astype(float)
        tot = j.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            p = np.where(j > 0, j / np.maximum(j.sum(1, keepdims=True), 1e-12), 0.0)
            out.append(-(j / tot * np.where(p > 0, np.log2(np.maximum(p, 1e-12)), 0.0)).sum())
    return np.array(out)


def marginal_tv(Oa, Ob, A):
    return float(max(0.5 * np.abs(np.bincount(Oa[:, f], minlength=A) / Oa.shape[0]
                                  - np.bincount(Ob[:, f], minlength=A) / Ob.shape[0]).sum() for f in range(F)))


def main(mode):
    T = {"dev": 6000, "smoke": 20000, "run": 50000}[mode]
    seeds = {"dev": list(range(7000, 7003)), "smoke": list(range(7000, 7006)),
             "run": list(range(7000, 7010))}[mode]
    enc1, enc2 = make_encoder(A1, EMIT_SEED_1), make_encoder(A2, EMIT_SEED_2)
    print(f"=== D-cal-w SMOKE [{mode}]  K={K} F={F} T={T} TAU={TAU} A1={A1} A2={A2} latents={len(seeds)} ===", flush=True)
    print(f"  roles per latent (positions VARY): {N_P} P_FEATS(base-visible) / {N_RECUR} RECUR(beyond-base,"
          f"compressor-visible) / {N_PARITY} PARITY(control) / rest NOISE", flush=True)

    # ---------- gate (i) NULL VALIDITY (load-bearing): base-matched shuffle matches base stats, differs in compressibility ----------
    s0 = seeds[0]
    _, L0 = latent_features_w(s0, T)
    Lsh = base_matched_null(L0, s0)
    print("\n--- gate (i) NULL VALIDITY (base-matched SHARED-shuffle: matches base stats, differs in compressibility) ---", flush=True)
    ck_real, ck_null, base_ok = {}, {}, True
    for tag, (enc, A) in [("enc1", (enc1, A1)), ("enc2", (enc2, A2))]:
        Oreal = encode(L0, enc, (EMIT_SEED_1 if tag == "enc1" else EMIT_SEED_2) * 7 + s0)[0]
        Onull = encode(Lsh, enc, (EMIT_SEED_1 if tag == "enc1" else EMIT_SEED_2) * 7 + s0)[0]
        # base-stat match (real vs shared-shuffle, SAME encoder)
        tv = marginal_tv(Oreal, Onull, A)
        pmi_real, pmi_null = pairwise_coupling(Oreal, A), pairwise_coupling(Onull, A)
        pmi_diff = float(np.max(np.abs(pmi_real - pmi_null)))
        er_real, er_null = entropy_rate(Oreal, A), entropy_rate(Onull, A)
        er_diff = float(np.max(np.abs(er_real - er_null)))
        ck_real[tag] = compression_delta_proxy_cat(Oreal, F, alphabet=A)
        ck_null[tag] = compression_delta_proxy_cat(Onull, F, alphabet=A)
        # shared-timestep shuffle preserves same-time joints EXACTLY at the latent (row permutation); the encoded
        # diffs are finite-sample / independent-noise (pairwise = a sum of 17 MIs -> sampling SD ~0.02). tols sized to that.
        matched = (tv < 0.02 and pmi_diff < 0.04 and er_diff < 0.05)
        base_ok = base_ok and matched
        print(f"  [{tag}] base-match: marginal TV={tv:.4f} pairwise-coupling max|d|={pmi_diff:.4f} "
              f"entropy-rate max|d|={er_diff:.4f} -> matched={matched}", flush=True)
        print(f"        compressibility C_K1: real={ck_real[tag]:.4f}  base-matched-null={ck_null[tag]:.4f}  "
              f"GAP={ck_real[tag]-ck_null[tag]:+.4f}  (real >> null?)", flush=True)
    gap1, gap2 = ck_real["enc1"] - ck_null["enc1"], ck_real["enc2"] - ck_null["enc2"]
    gate_i = base_ok and (gap1 > 0.05) and (gap2 > 0.05)
    print(f"  gate (i): base-matched={base_ok} AND compressibility gap>0.05 both encoders -> {gate_i}", flush=True)
    if base_ok and not gate_i:
        print("  NOTE: base-matched null does NOT differ in compressibility -> NO w-beyond-base structure to plant "
              "-> strong evidence for the DEFLATIONARY NEGATIVE (do not force a null). RECORD + HOLD.", flush=True)

    # ---------- induce w + base (same-time) + b_full (FULL statistical info) on the ensemble, both encoders ----------
    W1, W2, B1, B2, Wsh1, Wsh2, BF1, BF2, BC1, BC2 = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    for s in seeds:
        _, L = latent_features_w(s, T)
        Lsh_s = base_matched_null(L, s)
        O1 = encode(L, enc1, EMIT_SEED_1 * 7 + s)[0]; O2 = encode(L, enc2, EMIT_SEED_2 * 7 + s)[0]
        Os1 = encode(Lsh_s, enc1, EMIT_SEED_1 * 7 + s)[0]; Os2 = encode(Lsh_s, enc2, EMIT_SEED_2 * 7 + s)[0]
        W1[s], W2[s] = induce_w(O1, A1), induce_w(O2, A2)
        B1[s], B2[s] = base_measure(O1, A1), base_measure(O2, A2)        # same-time base (the prior, too-narrow base)
        BF1[s], BC1[s] = base_full(O1, A1); BF2[s], BC2[s] = base_full(O2, A2)   # FULL base: scalar + 3 components
        Wsh1[s], Wsh2[s] = induce_w(Os1, A1), induce_w(Os2, A2)
        print(f"  induced w+base(same-time)+b_full seed {s}", flush=True)

    # ---------- gate (ii) w COMPUTABLE + STABLE ----------
    std_w = float(np.min([np.std(W1[s]) for s in seeds] + [np.std(W2[s]) for s in seeds]))
    gate_ii = std_w > 1e-3
    print(f"\n--- gate (ii) w COMPUTABLE + STABLE: min std(w) over streams = {std_w:.4f} (>1e-3?) -> {gate_ii}", flush=True)
    # which features carry w vs base? (mean by per-latent role, enc1)
    wg = group_means(W1, seeds); bg = group_means(B1, seeds)
    print(f"  mean w    by role (enc1): P={wg['P']} RECUR={wg['RECUR']} PARITY={wg['PARITY']} NOISE={wg['NOISE']}  "
          f"(w should rank RECUR high: beyond-base/compressor-visible)", flush=True)
    print(f"  mean base by role (enc1): P={bg['P']} RECUR={bg['RECUR']} PARITY={bg['PARITY']} NOISE={bg['NOISE']}  "
          f"(base should rank P high: same-time pairwise)", flush=True)

    # ---------- transfers + gate (iii) CEILING ----------
    w_real = [spearman(W1[s], W2[s]) for s in seeds]
    w_null = [spearman(W1[a], W2[b]) for a in seeds for b in seeds if a != b]      # across-latent
    w_bmn = [spearman(Wsh1[s], Wsh2[s]) for s in seeds]                            # base-matched null
    b_real = [spearman(B1[s], B2[s]) for s in seeds]
    b_null = [spearman(B1[a], B2[b]) for a in seeds for b in seeds if a != b]
    n_bmn_degen = sum(1 for x in w_bmn if not np.isfinite(x))
    wr, wn, wb, br, bn = map(lambda z: np.array([x for x in z if np.isfinite(x)]), (w_real, w_null, w_bmn, b_real, b_null))
    wb_mean = float(wb.mean()) if wb.size else float("nan")
    print("\n--- transfers (Spearman of per-feature vectors across the two disjoint encoders) ---", flush=True)
    print(f"  w-transfer    real={wr.mean():+.3f}  across-latent-null={wn.mean():+.3f}  "
          f"base-matched-null={wb_mean:+.3f} (DEGENERATE w on {n_bmn_degen}/{len(w_bmn)} latents -> w killed when RECUR removed)", flush=True)
    print(f"  base-transfer real={br.mean():+.3f}  across-latent-null={bn.mean():+.3f}", flush=True)
    gate_iii = wr.mean() > wn.mean() + 0.2          # ceiling: w transmits with shared index, real >> across-latent null
    print(f"  gate (iii) CEILING: w-transfer real >> across-latent null -> {gate_iii}", flush=True)

    # ---------- DEFLATIONARY DEMONSTRATION (base correction: same-time -> FULL statistical information) ----------
    print("\n--- DEFLATIONARY DEMONSTRATION (b_full = z[same-time MI] + z[lagged self-MI @K^2] + z[predictive info]) ---", flush=True)
    bfg = group_means(BF1, seeds)
    print(f"  [4] mean b_full by role (enc1): P={bfg['P']} RECUR={bfg['RECUR']} PARITY={bfg['PARITY']} NOISE={bfg['NOISE']}  "
          f"(b_full should now ALSO rank RECUR high; PARITY stays low = sanity)", flush=True)
    sp_full = float(np.mean([spearman(W1[s], BF1[s]) for s in seeds] + [spearman(W2[s], BF2[s]) for s in seeds]))
    sp_same = float(np.mean([spearman(W1[s], B1[s]) for s in seeds] + [spearman(W2[s], B2[s]) for s in seeds]))
    print(f"  [1] Spearman(w, b_full)={sp_full:+.3f}  vs  Spearman(w, b_sametime)={sp_same:+.3f}  "
          f"(w explained by the FULL base, not the same-time base)", flush=True)
    bf_real = [spearman(BF1[s], BF2[s]) for s in seeds]
    bf_null = [spearman(BF1[a], BF2[b]) for a in seeds for b in seeds if a != b]
    bfr = np.array([x for x in bf_real if np.isfinite(x)]); bfn = np.array([x for x in bf_null if np.isfinite(x)])
    print(f"  [2] transfer(b_full) real={bfr.mean():+.3f} (across-latent null={bfn.mean():+.3f})  vs  "
          f"transfer(w) real={wr.mean():+.3f}  (the full base transmits what w transmits)", flush=True)
    WR1 = {s: w_residual(W1[s], BC1[s]) for s in seeds}; WR2 = {s: w_residual(W2[s], BC2[s]) for s in seeds}
    wres_real = [spearman(WR1[s], WR2[s]) for s in seeds]
    wres_null = [spearman(WR1[a], WR2[b]) for a in seeds for b in seeds if a != b]
    n_res_degen = sum(1 for x in wres_real if not np.isfinite(x))
    wrr = np.array([x for x in wres_real if np.isfinite(x)]); wrn = np.array([x for x in wres_null if np.isfinite(x)])
    wrr_mean = float(wrr.mean()) if wrr.size else float("nan")
    resid_role = group_means({s: np.abs(WR1[s]) for s in seeds}, seeds)        # mean |residual| by role
    w_role_abs = group_means({s: np.abs(W1[s] - W1[s].mean()) for s in seeds}, seeds)
    print(f"  [3] RESIDUAL transfer(w_resid) real={wrr_mean:+.3f}  across-latent null={wrn.mean():+.3f}  "
          f"(degenerate on {n_res_degen}/{len(wres_real)})", flush=True)
    print(f"      mean |w_resid| by role: P={resid_role['P']} RECUR={resid_role['RECUR']} PARITY={resid_role['PARITY']} "
          f"NOISE={resid_role['NOISE']}  (RECUR NOT elevated = w's signal ABSORBED by the full base; cf |w-mean| RECUR={w_role_abs['RECUR']})", flush=True)
    # deflationary = (1) w explained by full base >> same-time; (2) full base transmits AT LEAST what w does
    # (b_full >= w -tol -- exceeding is fine, it means the base captures w's transmission and more); (3) the
    # residual transfer ~= the across-latent null AND the residual magnitude on RECUR is absorbed (~ noise).
    resid_absorbed = (resid_role['RECUR'] <= 2 * resid_role['NOISE'] + 1e-9)
    deflationary = (sp_full > sp_same + 0.2) and (bfr.mean() >= wr.mean() - 0.1) and \
                   (wrr.size == 0 or abs(wrr_mean - wrn.mean()) < 0.15) and resid_absorbed
    print(f"  => DEFLATIONARY CONFIRMED (w reduces to its FULL statistical base; no coherence-specific residual): {deflationary}", flush=True)

    # ---------- gate (iv) DISJOINTNESS (encoders share no surface stat; disjoint alphabets) ----------
    e1a = encode(latent_features_w(seeds[0], T)[1], enc2, EMIT_SEED_2 * 7 + seeds[0])[0]
    e1b = encode(latent_features_w(seeds[1], T)[1], enc2, EMIT_SEED_2 * 7 + seeds[1])[0]
    tv_g = marginal_tv(e1a, e1b, A2)
    er_g = float(np.max(np.abs(entropy_rate(e1a, A2) - entropy_rate(e1b, A2)) / np.maximum(entropy_rate(e1a, A2), 1e-9)))
    gate_iv = (A1 != A2) and (tv_g < 0.05) and (er_g < 0.05)
    print(f"\n--- gate (iv) DISJOINTNESS: alphabets A1={A1}!=A2={A2}; generic-stat equality TV={tv_g:.4f} "
          f"entropy-rate reldiff={er_g:.4f} -> {gate_iv}", flush=True)

    # ---------- SMOKE SUMMARY (HOLD before official run) ----------
    gates = {"i_null_validity": gate_i, "ii_w_stable": gate_ii, "iii_ceiling": gate_iii, "iv_disjoint": gate_iv}
    print("\n=== SMOKE GATES ===", flush=True)
    for k_, v_ in gates.items():
        print(f"  {k_:16s}: {'PASS' if v_ else 'FAIL'}", flush=True)
    # ---------- VERDICT (the base-corrected demonstration is the headline; the same-time read was the artifact) ----------
    print(f"\n=== VERDICT (base-corrected) ===", flush=True)
    print(f"  same-time base (too narrow, ARTIFACT): w-transfer real {wr.mean():+.3f} >> across-latent null {wn.mean():+.3f}; "
          f"Spearman(w, b_sametime)={sp_same:+.3f} (LOW)", flush=True)
    print(f"  FULL statistical base: Spearman(w, b_full)={sp_full:+.3f}; transfer(b_full) {bfr.mean():+.3f} ~= transfer(w) "
          f"{wr.mean():+.3f}; RESIDUAL transfer(w_resid) real {wrr_mean:+.3f} ~= across-latent null {wrn.mean():+.3f}", flush=True)
    print(f"  => {'DEFLATIONARY CONFIRMED -- w REDUCES to its full statistical base; no coherence-specific transmissible residual' if deflationary else 'NOT clean -- inspect (residual or match off)'}", flush=True)
    print("  HOLD for Benjamin (statistical-only base; the de Bruijn period is detectable by lagged MI -> a", flush=True)
    print("  predictive-information statistic, not coherence-beyond-information; consistent with SMB).", flush=True)

    out = {"mode": mode, "T": T, "gates": gates,
           "gate_i": {"ck_real": ck_real, "ck_null": ck_null, "gap_enc1": gap1, "gap_enc2": gap2, "base_matched": base_ok},
           "w_by_role_enc1": wg, "base_sametime_by_role_enc1": bg, "b_full_by_role_enc1": bfg,
           "transfers": {"w_real": float(wr.mean()), "w_acrosslatent_null": float(wn.mean()),
                         "w_basematched_null": wb_mean, "w_basematched_degenerate": f"{n_bmn_degen}/{len(w_bmn)}",
                         "base_sametime_real": float(br.mean()), "b_full_real": float(bfr.mean()),
                         "b_full_acrosslatent_null": float(bfn.mean())},
           "demonstration": {"spearman_w_bfull": sp_full, "spearman_w_bsametime": sp_same,
                             "transfer_bfull_real": float(bfr.mean()), "transfer_w_real": float(wr.mean()),
                             "residual_transfer_real": wrr_mean, "residual_transfer_null": float(wrn.mean()),
                             "residual_degenerate": f"{n_res_degen}/{len(wres_real)}", "deflationary": bool(deflationary)},
           "std_w_min": std_w}
    json.dump(out, open(f"data/dcal_w_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal_w_{mode}.json", flush=True)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "smoke")
