"""v0.7.1 R1 (persistence prediction) on D1 -- the calibration tier.

Pre-registered: pre_registration.md, the 2026-06-24 v0.7.1 R1 entries (the original
lock + the build-time amendment). D1's regime path is EMISSION-INDEPENDENT
(_sojourn_states draws pure negbinom dwells + uniform jumps, fixed before emission),
so the Metacoherence Sec 5.4 drift->transition coupling is NOT instantiated and D1
"persistence" reduces to REGIME-INFERENCE structure -- A-dominated, necessary-not-
sufficient (the load-bearing R1 is D2/D3). So D1 R1 is INSTRUMENT-CALIBRATION.

PRIMARY measure (decoder-free, estimator-neutral): the SUSTAINED marginal-relative
log-likelihood-cost MAGNITUDE of corrupting one feature's emission channel,

    persistence_cost(f, seed) = mean over t in [PERTURB_ONSET, T] of
        ( coh_loglik(obs_unperturbed_t, f) - coh_loglik(obs_perturbed_f_t, f) )

    coh_loglik(x, f) at t = log P_cond[t, f, x] - log P_marg[f, x]

where P_cond is the true per-step emission distribution (regime path + the feature's
OWN latents, other features marginalized -- so A and D show structure, while the
relational B and coalitional C are per-feature-invisible, matching the coverage map)
and P_marg is the feature's empirical marginal. Per-(K,A) cell Cohen's d on the
median-w high/low feature split; B=1000 bootstrap over the 20 replicate seeds.

The locked generate_stream is NOT modified: stream_with_emission_dists re-runs the
SAME generation bit-exactly (guard test) and additionally exposes the per-step
emission distributions. ASCII-only; deterministic (numpy default_rng only).
"""

import numpy as np

from cit.data.hsmm_d1 import (
    generate_stream,
    _softmax_rows,
    _sojourn_states,
    ALPHABET,
    N_FEATURES,
    N_STATES,
    MEAN_DWELL,
    N_BUCKET,
    B_LAG,
    B_KEEP,
    DRIFT_STD,
    DRIFT_PEAK,
    F0_SCALE,
    ZIPF_S,
    LOWFREQ_P,
    T_DEFAULT,
    REPLICATE_SEEDS,
    FEATURE_PROPERTY,
    COHERENCE_BEARING,
    NOISE,
)

# --- locked R1 constants (pre_registration.md 2026-06-24 v0.7.1) ---
PERTURB_ALPHA = 0.3          # convex-uniform mix magnitude
PERTURB_ONSET = 25_000       # T // 2
PERTURB_SEED = 0             # perturbation RNG
R1_BOOTSTRAP_SEED = 0        # bootstrap RNG
N_BOOTSTRAP = 1000           # B (source Sec 8.7 / App C.3)
_EPS = 1e-12                 # categorical log-prob floor

# pass thresholds (source Sec 8.7) -- provisional at the slice (Bonferroni at capstone)
R1_D_MIN = 0.5
R1_CI_MIN = 0.3
R1_P_MAX = 0.01

PROXIES = ("K1", "K2", "K3", "K4", "K5")
ABLATIONS = ("A1", "A2", "A3")


# ---------------------------------------------------------------------------
# Additive sibling generator: re-runs the locked generation bit-exactly and
# exposes the true per-step per-feature emission distributions.
# ---------------------------------------------------------------------------
def stream_with_emission_dists(seed, T=T_DEFAULT):
    """Re-run the locked D1 generation EXACTLY, returning (states, obs, P).

    P[t, f, :] is the per-feature emission distribution used at step t under the
    "per-state + own-latents" reading (other features marginalized):
        f0 A : F0[states[t]]          (regime-conditional categorical)
        f4 D : p4[t]                  (per-step drift mode -- its OWN latent)
        f6   : F6 (Zipf marginal)     f7 : F7 (low-freq marginal)
        f1 B : uniform   f2,f3 C : uniform   f5 : uniform
    (B is lag-coupled to OTHER features and C is a coalition with the sibling; a
    per-feature measure marginalizes those, so their per-state dist is uniform.)

    Bit-exact: obs equals generate_stream(seed, T)[1] (guarded by a test). The
    locked generate_stream is untouched -- this duplicates its loop additively.
    """
    rng = np.random.default_rng(seed)

    F0 = _softmax_rows(F0_SCALE * rng.standard_normal((N_STATES, ALPHABET)))
    C_VAL = rng.integers(0, ALPHABET, size=(N_STATES, N_BUCKET))
    F6 = 1.0 / (np.arange(1, ALPHABET + 1) ** ZIPF_S); F6 /= F6.sum()
    F7 = np.array([LOWFREQ_P] + [(1.0 - LOWFREQ_P) / (ALPHABET - 1)] * (ALPHABET - 1))
    g = rng.integers(0, ALPHABET, size=ALPHABET ** 3)

    states = _sojourn_states(rng, T)

    obs = np.zeros((T, N_FEATURES), dtype=np.int64)
    P = np.zeros((T, N_FEATURES, ALPHABET), dtype=np.float64)
    unif = np.full(ALPHABET, 1.0 / ALPHABET)
    drift = 0.0
    arange_A = np.arange(ALPHABET)
    for ti in range(T):
        s = states[ti]
        if ti > 0 and states[ti] != states[ti - 1]:
            drift = 0.0
        drift += rng.normal(0.0, DRIFT_STD)
        obs[ti, 0] = rng.choice(ALPHABET, p=F0[s])
        P[ti, 0] = F0[s]
        bucket = (ti % MEAN_DWELL) * N_BUCKET // MEAN_DWELL
        f2 = int(rng.integers(ALPHABET))
        obs[ti, 2] = f2
        P[ti, 2] = unif
        obs[ti, 3] = (f2 + C_VAL[s, bucket]) % ALPHABET
        P[ti, 3] = unif
        mode = int((np.tanh(0.4 * drift) + 1.0) / 2.0 * (ALPHABET - 1))
        p4 = _softmax_rows((-DRIFT_PEAK * (arange_A - mode) ** 2)[None])[0]
        obs[ti, 4] = rng.choice(ALPHABET, p=p4)
        P[ti, 4] = p4
        obs[ti, 5] = rng.integers(ALPHABET)
        P[ti, 5] = unif
        obs[ti, 6] = rng.choice(ALPHABET, p=F6)
        P[ti, 6] = F6
        obs[ti, 7] = rng.choice(ALPHABET, p=F7)
        P[ti, 7] = F7

    for ti in range(T):
        if ti >= B_LAG and rng.random() < B_KEEP:
            key = (obs[ti - B_LAG, 0] * ALPHABET + obs[ti - B_LAG, 2]) * ALPHABET + obs[ti - B_LAG, 4]
            obs[ti, 1] = g[key]
        else:
            obs[ti, 1] = rng.integers(ALPHABET)
        P[ti, 1] = unif

    return states, obs, P


# ---------------------------------------------------------------------------
# Generative substrate perturbation (A1) -- RNG-preserving, single feature.
# ---------------------------------------------------------------------------
def _perturb_feature(obs, feature, alpha, onset, seed):
    """Corrupt ONLY `feature`'s channel from `onset`: w.p. alpha replace the emitted
    symbol with a uniform draw (the convex-uniform mix, structure-DEGRADING = R1, not
    R3's structure-preserving relabel). A dedicated perturbation rng keyed by
    (PERTURB_SEED, seed, feature) leaves the base stream -- states and every non-target
    feature -- BIT-IDENTICAL. Returns a fresh perturbed obs array.
    """
    obs_p = obs.copy()
    T = obs.shape[0]
    if onset >= T:
        return obs_p
    prng = np.random.default_rng([PERTURB_SEED, int(seed), int(feature)])
    n = T - onset
    coin = prng.random(n) < alpha
    repl = prng.integers(0, ALPHABET, size=n)
    seg = obs_p[onset:, feature].copy()
    seg[coin] = repl[coin]
    obs_p[onset:, feature] = seg
    return obs_p


def generate_perturbed_stream(seed, feature, alpha=PERTURB_ALPHA, onset=PERTURB_ONSET, T=T_DEFAULT):
    """(states, obs_perturbed): the locked base stream with ONLY `feature` corrupted
    from `onset` (convex-uniform mix). states + all non-target features bit-identical.
    """
    states, obs = generate_stream(seed, T)
    return states, _perturb_feature(obs, feature, alpha, onset, seed)


# ---------------------------------------------------------------------------
# The decoder-free measure: sustained marginal-relative log-likelihood cost.
# ---------------------------------------------------------------------------
def _logclip(p):
    return np.log(np.clip(p, _EPS, None))


def _coh_loglik(values, P, pmarg, feature, idx):
    """Per-step marginal-relative coherence log-lik of `feature` at the steps `idx`:
    log P_cond[t, feature, value] - log P_marg[feature, value]."""
    vals = values[idx]
    cond = _logclip(P[idx, feature, vals])
    marg = _logclip(pmarg[feature, vals])
    return cond - marg


def persistence_cost_table(seeds=REPLICATE_SEEDS, T=T_DEFAULT, alpha=PERTURB_ALPHA,
                           onset=PERTURB_ONSET):
    """(n_seeds, N_FEATURES) array of persistence_cost(feature, seed). Each stream is
    generated ONCE (estimator-agnostic); every feature is perturbed off the same base.
    """
    seeds = tuple(seeds)
    out = np.zeros((len(seeds), N_FEATURES), dtype=np.float64)
    for i, sd in enumerate(seeds):
        states, obs, P = stream_with_emission_dists(sd, T)
        pmarg = np.stack([
            np.bincount(obs[:, f], minlength=ALPHABET).astype(np.float64) / T
            for f in range(N_FEATURES)
        ])
        idx = np.arange(onset, T)
        for f in range(N_FEATURES):
            obs_p = _perturb_feature(obs, f, alpha, onset, sd)
            coh_un = _coh_loglik(obs[:, f], P, pmarg, f, idx)
            coh_pt = _coh_loglik(obs_p[:, f], P, pmarg, f, idx)
            out[i, f] = float(np.mean(coh_un - coh_pt))
    return out


# ---------------------------------------------------------------------------
# Effect size + bootstrap (numpy-only; no scipy).
# ---------------------------------------------------------------------------
def cohens_d(high, low):
    """Pooled-variance Cohen's d, (high - low). 0.0 if the pooled sd is degenerate."""
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    nh, nl = len(high), len(low)
    if nh < 2 or nl < 2:
        return 0.0
    vh, vl = np.var(high, ddof=1), np.var(low, ddof=1)
    sp2 = ((nh - 1) * vh + (nl - 1) * vl) / (nh + nl - 2)
    if sp2 <= 0.0:
        return 0.0
    return float((np.mean(high) - np.mean(low)) / np.sqrt(sp2))


def _split_costs(cost_rows, w_by_feature):
    """Median-w split of features into high/low, returned as pooled cost samples.
    cost_rows: (n_seeds, N_FEATURES). w_by_feature: {feature_idx -> w}. Returns
    (high_costs, low_costs) flattened over seeds x features-in-group."""
    feats = sorted(w_by_feature)
    wvals = np.array([w_by_feature[f] for f in feats])
    med = np.median(wvals)
    high_f = [f for f, wv in zip(feats, wvals) if wv > med]
    low_f = [f for f, wv in zip(feats, wvals) if wv <= med]
    high = cost_rows[:, high_f].reshape(-1)
    low = cost_rows[:, low_f].reshape(-1)
    return high, low, high_f, low_f


def _cell_verdict(cost_rows, w_by_feature, rng):
    """Per-(K,A) cell: Cohen's d on the median-w split + B=1000 bootstrap over seeds."""
    high, low, high_f, low_f = _split_costs(cost_rows, w_by_feature)
    d = cohens_d(high, low)
    n_seeds = cost_rows.shape[0]
    boots = np.empty(N_BOOTSTRAP, dtype=np.float64)
    for b in range(N_BOOTSTRAP):
        pick = rng.integers(0, n_seeds, size=n_seeds)
        cr = cost_rows[pick]
        bh = cr[:, high_f].reshape(-1)
        bl = cr[:, low_f].reshape(-1)
        boots[b] = cohens_d(bh, bl)
    ci_lo = float(np.percentile(boots, 2.5))
    ci_hi = float(np.percentile(boots, 97.5))
    p = float(np.mean(boots <= 0.0))
    return {
        "d": d,
        "ci95": (ci_lo, ci_hi),
        "p": p,
        "high_features": high_f,
        "low_features": low_f,
        "pass": bool(d > R1_D_MIN and ci_lo > R1_CI_MIN and p < R1_P_MAX),
    }


# ---------------------------------------------------------------------------
# Validation gate (the D1 calibration deliverable) + per-property diagnostic.
# ---------------------------------------------------------------------------
def per_property_diagnostic(cost_rows):
    """Mean persistence cost per feature (over seeds) + per-property aggregation.
    The expected calibration signature: A (f0) and D (f4) carry cost; the relational
    B and coalitional C and the distractors are per-feature ~0."""
    mean_cost = cost_rows.mean(axis=0)
    by_feature = {f: float(mean_cost[f]) for f in range(N_FEATURES)}
    by_property = {}
    for f, prop in FEATURE_PROPERTY.items():
        key = prop if prop is not None else "distractor"
        by_property.setdefault(key, []).append(float(mean_cost[f]))
    by_property = {k: float(np.mean(v)) for k, v in by_property.items()}
    return {"by_feature": by_feature, "by_property": by_property}


def validation_gate(cost_rows, tol_distractor=0.05):
    """The hard calibration gate. On a clean run the magnitude cost must (a) leave the
    distractors f5/f6/f7 at ~0 (marginal-relative correctness) and (b) put f0 (A) above
    every distractor. Returns a dict; `ok` is the conjunction. A failure is a HARD STOP
    (the likelihood computation is wrong), NOT a tuning prompt."""
    mean_cost = cost_rows.mean(axis=0)
    distractor_max = float(max(mean_cost[f] for f in NOISE))
    a_cost = float(mean_cost[0])
    order = sorted(range(N_FEATURES), key=lambda f: -mean_cost[f])
    return {
        "by_feature": {f: float(mean_cost[f]) for f in range(N_FEATURES)},
        "order_high_to_low": order,
        "f0_A_cost": a_cost,
        "distractor_max": distractor_max,
        "distractors_near_zero": bool(distractor_max <= tol_distractor),
        "A_above_distractors": bool(a_cost > distractor_max),
        "A_is_largest": bool(order[0] == 0),
        "ok": bool(distractor_max <= tol_distractor and a_cost > distractor_max),
    }


# ---------------------------------------------------------------------------
# Full R1 grid verdict (heavy: induces w per (K,A,seed) via compute_cell).
# ---------------------------------------------------------------------------
def compute_r1_run(seeds=REPLICATE_SEEDS, T=T_DEFAULT, proxies=PROXIES, ablations=ABLATIONS):
    """Run D1 R1 end-to-end: the (estimator-agnostic) cost table ONCE, then per-(K,A)
    Cohen's d on each cell's median-w split, aggregated as median-d + pass-count across
    the 15 cells. NO cross-estimator w-agreement anywhere (the spec guard). Heavy --
    driver/full-run only; the fast tests exercise the cost machinery directly.
    """
    from cit.metacoherence import compute_cell  # local import: avoid import cycle

    seeds = tuple(seeds)
    cost_rows = persistence_cost_table(seeds=seeds, T=T)
    rng = np.random.default_rng(R1_BOOTSTRAP_SEED)

    cells = {}
    for K in proxies:
        for A in ablations:
            w_rows = [compute_cell(K, A, seed=sd, T=T)["w"] for sd in seeds]
            # median-w split is per (cell, seed); pool the per-seed high/low costs
            highs, lows, hf, lf = [], [], None, None
            for i, w in enumerate(w_rows):
                wf = {int(f): float(v) for f, v in w.items()}
                feats = sorted(wf)
                med = np.median([wf[f] for f in feats])
                hi = [f for f in feats if wf[f] > med]
                lo = [f for f in feats if wf[f] <= med]
                highs.append(cost_rows[i, hi])
                lows.append(cost_rows[i, lo])
            high = np.concatenate(highs)
            low = np.concatenate(lows)
            d = cohens_d(high, low)
            # bootstrap over seeds (resample the per-seed high/low cost groups together)
            boots = np.empty(N_BOOTSTRAP, dtype=np.float64)
            n_seeds = len(seeds)
            for b in range(N_BOOTSTRAP):
                pick = rng.integers(0, n_seeds, size=n_seeds)
                bh = np.concatenate([highs[j] for j in pick])
                bl = np.concatenate([lows[j] for j in pick])
                boots[b] = cohens_d(bh, bl)
            ci_lo = float(np.percentile(boots, 2.5))
            p = float(np.mean(boots <= 0.0))
            cells[f"{K}x{A}"] = {
                "d": d,
                "ci95_lo": ci_lo,
                "p": p,
                "pass": bool(d > R1_D_MIN and ci_lo > R1_CI_MIN and p < R1_P_MAX),
            }

    ds = np.array([c["d"] for c in cells.values()])
    n_pass = int(sum(c["pass"] for c in cells.values()))
    return {
        "seeds": list(seeds),
        "T": T,
        "median_d": float(np.median(ds)),
        "pass_count": n_pass,
        "n_cells": len(cells),
        "cells": cells,
        "gate": validation_gate(cost_rows),
        "diagnostic": per_property_diagnostic(cost_rows),
    }
