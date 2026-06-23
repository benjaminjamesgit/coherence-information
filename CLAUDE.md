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

- Version `0.5.5` (pyproject + README). v0.5.5 = capstone (noise-only falsifiability + Seam 1 resolution).
- Proxies (K_n): K1 compression-delta (zstd), K2 n-gram MDL, K3 neural prequential
  (single-layer GRU), K4 MDL-HMM (factorized-Bernoulli HMM, two-part MDL selection over
  H in {1,2,3,4}, deterministic Baum-Welch, `HMM_SEED=0`), K5 Lempel parsing (bit-level LZ76, numba).
- Ablations (A_m): A1 LOO replace-with-uniform, A2 Shapley (k=64), A3 correlation-cluster.
- Tests: 127 fast + 75 slow + 18 very_slow (1 xfail). v0.5.5: noise-only counterfactual
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

v0.6 capacity estimator (C_C = max I_w(X;Y)) + weighted typical-set coder /
Selective Compression -> v0.7 cross-domain (Metacoherence).
