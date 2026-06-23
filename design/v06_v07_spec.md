# CIT Architecture & Design Spec -- v0.6-v0.7 reference

**Status:** living design reference, written at HEAD = v0.5.5 (2026-06-23).
**Scope:** the full architecture as built through v0.5.5 (the robustness program, COMPLETE)
plus the design plan for v0.6 (operational theorems) and v0.7 (cross-domain).

**Authority.** This document is a DESIGN/ARCHITECTURE reference, not a locked record.
The authority order is: **Benjamin live > global ACRE > `pre_registration.md` (the locked
commitments, authoritative over code) > this spec > code comments.** Anything described
here as "planned" / "proposed" / "open choice" for v0.6-v0.7 is NOT yet pre-registered;
it becomes binding only when written into `pre_registration.md` as a dated amendment
BEFORE implementation. If this spec and `pre_registration.md` ever disagree, the pre-reg wins.

---

## 0. Orientation -- how to use this doc

CIT (Coherence Information Theory) is the empirical, falsifiable arm of the Recursive
Coherence corpus. The repo's reason for existing: **commitments must precede outcomes.**
Every estimator/threshold is pre-registered before it is run, so the framework is
"vulnerable in the right way." A passing test suite that no longer tests convergence is
lock-in, not success.

Sections 1-6 describe what exists and the working method. Sections 7-10 are the forward
plan (v0.6, v0.7) with the source theorems verbatim and the known gaps. Sections 11-12 are
open issues and notation.

---

## 1. Thesis and formal foundation

CIT generalizes Shannon by attaching a bounded **coherence weight** `w(x) in [0,1]`
(the papers write `kappa(x)`; `w == kappa` throughout) to each source symbol, measuring
that symbol's contribution to recursive structural stability. Three core quantities
(implemented in `cit/information.py`, all default to bits / base-2):

    H(X)      = -sum_x p(x) log p(x)                          (Shannon entropy)
    H_w(X)    = sum_x p(x) w(x) [-log p(x)]                   (coherence-weighted entropy)
    I_w(X;Y)  = sum_{x,y} p(x,y) w(x) log[p(x,y)/(p(x)p(y))]  (coherence-weighted MI)
              = E_{p(x) w(X)} D( p(Y|X) || p(Y) )

**Boundary condition (the spine).** When `w(x) = 1` for all x, every weighted quantity
collapses EXACTLY to its Shannon counterpart. This is what licenses CIT as a
*generalization*, not a replacement. Enforced empirically by `tests/test_shannon_recovery.py`.
Every future estimator, ablation, weight map, OR CODER must preserve this collapse.

**Proved properties of `I_w`** (from the formal paper, see Section 7.1):
- P1 nonnegativity: `I_w >= 0` (since `D >= 0`, `w >= 0`); `=0` iff `p(y|x)=p(y)` for all x with `w(x)>0`.
- P2 upper bound: `0 <= I_w(X;Y) <= I(X;Y)` (weighting never increases MI, since `w <= 1`).
- P3 asymmetry: `I_w(X;Y) != I_w(Y;X)` in general (weights attach to X).
- Weighted Data Processing Inequality: `X->Y->Z` Markov under same `w` => `I_w(X;Z) <= I_w(X;Y)`.

`H_w == H_kappa`: the paper's `H_kappa = -sum kappa(x) p(x) log p(x)` and the repo's
`H_w = sum p(x) w(x) [-log p(x)]` are algebraically identical (the weight multiplies the
surprisal). State this equivalence anywhere the H_w bound is used.

---

## 2. The claim under test (the falsifiable core)

The whole construct rests on ONE empirical claim, now established through v0.5.5:

> Independent proxies of "coherence" (different epistemic bases: prediction, compression,
> MDL, neural, parsing) and independent ablation operators (LOO, Shapley, correlation-cluster)
> CONVERGE on the same per-symbol coherence signal `rho(x)` on structured data, and that
> convergence is DESTROYED on a structure-free (noise-only) counterfactual.

If independent proxies did not converge, the construct would be empty (no stable thing
being measured). If they converged even on noise, the construct would be circular (an
artifact of the method). v0.5 demonstrated neither failure mode occurs. v0.6-v0.7 build
the operational and cross-domain theory ON TOP of this validated signal.

---

## 3. Repository architecture (current = v0.5.5)

### 3.1 Pipeline (the spine of the induced-weight path)

    stream  --proxy K-->  C_hat (scalar coherence)
            --ablation A-->  rho(x) (per-symbol/feature contribution, centered)
            --sigmoid-->     w(x) = sigma(beta * rho(x)),  beta = 4.0 (locked)

Proxies and ablations are deliberately swappable; the convergence claim IS that the
choice of K and A does not change the rho signal's structure.

### 3.2 Module map

| Layer | Module | Role |
|-------|--------|------|
| Formal | `cit/information.py` | `H`, `H_w`, `I_w` (+ aliases `shannon_entropy`, `coherence_weighted_entropy`, `coherence_weighted_mutual_information`), `pmf_from_counts`. base-2 default; weights validated to [0,1]; probs validated to simplex. |
| Substrate (1-D) | `cit/data/synthetic.py` | `labeled_coherence_stream` -- single-symbol sticky-Markov coherent symbols + i.i.d. noise (v0.2 substrate). |
| Substrate (multi) | `cit/data/multi_feature.py` | `labeled_multi_feature_stream` (shared 2-state HMM, 4 coherent + 6 noise binary features, marginal-matched) and `noise_only_multi_feature_stream` (all i.i.d. Bernoulli(0.5)). The v0.5 substrate. |
| Proxies (1-D) | `cit/proxies/predictive_logloss.py`, `compression_delta.py` | form B (predictive log-loss), K1 (zstd compression-delta). |
| Proxies (multi) | `predictive_logloss_multi.py`, `compression_delta_multi.py`, `ngram_mdl.py`, `lempel_parsing.py`, `neural_prequential.py`, `mdl_hmm.py` | form B multi, K1 multi, K2, K5, K3, K4 (see 3.4). |
| Ablations (1-D) | `cit/ablations/loo.py`, `shapley.py` | A1 LOO, A2 Shapley (single-symbol). |
| Ablations (multi) | `loo_multi.py`, `shapley_multi.py`, `correlation_cluster.py` | A1, A2, A3 (feature-level). |
| Induction | `cit/induce.py`, `cit/induce_multi.py` | `induce_weights` (1-D), `induce_weights_multi` (multi). `BETA = 4.0`. |
| Coders | `cit/coders/__init__.py` | EMPTY placeholder. The v0.6 weighted typical-set coder lands here. |
| Tests | `tests/test_*.py` | 5 files (see 3.7). |
| Design | `design/multi_feature_substrate.md`, `design/v06_v07_spec.md` (this file) | locked v0.5 substrate memo + this spec. |

### 3.3 The contracts (stable interfaces v0.6 must respect)

- **Proxy:** `proxy(stream_2d_uint8, n_features=None) -> float in [0,1]`. Deterministic.
  Higher = more coherent structure. `stream_2d` is `(T, n_features)` binary. The ablation
  operator handles per-feature `rho` by calling the proxy on column-replaced streams; the
  proxy itself only returns a scalar.
- **Ablation:** `ablation(stream, proxy, n_features=None, *, rng=None, center=True) -> dict`
  with keys `rho` (dict feature->value, cohort-mean-centered when `center=True`),
  `c_ablated`, `centered` (and `clusters` for A3). LOO/Shapley/CorrCluster all share this.
- **Induction:** `induce_weights_multi(stream, n_features=None, *, proxy=None, ablation=None,
  rng=None, beta=4.0) -> {rho, w, c_ablated, centered}` with `w(j) = sigmoid(beta*rho(j))`.

### 3.4 Proxy family identities (each a structurally distinct lens; this distinctness is the point)

| K | Module | Family | Key mechanism |
|---|--------|--------|---------------|
| form B multi | `predictive_logloss_multi` | predictive log-loss, no penalty | joint conditioning on previous full feature vector, Laplace-smoothed |
| K1 multi | `compression_delta_multi` | universal compression | zstd level 3 on 2-byte-per-step encoding (10 active + 6 padding bits); `C = 1 - len(compressed)/len(uncompressed)` |
| K2 | `ngram_mdl` | explicit MDL with model penalty | per-feature factorized bigram, 2-part MDL (Rissanen `0.5*num_params*log2(T)`), `num_params = 2*n_features` |
| K3 | `neural_prequential` | neural online cross-entropy, no penalty | single-layer GRU (hidden=64), per-feature sigmoid heads, strict online prequential SGD (lr=0.01), `NEURAL_SEED=7`, torch CPU-deterministic |
| K4 | `mdl_hmm` | latent-variable model + MDL cardinality selection | factorized-Bernoulli HMM, Baum-Welch EM, MDL search over `H in {1,2,3,4}`, `num_params(H)=H(H-1)+H*n+(H-1)`, `HMM_SEED=0` |
| K5 | `lempel_parsing` | non-coding pattern counting | bit-level LZ76 phrase parse (numba Kaspar-Schuster) on the unpacked K1 byte stream; no entropy coder |

K4 is the only proxy with a latent variable AND an explicit complexity penalty. K3/K4 share
K2's per-feature factorization, so K-vs-K2 comparisons isolate the model-class difference.
K1 and K5 share the same underlying bits (K1 compresses bytes via zstd; K5 parses bits via
LZ76) so their difference traces to the parsing/coding boundary, not representation drift.

### 3.5 Ablation operators

| A | Module | Mechanism |
|---|--------|-----------|
| A1 | `loo_multi` | leave-one-out: replace one feature column with Bernoulli(0.5); `rho = C_full - C_ablated`, centered. |
| A2 | `shapley_multi` | Shapley value over `k=64` sampled coalitions; replace-with-uniform from kept set; cohort-mean centered. EXPENSIVE. |
| A3 | `correlation_cluster` | Pearson signed-correlation clustering (threshold `DEFAULT_CORRELATION_THRESHOLD = 0.15`), connected components, ablate cluster-wise. Multi-feature-native (no 1-D analog). |

### 3.6 Coders -- `cit/coders/` is empty

This is the deliberate v0.6 placeholder. The weighted typical-set coder (Section 7.3)
lands here. Nothing is implemented yet.

### 3.7 Tests and gating

Five test files. Total **220 tests: 127 fast + 75 slow + 18 very_slow (1 xfail = Seam 1).**

| File | Covers |
|------|--------|
| `test_shannon_recovery.py` | the boundary-condition spine (H_w/I_w collapse to Shannon at w=1); `SEED=42`. |
| `test_induction_pipeline.py` | v0.2 single-symbol induction; `STREAM_SEED=42`, `ABLATION_SEED=123`. |
| `test_cross_proxy_validation.py` | v0.3 cross-proxy (form B vs K1) at the 1-D level (threshold 0.7). |
| `test_cross_ablation_validation.py` | v0.4 cross-ablation (A1 vs A2) sign agreement + Spearman >= 0.7. |
| `test_multi_feature_substrate.py` | the v0.5 program: substrate, all 6 proxies x 3 ablations, the 15-pair cross-proxy matrix, the noise-only falsifiability (`TestNoiseOnlyFalsifiability`), Seam 1 xfail, A3 cluster recovery (observational). |

**Gating** (`pyproject.toml addopts = -m 'not slow and not very_slow'`):
- **fast** (default `pytest`, ~25s): everything cheap (form B / K1 / K2 proxies and their A1/A3/A2, the boundary spine, the 6 cheap noise-falsifiability tests).
- **slow** (`-m slow`, ~19 min): LOO + CorrCluster for K3/K4/K5 (structured AND noise), proxy invariants, the A2 cheap-proxy noise sample. CI workflow `slow.yml` runs on every push, `timeout-minutes: 60`.
- **very_slow** (`-m very_slow`, workflow_dispatch only): Shapley (A2) for K3/K4/K5. K4 Shapley ~2.1h (under 6h hosted ceiling); K5 ~135 min; K3 ~4.3h (local-gated, exceeds hosted ceiling). Hosted `very_slow.yml` runs `-k "not K3"` (K4+K5 families), `timeout-minutes: 350`.

(Note: the `markers` docstrings in `pyproject.toml` still say "K_5 LZ76" only -- a stale
comment predating K3/K4 and the noise tests. Harmless; not corrected as of this writing.)

---

## 4. The v0.5 robustness program (COMPLETE) -- results and invariants

v0.5.0 substrate -> v0.5.1 K2 -> v0.5.2 K5 (Seam 1 surfaced) -> v0.5.3 K3 -> v0.5.4 K4
(Seam 1 specificity evidence) -> v0.5.5 capstone (noise-only falsifiability + Seam 1 resolved).

### 4.1 Cross-proxy convergence matrix (structured substrate)
All 15 off-diagonal pairs of {form B, K1, K2, K3, K4, K5} under each of A1, A2, A3 (45 cells)
clear **Spearman rho >= 0.5** (the multi-feature threshold, calibrated 2026-05-26). Built
incrementally; consolidated at the capstone.

### 4.2 Cross-ablation convergence
A1 vs A2 per-symbol sign agreement (strict) + Spearman rho >= 0.7 (the 1-D / ablation-axis threshold).

### 4.3 Noise-only counterfactual (the falsifiability spine, v0.5.5)
For each off-diagonal pair: structured Spearman `>= 0.5` AND noise-only Spearman `< 0.3`
(`T_NOISE = 0.3`, locked). Asserted on A1 + A3 for all 15 pairs; A2 (Shapley) sampled on the
3 cheap-proxy pairs (full A2-on-noise would be a second ~8h very_slow tier for marginal value).
Calibration (locked seeds), structured vs noise-only cross-proxy Spearman:

| Ablation | structured (min/mean/max) | noise-only (min/mean/max) |
|----------|---------------------------|---------------------------|
| A1 (LOO) | 0.571 / 0.753 / 0.948 | -0.390 / -0.049 / 0.000 |
| A3 (CorrCluster) | 0.583 / 0.754 / 0.985 | -0.390 / -0.049 / 0.000 |
| A2 (Shapley, cheap) | 0.733 / 0.794 / 0.855 | -0.297 / -0.099 / 0.000 |

No pair has positive convergence on noise under any ablation. (Many noise pairs are exactly
0.000 because proxies that clip C to a constant on noise yield tied rho vectors -> Spearman 0.)

### 4.4 Seam 1 (RESOLVED at v0.5.5; stays xfail)
`(K5, K2)` under A2 Shapley = **0.491**, just under 0.5. Surfaced v0.5.2. Resolved
`(K5, K2)`-SPECIFIC: of all `(X, K2)` pairs under A2, only K5 misses; K3, K4 (0.830),
form B, K1 all clear. So the divergence is particular to K5's LZ76 phrase dictionary vs K2's
factorization under random-coalition ablation, and does NOT generalize -> the framework's
operating envelope is NOT restricted. Mechanically `@pytest.mark.xfail(strict=True)` in
`test_multi_feature_substrate.py::TestCrossProxyConvergenceMulti::test_K5_vs_K2_under_A2`.
A strict XPASS forces re-evaluation. **Do not "fix" silently.**

---

## 5. Locked constants, conventions, environment

### 5.1 Locked constants (pre-registered; change only with a version bump + pre-reg amendment)
| Constant | Value | Where | Role |
|----------|-------|-------|------|
| `beta` | 4.0 | `cit/induce.py`, `cit/induce_multi.py:BETA` | weight-map sensitivity `w=sigma(beta*rho)` |
| `SEED` | 42 | `tests/test_shannon_recovery.py` | Shannon-recovery stochastic tests |
| `STREAM_SEED` | 42 | `test_induction_pipeline.py`, `test_cross_proxy_validation.py`, `test_cross_ablation_validation.py`, `test_multi_feature_substrate.py` | synthetic-stream generation |
| `ABLATION_SEED` | 123 | same four test files | ablation RNG (LOO/Shapley/CorrCluster) |
| `NEURAL_SEED` | 7 | `cit/proxies/neural_prequential.py` | K3 GRU init/SGD |
| `HMM_SEED` | 0 | `cit/proxies/mdl_hmm.py` | K4 Baum-Welch EM init |
| `DEFAULT_CORRELATION_THRESHOLD` | 0.15 | `cit/ablations/correlation_cluster.py` | A3 clustering edge threshold |
| cross-proxy R2 (multi) | Spearman >= 0.5 | `test_multi_feature_substrate.py:R2_THRESHOLD` | convergence floor |
| cross-proxy R2 (1-D) | Spearman >= 0.7 | v0.3/v0.4 tests | 1-D convergence floor |
| cross-ablation | Spearman >= 0.7 + sign agreement | v0.4 | A1 vs A2 |
| `T_NOISE` | 0.3 | `test_multi_feature_substrate.py` | noise-only falsifiability ceiling |
| collapse tol | 1e-12 (algebraic); empirical atol in pre-reg | tests | boundary-condition precision |

### 5.2 Working conventions
- **One sub-step per "proceed."** Hand steering back; no unsupervised bulk output.
- **Pre-register before implementation.** If structural findings emerge, pre-register
  honestly rather than silently adjusting thresholds. The amendment pattern: bump version,
  add a dated entry to `pre_registration.md`'s history (most recent last), update the design
  memo in the same commit, never silently edit a lock.
- **Surgical Python edits** via `python << 'PYEOF'` with BOTH guards:
  `assert src.count(old) == 1` (anchor) AND `assert <new-token> not in src` (idempotency).
  Heredocs use `MULTIEOF`, not `EOF`. (Markdown/config: direct edits are fine.)
- **ASCII-only in code payloads.** Unicode allowed in README.md / pre_registration.md prose
  (and this design doc keeps ASCII for consistency with `design/`).
- **Parse at the bit level**, not byte level, where byte-level clips a metric to zero
  (the K2 joint-bigram and K5 byte-level amendments both stemmed from clip-to-zero).
- **Commits:** two `-m` flags, dense paragraph body; version strings `"vX.Y.Z: subject"`;
  end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Commit/push only when asked.
- **Per-version release checklist** (do not miss any): bump `pyproject.toml` AND
  `CITATION.cff` (version + `date-released`); update README status row + counts; refresh
  CLAUDE.md; pre-reg amendment (if behavior); then commit + annotated tag `vX.Y.Z` +
  `gh release create` (which mints the Zenodo version DOI). The README DOI badge is the
  concept DOI (auto-resolves to latest) and must not be edited per the 2026-05-26 convention.

### 5.3 Environment & determinism
- Python 3.11/3.12. `python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
- Deps: `numpy<2`, `zstandard`, `numba>=0.60`, `torch>=2.0,<2.3`. (No scipy: Spearman is
  hand-implemented with midrank ties in the test file.)
- Bit-exact determinism is load-bearing for the convergence claims. x86<->arm64 migration
  breaks bit-exact CI parity (multi-day measurement-and-amendment lift, not a quick port).
- **Operational gotcha:** heavy numba/pytest background runs, when killed, can leave orphaned
  child processes that consume CPU and starve later runs (caused a ~12h false "hang" once).
  Launch long jobs as plain `python/pytest` under the harness background (no `nohup`/`&`);
  do not overlap heavy runs; verify with `pgrep -fl python` and `pkill -9 -f <script>` after killing.

---

## 6. Pre-registration discipline (the method, proven over v0.5)

The pattern that worked for K3, K4, and the v0.5.5 capstone, and that v0.6 should follow:

1. **Gather state** (boot: README, pre-reg, git, fast suite).
2. **Due-diligence BEFORE locking.** Run an empirical pre-check (often two independent
   throwaway implementations that must agree) to settle the one decisive risk -- e.g. "does
   the metric clip to zero on this substrate?" (K2/K5) or "what is the noise baseline?"
   (v0.5.5 threshold). Cite the measured numbers in the amendment.
3. **Surface the genuine design choices** to Benjamin (narrow vs rich, threshold value,
   compute scope) and get sign-off.
4. **Write the pre-reg amendment** (definition, locked constants, rationale, expected
   values, gating, the honest gaps). Update the design memo in the same commit.
5. **Implement** to match the lock; verify it reproduces the pre-registered expectation.
6. **Wire tests**, assign markers, run fast+slow green; expensive tiers separately.
7. **Ship** (the release checklist).

If a measured result contradicts the lock (e.g. a pair lands < threshold), record it
honestly as a seam (`xfail(strict=True)`) with a resolution version -- do not tune to pass.

---

## 7. v0.6 -- Capacity, Coder, Selective Compression (THE PLAN)

**Decided (2026-06-23):** sequence is **capacity estimator first (v0.6.0)**, then coder
(v0.6.1), then Selective Compression empirics (v0.6.2). Source specs come from the papers
(Benjamin supplied them; see Section 10). The capacity estimator is the most self-contained,
low-risk deliverable; the coder and the soundness gap are where the real authoring burden is.

### 7.1 The theorems (verbatim from `cit formal.docx` = JAMFFO-2, "Capacity and Compression Theorems")

**Coherence Capacity Theorem (Thm 4.1).** For a DMC `p(y|x)` and weight `w: X -> [0,1]`,
a rate R (bits/use) is achievable for coherence-relevant transmission iff
`R < C_C = max_{p(x)} I_w(X;Y)`. Reliability = block error `Pe(n) -> 0` AND the decoder
recovers every symbol whose weight exceeds any fixed `delta > 0`. Achievability: random
coding + coherence-joint-typicality decoding. Converse: weighted Fano +
single-letterization `I_w(X^n;Y^n) = sum_i I_w(X_i;Y_i) <= n*C_C`. **Cor 4.4:** `w=1 => C_C = C`
(Shannon channel capacity recovered) -- the boundary condition.

**Selective Compression Theorem (Thm 5.1).** For an i.i.d. source `p(x)` with weights
`w(x) in [0,1]`, any uniquely-decodable lossless code whose decoder must reproduce every
symbol with `w(x) > delta` has expected per-symbol length `L >= H_w(X)`, and for every
`eps>0` there is a block-length and coding scheme achieving `L <= H_w(X) + eps`. Converse:
Kraft-McMillan with weighted typical-set counting. `w=1 => L >= H(X)` (Shannon).

**Weighted AEP.** `-(1/n) sum_i w(x_i) log p(x_i) -> H_w(X)` in probability; equivalently
`Pr{X^n in T_w,eps^n} -> 1`. Coherence-typical set
`T_w,eps^n(X) = { x^n : | -(1/n) sum_i w(x_i) log p(x_i) - H_w(X) | < eps }`.
Proofs: weighted WLLN (Lemma A.1) + Chebyshev/Chernoff (A.2); cardinality (A.3)
`(1-d) 2^{n(H_w-eps)} <= |T| <= 2^{n(H_w+eps)}`.

### 7.2 v0.6.0 -- Coherence capacity estimator (LOCKED 2026-06-23)

Pre-registered in `pre_registration.md` (the `## v0.6` section + the 2026-06-23 amendment entry).
Due-diligence settled the decisive risk (does a numpy simplex maximizer reproduce the fixture and
the boundary) before locking. What is locked:

- **Definition:** `C_C = max_{p(x)} I_w(X;Y)` for fixed DMC `p(y|x)` and fixed `w(x)`,
  over the input simplex. Reuse `cit/information.py:I_w`.
- **Boundary unit test (the spine):** `C_C(w=1) == Shannon channel capacity` to tolerance,
  mirroring `test_shannon_recovery`. Use a channel with closed-form Shannon capacity (BSC, Z-channel).
- **Binary Coherence Channel fixture -- CORRECTED (Sec 6 erratum).** The paper's Sec 6
  `C_C(eps)=0.5(1+eps)` (identity channel, `w=(1,eps)`, uniform input) is `I_w` at UNIFORM input,
  NOT the capacity: `I_w = H_w = -q log2 q - eps(1-q) log2(1-q)` is maximized at `q* < 0.5` for
  eps<1, so `0.5(1+eps)` is only a lower bound (equal at eps=1). Locked TRUE capacity: eps=0 ->
  0.530738 (=`1/(e*ln2)`, `q*=1/e`); 0.25 -> 0.639687; 0.5 -> 0.755588; 0.75 -> 0.876210; 1.0 ->
  1.0. No closed form for general eps; only the endpoints are exact. Erratum affects ONLY the Sec 6
  example, NOT Capacity Theorem 4.1 (`C_C = max_p I_w`, correct). Flagged for author erratum.
- **CHOICES LOCKED at pre-reg (the papers leave these to us; now settled):**
  - *Solver.* Projected-gradient ascent on the simplex with a DETERMINISTIC multi-start set
    (centroid + n vertices + resolution-m=20 lattice), best local optimum; analytic gradient
    FD-checked; `tol=1e-10`, `max_iter=2000`; no RNG (bit-exact, no new seed). Small-alphabet
    fixtures only; larger alphabets need a seeded-sampling amendment. Blahut-Arimoto NOT used.
  - *Concavity: OPEN.* Not proven (the `w(x)` factor breaks the standard argument). Multi-start
    agreement is the empirical uniqueness stand-in, asserted on the fixtures. No guarantee claimed.
  - *Tolerance / iteration cap:* `tol=1e-10`, `max_iter=2000`; test atols 1e-6 (boundary), 1e-8
    (closed-form anchors; corrected from 1e-9 post-implementation -- the locked tol floors at
    ~1e-9 value accuracy on the flat eps=0 max), 1e-5 (grid-verified eps).
  - *delta (must-preserve threshold):* the capacity value is delta-independent; deferred to v0.6.1.
  - *Test channels:* BSC(p in {0.1,0.25}) + Z-channel(f=0.5) for the boundary; the corrected
    Binary Coherence Channel for the fixture.
- **Asserted invariants (locked):** boundary collapse (BSC + Z, atol 1e-6); the corrected fixture
  (closed-form anchors atol 1e-8, grid-verified eps atol 1e-5, `q*<0.5` strict); `C_C(eps) >=
  0.5(1+eps)`; `0 <= C_C <= C_Shannon` (P2); determinism (bit-identical); monotonicity of `C_C` in
  a uniform weight scale. Tests FAST in `tests/test_capacity.py`.

### 7.3 v0.6.1 -- Selective compression coder (LOCKED 2026-06-23; Thm 5.1 repaired)

Pre-registered in `pre_registration.md` (the v0.6 "Selective compression coder" subsection + the
2026-06-23 v0.6.1 amendment). A 4-agent adversarial analysis (confirmed against the paper text)
found the paper's Thm 5.1 UNSOUND for non-constant w -- RESOLVED-NEGATIVE -- so the repo builds the
corrected theorem instead.

- **Thm 5.1 is unsound for w != 1 (resolved-negative).** Achievability `L <= H_w + eps` and the
  App A.2 cardinality bound `|T| <= 2^{n(H_w+eps)}` both fail: w-typicality constrains the WEIGHTED
  log-prob `~ H_w`, but the typical set's SIZE is governed by the RAW `-log p(x^n)` (enumerated:
  `|T|=6 > 5.28`; `|T|=15 >> 5.43`). Under the threshold criterion only `S_delta={x:w(x)>delta}` must
  be reproduced, so the true floor is the merged-source entropy `H(Z)`, which can exceed `H_w`. The
  paper's own Sec 5.4 binary example is the counterexample. Holds only at `w=1` (Shannon).
- **H_w recast (kept):** `H_w = E_p[w(X)(-log p(X))]` stays as the "bits that matter" MEASURE, not a
  compression rate. `cit/information.py:H_w` unchanged.
- **Corrected theorem (Option A, built):** compress to `H(Z)`, `Z=(S_delta union {*})` -- reproduce
  `S_delta` exactly, collapse all don't-cares to one token. Converse `L >= H(Z)`; achievability
  `L <= H(Z)+eps` (entropy coding of Z); boundary `S_delta=X => H(Z)=H(X)` (Shannon spine);
  `H(Z) <= H(X)` always. H(Z) is partition-driven (the threshold, not the graded weights, sets it;
  the graded weights live in the H_w measure).
- **Coder (`cit/coders/selective.py`):** "merge -> entropy-code." Primary = static arithmetic/range
  coder on Z (rate `-> H(Z)+eps`, bit-exact); practical variant = zstd on the merged byte stream
  (reuses K1). `delta` explicit; decoder reproduces `S_delta` exactly + a fixed placeholder for `*`.
- **Invariants:** lossless on `S_delta`; arithmetic rate `<= H(Z)+0.02` at `N=200k`; `H(Z) <= H(X)`;
  coherence saving vs weight-blind when `>= 2` don't-cares; boundary collapse; determinism. Fast tier.

### 7.4 v0.6.2 -- Selective Compression empirics (LOCKED 2026-06-23)

Pre-registered in `pre_registration.md` (the v0.6 "Selective Compression empirics" subsection + the
2026-06-23 v0.6.2 amendment). The win-margin demonstration of the corrected coder (Section 7.3), on
the SOUND `H(Z)` footing (the floor is `H(Z)`, NOT `H_w`).

- **Win metric:** fractional saving `Delta_frac = (rate_blind - rate_selective)/rate_blind`
  (arithmetic coder), where weight-blind = `delta` below all weights (no merge, full lossless). Both
  coders are lossless on `S_delta`, so the win is at ZERO coherence-retention cost (equal-retention,
  lower-rate -- cleaner than the paper's equal-rate/higher-retention asymmetry).
- **Falsifiable claim (two-sided):** per structured substrate `Delta_frac >= WIN_MARGIN = 0.20` AND
  lossless on `S_delta`; at the boundary (`S_delta = X`) `Delta = 0` exactly. Falsified if the saving
  falls below 0.20 on structure, is non-zero at the boundary, or any `S_delta` symbol is corrupted.
- **Substrates (locked seeds, N=100k):** iid (`rng(42)`), Gilbert-Elliott memory (`rng(1)`), TCUN
  toggle+noise (`rng(2)`). Calibration (arith `Delta_frac`): iid 0.492, G-E 0.411, TCUN 0.307;
  boundary 0.000. Margin 0.20 sits below the 0.307 floor with headroom. The v0.5 multi-feature
  substrate is per-feature-binary, not a symbol stream -- deliberately excluded.
- **Gating:** fast. `tests/test_selective_compression_empirics.py`. Completes the v0.6 program.

### 7.5 KNOWN GAPS AND RISKS (carry these into the v0.6 pre-reg, honestly)

1. **No capacity solver / no concavity result IN THE PAPERS.** Authored repo-side: solver LOCKED
   v0.6.0 (deterministic projected-gradient multi-start); concavity remains OPEN (multi-start
   agreement is the empirical stand-in). See Section 7.2.
2. **The practical weighted coder is constructed nowhere** -- RESOLVED at v0.6.1: the weighted
   typical-set coder is unsound (Section 7.3); the corrected `merge -> entropy-code` selective coder
   (`cit/coders/selective.py`) is built against `H(Z)` and demonstrated in v0.6.2.
3. **App A.2 soundness flag -- RESOLVED-NEGATIVE at v0.6.1 (2026-06-23).** The typical-set
   cardinality bound `|T| <= 2^{n(H_w+eps)}` is false for `w != 1`: w-typicality controls the
   WEIGHTED log-prob `sum_i w(x_i)(-log p(x_i)) ~ H_w`, which does NOT bound the RAW
   `-log p(x^n)`, so the bound and the `H_w` achievability rate fail (enumerated counterexamples).
   Adversarially verified (4-agent) and confirmed against the paper text; Thm 5.1 holds only at
   `w=1`. Both the converse and achievability to `H_w` are unsound; the capacity theorem (Sec 4) is
   UNAFFECTED. Repaired in v0.6.1: `H_w` demoted to a measure, operational floor replaced by the
   merged-source entropy `H(Z)` (Section 7.3 + the 2026-06-23 v0.6.1 amendment in `pre_registration.md`).
4. **No finite-blocklength theory** (paper Sec 9 defers to Polyanskiy-Poor-Verdu). Any finite-n
   empirical correction needs its own pre-registration.
5. **No numeric reproducibility constants** in any document (no seeds/tolerances/alphabet sizes
   for the estimator/coder; the paper's LM simulation reports numbers with no seed/code).
   All repo-side; set them at pre-reg.
6. **Robustness-bar mismatch across docs** (engineering wants median Spearman > 0.8;
   Metacoherence R2 >= 0.7; repo cross-proxy 0.5). Reconcile in v0.6.2: those higher bars are
   validation-program bars, not capacity/coder bars.

---

## 8. v0.7 -- Cross-domain validation (Metacoherence)

The cross-domain architecture from Metacoherence. Tests that the SAME `rho` signal recovers across
distinct domain substrates `D1, D2, D3`. **v0.7.0 LOCKED 2026-06-23** (pre_registration.md: the
`## v0.7` section + the 2026-06-23 v0.7.0 amendment): D1 = a 3-state hidden semi-Markov substrate
(8 alphabet-8 features encoding 4 properties A/B/C/D + 3 distractors; params MI-balanced so no
property exceeds 40% of recoverable info), its exact-by-construction M5 partition ({f0..f4} vs
{f5..f7}), and R2 (cross-philosophy median Spearman `> 0.6`, CI `> 0.4`) via the categorical 5x3
grid with the LOAD-BEARING marginal-relative coherence requirement (else skewed-marginal distractors
read as coherent). Sequenced: v0.7.0 D1+M5-partition+R2; v0.7.1 R1 (persistence); v0.7.2 R3
(interventions); then D2 (Pfam, CC0), D3 (FOMC), and the M5 + eight-cell capstone. Four conditions:
R1 (persistence prediction), R2 (cross-philosophy convergence), R3 (intervention asymmetry), and:

- **M5 cross-domain admissibility gate** (operationalized in Metacoherence): mean-w over
  coherence-bearing vs noise features, rank-normalized, within a factor-of-2 across all domain
  pairs for at least 3 of 5 estimator classes.
- **The eight-cell outcome interpretation matrix** (Metacoherence Sec 8.3-8.4) to be reproduced
  verbatim and bound to outcomes in advance.
- **M-conditions** (the weight admissibility axioms; the principled-quantity layer): see Section 9.

v0.7 has empirical content only because v0.3-v0.6 anchored operator-invariance and the
operational theorems on a single substrate first.

---

## 9. Weight admissibility (M-conditions) -- the principled-quantity layer

The capacity/compression theorems need only `w in [0,1]`, finite alphabet, and `w` a fixed
per-symbol function (`w=1` recovers Shannon). The DISCIPLINE on induced weights is the
M-condition layer (from `formal 3.docx` = JAMFFO-3, extended in `Meta-coherence.docx`):

- **M1** boundedness + monotonicity in `rho` (rho up => w not down). [repo: `w=sigma(beta*rho)`]
- **M2** coherence-consistency under coarse-graining (no relevance-order flips under benign regrouping).
- **M3** stability under recursive reuse (long-run contribution, not transient salience).
  [operationalized as R2 cross-replicate Spearman >= 0.7]
- **M4** empirical derivability without exogenous semantics (>=1 data->C->rho->w route).
- **M5** domain-translation invariance up to monotone transformation. [the cross-domain gate]
- **M6** (Metacoherence only) recursive-reinforcement compatibility.

"Within the admissible class, estimation may vary" -- which is exactly why cross-proxy
convergence is the test. The repo's induction (`induce.py`/`induce_multi.py`) implements the
M4 route: `rho(x) = E_t[C_t - C_t(-x)]` (mean LOO drop in proxy coherence), `w = sigma(beta*rho)`.

---

## 10. Source documents (the theory lives outside the repo)

Benjamin's OneDrive (supplied 2026-06-23). `w == kappa`, `H_w == H_kappa`.

| File | Content |
|------|---------|
| `.../UFAP/Research/cit formal.docx` | **CANONICAL** -- "Capacity and Compression Theorems" (JAMFFO-2). Full proofs: Capacity Thm 4.1, Selective Compression Thm 5.1, weighted AEP (App A.2), I_w properties P1-P3 + weighted DPI, Binary Coherence Channel fixture (Sec 6). The App A.2 soundness flag lives here. |
| `.../UFAP/Research/cit_formal_equations.tex` | clean LaTeX summary of the above theorems. |
| `.../UFAP/2026/cit engineering.docx` | Engineering Induced Coherence Weights -- empirical protocols, Selective Compression as the primary target, win-margin examples, benchmark toys. |
| `.../UFAP/2026/formal 3.docx` | Formal Foundation of Induced Coherence Weights (JAMFFO-3) -- M1-M5 admissibility. |
| `.../UFAP/2026/Meta-coherence.docx` | cross-domain (M1-M6, M5 gate, eight-cell matrix) -- the v0.7 source. |
| `.../UFAP/Research/Info.docx` | background; low relevance to the operational theorems. |

PhilPapers references are listed in README.md and `cit/information.py`. NOTE: the capacity
solver, the concavity result, and the practical streaming coder appear in NONE of these.

---

## 11. Open seams and known issues

- **Seam 1** -- `(K5,K2)` under A2 = 0.491. RESOLVED `(K5,K2)`-specific (Section 4.4); stays
  `xfail(strict=True)`. Do not "fix" silently.
- **App A.2 soundness flag** -- Section 7.5(3). Real proof gap in the compression coder
  achievability; Benjamin's call; parked for v0.6.1.
- **Stale `pyproject.toml` markers docstring** -- names only "K_5 LZ76", predates K3/K4 and
  the noise tests. Cosmetic; left as-is.
- **v0.6.0 capacity estimator PRE-REGISTERED (2026-06-23)** -- locked in `pre_registration.md`
  (`## v0.6` + the 2026-06-23 entry); Section 7.2 updated to the corrected fixture. v0.6.1 (coder),
  v0.6.2 (Selective Compression), and all of v0.7 remain PLANNING until their own dated amendments.
- **Sec 6 fixture erratum (2026-06-23)** -- `C_C(eps)=0.5(1+eps)` is the value at uniform input,
  not the capacity (true `C_C` is higher for eps<1; see Section 7.2). Author erratum flagged; does
  NOT affect Capacity Theorem 4.1.

---

## 12. Notation / glossary

| Symbol | Meaning |
|--------|---------|
| `w(x)` / `kappa(x)` | coherence weight in [0,1] (same object) |
| `H_w` / `H_kappa` | coherence-weighted entropy (same object) |
| `I_w(X;Y)` | coherence-weighted mutual information |
| `C_C` / `C_kappa` | coherence capacity = `max_{p(x)} I_w(X;Y)` |
| `rho(x)` | per-symbol/feature coherence contribution (centered ablation differential) |
| `C_hat` | scalar proxy coherence estimate in [0,1] |
| `K1..K5`, form B | the six proxies (Section 3.4) |
| `A1/A2/A3` | LOO / Shapley / correlation-cluster ablations |
| `T_w,eps^n` | weighted (coherence) typical set |
| DMC | discrete memoryless channel `p(y|x)` |
| Seam | a pre-registered near-miss (`xfail(strict=True)`), not a bug |

---

*End of spec. Update this file alongside `pre_registration.md` as v0.6-v0.7 amendments land.*
