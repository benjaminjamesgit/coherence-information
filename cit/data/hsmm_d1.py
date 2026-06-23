"""D1 substrate -- 3-state hidden semi-Markov generator (Metacoherence cross-domain, domain 1).

LOCKED v0.7.0 (pre_registration.md, 2026-06-23 amendment). The full-transparency
domain of the cross-domain (Metacoherence) program: a 3-state HSMM regime layer
with eight structured discrete emissions (alphabet 8). Five features carry one of
four coherence properties; three are distractors with skewed marginals but NO
structural coherence. The M5 feature-partition is exact by construction.

Properties (locked):
    f0          A  regime indicator      -- regime-conditional categorical
    f1          B  long-range coupling   -- g(f0,f2,f4 @ t-L), prob B_KEEP else uniform
    f2, f3      C  coalitional pair      -- additive mask: individually uniform, jointly recover regime
    f4          D  drift carrier         -- emission peaked at a slowly-drifting, regime-reset mode
    f5, f6, f7  -- distractors           -- uniform / Zipf(1.1) / low-frequency(0.6)

M5 partition (exact, by construction):
    coherence-bearing = {f0, f1, f2, f3, f4};  noise = {f5, f6, f7}

CRITICAL (load-bearing) -- coherence on D1 must be measured MARGINAL-RELATIVE.
The Zipf / low-frequency distractors carry low marginal entropy by design; a
uniform-baseline coherence measure mistakes that for coherence (the precise
failure D1 exists to catch). Every downstream proxy generalization measures
coherence relative to each feature's marginal, never against a uniform baseline.

Calibration target (marginal-relative MI, Metacoherence Sec 5.4):
    I_A = 0.76,  I_B = 0.46,  I_C = 0.34,  I_D = 0.58  (bits)
    max single-property share 0.356 < 0.40;  distractors structurally flat.

Determinism: each stream is a pure function of its seed (numpy default_rng only;
no global RNG, no Date/random). Bit-exact reproducible per seed.
"""

import numpy as np

# --- locked structure (do NOT change without a version bump + amendment) ---
ALPHABET = 8           # emission alphabet size (per feature)
N_FEATURES = 8         # f0..f7
N_STATES = 3           # HSMM regimes
MEAN_DWELL = 200       # negbinom sojourn mean
NB_R = 6               # negbinom dispersion (CV ~ 0.41)
T_DEFAULT = 50_000     # locked stream length (~250 sojourns)
N_REPLICATES = 20      # locked independent seeded streams
N_BUCKET = 8           # C-property mask buckets per sojourn period
B_LAG = 12             # B-property long-range lag (L)
B_KEEP = 0.35          # B-property coupling retention probability
DRIFT_STD = 0.10       # D-property drift random-walk step std
DRIFT_PEAK = 1.0       # D-property emission peaking
F0_SCALE = 1.7         # A-property regime-conditional logit scale
ZIPF_S = 1.1           # f6 distractor Zipf exponent
LOWFREQ_P = 0.6        # f7 distractor mode mass

REPLICATE_SEED_BASE = 7000
REPLICATE_SEEDS = tuple(REPLICATE_SEED_BASE + i for i in range(N_REPLICATES))

# M5 partition (exact, by construction)
COHERENCE_BEARING = (0, 1, 2, 3, 4)
NOISE = (5, 6, 7)

# feature -> property label (None for distractors)
FEATURE_PROPERTY = {0: "A", 1: "B", 2: "C", 3: "C", 4: "D", 5: None, 6: None, 7: None}


def _softmax_rows(M):
    M = M - M.max(axis=1, keepdims=True)
    E = np.exp(M)
    return E / E.sum(axis=1, keepdims=True)


def _sojourn_states(rng, T):
    """3-state HSMM regime path: negbinom dwells, equiprobable jumps to the two others."""
    p = NB_R / (NB_R + MEAN_DWELL)
    states = np.empty(T, dtype=np.int64)
    t = 0
    s = int(rng.integers(N_STATES))
    while t < T:
        d = int(rng.negative_binomial(NB_R, p)) + 1
        states[t:t + d] = s
        t += d
        s = (s + 1 + int(rng.integers(N_STATES - 1))) % N_STATES
    return states


def generate_stream(seed, T=T_DEFAULT):
    """Generate one D1 stream.

    Returns
    -------
    states : (T,) int64 array in [0, N_STATES)   -- hidden regime path
    obs    : (T, N_FEATURES) int64 array in [0, ALPHABET)  -- the eight emissions

    Pure function of (seed, T): bit-exact reproducible.
    """
    rng = np.random.default_rng(seed)

    # fixed-per-stream structure tables
    F0 = _softmax_rows(F0_SCALE * rng.standard_normal((N_STATES, ALPHABET)))     # A: regime emissions
    C_VAL = rng.integers(0, ALPHABET, size=(N_STATES, N_BUCKET))                 # C: additive mask
    F6 = 1.0 / (np.arange(1, ALPHABET + 1) ** ZIPF_S); F6 /= F6.sum()            # f6 Zipf marginal
    F7 = np.array([LOWFREQ_P] + [(1.0 - LOWFREQ_P) / (ALPHABET - 1)] * (ALPHABET - 1))  # f7 low-freq marginal
    g = rng.integers(0, ALPHABET, size=ALPHABET ** 3)                            # B: fixed coupling table

    states = _sojourn_states(rng, T)

    obs = np.zeros((T, N_FEATURES), dtype=np.int64)
    drift = 0.0
    arange_A = np.arange(ALPHABET)
    for ti in range(T):
        s = states[ti]
        if ti > 0 and states[ti] != states[ti - 1]:
            drift = 0.0                                   # D: re-center per regime entry
        drift += rng.normal(0.0, DRIFT_STD)
        obs[ti, 0] = rng.choice(ALPHABET, p=F0[s])        # f0  A
        bucket = (ti % MEAN_DWELL) * N_BUCKET // MEAN_DWELL
        f2 = int(rng.integers(ALPHABET))
        obs[ti, 2] = f2                                   # f2  C (uniform)
        obs[ti, 3] = (f2 + C_VAL[s, bucket]) % ALPHABET   # f3  C (masked)
        mode = int((np.tanh(0.4 * drift) + 1.0) / 2.0 * (ALPHABET - 1))
        p4 = _softmax_rows((-DRIFT_PEAK * (arange_A - mode) ** 2)[None])[0]
        obs[ti, 4] = rng.choice(ALPHABET, p=p4)           # f4  D
        obs[ti, 5] = rng.integers(ALPHABET)               # f5  distractor: uniform
        obs[ti, 6] = rng.choice(ALPHABET, p=F6)           # f6  distractor: Zipf
        obs[ti, 7] = rng.choice(ALPHABET, p=F7)           # f7  distractor: low-freq

    # f1  B: long-range coupling on (f0, f2, f4) at lag L
    for ti in range(T):
        if ti >= B_LAG and rng.random() < B_KEEP:
            key = (obs[ti - B_LAG, 0] * ALPHABET + obs[ti - B_LAG, 2]) * ALPHABET + obs[ti - B_LAG, 4]
            obs[ti, 1] = g[key]
        else:
            obs[ti, 1] = rng.integers(ALPHABET)

    return states, obs


def generate_replicates(T=T_DEFAULT, seeds=REPLICATE_SEEDS):
    """Yield (seed, states, obs) for each locked replicate seed."""
    for seed in seeds:
        states, obs = generate_stream(seed, T)
        yield seed, states, obs
