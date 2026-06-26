#!/usr/bin/env python3
"""D-cal-w-real -- v0.7.3 REAL-DOMAIN falsification of "w = its statistical base". SMOKE ONLY -> HOLD.

Pre-registered 2026-06-26 (pre_registration.md "v0.7.3 D-cal-w-real PRE-REGISTRATION"). On REAL, non-stationary,
disjoint-prior data (A = protein MSA; B = text corpus) does the zstd-compression-induced weight w carry structure
BEYOND its FULL STATISTICAL BASE -- against a structured-noise null? The blind base ladder is LOCKED in the pre-reg
and NEVER tuned (the anti-tautology pin). SMOKE validates the machinery on real data (null validity, w computable,
b_blind computable) then HOLD; the Layer-1 fork (w_resid real vs structured-noise null) is the OFFICIAL run.

Base = statistical estimators ONLY (MI, entropy rate); real compressor (zstd) for w ONLY. Text corpus (network was
blocked) = concatenated in-repo markdown prose (README + CLAUDE + design/*.md + docs/*.md), char-level a-z+space
(alphabet 27) -- the network-blocked fallback per the pre-reg, source recorded here. Protein = the saved D2 Pfam
matrices data/pfam/pilotS_*.npy (sequences x positions, alphabet 21). Outputs -> data/ (gitignored). ASCII.
Usage: python scripts/dcal_w_real.py [smoke]
"""
import sys, json, glob, re
from itertools import combinations
from collections import defaultdict
import numpy as np

sys.path.insert(0, ".")
import zstandard
from cit.information import coherence_weighted_mutual_information, pmf_from_counts

_CCTX = zstandard.ZstdCompressor(level=3)   # real compressor for w (zstd K1 level)

# ---- LOCKED blind base ladder (pre-reg; NEVER tuned/enriched) ----
LAG_LADDER = (1, 2, 4, 8, 16, 32, 64, 128, 256)
ORDER_SET = (1, 2, 3, 4)
TEXT_MARKOV_K = 3          # structured-noise null order for text (pinned, smoke)
TEXT_FILES = ["README.md", "CLAUDE.md"]


# ================= statistical estimators (NO compressor) =================
def raw_mi(x, y, Ax, Ay):
    c = np.bincount(x.astype(np.int64) * Ay + y.astype(np.int64), minlength=Ax * Ay).reshape(Ax, Ay).astype(float)
    return coherence_weighted_mutual_information(pmf_from_counts(c), np.ones(Ax))


def _ent(c):
    c = c[c > 0].astype(float)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def marg_entropy(x, A):
    return _ent(np.bincount(x, minlength=A))


def same_time_coupling(O, A):
    F = O.shape[1]
    M = np.zeros((F, F))
    for i, j in combinations(range(F), 2):
        M[i, j] = M[j, i] = raw_mi(O[:, i], O[:, j], A, A)
    return M.sum(1)


def lagged_self_mi(O, A, lag):
    F = O.shape[1]
    if lag >= O.shape[0] - 1:
        return np.zeros(F)
    return np.array([raw_mi(O[lag:, f], O[:-lag, f], A, A) for f in range(F)])


def cond_entropy_order(O, A, M):
    """per-feature order-M conditional entropy H(X_t | X_{t-1..t-M}) along the ROW (time/window) axis."""
    Tn, F = O.shape
    out = []
    for f in range(F):
        x = O[:, f]
        if Tn - M < 2:
            out.append(0.0); continue
        ctx = np.zeros(Tn - M, dtype=np.int64)
        for m in range(M):
            ctx = ctx * A + x[m:Tn - M + m]
        out.append(_ent(np.bincount(ctx * A + x[M:])) - _ent(np.bincount(ctx)))
    return np.array(out)


def _z(v):
    s = v.std()
    return (v - v.mean()) / s if s > 1e-9 else v * 0.0


def b_blind(O, A):
    """LOCKED blind base: z[same-time coupling] + sum_lag z[lagged self-MI] + sum_order z[predictive info].
    Returns (scalar z-sum, components F x n)."""
    marg = np.array([marg_entropy(O[:, f], A) for f in range(O.shape[1])])
    cols = [same_time_coupling(O, A)]
    cols += [lagged_self_mi(O, A, lag) for lag in LAG_LADDER]
    cols += [marg - cond_entropy_order(O, A, M) for M in ORDER_SET]
    comps = np.column_stack([_z(c) for c in cols])
    return comps.sum(1), comps


def b_sametime(O, A):
    marg = np.array([marg_entropy(O[:, f], A) for f in range(O.shape[1])])
    return marg + same_time_coupling(O, A)


# ---- REAL compressor for w: TIME-MAJOR zstd leave-one-out ablation ----
# (the feature-major K1 proxy compresses each feature's column ALONE -> it sees only WITHIN-feature structure and
# is DEGENERATE on real matrices whose structure is CROSS-feature -- protein coevolution, text char-adjacency. The
# TIME-MAJOR serialization lays each row's F features contiguously so zstd sees the cross-feature/within-row
# structure; marginal-relative via a per-column shuffle baseline. The blind base ladder is unchanged; this is the
# w-serialization, not the locked base.)
def _bits_time_major(O, A):
    bps = max(1, int(np.ceil(np.log2(A))))
    shifts = np.arange(bps - 1, -1, -1)
    bits = ((O[:, :, None] >> shifts) & 1).astype(np.uint8)        # (T, F, bps)
    return np.packbits(bits.reshape(-1)).tobytes()                 # row-major (time-major) flat


def _col_shuffle(O, seed):
    rng = np.random.default_rng(seed)
    out = np.empty_like(O)
    for f in range(O.shape[1]):
        out[:, f] = O[rng.permutation(O.shape[0]), f]
    return out


def compress_ratio(O, A):
    b = _bits_time_major(O, A)
    return len(_CCTX.compress(b)) / max(len(b), 1)


def compress_C(O, A, shuf_seed=0):
    """marginal-relative compressibility: 1 - len(zstd(real))/len(zstd(per-column-shuffled)) (column shuffle keeps
    marginals, destroys cross-feature coupling -> isolates the cross-feature/temporal structure zstd exploits)."""
    real = len(_CCTX.compress(_bits_time_major(O, A)))
    surr = len(_CCTX.compress(_bits_time_major(_col_shuffle(O, shuf_seed), A)))
    return (1.0 - real / surr) if surr > 0 else 0.0


def induce_w(O, A, seed=0):
    rng = np.random.default_rng(seed)
    Cfull = compress_C(O, A)
    F = O.shape[1]
    rho = np.empty(F)
    for f in range(F):
        Oa = O.copy()
        Oa[:, f] = rng.integers(0, A, O.shape[0])                  # leave-one-out: replace feature f with uniform
        rho[f] = Cfull - compress_C(Oa, A)
    rho = rho - rho.mean()
    return 1.0 / (1.0 + np.exp(-4.0 * rho))


def w_residual(w, comps):
    X = np.column_stack([np.ones(len(w)), comps])
    coef, *_ = np.linalg.lstsq(X, w, rcond=None)
    return w - X @ coef


def rank(x):
    return np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)


def spearman(x, y):
    if np.std(x) < 1e-9 or np.std(y) < 1e-9:
        return float("nan")
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def entropy_rate_drift(O, A):
    """SMB stationarity diagnostic: per-feature 1-step entropy rate on the first vs last third; report max drift."""
    Tn = O.shape[0]; t = Tn // 3
    def er(seg):
        out = []
        for f in range(seg.shape[1]):
            x = seg[:, f]
            j = np.bincount(x[:-1] * A + x[1:], minlength=A * A).reshape(A, A).astype(float)
            tot = j.sum()
            with np.errstate(divide="ignore", invalid="ignore"):
                p = np.where(j > 0, j / np.maximum(j.sum(1, keepdims=True), 1e-12), 0.0)
                out.append(-(j / max(tot, 1) * np.where(p > 0, np.log2(np.maximum(p, 1e-12)), 0.0)).sum())
        return np.array(out)
    return float(np.max(np.abs(er(O[:t]) - er(O[-t:]))))


# ================= domains =================
def load_protein(acc, n_seq, n_pos, seed=0):
    M = np.load(f"data/pfam/pilotS_{acc}_matrix.npy")
    rng = np.random.default_rng(seed)
    rows = rng.permutation(M.shape[0])[:n_seq]
    return M[np.ix_(rows, np.arange(min(n_pos, M.shape[1])))].astype(np.int64), 21


def protein_null(M, seed=0):
    """structured-noise null: permute rows INDEPENDENTLY per column -> per-column marginals EXACT, cross-column
    coupling DESTROYED (the D2 marginals-preserved/coupling-destroyed null)."""
    rng = np.random.default_rng(seed)
    out = np.empty_like(M)
    for f in range(M.shape[1]):
        out[:, f] = M[rng.permutation(M.shape[0]), f]
    return out


def load_text(F, T_windows):
    files = TEXT_FILES + sorted(glob.glob("design/*.md")) + sorted(glob.glob("docs/*.md"))
    txt = ""
    for fn in files:
        try:
            txt += open(fn, encoding="utf-8", errors="ignore").read() + "\n"
        except OSError:
            pass
    clean = re.sub(" +", " ", re.sub("[^a-z ]+", " ", txt.lower()))
    stream = np.array([26 if c == " " else ord(c) - 97 for c in clean], dtype=np.int64)
    need = F * T_windows
    stream = stream[:need]
    return stream.reshape(T_windows, F), 27, stream, files


def text_markov_null(stream, A, k, seed=0):
    """order-k Markov surrogate: preserve order-k transition stats, destroy long-range (beyond k)."""
    rng = np.random.default_rng(seed)
    n = len(stream)
    cn = defaultdict(lambda: np.zeros(A))
    for t in range(k, n):
        cn[tuple(stream[t - k:t])][stream[t]] += 1
    # precompute normalized cumulative per seen context
    cum = {c: np.cumsum(v / v.sum()) for c, v in cn.items()}
    out = list(stream[:k])
    u = rng.random(n)
    for t in range(k, n):
        c = tuple(out[-k:])
        cc = cum.get(c)
        out.append(int(rng.integers(A)) if cc is None else int(np.searchsorted(cc, u[t])))
    return np.array(out, dtype=np.int64)


# ================= driver =================
def run_domain(name, O, A, null_fn, extra=None):
    print(f"\n========== DOMAIN {name}  (T={O.shape[0]} x F={O.shape[1]}, alphabet A={A}) ==========", flush=True)
    Onull = null_fn()

    # ---- gate (iii) b_blind computable at all lags/orders + effective sampling ----
    print("--- gate (iii) b_blind COMPUTABLE (locked ladder) + effective sampling ---", flush=True)
    bf, comps = b_blind(O, A)
    print(f"  b_blind built: {comps.shape[1]} components (1 same-time + {len(LAG_LADDER)} lags + {len(ORDER_SET)} orders); finite={np.isfinite(bf).all()}", flush=True)
    for M in ORDER_SET:
        eff = O.shape[0] / (A ** (M + 1))
        print(f"    order-{M} predictive info: effective samples/cell = {eff:.2f} {'(WELL-sampled)' if eff >= 5 else '(UNDERSAMPLED -- reported, NOT dropped)'}", flush=True)
    gate_iii = bool(np.isfinite(bf).all())

    # ---- gate (ii) w computable + stable on REAL data ----
    w = induce_w(O, A)
    gate_ii = float(np.std(w)) > 1e-3
    print(f"\n--- gate (ii) w COMPUTABLE+STABLE on real data: std(w)={np.std(w):.4f} (>1e-3?) -> {gate_ii}  "
          f"[range {w.min():.3f}-{w.max():.3f}]", flush=True)

    # ---- gate (i) NULL VALIDITY: structured-noise null matches low-order, differs in higher-order ----
    print("\n--- gate (i) NULL VALIDITY (structured-noise null: low-order matched, higher-order destroyed) ---", flush=True)
    # marginals match -- POOLED over all T*F symbols (well-sampled; per-column max-TV is finite-sample-inflated at
    # ~0.05 by chance for 27 symbols x ~4000 samples). per-column max reported as a diagnostic.
    pr = np.bincount(O.ravel(), minlength=A) / O.size
    pn = np.bincount(Onull.ravel(), minlength=A) / Onull.size
    marg_tv = float(0.5 * np.abs(pr - pn).sum())
    marg_tv_col = float(np.max([0.5 * np.abs(np.bincount(O[:, f], minlength=A) / O.shape[0]
                                             - np.bincount(Onull[:, f], minlength=A) / O.shape[0]).sum() for f in range(O.shape[1])]))
    if name == "PROTEIN":
        lo_real, lo_null = same_time_coupling(O, A).mean(), same_time_coupling(Onull, A).mean()
        lo_label = "same-time coupling (the destroyed higher-order)"
    else:
        # text: order-k cond entropy is PRESERVED (low-order matched); long-range lagged-MI is DESTROYED
        ok_real = cond_entropy_order(O, A, TEXT_MARKOV_K).mean()
        ok_null = cond_entropy_order(Onull, A, TEXT_MARKOV_K).mean()
        print(f"  [low-order matched] order-{TEXT_MARKOV_K} cond-entropy real={ok_real:.3f} null={ok_null:.3f} (|d|={abs(ok_real-ok_null):.3f}<0.1?)", flush=True)
        lo_real = lagged_self_mi(O, A, 128).mean(); lo_null = lagged_self_mi(Onull, A, 128).mean()
        lo_label = "lagged self-MI @128 (the destroyed long-range)"
    # time-major compressibility (real vs null): lower ratio = more compressible; English/coevolution structure the
    # structured-noise null lacks -> real MORE compressible -> gap = ratio_null - ratio_real > 0
    cr_real, cr_null = compress_ratio(O, A), compress_ratio(Onull, A)
    ck_gap = cr_null - cr_real
    print(f"  marginal TV(real,null) POOLED={marg_tv:.4f} (<0.02? low-order matched)  [per-column max={marg_tv_col:.4f}, finite-sample]", flush=True)
    print(f"  {lo_label}: real={lo_real:.4f}  null={lo_null:.4f}  -> destroyed-gap={lo_real-lo_null:+.4f}", flush=True)
    print(f"  compress ratio (time-major): real={cr_real:.4f}  null={cr_null:.4f}  -> real-more-compressible gap={ck_gap:+.4f}", flush=True)
    gate_i = (marg_tv < 0.02) and ((lo_real - lo_null) > 0.01 or ck_gap > 0.02)
    print(f"  gate (i): marginals matched AND higher-order/long-range destroyed -> {gate_i}", flush=True)

    # ---- LAYER-1 PREVIEW (readout 1 + a residual preview; the FORK is the official run) ----
    sp_blind = spearman(w, bf)
    sp_same = spearman(w, b_sametime(O, A))
    wr = w_residual(w, comps)
    wnull = induce_w(Onull, A); _, cnull = b_blind(Onull, A); wrn = w_residual(wnull, cnull)
    r2 = 1.0 - np.var(wr) / max(np.var(w), 1e-12)
    print("\n--- LAYER-1 PREVIEW (NOT the fork; official run decides) ---", flush=True)
    print(f"  [1] Spearman(w, b_blind)={sp_blind:+.3f}  vs  Spearman(w, b_sametime)={sp_same:+.3f}  (R^2 of w on b_blind={r2:.3f})", flush=True)
    print(f"  [2 preview] var(w_resid) real={np.var(wr):.2e}  structured-noise-null={np.var(wrn):.2e}", flush=True)

    drift = entropy_rate_drift(O, A)
    print(f"  [stationarity] entropy-rate drift (first vs last third, max over features)={drift:.4f}", flush=True)

    return {"name": name, "T": O.shape[0], "F": O.shape[1], "A": A,
            "gate_i_null_validity": gate_i, "gate_ii_w_stable": gate_ii, "gate_iii_b_blind": gate_iii,
            "marg_tv": marg_tv, "destroyed_gap": float(lo_real - lo_null), "ck_gap": float(ck_gap),
            "spearman_w_bblind": sp_blind, "spearman_w_bsametime": sp_same, "r2_w_on_bblind": float(r2),
            "var_wresid_real": float(np.var(wr)), "var_wresid_null": float(np.var(wrn)), "entropy_rate_drift": drift}


def main(mode):
    print(f"=== D-cal-w-real SMOKE [{mode}]  blind ladder LAGS={LAG_LADDER} ORDERS={ORDER_SET} ===", flush=True)
    Mp, Ap = load_protein("PF13354", 1500, 60, seed=0)
    rp = run_domain("PROTEIN", Mp, Ap, lambda: protein_null(Mp, seed=1))

    Ot, At, stream, files = load_text(F=24, T_windows=4000)
    print(f"\n[text source] {len(files)} in-repo prose files (network-blocked fallback): {[f.split('/')[-1] for f in files]}", flush=True)
    null_stream = text_markov_null(stream, At, TEXT_MARKOV_K, seed=1)
    Ot_null = null_stream[:Ot.size].reshape(Ot.shape)
    rt = run_domain("TEXT", Ot, At, lambda: Ot_null)

    print("\n=== SMOKE GATE SUMMARY ===", flush=True)
    for r in (rp, rt):
        gates = all([r["gate_i_null_validity"], r["gate_ii_w_stable"], r["gate_iii_b_blind"]])
        print(f"  {r['name']:8s}: null-validity={r['gate_i_null_validity']} w-stable={r['gate_ii_w_stable']} "
              f"b_blind={r['gate_iii_b_blind']} -> ALL={gates}  | preview Spearman(w,b_blind)={r['spearman_w_bblind']:+.3f} "
              f"vs same-time {r['spearman_w_bsametime']:+.3f}; drift={r['entropy_rate_drift']:.3f}", flush=True)
    print("  -> HOLD for Benjamin (real-data confounds + structured-null validity reviewed first; the locked", flush=True)
    print("     blind ladder is NEVER tuned; the Layer-1 fork is the OFFICIAL run).", flush=True)
    json.dump({"protein": rp, "text": rt, "text_files": files}, open(f"data/dcal_w_real_{mode}.json", "w"), indent=2, default=float)
    print(f"\nsaved data/dcal_w_real_{mode}.json", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "smoke")
