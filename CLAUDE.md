# CLAUDE.md — coherence-information (CIT)

Repo-scoped instructions for Claude Code. The global ACRE operating instructions
load separately and govern register and posture; this file governs only this repo.
On conflict: Benjamin live > global ACRE > this file > code comments.

## Boot procedure (run on every fresh session, before any change)

1. Read `README.md` (status table = version history and current state).
2. Read `pre_registration.md` (the locked-commitment record; authoritative over code).
3. `git log --oneline -15` and `git status` — confirm HEAD and clean tree.
4. Run the fast suite: `pytest` (defaults to fast-only). Report green/red.
5. Report state, then wait for steering. Do not edit before reporting.

## What CIT is, and why

Coherence Information Theory generalizes Shannon by attaching a bounded weight
`w(x) in [0,1]` to each source symbol, measuring that symbol's contribution to
recursive structural stability. Three formal quantities:

    H(X)      = -sum p(x) log p(x)                       (Shannon entropy)
    H_w(X)    = sum p(x) w(x) [-log p(x)]                (coherence-weighted entropy)
    I_w(X;Y)  = sum p(x,y) w(x) log[p(x,y)/(p(x)p(y))]   (coherence-weighted MI)

Boundary condition: when `w(x)=1` for all x, every weighted quantity collapses
exactly to its Shannon counterpart. This is what licenses CIT as a generalization,
not a replacement; `tests/test_shannon_recovery.py` enforces it empirically.

Why it exists: CIT is the empirical, falsifiable arm of the Recursive Coherence
corpus (T1). It is the proof of intent — the framework is "vulnerable in the right
way" only if commitments precede outcomes. The whole point is cross-proxy and
cross-ablation convergence plus noise-only falsifiability: if independent proxies
of coherence did not converge, the construct would be empty. That is the claim
under test. Do not let the code drift from this; a passing suite that no longer
tests convergence is lock-in.

Weights are either user-supplied or induced from data:
`stream -> C_hat (proxy K) -> rho(x) (ablation A) -> w(x) = sigma(beta * rho(x))`.

## Current state

- Version `0.6.2` (pyproject + README). v0.6 operational-theorem program COMPLETE: v0.6.0 capacity
  estimator, v0.6.1 selective coder (Thm 5.1 repaired), v0.6.2 Selective Compression empirics.
- Proxies (K_n): K1 compression-delta (zstd), K2 n-gram MDL, K3 neural prequential
  (single-layer GRU), K4 MDL-HMM (factorized-Bernoulli HMM, two-part MDL selection over
  H in {1,2,3,4}, deterministic Baum-Welch, `HMM_SEED=0`), K5 Lempel parsing (bit-level LZ76, numba).
- Ablations (A_m): A1 LOO replace-with-uniform, A2 Shapley (k=64), A3 correlation-cluster.
- Capacity (v0.6.0): `cit/capacity.py:coherence_capacity` = max_p I_w(X;Y) over the input simplex
  via deterministic projected-gradient multi-start (analytic gradient, no RNG, bit-exact); `w=1`
  recovers Shannon capacity (BSC/Z). Sec 6 fixture erratum recorded: paper's C_C(eps)=0.5(1+eps)
  is I_w@uniform, a lower bound, NOT the max (uniform not optimal for eps<1). Concavity OPEN.
- Coder (v0.6.1): `cit/coders/selective.py` — repairs Selective Compression Thm 5.1 (UNSOUND for
  non-constant w; H_w demoted to a "bits that matter" MEASURE). Corrected floor = merged-source
  entropy H(Z) (reproduce S_delta={x:w(x)>delta} exactly, collapse don't-cares). merge->entropy-code:
  bit-exact arithmetic coder (rate -> H(Z)+eps) + zstd variant. Boundary S_delta=X collapses to Shannon.
- Empirics (v0.6.2): falsifiable win-margin — selective coder compresses 31-49% below the weight-blind
  lossless rate at zero retention cost on coherence-structured sources; saving = 0 at the boundary.
  arith Delta_frac >= WIN_MARGIN=0.20 on iid/Gilbert-Elliott/TCUN substrates (calibrated like T_NOISE).
- v0.7 (IN PROGRESS, cross-domain / Metacoherence; version still `0.6.2`, not yet shipped): v0.7.0 D1
  BUILT (slices 1-3, uncommitted at this note's writing). D1 generator `cit/data/hsmm_d1.py` (seeds
  7000..7019); categorical marginal-relative K1-K5 `cit/proxies/categorical.py`; categorical A1/A2/A3
  `cit/ablations/categorical.py`; `cit/induce_cat.py`; R2 + cross-tab `cit/metacoherence.py`;
  CI verdict job `scripts/run_metacoherence_grid.py`. LOAD-BEARING lock HELD: coherence on D1 is
  MARGINAL-RELATIVE (predictive `H_marg - H_pred`; compression via a TIME-SHUFFLE surrogate baseline,
  `SHUFFLE_SEED=0`, feature-major bit encoding). **R2 SEAM (recorded, not tuned):** on D1's A1 column
  the proxies recover COMPLEMENTARY properties (K5 {A,B,C,D}, K1 {A,C}, K2/K3/K4 {A,D}; agree on A,
  diverge on B/C/D) -> cross-philosophy median Spearman ~ -0.08, FALSIFYING `R2>0.6`. The A2-Shapley
  rescue (source expected convergence) is the decisive OPEN question, deferred to CI/very_slow (hours).
  A3==A1 on D1 (Pearson finds only singletons). pre-reg line 791 corrected (K1/K5 were NOT
  alphabet-agnostic). Sequenced next: v0.7.1 R1; v0.7.2 R3; then D2 (Pfam, CC0), D3 (FOMC), M5 + capstone.
- Tests: 234 fast + ~95 slow + 18 very_slow (1 xfail). v0.7.0: 12 D1-structure + 24 categorical-proxy +
  8 categorical-ablation + 7 R2/cross-tab. v0.6.2: 12 empirics. v0.6.1: 23 coder. v0.6.0: 32 capacity.
  v0.5.5: noise-only counterfactual
  falsifiability (each off-diagonal pair structured >= 0.5 AND noise < 0.3, `T_NOISE=0.3`);
  33 new noise tests on A1+A3 (all 15 pairs) + A2 sample. Seam 1 resolved `(K5, K2)`-specific.

## Locked constants (pre-registered — do NOT change without a version bump + amendment)

- `beta = 4.0` — weight-map sensitivity, locked from v0.2. In `cit/induce.py` and
  `cit/induce_multi.py:BETA`.
- `NEURAL_SEED = 7` — K3 GRU init/SGD. CPU-only; `torch.use_deterministic_algorithms(True)`.
- `HMM_SEED = 0` — K4 Baum-Welch EM init. CPU/numpy deterministic. In `cit/proxies/mdl_hmm.py`.
- `DEFAULT_CORRELATION_THRESHOLD = 0.15` — A3 clustering, `cit/ablations/correlation_cluster.py`.
- `SEED = 42` — Shannon-recovery stochastic tests, `tests/test_shannon_recovery.py:SEED`.
- `STREAM_SEED = 42` — synthetic-stream generation. In `tests/test_induction_pipeline.py`,
  `test_cross_proxy_validation.py`, `test_cross_ablation_validation.py`, `test_multi_feature_substrate.py`.
- `ABLATION_SEED = 123` — ablation RNG (A1 LOO / A2 Shapley / A3 corr-cluster). Same four test files.
- Convergence thresholds: cross-proxy Spearman rho >= 0.5 (multi-feature substrate);
  cross-ablation rho >= 0.7 (A1 vs A2) plus per-symbol sign agreement.
- Collapse tolerances: algebraic identity `1e-12`; empirical convergence per-distribution
  atol in `pre_registration.md`.
- Capacity solver (v0.6.0): `tol = 1e-10`, `max_iter = 2000`, `lattice_m = 20`, no RNG
  (deterministic, bit-exact). In `cit/capacity.py`. Closed-form-anchor test atol `1e-8`
  (corrected from 1e-9 post-impl; the locked tol floors at ~1e-9 on the flat eps=0 max).
- Selective coder (v0.6.1): `ZSTD_LEVEL = 19`; achievability test atol `0.02` bits/sym at `N=200_000`.
  In `cit/coders/selective.py`. v0.6.2 win-margin: `WIN_MARGIN = 0.20`, `N=100_000`, seeded substrates.
- v0.7.0 categorical (`cit/proxies/categorical.py`, `cit/ablations/categorical.py`, `cit/metacoherence.py`):
  `SHUFFLE_SEED = 0` (K1/K5 time-shuffle surrogate baseline); K1 `ZSTD_LEVEL = 3`; feature-major bit-tight
  encoding (`ceil(log2 A)` bits/feature, channel-grouped -- the post-audit correctness fix, do NOT revert
  to step-major); `GRID_ABLATION_SEED = 123`; K3 `NEURAL_SEED=7`, K4 `HMM_SEED=0` carried. R2 threshold
  `0.6` / CI `0.4` LOCKED (currently a SEAM on D1's A1 column -- recorded, not adjusted).
- D1 substrate (v0.7.0, pre-registered; build pending): 3-state HSMM, mean dwell 200, dispersion
  `r=6`, `T=50_000`, `N_REPLICATES=20`; 8 alphabet-8 features (`F0_scale=1.7`; B lag `L=12`,
  `B_keep=0.35`; C additive mask; D drift `std=0.10`, `peak=1.0`); M5 partition coherence-bearing
  {f0..f4} / noise {f5..f7}. R2 threshold median Spearman `> 0.6` (CI `> 0.4`); bootstrap `B=1000`
  (block = mean sojourn 200). MARGINAL-RELATIVE coherence is a hard requirement. `cit/data/hsmm_d1.py`
  (pending). Calibrated by MI-balancing (Sec 5.4); exact K3xA1 ceiling verified in-build.

The locked record is `pre_registration.md`. If evidence forces a change: bump the
version, record the amendment in that file's history section, never silently edit.

## Open seam (do not "fix" silently)

Seam 1: `(K5, K2)` under A2 Shapley sits at Spearman 0.491, just under the 0.5
threshold. **Resolved at v0.5.5 as `(K5, K2)`-specific** — of all `(X, K2)` pairs under
A2 only K5 misses; K3, K4 (0.830), form B, K1 all clear — so the framework's operating
envelope is not restricted. It stays mechanically `xfail(strict=True)` as a documented
near-miss; leave it xfail (a strict XPASS forces re-evaluation) unless Benjamin directs otherwise.

## Test gating

- Default `pytest` runs fast only (`addopts = -m 'not slow and not very_slow'`).
- `slow` (~5-10 min): LOO + CorrCluster K5 + proxy invariants. Run with `-m slow`.
- `very_slow` (Shapley K5, ~135 min): `workflow_dispatch` only. Run with `-m very_slow`.
- K3 Shapley (A2) is ~4.3h/fixture, local-gated (exceeds 6h hosted ceiling). Hosted
  very_slow runs K5 family only via `-k "not K3"`.

## Working conventions (§8)

- One sub-step per "proceed." Hand steering back; no unsupervised bulk output.
- Surgical Python edits via `python << 'PYEOF'` with BOTH guards:
  `assert src.count(old) == 1` (anchor) AND `assert <distinctive-new-token> not in src`
  (idempotency — the anchor alone misses double-application after a clean first run).
- Heredocs use `MULTIEOF`, not `EOF`.
- ASCII-only in code payloads. Unicode allowed in README.md and pre_registration.md prose.
- Commits: two `-m` flags, dense paragraph body. Version strings `"vX.Y.Z: subject"`.
- Parse at the bit level, not byte level, where byte-level clips a metric to zero.
- Pre-register before implementation; if structural findings emerge, pre-register
  honestly rather than silently adjusting thresholds.

## Environment

- Python 3.11 / 3.12. `python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
- Deps: numpy<2, zstandard, numba>=0.60, torch>=2.0,<2.3.
- x86 <-> arm64 migration breaks bit-exact CI parity; treat as a multi-day
  measurement-and-amendment lift, not a quick port.

## Roadmap (next)

v0.6 program COMPLETE. v0.7 cross-domain (Metacoherence) IN PROGRESS: v0.7.0 D1 BUILT (slices 1-3,
uncommitted) -- generator + categorical K1-K5 + categorical A1/A2/A3 + R2/cross-tab machinery + the CI
verdict script. Headline result: the A1-column R2 is a SEAM (proxies recover COMPLEMENTARY properties,
median Spearman ~ -0.08 << 0.6), recorded honestly. IMMEDIATE next options: (a) run the A2 rescue
verdict via `scripts/run_metacoherence_grid.py --T 50000 --ablations A1,A2,A3` (CI/local, hours) to
decide if Shapley converges; (b) ship v0.7.0 as the D1 characterization (version bump) with the seam +
A2-pending recorded; (c) commit the build. Then v0.7.1 R1 (persistence), v0.7.2 R3 (interventions),
D2 (Pfam), D3 (FOMC), M5 + eight-cell capstone.
