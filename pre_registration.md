# Pre-Registration: coherence-information

This document records, in advance of results, the parameters, seeds, thresholds, and methodological commitments that govern the empirical claims made by this codebase. Per James (2026), the framework is "vulnerable in the right way" only when commitments precede outcomes — this file is the structural record of those commitments.

**Commitment principle.** Once a parameter is locked for a given version, it cannot be silently changed in that version. If the empirical evidence requires a change, the version is bumped and the amendment is recorded in the history section at the bottom of this file.

---

## v0.1 — locked commitments

### Random seeds

| Seed | Use |
|------|-----|
| `42` | All stochastic tests in `tests/test_shannon_recovery.py` (parametrized random distributions, empirical convergence, upper-bound stress test) |

The seed is defined as `tests/test_shannon_recovery.py:SEED` and must not be changed within v0.1.

### Empirical-convergence tolerances

For `test_empirical_entropy_converges_to_true_entropy` at `n = 100_000` samples:

| Distribution | `atol` (bits) | Justification |
|--------------|---------------|---------------|
| `[0.25, 0.25, 0.25, 0.25]` (uniform) | `1e-3` | Leading-order variance term vanishes; only higher-order terms contribute |
| `[0.5, 0.3, 0.15, 0.05]` (skewed)    | `5e-3` | Standard error ≈ √((Σ p log² p − H²) / n) ≈ 3×10⁻³ |
| `[0.99, 0.01]` (near-deterministic)  | `5e-3` | Same first-order variance argument |

### Formal-collapse tolerance

For the boundary-condition tests (`H_w` with `w ≡ 1` equals `H`, etc.):

| Tolerance | Use |
|-----------|-----|
| `1e-12` | Algebraic-identity tests; gap should sit at floating-point precision |

---

## v0.2 — induction pipeline commitments (pre-registered, not yet implemented)

These lock the parameters that will govern the v0.2 implementation. Locking them now, before the code is written, prevents the parameters from drifting to fit data.

### Weight mapping

The induced-weight mapping follows the logistic form from James (2026), Step D:w(x) = σ(β · ρ(x))| Parameter | Value | Justification |
|-----------|-------|---------------|
| `β` (sensitivity) | `4.0` | Initial value. Will be calibrated by cross-validation on a held-out segment under a fixed rate budget, per cit_engineering.pdf §"Induced weights". |

### Proxy form

| Domain | Primary proxy | Sanity-check proxy |
|--------|---------------|--------------------|
| Synthetic (D₁) | Predictive log-loss (form B) | Compression-delta (form A) |
| Empirical (D₂, D₃) | Predictive log-loss (form B) | None until v0.4 |

Per cit_engineering.pdf: "Start with B for synthetic benchmarks (clean signal), then graduate to A when you want the compression link to be literal."

### Ablation operator

| Stage | Operator |
|-------|----------|
| v0.2 primary | A₁ (leave-one-out) |
| v0.3 additions | A₂ (Shapley, `k = 64` sampled coalitions), A₃ (correlation-cluster group ablation, Pearson threshold `0.5`) |

### Test seeds (locked for v0.2 test suite)

| Seed | Variable name | Use |
|------|---------------|-----|
| `42`  | `STREAM_SEED`   | Synthetic-stream generation in `tests/test_induction_pipeline.py` |
| `123` | `ABLATION_SEED` | Replace-with-uniform RNG in `tests/test_induction_pipeline.py` |

### Synthetic-stream parameters (locked for v0.2 test suite)

| Parameter | Value |
|-----------|-------|
| `n_steps` | `20_000` |
| `n_coherent` | `2` |
| `n_noise` | `3` |
| `self_transition_prob` | `0.9` |
| `noise_injection_prob` | `0.2` |

### Test invariants (locked for v0.2 test suite)

| Invariant | Threshold | Justification |
|-----------|-----------|---------------|
| `w(x) > 0.5` for x in `labels['coherence_bearing']` | strict | Structural: w(x) = σ(β·ρ), ρ > 0 ⇒ w > 0.5 |
| `w(x) < 0.5` for x in `labels['noise']` | strict | Structural: ρ < 0 ⇒ w < 0.5 |
| `min w(coherent) > max w(noise)` | strict | Class separation |
| `|w(x) - 0.5| < 0.2` on uniform i.i.d. streams | loose | At N=20,000 and β=4 the plug-in proxy std + replacement-noise std propagate to ~0.05–0.10 in w; the 0.2 bound is ~3σ above that |

### Ablation operator form

Leave-one-out is instantiated as **replace-with-uniform**: for each occurrence of the target symbol x, substitute a uniformly drawn symbol from the alphabet excluding x. Removal-based ablation was considered and rejected because it biases the proxy upward on shrinking alphabets, inverting the canonical sign convention.

---

## v0.3 — robustness harness (K₁ locked v0.3.0; K₂–K₅ pending)

### Estimator classes (per Metacoherence §3.1)

| ID  | Description |
|-----|-------------|
| K₁ | zstd compression, negative compressed length normalized by stream length |
| K₂ | Arithmetic-coded n-gram MDL, `n ∈ {3, 4, 5}`, averaged |
| K₃ | Small transformer with prequential coding, cumulative negative log-likelihood |
| K₄ | MDL search over HMM hidden-state cardinality and emission structure |
| K₅ | Lempel parsing factor enumeration (non-coding registrant; critical for cross-philosophy convergence per Metacoherence §3.1) |

### Convergence thresholds

| Metric | Threshold | Source |
|--------|-----------|--------|
| R2 cross-replicate Spearman (within-domain weight stability) | `≥ 0.7` | Metacoherence Appendix B.4 |
| M5 cross-domain ratio (mean-w over coherence-bearing vs noise features, rank-normalized) | Factor-of-2 consistency across all domain pairs for at least 3 of 5 estimator classes | Metacoherence §M5 |

### Replication

| Parameter | Value |
|-----------|-------|
| M (replicate streams per domain) | `20` |
| Shapley coalitions sampled per feature | `64` |

### K₁ implementation (locked v0.3.0)

| Item | Value |
|------|-------|
| Implementation | `cit.proxies.compression_delta.compression_delta_proxy` |
| Encoding | Smallest unsigned-int dtype: uint8 for K ≤ 256, uint16 for K ≤ 65 536, uint32 for K ≤ 2³² |
| Compressor | zstandard at level 3 |
| Mapping to [0, 1] | `Ĉ = 1 − len(compressed) / len(uncompressed)` |
| Clipping | Result clipped to [0, 1] for very-short-stream regimes where zstd frame-header overhead pushes the ratio above 1 |

### Cross-proxy convergence (locked v0.3.0)

The R2 threshold from Metacoherence §3.1 is operationalized in v0.3.0 as a **cross-proxy** test: Spearman rank correlation of ρ vectors between form B (predictive log-loss) and K₁ (compression-delta) `≥ 0.7`. This is the first empirical instance in this codebase of cross-philosophy convergence at the within-domain level — different epistemic bases (predictive vs coding) agreeing on which symbols carry coherence-bearing structure.

| Test invariant | Threshold | Justification |
|----------------|-----------|---------------|
| Canonical signs under K₁: ρ > 0 for coherence-bearing, ρ < 0 for noise | strict | Replace-with-uniform destroys structure x participates in; signal direction is invariant to estimator class |
| `min ρ(coherent) > max ρ(noise)` under K₁ | strict | Class separation under K₁ |
| `w(coherent) > 0.5` and `w(noise) < 0.5` under K₁ via `induce_weights` | strict | Sigmoid inherits sign |
| Sign agreement on every symbol between form B and K₁ | strict | Cross-philosophy convergence at the per-symbol sign level |
| Spearman ρ rank correlation between form B and K₁ ρ vectors | `≥ 0.7` | R2 threshold (Metacoherence §3.1 and Appendix B.4) |

---

## v0.4 — cross-ablation validation (A₂ locked v0.4.0; A₃ deferred to v0.5)

Locks the ablation axis of the Metacoherence §3.1 robustness grid. Cross-philosophy convergence between A₁ (leave-one-out) and A₂ (Shapley) is the symmetric pair to v0.3's cross-proxy R2 invariant (form B vs K₁). Agreement at the rank-correlation level demonstrates that the ρ signal is not an artifact of the ablation strategy.

### A₂ implementation (locked v0.4.0)

| Item | Value |
|------|-------|
| Implementation | `cit.ablations.shapley.shapley_ablation` |
| Coalitions sampled per feature | `k = 64` |
| Ablation operator | Replace-with-uniform from kept set (same form as A₁ — isolates ablation strategy from operator drift) |
| Centering | `center = True` by default; subtracts cohort-mean raw ρ |
| Centering rationale | Adding any symbol to the kept set enlarges the replacement alphabet at ablated positions, raising entropy and depressing the proxy. The dilution penalty pushes all marginals negative regardless of structural relevance; rank order survives but absolute LOO-style signs do not. Cohort-mean centering is the standard normalization in cooperative-game Shapley when the operator's absolute baseline is operator-dependent. |
| Seed | `ABLATION_SEED = 123` (reused from A₁) |
| Return dict | Includes `"centered": bool` key alongside `"rho"` and `"c_ablated"` |

### Cross-ablation convergence (locked v0.4.0)

Operationalizes the Metacoherence §3.1 R2 threshold at the ablation axis. v0.3 closed the proxy axis (form B vs K₁); v0.4 closes the symmetric pair.

| Test | Threshold | Rationale |
|------|-----------|-----------|
| Per-symbol sign agreement: `sign(ρ_A₁(x)) == sign(ρ_A₂(x))` for all `x` | strict | Stricter than rank correlation: requires both operators to agree on the structural-vs-noise classification of every symbol, not just their relative ordering. |
| Spearman rank correlation of ρ vectors across A₁ and A₂ | `≥ 0.7` | R2 threshold from Metacoherence §3.1, operationalized at the ablation axis. Same threshold v0.3 locked at the proxy axis — keeps the robustness grid symmetric across the (proxy, ablation) pair. |
| `induce_weights` under A₂: `w(coherent) > 0.5`, `w(noise) < 0.5`, `|w − 0.5| < 0.2` | locked | Same locked invariant as A₁ (v0.2). Confirms the swappable-ablation contract: same stream → same class separation under the same locked β = 4.0, independent of ablation operator. |

### A₃ (correlation-cluster) deferral

Pre-registered for v0.5. Metacoherence §3.2 specifies A₃ as feature-stream Pearson clustering — grouping features by correlation and ablating cluster-wise. The v0.4 substrate is single-symbol streams where each "feature" is a symbol indicator vector. Indicator-vector clustering on single-symbol streams does not reliably group coherence-bearing symbols: the dependency structure A₃ is designed to exploit (cross-feature correlation under shared latent structure) is not exposed by the substrate. Implementing A₃ on this substrate would produce a no-op or near-no-op operator and fail to falsify anything meaningful.

A₃ is therefore deferred to v0.5, where it lands alongside the K₂–K₅ estimators and a multi-feature synthetic substrate that exposes the required correlation geometry. v0.5 closes the full {K} × {A} robustness grid within-domain; v0.4's grid is the (A₁, A₂) pair at the form B / K₁ proxy slice.

---

## v0.7 — cross-domain validation (not yet implemented)

The cross-domain validation architecture from Metacoherence Appendix A. Domain specifications D₁, D₂, D₃ will be pre-registered in an amendment to this file before v0.5 implementation begins. The eight-cell outcome interpretation matrix from Metacoherence §8.3–8.4 will be reproduced verbatim and bound to outcomes in advance.

---

## Amendment history

No amendments yet. Initial registration committed in the v0.1 first commit.
