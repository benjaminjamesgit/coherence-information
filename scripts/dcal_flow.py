#!/usr/bin/env python3
"""D-cal-flow STEP 1 -- v0.7.3 cross-domain: apparatus validation for the corpus-faithful FLOW object.

Pre-registered 2026-06-26 (pre_registration.md "v0.7.3 CROSS-DOMAIN / D-cal-flow PRE-REGISTRATION (corpus-faithful
flow object; STEP 1 = apparatus validation)"). STEP 1 ONLY -- validate that the corpus coarse-graining (Formal
Foundations Sec 2.3 + Sec 6) extracts the planted eta-STRUCTURE WITH correspondence. NOT the transmission test
(Step 2). NO verdict on option (c).

CORPUS GROUNDING. Sec 2.3 nested closure: coarse-graining = nested grouping; coherence composes by a bounded
log-odds rule (cannot densify/saturate); C is form-invariant, the flow is in the PARAMETERS. Sec 6.1-6.3 RG flow
over a PROCESS scale ell (block b=2^ell): beta(ell)=beta0*b^d (sensitivity, GROWS), lam(ell)=lam0*b^(-d/2)
(dissipation, SHRINKS), g=beta*lam GROWS to the coherence fixed point; Sec 6.3 anomalous dimension eta from
feedback among components (d generic / eta the only structure-bearing part; corpus eta SCALAR -> eta-STRUCTURE the gap).

CONSTRUCTION. Nested-regime latent: a SLOW super-regime (dwell M_SUP) and a FAST sub-regime (dwell M_SUB) run
together. Features are grouped in MODULES of size MOD_SIZE that share a real-valued driver + idiosyncratic white
noise. NORMAL modules are driven by the FAST sub-regime (their coupling rises then PLATEAUS under temporal
coarse-graining -- the sub-signal averages out at the same 1/b rate as the noise -> trivial exponent). ANOMALOUS
modules are driven by the SLOW super-regime (their coupling keeps RISING across the scale window because the slow
signal survives block-averaging while the noise dies -> the anomalous, structure-bearing exponent = feedback).
Plus pure-noise (uncoupled) features. The continuous latent is quantized to K ordinal bins and rendered through ONE
disjoint-alphabet encoder (D-cal lineage; Step 2 uses both). Planted ground truth = the anomalous-feature set +
the within-module coupling graph (the eta-STRUCTURE).

APPARATUS (on the rendered categorical data; permutation-invariant -> Step-2-ready). Coarse-grain over TIME by
block-MODE at b=2^ell (mode is alphabet-permutation-equivariant; normalized MI is permutation-INVARIANT). At each
ell: W(ell) = symmetric-uncertainty (normalized-MI) coupling matrix. noise_fraction(ell) = mean over features of
(1 - U*_f), U*_f = mean of feature f's top (MOD_SIZE-1) normalized-MI couplings. beta = 1/noise_fraction (GROWS),
lam = sqrt(noise_fraction) (SHRINKS, the b^(-d/2) half-rate), g = beta*lam = 1/sqrt(noise_fraction) (GROWS by
construction iff noise_fraction decays -> faithful to dg/dell=(d/2)g). Fit log2(beta) vs ell -> slope d (generic).
Per-feature beta_f = 1/(1-U*_f); slope d_f; eta_f = d_f - d_generic (EXCESS reinforcement exponent: ~0 normal,
>0 anomalous). eta-STRUCTURE = the per-feature eta_f vector + the recovered coupling graph.

Usage: python scripts/dcal_flow.py [dev|smoke|run]   (default run)
"""
import sys, json
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
import scripts.dcal2 as d2   # MASS + the disjoint-alphabet encoder convention (mirrored below, F-parametrized)

MASS = d2.MASS              # 0.7 keep-probability (D-cal lineage)


def make_encoder(A, table_seed, F):
    rng = np.random.default_rng(table_seed)
    return np.stack([rng.permutation(A)[:K] for _ in range(F)]), A


def encode(L, enc, noise_seed):
    pi, A = enc
    rng = np.random.default_rng(noise_seed)
    O = np.zeros_like(L)
    for f in range(L.shape[1]):
        prim = pi[f][L[:, f]]
        keep = rng.random(L.shape[0]) < MASS
        other = rng.integers(0, A - 1, L.shape[0])
        other = other + (other >= prim)
        O[:, f] = np.where(keep, prim, other)
    return O, A

# ---- LOCKED-ish construction constants (Step 1; smoke-amend append-only if a gate fails on a confound) ----
K = 8                     # ordinal quantization bins of the continuous latent
MOD_SIZE = 3              # features per coupled module
M_SUB = 4                # FAST sub-regime mean dwell (normal-module driver timescale)
M_SUP = 400              # SLOW super-regime mean dwell (anomalous-module driver timescale)
N_SUB, N_SUP = 6, 6      # regime state counts (distinct driver values)
DISP = 6                 # negative-binomial dwell dispersion (as in hsmm_d1)
SIGMA = 1.0              # idiosyncratic white-noise std (driver signal std ~1 -> latent corr ~0.5..0.98 across scales)
ELL_FIT_LO = 0           # fit the per-feature exponent over the FULL measured scale window (anomalous rises
                         # throughout, normal rises-then-plateaus -> full-window slope separates them; the
                         # well-sampled fine scales stabilize the fit vs a starved coarse-only fit)
A1, A2 = 12, 10          # disjoint encoder alphabets (Step 1 uses A1)
EMIT_SEED_1, EMIT_SEED_2 = 10001, 20002
GEN_SEED = 7000          # latent realization seed (Step 1: single realization + ground truth)
BOOT_BLOCK = M_SUP       # moving-block-bootstrap block length for the eta CI (gate iii): one super-regime dwell


def _modes(F):
    """dev/smoke/run feature layout: alternate NORMAL/ANOMALOUS modules of MOD_SIZE, reserve ~F/5 noise features."""
    n_noise = max(MOD_SIZE, F // 5)
    n_mod = (F - n_noise) // MOD_SIZE
    if n_mod % 2:                                  # keep normal/anomalous balanced
        n_mod -= 1
    return n_mod, n_noise


# =================== nested-regime continuous latent (the planted physics) ===================
def regime_path(rng, T, n_states, mean_dwell):
    """Negative-binomial-dwell regime sequence (forced switch at each dwell boundary)."""
    p = DISP / (DISP + mean_dwell)
    out = np.empty(T, dtype=np.int64)
    t = 0; cur = int(rng.integers(n_states))
    while t < T:
        dwell = max(1, int(rng.negative_binomial(DISP, p)))
        out[t:t + dwell] = cur
        t += dwell
        cur = (cur + 1 + int(rng.integers(n_states - 1))) % n_states
    return out[:T]


def generate(seed, T, F):
    """Return (Lq categorical latent (T,F) in [0,K), anomalous_label (F,), module_id (F,) with -1 for noise)."""
    rng = np.random.default_rng(seed)
    sup = regime_path(rng, T, N_SUP, M_SUP)        # slow
    sub = regime_path(rng, T, N_SUB, M_SUB)        # fast
    n_mod, n_noise = _modes(F)
    module_id = -np.ones(F, dtype=np.int64)
    anomalous = np.zeros(F, dtype=np.int64)
    X = np.empty((T, F), dtype=np.float64)
    f = 0
    for m in range(n_mod):
        is_anom = (m % 2 == 1)                     # alternate: even=normal(sub), odd=anomalous(sup)
        vals = rng.normal(0.0, 1.0, size=(N_SUP if is_anom else N_SUB))   # driver value per regime state
        driver = vals[sup] if is_anom else vals[sub]
        for _ in range(MOD_SIZE):
            X[:, f] = driver + SIGMA * rng.normal(0.0, 1.0, size=T)
            module_id[f] = m; anomalous[f] = int(is_anom); f += 1
    while f < F:                                   # pure-noise (uncoupled) features
        X[:, f] = rng.normal(0.0, 1.0, size=T); f += 1
    # quantize each feature to K ordinal bins by its own quantiles (marginally ~uniform)
    Lq = np.empty((T, F), dtype=np.int64)
    for j in range(F):
        edges = np.quantile(X[:, j], np.linspace(0, 1, K + 1)[1:-1])
        Lq[:, j] = np.searchsorted(edges, X[:, j])
    return Lq, anomalous, module_id


# =================== temporal coarse-graining (block-MODE) + coupling matrix (normalized MI) ===================
def block_mode(O, A, b):
    """Coarse-grain time by non-overlapping block-MODE per feature (permutation-equivariant). Returns (T//b, F)."""
    if b == 1:
        return O
    T, F = O.shape
    nb = T // b
    Oc = np.empty((nb, F), dtype=np.int64)
    blk = O[:nb * b].reshape(nb, b, F)
    for j in range(F):
        counts = np.zeros((nb, A), dtype=np.int64)
        col = blk[:, :, j]
        for off in range(b):
            counts[np.arange(nb), col[:, off]] += 1
        Oc[:, j] = counts.argmax(1)
    return Oc


def _entropy(c):
    p = c[c > 0] / c.sum()
    return float(-(p * np.log2(p)).sum())


def _raw_nmi(M, A):
    """Raw symmetric-uncertainty (normalized MI) matrix U_ij = 2 I(i;j)/(H_i+H_j) in [0,1], diag 0 (plug-in)."""
    F = M.shape[1]
    H = np.array([_entropy(np.bincount(M[:, i], minlength=A)) for i in range(F)])
    W = np.zeros((F, F))
    for i, j in combinations(range(F), 2):
        cij = np.bincount(M[:, i] * A + M[:, j], minlength=A * A).reshape(A, A).astype(float)
        Iij = _entropy(cij.sum(1)) + _entropy(cij.sum(0)) - _entropy(cij)
        denom = H[i] + H[j]
        W[i, j] = W[j, i] = (2.0 * Iij / denom) if denom > 1e-12 else 0.0
    return W


def norm_mi_matrix(M, A):
    """Bias-corrected coupling matrix: raw normalized MI minus the analytic Miller-Madow independence floor
    (A-1)^2/(2N) (nats) -> bits -> normalized. Removes the finite-sample plug-in bias that scales as 1/N and
    swamps the signal at sample-starved coarse scales. Deterministic -> EXACTLY permutation-invariant (Step-2
    ready, gate v clean). Clamped at 0."""
    W = _raw_nmi(M, A)
    N = M.shape[0]
    floor = ((A - 1.0) ** 2 / (2.0 * N)) / np.log(2.0) / np.log2(A)   # MM bias, normalized-MI units
    return np.maximum(0.0, W - floor)


def _Ustar(W, k):
    """Per-feature coupling-reinforcement: mean of feature f's top-k normalized-MI couplings."""
    F = W.shape[0]
    out = np.empty(F)
    for f in range(F):
        row = np.sort(W[f])[::-1]
        out[f] = float(np.mean(row[:k]))
    return out


# =================== flow over scales ===================
def flow(O, A, L, topk):
    """Return per-scale ells, W list, global beta/lam/g, and per-feature Ustar matrix (scales x F)."""
    ells = list(range(L + 1))
    Ws, Ustars, nf = [], [], []
    for ell in ells:
        M = block_mode(O, A, 2 ** ell)
        W = norm_mi_matrix(M, A)
        us = _Ustar(W, topk)
        Ws.append(W); Ustars.append(us)
        nf.append(float(np.mean(1.0 - us)))
    nf = np.array(nf)
    beta = 1.0 / np.maximum(nf, 1e-6)
    lam = np.sqrt(np.maximum(nf, 1e-12))
    g = beta * lam
    return ells, Ws, beta, lam, g, np.array(Ustars)


def _slope(y_ell):
    """slope of log2(y) vs ell (b=2^ell -> this is the exponent d in y ~ b^d)."""
    x = np.arange(len(y_ell))
    ly = np.log2(np.maximum(y_ell, 1e-9))
    return float(np.polyfit(x, ly, 1)[0])


def eta_per_feature(Ustars, ell_lo=ELL_FIT_LO):
    """eta_f = d_f - d_generic, d_f = slope of log2(beta_f)=log2(1/(1-U*_f)) vs ell over the COARSE half
    (ell>=ell_lo); d_generic = median over features (~0 = normal/noise baseline)."""
    F = Ustars.shape[1]
    beta_f = 1.0 / np.maximum(1.0 - Ustars, 1e-6)        # scales x F
    d_f = np.array([_slope(beta_f[ell_lo:, f]) for f in range(F)])
    d_generic = float(np.median(d_f))
    return d_f - d_generic, d_f, d_generic


def auroc(scores, labels):
    pos = scores[labels == 1]; neg = scores[labels == 0]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    r = pos[:, None]; n = neg[None, :]
    return float((np.sum(r > n) + 0.5 * np.sum(r == n)) / (r.size * n.size))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    return float((ra @ rb) / (np.sqrt(ra @ ra) * np.sqrt(rb @ rb) + 1e-12))


# =================== driver ===================
def main(mode):
    F = 18 if mode == "dev" else 30
    T = {"dev": 4000, "smoke": 12_000, "run": 50_000}[mode]
    L = 5 if mode == "dev" else 6
    print(f"=== D-cal-flow STEP 1 [{mode}]  F={F} K={K} T={T} scales b=1..{2**L} "
          f"M_SUB={M_SUB} M_SUP={M_SUP} SIGMA={SIGMA} ===", flush=True)

    Lq, anomalous, module_id = generate(GEN_SEED, T, F)
    n_anom = int(anomalous.sum()); n_norm = int(((module_id >= 0) & (anomalous == 0)).sum())
    n_noise = int((module_id < 0).sum())
    print(f"[plant] features: {n_norm} normal-module / {n_anom} anomalous-module / {n_noise} noise "
          f"(MOD_SIZE={MOD_SIZE})", flush=True)

    enc1 = make_encoder(A1, EMIT_SEED_1, F)
    O1 = encode(Lq, enc1, EMIT_SEED_1 * 7 + GEN_SEED)[0]       # ONE encoder (Step 1)

    topk = MOD_SIZE - 1
    B_BOOT = {"dev": 15, "smoke": 25, "run": 40}[mode]
    ells, Ws, beta, lam, g, Ustars = flow(O1, A1, L, topk)

    # ---------- gate (ii) FLOW ----------
    d_global = _slope(beta)
    beta_up = bool(np.all(np.diff(beta) > -1e-9))
    lam_dn = bool(np.all(np.diff(lam) < 1e-9))
    g_up = bool(np.all(np.diff(g) > -1e-9))
    print("\n--- gate (ii) FLOW (beta grows / lam shrinks / g monotone) ---", flush=True)
    print(f"  ell:    {ells}", flush=True)
    print(f"  beta:   {np.round(beta,3).tolist()}  grows={beta_up}", flush=True)
    print(f"  lam:    {np.round(lam,3).tolist()}  shrinks={lam_dn}", flush=True)
    print(f"  g:      {np.round(g,3).tolist()}  monotone-up={g_up}", flush=True)
    print(f"  fitted d (slope log2 beta vs ell) = {d_global:.3f}", flush=True)
    gate_ii = beta_up and lam_dn and g_up

    # ---------- gate (i) RECOVERY (rendered data coarse-grain recovers planted couplings) ----------
    planted = np.zeros((F, F))
    for i, j in combinations(range(F), 2):
        planted[i, j] = planted[j, i] = 1.0 if (module_id[i] >= 0 and module_id[i] == module_id[j]) else 0.0
    iu = np.triu_indices(F, 1)
    ell_star = L                                             # most coarse-grained scale (bias-corrected MI is reliable here)
    rec_curve = [spearman(Ws[e][iu], planted[iu]) for e in ells]
    rec_sp = rec_curve[ell_star]
    print("\n--- gate (i) RECOVERY (Spearman W(coarse-grained) vs planted coupling) ---", flush=True)
    print(f"  per-scale Spearman(W(ell), planted): {[round(x,3) for x in rec_curve]}", flush=True)
    print(f"  read at the coarsest scale ell*={ell_star} (b={2**ell_star}, N={T//2**ell_star} blocks): {rec_sp:.3f}  (>=0.7?)", flush=True)
    gate_i = rec_sp >= 0.7

    # ---------- gate (iii) eta IDENTIFIABLE + (iv) CEILING ----------
    eta, d_f, d_generic = eta_per_feature(Ustars)           # full-data point estimate
    # moving-block bootstrap CI: resample BOOT_BLOCK-length contiguous blocks with replacement to full length T
    # (preserves the super-regime structure; full-T per resample -> tight, correct CIs)
    nblk = max(2, T // BOOT_BLOCK) + 1
    rngb = np.random.default_rng(20260626)
    eta_bs = []
    for _ in range(B_BOOT):
        starts = rngb.integers(0, T - BOOT_BLOCK + 1, size=nblk)
        idx = (starts[:, None] + np.arange(BOOT_BLOCK)[None, :]).ravel()[:T]
        _, _, _, _, _, Us = flow(O1[idx], A1, L, topk)
        eta_bs.append(eta_per_feature(Us)[0])
    eta_bs = np.array(eta_bs)                                # B x F
    eta_lo = np.percentile(eta_bs, 2.5, axis=0)
    norm_mask = (module_id >= 0) & (anomalous == 0)
    eta_anom_med = float(np.median(eta[anomalous == 1]))
    eta_norm_med = float(np.median(eta[norm_mask]))
    eta_noise_med = float(np.median(eta[module_id < 0]))
    anom_lo = eta_lo[anomalous == 1]
    anom_ci_pos = bool(np.all(anom_lo > 0))                  # every anomalous feature's 2.5% CI excludes 0
    print("\n--- gate (iii) eta IDENTIFIABLE (~0 normal / >0 anomalous; CI stable) ---", flush=True)
    print(f"  median eta: anomalous={eta_anom_med:+.3f}  normal-module={eta_norm_med:+.3f}  noise={eta_noise_med:+.3f}", flush=True)
    print(f"  every anomalous feature CI_lo>0 : {anom_ci_pos}  (B={B_BOOT}; anom CI_lo range "
          f"[{anom_lo.min():+.3f},{anom_lo.max():+.3f}])", flush=True)
    gate_iii = (eta_anom_med > 0) and (abs(eta_norm_med) < eta_anom_med) and anom_ci_pos

    # CEILING: recover the anomalous-feature SET (AUROC) + the anomalous COUPLING GRAPH (precision), with correspondence
    ceil_auroc = auroc(eta, anomalous)
    # coupling-graph precision: top-E off-diag edges of W(coarse) vs planted anomalous edges
    anom_edges = [(i, j) for i, j in zip(*iu) if anomalous[i] == 1 and anomalous[j] == 1 and module_id[i] == module_id[j]]
    n_anom_edges = len(anom_edges)
    Wc = Ws[ell_star]
    order = np.argsort(-Wc[iu])
    topE = set((int(iu[0][o]), int(iu[1][o])) for o in order[:n_anom_edges])
    graph_prec = len(topE & set(anom_edges)) / max(n_anom_edges, 1)
    planted_density = n_anom_edges / (F * (F - 1) / 2)
    print("\n--- gate (iv) CEILING (eta-structure recovered WITH correspondence) ---", flush=True)
    print(f"  anomalous-SET AUROC(eta_f, label) = {ceil_auroc:.3f}  (>=0.90?)", flush=True)
    print(f"  anomalous-GRAPH precision @top-{n_anom_edges} = {graph_prec:.3f}  (>= planted density {planted_density:.3f}?)", flush=True)
    gate_iv = (ceil_auroc >= 0.90) and (graph_prec >= planted_density)

    # ---------- gate (v) NON-DEGENERACY ----------
    maxoff = float(np.max(Ws[ell_star][iu]))
    # perm-invariance of the coordinate-free piece (spectrum / beta) under feature relabeling
    pp = np.random.default_rng(123).permutation(F)
    Mc = block_mode(O1, A1, 2 ** ell_star)
    sp0 = np.sort(np.linalg.eigvalsh(norm_mi_matrix(Mc, A1)))
    spp = np.sort(np.linalg.eigvalsh(norm_mi_matrix(Mc[:, pp], A1)))
    perm_l2 = float(np.linalg.norm(sp0 - spp))
    print("\n--- gate (v) NON-DEGENERACY (no saturation; perm-invariant coordinate-free piece) ---", flush=True)
    print(f"  max off-diag W(coarse) = {maxoff:.3f}  (no saturation, <0.98?)", flush=True)
    print(f"  spectrum perm-invariance L2 = {perm_l2:.2e}  (<1e-9?)", flush=True)
    gate_v = (maxoff < 0.98) and (perm_l2 < 1e-9)

    # ---------- summary ----------
    gates = {"i_recovery": gate_i, "ii_flow": gate_ii, "iii_eta": gate_iii, "iv_ceiling": gate_iv, "v_nondeg": gate_v}
    allpass = all(gates.values())
    print("\n=== STEP-1 GATES ===", flush=True)
    for k_, v_ in gates.items():
        print(f"  {k_:14s}: {'PASS' if v_ else 'FAIL'}", flush=True)
    print(f"  -> {'ALL GATES PASS -- apparatus VALIDATED (Step-1 fork: proceed to Step 2 pre-reg)' if allpass else 'GATE FAIL -- smoke-amend the construction append-only (fork untouched) or record negative'}", flush=True)

    out = {"mode": mode, "F": F, "T": T, "L": L, "d_global": d_global,
           "beta": beta.tolist(), "lam": lam.tolist(), "g": g.tolist(),
           "recovery_spearman": rec_sp, "eta_median": {"anom": eta_anom_med, "norm": eta_norm_med, "noise": eta_noise_med},
           "anom_ci_pos": anom_ci_pos, "ceiling_auroc": ceil_auroc, "graph_prec": graph_prec,
           "planted_density": planted_density, "max_offdiag": maxoff, "perm_l2": perm_l2,
           "gates": gates, "all_pass": allpass, "rec_curve": [float(x) for x in rec_curve],
           "eta": eta.tolist(), "eta_lo": eta_lo.tolist(), "anomalous_label": anomalous.tolist()}
    json.dump(out, open(f"data/dcal_flow_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal_flow_{mode}.json", flush=True)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "run")
