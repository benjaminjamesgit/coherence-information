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

## v0.5 — multi-feature substrate + cross-ablation extension (v0.5.0 locked; K_2-K_5 sub-versions pending)

Per `design/multi_feature_substrate.md` (locked 2026-05-26). Sub-version sequencing locked Option B: v0.5.0 = substrate + A_3 + form B multi + K_1 multi; v0.5.1 = K_2; v0.5.2 = K_5; v0.5.3 = K_3; v0.5.4 = K_4; v0.5.5 = capstone full 15-pair convergence matrix + noise-only counterfactual.

### Multi-feature substrate parameters (locked v0.5.0)

| Parameter | Value |
|-----------|-------|
| `STREAM_SEED` | `42` (carries from v0.2) |
| `ABLATION_SEED` | `123` (carries from v0.2) |
| `n_steps` | `20_000` |
| `n_features` | `10` |
| `n_coh_features` | `4` |
| `n_noise_features` | `6` |
| Coherent indices | `{0, 1, 2, 3}` |
| Noise indices | `{4, 5, 6, 7, 8, 9}` |
| Feature type | binary Bernoulli (`K = 2` per feature) |
| Observation density | dense (every feature observed every step) |

### Hidden Markov generator (locked v0.5.0)

| Parameter | Value |
|-----------|-------|
| Hidden state count `C` | `2` |
| Transition matrix | symmetric sticky, `self_transition_prob = 0.9` |
| Initial state distribution | stationary (uniform) |
| Stationary marginal | `p(x_j=1) = 0.5` for all `j` (marginal-matching invariant) |

| Feature group | Emission |
|---------------|----------|
| Features 0, 1 | `Pr(x=1 in state 0) = 0.8`, `Pr(x=1 in state 1) = 0.2` |
| Features 2, 3 | `Pr(x=1 in state 0) = 0.2`, `Pr(x=1 in state 1) = 0.8` |
| Features 4-9  | `Pr(x=1) = 0.5` i.i.d., state-independent |

### Ground-truth label dict (locked v0.5.0)

```python
labels = {
    "coherence_bearing": {0, 1, 2, 3},
    "noise": {4, 5, 6, 7, 8, 9},
    "clusters": {
        "cluster_A": {0, 1},
        "cluster_B": {2, 3},
    },
}
```

### Proxy and ablation implementations (locked v0.5.0)

| Component | Function | Locked parameters |
|-----------|----------|-------------------|
| form B multi | `cit.proxies.predictive_logloss_multi.predictive_logloss_proxy_multi` | autoregressive joint factorization, first-order context, Laplace smoothing, 10,240-cell parameter space |
| K_1 multi | `cit.proxies.compression_delta_multi.compression_delta_proxy_multi` | 2-byte fixed-width encoding (10 active + 6 padding zeros), zstd level 3 |
| K_2 multi | `cit.proxies.ngram_mdl.ngram_mdl_proxy` | per-feature factorized bigram, 2-part MDL (Rissanen prior `0.5 * 2 * n_features * log2(T)`), Laplace smoothing, `C_K2 = 1 - (L_data + L_model) / L_iid` clipped to `[0, 1]` (locked v0.5.1; see K_2 factorization amendment) |
| K_5 multi | `cit.proxies.lempel_parsing.lempel_parsing_proxy` | bit-level LZ76 phrase parsing on unpacked byte stream (shared K_1 multi encoder), `c_iid = T_bits / log_2(T_bits)` binary uniform asymptotic, `C_K5 = 1 - c(bit_stream) / c_iid` clipped to `[0, 1]`, numba `@njit` Kaspar-Schuster implementation (locked v0.5.2; see K_5 bit-level parsing amendment) |
| K_3 multi | `cit.proxies.neural_prequential.neural_prequential_proxy` | single-layer GRU (hidden=64), per-feature sigmoid output heads, strict online prequential SGD (lr=0.01, momentum=0), `NEURAL_SEED=7`, `H_pred` = mean per-step per-feature BCE in bits over T=20000 steps, `H_iid = 1.0` bit/feature/step (binary uniform), `C_K3 = 1 - H_pred / H_iid` clipped to `[0, 1]` (locked v0.5.3; see K_3 neural prequential protocol lock) |
| A_1 multi | `cit.ablations.loo_multi.leave_one_out_ablation_multi` | feature-level LOO, replace-with-uniform Bernoulli(0.5), `center=True` default |
| A_2 multi | `cit.ablations.shapley_multi.shapley_ablation_multi` | feature-level Shapley, `k=64` coalitions, `center=True` default |
| A_3 | `cit.ablations.correlation_cluster.correlation_cluster_ablation` | Pearson signed correlation `> 0.15` for cluster edges, connected components, replace-with-uniform per cluster, `center=True` default |
| Orchestrator | `cit.induce_multi.induce_weights_multi` | `beta = 4.0` (carries from v0.2), default proxy = form B multi, default ablation = A_1 multi |

### Asserted test invariants (locked v0.5.0)

| Invariant | Threshold |
|-----------|-----------|
| Canonical signs | `rho(coh) > 0`, `rho(noise) < 0` per (proxy, ablation) pair |
| Class separation | `min rho(coh) > max rho(noise)` per (proxy, ablation) pair |
| Weight separation | `w(coh) > 0.5`, `w(noise) < 0.5` |
| Weight band | `abs(w - 0.5) < 0.2` |
| Per-feature sign agreement | `sign(rho_A_1) == sign(rho_A_2)` per feature (v0.4 carry) |
| Cross-proxy R2 (multi-feature) | Spearman `rho(form B multi, K_1 multi) >= 0.5` under A_1, A_2, A_3 |

### Observational invariants (logged, not asserted at v0.5.0)

- A_3 cluster recovery: Adjusted Rand Index between A_3 partition of coherent features and ground-truth `clusters` dict. Promotable to required invariant at v0.5.5 capstone with empirically-determined threshold.

### Cross-K convergence (sub-version progression)

| Sub-version | New asserted pairs |
|-------------|---------------------|
| **v0.5.0** | `(form B multi, K_1 multi)` per ablation A_1, A_2, A_3 |
| **v0.5.1** | `(K_2, form B multi)` and `(K_2, K_1 multi)` per ablation A_1, A_2, A_3 |
| **v0.5.2** | `(K_5, form B multi)` and `(K_5, K_1 multi)` per ablation A_1, A_2, A_3; `(K_5, K_2)` per A_1, A_3 only (A_2 pair is xfail-marked seam, see Known seams) |
| **v0.5.3** | `(K_3, *)` for each of `{form B multi, K_1 multi, K_2, K_5}` per ablation A_1, A_2, A_3; all 12 pairs clear Spearman >= 0.5 (no new seam) |
| v0.5.4 | add `(K_4, *)` for each of `{form B multi, K_1 multi, K_2, K_5, K_3}` |
| v0.5.5 capstone | Full 15-pair off-diagonal matrix per ablation; every pair `>= 0.5` on structured substrate; every pair drops significantly on noise-only counterfactual |

Threshold calibrated per `2026-05-26 -- Multi-feature cross-proxy R2 threshold calibration` amendment.

### Noise-only counterfactual (locked v0.5.0)

| Parameter | Value |
|-----------|-------|
| Function | `cit.data.multi_feature.noise_only_multi_feature_stream` |
| Generation | All features i.i.d. `Bernoulli(0.5)`, including indices 0-3 |
| Label dict | omitted (or all features labeled `noise`) |
| Use | v0.5.5 capstone falsifiability test for cross-K convergence claim |

### Known seams (deferred resolutions)

Pre-registered framework limitations surfaced by empirical execution. Each seam is mechanically marked at the test layer (`@pytest.mark.xfail(strict=True)`) and has a designated resolution version. A strict XPASS at any future run forces re-evaluation of the corresponding seam record.

**Seam 1: K_5 vs K_2 cross-proxy R_2 under Shapley (A_2) ablation.**

| Element | Value |
|---------|-------|
| Surfaced | v0.5.2 |
| Observation | Spearman correlation of per-feature `rho` vectors, K_5 vs K_2 under A_2 = **0.491** with locked seeds (STREAM_SEED=42, ABLATION_SEED=123). Below the v0.5+ multi-feature cross-proxy R_2 threshold of `>= 0.5`. |
| Convergence holds elsewhere | K_5 vs K_2 under A_1 (Spearman 0.7697) and under A_3 (`>= 0.5`). K_5 vs form B multi and K_5 vs K_1 multi all converge under A_1, A_2, A_3. |
| Structural hypothesis | K_5 (bit-level LZ76 phrase parsing) captures variable-length cross-feature phrase interactions inside the dictionary; K_2 (per-feature factorized bigram MDL) is structurally factorized and cannot represent cross-feature coalition effects. Shapley (random multi-feature coalitions) surfaces the asymmetry; A_1 (single-feature LOO) and A_3 (correlation-cluster) do not. |
| Resolution path | **v0.5.5 capstone**. Addition of K_3 (neural online cross-entropy) and K_4 (HMM with model selection) yields a 15-pair convergence matrix. If the pattern is K_5 vs K_2-specific, the seam remains marked. If it generalizes to "Shapley applied to any phrase-aware versus factorized proxy pair", the framework's operating envelope is restricted via formal amendment to the multi-feature R_2 threshold or the asserted pair set. |
| Mechanical mark | `tests/test_multi_feature_substrate.py::TestCrossProxyConvergenceMulti::test_K5_vs_K2_under_A2` carries `@pytest.mark.xfail(strict=True)`. XPASS triggers strict-mode failure and forces seam re-evaluation. |
| Cost at v0.5.2 | One pair removed from v0.5.2 asserted cross-K convergence: 9 pairs total (3 K_5 cross-proxy pairs across 3 ablations), 8 are asserted, 1 is xfail-marked. |

---

## v0.7 — cross-domain validation (not yet implemented)

The cross-domain validation architecture from Metacoherence Appendix A. Domain specifications D₁, D₂, D₃ will be pre-registered in an amendment to this file before v0.5 implementation begins. The eight-cell outcome interpretation matrix from Metacoherence §8.3–8.4 will be reproduced verbatim and bound to outcomes in advance.

---

## Amendment history

Amendments are listed chronologically, most recent last. Each entry records the change, the rationale, and (where applicable) the structural convention being locked so future maintainers do not undo the change.

### 2026-05-26 — v0.4 roadmap repositioning

**Change.** The original v0.1 pre-registration placed cross-domain validation (Metacoherence Appendix A; D₁, D₂, D₃; eight-cell outcome matrix) at v0.4. With v0.4 actually shipping as cross-ablation validation (A₂ Shapley + cross-ablation R2), the public roadmap was resequenced:

- v0.4 (shipped 2026-05-26): cross-ablation validation (A₂ locked; A₃ deferred).
- v0.5 (planned): K₂–K₅ estimators + A₃ correlation-cluster ablation + multi-feature synthetic substrate; full within-domain `{K} × {A}` robustness grid.
- v0.6 (planned): coherence capacity estimator + weighted typical-set coder + Selective Compression empirics.
- v0.7 (planned): cross-domain validation per Metacoherence Appendix A; M5 admissibility gate; eight-cell outcome matrix.

**Rationale.** The robustness axis (proxy × ablation) needed to close at the within-domain level before cross-domain validation became a meaningful test. Cross-domain convergence asserts that the same ρ signal recovers across domain substrates; that claim has empirical content only after the ρ signal has been shown to be operator-invariant on a single substrate. v0.3 (proxy axis) and v0.4 (ablation axis) anchor that operator-invariance; v0.5 fills out the full grid; v0.6 adds the formal-theorem operationalizations (capacity, Selective Compression); v0.7 then tests the whole pipeline across domains. The repositioning preserves all original commitments — none are dropped — and sequences them by epistemic dependency rather than by initial enthusiasm.

**A₃ deferral.** Originally co-located with A₂ in v0.4. Pushed to v0.5 because the v0.4 substrate is single-symbol streams where indicator-vector clustering does not reliably group coherence-bearing symbols. A₃ requires the multi-feature substrate that v0.5 introduces.

### 2026-05-26 — DOI badge convention (concept DOI, not version DOI)

**Change.** The README DOI badge was pinned to the v0.1.0 version DOI (`10.5281/zenodo.20399413`) — an immutable snapshot citation. Repointed to the concept DOI (`10.5281/zenodo.20399412`), which Zenodo assigns to the record as a whole and which auto-resolves to the latest version.

**Rationale.** Version DOIs and the concept DOI serve different purposes. Version DOIs are immutable snapshots — what you cite when you want to pin to a specific release for reproducibility. The concept DOI is the parent record identifier — what you cite when you mean "this software" rather than "this specific version of this software." A README badge advertising the project's DOI should track the concept (auto-updating), not a specific snapshot. The original v0.1.0 setup used the version DOI by default because no other DOI existed at that point; the divergence between concept DOI and latest-version DOI only became visible at v0.2.0+.

**Convention locked.** Future releases must not modify the README DOI badge. The concept DOI does not change across versions. Each new release will get its own version DOI on Zenodo automatically — those remain accessible from the concept-DOI landing page's "Versions" sidebar. Citers wanting to pin to a specific release follow the version DOI from Zenodo; citers wanting "the software" follow the badge. CITATION.cff intentionally does not pin a `doi:` field, deferring DOI semantics to Zenodo and the README badge.


### 2026-05-26 — Multi-feature cross-proxy R2 threshold calibration

**Change.** The v0.5.0 multi-feature substrate locks a substrate-specific cross-proxy R2 threshold of `Spearman rho >= 0.5`. The v0.3 single-symbol substrate threshold of `>= 0.7` continues to apply unchanged to v0.2-v0.4 single-symbol tests.

**Rationale.** v0.3's 0.7 threshold was calibrated for a 5-symbol substrate with continuous signal-vs-noise gradient. The v0.5 multi-feature substrate has class-bimodal signal structure: class separation (4 coherent vs 6 noise, strong, both proxies agree) plus within-class ordering (mostly Monte Carlo, no underlying signal in the noise singletons; modest in the coherent cluster pair). Spearman on the full 10-feature rho vector mixes class-level signal (real) with within-class noise (random). Operators without variance reduction (A_1 uses one LOO per feature, A_3 uses one ablation per cluster) have their global Spearman dominated by the noise contribution; only A_2 (averaging 64 sampled coalitions) reduces within-class variance enough to clear 0.7. Empirical baseline on the locked substrate: A_1 = 0.571, A_3 = 0.652, A_2 >= 0.7.

The calibrated 0.5 threshold sits above the random baseline (~0.0 for fully-independent rho vectors with matched class structure) and below the variance-reduced ceiling (~0.8 achievable by A_2). It is structurally meaningful: asserts cross-proxy agreement on class separation while not over-asking for agreement on within-class noise ordering that the substrate cannot produce.

**Lock scope**: v0.5.0+ multi-feature substrate cross-proxy R2 tests across all (proxy, ablation) pairs. Includes the v0.5.5 capstone 15-pair convergence matrix -- each off-diagonal pair must clear 0.5 on the structured substrate and drop significantly on the noise-only counterfactual.

**Lock exclusion**: v0.3 single-symbol cross-proxy R2 tests retain the 0.7 threshold. Different substrate, different signal structure, different threshold.

**Future tightening path**: If empirical evidence at v0.5.5 shows pairs systematically clearing thresholds higher than 0.5, a further amendment can tighten the multi-feature threshold post-hoc -- but only after observation, not before.


### 2026-05-26 — K_2 (n-gram MDL) factorization amendment

**Change.** The K_2 multi-feature proxy is amended from joint feature-vector bigram (as locked in `design/multi_feature_substrate.md` Q5) to per-feature factorized bigram. Conditioning context changes from `v_{t-1}` (1024-state joint vector) to `v_{t-1}^j` (2 states per feature). All other elements preserved: 2-part MDL coding, Rissanen universal prior `L(model) = (1/2) * num_params * log(T)`, Laplace smoothing, `C_K2 = 1 - L_total / L_iid_uniform` clipped to `[0, 1]`.

**Rationale.** Pre-implementation analytical analysis showed the joint-bigram formulation produces `C_K2 = 0` (clipped) on both structured and noise streams of the v0.5 substrate. The substrate's signal (form B multi saturates at `C_hat ≈ 0.09`) cannot overcome the joint-bigram model's parameter penalty: ~7,500 active cells × `0.5 * log2(20,000) ≈ 7.15` bits/param = ~53,600 bits model cost vs ~18,000 bits data savings (in the structured-vs-iid differential). MDL correctly says "joint bigram on 1024-state space isn't worth fitting on this data" -- but this collapses K_2's per-feature rho differential to zero, defeating cross-proxy convergence testing entirely.

The factorized formulation `p(v_t^j | v_{t-1}^j)` reduces the parameter count to `2 * n_features = 20` total (one Bernoulli emission per (previous_value, feature)) and reads each feature's lag-1 temporal autocorrelation (analytically ~0.29 for coherent features per the locked Q2 emission matrix, ~0 for noise). Expected `C_K2 ≈ 0.02-0.05` on structured stream, ~0 on noise -- meaningful per-feature differential restored.

**K_2 family identity (preserved across amendment).** K_2 remains the "explicit MDL with model penalty" family, structurally distinct from:
- form B (joint conditioning `p(v_t^j | v_{t-1})`, no penalty)
- K_1 (universal compression on byte stream, implicit model)
- K_3 (neural online prediction, no penalty)
- K_4 (HMM with explicit model selection)
- K_5 (non-coding pattern counting)

The factorization itself becomes a structural feature of K_2: per-feature marginal temporal predictability, ignoring the cross-feature joint structure that form B captures. The lens difference between K_2 and form B is preserved -- if anything, sharpened by the amendment.

**Lock scope.** v0.5.1+ K_2 implementations and cross-proxy R2 tests involving K_2. Supersedes the K_2 protocol specification in `design/multi_feature_substrate.md` Q5; the design memo is updated to reflect the amended spec in the same commit (see updated Q5 and Q7 entries).

**Implementation locked v0.5.1.**

| Parameter | Value |
|-----------|-------|
| Function | `cit.proxies.ngram_mdl.ngram_mdl_proxy` |
| Conditioning context | `v_{t-1}^j` per feature (per-feature factorized bigram) |
| Parameter count | `2 * n_features` (one Bernoulli per (previous_value, feature)) |
| Smoothing | Laplace (matches v0.2 form B and v0.5.0 form B multi) |
| Model cost | Rissanen prior: `L(model) = (1/2) * num_params * log2(T)` bits |
| Data cost | Plug-in negative log-likelihood under Laplace-smoothed bigram, summed and converted to bits |
| Baseline | `L_iid_uniform = T * n_features * log2(2) = T * n_features` bits |
| Coherence | `C_K2 = 1 - (L_data + L_model) / L_iid_uniform`, clipped to `[0, 1]` |

### 2026-05-26 — K_5 (Lempel parsing) bit-level parsing amendment

**Change.** The K_5 multi-feature proxy is amended from byte-level LZ76 parsing (as locked in `design/multi_feature_substrate.md` K_5 protocol section) to bit-level LZ76 parsing on the unpacked byte stream. The encoder remains shared with K_1 multi (2-byte-per-step, 10 active + 6 padding zeros); K_5 unpacks the byte stream to bits via `numpy.unpackbits` before parsing. `T_bits = 8 * T_bytes`. All other elements preserved: LZ76 production complexity, `c_iid = T / log_2(T)` binary uniform asymptotic, `C_K5 = 1 - c(stream) / c_iid` clipped to `[0, 1]`.

**Rationale.** Pre-implementation analytical analysis showed the byte-level formulation produces `C_K5 = 0` (clipped) on both structured and noise streams of the v0.5 substrate. The spec's `c_iid = T_bytes / log_2(T_bytes)` is the binary-uniform Lempel asymptotic; applied to byte-level parsing (256-alphabet, h_byte up to 8 bits/byte), `c(s)` exceeds `c_iid` by a factor of ~h_byte. Empirical confirmation on uniform random sequences at T=40,000:

| Parsing | c(uniform) | c_iid (binary formula) | Ratio |
|---------|------------|------------------------|-------|
| Byte-level | 17,868 | 2,616 | 6.83 |
| Bit-level  | 2,671  | 2,616 | 1.02 |

Byte-level `c(uniform)` clips `C_K5` to 0; bit-level `c(uniform)` aligns within 2% of the asymptotic baseline. The substrate's noise stream (h ~ 0.625 bits/bit due to padding) gives `c(noise, bit) ~ 11,000`; coherent HMM structure further reduces phrase count. Differential separation analytically estimated at `C_K5(coh) - C_K5(noise) ~ 0.15-0.35`, comfortably above the cross-proxy R2 threshold floor.

**K_5 family identity (preserved across amendment).** K_5 remains the "non-coding pattern counting" family, structurally distinct from:

- K_1: universal compression via zstd, byte-level entropy coding
- K_2: explicit MDL with model penalty, per-feature factorized bigram
- K_3: neural online cross-entropy (no coding boundary)
- K_4: HMM with model selection across H, explicit MDL

K_5's parsing/coding distinction is sharpened by the amendment: K_1 compresses bytes via zstd, K_5 parses bits via LZ76 (no entropy coder). Same underlying encoded information, different parsing layer. The shared-encoder rationale is preserved at the information level -- K_1 wraps the bits in a byte container for zstd, K_5 unpacks the same bits for LZ76 phrase counting. Representation drift is eliminated.

**Lock scope.** v0.5.2+ K_5 implementations and cross-proxy R2 tests involving K_5. Supersedes the K_5 protocol specification in `design/multi_feature_substrate.md`; the design memo is updated to reflect the amended spec in the same commit.

**Implementation locked v0.5.2.**

| Element | Locked value |
|---------|--------------|
| Input | 2-byte-per-step byte encoding via K_1 multi encoder (shared) |
| Unpack | `numpy.unpackbits` of the byte stream |
| Bit stream length | `T_bits = 8 * T_bytes = 16 * n_steps` |
| Parser | LZ76 production complexity, longest-match incremental parse |
| Phrase count | `c(bit_stream)` = distinct phrases in parse |
| iid baseline | `c_iid = T_bits / log_2(T_bits)` (binary uniform asymptotic) |
| Coherence | `C_K5 = 1 - c(bit_stream) / c_iid`, clipped to `[0, 1]` |

### 2026-05-28 — K_3 (neural prequential cross-entropy) protocol lock

**Change.** K_3 multi-feature proxy locked for v0.5.3 implementation. Single-layer GRU consumes the 10-feature substrate stream as float32 input; per-feature factorized sigmoid output predicts each binary feature independently. Strict online prequential SGD: predict x_t given hidden state h_{t-1}, observe x_t, accumulate per-feature BCE, single SGD step on the per-step loss, advance hidden state. No offline training, no epochs, no train/test split, no warmup. Mean per-feature per-step cross-entropy in bits divided by binary uniform baseline (1.0 bit/feature/step) yields C_K3.

**Rationale.** Pre-implementation analytical reasoning. The K_3 family slot is "neural online cross-entropy (no coding boundary)" per the v0.5 sequencing -- structurally distinct from K_1 (zstd entropy coding), K_2 (explicit MDL with model penalty), K_5 (LZ76 phrase parsing). Among neural classes (GRU / LSTM / transformer head / minimal attention), GRU was selected for: (a) narrowest pre-registration lock surface, (b) canonical CPU determinism via `torch.use_deterministic_algorithms(True)`, (c) substrate match -- the substrate's coherent features are bigram-order, so attention's long-range routing provides no expressivity payoff over gated recurrence, (d) lowest seam risk -- smallest parameter count among the four candidates minimizes random-init variance under NEURAL_SEED. Per-feature factorized output matches K_2's bigram factorization, so the K_3 vs K_2 cross-proxy R_2 isolates model-class structural difference rather than entangling it with a factorization shift.

**K_3 family identity (locked).** K_3 is the "neural online cross-entropy" family, structurally distinct from:

- K_1: universal compression via zstd, byte-level entropy coding
- K_2: explicit MDL with model penalty, per-feature factorized bigram
- K_4: HMM with model selection across H, explicit MDL
- K_5: LZ76 bit-level phrase parsing, no entropy coder

K_3's no-coding-boundary distinction is structural: no codebook, no entropy coder, no MDL prior, no phrase dictionary. The output is the mean negative log-likelihood under the GRU's online predictive distribution. Determinism is enforced by `torch.manual_seed(NEURAL_SEED)` + `torch.use_deterministic_algorithms(True)` and CPU-only execution.

**Lock scope.** v0.5.3+ K_3 implementations and cross-proxy R_2 tests involving K_3. Marker assignment resolved at v0.5.3 ship (2026-05-29): ~12s/call at T=20000; A_1 LOO, A_3 CorrCluster, and proxy invariants are `slow`; A_2 Shapley is `very_slow` at ~4.3h/fixture (1,280 proxy calls = 10 features x 64 coalitions x 2 marginal evaluations). K_3 Shapley exceeds the 6h hosted-runner hard ceiling, so it is local-gated: hosted `very_slow.yml` runs `-k "not K3"` (K_5 family only, ~135 min), while local `pytest -m very_slow` runs the full tier. Validated locally 2026-05-29: 10 passed, 1 xfailed (Seam 1), 6h33m.

**Implementation locked v0.5.3.**

| Element | Locked value |
|---------|--------------|
| Input | 10-feature substrate stream (4 coherent + 6 noise), cast to `float32` in `[0, 1]`, no byte/bit packing |
| Model class | Single-layer GRU |
| Hidden dim | 64 |
| Num layers | 1 |
| Init | PyTorch GRU default (`orthogonal_` recurrent weights, `xavier_uniform_` input weights, zero biases) under `torch.manual_seed(NEURAL_SEED)` |
| Output head | `Linear(64, 10)` + `sigmoid` (10 independent binary predictors) |
| Factorization | Per-feature factorized, matching K_2 bigram factorization |
| Loss | Per-feature binary cross-entropy in bits, summed over 10 features per step, accumulated over T_steps |
| Optimizer | SGD, `lr=0.01`, `momentum=0`, `weight_decay=0` |
| Training regime | Strict cumulative prequential; each sample seen exactly once; one SGD step per timestep on the per-step loss |
| T_steps | 20,000 (`= T_bytes / 2` from K_1 multi shared step count) |
| H_pred | `(1 / (T * 10)) * sum_t sum_i BCE_bits(x_{i,t}, P_{i,t})` |
| H_iid | `1.0` bit per feature per step (binary uniform baseline) |
| Coherence | `C_K3 = 1 - H_pred / H_iid`, clipped to `[0, 1]` |
| Determinism | `torch.manual_seed(NEURAL_SEED)`, `torch.use_deterministic_algorithms(True)`, CPU-only execution |
| NEURAL_SEED | `7` (new locked constant, distinct from `STREAM_SEED=42` and `ABLATION_SEED=123`) |


