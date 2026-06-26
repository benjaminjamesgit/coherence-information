#!/usr/bin/env python3
"""D-cal-w-real (PROPER) -- v0.7.3 REAL-DOMAIN falsification of "w = its statistical base". SMOKE -> HOLD.

Pre-registered 2026-06-26 (pre_registration.md "v0.7.3 D-cal-w-real (PROPER)"). Supersedes the mis-specified prior
smoke (protein unordered -> temporal ladder meaningless; text window-position unit degenerate). Two REAL, NON-STATIONARY,
disjoint-prior SEQUENTIAL streams: A = literary English text (Moby Dick, Project Gutenberg); B = real genomic DNA (E.
coli K-12 U00096.3, NCBI). UNIT = PER-POSITION: each position t in the 1-D stream gets w_t (a real-compressor relevance)
and base_t (the LOCKED statistical ladder applied along the stream); the residual test is over the T positions.

LOCKED blind ladder (NEVER tuned): lagged pointwise self-MI at LAG_LADDER + order-M predictive info at ORDER_SET, along
the stream. Induced w = per-position greedy-LZ77 codelength (the LZ-family core of zstd; a real-compressor per-position
relevance, NOT the base). Structured-noise null = order-k Markov surrogate (preserve order-k, destroy beyond). Base =
statistical estimators ONLY. RE-BASE 2026-06-26 (pre_registration.md "D-cal-w-real RE-BASE"): the prior sparse 13-dim
ladder was a STRAWMAN base (LZ relevance lives at off-ladder distances/lengths the ladder cannot represent -> residual
guaranteed large). REPLACED by a FROZEN universal PPM-C base (max-order PPM_MAX_ORDER, full exclusions, order-(-1)
uniform) -- of LZ's representational class -- gated by a FAIRNESS check (mean PPM codelength ~= mean LZ codelength = same
entropy-rate class) so the per-position residual is an anti-strawman test. Real corpora FETCHED (data/*.txt, data/*.fasta
-- gitignored; source URLs recorded below). ASCII. Usage: python scripts/dcal_w_real.py [smoke]
"""
import sys, json, re, math
from collections import defaultdict
import numpy as np

sys.path.insert(0, ".")

# ---- LOCKED blind base ladder (pre-reg; NEVER tuned/enriched) ----
LAG_LADDER = (1, 2, 4, 8, 16, 32, 64, 128, 256)
ORDER_SET = (1, 2, 3, 4)
# structured-noise null order: pinned PER DOMAIN to the highest WELL-SAMPLED order so the surrogate actually
# PRESERVES order-k (text A=27 only samples up to order ~2 at smoke sizes; DNA A=4 samples order-4+). The locked
# ladder is UNCHANGED -- this is the null's k, "pinned in smoke" per the pre-reg; undersampled ladder orders stay
# in the base as a reported limitation.
MARKOV_K = {"TEXT": 2, "DNA": 4}
TEXT_URL = "https://www.gutenberg.org/files/2701/2701-0.txt"
# DNA: human chr22 region (repeat-rich = strong long-range structure for the SMB crack; E. coli was compact/near-
# stationary with little beyond-order-4 structure -> a low-power crack test, swapped out).
DNA_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_000022.11&rettype=fasta&seq_start=23000000&seq_stop=24200000"

# ---- FROZEN per-position universal statistical base: PPM-C (re-base 2026-06-26; replaces the strawman ladder) ----
# Anti-tautology pin: ONE frozen estimator of the per-position information content -log2 P(x_t | context), max-order
# pinned a priori. PPM-C escape (denom = total + distinct), FULL exclusions down the escape chain, order-(-1) uniform
# over the A - |excluded| remaining symbols. Captures arbitrary-order/long-range structure (a long matching context =
# a repeat -> confident low-codelength prediction, the statistical analog of LZ's match). NO compressor in the base.
PPM_MAX_ORDER = 24                                          # pinned a priori (raise to PPM_ORDER_CAP only if fairness forces)
PPM_ORDER_CAP = 32
PPM_HASH = ((2147483647, 1000003), (1000000007, 998997))   # two (modulus, base) lanes -> 62-bit collision-safe context key


# ================= corpora -> 1-D categorical streams =================
def load_text(path="data/text_corpus.txt"):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    # strip Project Gutenberg header/footer markers if present
    m = re.search(r"\*\*\* START OF .*?\*\*\*", raw)
    if m:
        raw = raw[m.end():]
    m = re.search(r"\*\*\* END OF .*?\*\*\*", raw)
    if m:
        raw = raw[:m.start()]
    clean = re.sub(" +", " ", re.sub("[^a-z ]+", " ", raw.lower()))
    return np.array([26 if c == " " else ord(c) - 97 for c in clean], dtype=np.int64), 27


def load_dna(path="data/dna_human.fasta"):
    lines = open(path).read().splitlines()
    seq = "".join(l.strip().upper() for l in lines if not l.startswith(">"))
    mp = {"A": 0, "C": 1, "G": 2, "T": 3}
    return np.array([mp[c] for c in seq if c in mp], dtype=np.int64), 4   # human chr22 region (0% N)


# ================= LOCKED per-position statistical base (NO compressor) =================
def _log2(x):
    return np.log2(np.maximum(x, 1e-300))


def lagged_pmi(s, A, L):
    """per-position pointwise self-MI at lag L: log2[ P(s[t],s[t-L]) / (P(s[t]) P(s[t-L])) ]; 0 for t<L."""
    T = len(s)
    out = np.zeros(T)
    if L >= T:
        return out
    a, b = s[:-L], s[L:]                                  # s[t-L], s[t]
    joint = np.bincount(a * A + b, minlength=A * A).reshape(A, A).astype(float)
    pj = joint / joint.sum()
    pa = pj.sum(1); pb = pj.sum(0)
    pmi = _log2(pj) - _log2(pa[:, None]) - _log2(pb[None, :])
    out[L:] = pmi[a, b]
    return out


def predictive_info(s, A, M):
    """per-position predictive info at order M: log2[ P(s[t]|s[t-M..t-1]) / P(s[t]) ]; 0 for t<M."""
    T = len(s)
    out = np.zeros(T)
    if M >= T:
        return out
    pm = np.bincount(s, minlength=A).astype(float); pm /= pm.sum()
    ctx = np.zeros(T - M, dtype=np.int64)
    for m in range(M):
        ctx = ctx * A + s[m:T - M + m]
    cur = s[M:]
    jc = defaultdict(lambda: np.zeros(A))
    for c, x in zip(ctx, cur):
        jc[c][x] += 1
    cprob = {c: v / v.sum() for c, v in jc.items()}
    out[M:] = np.array([_log2(cprob[c][x]) - _log2(pm[x]) for c, x in zip(ctx, cur)])
    return out


def b_blind(s, A):
    """LOCKED blind base, per position: [lagged pmi @each LAG] + [predictive info @each ORDER]; z-scored columns.
    Returns (scalar z-sum, component matrix T x 13)."""
    cols = [lagged_pmi(s, A, L) for L in LAG_LADDER] + [predictive_info(s, A, M) for M in ORDER_SET]
    def z(v):
        sd = v.std()
        return (v - v.mean()) / sd if sd > 1e-9 else v * 0.0
    comps = np.column_stack([z(c) for c in cols])
    return comps.sum(1), comps


def b_sametime(s, A):
    """artifact baseline: the narrow same-time/order-1 base (order-1 predictive info only)."""
    return predictive_info(s, A, 1)


# ================= induced w: per-position greedy-LZ77 codelength (REAL compressor) =================
def lz77_codelength(s, A, window=8192):
    """greedy LZ77 (the LZ core of zstd): per-position codelength (bits). Matched positions (long-range repeats a
    fixed-order base misses) get low amortized bits; literals get log2(A). Integer k-gram hash, recent-position chains."""
    T = len(s)
    K = max(4, int(np.ceil(np.log(20000.0) / np.log(A))))    # k-gram selectivity ~10^4-10^5 distinct keys
    if T < K + 2:
        return np.full(T, np.log2(A))
    pw = A ** np.arange(K - 1, -1, -1, dtype=np.int64)        # k-gram -> int key
    keys = np.zeros(T - K + 1, dtype=np.int64)
    for j in range(K):
        keys += s[j:T - K + 1 + j] * pw[j]
    table = defaultdict(list)
    cl = np.zeros(T)
    lit = np.log2(A)
    i = 0
    while i < T:
        best = 0; bp = -1
        if i <= T - K:
            for p in table.get(int(keys[i]), ())[-12:]:      # recent candidates
                if i - p > window:
                    continue
                m = 0
                while i + m < T and s[p + m] == s[i + m] and m < 4096:
                    m += 1
                if m > best:
                    best, bp = m, p
        if best >= K:
            per = (np.log2(window) + np.log2(best)) / best     # amortized match-token cost
            cl[i:i + best] = per
            for j in range(i, min(i + best, T - K + 1)):
                table[int(keys[j])].append(j)
            i += best
        else:
            cl[i] = lit
            if i <= T - K:
                table[int(keys[i])].append(i)
            i += 1
    return cl


# ================= FROZEN per-position statistical base: PPM-C (NO compressor) =================
def ppm_codelength(s, A, max_order=PPM_MAX_ORDER):
    """FROZEN PPM-C per-position codelength = -log2 P(x_t | context) in bits. Escape method C (denom = total + distinct
    seen symbols), FULL exclusions accumulated down the escape chain, order-(-1) = uniform over A - |excluded| remaining
    symbols. Two-lane rolling-hash context keys (collision-safe 62-bit). Explicit -log2 P model -- NOT a compressor."""
    T = len(s)
    out = np.empty(T)
    model = [dict() for _ in range(max_order + 1)]              # model[d][ctx_key] = {symbol: count}
    (P1, B1), (P2, B2) = PPM_HASH
    Bpow1 = [pow(B1, d, P1) for d in range(max_order + 1)]
    Bpow2 = [pow(B2, d, P2) for d in range(max_order + 1)]
    h1 = [0] * (max_order + 1)                                  # h*[d] = rolling hash of the length-d suffix ending at t-1
    h2 = [0] * (max_order + 1)
    log2 = math.log2
    sl = s.tolist()
    for t in range(T):
        x = sl[t]
        dmax = t if t < max_order else max_order
        bits = 0.0
        excluded = None                                        # lazily-built exclusion set (None until first escape)
        coded = False
        for d in range(dmax, -1, -1):
            counts = model[d].get(h1[d] * P2 + h2[d]) if d > 0 else model[0].get(0)
            if not counts:
                continue
            if excluded is None:
                tot = 0
                for c in counts.values():
                    tot += c
                distinct = len(counts)
                cx = counts.get(x, 0)
            else:
                tot = 0; distinct = 0; cx = 0
                for sym, c in counts.items():
                    if sym not in excluded:
                        tot += c; distinct += 1
                        if sym == x:
                            cx = c
                if distinct == 0:
                    continue
            denom = tot + distinct
            if cx > 0:
                bits += -log2(cx / denom)
                coded = True
                break
            bits += -log2(distinct / denom)                    # PPM-C escape
            if excluded is None:
                excluded = set(counts.keys())
            else:
                excluded.update(counts.keys())
        if not coded:
            remaining = A - (len(excluded) if excluded is not None else 0)
            bits += log2(remaining if remaining >= 1 else 1)   # order-(-1) uniform
        out[t] = bits
        # ---- update the contexts we predicted from (orders 0..dmax) with the observed x ----
        for d in range(0, dmax + 1):
            key = (h1[d] * P2 + h2[d]) if d > 0 else 0
            m = model[d]
            cc = m.get(key)
            if cc is None:
                m[key] = {x: 1}
            else:
                cc[x] = cc.get(x, 0) + 1
        # ---- advance the rolling hashes to include x (length-d suffix now ends at t) ----
        for d in range(1, max_order + 1):
            drop = sl[t - d] if t - d >= 0 else 0
            h1[d] = (h1[d] * B1 + x - drop * Bpow1[d]) % P1
            h2[d] = (h2[d] * B2 + x - drop * Bpow2[d]) % P2
    return out


def w_residual(w, comps):
    X = np.column_stack([np.ones(len(w)), comps])
    coef, *_ = np.linalg.lstsq(X, w, rcond=None)
    return w - X @ coef


# ================= structured-noise null: order-k Markov surrogate =================
def markov_surrogate(s, A, k, seed=0):
    rng = np.random.default_rng(seed)
    n = len(s)
    cn = defaultdict(lambda: np.zeros(A))
    for t in range(k, n):
        cn[tuple(s[t - k:t])][s[t]] += 1
    cum = {c: np.cumsum(v / v.sum()) for c, v in cn.items()}
    out = list(s[:k]); u = rng.random(n)
    for t in range(k, n):
        c = tuple(out[-k:]); cc = cum.get(c)
        out.append(int(rng.integers(A)) if cc is None else int(np.searchsorted(cc, u[t])))
    return np.array(out, dtype=np.int64)


# ================= diagnostics =================
def entropy_rate_drift(s, A):
    t = len(s) // 3
    def er(x):
        j = np.bincount(x[:-1] * A + x[1:], minlength=A * A).reshape(A, A).astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            p = np.where(j > 0, j / np.maximum(j.sum(1, keepdims=True), 1e-12), 0.0)
            return -(j / j.sum() * np.where(p > 0, np.log2(np.maximum(p, 1e-12)), 0.0)).sum()
    return float(abs(er(s[:t]) - er(s[-t:])))


def composition_drift(s, A):
    """marginal (composition) drift first-vs-last third -- DNA's non-stationarity is COMPOSITIONAL (GC drift),
    which the ~flat entropy rate misses; text drifts in both."""
    t = len(s) // 3
    pa = np.bincount(s[:t], minlength=A) / t
    pb = np.bincount(s[-t:], minlength=A) / t
    return float(0.5 * np.abs(pa - pb).sum())


def cond_entropy(s, A, M):
    T = len(s)
    ctx = np.zeros(T - M, dtype=np.int64)
    for m in range(M):
        ctx = ctx * A + s[m:T - M + m]
    def ent(c):
        c = c[c > 0].astype(float); p = c / c.sum(); return -(p * np.log2(p)).sum()
    return ent(np.bincount(ctx * A + s[M:])) - ent(np.bincount(ctx))


def rank(x):
    return np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)


def spearman(x, y):
    if np.std(x) < 1e-9 or np.std(y) < 1e-9:
        return float("nan")
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


# ================= driver =================
def run_domain(name, s, A, url, markov_k):
    print(f"\n========== DOMAIN {name}  (T={len(s)} stream, alphabet A={A}; {url}) ==========", flush=True)

    # ---- gate (i) REAL + NON-STATIONARY (entropy-rate OR composition drift) ----
    drift = entropy_rate_drift(s, A)
    cdrift = composition_drift(s, A)
    print(f"--- gate (i) CORPUS REAL + NON-STATIONARY ---", flush=True)
    print(f"  entropy-rate drift={drift:.4f}  composition(marginal) drift={cdrift:.4f}  (>0 = non-stationary; magnitude reported for review)", flush=True)
    gate_i = (drift > 0.002) or (cdrift > 0.002)   # detectable non-stationarity (the SMB-crack-relevant LONG-RANGE structure is gate iii's destroyed-gap)

    # ---- gate (iv) base computable (FROZEN PPM-C) ----
    print(f"--- gate (iv) base computable (FROZEN PPM-C, max-order {PPM_MAX_ORDER}) ---", flush=True)
    w = lz77_codelength(s, A)
    base = ppm_codelength(s, A)
    gate_iv = bool(np.isfinite(base).all()) and bool(np.isfinite(w).all())
    print(f"    base finite={gate_iv}  mean(base)={base.mean():.3f} bits  std(base)={base.std():.3f}", flush=True)

    # ---- FAIRNESS GATE (re-base; make-or-break, both directions: same entropy-rate class) ----
    mean_w, mean_base = float(w.mean()), float(base.mean())
    fair_d = abs(mean_base - mean_w)
    gate_fair = fair_d < 0.15
    print(f"--- FAIRNESS GATE (mean PPM ~= mean LZ; if mean(base)>>mean(w) raise order to cap {PPM_ORDER_CAP}) ---", flush=True)
    print(f"  mean(w LZ)={mean_w:.3f}  mean(base PPM)={mean_base:.3f}  |d|={fair_d:.3f} (<0.15?) -> {gate_fair}", flush=True)

    # ---- gate (ii) UNITS POWERED (per-position w + base non-degenerate; residual not flat) ----
    wr = w_residual(w, base[:, None])
    r2 = 1.0 - np.var(wr) / max(np.var(w), 1e-12)
    sp_base = spearman(w, base)
    sp_same = spearman(w, b_sametime(s, A))
    gate_ii = (np.std(w) > 1e-3) and (np.std(wr) > 1e-3) and (np.std(base) > 1e-3)
    print(f"--- gate (ii) UNITS POWERED ---", flush=True)
    print(f"  std(w)={np.std(w):.4f} std(base)={np.std(base):.4f} std(w_resid)={np.std(wr):.4f}  R^2(w on base)={r2:.3f}  -> {gate_ii}", flush=True)
    print(f"  Spearman(w,base PPM)={sp_base:+.3f}  vs  Spearman(w,b_sametime order-1)={sp_same:+.3f}", flush=True)

    # ---- gate (iii) NULL VALIDITY ----
    snull = markov_surrogate(s, A, markov_k, seed=1)
    marg_tv = float(0.5 * np.abs(np.bincount(s, minlength=A) / len(s) - np.bincount(snull, minlength=A) / len(snull)).sum())
    ce_k_real, ce_k_null = cond_entropy(s, A, markov_k), cond_entropy(snull, A, markov_k)
    ce_hi_real, ce_hi_null = cond_entropy(s, A, markov_k + 2), cond_entropy(snull, A, markov_k + 2)
    w_null = lz77_codelength(snull, A)
    cl_real, cl_null = float(w.mean()), float(w_null.mean())       # mean LZ codelength = inverse compressibility
    print(f"--- gate (iii) NULL VALIDITY (order-{markov_k} Markov surrogate) ---", flush=True)
    print(f"  marginal TV={marg_tv:.4f} (<0.02?)  | order-{markov_k} cond-entropy real={ce_k_real:.3f} null={ce_k_null:.3f} (|d|={abs(ce_k_real-ce_k_null):.3f}, matched <0.1?)", flush=True)
    print(f"  [destroyed beyond-k] order-{markov_k+2} cond-entropy real={ce_hi_real:.3f} null={ce_hi_null:.3f} (null higher = real has structure null lacks; gap={ce_hi_null-ce_hi_real:+.3f})", flush=True)
    print(f"  [LZ compressibility] mean codelength real={cl_real:.3f} null={cl_null:.3f} (real lower = more compressible; gap={cl_null-cl_real:+.3f} bits)", flush=True)
    gate_iii = (marg_tv < 0.02) and (abs(ce_k_real - ce_k_null) < 0.1) and ((ce_hi_null - ce_hi_real) > 0.005 or (cl_null - cl_real) > 0.005)

    # ---- LAYER-1 PREVIEW (NOT the fork; official run decides) ----
    base_null = ppm_codelength(snull, A)
    wr_null = w_residual(w_null, base_null[:, None])
    print(f"--- LAYER-1 PREVIEW (residual structure; the FORK is the official run) ---", flush=True)
    print(f"  [residual autocorr lag-1] real={np.corrcoef(wr[:-1], wr[1:])[0,1]:+.3f}  surrogate={np.corrcoef(wr_null[:-1], wr_null[1:])[0,1]:+.3f}  (real>>surrogate = beyond-base structure?)", flush=True)
    print(f"  [var(w_resid)] real={np.var(wr):.3e}  surrogate={np.var(wr_null):.3e}", flush=True)

    return {"name": name, "url": url, "T": len(s), "A": A, "drift": drift, "composition_drift": cdrift, "markov_k": markov_k,
            "gate_i_nonstationary": gate_i, "gate_ii_powered": gate_ii, "gate_iii_null_valid": gate_iii, "gate_iv_base": gate_iv,
            "gate_fair": gate_fair, "fair_d": float(fair_d), "mean_w": mean_w, "mean_base": mean_base,
            "r2_w_on_base": float(r2), "spearman_w_base": sp_base, "spearman_w_bsametime": sp_same,
            "marg_tv": marg_tv, "ce_k_gap": float(ce_k_real - ce_k_null), "ce_hi_gap": float(ce_hi_null - ce_hi_real),
            "lz_gap": float(cl_null - cl_real),
            "resid_autocorr_real": float(np.corrcoef(wr[:-1], wr[1:])[0, 1]),
            "resid_autocorr_null": float(np.corrcoef(wr_null[:-1], wr_null[1:])[0, 1])}


# ================= CLOSE: compressor-free longest-previous-match statistic (suffix array; NO coding) =================
AUTOCORR_LAGS = (1, 2, 4, 8, 16, 32)
BLOCK_SURR = 256                                            # repeat-preserving block-permutation block size (pinned)
CLOSE_K = {"TEXT": 2, "DNA": 8}                             # order-k Markov surprisal order, well-sampled per domain (pinned)


def suffix_array(s):
    """SA[r] = start position of the r-th smallest suffix. numpy prefix-doubling (O(n log n))."""
    s = np.asarray(s, dtype=np.int64)
    n = len(s)
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    _, rank = np.unique(s, return_inverse=True)
    rank = rank.astype(np.int64)
    k = 1
    order = np.argsort(rank, kind="stable")
    while True:
        rank_k = np.full(n, -1, dtype=np.int64)
        if k < n:
            rank_k[:n - k] = rank[k:]
        order = np.lexsort((rank_k, rank))
        diff = (rank[order[1:]] != rank[order[:-1]]) | (rank_k[order[1:]] != rank_k[order[:-1]])
        new_rank = np.empty(n, dtype=np.int64)
        new_rank[order[0]] = 0
        new_rank[order[1:]] = np.cumsum(diff)
        rank = new_rank
        if int(rank.max()) == n - 1:
            break
        k *= 2
    return order


def kasai_lcp(s, sa):
    """lcp[r] = lcp(SA[r-1], SA[r]) (lcp[0]=0); plus rank = inverse(SA). Kasai O(n)."""
    sl = np.asarray(s, dtype=np.int64).tolist()
    n = len(sl)
    rank = np.empty(n, dtype=np.int64)
    rank[sa] = np.arange(n)
    sa_l = sa.tolist(); rk = rank.tolist()
    lcp = np.zeros(n, dtype=np.int64)
    h = 0
    for i in range(n):
        r = rk[i]
        if r > 0:
            j = sa_l[r - 1]
            while i + h < n and j + h < n and sl[i + h] == sl[j + h]:
                h += 1
            lcp[r] = h
            if h > 0:
                h -= 1
        else:
            h = 0
    return lcp, rank


def _build_rmq(lcp):
    n = len(lcp)
    table = [lcp.astype(np.int32)]
    j = 1
    while (1 << j) <= n:
        prev = table[-1]; half = 1 << (j - 1)
        table.append(np.minimum(prev[:n - (1 << j) + 1], prev[half:n - half + 1]))
        j += 1
    return table


def longest_previous_match(s):
    """L_t = length of the longest factor starting at t that also occurs starting EARLIER (start < t); Dist_t = t minus
    that earlier start. Pure suffix-array combinatorial statistic -- NO coding, NO probability model. Crochemore-Ilie
    LPF: nearest smaller SA-value neighbor on each side (prev/next-smaller) + RMQ over the adjacent-LCP array."""
    n = len(s)
    L = np.zeros(n, dtype=np.int64)
    Dist = np.zeros(n, dtype=np.int64)
    if n <= 1:
        return L, Dist
    sa = suffix_array(s)
    lcp, _ = kasai_lcp(s, sa)
    table = _build_rmq(lcp)
    sa_l = sa.tolist()
    psv = [-1] * n; nsv = [n] * n
    st = []
    for r in range(n):                                     # previous-smaller SA-value (nearest earlier-starting suffix above)
        v = sa_l[r]
        while st and sa_l[st[-1]] > v:
            st.pop()
        psv[r] = st[-1] if st else -1
        st.append(r)
    st = []
    for r in range(n - 1, -1, -1):                         # next-smaller SA-value (nearest earlier-starting suffix below)
        v = sa_l[r]
        while st and sa_l[st[-1]] > v:
            st.pop()
        nsv[r] = st[-1] if st else n
        st.append(r)

    def rmq(l, r):
        if l > r:
            return 0
        j = (r - l + 1).bit_length() - 1
        a = table[j]
        return int(min(a[l], a[r - (1 << j) + 1]))

    for r in range(n):
        p = sa_l[r]
        bestL = 0; bestpos = -1
        pu = psv[r]
        if pu != -1:
            lu = rmq(pu + 1, r)
            if lu > bestL:
                bestL = lu; bestpos = sa_l[pu]
        nu = nsv[r]
        if nu != n:
            ld = rmq(r + 1, nu)
            if ld > bestL or (ld == bestL and bestpos != -1 and (p - sa_l[nu]) < (p - bestpos)):
                bestL = ld; bestpos = sa_l[nu]
        L[p] = bestL
        if bestL > 0 and bestpos != -1:
            Dist[p] = p - bestpos
    return L, Dist


def markov_surprisal(s, A, k, alpha=1.0):
    """S_t = -log2 P_k(x_t | x_{t-k..t-1}); Laplace add-alpha, whole-sequence MLE counts. A count model -- NO compressor."""
    n = len(s)
    S = np.zeros(n)
    if k >= n:
        return S
    ctx = np.zeros(n - k, dtype=np.int64)
    for m in range(k):
        ctx = ctx * A + s[m:n - k + m]
    cur = s[k:]
    cnt = defaultdict(lambda: np.zeros(A))
    cl = ctx.tolist(); xl = cur.tolist()
    for c, x in zip(cl, xl):
        cnt[c][x] += 1
    out = np.empty(n - k)
    for idx, (c, x) in enumerate(zip(cl, xl)):
        v = cnt[c]
        out[idx] = -math.log2((v[x] + alpha) / (v.sum() + A * alpha))
    S[k:] = out
    return S


def block_permute(s, B, seed=0):
    """repeat-preserving surrogate: shuffle length-B blocks -- keeps the block multiset (local repeats), destroys
    long-range placement of repeats beyond B."""
    rng = np.random.default_rng(seed)
    n = len(s); nb = n // B
    if nb < 2:
        return np.array(s, dtype=np.int64)
    head = np.asarray(s[:nb * B], dtype=np.int64).reshape(nb, B)
    out = head[rng.permutation(nb)].reshape(-1)
    return np.concatenate([out, np.asarray(s[nb * B:], dtype=np.int64)])


def close_features(s, A, k):
    """F = [L_t, log2(Dist_t+1), S_t, 1(L_t==0)] -- pinned compressor-free statistics."""
    L, Dist = longest_previous_match(s)
    S = markov_surprisal(s, A, k)
    F = np.column_stack([L.astype(float), np.log2(Dist + 1.0), S, (L == 0).astype(float)])
    return F, L, S


def decompose(w, F):
    X = np.column_stack([np.ones(len(w)), F])
    coef, *_ = np.linalg.lstsq(X, w, rcond=None)
    r = w - X @ coef
    r2 = 1.0 - np.var(r) / max(np.var(w), 1e-12)
    return r, float(r2), coef


def autocorr(x, lags):
    x = x - x.mean()
    v = float(np.dot(x, x))
    return {int(L): (float(np.dot(x[:-L], x[L:]) / v) if (0 < L < len(x) and v > 0) else float("nan")) for L in lags}


def _close_pipeline(s, A, k):
    """full per-condition pipeline: w (LZ) -> features -> decomposition -> residual."""
    w = lz77_codelength(s, A)
    F, L, S = close_features(s, A, k)
    r, r2, coef = decompose(w, F)
    return {"w": w, "F": F, "L": L, "r": r, "r2": r2, "coef": coef}


def run_close_domain(name, s, A, k, url):
    print(f"\n========== CLOSE DOMAIN {name}  (T={len(s)} stream, A={A}, Markov k={k}; {url}) ==========", flush=True)
    real = _close_pipeline(s, A, k)
    w, r, r2 = real["w"], real["r"], real["r2"]
    sp = spearman(w, -real["L"].astype(float))
    print("--- readout (1) DECOMPOSITION: how much of w is the sequence's own match/Markov statistics ---", flush=True)
    print(f"  R^2(w on F=[L,logD,S,lit])={r2:.4f}   Spearman(w, -L)={sp:+.4f}", flush=True)
    print(f"  OLS coef [intercept,L,logD,S,lit]={np.array2string(real['coef'], precision=4, floatmode='fixed')}", flush=True)

    print("--- readout (2) RESIDUAL FORK: structure of r real vs matched-statistics nulls ---", flush=True)
    nulls = {"markov": markov_surrogate(s, A, k, seed=1), "block": block_permute(s, BLOCK_SURR, seed=1)}
    rows = {"real": (r2, np.var(r), autocorr(r, AUTOCORR_LAGS))}
    for label, ss in nulls.items():
        nd = _close_pipeline(ss, A, k)
        rows[label] = (nd["r2"], np.var(nd["r"]), autocorr(nd["r"], AUTOCORR_LAGS))
    for label in ("real", "markov", "block"):
        rr2, vr, ac = rows[label]
        acs = " ".join(f"L{L}={ac[L]:+.3f}" for L in AUTOCORR_LAGS)
        print(f"  {label:7s}: R^2={rr2:.4f}  var(r)={vr:.4e}  autocorr[{acs}]", flush=True)
    vreal = rows["real"][1]
    print(f"  -> var(r) ratios real/markov={vreal/max(rows['markov'][1],1e-12):.2f}x  real/block={vreal/max(rows['block'][1],1e-12):.2f}x "
          f"(>>1 = residual MORE structured than the matched null = reopen signal; ~1 = deflationary)", flush=True)

    print("--- readout (3) ROBUSTNESS: per-half stability ---", flush=True)
    h = len(s) // 2
    for hi, ss in (("half1", s[:h]), ("half2", s[h:])):
        hd = _close_pipeline(np.asarray(ss, dtype=np.int64), A, k)
        print(f"  {hi}: R^2={hd['r2']:.4f}  var(r)={np.var(hd['r']):.4e}", flush=True)
    if name == "TEXT":
        print("  Markov-order cross-check (residual vs order K; does var(r) shrink as K grows?):", flush=True)
        for kk in (1, 2, 4, 8):
            Fk = np.column_stack([real["F"][:, 0], real["F"][:, 1], markov_surprisal(s, A, kk), real["F"][:, 3]])
            rk, r2k, _ = decompose(w, Fk)
            print(f"    K={kk}: R^2={r2k:.4f}  var(r)={np.var(rk):.4e}", flush=True)

    return {"name": name, "url": url, "T": len(s), "A": A, "k": k, "r2": r2, "spearman_w_negL": sp,
            "var_r_real": float(vreal), "var_r_markov": float(rows["markov"][1]), "var_r_block": float(rows["block"][1]),
            "ratio_real_markov": float(vreal / max(rows["markov"][1], 1e-12)),
            "ratio_real_block": float(vreal / max(rows["block"][1], 1e-12)),
            "autocorr_real": rows["real"][2], "autocorr_markov": rows["markov"][2], "autocorr_block": rows["block"][2]}


def run_close():
    print("=== D-cal-w-real CLOSE  (compressor-free longest-previous-match decomposition; FULL corpora) ===", flush=True)
    st, At = load_text()
    sd, Ad = load_dna()
    rt = run_close_domain("TEXT", st, At, CLOSE_K["TEXT"], TEXT_URL)
    rd = run_close_domain("DNA", sd, Ad, CLOSE_K["DNA"], DNA_URL)
    print("\n=== CLOSE FORK SUMMARY ===", flush=True)
    for r in (rt, rd):
        print(f"  {r['name']:5s}: R^2(w on F)={r['r2']:.4f}  Spearman(w,-L)={r['spearman_w_negL']:+.4f}  "
              f"var(r) real/markov={r['ratio_real_markov']:.2f}x real/block={r['ratio_real_block']:.2f}x", flush=True)
    print("  -> deflationary CONFIRMED if w is substantially decomposed by F AND var(r)/autocorr(r) real ~ matched null;", flush=True)
    print("     REOPEN if residual structure real >> the matched (esp. block-permute) null. HOLD for Benjamin's read.", flush=True)
    json.dump({"text": rt, "dna": rd}, open("data/dcal_w_real_close.json", "w"), indent=2, default=float)
    print("\nsaved data/dcal_w_real_close.json", flush=True)


def main(mode):
    # PPM-C is pure-Python per-position; smoke subsamples keep both domains tractable while powering order-4 sampling
    # and preserving non-stationarity (DNA contiguous slice spans GC drift).
    SUB_T_TEXT = 100000 if mode == "smoke" else 300000
    SUB_T_DNA = 250000 if mode == "smoke" else 600000
    print(f"=== D-cal-w-real RE-BASE SMOKE [{mode}]  per-position unit; FROZEN PPM-C base (max-order {PPM_MAX_ORDER}); null=order-k Markov ===", flush=True)
    st, At = load_text(); st = st[:SUB_T_TEXT]
    sd, Ad = load_dna(); sd = sd[:SUB_T_DNA]               # contiguous chr22 slice (still spans compositional drift)
    rt = run_domain("TEXT", st, At, TEXT_URL, MARKOV_K["TEXT"])
    rd = run_domain("DNA", sd, Ad, DNA_URL, MARKOV_K["DNA"])

    print("\n=== SMOKE GATE SUMMARY ===", flush=True)
    for r in (rt, rd):
        allg = all([r["gate_i_nonstationary"], r["gate_ii_powered"], r["gate_iii_null_valid"], r["gate_iv_base"], r["gate_fair"]])
        print(f"  {r['name']:5s}: nonstationary={r['gate_i_nonstationary']} powered={r['gate_ii_powered']} "
              f"null-valid={r['gate_iii_null_valid']} base={r['gate_iv_base']} FAIR={r['gate_fair']} -> ALL={allg}  | "
              f"meanW={r['mean_w']:.3f} meanBase={r['mean_base']:.3f} |d|={r['fair_d']:.3f}  R^2(w,base)={r['r2_w_on_base']:.3f}", flush=True)
    print("  -> HOLD for Benjamin (FAIRNESS gate is the make-or-break re-base check; the frozen PPM-C base + the", flush=True)
    print("     blind-fork are NEVER tuned post-hoc; the Layer-1 residual fork is the OFFICIAL run).", flush=True)
    json.dump({"text": rt, "dna": rd}, open(f"data/dcal_w_real_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal_w_real_{mode}.json", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if mode == "close":
        run_close()
    else:
        main(mode)
