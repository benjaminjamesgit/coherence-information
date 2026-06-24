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
  BUILT + record-corrected (slices 1-3, committed `823928a` + `f1d1da3`; full v0.7 chain `d9eb3b5`..`bbd081c`). D1 generator `cit/data/hsmm_d1.py`
  (seeds 7000..7019); categorical marginal-relative K1-K5 `cit/proxies/categorical.py`; categorical A1/A2/A3
  `cit/ablations/categorical.py`; `cit/induce_cat.py`; R2 + cross-tab `cit/metacoherence.py` (incl.
  `partition_diagnostic`, the +0.43 shared-top-k bound); CI verdict job `scripts/run_metacoherence_grid.py`.
  LOAD-BEARING lock HELD: coherence on D1 is MARGINAL-RELATIVE (predictive `H_marg - H_pred`; compression via
  a TIME-SHUFFLE surrogate baseline, `SHUFFLE_SEED=0`, feature-major bit encoding). **R2 result =
  INSTRUMENT-VALIDITY, NOT a falsification (corrected at `f1d1da3`):** on D1's A1 column the proxies recover
  COMPLEMENTARY properties (K5 {A,B,C,D}, K1 {A,C}, K2/K3/K4 {A,D}); the induced-w Spearman blocks {K1,K5}
  (within +0.68) vs {K2,K3,K4} (within 0.71-0.93) split COLLINEAR with the encoder boundary (byte-stream vs
  categorical-native), so philosophy and REPRESENTATION are CONFOUNDED -> `R2>0.6` NOT YET ADJUDICABLE (not
  falsification, not vindication). PROVISIONAL (single seed 7000, T=8000=16% of locked 50k; C most
  seed-variable). BANKED: property A converges across BOTH representations + all 5 proxies. Invariant (2)
  SPLIT (substrate-MI holds / induced-w fails at A1). The representation-vs-philosophy DECOUPLING CONTROL
  (modeling-on-byte-stream crossings K3b/K2b, A1, full-T, 20 seeds) RAN (2026-06-24): terminal verdict
  INCONCLUSIVE -- necessary-NOT-sufficient. It WEAKENS the representation-artifact reading (nothing leaned byte
  at full power) but does NOT establish philosophy: K3b leans modeling confidently (20/20, median +0.51) yet was
  pre-flagged as able to for trivial flexibility reasons (twin 0.88 is consistent with representation-invariance);
  K2b -- which probes the actual factorized C-blindness -- was UNSTABLE (17/20, one seed short). A pre-registered
  read-only I_C diagnostic REJECTED a property-dependent-representation explanation (the 3 negative-Delta seeds are
  NOT high-I_C; ranks [12,1,17], Spearman -0.25 n.s.), so the K2b near-miss is genuine borderline NOISE. Option
  (e)(i) (hold-encoding-constant) stays the recorded-but-UNJUDGED next control (see 2026-06-24 amendment). A3==A1
  on D1 (Pearson singletons); pre-reg line 791 corrected (K1/K5 were NOT alphabet-agnostic). PROGRAM REFRAME (2026-06-24 amendment, epistemics NOT results): D1's role recast as ESTIMATOR
  COVERAGE-CALIBRATION vs known ground truth -- the finding is DIFFERENTIAL coverage with K5 (parsing) MOST
  COMPLETE -- ASYMMETRIC, not compositional: K5 widest aperture (A,B,C,D), modeling-trio gapped {A,D},
  compression {A,C}, A universal; the union-recovers-all is CARRIED BY K5, NOT a composition (D2/D3 action:
  weight parsing widest, treat the trio/compression as specialized/confirmatory; the ranking itself is
  provisional -- single seed 7000, 16% T). So the D1 `R2>0.6` commitment is SUPERSEDED IN STATUS (not
  deleted, not edited). R2 reclassified DIAGNOSTIC: coverage-capped -- corroborating on convergence,
  NON-FALSIFYING on divergence (0.6/0.4 stay as a convergence flag; grid unchanged, still runs). R1 (persistence)
  + the v0.6.2 selective-compression FUNCTIONAL win ELEVATED to PRIMARY cross-domain evidence (functional
  convergence -- w doing the same work -- NOT weight-vector matching). R1 SPEC GUARD (pre-registered):
  functional convergence = PER-ESTIMATOR functional validity (each w predicts persistence, clean yes/no)
  AGGREGATED, NOT cross-estimator agreement on predictions (else R2's coverage-ambiguity returns in a functional
  costume; R1 escapes the ceiling by not requiring cross-estimator AGREEMENT, not by being coverage-free).
  Eight-cell matrix needs re-derivation under R2-as-diagnostic (capstone-pending). Sequenced next: v0.7.1 R1 (now PRIMARY); v0.7.2 R3; then D2 (Pfam, CC0),
  D3 (FOMC), M5 + capstone.
- Tests: 261 fast + 100 slow + 18 very_slow = 379 (1 xfail). v0.7.0: 13 D1-structure + 35 categorical-proxy
  + 8 categorical-ablation + 8 R2/cross-tab + 6 crossing-proxy (+1 slow) + 20 decoupling-control (+1 slow).
  v0.6.2: 12 empirics. v0.6.1: 23 coder. v0.6.0: 32 capacity.
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
  `SHUFFLE_SEED = 0` (K1/K5 time-shuffle surrogate baseline); K1 `_ZSTD_LEVEL_K1 = 3`; feature-major bit-tight
  encoding (`ceil(log2 A)` bits/feature, channel-grouped -- the post-audit correctness fix, do NOT revert
  to step-major); `GRID_ABLATION_SEED = 123`; K3 `NEURAL_SEED=7`, K4 `HMM_SEED=0` carried. R2 threshold
  `0.6` / CI `0.4` KEPT (number unchanged) but RECLASSIFIED by the bbd081c reframe: a CONVERGENCE FLAG,
  NOT a pass/fail gate -- R2 is DIAGNOSTIC (corroborating on convergence, non-falsifying on divergence,
  coverage-capped); falsifiability relocated to R1/R3 (pre-reg 2026-06-24 program reframe).
- v0.7.0 decoupling control (`cit/metacoherence.py`): `DECOUPLE_STABILITY_N = 18` (per-proxy sign-count
  supermajority of `N_REPLICATES=20`); `DECOUPLE_CONFIDENT = 0.40` / `DECOUPLE_WEAK = 0.10` (|median Delta|
  two-band magnitude); `CROSSING_REFS` (twin-excluded nine-cell refs for K3b/K2b); `DECOUPLE_PROXIES =
  PROXIES + (K3b, K2b)`. Crossings carry `NEURAL_SEED=7` (K3b) + `SHUFFLE_SEED=0`. NO locked constant VALUE
  was changed by ANY v0.7 work.
- D1 substrate (v0.7.0, pre-registered; BUILT): 3-state HSMM, mean dwell 200, dispersion
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

v0.6 program COMPLETE. v0.7 cross-domain (Metacoherence) IN PROGRESS, all committed on main through
`bbd081c`: v0.7.0 D1 build (`d9eb3b5`, `823928a`) + record-correction (`f1d1da3`, instrument-validity not
falsification) + decoupling control (pre-reg `7cca0c5`, proxies `231fd94`, metric `8277bdb`, wiring
`3ea5c50`, RESULT `d840553`) + program reframe (`bbd081c`). The decoupling control RAN -> verdict
INCONCLUSIVE / necessary-not-sufficient: K3b modeling-confident (20/20, median +0.51), K2b unstable
(17/20); a read-only I_C diagnostic REJECTED property-dependence, so K2b's near-miss is genuine NOISE;
(e)(i) hold-encoding-constant stays gated/unjudged. PROGRAM REFRAME (epistemics): D1 recast as ESTIMATOR
COVERAGE-CALIBRATION (DIFFERENTIAL coverage, K5/parsing MOST COMPLETE, ASYMMETRIC not compositional); R2
reclassified DIAGNOSTIC (0.6/0.4 kept as a convergence flag, non-falsifying on divergence); R1 (persistence)
+ the v0.6.2 selective-compression functional win ELEVATED to PRIMARY (per-estimator functional validity
AGGREGATED, NOT cross-estimator prediction-agreement -- the R1 spec guard). Eight-cell matrix needs
RE-DERIVATION under R2-as-diagnostic (capstone-pending). NEXT = v0.7.1 R1 (now PRIMARY); v0.7.2 R3; D2
(Pfam, CC0); D3 (FOMC); M5 + capstone. Deferred (not pre-judged): the A2-Shapley rescue verdict; the
R2-statistic all-pairs-vs-cross-philosophy-pairs decision.
