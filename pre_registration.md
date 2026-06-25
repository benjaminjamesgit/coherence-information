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
| K_4 multi | `cit.proxies.mdl_hmm.mdl_hmm_proxy` | factorized Bernoulli HMM, MDL model selection over `H in {1,2,3,4}`, Baum-Welch EM (single deterministic init `HMM_SEED=0`, `max_iter=100`, `tol=1e-4`), `num_params(H) = H(H-1) + H*n_features + (H-1)`, `C_K4 = 1 - (L_data(H*) + L_model(H*)) / (T*n_features)` clipped to `[0, 1]` (locked v0.5.4; see K_4 MDL-HMM protocol lock) |
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
| **v0.5.4** | add `(K_4, *)` for each of `{form B multi, K_1 multi, K_2, K_5, K_3}` per ablation A_1, A_2, A_3 (15 pairs). 13 measured and clear Spearman >= 0.5; the 2 remaining A_2 pairs (vs K_5, vs K_3) gated to the full very_slow run (not seam-risk). `(K_4, K_2)` under A_2 -- the Seam 1 structural twin -- measured **0.830**: no new seam. `(K_4, form B)` = 0.733, `(K_4, K_1)` = 0.915 under A_2; all A_1/A_3 pairs clear (see 2026-06-22 amendment + Seam 1 record) |
| **v0.5.5 capstone** | Consolidate the full 15-pair structured matrix (every pair Spearman `>= 0.5`; built v0.5.0-v0.5.4). Noise-only counterfactual operationalized: each pair noise-only Spearman `< 0.3` (`T_noise` locked) AND structured `>= 0.5`; asserted on A_1 + A_3 for all 15 pairs, A_2 (Shapley) noise sampled on the 3 cheap-proxy pairs. Seam 1 resolved: `(K_5, K_2)`-specific (see Seam 1 record + 2026-06-23 amendment) |

Threshold calibrated per `2026-05-26 -- Multi-feature cross-proxy R2 threshold calibration` amendment.

### Noise-only counterfactual (locked v0.5.0)

| Parameter | Value |
|-----------|-------|
| Function | `cit.data.multi_feature.noise_only_multi_feature_stream` |
| Generation | All features i.i.d. `Bernoulli(0.5)`, including indices 0-3 |
| Label dict | omitted (or all features labeled `noise`) |
| Use | v0.5.5 capstone falsifiability test for cross-K convergence claim. Operationalized 2026-06-23: each off-diagonal pair structured Spearman `>= 0.5` AND noise-only Spearman `< 0.3` (`T_noise`); asserted on A_1 + A_3 for all 15 pairs, A_2 sampled on cheap-proxy pairs (see 2026-06-23 amendment) |

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
| v0.5.4 evidence (2026-06-22) | `(K_4, K_2)` under A_2 measured **0.830** -- the structural twin (latent/coupled K_4 vs factorized K_2 under Shapley) CLEARS, while `(K_5, K_2)` sits at 0.491. Evidence that Seam 1 is `(K_5, K_2)`-specific (particular to K_5's LZ76 phrase dictionary), NOT a general "Shapley + coupled-versus-factorized" law. The generalization branch of the Resolution path is disfavored; seam remains marked pending v0.5.5 capstone. |
| v0.5.5 resolution (2026-06-23) | **RESOLVED -- `(K_5, K_2)`-specific.** Of all "X vs K_2 under A_2 (Shapley)" pairs, only `(K_5, K_2)` = 0.491 misses; `(K_3, K_2)`, `(K_4, K_2)` = 0.830, `(form B, K_2)`, and `(K_1, K_2)` all clear `>= 0.5`. The divergence does NOT generalize, so the framework's operating envelope is NOT restricted (no threshold or asserted-pair amendment taken). Seam stays mechanically `xfail(strict=True)` as a documented near-miss; a strict XPASS still forces re-evaluation. |

---

## v0.6 — operational theorems (COMPLETE: capacity v0.6.0 + selective coder v0.6.1 + Selective Compression empirics v0.6.2)

Operationalizes the formal capacity/compression theorems from `cit formal.docx` (JAMFFO-2) on top of the v0.5-validated rho signal. v0.6.0 locks the coherence-capacity estimator; the weighted typical-set coder (v0.6.1) and Selective Compression empirics (v0.6.2) are pending. Full protocol rationale, due-diligence numbers, and the Sec 6 erratum are in the 2026-06-23 amendment-history entry below.

### Coherence capacity estimator (locked v0.6.0)

| Element | Locked value |
|---------|--------------|
| Definition | `C_C = max_{p(x)} I_w(X;Y)` over the input simplex, fixed DMC `p(y|x)`, fixed `w(x) in [0,1]` |
| Implementation | `cit.capacity.coherence_capacity`; reuses `cit.information.I_w` unchanged (inherits the boundary spine) |
| Solver | projected-gradient ascent on the simplex (Euclidean projection), deterministic multi-start (centroid + n vertices + resolution-`m=20` simplex lattice), best local optimum |
| Gradient | analytic `dI_w/dp(x)`, unit-test-verified against central finite differences |
| Solver params | `tol = 1e-10` (objective improvement), `max_iter = 2000` per start; no RNG (bit-exact deterministic) |
| Scope | deterministic-lattice multi-start locked for small-alphabet fixtures only; larger alphabets require a future seeded-sampling amendment |
| Concavity | OPEN -- the `w(x)` factor breaks the standard `I(X;Y)` concavity argument; multi-start agreement is the empirical uniqueness stand-in, asserted only on the pre-registered fixtures |
| `delta` (must-preserve threshold) | not required by the capacity value (`C_C` is delta-independent); deferred to the v0.6.1 coder layer |
| Gating | fast (small DMCs, sub-second); no slow/very_slow tier |

### Binary Coherence Channel fixture (CORRECTED -- Sec 6 erratum)

`cit formal.docx` Sec 6 gives `C_C(eps) = 0.5(1+eps)` for the identity channel with `w=(1, eps)` and uniform input. Due-diligence (2026-06-23) shows uniform is NOT the capacity-achieving input for `eps < 1`: for the identity channel `I_w = H_w(X) = -q log2 q - eps(1-q) log2(1-q)` (`q = p(0)`), and `d/dq` at `q=0.5` equals `(1-eps)(1 - 1/ln2) < 0`, so the maximizer sits at `q* < 0.5`. Thus `0.5(1+eps)` is `I_w` evaluated at uniform -- a valid lower bound on `C_C`, equal to `C_C` only at `eps=1`. Locked true capacity:

| eps | C_C = max_p I_w | argmax q*=p(0) | 0.5(1+eps) = I_w@uniform |
|-----|-----------------|----------------|--------------------------|
| 0.00 | 0.530738 (= `1/(e*ln2)`, exact) | 0.367879 (= `1/e`, exact) | 0.500000 |
| 0.25 | 0.639687 (grid-verified) | 0.4134 | 0.625000 |
| 0.50 | 0.755588 (grid-verified) | 0.4499 | 0.750000 |
| 0.75 | 0.876210 (grid-verified) | 0.4782 | 0.875000 |
| 1.00 | 1.000000 (exact, Shannon boundary) | 0.500000 | 1.000000 |

No elementary closed form exists for general `eps` (the argmax solves a transcendental equation); only the endpoints `eps in {0, 1}` have exact closed forms. This erratum affects ONLY the Sec 6 worked example, NOT Capacity Theorem 4.1 itself (`C_C = max_p I_w` is correct as stated). Flagged for author erratum; parked with the App A.2 soundness flag.

### Asserted invariants (locked v0.6.0)

| Invariant | Threshold |
|-----------|-----------|
| Boundary (spine): `w=1 => C_C == Shannon capacity` on BSC(`p in {0.1, 0.25}`), Z-channel(`f=0.5`) | atol `1e-6` |
| Corrected fixture closed-form anchors `C_C(0)=1/(e*ln2)`, `C_C(1)=1` | atol `1e-8` |
| Corrected fixture grid-verified `C_C(eps)`, `eps in {0.25, 0.5, 0.75}` | atol `1e-5` |
| `argmax q* < 0.5` for `eps < 1` | strict |
| Lower-bound relation `C_C(eps) >= 0.5(1+eps)` (strict for `eps<1`, equal at `eps=1`) | strict |
| P2 bound `0 <= C_C <= C_Shannon` (capacity at `w=1`) on every test channel | strict |
| Determinism: repeated calls bit-identical | strict |
| Monotonicity: `C_C` non-decreasing under a uniform upward scaling of all weights toward 1 | strict |

### Known gaps (carried into v0.6.1)

- No closed form for general `eps` (transcendental argmax); only endpoints anchored.
- `I_w` concavity in `p(x)` unproven; multi-start agreement is the empirical stand-in.
- Deterministic-lattice multi-start is small-alphabet-only.
- App A.2 soundness flag (raw vs weighted log-prob in the typical-set cardinality bound) -- RESOLVED-NEGATIVE at v0.6.1 (Thm 5.1 holds only at `w=1`; see the selective coder subsection below + the 2026-06-23 v0.6.1 amendment).

### Selective compression coder (locked v0.6.1)

Repairs Selective Compression Theorem 5.1, which is unsound for non-constant w (RESOLVED-NEGATIVE; full record, counterexamples, and paper-text confirmation in the 2026-06-23 v0.6.1 amendment below). `H_w` is recast as a MEASURE ("bits that matter"), not a compression rate; the operational floor is the merged-source entropy `H(Z)`.

| Element | Locked value |
|---------|--------------|
| Corrected floor | `H(Z)`, `Z = (S_delta union {*})`, `S_delta = {x: w(x) > delta}`; `H(Z) = sum_{x in S_delta} p(x) log2(1/p(x)) + (1-q) log2(1/(1-q))`, `q = p(S_delta)` |
| Converse | any uniquely-decodable code reproducing every `x in S_delta` exactly has `L >= H(Z)` (Shannon converse on the i.i.d. source Z) |
| Achievability | entropy coder on Z: `L <= H(Z) + eps` |
| Boundary (spine) | `S_delta = X` (e.g. `w=1`, or `delta < min w`) `=> H(Z) = H(X)`; collapses to Shannon |
| Coder | `cit/coders/selective.py`: merge -> entropy-code. Primary = static arithmetic/range coder on Z (rate `-> H(Z)+eps`, bit-exact); practical variant = zstd on the merged byte stream (reuses K1 encoder) |
| `delta` | explicit must-preserve threshold; no hidden default |
| Decoder contract | reproduce every `S_delta` symbol exactly; fixed placeholder for `*` positions (don't-cares not reconstructed) |
| `H_w` | unchanged in `cit/information.py`; a MEASURE, not a rate |

Asserted invariants: lossless on `S_delta` (strict); arithmetic rate `<= H(Z) + 0.02` bits/symbol at `N=200_000`; `H(Z) <= H(X)` (strict `<` when `>= 2` don't-cares merged); coherence saving (merged rate `<` weight-blind when `>= 2` don't-cares); boundary `S_delta=X => rate -> H(X)`; determinism (bit-identical). Fast tier; `tests/test_selective_coder.py`.

### Selective Compression empirics (locked v0.6.2)

The engineering payoff of the v0.6.1 coder as a falsifiable WIN-MARGIN: on coherence-structured sources the selective coder compresses below the weight-blind lossless rate at zero coherence-retention cost, and the saving vanishes at the boundary. Built on `cit/coders/selective.py`; no coder changes. Full record in the 2026-06-23 v0.6.2 amendment below.

| Element | Locked value |
|---------|--------------|
| Win metric | `Delta_frac = (rate_blind - rate_selective) / rate_blind`, arithmetic coder (both lossless on `S_delta`); weight-blind = `delta` below all weights (no merge) |
| Win margin | `WIN_MARGIN = 0.20` (structured floor measured 0.307; calibrated below it) |
| Falsifiable claim | per structured substrate `Delta_frac >= 0.20` AND lossless on `S_delta`; at boundary `S_delta=X`, `Delta = 0` exactly |
| Substrates (`N=100_000`) | iid (`default_rng(42)`); Gilbert-Elliott memory (`default_rng(1)`); TCUN toggle+noise (`default_rng(2)`); v0.5 multi-feature excluded (not a symbol stream) |
| zstd saving | reported per substrate (observational; larger on memory sources) |

Asserted invariants: arithmetic `Delta_frac >= 0.20` on iid/G-E/TCUN; lossless on `S_delta` each (strict); boundary `Delta = 0` at `S_delta=X` each (exact). Fast tier; `tests/test_selective_compression_empirics.py`. Completes the v0.6 operational-theorem program.

---

## v0.7 — cross-domain validation (Metacoherence; v0.7.0 locked; D2/D3/M5 capstone pending)

The cross-domain validation architecture from Metacoherence. Four conditions: R1 (persistence prediction), R2 (cross-philosophy convergence), R3 (intervention asymmetry) -- within-domain signatures -- plus the M5 admissibility gate (domain-translation invariance, evaluated FIRST; it conditions the matrix). Three domains on a transparency gradient: D1 (synthetic HSMM, exact partition), D2 (Pfam protein families, CC0 via EBI/InterPro), D3 (FOMC statements, public domain). The eight-cell outcome interpretation matrix (Metacoherence Sec 8.3-8.4) binds each (R1,R2,R3) configuration to a framework consequence under M5-pass and M5-fail -- reproduced verbatim and bound in advance at the capstone. Locked statistical thresholds (Sec 8.7): R2 median Spearman `> 0.6` (lower 95% CI `> 0.4`); R1 Cohen's d `> 0.5` (CI `> 0.3`, `p < 0.01`); R3 structural/interpretive ratio `> 3.0` (CI `> 2.0`); M5 factor-of-2 rank-normalized ratio across all domain pairs for `>= 3 of 5` estimators; Bonferroni across 51 cells; bootstrap `B = 1000`.

Sequencing (sliced): v0.7.0 = D1 substrate + M5 partition + R2; v0.7.1 = R1 (persistence); v0.7.2 = R3 (interventions); then D2, D3, and the M5 cross-domain + eight-cell capstone.

### D1 substrate + M5 partition + R2 (locked v0.7.0)

The full-transparency domain; its M5 partition is exact by construction. Full record in the 2026-06-23 v0.7.0 amendment below.

| Element | Locked value |
|---------|--------------|
| Generator | 3-state hidden semi-Markov; negbinom sojourns (mean dwell 200, dispersion `r=6`, CV ~ 0.41); transitions equiprobable to the two non-current states; `T=50_000` (~250 sojourns); `N_REPLICATES=20` seeded streams |
| Features (8, alphabet 8) | f0 A:regime (`F0_scale=1.7`); f1 B:long-range (`f1 = g(f0,f2,f4 @ t-L)` w.p. `B_keep=0.35` else uniform, `L=12`); f2,f3 C:coalition (additive mask -- individually uniform, jointly recover regime); f4 D:drift (`std=0.10`, `peak=1.0`); f5/f6/f7 distractors (uniform / Zipf / low-freq) |
| Calibration (Sec 5.4) | MI-balanced: `I_A=0.76, I_B=0.46, I_C=0.34, I_D=0.58`; max single-property share `0.356 < 0.40`; distractors structurally flat (regime/local MI ~ 0). Exact `K3 x A1` ceiling verified in-build |
| Marginal-relative coherence | LOCKED -- every estimator's coherence measured relative to each feature's marginal (NOT a uniform baseline); else skewed-marginal distractors are mistaken for coherent (the failure D1 exists to catch) |
| M5 partition (by construction) | coherence-bearing = {f0,f1,f2,f3,f4}; noise = {f5,f6,f7} |
| R2 | 5x3 grid {K1..K5} x {A1,A2,A3} categorical, induced `w` over 8 features; cross-philosophy median Spearman `> 0.6` (CI `> 0.4`); bootstrap `B=1000`, block = mean sojourn (200) |
| Deliverable | property-recovery cross-tab (15 cells x 4 properties); D1 is CHARACTERIZED, not pass/failed |

Asserted invariants: R2 median Spearman `> 0.6` (CI `> 0.4`); class separation (coherence-bearing rank above distractors in every cell); distractor flatness (marginal-relative); cross-tab matches the pre-registered qualitative pattern; generator determinism (bit-exact per seed). Gating: cheap cells (K1/K2 x A1/A3) fast; K3 + K5/K3 Shapley slow/very_slow. New `cit/data/hsmm_d1.py` + categorical proxy generalizations + `tests/test_metacoherence_d1.py`.

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

### 2026-06-22 -- K_4 (MDL-HMM) protocol lock

**Change.** K_4 multi-feature proxy locked for v0.5.4 implementation. A hidden Markov model with factorized Bernoulli emissions (each of the n_features binary features conditionally independent given the hidden state; one free Bernoulli parameter `p[h, j]` per (state h, feature j)) is fit by Baum-Welch EM at each hidden-state cardinality `H in {1, 2, 3, 4}`. Two-part MDL selects `H* = argmin_H [L_data(H) + L_model(H)]`; `C_K4 = 1 - (L_data(H*) + L_model(H*)) / L_iid`, clipped to `[0, 1]`. The emission family is FIXED (factorized Bernoulli) for all H; the MDL search ranges only over hidden-state cardinality, never over emission structure (see Emission-structure scope below).

This supersedes the K_4 protocol sketch in `design/multi_feature_substrate.md` (K_4 protocol section + estimator table) in three respects, each justified below: (1) parameter count uses the rigorous free-parameter accounting `H(H-1) + H*n_features + (H-1)` rather than the memo's `H^2 + n*H`; (2) the cardinality grid is `{1, 2, 3, 4}` rather than `[1, 8]`; (3) EM is a single deterministic seeded initialization (`HMM_SEED`), `max_iter = 100`, `tol = 1e-4`, rather than 5 random restarts x 50 fixed iterations. The design memo is updated to the amended spec in the same commit.

**Rationale.** Pre-implementation analytical reasoning plus an empirical due-diligence pass. Two independent throwaway Baum-Welch prototypes were measured on the locked substrate (STREAM_SEED=42, ABLATION_SEED=123); they agree to six significant figures on every decisive quantity.

- *No clip-to-zero.* The K_2 and K_5 amendments exist because their first formulations clipped `C` to 0 on this substrate. K_4 does not: `C_K4(structured) = 0.0755` selecting `H* = 2`, recovering the ground-truth 2-state generator (fitted emissions ~ 0.8/0.2 on coherent features, ~ 0.5 on noise, self-transition ~ 0.9). `C_K4(noise-only) = 0.000` selecting `H* = 1`. The structured-vs-noise differential and the exact zero on the counterfactual are the desired falsifiability signature. The analytic upper bound under perfect state knowledge is `C = 0.110` (per-coherent-feature conditional entropy `H(0.8) = 0.722` bits vs `1.0` iid); the realized `0.0755` is lower because the sticky-0.9 chain caps state inference -- the value is structurally explained, not a free parameter.

- *Canonical signs and class separation under ablation.* Centered LOO (A_1) gives `rho > 0` for all coherent features {0,1,2,3} (~ +0.0143) and `rho < 0` for all noise features {4..9} (~ -0.0098), a separation margin (~0.024) that dwarfs inter-run jitter (<= 2e-6). K_4's likelihood-based ablation gives ~50% larger |rho| on coherent features than K_2 because removing a column the shared latent state was jointly explaining costs more likelihood than K_2's per-feature lag-1 view.

- *Cross-proxy convergence under A_1.* Spearman(rho_K4, rho_K2) = 0.818 under A_1, well clear of the multi-feature 0.5 threshold.

- *Parameter-count convention.* The locked `num_params(H) = H(H-1) [transition rows sum to 1] + H*n_features [emissions] + (H-1) [initial sums to 1]` counts free parameters under the same convention K_2 uses (K_2 counts `2*n_features` free Bernoulli params, exploiting `p(0|.) = 1 - p(1|.)`). The memo's `H^2 + n*H` over-counts transitions as `H^2` and omits the initial distribution; the two differ by exactly one parameter (~7 bits at T=20000) and do not change H-selection, but the free-parameter count is the principled, K_2-consistent choice and is locked as such.

- *Cardinality grid.* `{1, 2, 3, 4}` contains the true cardinality (2) with 2x headroom. Empirically the MDL penalty rejects `H >= 3` decisively (`H=3` total description length exceeds `H=2` by ~100 bits; `H=4` by more), so `H in {5,...,8}` would never be selected on this substrate and only ~double the compute. `{1, 2, 3, 4}` is locked as the narrowest grid containing the truth with headroom; the penalty, not the grid bound, excludes higher H, so this is not tuning to a result.

- *Determinism.* A single deterministic seeded initialization (sticky-0.9 self-transition, uniform initial, emissions = per-feature global Bernoulli MLE perturbed by a fixed `HMM_SEED` jitter; H=1 closed-form) is locked instead of random restarts, mirroring the K_3 `NEURAL_SEED` discipline. On this substrate the two states are well separated (0.2 vs 0.8), EM converges to the global optimum in <= 17 iterations from the perturbed-MLE start across all ablations tested, and a single init is bit-exactly reproducible. Residual risk recorded honestly: if the A_2 Shapley sweep (1,280 proxy calls over random coalitions) surfaces a local-optimum instability, that is a structural finding to record, not to silently patch.

**Emission-structure scope (deliberate, narrow).** "MDL search over hidden-state cardinality and emission structure" is locked under the narrow reading: emissions are a fixed factorized-Bernoulli family and the MDL two-part search ranges only over `H`. The rich reading -- letting MDL select, per feature, whether each emission is state-dependent -- is rejected because it performs feature attribution inside the proxy, which is precisely the role of the ablation operator A_m; convergence between a proxy and an ablation that share a feature-selection mechanism is not independent evidence. Recorded as a deliberate scope choice so a future emission-structure-search variant is a versioned amendment, not silent drift.

**K_4 family identity (locked).** K_4 is the only proxy in the family with a latent variable AND an explicit MDL model-complexity penalty over a searched cardinality. Structurally distinct from:

- form B: joint conditioning on the previous full feature vector, no latent state, no penalty.
- K_1: zstd universal byte compression, implicit/amortized model, no explicit parameter count, no latent state.
- K_2: per-feature factorized bigram MDL, observed lag-1 conditioning, no latent state, no cross-feature coupling.
- K_3: neural online prequential cross-entropy, amortized via SGD, no explicit MDL prior and no discrete model selection.
- K_5: LZ76 bit-level phrase parsing, combinatorial dictionary, no probability model, no penalty.

K_4's unique axis is selected latent-state cardinality under a description-length penalty. Its emissions are factorized (matching K_2), so a K_4-vs-K_2 comparison isolates the latent-state / model-selection difference rather than entangling it with a factorization shift; the cross-feature coupling K_4 adds via the shared hidden state is exactly what K_2 lacks.

**Cross-proxy convergence commitment (v0.5.4).** v0.5.4 asserts all 15 new pairs -- `(K_4, P)` for `P in {form B multi, K_1 multi, K_2, K_5, K_3}` under each of `A_1, A_2, A_3` -- at the multi-feature threshold Spearman `rho >= 0.5`. Pre-registered structural prediction: **`(K_4, K_2)` under A_2 (Shapley) is the most likely pair to fall short.** It is the structural twin of Seam 1 (`(K_5, K_2)` under A_2 = 0.491): a cross-feature-coupling proxy (here K_4's shared latent state) versus a purely factorized proxy (K_2), under Shapley's coalition-credit redistribution, where A_1 (single-feature LOO) and A_3 (correlation-cluster) do not surface the asymmetry. If `(K_4, K_2)` under A_2 measures below 0.5 with the locked seeds, it is recorded honestly as **Seam 2** (mechanically `@pytest.mark.xfail(strict=True)`, resolution deferred to the v0.5.5 capstone), exactly as Seam 1 was recorded post-measurement at v0.5.2 -- not pre-marked and not tuned over. Either outcome is a direct probe of Seam 1's generalization hypothesis (whether "Shapley applied to a coupled-versus-factorized proxy pair" is a one-off or a structural law): a `(K_4, K_2)` miss is evidence the pattern generalizes; a clear pass is evidence Seam 1 is `(K_5, K_2)`-specific.

**Result (measured 2026-06-22).** `(K_4, K_2)` under A_2 = **0.830** -- clears; **no Seam 2**. `(K_4, form B)` = 0.733 and `(K_4, K_1)` = 0.915 under A_2; K_4's own A_2 invariants hold (canonical signs, class separation, `|w - 0.5|_max = 0.013`). All A_1 and A_3 cross-proxy pairs clear (slow suite green). The two remaining A_2 pairs `(K_4, K_5)` and `(K_4, K_3)` are gated to the full very_slow run and are not seam-risk. The clear pass is evidence Seam 1 is `(K_5, K_2)`-specific rather than a general "Shapley + coupled-versus-factorized" restriction; the generalization branch of Seam 1's resolution path is now disfavored, pending final v0.5.5 capstone confirmation. K_4 Shapley fixture measured ~2.1 h (1,280 proxy calls), under the 6 h hosted ceiling.

**Lock scope.** v0.5.4+ K_4 implementations and cross-proxy R_2 tests involving K_4. Marker assignment (validated by the due-diligence prototypes at ~9 s/proxy call, ~100 s full LOO): A_1 LOO, A_3 correlation-cluster, and proxy-level invariants are `slow`; A_2 Shapley is `very_slow` at ~2.8-3.2 h/fixture (1,280 proxy calls = 10 features x 64 coalitions x 2 marginal evaluations). Unlike K_3 (~4.3 h, local-gated), K_4's Shapley fits under the 6 h hosted-runner ceiling, so hosted `very_slow.yml` can run the K_4 family. Pure-numpy vectorized EM is sufficient for the ceiling; numba acceleration is an optional implementation detail, not a locked element.

**Implementation locked v0.5.4.**

| Element | Locked value |
|---------|--------------|
| Input | 10-feature substrate stream (4 coherent + 6 noise), uint8 in {0,1}; no byte/bit packing |
| Model class | Hidden Markov model, factorized Bernoulli emissions |
| Emission | `p(v_t | h_t) = prod_j p(v_t^j | h_t)`; one free `p[h,j]` per (state, feature); fixed family, never searched |
| Cardinality grid | `H in {1, 2, 3, 4}` (H=1 = independent per-feature Bernoulli, closed-form) |
| Fit | Baum-Welch EM; scaled forward-backward; log-space emission likelihood with per-row max offset |
| Init | sticky-0.9 self-transition; uniform initial; emissions = per-feature global Bernoulli MLE + fixed seeded jitter |
| max_iter | 100 (observed convergence <= 17 iters) |
| tol | 1e-4 on per-step mean log-likelihood improvement |
| Numerical guards | emission probs clipped to [1e-6, 1-1e-6]; transition rows clipped [1e-12, .] and renormalized each M-step |
| num_params(H) | `H(H-1) [transition] + H*n_features [emission] + (H-1) [initial]` |
| L_model(H) | `0.5 * num_params(H) * log2(T)` bits |
| L_data(H) | `-log2` marginal likelihood of the fitted HMM (independent forward pass on fitted params), bits |
| L_iid | `T * n_features` bits (uniform Bernoulli baseline) |
| Selection | `H* = argmin_H [L_data(H) + L_model(H)]` |
| Coherence | `C_K4 = 1 - (L_data(H*) + L_model(H*)) / L_iid`, clipped to `[0, 1]` |
| Determinism | fixed `HMM_SEED`, CPU/numpy, vectorized; bit-exact reproducible |
| HMM_SEED | `0` (new locked constant, distinct from `STREAM_SEED=42`, `ABLATION_SEED=123`, `NEURAL_SEED=7`) |
| Expected (structured) | `C_K4 ~ 0.075`, `H* = 2` |
| Expected (noise-only) | `C_K4 = 0.0`, `H* = 1` |

### 2026-06-23 -- v0.5.5 capstone: noise-only falsifiability + Seam 1 resolution

**Change.** v0.5.5 capstone locked. Three elements: (1) the full 15-pair off-diagonal cross-proxy convergence matrix on the structured substrate is consolidated as the standing within-domain robustness claim (built incrementally v0.5.0-v0.5.4; no new structured pairs added); (2) the noise-only counterfactual falsifiability test is operationalized and asserted; (3) Seam 1 is resolved on the evidence.

**Noise-only counterfactual (operationalized).** The v0.5.0 "drops significantly" placeholder is locked to a concrete rule. For each off-diagonal proxy pair, the falsifiability claim is the conjunction:

- structured-substrate Spearman of the per-feature rho vectors `>= 0.5` (the existing multi-feature convergence threshold), AND
- noise-only-substrate Spearman `< 0.3` (`T_noise`, locked).

Asserted on A_1 (LOO) and A_3 (CorrCluster) for all 15 pairs. A_2 (Shapley) noise-only is asserted on the 3 cheap-proxy pairs (form B, K_1, K_2) as a sampled invariant; the full A_2 noise-only matrix (K_3/K_4/K_5 Shapley on noise) is NOT asserted -- it would mirror the ~8 h structured very_slow tier for marginal additional evidence, and the sample already shows A_2 collapses identically on noise.

**Threshold calibration (pre-implementation, 2026-06-23).** Measured on the locked substrate (STREAM_SEED=42, ABLATION_SEED=123): per-feature rho vectors, cross-proxy Spearman, structured vs noise-only.

| Ablation | structured (min / mean / max) | noise-only (min / mean / max) |
|----------|-------------------------------|-------------------------------|
| A_1 (LOO) | 0.571 / 0.753 / 0.948 | -0.390 / -0.049 / 0.000 |
| A_3 (CorrCluster) | 0.583 / 0.754 / 0.985 | -0.390 / -0.049 / 0.000 |
| A_2 (Shapley, cheap pairs) | 0.733 / 0.794 / 0.855 | -0.297 / -0.099 / 0.000 |

No proxy pair has positive convergence on noise under any ablation (signed max = 0.000; the non-zero values are negative, driven by K_5's non-degenerate noise rho and one A_2 pair). Structured convergence is `>= 0.571` everywhere. The locked `T_noise = 0.3` sits above the observed noise ceiling (0.000) with margin and below the structured floor (0.571) with margin; it asserts that convergence is destroyed on structure-free data without over-fitting to the exact observed noise level. Several noise pairs are exactly 0.000 because proxies that clip C to a constant on noise (e.g. K_2, K_4) yield tied rho vectors -> Spearman 0 (the d=0 guard); this is the expected degenerate signature and is well below `T_noise`.

**Seam 1 resolution.** Resolved per the v0.5.2 resolution path. Of all "X vs K_2 under A_2 (Shapley)" pairs, only `(K_5, K_2)` falls short (0.491); `(K_3, K_2)`, `(K_4, K_2)` (0.830), `(form B, K_2)`, and `(K_1, K_2)` all clear `>= 0.5`. The K_4 evidence (2026-06-22) and the consolidated matrix show the divergence is **`(K_5, K_2)`-specific** -- particular to K_5's LZ76 phrase-dictionary interaction with K_2's factorized bigram under random-coalition ablation -- and does NOT generalize to "Shapley applied to any coupled-versus-factorized proxy pair." The generalization branch of the resolution path (which would have restricted the framework's operating envelope via a threshold or asserted-pair amendment) is therefore NOT taken. Seam 1 remains a documented near-miss, mechanically `xfail(strict=True)`; no envelope restriction. A strict XPASS still forces re-evaluation.

**A_3 cluster-recovery ARI.** Remains observational (not promoted). The v0.5.0 note flagged promotion as optional at the capstone; deferred to keep the capstone focused on the falsifiability spine. Promotable in a later amendment with a calibrated threshold.

**Lock scope.** v0.5.5+ noise-only counterfactual tests and the consolidated structured matrix. `T_noise = 0.3` locked. Gating: noise-only A_1/A_3 for K_3/K_4/K_5 are `slow` (mirror the structured slow cost); the A_2 cheap-proxy noise sample is `slow` (form B/K_1/K_2 Shapley ~ seconds). No new very_slow tier.

**Implementation (v0.5.5).** Noise-only fixtures (LOO + CorrCluster per proxy on `noise_only_multi_feature_stream(20000, seed 42)`); per-pair noise-Spearman `< 0.3` assertions under A_1/A_3 for all 15 pairs; the A_2 cheap-proxy noise sample; a consolidated structured-matrix capstone assertion. Seam 1 xfail retained.

### 2026-06-23 -- v0.6.0 coherence-capacity estimator protocol lock

**Change.** First operational-theorem estimator locked. `C_C = max_{p(x)} I_w(X;Y)` for a fixed discrete memoryless channel `p(y|x)` and fixed weights `w(x) in [0,1]`, maximized over the input simplex. Implements Coherence Capacity Theorem 4.1 (`cit formal.docx`, JAMFFO-2). New module `cit/capacity.py`; reuses `cit/information.py:I_w` unchanged, so the estimator inherits the boundary-condition spine. Capacity tests are `fast` (small DMCs, sub-second); no slow/very_slow tier. This opens the v0.6 program (capacity v0.6.0; coder v0.6.1; Selective Compression v0.6.2), sequenced capacity-first as the most self-contained, lowest-risk deliverable.

**Solver (locked).** Projected-gradient ascent on the probability simplex (Euclidean projection), polished from a deterministic multi-start set -- centroid + all `n` vertices + a resolution-`m=20` simplex lattice -- taking the best local optimum. Analytic gradient of `I_w` with respect to `p(x)`, verified against central finite differences in a unit test. `tol = 1e-10` on objective improvement, `max_iter = 2000` per start. No RNG: fully deterministic and bit-exact (no new seed constant is introduced). The deterministic-lattice multi-start is locked ONLY for the small-alphabet fixtures pre-registered here; larger-alphabet capacity requires a future seeded-sampling amendment (out of v0.6.0 scope, recorded so it is a versioned change, not silent drift).

**Concavity is OPEN.** Concavity of `I_w` in `p(x)` is not proven in any source document -- the `w(x)` factor breaks the standard `I(X;Y)`-concavity argument. Recorded as open/asserted; the empirical stand-in for uniqueness is multi-start agreement (all starts finishing within atol of the best agree on the argmax), asserted only on the pre-registered fixtures. No guarantee is claimed that the papers do not provide.

**Due-diligence (measured 2026-06-23, throwaway prototype reusing repo `I_w`).** Projected-gradient multi-start reproduces an independent brute-force simplex grid to `~1e-12` (binary channels) and `~4e-8` (a 3-input channel). Boundary `w=1` recovers Shannon capacity exactly: BSC(`p`) -> `1 - H_b(p)` at the uniform maximizer; Z-channel(`f=0.5`) -> `0.321928` at `q* ~ 0.6`. These settle the decisive pre-lock risk (does a numpy simplex maximizer reproduce the paper's closed form and the boundary) before any code is committed.

**Binary Coherence Channel fixture -- CORRECTED (Sec 6 erratum).** `cit formal.docx` Sec 6 states the identity channel with `w=(1, eps)` and uniform input gives `C_C(eps) = 0.5(1+eps)`. Due-diligence shows uniform input is NOT the capacity-achieving input for `eps < 1`: for the identity channel `I_w = H_w(X) = -q log2 q - eps(1-q) log2(1-q)` (`q = p(0)`), whose derivative at `q=0.5` is `(1-eps)(1 - 1/ln2) < 0`, so the maximizer sits at `q* < 0.5`. Therefore `0.5(1+eps)` is `I_w` evaluated at uniform -- a valid lower bound on `C_C`, equal to `C_C` only at `eps=1` -- not the capacity. The true capacity (max over the simplex), locked:

| eps | C_C = max_p I_w | argmax q*=p(0) | 0.5(1+eps) = I_w@uniform |
|-----|-----------------|----------------|--------------------------|
| 0.00 | 0.530738 (= `1/(e*ln2)`, exact) | 0.367879 (= `1/e`, exact) | 0.500000 |
| 0.25 | 0.639687 (grid-verified) | 0.4134 | 0.625000 |
| 0.50 | 0.755588 (grid-verified) | 0.4499 | 0.750000 |
| 0.75 | 0.876210 (grid-verified) | 0.4782 | 0.875000 |
| 1.00 | 1.000000 (exact, Shannon boundary) | 0.500000 | 1.000000 |

No elementary closed form exists for general `eps` (the argmax solves a transcendental equation); only the endpoints `eps in {0, 1}` have exact closed forms (`1/(e*ln2)` and `1`). This erratum affects ONLY the Sec 6 worked example, NOT Capacity Theorem 4.1 itself (`C_C = max_p I_w` is correct as stated). Flagged for author erratum; parked with the App A.2 soundness flag.

**Asserted invariants (locked v0.6.0).**

1. *Boundary (spine):* `w=1 => C_C == Shannon capacity` on BSC(`p in {0.1, 0.25}`) and Z-channel(`f=0.5`), atol `1e-6`.
2. *Corrected fixture:* identity channel, `w=(1, eps)`. Closed-form anchors `C_C(1)=1` and `C_C(0)=1/(e*ln2)` to atol `1e-8` (see post-implementation correction below); grid-verified `C_C(eps)` for `eps in {0.25, 0.5, 0.75}` to atol `1e-5`; `argmax q* < 0.5` strict for `eps < 1`.
3. *Lower-bound relation:* `C_C(eps) >= 0.5(1+eps)` (the value-at-uniform), strict for `eps < 1`, equality at `eps = 1`.
4. *P2 bound:* `0 <= C_C <= C_Shannon` (capacity at `w=1`) on every test channel.
5. *Determinism:* repeated calls return bit-identical `C_C`.
6. *Monotonicity:* `C_C` non-decreasing under a uniform upward scaling of all weights toward 1 (follows from `I_w` monotone in `w`).

**delta (must-preserve threshold).** The capacity value `C_C = max_p I_w` is independent of the reliability threshold `delta > 0` (which governs which symbols the decoder must recover). delta belongs to the achievability/coder layer; deferred to v0.6.1. Recorded so its absence here is a deliberate scope choice, not an omission.

**Known gaps carried forward.** (a) no closed form for general `eps`; (b) concavity open; (c) deterministic multi-start small-alphabet-only; (d) the Sec 6 erratum above; (e) the App A.2 soundness flag still parked for v0.6.1.

**Lock scope.** v0.6.0+ capacity estimator and tests. New module `cit/capacity.py`; new test file `tests/test_capacity.py` (fast tier). The `design/v06_v07_spec.md` Section 7.2 fixture line (`reproduce C_C(eps)=0.5(1+eps)`) is superseded by this corrected fixture; the design memo is updated to match in the same commit.

**Correction (2026-06-23, post-implementation).** Implementation showed the locked solver stop (`tol = 1e-10` on objective improvement) reaches ~`1e-9` *value* accuracy on the FLAT `eps=0` maximum (`f''(1/e) = -e/ln2 ~ -3.92`; measured error `1.12e-9`, scaling ~11x `tol` near the flat max), so the closed-form-anchor test atol is corrected from `1e-9` to `1e-8`. This is a test-tolerance correction ONLY: the analytic gradient and solver are verified correct -- tightening `tol` to `1e-12` / `1e-14` drives the error to `1.1e-11` / `1.1e-13`, converging to the exact `1/(e*ln2)`. No theory quantity, locked constant (`tol`, `max_iter`, `lattice_m` unchanged), or fixture value changes; `1e-8` is still an 8-significant-digit match to the closed form. The boundary-spine (atol `1e-6`) and grid-verified (atol `1e-5`) tolerances are unaffected. Recorded here rather than silently loosened.

### 2026-06-23 -- v0.6.1 Selective Compression repair (Thm 5.1 resolved-negative) + corrected H(Z) coder

**Thm 5.1 / App A.2 resolution (RESOLVED-NEGATIVE for non-constant w).** The paper's Selective Compression Theorem 5.1 (`cit formal.docx` Sec 5) -- "any uniquely-decodable lossless code whose decoder reproduces every symbol with `w(x) > delta` has `L >= H_w`, achievable to `L <= H_w + eps` via weighted typical-set coding" -- is UNSOUND for non-constant w; it holds only in the `w=1` Shannon boundary. Established 2026-06-23 by a 4-agent adversarial analysis (independent lenses: operational floor, cardinality bound, alternative criteria; an adversarial verifier failed to rescue the result), confirmed against the actual paper text:

- The operational criterion is verbatim the hard delta-threshold exact-reproduction (Sec 5.1).
- The cardinality bound `|T_{w,eps}^n| <= 2^{n(H_w+eps)}` (App A.2 Lemma A.3) is false for `w != 1`: w-typicality constrains the WEIGHTED self-information `~ n*H_w`, but the typical set's SIZE is governed by the RAW log-prob `-log p(x^n)`. Enumerated counterexamples: binary `p=(0.5,0.5)`, `w=(1,0)`, `n=3`, `eps=0.3` gives `|T|=6 > 2^2.4=5.28`; `p=(0.7,0.3)`, `w=(1,0)`, `n=4` gives `|T|=15 >> 5.43`. The index is too short to label typical blocks injectively -- the coder is not even uniquely decodable.
- Both directions fail: under the threshold criterion only `S_delta = {x: w(x) > delta}` must be reproduced, so the true floor is the merged-source entropy `H(Z)` (below), which can EXCEED `H_w`. The paper's own Sec 5.4 binary example (`w=(1, ~0)`, claims a weighted coder reaches `H_w -> p0(-log p0)`) is the counterexample: the true floor is the full Shannon `H_b(p0)` (knowing which positions are the structural symbol IS the whole binary sequence); at `p0=0.5` the paper claims `0.5` bits/symbol where `>= 1.0` is required.

The Capacity Theorem (Sec 4) is UNAFFECTED (its coherence-joint typicality is a sound union-bound use). `H_w` / `I_w` as measures (Sec 3) are unaffected.

**H_w recast (not dropped).** `H_w(X) = sum_x p(x) w(x) (-log2 p(x)) = E_p[w(X)*iota(X)]` (expected attention-weighted surprisal) is RETAINED as the coherence-weighted entropy MEASURE ("bits that matter") -- `cit/information.py:H_w` unchanged. It is explicitly NOT an achievable compression rate for non-constant w. The original theorem's error was identifying a significance MEASURE with a compression RATE; v0.6.1 separates them.

**Corrected Selective Compression Theorem (Option A, locked v0.6.1).** For an i.i.d. source `p(x)` over finite alphabet X, weights `w(x) in [0,1]`, threshold `delta > 0`:

- Must-preserve set `S_delta = {x: w(x) > delta}`; `q = p(S_delta)`.
- Merged source Z over alphabet `S_delta union {*}`: `Z = x` for `x in S_delta`, else `Z = *` (one token).
- Floor: `L* = H(Z) = sum_{x in S_delta} p(x) log2(1/p(x)) + (1-q) log2(1/(1-q))`.
- Converse: any uniquely-decodable code reproducing every `x in S_delta` exactly must convey Z losslessly, so `L >= H(Z)` (Shannon converse on the i.i.d. source Z).
- Achievability: an entropy coder on Z achieves `L <= H(Z) + eps` (arithmetic coding).
- Boundary (the spine): `S_delta = X` (e.g. `w=1`, or `delta < min_x w(x)`) `=> Z = X => H(Z) = H(X)`; collapses to Shannon lossless coding.
- Property: `H(Z) <= H(X)` always (merging symbols cannot increase entropy); strict `<` iff `>= 2` distinct symbols are merged.

**Coder (locked v0.6.1).** Module `cit/coders/selective.py`. Construction = "merge -> entropy-code":

- merge: each symbol -> itself if in `S_delta`, else the reserved token `*`.
- PRIMARY (theorem-faithful): a static integer arithmetic/range coder on the merged stream with the empirical Z-pmf (two-pass; model transmitted, `O(|S_delta|)` bits, negligible per-symbol); rate `-> H(Z) + eps`. Deterministic, bit-exact; exact round-trip on the merged stream.
- PRACTICAL variant: zstd (level locked) on the merged byte stream (reuses K1 encoder infra); reported alongside, looser overhead.
- `delta`: explicit parameter (the must-preserve threshold); no hidden default.
- Decoder contract: reproduce every `S_delta` symbol EXACTLY; emit a fixed placeholder (a designated don't-care symbol) for `*` positions (don't-cares are NOT reconstructed -- the point of selective compression).
- Determinism: bit-exact, no RNG in the coder; test source seeded `STREAM_SEED=42`.

**Asserted invariants (locked v0.6.1).**

1. *Lossless on S_delta:* `decode(encode(x))` reproduces every symbol with `w(x) > delta` exactly (strict).
2. *Achievability:* arithmetic-coder total rate (incl. model) `<= H(Z) + TOL_RATE` on a length-`N` i.i.d. stream. `N = 200_000`, `TOL_RATE = 0.02` bits/symbol (engineering calibration; confirmed at implementation).
3. *Floor ordering:* `H(Z) <= H(X)` (strict `<` when `>= 2` don't-care symbols merged).
4. *Coherence saving:* arithmetic `rate(merged) < rate(weight-blind, S_delta=X)` when `|X \ S_delta| >= 2`.
5. *Boundary spine:* `S_delta = X => H(Z) = H(X)` and coder rate `-> H(X)` (within `TOL_RATE`); covers `w=1` and `delta < min w`.
6. *Determinism:* bit-identical output across runs.
7. *H_w-as-measure:* `H_w` unchanged (`cit/information.py`); documented as a measure, not a rate.

**Gating.** Fast (small/medium i.i.d. streams; arithmetic coder + zstd both fast). No slow tier.

**Lock scope.** v0.6.1+ selective coder and tests. New module `cit/coders/selective.py`; new test file `tests/test_selective_coder.py` (fast). v0.6.2 (Selective Compression empirics: win-margin vs weight-blind on richer substrates) is separate, pending its own amendment. Design memo `design/v06_v07_spec.md` Sec 7.3-7.4 updated to the corrected theorem in the same commit.

**Known gaps / honest notes.** (a) `H(Z)` is partition-driven (depends on `S_delta` via `delta`, not the graded w values) -- a deliberate consequence of the threshold criterion; the graded weights live in the `H_w` measure, not the rate. (b) Corrected theorem is i.i.d.-source (Thm 5.1 scope); sources with memory are out of v0.6.1 scope. (c) `TOL_RATE`/`N` are engineering calibration, confirmed against the real coder at implementation.

### 2026-06-23 -- v0.6.2 Selective Compression empirics (win-margin)

**Change.** Operationalizes the engineering payoff of the corrected selective coder (v0.6.1, compress to `H(Z)`) as a falsifiable WIN-MARGIN: on coherence-structured sources the selective coder compresses strictly below the weight-blind lossless rate while reproducing every coherence-bearing symbol exactly, and the advantage VANISHES at the boundary (`S_delta = X`). Built on the v0.6.1 coder; no coder changes.

**Win metric.** The selective coder (`delta`) and a weight-blind baseline (`delta` below all weights `=> S_delta = X =>` no merge `=>` full lossless coding) are run with the SAME coder; the win is the fractional bitrate saving `Delta_frac = (rate_blind - rate_selective) / rate_blind` (arithmetic coder). Both are lossless on `S_delta`, so the saving is at ZERO coherence-retention cost. The zstd coder's saving is reported alongside (observational; larger on memory sources, which zstd exploits).

**Falsifiable claim (two-sided), locked.** For each pre-registered structured substrate: (i) `Delta_frac >= WIN_MARGIN = 0.20` (arithmetic), AND (ii) every symbol with `w(x) > delta` reproduced exactly; and at the boundary (`S_delta = X`, e.g. `w = 1`): (iii) `Delta = 0` (exactly). Falsified if any structured substrate's saving falls below 0.20, or the boundary saving is non-zero, or any coherence-bearing symbol is corrupted.

**Substrates (locked params + seeds, `N = 100_000`).**

| Substrate | Spec | weights / delta |
|-----------|------|-----------------|
| iid | `K=5`, `p=[0.5,0.18,0.14,0.1,0.08]`, `default_rng(42)` | `w=[1,0,0,0,0]`, `delta=0.5` |
| Gilbert-Elliott (memory) | `K=6`, 2-state Markov self-transition 0.95; good -> `choice([0,1], p=[0.7,0.3])`; bad -> uniform`{2,3,4,5}`; `default_rng(1)` | `w=[1,1,0,0,0,0]`, `delta=0.5` |
| TCUN (toggle + uniform noise) | `K=6`, toggle base `{0,1}` advanced each non-injection step; `injection_prob=0.35` -> uniform`{2,3,4,5}`; `default_rng(2)` | `w=[1,1,0,0,0,0]`, `delta=0.5` |

The v0.5 multi-feature substrate is per-feature-binary, not a symbol stream; it does not map to the per-symbol selective coder and is deliberately excluded.

**Margin calibration (pre-implementation, 2026-06-23).** Measured fractional saving (arithmetic) on the locked substrates:

| Substrate | arith `Delta_frac` | arith `Delta` (bits/sym) | zstd `Delta_frac` | lossless on `S_delta` |
|-----------|------|------|------|------|
| iid | 0.492 | +0.972 | 0.497 | yes |
| Gilbert-Elliott | 0.411 | +1.005 | 0.536 | yes |
| TCUN | 0.307 | +0.702 | 0.441 | yes |
| boundary `w=1` (iid) | 0.000 | +0.000 | 0.000 | yes |
| boundary `w=1` (G-E) | 0.000 | +0.000 | 0.000 | yes |

Structured floor = 0.307 (TCUN). `WIN_MARGIN = 0.20` sits ~35% below the floor with margin and above the boundary (0.000); it asserts a structurally meaningful ">= 20% bitrate saving at zero retention cost" without over-fitting to the observed values. Same calibrate-then-set-below-floor discipline as `T_NOISE` (v0.5.5).

**Asserted invariants (locked v0.6.2).** (1) arithmetic `Delta_frac >= 0.20` on each structured substrate (iid, G-E, TCUN); (2) lossless retention: every `S_delta` symbol reproduced exactly on each substrate (strict); (3) boundary `Delta = 0` at `S_delta = X` on each substrate (exact); (4) zstd `Delta_frac` per substrate logged, not asserted.

**Gating.** Fast (`N = 100_000`, arithmetic + zstd both quick). No slow tier.

**Lock scope.** v0.6.2+ Selective Compression empirics. New test file `tests/test_selective_compression_empirics.py` (fast); substrate generators in `cit/data/` or the test module. No changes to `cit/coders/selective.py`. Design memo `design/v06_v07_spec.md` Sec 7.4 updated. This COMPLETES the v0.6 operational-theorem program (capacity v0.6.0, coder v0.6.1, empirics v0.6.2); v0.7 cross-domain is next.

**Honest notes.** (a) On memory sources the arithmetic coder uses a static i.i.d. model, so it reaches the i.i.d. merged entropy, not the merged entropy RATE; the win-margin (a DIFFERENCE of blind vs selective under the same coder) is unaffected, and the zstd row confirms the saving grows when memory is exploited. (b) `WIN_MARGIN` is calibrated to the locked substrates; new substrates extend (not retune) the claim via a future amendment. (c) Both coders are fully lossless on `S_delta`, so this is an equal-retention/lower-rate demonstration; the dual equal-rate/higher-retention (lossy-baseline) framing is out of v0.6.2 scope.

### 2026-06-23 -- v0.7.0 D1 substrate + M5 partition + R2 (Metacoherence cross-domain, domain 1)

**Scope.** Opens the v0.7 cross-domain program (Metacoherence: R1 + R2 + R3 within-domain signatures + the M5 admissibility gate + the eight-cell outcome matrix, across three domains). v0.7 is sequenced: v0.7.0 = D1 (synthetic HSMM) substrate + the D1 M5 feature-partition + R2 (cross-philosophy convergence); R1 (persistence) = v0.7.1, R3 (intervention asymmetry) = v0.7.2; then D2 (Pfam, CC0), D3 (FOMC, public domain), and the M5 cross-domain + eight-cell capstone. D1 is the full-transparency tier; its partition is exact by construction.

**D1 generator (locked).** A 3-state hidden semi-Markov regime layer with structured discrete emissions, per Metacoherence Sec 5. Locked structure: 3 states; negative-binomial sojourns (mean dwell 200, dispersion `r=6` -> CV ~ 0.41); transitions equiprobable to the two non-current states (irreducible/aperiodic); stream length `T = 50_000` (~250 sojourns); `N_REPLICATES = 20` independent seeded streams. Eight features, alphabet 8 each:

| feature | property | construction (locked) |
|---------|----------|-----------------------|
| f0 | A (regime indicator) | regime-conditional categorical, 3 distributions, `F0_scale = 1.7` |
| f1 | B (long-range coupling) | `f1[t] = g(f0,f2,f4 @ t-L)` with prob `B_keep = 0.35`, else uniform; `L = 12`; `g` fixed pseudorandom |
| f2, f3 | C (coalitional pair) | additive mask: `f2 ~ uniform`, `f3 = (f2 + C_VAL[state, bucket]) mod 8`; individually uniform, jointly recover regime; bucket cycles with period = mean dwell |
| f4 | D (drift carrier) | emission peaked at a slowly-drifting mode; drift random-walk `std = 0.10`, peaking `1.0`, re-centered per regime entry |
| f5, f6, f7 | distractors | uniform / Zipf(1.1) / low-frequency(0.6) -- skewed marginals, NO structural coherence |

**Calibration (Metacoherence Sec 5.4, done 2026-06-23 by information-content balancing).** Parameters locked so the four properties' recoverable mutual information is comparable and no single property dominates. Measured (marginal-relative MI): `I_A = 0.76, I_B = 0.46, I_C = 0.34, I_D = 0.58` bits; max single-property share `0.356 < 0.40` (the Sec 5.4 ceiling); distractors structurally flat (regime MI 0.000, local MI 0.001) DESPITE skewed marginals. The exact "40%-of-`w`-variance-under-K3xA1" check is verified during the build with the real marginal-relative K3; params are fixed unless that verification forces a recorded amendment (the K4 / v0.6.0 discipline).

**CRITICAL design lock -- marginal-relative coherence.** Every estimator's coherence on D1 MUST be measured relative to each feature's marginal, NOT against a uniform baseline. The Zipf / low-frequency distractors carry low marginal entropy by design; a uniform-baseline measure mistakes that for coherence (a naive GRU did exactly this in due-diligence) -- the precise failure mode D1 exists to catch. This binds the categorical generalization of every proxy (predictive: `H_marginal - H_pred`; compression: structural vs marginal-only baseline).

**M5 feature-partition for D1 (locked, by construction).** Coherence-bearing class = {f0, f1, f2, f3, f4}; noise class = {f5, f6, f7}. Exact (a property of the generator, not derived from induced `w`). Feeds the M5 gate (deferred to the cross-domain capstone).

**R2 protocol (locked).** The 5x3 grid -- estimators {K1, K2, K3, K4, K5} x ablations {A1, A2, A3} -- generalized to alphabet-8 categorical features, run on D1; induced `w` over the 8 features per cell. R2 = cross-philosophy median Spearman rank correlation of the `w` vectors over philosophically-decoupled estimator pairs, with bootstrap CIs by time-window resampling at block length = mean sojourn (200), `B = 1000`. Pass: median Spearman `> 0.6`, lower 95% CI `> 0.4` (Metacoherence Sec 8.7, locked; distinct from v0.3's 0.7 and v0.5's 0.5). Categorical generalization: K1/K5 operate on the byte/bit encoding (alphabet-agnostic); K2 (per-feature categorical n-gram MDL), K3 (GRU softmax heads), K4 (categorical-emission HMM) are generalized from binary -- all with marginal-relative coherence.

**Property-recovery cross-tab (the Sec 5.7 deliverable).** For each of the 15 cells, report which of properties {A, B, C, D} the cell's induced `w` recovers (signal features ranking above distractors by a pre-registered margin). The 15x4 pattern is the diagnostic deliverable -- D1 is CHARACTERIZED, not pass/failed, at this level (expected: K1xA1 recovers A only; K3xA2 recovers A,B,C,D; A1 systematically misses C; short-context estimators miss B).

**Asserted invariants (locked v0.7.0).** (1) R2: cross-philosophy median Spearman `> 0.6` (CI `> 0.4`) on D1; (2) class separation: coherence-bearing features rank above distractors under every cell (the shared signal driving R2); (3) distractor flatness: distractors carry ~0 structural coherence (marginal-relative) despite skewed marginals; (4) the property-recovery cross-tab matches the pre-registered qualitative pattern; (5) generator determinism (bit-exact streams per seed).

**Gating.** The 5x3 grid on D1 includes K3 (neural) and K5/K3 Shapley (A2) -- `slow` / `very_slow` tiers as in v0.5. Cheap cells (K1/K2 x A1/A3) `fast`. New module `cit/data/hsmm_d1.py`; categorical proxy generalizations under `cit/proxies/`; tests `tests/test_metacoherence_d1.py`.

**Honest notes / risks.** (a) Marginal-relative coherence is load-bearing (above). (b) Property B recovery depends on the real categorical K3 actually learning the lag-12 coupling; if it cannot, B is recovered only by K4 (or not at all) -- recorded as a cross-tab finding, not tuned over. (c) `R2 > 0.6` on D1 is the source-locked threshold; because estimators legitimately diverge on B/C (the cross-tab's point), median Spearman is driven by class-separation with within-class rank noise -- if it falls short it is recorded honestly (seam), not adjusted. (d) `N_REPLICATES = 20`, replicate seeds locked; bootstrap `B = 1000`. (e) The exact Sec 5.4 ceiling is verified in-build. New locked constants: D1 generator params (above), `N_REPLICATES = 20`, R2 threshold `0.6` / CI `0.4`, bootstrap `B = 1000` (block = 200).

**Correction (2026-06-23, post-implementation, slice 1 build).** The generator `cit/data/hsmm_d1.py` is built and its structure verified (`tests/test_metacoherence_d1.py`). Two refinements of the record, no parameter changes. (1) The locked replicate seeds are pinned: `REPLICATE_SEED_BASE = 7000`, seeds `7000..7019`. (2) The calibration tuple above (`I_A = 0.76, I_B = 0.46, I_C = 0.34, I_D = 0.58`) was the *single* calibration-seed measurement (seed 1000, at the pre-lock `T = 60_000`); it is NOT representative of the locked replicate ensemble. Measured across all 20 locked seeds at the locked `T = 50_000` (plug-in MI): `I_A = 0.56 +/- 0.18` (range `[0.21, 0.99]`), `I_B = 0.47 +/- 0.01` (`[0.46, 0.48]`), `I_C = 0.46 +/- 0.17` (`[0.14, 0.82]`), `I_D = 0.58 +/- 0.03` (`[0.53, 0.63]`). Properties A and C are *seed-variable* -- each is fixed by one random structure draw per seed (the 3x8 `F0` regime logits for A; the 3x8 `C_VAL` mask table for C) -- so their recoverable MI legitimately varies seed to seed; B and D are seed-stable. Seed 1000 happened to draw A high and C low. The LOCKED invariant holds on EVERY replicate: max single-property share `0.315 +/- 0.03` (max `0.366`, `< 0.40` on every seed -- the Sec 5.4 ceiling); distractors structurally flat (max structural MI `~0.001`) marginal-relative DESPITE skewed marginals; class separation (every property MI `> 10x` every distractor's). The ensemble is in fact MORE balanced than the single calibration seed implied (all four means `0.46-0.58`). Consequence: the structure test asserts the seed-stable invariants (ceiling, flatness, separation, B/D bands, each property's structural signature), NOT a cherry-pickable point tuple. The exact `K3 x A1` `w`-variance ceiling is still verified in the slice-2 build with the real marginal-relative K3. Recorded here rather than silently anchoring the substrate to one favorable seed.

**Build record + findings (2026-06-23, slices 2-3).** Slices 2-3 build the categorical pipeline: `cit/proxies/categorical.py` (marginal-relative K1-K5), `cit/ablations/categorical.py` (A1/A2/A3, uniform-over-A replacement), `cit/induce_cat.py`, `cit/metacoherence.py` (R2 + property-recovery cross-tab). All marginal-relative per the load-bearing lock; distractors collapse from `~0.74-0.84` (raw baseline) to `~0.00`. K2 (per-feature bigram MDL), K3 (GRU softmax heads, `NEURAL_SEED=7`), K4 (factorized-categorical-emission HMM, `HMM_SEED=0`, H=1 is the marginal baseline). Findings, recorded honestly (no thresholds tuned):

1. **Line-791 correction (K1/K5 were NOT alphabet-agnostic).** The v0.5 byte encoder `(arr * 2^j).sum() -> uint16` is binary-specific: on alphabet-8 it is lossy (48490 distinct rows -> 1602 codes) and overflows. K1/K5 needed BOTH a categorical encoder AND a marginal-relative baseline (line 787's "every proxy", which binds). Built: a bit-tight `ceil(log2 A)`-bits/feature encoder + a **time-shuffle surrogate baseline** -- `C = 1 - complexity(real)/complexity(per-feature-time-shuffled)` -- the marginal-only surrogate (independent per-feature permutation, `SHUFFLE_SEED = 0`) preserves each marginal exactly while destroying all temporal/cross-feature structure, so skew and padding cancel. New locked constants: `SHUFFLE_SEED = 0`, K1 `ZSTD_LEVEL = 3` (carries v0.3), feature-major encoding.

2. **Encoding correctness fix (feature-major).** First-cut step-major layout (features interleaved 24 bits/step) buried per-feature temporal structure: K1xA1 was null, K5xA1 recovered only A. Audit criterion (set before seeing R2): *recover the A/D structure single-feature tests already prove present*. Feature-major layout (each feature's history contiguous -- the standard channel-grouped encoding for multivariate-sequence compression) recovers it: K5 then recovers A,B,C,D with distractors flat; K1 recovers A,C (noisier -- zstd is a global compressor, so LOO leaks cross-feature `~0.007`). Applied ONCE, justified by the recovery criterion independent of R2; no further encoder iteration.

3. **A3 degenerates to A1 on D1.** Pearson correlation-clustering finds only singleton clusters (D1's couplings are nonlinear mod-8 + lag-12 functional, invisible to Pearson), so `K x A3 == K x A1` here. Documented, not adjusted.

4. **R2 SEAM -- complementary, not convergent, recovery on the A1 column.** The A1 property-recovery cross-tab (reduced-T `T=8000` preview, seed 7000): K5 recovers `{A,B,C,D}`, K1 `{A,C}`, K2/K3/K4 `{A,D}` -- all agree on A, then DIVERGE on B/C/D. Because the philosophies are sensitive to different properties, their induced-`w` rank-vectors anti-correlate (K1|K3 Spearman `-0.66`) even as the modeling trio self-agrees (K2|K4 `0.93`, K3|K4 `0.88`, K2|K3 `0.71`); cross-philosophy median Spearman `~ -0.08`, FAR below the locked `0.6`. This is genuine philosophical divergence, NOT an artifact (it sharpened, not softened, after the K1/K5 correctness fix). Per the honest-notes (c) commitment above, `R2 > 0.6` on D1's A1 column is recorded as a **SEAM / falsifying result, not tuned**. D1 remains CHARACTERIZED (Sec 5.7): the complementary cross-tab IS the characterization.

5. **Open rescue (A2, deferred to CI).** The source expected A2 Shapley to recover all properties consistently (K3xA2 -> A,B,C,D); if so, the A1 divergence is ablation-specific and R2 could hold under A2. A2 Shapley is very_slow (K3/K5 A2 ~hours/cell at locked `T`, local-gated like the v0.5 K3 Shapley). The full locked-`T` 5x3 grid + A2 + the bootstrap-CI R2 verdict is therefore a CI/very_slow artifact (`scripts`/very_slow test, `GRID_ABLATION_SEED = 123`); the inline A1 preview is the honest interim result. The A2-rescue verdict is the decisive open question, recorded as pending -- NOT pre-judged.

### 2026-06-23 -- v0.7.0 record correction: D1 A1 result is instrument-validity (representation/philosophy confound), not a falsification; + decoupling-control pre-registration

**Why.** The slices 2-3 build record above (its point 4) framed the D1 A1-column result as an "R2 SEAM / falsifying result" against `R2 > 0.6`. A read-only audit of the single saved A1 column (seed 7000, T=8000, feature-major, w to 3dp; the `b1302...` grid preview) shows that framing OVERREACHES. This entry corrects it. The original point-4 text is left in place and is SUPERSEDED by this entry. No threshold moved (`R2 0.6` / CI `0.4` unchanged); no locked constant changed; no grid re-run; no code path changed by this entry.

**(a) Downgrade -- instrument-validity, not falsification.** The A1 grid splits into two blocks: {K1, K5} (within-block Spearman `+0.68`) versus {K2, K3, K4} (within `0.71-0.93`), anti-correlating across (every cross-block pair negative, cross-block median `~ -0.28`). That block boundary is COLLINEAR with the ENCODING boundary: K1/K5 share the byte/bit-stream encoder; K2/K3/K4 are categorical-native. So on D1, coding PHILOSOPHY and stream REPRESENTATION are CONFOUNDED -- the grid varies both together along the same cut. Sharpening the point: Metacoherence Sec 3.1 stakes its sharpest decoupling on K1 (codes) vs K5 (does not), yet empirically K1|K5 = `+0.68` -- one of the grid's strongest agreements -- so the source's designated K1-vs-K5 decoupling axis COLLAPSED (they agree, consistent with sharing the encoder). Consequence: `R2 > 0.6` on D1 is NOT YET ADJUDICABLE. A low cross-block median cannot be attributed to philosophy when philosophy and encoding move together. This is NOT a falsification of cross-philosophy convergence; it is "the instrument is not yet capable of the test." It is ALSO not a vindication.

**(b) Provisional.** The entire A1 picture is ONE underpowered draw: a single seed (7000), T=8000 (16% of the locked 50_000), w at 3dp. Property C -- which drives the {K1,K5} block (only a joint representation carries the f2,f3 coalition; a factorized proxy is architecturally blind to it) -- is the MOST seed-variable property (slice-1 correction above: `I_C = 0.46 +/- 0.17`). Nothing here is load-bearing in EITHER direction until it is rerun at full-T, 20 seeds, AND with the representation-decoupling control pre-registered in (e) below.

**(c) Banked positive.** One signal survives BOTH representations and ALL five proxies: property A (regime, f0) is recovered in every cell (saved cross-tab: A in K1, K2, K3, K4, K5; saved ranks: f0 outranks all three distractors in all five cells). This is the one genuine cross-decoupled convergence in the data and is recorded as the surviving R2 signal on D1.

**(d) Relabel the strict-separation invariant.** Asserted-invariant (2) (line 795: "class separation: coherence-bearing features rank above distractors under every cell") CONFLATES two distinct claims. It is split here; the original line-795 lock is NOT deleted, it is read henceforth as the substrate form only:
  - **(2-substrate) generator / MI-level separation** -- every property's recoverable MI far exceeds distractor MI. HOLDS (generator-tested, `tests/test_metacoherence_d1.py`: `> 10x` on every seed). This is what line 795 is now read to assert.
  - **(2-induced-w) induced-w separation per cell** -- every coherence-bearing feature outranks every distractor in the induced `w`. DOES NOT HOLD at A1: true for only 1 of 5 cells (K5). Saved ranks (seed 7000, T=8000): K2/K3/K4 leave f1,f2,f3 in/below the distractor band; K1 ranks f4 (property D) BELOW ALL THREE distractors (f4 = 0.483 < min distractor 0.494). The induced-w form is FALSE as a universal-over-cells claim; it is superseded by the per-property `recovered_properties` semantics already in code (each cell recovers a SUBSET of {A,B,C,D}).

**Discipline.** "Recorded, not tuned" carries into this correction: no threshold, no locked constant, no code path changed by it. The R2-statistic definition is separately flagged (read-only audit): the coded `cross_philosophy_r2` median is over ALL grid pairs, not the cross-decoupled pairs only -- diluting cross-block with within-block. Whether to redefine R2 to the source's cross-philosophy-pairs-only statistic (Metacoherence Sec 3.3) is a SEPARATE pre-registered decision, not made or coded here.

**(e) Pre-registered decoupling control (PENDING -- design only, NOT implemented).** Before D2/D3, and before any D1 R2 verdict is treated as load-bearing, run a control that makes REPRESENTATION and PHILOSOPHY independent axes:
  - **Diagnosis (locked):** the v0.7.0 grid varies coding philosophy and stream encoding together; the {K1,K5} | {K2,K3,K4} block boundary equals the byte-stream | categorical-native boundary.
  - **Control (one of, to be pre-registered when run):** (i) hold the ENCODING constant across all five proxies (every proxy on a single shared representation), OR (ii) add a non-coding JOINT proxy and/or run a factorized proxy on the joint byte stream, so "joint representation" and "coding philosophy" become independent axes.
  - **Confirm/deny criterion (LOCKED IN ADVANCE):** rerun at full-T (50_000), 20 seeds. If the block boundary FOLLOWS ENCODING (it moves when representation is crossed, holding philosophy fixed), the D1 R2 result is a REPRESENTATION ARTIFACT. If it FOLLOWS PHILOSOPHY (survives representation-crossing), R2 has real traction on D1. This criterion is fixed now; the outcome is recorded honestly in either direction.
  - **Status:** PENDING, not implemented, sequenced before D2/D3.

### 2026-06-23 -- v0.7.0 decoupling control: pre-registration (modeling-on-byte-stream crossing, A1, full-T, 20 seeds)

**What this is.** This entry pre-registers, in full and before any cell runs, the decoupling control whose DESIGN was committed as PENDING in the record-correction entry above (its point (e)). It selects control option (e)(ii) -- add MODELING proxies on the BYTE-STREAM representation -- and fixes the crossing proxies, the cluster-assignment metric, the seed ensemble, and the concordance decision rule NOW, so the verdict cannot be tuned after the fact (the Sec 8 pre-register-before-implementation discipline). No code is written in this entry; no v0.7.0 threshold or locked constant is changed (R2 `0.6` / CI `0.4` untouched). Implementation is the SECOND step, gated separately, with its outcome recorded honestly in either direction.

**The confound being broken.** The v0.7.0 A1 grid populates only two of the four (representation x philosophy) corners, and they lie on the SAME diagonal -- so representation and philosophy are collinear:

    representation \ philosophy   coding / parsing       modeling / predictive
    byte-stream                   K1 (zstd), K5 (LZ76)   -- EMPTY --   <- filled here
    categorical-native            -- EMPTY --            K2, K3, K4

The {K1,K5} | {K2,K3,K4} block split observed at A1 therefore cannot be attributed to philosophy: it equals the byte-stream | categorical boundary. This control fills the empty `byte-stream x modeling` corner, making representation and philosophy INDEPENDENT axes.

**The crossing proxies (LOCKED): K3b and K2b, co-primary.** Two modeling proxies are crossed onto the byte stream and run TOGETHER (neither is a fallback to the other), because a single crossing is weak evidence and the two are weak in OPPOSITE ways:
  - **K3b -- lowest-distortion crossing** = the K3 neural-prequential predictive-likelihood functional on the byte stream. K3 is the most flexible proxy, so K3b distorts the philosophy least under re-encoding; but for the same reason a lone K3b PHILOSOPHY result is weak -- a representation-invariant GRU may show "K3 is robust," not "the split is philosophical." `NEURAL_SEED = 7` carried (deterministic, CPU-only).
  - **K2b -- most mechanistically targeted crossing** = the K2 bigram-MDL functional on the byte stream. K2's factorized, coalition-blind structure IS the confound mechanism (a factorized proxy is architecturally blind to the C coalition that drives the {K1,K5} block), so K2b tests directly whether that blindness follows the PROXY or the REPRESENTATION. Deterministic (MDL, no RNG).

Both apply their functional to the IDENTICAL feature-major bit-tight byte-stream encoding that K1 and K5 consume, via the IDENTICAL A1 LOO machinery and the IDENTICAL time-shuffle surrogate baseline (`SHUFFLE_SEED = 0`); {K1, K5, K3b, K2b} share representation, encoder, baseline, and ablation EXACTLY and differ ONLY in the complexity functional (compression / parsing / neural-prediction / bigram-MDL). Requiring CONCORDANCE across both crossings is far stronger than either alone; if they DISAGREE, that disagreement is itself a finding (the split is proxy-specific, not a clean representation/philosophy dichotomy -- a first-class verdict below). (The mirror corner, a categorical-native CODING proxy, is NOT crossed: it would require a new, less-canonical "categorical compression" functional and so introduce its own representation question.)

**Scope (LOCKED).** A1 ONLY (A2 Shapley is the separate, deferred rescue verdict; A3 == A1 on D1, slices-2-3 build-record point 3). Full-T `= 50_000`. Seeds = the locked replicate ensemble `7000..7019` (`N_REPLICATES = 20`); no new seed base. "Enough seeds for stable cluster assignment" is operationalized by the 18/20 supermajority in the decision rule below.

**Cluster-assignment metric (LOCKED) -- twin-excluded, cross-functional.** For each seed `s in {7000..7019}`, run the A1 column at `T = 50_000` and induce the per-feature `w` rank-vector for each of {K1, K2, K3, K4, K5} plus the two crossings K3b, K2b. The decision Delta for a crossing proxy P is its mean Spearman to the MODELING reference set minus its mean to the BYTE-STREAM reference set -- with P's OWN TWIN EXCLUDED from the modeling set, so every term is cross-functional. The twin correlation (K3b-vs-K3, K2b-vs-K2) is a same-functional / same-information / different-serialization quantity, high for trivial reasons; putting it in the decision mean would inflate the modeling side and pre-tilt the verdict toward PHILOSOPHY. The claim under test is "P resembles the modeling philosophy AS A CLASS," not "P resembles its own reflection."

Reference sets (twin-excluded):

    P = K3b :  M3 = {K2, K4}      B = {K1, K5}
    P = K2b :  M2 = {K3, K4}      B = {K1, K5}

Per crossing proxy P and seed s:

    s_M(P,s)    = mean over X in M_P of  Spearman( w[P], w[X] )
    s_B(P,s)    = mean over X in B    of  Spearman( w[P], w[X] )
    Delta(P,s)  = s_M(P,s) - s_B(P,s)
    label(P,s)  = M  if Delta(P,s) > 0  else  B

Aggregate over the 20 seeds, per proxy: `n_M(P) = #{ s : label(P,s) = M }`; `median_Delta(P) = median_s Delta(P,s)`. (Spearman per the existing `cit.metacoherence.spearman`; a zero-variance cell yields NaN and is dropped from that seed's block mean, as already coded.)

**Twin sanity checks (REPORTED, NOT decision inputs).** Spearman(K3b, K3) and Spearman(K2b, K2) per seed are recorded SEPARATELY as representation-invariance diagnostics: high values confirm each functional is representation-stable (so the crossing is low-distortion); a low twin correlation would mean the functional is itself representation-sensitive, which would CONTEXTUALIZE -- but never drive -- that proxy's verdict.

**Per-proxy assignment (LOCKED) -- stability x magnitude, two-band.** For each crossing proxy P, combine the stability sign-count with a two-band magnitude read of `median_Delta(P)`. (Delta's real dynamic range is `~ +-1.1` -- full assignment `~ within-family 0.8` minus `cross-family -0.28` -- so a decisive decoupling lands near `+-0.5..1.0`; `0.10` only rules out `~0`, hence the second band.)

    stable-toward-M  :  n_M(P) >= 18 / 20
    stable-toward-B  :  n_M(P) <=  2 / 20
    |median_Delta(P)| >= 0.40         ->  CONFIDENT
    0.10 <= |median_Delta(P)| < 0.40  ->  WEAK-LEAN   (reported as a lean, not a clean call)
    |median_Delta(P)| <  0.10         ->  NONE (~0)

    assignment(P) = MODELING  if stable-toward-M and median_Delta(P) >= +0.10   (CONFIDENT if >= +0.40, else WEAK-LEAN)
                  = BYTE      if stable-toward-B and median_Delta(P) <= -0.10   (CONFIDENT if <= -0.40, else WEAK-LEAN)
                  = UNSTABLE  otherwise  (3 <= n_M(P) <= 17, or |median_Delta(P)| < 0.10)

The `18/20` sign-count is the locked stability bar; the implementation ALSO reports each proxy's 20-seed `Delta(P, .)` distribution 90% interval (whether it excludes 0) as a corroborating read, but the locked decision uses the sign-count.

**Concordance verdict (LOCKED IN ADVANCE -- TOTAL over all nine cells, fixed before any cell runs).** Each crossing independently resolves, after the 18/20 + two-band step, to exactly one of THREE per-crossing states: `assignment(P) in {MODELING, BYTE, UNSTABLE}` (MODELING/BYTE carry a CONFIDENT or WEAK-LEAN sub-band; UNSTABLE has none). Two crossings x three states = NINE combinations; ALL nine are mapped HERE, so no cell is adjudicated after seeing the number. Verdict = f(assignment(K3b), assignment(K2b)):

                       K2b=MODELING      K2b=BYTE          K2b=UNSTABLE
    K3b=MODELING       PHILOSOPHY        PROXY-SPECIFIC    INCONCLUSIVE*
    K3b=BYTE           PROXY-SPECIFIC    REPRESENTATION    INCONCLUSIVE*
    K3b=UNSTABLE       INCONCLUSIVE*     INCONCLUSIVE*     INCONCLUSIVE

    (*) exactly one crossing decisive, the other UNSTABLE -> INCONCLUSIVE, with the
        single decisive crossing's LEAN (which proxy, PHIL or REP direction) RECORDED
        but licensing NO terminal verdict; U/U -> INCONCLUSIVE with no lean.

The four terminal verdicts (the two same-decisive corners + the two opposite-decisive cells):

- **PHILOSOPHY (split tracks coding philosophy -> D1 R2 is adjudicable):** both = MODELING. Both modeling functionals join the modeling class DESPITE the byte-stream representation -> the {K1,K5}|{K2,K3,K4} split is driven by philosophy, the v0.7.0 confound is broken in favor of philosophy, and the A1 low cross-philosophy median is a GENUINE divergence -- `R2 > 0.6` becomes a valid (and, on the A1 evidence, failing) test on D1. CONFIDENT if both proxies CONFIDENT, else PHILOSOPHY-WEAK-LEAN.

- **REPRESENTATION ARTIFACT (split tracks encoding -> D1 R2 not yet a valid test):** both = BYTE. Both join the byte-stream block DESPITE the modeling philosophy -> the split is an encoding artifact; `R2 > 0.6` on D1 is not a valid cross-philosophy test as instrumented, and the recorded fix is to equalize representation (control option (e)(i)) before ANY D1 R2 verdict. CONFIDENT if both proxies CONFIDENT, else ARTIFACT-WEAK-LEAN.

- **PROXY-SPECIFIC SPLIT (a finding in its own right):** the two are OPPOSITE-decisive (one MODELING, one BYTE). The confound is then proxy-dependent -- K2's factorized blindness and K3's flexibility behave differently under re-encoding -- so neither a clean PHILOSOPHY nor a clean REPRESENTATION verdict holds; redirects to control option (e)(i) and/or a wider crossing before any D1 R2 verdict. **CAVEAT (weight accordingly):** K2b carries MORE model-change than K3b -- K3b is genuinely "same functional, different serialization," whereas K2b as a bigram over the byte stream is closer to a BYTE-bigram than a feature-bigram (its factorization unit shifts from feature to byte; that shift is exactly what targets the C-blindness). So a PROXY-SPECIFIC-SPLIT has an alternative reading -- K2b being a meaningfully different MODEL, not a deep proxy-specificity of the split -- and must be weighted as such, not read as a clean third dichotomy.

- **INCONCLUSIVE (no verdict licensed):** any cell with one or both crossings UNSTABLE (the five `*`/`U,U` cells above). Concordance cannot be established from a single decisive crossing -- the co-primary design exists precisely because one crossing is weak evidence -- so a lone decisive result does NOT license PHILOSOPHY or REPRESENTATION; it is recorded as INCONCLUSIVE with the single-crossing LEAN noted (proxy + direction), and the recorded next move is control option (e)(i) and/or additional crossings. Not pre-judged.

**New locked numbers (this entry only).** Stability supermajority `18/20` (with each proxy's 20-seed Delta-distribution 90% interval reported as a corroborating read); magnitude bands `CONFIDENT |median_Delta| >= 0.40`, `WEAK-LEAN 0.10 <= |median_Delta| < 0.40`, `NONE < 0.10`. No new estimator or seed constants -- K3b carries `NEURAL_SEED = 7`, K2b is deterministic, both carry `SHUFFLE_SEED = 0` and the feature-major encoder, and the control seeds are the locked `7000..7019`. The R2 threshold and every v0.7.0 locked constant are unchanged by this entry.

**Status.** PENDING implementation. The two co-primary crossing proxies (K3b, K2b), the twin-excluded cross-functional metric, the twin sanity checks, and the TOTAL nine-cell concordance decision rule (incl. the K2b model-change caveat) are FIXED as of this entry; the build (the K3b + K2b proxies + the A1 full-T x 20-seed run + the metric computation, a CI/very_slow artifact) is the next step and supersedes nothing here.

### 2026-06-24 -- v0.7.0 decoupling control: RESULT (INCONCLUSIVE) + I_C property-dependence diagnostic (REJECTED)

**What this is.** The decoupling control pre-registered in the 2026-06-23 entry above was RUN to completion; this entry records its outcome with the CAUTIOUS framing, plus a read-only I_C diagnostic pre-registered before computing. No locked constant changed; no grid re-run; control option (e)(i) NOT executed. The I_C diagnostic is read-only (plug-in MI on the locked seeds, the line-801 `_properties` method). Both the terminal verdict and the diagnostic are reported against rules fixed BEFORE the numbers were seen.

**Run.** `scripts/run_decoupling_control.py --T 50000` over the locked 20-seed ensemble (`7000..7019`), A1-only, sharded one seed per process. 20/20 seeds completed, ZERO failures (`results/decoupling_control/verdict.json`).

**(a) Terminal verdict: INCONCLUSIVE** -- per the locked nine-cell rule, the cell `(K3b = MODELING, K2b = UNSTABLE)`.

**(b) Per-crossing.**
- K3b (lowest-distortion crossing): MODELING, CONFIDENT. `n_M = 20/20`, median `Delta = +0.506`, 90% interval `[+0.137, +0.956]` (excludes 0).
- K2b (more-model-change crossing): UNSTABLE. `n_M = 17/20` (misses the locked `18/20` by ONE seed; 3 negative-`Delta` seeds `7003 -0.226`, `7008 -0.119`, `7018 -0.060`), median `+0.363` (WEAK band), 90% interval `[-0.124, +0.639]` (straddles 0).
- Twin sanity (REPORTED, not decisional): `K3b-K3 = 0.881`, `K2b-K2 = 0.798`.

**(c) Headline -- necessary, NOT sufficient (stated precisely).** The representation-artifact reading is WEAKENED: at full power nothing leaned byte (the underpowered `T=400`/2-seed smoke's negative lean was noise). But the PHILOSOPHY reading is NOT ESTABLISHED. The verdict rests SOLELY on K3b -- the crossing pre-flagged at design time (the 2026-06-23 entry, K3b bullet) as able to lean modeling for TRIVIAL flexibility reasons: a representation-invariant GRU shows "K3 is robust," not necessarily "the split is philosophical." Its twin Spearman `0.88` is consistent with representation-INVARIANCE, not only with faithfulness, so it does not discriminate the two readings. Meanwhile K2b -- the crossing that probes the ACTUAL factorized C-blindness mechanism -- was inconclusive. So the control removes the strong-artifact reading and leaves a SINGLE-crossing modeling lean that, by the pre-registered bar, does NOT license a PHILOSOPHY verdict. This entry does NOT narrate "the needle moved toward philosophy" or any equivalent gloss: a `17/20` that does not round to `18/20` must not be narrated as a near-win.

**(d) Discipline (Sec 5 / Sec 8).** The metric held the line -- `17/20` was NOT rounded to a verdict. This record holds the NARRATIVE to the same bar: the cautious framing in (c) is that discipline applied to prose, not only to the threshold.

**(e) I_C property-dependence diagnostic (pre-registered, read-only) -- REJECTED.** The cheap check before any follow-up control: does K2b's instability track coalition property C?
- **Hypothesis (fixed before computing):** K2b probes property C; on high-I_C seeds, byte-adjacency exposes the coalition and pulls K2b toward the `{K1,K5}` byte cluster (negative `Delta`). Prediction: the 3 negative-`Delta` seeds `{7003, 7008, 7018}` are HIGH-I_C (top half of I_C ranks, clustered), and `Spearman(K2b Delta, I_C)` over the 20 seeds is NEGATIVE.
- **Disconfirmer (pre-committed):** if the negative-`Delta` seeds are NOT systematically high on I_C, property-dependent-representation is REJECTED; the K2b instability is recorded as noise / genuine borderline -- INCONCLUSIVE-as-noise stands.
- **Computed** (per-seed I_C via the committed line-801 plug-in `_properties` method on the locked `T=50000` streams; ensemble mean `0.462 +/- 0.172`, range `[0.143, 0.821]` -- reproduces line-801 exactly): the 3 negative-`Delta` seeds rank `[12, 1, 17]` of 20 on I_C -- SCATTERED, mean rank `10.0` (random expectation `10.5`); one of them (`7008`) is the LOWEST-I_C seed of all 20 (rank 1, `I_C = 0.143`), the direct opposite of the prediction. `Spearman(K2b Delta, I_C) = -0.251`: weakly negative, BELOW the `|0.4|` support threshold, NOT significant at `n=20` (`|rho| ~ 0.45` needed for `p<0.05`), and NOT produced by the claimed mechanism (the negative-`Delta` seeds being high-I_C, which is falsified).
- **VERDICT: property-dependent-representation REJECTED.** Per the pre-committed disconfirmer the scattered ranks alone reject, independent of the weak Spearman. The K2b near-miss is genuine borderline NOISE, not a C-coalition representation signal. INCONCLUSIVE-as-noise stands. (No softening.)

**(f) Next control stays PENDING and gated.** The locked INCONCLUSIVE branch's recorded next move -- control option (e)(i), hold ONE encoding constant across all five proxies -- remains PENDING and UNJUDGED. With the I_C diagnostic REJECTED (Step-1 = noise), (e)(i) is the recorded next control IF the question is pursued further; it is NOT executed here. Known distortion of (e)(i), recorded so it is not forgotten: the coding/parsing proxies (K1, K5) CANNOT be made categorical-native, so holding encoding constant forces the MODELING proxies onto the byte stream rather than the reverse -- (e)(i) probes the same axis from the opposite anchor and carries its own representational commitment.

**Discipline.** No threshold moved (`R2 0.6` / CI `0.4`; the decoupling `18/20` + magnitude bands -- all unchanged); no locked constant changed; no grid re-run; (e)(i) NOT run. Artifact: `results/decoupling_control/verdict.json` + the run scripts are committed as the experiment record.

### 2026-06-24 -- v0.7 program reframe: D1 -> coverage-calibration; R2 demoted to DIAGNOSTIC; R1 / functional convergence elevated to PRIMARY

**What this is.** A PROGRAM-EPISTEMICS amendment, NOT a results change. It reclassifies the evidential STATUS of the v0.7 conditions; no locked constant VALUE is changed (the R2 `0.6` / CI `0.4` numbers are SUPERSEDED IN STATUS -- pass/fail gate -> diagnostic flag -- NOT deleted and NOT edited as numbers), the R2 grid is unchanged and still runs, control option (e)(i) is not run, and the one tabulation below is read-only from the EXISTING recorded cross-tab (no new compute).

**Anti-post-hoc gate (the structural justification, stated BEFORE the status change).** The two grounds for demoting R2 each hold INDEPENDENT of the D1 outcome; were either dependent on the D1 miss, the demotion would be post-hoc and would not proceed.

(i) **Coverage ceiling -- a property of cross-extractor agreement as such.** Induced `w` from estimator K is constitutively a property of the PAIR (substrate x K): `w(x) = sigmoid(beta * rho_K(x))`, and `rho_K` ablates K's OWN complexity functional, so `w` reflects the structure K can EXTRACT, not a substrate-intrinsic observable. Cross-estimator agreement can therefore certify coherence only of structure inside the SHARED representational coverage of all estimators. In the selectively-extractable region (structure some K see and others constitutively cannot), divergence is unavoidable AND ambiguous -- indistinguishable between "no latent coherence invariant" and "non-overlapping coverage." This holds regardless of D1: had D1's R2 PASSED, the pass would have certified only shared-coverage / least-common-denominator structure (the LEAST interesting claim -- the intersection of five inductive biases); having FAILED, the failure is ambiguous. R2 is structurally weak in BOTH directions, independent of outcome. The metrology analogy that grounds R2-as-convergence (independent instruments agreeing certifies a real observable) FAILS here because K1-K5 compute DIFFERENT FUNCTIONALS (compression / parsing / prediction / MDL), not independent measurements of one observable.

(ii) **Corpus alignment -- a fact about the framework's own structure.** Of Metacoherence's four conditions, R2 is the ONLY one demanding agreement on the weight VECTOR (a REPRESENTATIONAL / correspondence claim: do the w's match). R1 (does w predict persistence) and R3 (does w respond asymmetrically to structural vs interpretive intervention) are FUNCTIONAL (does w DO the work). The Synthetic Epistemology corpus is functionalist -- validation = coherence-under-composition / doing work, not correspondence to a hidden true weight -- so R2 is the LEAST corpus-aligned of the four conditions. This predates any D1 result.

**Honesty (the project's amendment rule).** The D1 failure SURFACED these limits; it did not CREATE them. This is a FAILURE-DRIVEN amendment in the project's documented sense -- amendments enter when an observed fork demands it -- NOT a threshold moved to dodge a miss. The distinction is preserved mechanically: the `0.6/0.4` numbers are untouched, the grid still runs, R2 still reports; only R2's evidential STATUS changes. CRITICALLY, the demotion does NOT immunize the framework: falsifiability is RELOCATED, not removed. R2 ceasing to falsify is COMPENSATED by elevating R1/R3 (functional) to the PRIMARY falsifiable cross-domain test -- a HEAVIER commitment, since the framework's empirical stake now rests on functional convergence (w from any estimator doing the same work), which is both more corpus-aligned and not coverage-capped. A demotion that left nothing falsifiable would be an immunizing dodge and is explicitly NOT what this entry does.

**Part A -- D1's role: ESTIMATOR COVERAGE CALIBRATION (not R2 pass/fail).**
- The D1-level commitment `R2 > 0.6` (the 2026-06-23 D1 lock + the D1 "Asserted invariants" line) is SUPERSEDED IN STATUS as of this entry (2026-06-24): D1 is no longer the site of an R2 pass/fail verdict. The NUMBER is NOT deleted; D1's R2 is read henceforth as a coverage diagnostic (Part B). This resolves the prior record's internal contradiction -- "D1 is CHARACTERIZED, not pass/failed" (Sec 5.7, lines 793/811) co-existing with a locked D1 `R2 > 0.6` threshold -- in favor of CHARACTERIZED.
- **D1 deliverable = the per-K coverage map** (read-only, from the existing A1 cross-tab; feature-major, `T=8000`, seed 7000):

      K (philosophy)           recovers (D1 A1)
      K1  compression (zstd)    A, C
      K2  bigram MDL            A, D
      K3  GRU prequential       A, D
      K4  MDL-HMM               A, D
      K5  LZ76 parsing          A, B, C, D
      ENSEMBLE (union K1..K5)   A, B, C, D     <- all four properties recoverable

  **The finding is DIFFERENTIAL coverage with K5 most complete -- ASYMMETRIC, not compositional.** Property A is recovered by ALL five estimators (the universal survivor); beyond A, coverage is gapped and unequal -- K5 (parsing) is the BROADEST net (A,B,C,D), the modeling trio gapped to {A,D}, compression to {A,C}. The ensemble union being all-four is TRUE but is CARRIED ENTIRELY BY K5: this is NOT "five partial views compose into a whole" (the romantic reading the original framing leaned toward), it is "one estimator is the widest aperture, the others are specialized / gapped." The ASYMMETRY, not the union, is the actionable calibration content. ACTIONABLE FOR D2/D3 (no ground truth there): weight K5-type PARSING as the widest aperture, and treat the modeling trio and compression as SPECIALIZED / CONFIRMATORY, NOT co-equal voters. CAVEAT (the calibration ITSELF is provisional, not just R2): "K5 most complete" rests on a SINGLE seed (7000) at 16% of locked T (`T=8000`) with C the most seed-variable property -- a provisional RANKING to re-confirm at full-T / 20-seed, not a locked fact. (This corrects the request's "ensemble recovers all though no single K does": K5 alone recovers all four, so the honest shape is differential-with-K5-most-complete, NOT complementary composition.)
- This coverage map is the calibration output: it tells you how to READ R2 on D2/D3 (Pfam, FOMC), where there is NO ground truth -- a low cross-K R2 there is read against the D1-calibrated expectation that estimators have DIFFERENTIAL coverage, NOT as a falsification.

**Part B -- R2 status (DIAGNOSTIC) + R1 elevation (PRIMARY), program-wide.**
- **R2 reclassified DIAGNOSTIC.** Informative when it CONVERGES (corroborating: shared-coverage structure is coherent), but UNINFORMATIVE-NOT-FALSIFYING when it DIVERGES (the coverage ceiling makes divergence ambiguous). R2 still runs on every domain (grid unchanged, `GRID_ABLATION_SEED = 123`); the `0.6` / CI `0.4` numbers stay as a CONVERGENCE-FLAG threshold, not a pass/fail gate.
- **R1 (persistence prediction) + the v0.6.2 selective-compression functional win ELEVATED to PRIMARY cross-domain evidence.** The primary claim becomes FUNCTIONAL convergence -- w induced by any estimator DOES THE SAME WORK (predicts persistence; yields the selective-compression saving) -- rather than weight-vectors matching across estimators. Re-sequence: R1 is the NEXT build; R2 runs alongside as a diagnostic.
- **R1 spec guard (pre-registered NOW, before R1 is built): functional convergence = per-estimator functional validity AGGREGATED, NOT cross-estimator agreement on predictions.** R1 per-estimator is STILL coverage-limited -- if K2 cannot see C, its w will not weight C, so its persistence prediction misses C-driven persistence. R1 escapes R2's coverage ceiling NOT by being coverage-free but because it does NOT require cross-estimator AGREEMENT: each estimator's w is tested for functional validity INDEPENDENTLY (does w predict persistence -- a clean per-estimator yes/no fork). So "functional convergence" is DEFINED as multiple independent estimators' w EACH doing the work (per-estimator validity, then aggregated), and explicitly NOT as "the estimators' persistence-predictions AGREE with each other." Operationalizing R1 as cross-estimator prediction-AGREEMENT would smuggle the coverage-ambiguity straight back in under a functional label -- demoting R2 only to recreate it. The PER-ESTIMATOR functional-validity test is the falsifiable unit; cross-estimator agreement is precisely what this amendment learned NOT to lean on. This distinction is LOCKED into R1's spec by this entry, while it is salient.
- **Eight-cell outcome matrix -- FLAGGED, not resolved.** The Metacoherence Sec 8.3-8.4 matrix binds (R1, R2, R3) configurations as pass/fail axes; under R2-as-diagnostic (R2 no longer a pass/fail axis) the matrix needs RE-DERIVATION (plausibly: R1/R3 as the pass/fail axes, R2 as a coverage annotation). Recorded as a CAPSTONE-PENDING dependency; NOT fixed in this entry.

**Discipline.** No locked constant VALUE changed (`R2 0.6` / CI `0.4`, `beta = 4.0`, all seeds, the decoupling `18/20` + bands -- unchanged); the R2 grid is intact and still runs; no grid re-run; (e)(i) not run; the eight-cell matrix is flagged-not-resolved. The coverage map is read-only from the existing cross-tab.

### 2026-06-24 -- v0.7.1 R1 (persistence prediction) pre-registration: D1 protocol, the K3-yardstick erratum, D-centricity recorded-not-gated

**Scope.** Pre-registers R1 (persistence prediction) for D1 ONLY -- the next build under the 2026-06-24 program reframe, which elevated R1 to the PRIMARY falsifiable cross-domain test. Design only: no code, no run, no grid in this entry. The R1 statistic, protocol, and pass thresholds are TRANSCRIBED from Meta-coherence.docx (the v0.7 source) where it locks a choice; the single deviation (the persistence yardstick) is recorded below as a dated erratum-correction in the project's established style (cf. the Sec 6 Binary-Coherence-Channel fixture erratum, 2026-06-23 v0.6.0; the Thm 5.1 repair, 2026-06-23 v0.6.1). D2 (Pfam) and D3 (FOMC) R1 statistics are deferred to those domains. Prerequisites on record: the R1 spec guard (this file, 2026-06-24 reframe, Part B) and the D1 coverage map (same entry); HEAD includes the reframe (`bbd081c`).

**1 -- transcribed from the source (LOCKED, not chosen).**

- **R1 = persistence prediction (Meta-coherence Sec 2.2).** Induced `w` names features as coherence-bearing; R1 requires that high-`w` features participate demonstrably in the substrate's ability to persist. The test is binary in form: `w` predicts persistence or it does not. "R1 is where the framework cashes its ontological commitment" -- if high-`w` features are not the ones the substrate's persistence dynamics retain, the measurement operation has decoupled from the ontology.
- **D1 protocol (Sec 5.5).** Per feature, corrupt that feature's emission distribution by a FIXED-MAGNITUDE convex mix with the uniform distribution, applied at a designated onset in a perturbation-replicate stream. Two persistence measures:
  - `tau_rec` (regime-inference recovery time): steps after onset before a Viterbi decoder on the perturbed stream re-agrees with the unperturbed-stream Viterbi regime estimates within a calibrated agreement threshold.
  - `h_pred` (predictive horizon): steps after onset over which the perturbed stream's predictive log-likelihood under the K3 baseline estimator stays within a calibrated band of the unperturbed stream's.
  R1 tests whether high-`w` features yield SYSTEMATICALLY WORSE persistence (larger cost) under perturbation than low-`w` features.
- **Statistic + pass (Sec 8.7, App C.3).** Per-(K,A) cell: Cohen's d between the high-`w`-feature and low-`w`-feature persistence outcomes, high/low partitioned at the MEDIAN induced-`w` per cell. Pass: `d > 0.5`, bootstrap lower 95% CI `> 0.3`, `p < 0.01` (Bonferroni at the capstone). Bootstrap `B = 1000`; for D1 the resampling unit is the 20 REPLICATE STREAMS (seeds 7000-7019) per the App C.3 D1 branch (`bootstrap_replicate_streams`) -- distinct from R2/M5's time-window block resampling, which is condition/domain-specific in the source, not a conflict.
- **Source design intent (Sec 5.4).** Property D (drift-persistence coupling, feature f4) IS the R1 signal in D1: recovery requires registering f4's slow drift component as coherence-bearing. Properties A/B/C are recoverability tests (whether the measurement operation can SEE them), not persistence carriers. D1 R1 is therefore D-CENTRIC BY CONSTRUCTION.

**2 -- the K3-yardstick erratum (deviation, documented; the contaminated measure is RETIRED from the verdict).** Sec 5.5 specifies `h_pred` under "the K3 baseline estimator." But K3 is ALSO one of the five scored estimators in the grid: its induced `w` ranks features by leave-one-out contribution to K3's OWN predictive coherence. So in K3's own cell, the features K3 calls high-`w` are -- BY CONSTRUCTION -- the features whose perturbation most degrades K3's predictive log-likelihood, i.e. high `h_pred`-cost. The yardstick and the ranker are the same functional; K3's Cohen's d is inflated relative to the other four cells. This is a FAIRNESS FLAW in an estimator-scoring test (the same class of self-reference the framework names as a failure mode, here at the metric level). It is corrected as an ERRATUM (cf. the Sec 6 fixture erratum, the Thm 5.1 repair), NOT carried as a flagged-but-retained measure -- keeping a known-biased readout when a clean equivalent exists merely carries the bias. Resolution:

  - **PRIMARY measure = `tau_rec`** (Viterbi on the TRUE D1 generator). Source-specified (Sec 5.5), integer-valued, estimator-NEUTRAL (the true HSMM parameters, owned in the full-transparency tier). The headline per-cell Cohen's d is computed on `tau_rec`; it is the zero-deviation, maximally-faithful load-bearing statistic.
  - **CO-REPORTED NEUTRAL ROBUSTNESS CHECK = true-HSMM `h_pred`** (predictive horizon measured under the TRUE generator's likelihood, NOT K3's). This is the neutral, CONTINUOUS form of the source's `h_pred`: same predictive-horizon shape, the K3 self-reference removed. It STRICTLY DOMINATES the contaminated K3 form (same continuous sensitivity, no contamination), so the contaminated form is retired rather than carried. The continuity directly buys back POWER -- the bottleneck this construct keeps hitting (coarse 4-vs-4 splits, 8 features, near-ties). Co-reported with `tau_rec`; feeds the verdict-stability rule (Step 4).
  - **DEMONSTRATION-DIAGNOSTIC = contaminated K3 `h_pred`, reported ONCE** to MEASURE the inflation rather than merely assert it: K3 `h_pred`'s Cohen's d for K3's OWN cell, reported next to `tau_rec` and true-HSMM `h_pred` on that cell. If it is inflated relative to the two neutral measures on K3's cell, the self-reference bias is shown EMPIRICALLY (the project's posture: demonstrate, don't claim). It does NOT enter the R1 verdict.

  **Deviation note (scoped -- the line to get right).** The source's K3-based `h_pred` is SUPERSEDED FOR D1 ONLY by the neutral true-HSMM form, because in this grid K3 is a SCORED estimator and using its likelihood as the persistence yardstick is self-referential. The neutral true-HSMM measure is legitimate SPECIFICALLY BECAUSE D1 is the FULL-TRANSPARENCY tier where the generator is owned; this correction therefore does NOT transfer to D2/D3, where the substrate generator is unavailable and a portable yardstick (K3, or a domain-appropriate estimator) returns. Sec 2.2 explicitly sanctions a domain-VARYING persistence measure (regime-recovery in D1, substitution tolerance in D2, post-statement persistence in D3), so a D1-specific neutral measure is WITHIN the source's own framing, not a silent global change to R1.

**3 -- R1 independence / D-centricity (RECORDED, NOT gated).** Because D1 R1 is D-centric by design (Sec 5.4), the per-estimator R1 outcome is SUBSTANTIALLY ANTICIPATED by the D-coverage column of the reframe coverage map:

      K1  compression (zstd)   covers {A,C}      -- MISSES D
      K2  bigram MDL           covers {A,D}      -- covers D
      K3  GRU prequential      covers {A,D}      -- covers D
      K4  MDL-HMM              covers {A,D}      -- covers D
      K5  LZ76 parsing         covers {A,B,C,D}  -- covers D

  PREDICTION (pre-registered as a per-estimator finding, NOT a global pass/fail): K1 is ATTENUATED on the D signal because it puts f4 (property D) in its LOW-`w` group -- already corroborated on record (2026-06-23 D1 build, honest-note 2-induced-w: at A1, K1 ranks f4 = 0.483 BELOW all three distractors), so perturbing K1's "low-`w`" set includes the genuinely persistence-bearing f4 and dilutes K1's Cohen's d. K2/K3/K4/K5 (all cover D) are expected to carry R1. This is recorded, not tuned. We do NOT impose a ">= 3-of-4-properties must cost persistence" gate -- that would contradict the source's D-centric design. INSTEAD, a per-property persistence-cost DIAGNOSTIC is pre-registered: corrupt f_A (f0), f_B (f1), f_C (f2,f3), f_D (f4) SEPARATELY and record each property's persistence cost, quantifying how D-CONCENTRATED the persistence signal is. CONSEQUENCE recorded honestly: D1 R1's INDEPENDENT content BEYOND the coverage map is LIMITED BY DESIGN -- a D-centric perturbation test on a substrate whose D-coverage is already mapped largely re-expresses that map in a persistence costume. The LOAD-BEARING independent R1 evidence is carried by D2 (per-position substitution tolerance) and D3 (post-statement persistence terciles), where persistence is an EXOGENOUS substrate property, not a written one. D1 R1's role is CALIBRATION + the per-estimator functional-validity unit, consistent with D1's reframed role as coverage-calibration. This keeps R1 honest without fighting the substrate.

**4 -- spec guard + verdict-stability (LOAD-BEARING).** The R1 verdict is the per-(K,A) Cohen's d -- each cell's OWN `w`-median split is a clean per-estimator "does THIS `w` predict persistence" fork -- aggregated as MEDIAN-d + PASS-COUNT across the 15 cells (5 K x 3 A) on the PRIMARY measure `tau_rec`. There is EXPLICITLY NO cross-estimator `w`-agreement anywhere in the R1 verdict. R1 escapes R2's coverage ceiling NOT by being coverage-free (each estimator's R1 is STILL coverage-limited -- K1 cannot weight D, so its persistence prediction misses D-driven persistence, recorded per-estimator) but by NOT REQUIRING cross-estimator AGREEMENT. Operationalizing R1 as cross-estimator prediction-agreement would rebuild R2 in a functional costume; this entry forbids it. (This instantiates the 2026-06-24 reframe R1 spec guard for D1.)

**Verdict-stability across the two NEUTRAL measures (a robustness discipline, NOT a second threshold).** Both `tau_rec` and true-HSMM `h_pred` are computed per cell. The R1 call requires the two to AGREE on the per-cell PASS/FAIL QUALITATIVE VERDICT -- NOT that both clear `d > 0.5` (threshold-concordance on two readouts of the SAME construct is too strict and power-costly). A cell where the two neutral measures give the same R1 call is FIRM; a cell where they DISAGREE is flagged FRAGILE; WIDESPREAD disagreement across the 15 cells -> the D1 R1 verdict is INCONCLUSIVE. This is the robustness analog of the decoupling control's co-primary discipline, CALIBRATED for the fact that `tau_rec` and true-HSMM `h_pred` measure the SAME persistence (so agreement-on-verdict, not joint-threshold-clearance, is the correct concordance). The contaminated K3 `h_pred` (Step 2) is NOT part of this stability check -- it is the once-reported demonstration-diagnostic only.

**5 -- build decisions LOCKED here (design values; no code).**

- `PERTURB_ALPHA = 0.3` (convex-mix magnitude with uniform; "small" per Sec 5.5, matched to the `T_NOISE = 0.3` convention), subject to an in-build NON-SATURATION CALIBRATION GATE: the perturbation must produce a MEASURABLE, NON-SATURATING `tau_rec` cost (neither floor nor ceiling) on the coherence-bearing features; if it does not, `PERTURB_ALPHA` is re-calibrated and the change recorded as a dated erratum (the K4 / v0.6.0 in-build-verification discipline). The per-property cost diagnostic (Step 3) runs in the SAME calibration pass.
- `PERTURB_ONSET = 25000` (T // 2, T = 50000): a long pre-window for the unperturbed baseline and a long post-window for recovery. One feature corrupted at a time, all 8 features.
- Viterbi decoder = the TRUE HSMM generator's Viterbi; agreement threshold proposed at `>= 0.9` per-step sustained regime-label agreement, CALIBRATED in-build (any change recorded as an erratum).
- New locked constants (NONE edits a prior lock's VALUE -- all NEW for the R1 slice): `PERTURB_ALPHA = 0.3`, `PERTURB_ONSET = 25000`, `PERTURB_SEED = 0` (perturbed-emission RNG), `R1_BOOTSTRAP_SEED = 0` (the B=1000 bootstrap over the 20 replicate seeds). The K3 baseline (now the TERTIARY demonstration-diagnostic only, NOT the verdict) carries the existing `NEURAL_SEED = 7`. Pass thresholds (`d > 0.5` / CI `> 0.3` / `p < 0.01`) and `B = 1000` are SOURCE-locked (Sec 8.7), already on record.
- Multiple comparisons: report per-cell d / CI / raw-p at the slice; the program-level Bonferroni (across the full K x A x Domain x condition family) is DEFERRED to the capstone (family size not yet fixed). The slice verdict uses UNADJUSTED `d > 0.5` / CI `> 0.3` / `p < 0.01`, marked PROVISIONAL.
- Efficiency (recorded): BOTH neutral measures are ESTIMATOR-AGNOSTIC (`tau_rec` and true-HSMM `h_pred` depend only on substrate + perturbation + the fixed true generator, NOT on any K or A) -> compute the persistence table `(tau_rec, h_pred_trueHSMM)[feature, seed]` ONCE (8 features x 20 seeds), then re-partition per (K,A) cell by that cell's median `w`. The 15 cells reuse one persistence table. The contaminated K3 `h_pred` demonstration-diagnostic is computed ONCE for K3's own cell only.
- Recorded limitation (TRANSCRIBE, do not change): the median-split Cohen's d operates on only 8 features (a coarse 4-vs-4 split per cell); a single mis-ranked feature swings d. The statistical power is carried by the 20-seed bootstrap and the continuous true-HSMM `h_pred`, NOT the feature count. The source LOCKS the statistic; the granularity is flagged so per-cell d-values are not over-read.
- Module placement (PLANNED, not built): `cit/persistence_d1.py` (perturbation + the two neutral measures `tau_rec` and true-HSMM `h_pred`, plus the K3 `h_pred` demonstration-diagnostic) + R1 helpers in `cit/metacoherence.py` (alongside R2); driver `scripts/run_r1_persistence.py`; tests `tests/test_r1_persistence.py`.
- Scope: v0.7.1 = D1 R1 ONLY. D2 R1 (Spearman of aggregated `w` vs inverse mutation tolerance) and D3 R1 (JS divergence over persistence terciles) are deferred to those domains' builds.

**Discipline.** Design only -- NO code written, NO run, NO grid re-run in this entry. NO locked constant VALUE in ANY prior lock was edited (`beta = 4.0`, all seeds, `R2 0.6` / CI `0.4`, the decoupling `18/20` + bands, the D1 generator params -- untouched); the new constants above are ADDITIVE for the R1 slice. The deviation from the source -- `tau_rec` PRIMARY, true-HSMM `h_pred` ADOPTED as the co-reported neutral robustness check (Benjamin's 2026-06-24 ruling), and the contaminated K3 `h_pred` RETIRED from the verdict (kept once as a demonstration-diagnostic) -- is recorded as the K3 self-reference erratum (Step 2), SCOPED to D1's full-transparency tier (does NOT transfer to D2/D3 per Sec 2.2's domain-varying-measure clause), not a silent global change.

### 2026-06-24 -- v0.7.1 R1 build-time amendment: D1 substrate lacks the Sec 5.4 drift->transition coupling -> h_pred PRIMARY (regime decoder deferred), D1 R1 = instrument-calibration

**What this is.** A read-only re-read of the LOCKED D1 generator (`cit/data/hsmm_d1.py`) during R1 build-prep surfaced a PREMISE-LEVEL structural finding that OUTRANKS the two implementation blockers found in recon (the missing generator perturbation-hook; the missing regime decoder) and REVISES the just-locked decoder decision. Pre-registered honestly per the structural-findings rule (pre-register honestly rather than silently adjusting), BEFORE any code. The finding was VERIFIED read-only (generator line numbers below), not taken on faith. No code written; the locked generator UNCHANGED; nothing in the prior R1 lock silently edited -- this entry SUPERSEDES-IN-STATUS the relevant parts of the 2026-06-24 v0.7.1 R1 entry (tau_rec-as-PRIMARY, the regime-decoder build, and the two-neutral-measure verdict-stability form on D1), exactly as the 2026-06-24 reframe superseded R2's status (append-only, never a silent edit to a prior lock).

**Finding (VERIFIED, read-only).** The locked D1 substrate does NOT implement the Metacoherence Sec 5.4 "drift-persistence coupling" in the sense the source's R1 needs (drift correlating with regime TRANSITION probability):
- The regime path is produced by `_sojourn_states(rng, T)` (lines 69-80) as PURE negative-binomial dwells (`d = int(rng.negative_binomial(NB_R, p)) + 1`, line 76) with EMISSION-INDEPENDENT transitions (`s = (s + 1 + int(rng.integers(N_STATES - 1))) % N_STATES`, line 79). Both transition draws consume ONLY `rng` -- no `obs`/`drift`/emission input.
- `states` is fixed at line 102, BEFORE the emission loop (lines 107-122). `drift` is initialized at line 105 (AFTER states), reset to 0 at each regime ENTRY (`states[ti] != states[ti-1]`, lines 109-110), random-walks (line 111), and feeds ONLY f4's emission mode (lines 117-119). `drift` NEVER appears in `_sojourn_states` and NEVER feeds back into the regime path.
- CONSEQUENCE: in the locked substrate D (f4) is a ONE-WAY regime->drift->emission CARRIER (the regime resets the drift; the drift shapes f4's emission); there is NO drift->transition coupling. The Sec 5.4 "D is the R1 signal" mechanism (drift correlating with regime persistence/transition) is NOT instantiated here. No coupling path was found.

**(i) Substrate/source mismatch -- DO NOT fix the substrate.** The locked D1 generator lacks the Sec 5.4 drift->transition coupling (transitions emission-independent at lines 76/79; drift post-hoc and downstream-only at lines 105/109-111/117-119). The substrate is LOCKED (v0.7.0): changing it would break bit-exactness with ALL prior D1 results -- the R2 grid, the decoupling control (`90a3211` pre-reg / `d840553` result, 20 seeds), the coverage map -- for NO gain, given D1's reframed role as coverage-calibration. The mismatch is RECORDED, not repaired (the project's posture for source/implementation gaps: cf. the Sec 6 fixture erratum, the Thm 5.1 repair; record, do not silently retrofit a locked artifact).

**(ii) D1 R1 reframed -- INSTRUMENT-CALIBRATION + an A-dominated near-trivial result.** Because perturbing a feature's emission CANNOT change the (emission-independent) regime path, D1 "persistence" is REGIME-INFERENCE STABILITY under perturbation, NOT D-driven regime survival. That signal is A-DOMINATED: f0 (F0_SCALE=1.7 regime-conditional categorical, lines 96/112) is the strong DIRECT regime cue; f4 (D drift) a weak secondary cue (drift random-walks within a regime, so mid-sojourn f4 weakly indicates which regime); C (f2,f3) coalition-gated; distractors carry none. Since A is the coverage map's universal survivor, D1 R1 is EXPECTED to yield a near-trivial UNIVERSAL pass driven by A-detection -> LIMITED independent content; it substantially RE-MEASURES the coverage map (the per-property diagnostic, kept, quantifies how A-concentrated it actually is). So D1 R1 is reframed (mirroring the R2 D1-as-calibration reframe already on record): BUILD + VALIDATE the R1 apparatus against full-transparency ground truth on D1; a D1 R1 pass is NECESSARY-NOT-SUFFICIENT (A-driven, anticipated by coverage). The LOAD-BEARING R1 evidence is D2 (per-position substitution tolerance) and D3 (post-statement persistence terciles), which have REAL persistence mechanisms per Sec 2.2's domain-varying measure.

**(iii) Decoder decision REVISED -- h_pred PRIMARY (decoder-free); the regime decoder DEFERRED.** This SUPERSEDES the 2026-06-24 R1 entry's "`tau_rec` PRIMARY / decoder = the true generator's Viterbi" (recon confirmed: NO Viterbi exists in the repo, and the true model is HSMM not HMM, so the assumed decoder would have to be BUILT and would face an explicit-duration modeling choice). The PRIMARY D1 R1 measure is now the DECODER-FREE true-model predictive horizon `h_pred`: the per-step log-likelihood of the (generatively perturbed) observations under the EXPOSED true regime path (`states`, already returned by the generator) + the known per-state emission distributions (F0 for f0; the drift-mode p4 for f4; the deterministic mask for f3; F6/F7 for the distractors). Continuous, estimator-neutral, NO regime decoder needed -- this DISSOLVES the `tau_rec` decoder blocker for D1. The explicit-duration / true-HSMM regime decoder (recon options B1/B3) is DEFERRED until a domain demonstrably needs a regime DECODE (the opaque domains D2/D3); it is NOT built for D1's near-trivial result. The contaminated K3 `h_pred` stays a ONE-SHOT demonstration-diagnostic only (prior entry Step 2, unchanged).

**Consequence for the verdict-stability rule (D1).** The prior R1 entry's verdict-stability discipline required TWO neutral measures (`tau_rec` + true-HSMM `h_pred`) to agree on each cell's pass/fail. With the decoder DEFERRED, D1 has ONE neutral measure (`h_pred`), so the two-neutral-measure cross-check is NOT AVAILABLE on D1 (recorded); it RETURNS at D2/D3 (or whenever a second neutral measure / the regime decoder is built). On D1 the verdict rests on the single neutral `h_pred` -- acceptable precisely BECAUSE D1 R1 is reframed to instrument-calibration / necessary-not-sufficient (ii). Supersedes-in-status the prior entry's Step-4 verdict-stability paragraph FOR D1 ONLY (it stands unchanged for any domain that has two neutral measures).

**(iii-A) Measure refinement -- SUSTAINED LIKELIHOOD-COST MAGNITUDE, not a recovery horizon** (supersedes the "predictive horizon" wording in (iii) FOR D1; documented deviation, same family as the coupling-absence finding). The source's `h_pred` ("steps the perturbed log-likelihood stays within a band of unperturbed") is a RECOVERY measure presuming the perturbation disrupts then re-stabilizes. That presumption IS the absent drift->transition coupling: the regime is emission-independent and FIXED, so nothing "recovers" -- sustained single-feature corruption never returns to band (horizon ~ 0 for every feature -> no discrimination), and a transient-window variant merely recovers the window length (uninformative). So D1 substitutes the well-defined MAGNITUDE form:

      persistence_cost(f, seed) = mean over t in [PERTURB_ONSET, T] of
          ( logL_true(obs_unperturbed_t) - logL_true(obs_perturbed_f_t) )

where `logL_true` is the per-step log-likelihood of the observations under the EXPOSED true regime path + the known per-step emission distributions. Decoder-free, continuous, estimator-neutral. The recovery-horizon framing RETURNS at D2/D3, where persistence is a real substrate mechanism. Unchanged: `d > 0.5` / CI `> 0.3` / `p < 0.01`, the median-`w` split, `B = 1000` over the 20 seeds, the spec guard -- only the persistence OUTCOME is the magnitude, not a horizon. Validation-gate ordering (the calibration deliverable): on a clean unperturbed stream the magnitude cost must order f0 (A) LARGEST and the distractors f5/f6/f7 at ~0; a gate failure is a HARD STOP (the likelihood computation -- almost certainly the f4 per-step reconstruction -- is wrong), NOT a tuning prompt.

**(iv) A1 confirmed -- generative substrate perturbation, RNG-preserving.** Faithful R1 needs a GENERATIVE substrate perturbation (`generate_perturbed_stream(seed, feature, alpha, onset, T)` -- ADDITIVE, in `cit/persistence_d1.py`, NOT in the locked generator), NOT post-hoc symbol replacement (which is R3's STRUCTURE-PRESERVING interpretive intervention; conflating them collapses the R1/R3 distinction -- Sec 2.2 "perturbation of the substrate, not of the symbol"). The locked `generate_stream` stays BIT-IDENTICAL. Constraint: perturb ONLY feature f's emission distribution (convex-uniform mix from onset) such that the RNG draws consumed for `states` and all NON-target features are PRESERVED -> `states` and every non-target feature stay bit-identical to the unperturbed stream (clean per-feature attribution; the perturbation is the convex-uniform CORRUPTION of f's channel, distinct from R3's relabel). Per-feature perturbation map (the gap, specified before coding; ALL realized RNG-preservingly via a dedicated perturbation rng applied post-onset to feature f's column only, so the base stream's `states` and every non-target feature stay bit-identical):
  - f0 (A): convex-uniform mix of F0[s].
  - f4 (D): convex-uniform mix of the PER-STEP drift-mode p4 (per-step, not per-state -- see the emission-distribution note below).
  - f6 (Zipf), f7 (low-freq): convex-uniform mix of their fixed marginals.
  - f1 (B), f3 (C): OUTPUT-MIX -- replace with a uniform draw w.p. alpha from onset. f1 is itself a g-table-or-uniform mixture; f3 is DETERMINISTIC (`= (f2 + C_VAL[s,bucket]) mod A`, line 116) so it has NO sampled emission to convex-mix. The C coalition is probed via f3 (perturbing f2 alone is a null, below).
  - f2 (C, uniform marginal), f5 (uniform distractor): DOCUMENTED NULL -- already uniform, so mix-with-uniform is a no-op.
  The output-mix (replace-with-UNIFORM) is structure-DEGRADING corruption (R1), distinct from R3's structure-PRESERVING relabel/permutation: the R1/R3 line is degrade-vs-preserve realized RNG-preservingly, NOT post-hoc-vs-generative. The documented nulls (f2, f5) and ~0-cost distractors (f6, f7) are CORRECT behavior and feed the per-property diagnostic as confirmation of A-dominance.

**Emission-distribution access (no generator change) -- PER-STEP, not per-state.** `logL_true` needs the true PER-STEP emission distributions. f4 (D) is the load-bearing case: its emission mode follows the drifting random walk (generator lines 117-119), so its per-step distribution p4 is PER-STEP and a static per-state table is INSUFFICIENT -- the likelihood MUST reconstruct the per-step drift trajectory. Chosen mechanism (recorded): an ADDITIVE SIBLING GENERATOR in `cit/persistence_d1.py` that re-runs the generation loop and RETURNS the per-step per-feature emission distributions (F0[s]; the per-step p4; the deterministic f3 value; F6 / F7; the uniforms), WITHOUT touching the locked `generate_stream`. PREFERRED over RNG-replay re-derivation of static tables (the interleaved-RNG fragility the recon flagged, which would corrupt the D reconstruction specifically). EITHER mechanism is GATED by a bit-exact test: the sibling's reconstructed `obs` must equal `generate_stream(seed)`'s `obs` EXACTLY (guards the duplicated logic against drift).

**(v) Kept locked (unchanged from the 2026-06-24 R1 entry):** `PERTURB_ALPHA = 0.3` (+ the in-build non-saturation calibration gate), `PERTURB_ONSET = 25000`, per-cell Cohen's d on the median-`w` high/low feature split, pass `d > 0.5 / CI > 0.3 / p < 0.01`, `B = 1000` bootstrap over the 20 seeds (App C.3 `bootstrap_replicate_streams`), the coarse-4v4 granularity caveat, the per-property persistence-cost DIAGNOSTIC (now EXPECTED to confirm A-dominance), the spec guard (per-estimator validity aggregated, NEVER cross-estimator agreement), `PERTURB_SEED = 0`, `R1_BOOTSTRAP_SEED = 0` (deterministic). NO locked constant VALUE changed by this entry.

**Discipline.** Read-only verification (generator line numbers cited) -> this dated build-time amendment -> (on Benjamin's ruling) a LEAN build. The locked generator is UNCHANGED and stays bit-identical; no prior lock silently edited (this entry supersedes-in-status the prior R1 entry's tau_rec-primary / decoder-build / D1-verdict-stability, append-only). Build is GATED on Benjamin's ruling on the reframe + h_pred-primary / decoder-deferral.

### 2026-06-24 -- v0.7.1 R1 calibration finding: D1 cost ordering is D-LED (not A-dominated), disambiguated at 20 seeds; the magnitude measure is information-sensitive AND concentration-weighted

**What this is.** The v0.7.1 R1 module (`cit/persistence_d1.py`, built; 11 tests green; UNCOMMITTED pending this record) was run as the D1 instrument-CALIBRATION it is reframed to be. The validation gate PASSED -- distractors ~0 (the marginal-relative computation correctly refuses the skewed Zipf/low-freq marginals) and the relational B / coalitional C are per-feature-invisible by design (recoverable only by joint proxies, matching the coverage map) -- so the likelihood computation, INCLUDING the f4 per-step drift reconstruction, is VALIDATED. The per-feature cost ORDERING, however, is D-LED, not A-dominated as the build-time amendment (ii) anticipated. This entry records the corrected ordering WITH its cause, disambiguated by a PRE-REGISTERED seed-variability diagnostic (pre-committed reads fixed before the numbers; read-only; no proxy grid, no Cohen's d, no constant changed).

**The finding (20 locked seeds, T=50000, the estimator-agnostic cost table).** Per-feature mean persistence cost: f4 (D) ~ 1.72, f0 (A) ~ 0.28, every other feature (B, C, the three distractors) ~ 0. D leads A on 20/20 seeds; mean ratio D/A ~ 6.7 (median 6.1). [A 4-seed preview read ~5x; the 20-seed table is the authority.]

**Disambiguation (pre-registered diagnostic, reads fixed BEFORE computing).** Is the D-lead a measure property or an artifact of A's seed-variability?
- (a) `Spearman(A_cost, I_A)` across the 20 seeds = **+0.835** (Pearson +0.921). A's cost STRONGLY tracks its seed-variable information -> the measure IS information-sensitive (within a property). A_cost is itself seed-variable (mean 0.28 +/- 0.08, range [0.11, 0.48]), tracking I_A (mean 0.56 +/- 0.18, range [0.21, 0.99]).
- (b) D-cost is STABLE: mean 1.72 +/- 0.054 (CV 0.031), matching I_D's stability (`I_D = 0.58 +/- 0.03`).
- (c) D > A on **20/20** seeds; ratio ~6.7. The pre-registered disconfirmer for "D robustly leads" (D>A on `< 15/20`, or ratio `-> ~1`) is NOT triggered. The 4-seed preview seeds (7000-7003) had mean I_A 0.61, ABOVE the ensemble mean -- so the preview lead was NOT a low-A draw.
- Classification (no softening): **MIXED**. The measure is information-sensitive WITHIN a property (A-cost ~ I_A, rho +0.84), AND D robustly leads A across ALL seeds. Because `I_A ~ I_D` (0.56 vs 0.58, near-equal) yet D costs ~6.7x more, the D-over-A gap is NEITHER an information difference NOR seed-sampling -- it is the measure's CONCENTRATION-weighting: uniformizing D's sharply-peaked per-step drift emission drops the true-model likelihood far more than uniformizing A's moderately-peaked `F0[s]`. Both effects are real; this entry does NOT assert "peakedness not information."

**Record corrections.**
- "A-dominated" (the build-time amendment (ii)) is CORRECTED to: D-LED, with A second and B/C/distractors ~0. The regime-informative features that survive a per-feature measure are A (direct regime cue) and D (drift), D leading by ~6.7x at locked T.
- A's persistence cost is INTRINSICALLY SEED-VARIABLE (F0-draw-coupled; `I_A in [0.21, 0.99]`, A_cost in [0.11, 0.48], correlated rho +0.84); D's is stable. A 4-seed readout CANNOT establish the ordering -- the 20-seed table does (and confirms D-led 20/20).

**STANDING instrument property (park for D2/D3, NOT now).** The magnitude measure is mechanically CONCENTRATION-SENSITIVE: for equal information, uniformizing a sharper conditional emission drops likelihood more. This is an instrument-faithfulness property to RESOLVE BEFORE D2/D3, where R1 is LOAD-BEARING -- via either the domain's own persistence operationalization (Sec 2.2 varies the measure by domain: per-position substitution tolerance in D2, post-statement persistence terciles in D3) or an information-normalized cost. SHARPENED (Benjamin, 2026-06-24): the cross-property confound bites ONLY when a domain's features have HETEROGENEOUS emission concentration (the diagnostic showed information-sensitivity WITHIN a fixed emission shape; the cross-property bias is the CONCENTRATION spread). So the D2/D3 resolution is NOT unconditional info-normalization but a CONDITIONAL: FIRST check emission-concentration HOMOGENEITY across the domain's features; if comparable, the measure is fine AS-IS; if heterogeneous, normalize. Pre-register this homogeneity check before trusting the measure on D2/D3. Recorded as a D2/D3 dependency; deliberately NOT changed for D1's calibration role.

**Kept / confirmed.**
- The validation gate stands AS BUILT (PASSED: distractors ~0; B/C per-feature-invisible by design = instrument validated). The D-vs-A magnitude is a MEASURE property, NOT a correctness failure; the gate hard-asserts distractors-~0 + A-above-distractors, and reports `A_is_largest` as a field (False here, by the D-lead).
- f1 (B) / f3 (C) are recorded as PER-STATE-UNIFORM (condition on own latents, marginalize cross-feature relations) -- the principled per-feature choice, and WHY B/C read ~0 (per-feature-invisible relation/coalition). Confirmed.
- Grid prediction is CONDITIONAL (the proxy grid is NOT run this turn): GIVEN D robustly leads (now confirmed 20/20), K1 -- which misses D and places f4 in its LOW-w group -- is EXPECTED attenuated / negative Cohen's d; K2/K3/K4/K5 (cover D) positive. To be MEASURED by the proxy grid (15 cells x 20 seeds), the separately-gated next step; the 20-seed cost table computed here is its estimator-agnostic foundation (saved to `results/r1_persistence/cost_table_T50000.json`, reused).
- D1 R1: CALIBRATION / necessary-not-sufficient / coverage-anticipated AND MECHANISM-CONFOUNDED. On D1, D (f4) is BOTH the sharpest-emission feature AND the source's persistence-DESIGNATED property (Sec 5.4) -- confounded-but-ALIGNED. So K2-K5 passing R1 on D1 confirms only that they weight the SHARP feature D, which here COINCIDES with the designated persistence feature but for the WRONG reason (concentration, NOT the absent drift->transition coupling). A clean D1 R1 pass therefore validates the APPARATUS and confirms COVERAGE; it does NOT validate that w tracks persistence-RELEVANCE. The load-bearing R1 is D2/D3, where the concentration-homogeneity check (above) must be resolved first.

**Discipline.** Read-only diagnostic computed from the locked generator (NO proxies, NO grid, NO Cohen's d). Pre-committed reads fixed before the numbers; the disconfirmer was set in advance and not triggered. No locked constant VALUE changed. The module `cit/persistence_d1.py` stays UNCOMMITTED pending Benjamin's confirm. Append-only, ASCII.

### 2026-06-24 -- v0.7.1 R1 CLOSER: partial proxy d-matrix confirms the mechanism-confound (K1 FAILS, K2 PASSES); K3/K4/K5 + A2 deferred (predictable, confounded, slow)

**What this is.** The D1 R1 closer: the proxy grid (induce `w` -> per-(cell,seed) median-`w` split -> Cohen's d -> B=1000 bootstrap) run on the CHEAP cells to validate the full pipeline end-to-end and confirm the coverage pattern, REUSING the estimator-agnostic cost table (`results/r1_persistence/cost_table_T50000.json`). Calibration-only, partial-by-design.

**Scope decision (timing-justified, Benjamin 2026-06-24: run the cheap cells, do NOT spend the very_slow tier).** Timing probe at locked T=50000 (per cell, x20 seeds): K1/K2 x {A1,A3} ~1.8 min each; K1/K2 x A2 ~10-12 min each; K4 x A1 ~99 min and K4 x A3 ~100 min; K3/K5 (GRU / LZ76 under LOO) worse still. So "A1/A3 x all K" at full scale is a NIGHT. The cheap grid is therefore K1, K2 x {A1, A3} (~7 min total) -- a D-MISSER (K1, covers {A,C}) and a D-COVERER (K2, covers {A,D}), the crux contrast. K3/K4/K5 (all cover D -> predicted to pass like K2) and the A2-Shapley cells are DEFERRED: predictable from the coverage map, mechanism-confounded, and slow (the very_slow A2 x K3/K5 is the ~20h artifact, explicitly NOT spent to confirm an already-known confounded pattern).

**Result (partial d-matrix, 20 seeds, T=50000; saved `results/r1_persistence/d_matrix_cheap.json`):**

      K1xA1   d = -0.386   ci95_lo = -0.485   p = 1.000   FAIL   (D=f4 in high-w on 0/20 seeds)
      K1xA3   d = -0.386   ci95_lo = -0.486   p = 1.000   FAIL   (0/20)
      K2xA1   d = +0.986   ci95_lo = +0.965   p = 0.000   PASS   (D=f4 in high-w on 20/20 seeds)
      K2xA3   d = +0.986   ci95_lo = +0.965   p = 0.000   PASS   (20/20)

A1 == A3 exactly (the recorded `A3 == A1` on D1: Pearson finds only singletons).

**Reading.** The pipeline is VALIDATED end-to-end (induce -> split -> Cohen's d -> bootstrap -> verdict). The result is the MECHANISM-CONFOUND made concrete: K2 PASSES purely because it ranks the sharp feature D (f4, ~all the persistence cost) in its high-`w` half on 20/20 seeds; K1 FAILS (in fact NEGATIVE d) because it MISSES D and puts f4 in its low-`w` half on 0/20 seeds. So "passing R1 on D1" == "weighting the sharp feature D high," which COINCIDES with the persistence-designated feature but for the CONCENTRATION reason, NOT persistence-relevance (the drift->transition coupling is absent). K3/K4/K5 cover D -> predicted to pass like K2. This CONFIRMS, at the d-matrix level, the necessary-not-sufficient + mechanism-confounded verdict; by design it adds NO independent evidence.

**D1 R1 status: CLOSED as calibration.** Apparatus built + validated against full-transparency ground truth (`cit/persistence_d1.py`, committed `95d85ff`); cost ordering disambiguated (D-led, 20/20); mechanism-confound exposed + recorded; partial d-matrix confirms the coverage pattern. The load-bearing R1 is D2/D3 (the concentration-homogeneity check above is pre-registered FIRST). No locked constant changed; A2 + K3/K4/K5 deferred (not pre-judged beyond the coverage prediction). NEXT: D2 (Pfam) pre-registration with the homogeneity check.

### 2026-06-24 -- v0.7.x D2 (Pfam) R1 pre-registration: substrate, substitution-tolerance persistence-op (ML per-site rate, LOCKED), and the conservation-tautology confound check (entropy-baseline contrast, LOCKED) [entropy margin + family count flagged for Benjamin's number]

**What this is.** Pre-registers R1 (persistence prediction) for D2 (Pfam protein families, CC0) -- the LOAD-BEARING R1 domain under the v0.7 reframe (R1 = PRIMARY cross-domain test). DESIGN + DOCS only: NO D2 code, NO data fetch, NO run. Transcribes Meta-coherence.docx Sec 6 where it locks. The two choices the source left open -- the phylogenetic-correction METHOD (c) and the CONFOUND-CONTROL FORM (d) -- are now LOCKED per Benjamin's 2026-06-24 ruling (below). TWO numeric items remain FLAGGED for Benjamin's number / the D2 data-survey, NOT picked unilaterally: the (d) ENTROPY-BASELINE MARGIN and the (a) FAMILY COUNT + stratification commit list (data-availability-dependent). D3 (FOMC) and R3 are separate steps; R2 is the diagnostic (carried, not load-bearing). The D2-specific addition beyond transcription is the CONSERVATION-TAUTOLOGY confound check (d), the correct analog of D1's marginal-relative lock, pre-registered FIRST -- before R1 on D2 is trusted.

**(a) Substrate + selection (Sec 6.1).** 20-30 Pfam families, EXACT COUNT fixed at pre-registration, NO post-hoc adjustment. Stratified EQUALLY across four axes (none dominates):
  1. ORTHOLOG DEPTH: each family `>= 500` sequences AFTER 90%-sequence-identity redundancy filtering (below it, position-wise tolerance is noise-dominated and 6.3 loses traction); BOTH 500-1500 and 1500+ ortholog families sampled.
  2. STRUCTURAL CLASS: all-alpha, all-beta, alpha/beta, alpha+beta folds in ~EQUAL counts, from CATH or SCOP at pre-reg time.
  3. FUNCTIONAL CLASS: enzymatic, structural, regulatory, signaling, from Gene Ontology at pre-reg time.
  4. CATALYTIC COVERAGE: ~HALF enzymatic with documented catalytic residues (UniProt / PDB); the other half non-enzymatic functional sites (substrate-binding pockets, interfaces, regulatory sites) -- so the M5 partition is not over-fit to one structural role.
  The family list + class assignments + catalytic annotations are COMMITTED at pre-registration; NO post-hoc addition; removal ONLY under pre-registered exclusion criteria (to be specified at lock: alignment-quality / coverage floors). FLAGGED (Benjamin's number / deferral to the D2 data-survey, NOT picked unilaterally): the EXACT family count within 20-30 and the concrete stratification commit list (the specific families + their 4-axis class assignments) are DATA-AVAILABILITY-DEPENDENT -- they are locked at the data-survey step (the next gated step), not here.

**(b) Stream construction (Sec 6.2).** MSAs from the active Pfam release -> standard MSA QC -> POSITION-BY-ORTHOLOG matrices over the 21-letter alphabet (20 amino acids + gap), after low-coverage column trimming. CRITICAL: the grid index is ORTHOLOG, NOT TIME (no temporal / sojourn structure; the R1 bootstrap resamples ORTHOLOGS, not time-windows -- per Sec 6.3 / App C.3). The categorical 5x3 grid (K1-K5 x A1-A3) runs UNMODIFIED on these matrices (the proxies are alphabet-agnostic over the 21 letters).

**(c) R1 measure (Sec 6.3) -- REPLACES the D1 magnitude measure; phylo-correction LOCKED.** Per-position MUTATION TOLERANCE = observed substitution frequency across the ortholog set AFTER PHYLOGENETIC CORRECTION (correcting non-independence from shared ancestry). The R1 statistic PER FAMILY = Spearman(induced `w`, INVERSE mutation tolerance); bootstrap CIs by ORTHOLOG RESAMPLING; the R1 pass requires the CROSS-FAMILY AGGREGATE to clear the Sec 8 threshold under multiple-comparison adjustment. This is an EMPIRICAL, substitution-counting measure -- NOT likelihood-based, NOT the D1 `h_pred`-magnitude -- so the D1 CONCENTRATION CONFOUND does NOT carry to D2 (a different measure entirely; the D2 confound is a DIFFERENT one, (d) below).
  LOCKED (Benjamin 2026-06-24): phylogenetic correction = ML PER-SITE RATE (Rate4Site-style), the CONTINUOUS per-site rate form -- NOT integer counts of reconstructed substitutions (integer counts TIE heavily and degrade the Spearman; the continuous rate preserves rank resolution). Independent-contrasts is REJECTED (a continuous-TRAIT method -- a category mismatch for per-site discrete substitution rates).
  DETERMINISM DISCIPLINE -- a deliberate, recorded DEPARTURE scoped to D2/D3. D2 CANNOT be bit-exact: the MSA, the tree inference, and the rate estimation are EXTERNAL tools. D2 REPLACES D1's bit-exact standard with SOFTWARE-PINNED reproducibility. Pre-register (at the D2 lock / data-survey): the exact MSA source + Pfam release, the tree-inference method, the rate-estimation tool, ALL versions, and ALL parameters; the per-family TREE is a PINNED INPUT. This is a RECORDED scope change from the D1 bit-exact discipline (the same care that flagged x86<->arm64 parity), legitimate because D2/D3 are EMPIRICAL domains with external-tool pipelines, not written generators -- and it is SCOPED to D2/D3 (D1 / the v0.6 program remain bit-exact).

**(d) THE CONSERVATION-TAUTOLOGY CONFOUND CHECK (pre-registered FIRST; the load-bearing D2 falsification control; RESTRUCTURED + LOCKED).** Inverse substitution tolerance is near-IDENTICAL to column CONSERVATION / low column ENTROPY. A compression proxy's induced `w` may track column entropy DEFINITIONALLY (low-entropy columns compress better) -- so a high Spearman(`w`, inverse-tolerance) risks reducing R1 to "does `w` detect low-entropy columns," a NEAR-TAUTOLOGY, rather than testing functional-coherence PERSISTENCE. This is the D2 analog of D1's marginal-relative lock and the D1 concentration confound: a known mechanism by which R1 could read as a pass for the WRONG reason. LOCKED structure (Benjamin 2026-06-24):
  - PRIMARY = ENTROPY-BASELINE CONTRAST (the project's native baseline-relative idiom -- cf. marginal-relative coherence, the noise-only counterfactual, the `w=1` Shannon spine): for each (K,A) cell, test whether the proxy's Spearman(`w`, inverse-tolerance) EXCEEDS the Spearman of a PURE COLUMN-ENTROPY baseline `w` (raw column conservation = inverse column entropy) against inverse-tolerance, by a PRE-REGISTERED MARGIN. This directly operationalizes "is `w` MORE than a conservation detector." The MARGIN VALUE is PENDING Benjamin's number (flagged below) -- NOT picked unilaterally; candidate framing for his consideration: in the spirit of the project's other calibrated margins (`T_NOISE = 0.3`, `WIN_MARGIN = 0.20`, the decoupling `0.40 / 0.10` bands), a Spearman margin to be set by him.
  - CORROBORATING = CONSERVATION-STRATIFIED within-bin R1: bin positions by column entropy / conservation, compute R1 WITHIN each bin, aggregate across bins. Non-parametric, robust to nonlinearity in the confound.
  - DROPPED: partial Spearman (the weakest of the three; SUPERSEDED by the entropy-baseline contrast).
  - PRE-COMMITTED CONCORDANCE RULE: R1 is recorded as "SURVIVING the conservation confound" ONLY IF BOTH controls show survival above their thresholds (the entropy-baseline contrast clears the margin AND the stratified within-bin R1 clears its threshold). If they DISAGREE, the outcome is CONFOUND-AMBIGUOUS -- a NAMED outcome, recorded as such, NOT post-hoc adjudicated.
  - DISCONFIRMER (unchanged): if R1 COLLAPSES toward the entropy baseline once conservation is controlled (Spearman not exceeding the baseline by the margin, and/or within-bin R1 ~0 across bins), then D2 R1 is recorded as CONSERVATION-CONFOUNDED -- "compressors find conserved columns" -- NOT functional-persistence evidence. A surviving R1 AFTER the control is the genuine signal. This check is NOT optional and NOT skippable; it is the D2 equivalent of catching the D1 concentration bias before the measure is trusted.

**(e) Pfam = comparison compression, NOT adjudicator (Sec 4.4, 6.4) -- three DISTINCT uses of annotation.** Keep separate and state so:
  - M5 PARTITION = documented CATALYTIC / structural residues (UniProt / PDB / structural-biology literature) -- biology used for the feature-class partition ONLY.
  - R1 MEASURE = substitution TOLERANCE (the empirical substitution-counting of (c)) -- NOT Pfam conservation scores.
  - Pfam conservation scores = a PARALLEL COMPRESSION run through the framework's functional to a Pfam-derived `w`-equivalent, contributing ONE ADDITIONAL R2 instance (framework-vs-Pfam convergence). `w`-vs-Pfam DIVERGENCE is reported as an informative FINDING (apparatus sees structure Pfam misses, or vice versa, or partially-distinct aspects), NEVER as an induced-`w` failure. Pfam does NOT arbitrate (deference to incumbent symbolic authority is the corpus's named failure mode).

**(f) M5 partition (Sec 6.4) -- documented biology, fixed at pre-reg.** Coherence-bearing class = documented CATALYTIC residues (where applicable) + FOLD-DEFINING positions (load-bearing for fold integrity, structural-biology literature) + CONSERVED CORES (top conservation QUINTILE under a committed conservation-scoring method). Noise class = SURFACE-EXPOSED NON-FUNCTIONAL residues (solvent-accessible, no annotated functional role) + BOTTOM conservation QUINTILE. By documented biology; committed per family at pre-reg; not adjustable post-hoc. NOTE: the partition's conservation-quintile components are themselves conservation-based, so the (d) confound check ALSO informs the M5/partition reading (recorded).

**(g) Carried forward.** R1 SPEC GUARD (unchanged): functional convergence = PER-ESTIMATOR functional validity (each estimator's `w` predicts persistence -- a clean per-family Spearman) AGGREGATED, NEVER cross-estimator agreement on predictions. R1 stays the PRIMARY (load-bearing) cross-domain test on D2; R2 (framework-vs-framework + the Pfam instance) is the DIAGNOSTIC; R3 (Sec 6.5: structural = in-silico relaxed-selection rate increase; interpretive = BLOSUM-equivalence-class amino-acid relabeling) is DEFERRED to its own step. The D1 concentration confound does NOT transfer (different measure); the NEW D2 confound is conservation-tautology (d), pre-registered first.

**Discipline.** DESIGN + DOCS only -- NO D2 code, NO data fetch, NO run. Transcribed from Meta-coherence Sec 6; (c) ML PER-SITE RATE + (d) ENTROPY-BASELINE-CONTRAST structure are LOCKED per Benjamin's 2026-06-24 ruling. TWO numeric items remain FLAGGED for his number / the data-survey, NOT picked unilaterally: the (d) entropy-baseline MARGIN and the (a) FAMILY COUNT + stratification list -- to be locked BEFORE any D2 data work. The DETERMINISM DEPARTURE (software-pinned reproducibility, NOT bit-exact) is a RECORDED scope change for D2/D3 ONLY; no locked constant VALUE changed and D1 / the v0.6 program remain bit-exact. NEXT gated step = the D2 DATA SURVEY (no implementation started here). Append-only, ASCII.

### 2026-06-24 -- v0.7.x D2 grounding + resume note: D2 R1 rulings consolidated (open items flagged) + the adaptive-coherence corpus lineage (CIT's non-CIT ancestors; T1 tier-guard)

**What this is.** A GROUNDING + RESUME note appended ahead of a context compaction. It carries two things that the running context held but the repo does not: (A) a CONSOLIDATION of the D2 (Pfam) R1 rulings LOCKED this session -- already recorded substantively in the 2026-06-24 D2 pre-reg entry above, restated here as the compact resume anchor together with the OPEN items that still gate the D2 lock; and (B) the adaptive-coherence CORPUS CONTEXT for D2 -- the lineage from which CIT descends, transcribed from two source documents (NOT in this repo) so that D2's confound control (d) can be read as testing a load-bearing corpus claim, not merely a nuisance variable. No code, no data, no run. Append-only, ASCII. PART B is CORPUS CONTEXT (claims attributed to their source stratum and tier), NOT CIT results; the tier-guard (B4) fences those claims out of D2's interpretation.

#### PART A -- D2 (Pfam) R1 rulings locked this session (resume anchor; full text in the entry above)

- **(c) PERSISTENCE MEASURE = ML PER-SITE EVOLUTIONARY RATE (Rate4Site-style, CONTINUOUS).** A continuous per-site rate, NOT integer counts of reconstructed substitutions (integer counts TIE heavily and degrade the Spearman; the continuous rate preserves rank resolution). INDEPENDENT-CONTRASTS REJECTED (a continuous-trait-across-taxa method -- category mismatch for per-site discrete rates). DISCIPLINE SHIFT: D2 CANNOT be bit-exact (external MSA / tree-inference / rate tools), so D2 REPLACES D1's bit-exact standard with SOFTWARE-PINNED reproducibility -- commit the exact MSA source + Pfam release, the tree-inference method, the rate tool, ALL versions and parameters; the per-family tree is a PINNED INPUT. Scope this departure to D2/D3 (empirical domains); D1 / the v0.6 program stay bit-exact.
- **(d) CONSERVATION-TAUTOLOGY CONFOUND CONTROL (load-bearing).** Inverse substitution tolerance ~= column conservation ~= low column entropy ~= what a compression proxy's `w` may track DEFINITIONALLY. PRIMARY control = ENTROPY-BASELINE CONTRAST: does each proxy's Spearman(`w`, inverse-tolerance) EXCEED that of a pure column-entropy baseline "`w`" by a PRE-REGISTERED MARGIN (the project's native baseline-relative idiom -- cf. marginal-relative / noise-only / `w=1`). CORROBORATING = conservation-stratified within-bin R1. DROPPED: partial Spearman. PRE-COMMITTED CONCORDANCE RULE: R1 "survives the confound" ONLY IF BOTH controls survive; disagreement -> recorded CONFOUND-AMBIGUOUS (a NAMED outcome, NOT post-hoc adjudicated). DISCONFIRMER: R1 collapses toward the entropy baseline once conservation is controlled -> recorded CONSERVATION-CONFOUNDED ("compressors find conserved columns"), NOT functional-persistence evidence. Pfam stays COMPARISON-COMPRESSION, NOT adjudicator, in THREE distinct roles: M5 PARTITION = documented catalytic/structural residues (UniProt/PDB); R1 MEASURE = substitution tolerance; Pfam conservation scores = a PARALLEL compression contributing one EXTRA R2 instance.
- **OPEN, awaiting Benjamin (NOT picked unilaterally):** the (d) ENTROPY-BASELINE MARGIN value; the FAMILY COUNT (20-30) + the exact stratification commit list (data-survey-dependent); the phylo-correction SOFTWARE / VERSION pins. These lock at the D2 DATA SURVEY (the next gated step), BEFORE any D2 data work.

#### PART B -- adaptive-coherence grounding (transcribed corpus context; CIT's non-CIT lineage)

**Provenance + stratigraphy.** Two source documents in Benjamin's corpus, EARLIER strata than CIT: "Formal Foundations of Adaptive Coherence" (the formalization) and "Adaptive Coherence Theory" / ACT (the biology). The corpus vocabulary migrated: Neodynamics -> SPARC/UFAP -> ACT -> Recursive Coherence -> Coherence Engine -> CIT. These are ANCESTORS of CIT, NOT competitors; the latest formal stratum (CIT) governs WITHIN its scope. CROSS-STRATUM IDENTITIES: CIT's weight `w` == the parent's coherence weight `kappa`; CIT's `H_w` == the parent's `H_C`.

**B1. Coherence-weighted entropy OUTSIDE CIT** (verbatim formalism, "Formal Foundations of Adaptive Coherence" Sec 4):

      H_C = - sum_i kappa_i p_i log p_i      (Shannon at kappa_i = 1; kappa->0 noise, ->1 persistent)

  - Residual entropy floor (Sec 4.3): `H_C_min = kappa_max * H`, `kappa_max < 1` (nonzero floor).
  - Monotonic decay under dissipation (Sec 4.2): `E[d H_C/dt] <= -lambda_eff * H_C`.
  - Coherence rate-distortion (Sec 4.4): coherence-weighted distortion `D_C = sum_{x,xhat} p(x) kappa(x) d(x, xhat)`; rate `R(D_C) = min I_C(X;Y) s.t. E[D_C] <= D_C`; coherence channel capacity `C_C = max_{p(x)} I_C(X;Y)`.
  - => CIT's Capacity Theorem (`max_p I_w`, v0.6.0) and the v0.6.1 Selective Compression coder are the FALSIFIABLE INSTANTIATION of this pre-existing rate-distortion / capacity formalism.

**B2. The induction pipeline is the PARENT metric, not a CIT invention.** Parent coherence metric:

      C(s,t) = sigma(beta * R(s,t)) = 1 / (1 + e^{-beta R}),   bounded 0 < C < 1.

  - Empirical computability (Sec 2.6): `R ~= Delta_K - 1`, where `Delta_K = len(LZMA(s_{t-1})) - len(LZMA(s_t | s_{t-1}))` (compression-delta). => the repo's `w = sigma(beta * rho)` with `rho` from a compression / prediction proxy IS this.
  - Nested-system closure (Sec 2.3, weighted log-odds; preserves the sigmoid under composition): `C(S) = prod_i C_i^{w_i} / ( prod_i C_i^{w_i} + prod_i (1-C_i)^{w_i} )`, `sum_i w_i = 1`.
  - Viable band (Sec 2.4): `C_min < C < C_max` (below = noise / disintegration; above = rigidity / calcification).
  - Related applications in the same doc (CONTEXT, not used in D2): coherence-weighted training loss `L = -sum_i kappa_i yhat_i log y_i` (Sec 9.1); ethics as marginal coherence contribution `M(phi_i) = d C_sys / d phi_i` (Sec 9.6, an ablation form). The parent also formalizes quantum / time / logic / governance from the same metric -- breadth NOTED, not transcribed, NOT load-bearing for CIT / D2.

**B3. Biology (ACT) -- the D2-load-bearing connection.** ACT frames evolution as COHERENCE selection, not survival selection: systems persist iff they maintain recursive coherence. ACT Sec 1.1.1 "Circularity of Fitness Selection" argues survival-of-the-fittest is TAUTOLOGICAL -- fitness is defined post hoc; Neo-Darwinism is mechanistic for microevolution but (ACT CLAIMS) fails macroevolution / structural persistence. CONNECTION: the D2 conservation-tautology confound [PART A (d)] is the EMPIRICAL INSTANCE of ACT's fitness-tautology critique. ACT claims coherence is the NON-circular alternative; the entropy-baseline contrast directly TESTS whether induced-`w` escapes the conservation tautology that ACT accuses fitness-talk of. So the (d) control is testing a load-bearing CORPUS claim, not just a nuisance variable.

**B4. TIER-GUARD (recorded explicitly).** "Formal Foundations of Adaptive Coherence" and ACT are HIGH-CLAIM T2/T3 strata ("supersede energy / entropy / probability"; macroevolution as coherence bifurcation; convergent-evolution predictability). D2 STAYS at CIT's FALSIFIABLE T1 tier: R1 tests ONLY whether induced-`w` predicts substitution tolerance BEYOND raw conservation, per family, with bootstrap CI. A D2 R1 PASS does NOT validate ACT's macroevolution theses; do NOT import them into D2's interpretation. The B1/B2 formalisms are recorded as LINEAGE (what CIT instantiates), the B3 critique as the MOTIVATION the (d) control empirically tests; neither is asserted as established here.

**Discipline.** GROUNDING + RESUME note: NO code, NO data, NO run. PART A restates this session's locked D2 rulings (full text above) + the OPEN items that gate the lock; PART B transcribes the corpus lineage faithfully, each claim attributed to its source stratum and FENCED to T1 by the tier-guard. No prior lock edited; no constant changed. Append-only, ASCII. NEXT gated step UNCHANGED = the D2 DATA SURVEY (lock the family list + the entropy-baseline margin).

### 2026-06-24 -- v0.7.2 D2 (Pfam) PRE-REG REWORK: the conservation-tautology GATE (entropy-baseline control extended from R1 to M5), ortholog-ordering PIN, proxy/phylogeny-mismatch disambiguation, and family-selection RE-ORIENTATION [DESIGN ONLY; pre-family-lock; Benjamin-choice items flagged PENDING]

**What this is.** A dated, append-only amendment that REWORKS the D2 (Pfam) R1/M5 design BEFORE any family is locked, in response to a GATING adversarial finding from the data survey: D2 AS SURVEYED RISKS MEASURING CONSERVATION, NOT METACOHERENCE. DESIGN ONLY -- NO family selection, NO alignment fetch, NO induction/R1/R2/M5 run, NO data committed (`data/` stays gitignored; survey artifacts -- `candidate_pool.tsv`, `manifest.json`, `api_cache/` -- are local-only). Context on disk: InterPro-Version 109.0 pinned; M-CSA (2026-06-24, 1003 entries); 253 catalytic candidate families (>=500 `alignment:full`, folds balanced, ALL enzymatic) + 18 thin non-catalytic; per-family alignment route verified. This SUPERSEDES-IN-STATUS (append-only, no prior lock edited) three parts of the 2026-06-24 D2 pre-reg entry above: the (d) conservation-tautology control's SCOPE (was R1-only -> now R1 + M5), the (a) family-selection criteria (re-oriented), and the (f) M5 partition's PASS CRITERION (now entropy-baseline-relative). Every numeric/option choice below is FLAGGED PENDING Benjamin's ruling; the family list is selected and the pre-reg LOCKED only AFTER he rules.

**THE GATING FINDING (source-cited).** On D2, the persistence target, the M5 partition, AND the catalytic seed are ALL conservation -- so a compressor (or any column-entropy detector) passes TRIVIALLY by detecting conserved columns. That is the NULL the framework must be VULNERABLE TO, not the claim:
  - R1 (Meta-coherence Sec 6.3) = Spearman(`w`, INVERSE substitution tolerance) = column conservation.
  - M5 partition (Sec 4.7, ~line 579) noise class = "bottom-conservation-quintile" positions (and the coherence-bearing class includes the "top-conservation-quintile") -- the partition is conservation-DEFINED.
  - Catalytic seed (M-CSA, axis 4) = the most conservation-DOMINATED families (catalytic residues are the most conserved columns).
The entropy-baseline control (the only non-tautology guard) was scoped to R1 ONLY. This amendment makes it the PRIMARY D2 GATE across BOTH R1 and M5, pins the load-bearing ortholog-ordering knob, disambiguates control-failure from measurement-mismatch, and re-orients family selection away from the tautology-optimizing catalytic-heavy pool.

**(1) ENTROPY-BASELINE CONTROL = THE PRIMARY D2 GATE, EXTENDED TO M5.**
  - R1 (restated as primary, unchanged from the prior lock): the R1 statistic per (K,A) cell is the ENTROPY-BASELINE CONTRAST -- does the proxy's Spearman(`w`, inverse-tolerance) EXCEED a pure column-entropy baseline "`w`"'s Spearman(inverse-column-entropy, inverse-tolerance) by the pre-registered R1 margin -- in concordance with the conservation-stratified within-bin R1 (BOTH must clear; disagreement = CONFOUND-AMBIGUOUS).
  - M5 (NEW): the M5 admissibility ratio `M5_raw = mean_w(coherence-bearing positions) / mean_w(noise positions)` must EXCEED the SAME ratio computed for a pure column-entropy baseline "`w`" (`M5_entropy`), by the pre-registered M5 margin (`M5_raw - M5_entropy >= M5_MARGIN`, additive form; a ratio-of-ratios form is an alternative -- FLAGGED). An M5 ratio that does NOT beat the entropy baseline is recorded as CONSERVATION-CONFOUNDED, NOT M5-pass. Mirror R1's discipline: a conservation-stratified within-bin M5 corroborator + the concordance rule (both clear, else CONFOUND-AMBIGUOUS) + the disconfirmer (collapse to baseline = conservation-confounded).
  - STATED PLAINLY: a D2 result that clears R1/M5 on RAW conservation but NOT above the entropy baseline is NOT metacoherence evidence -- it is the tautology, recorded as such.
  - FLAGGED PENDING (Benjamin's numbers): the R1 contrast margin AND the M5 contrast margin (two values), plus the M5 additive-vs-ratio-of-ratios form. Candidate framing (NOT picked): the project's calibrated-margin idiom (cf. `T_NOISE=0.3`, `WIN_MARGIN=0.20`, the decoupling `0.40/0.10` bands).

**(2) THE SUBSTANTIVE D2 CLAIM = HIGHER-ORDER STRUCTURE BEYOND PER-COLUMN CONSERVATION.** The real signal D2 must capture is structure INVISIBLE to column entropy but VISIBLE to joint/sequential proxies: coevolving/contacting residues conserved as PAIRS (not individually), sequence motifs, allosteric couplings. The D2 claim is therefore: philosophically-decoupled proxies CONVERGE on persistence-relevant structure that BEATS raw per-column conservation. Item (1) is the operationalization of this claim; Items (3)-(5) ensure the design can actually express it (sequential proxies must see order; the family pool must contain the higher-order signal).

**(3) ORTHOLOG ORDERING -- PINNED (was unspecified; load-bearing).** In D1 the grid index was TIME (a natural canonical order); in D2 the index is "ortholog" with NO canonical order, yet the sequential proxies (K2 n-gram MDL, K3 GRU prequential, K5 LZ76 parsing) CONDITION on that order. An arbitrary order degrades them toward per-column estimators, which (a) makes them entropy-baseline-LIKE (re-introducing the tautology through the back door) and (b) COLLAPSES the cross-philosophy decoupling that R2 needs -- the exact D1 R2 failure re-entering through an unpinned knob. The ordering MUST be deterministic and pinned. FLAGGED PENDING (Benjamin's option + the trade):
    (i) PHYLOGENETIC / guide-tree order -- exposes evolutionary structure to the sequential proxies (strongest signal for them) BUT couples D2 to the tree-inference tool (pin tool+version+params; the per-family tree is already a pinned input under the software-pinned discipline).
    (ii) FIXED deterministic order (e.g. by UniProt accession) -- exposes NO phylogenetic signal; cleaner / tool-light but WEAKER for the sequential proxies (closer to per-column).
    (iii) ORDER-INVARIANT treatment -- aggregate each sequential proxy over several PINNED random orders (pinned seeds), removing order as a confound entirely; most conservative, highest compute.
  REQUIRED PRE-BUILD GATE (recorded, pre-registered): BEFORE any grid run, verify on 1-2 PILOT families that the chosen ordering does NOT collapse the proxies toward each other -- i.e. the cross-philosophy decoupling SURVIVES (the proxies remain distinguishable, not all reduced to column-entropy). This is an R2-PREREQUISITE gate; a collapse means the ordering choice is INADMISSIBLE and must change before the grid.

**(4) PROXY / PHYLOGENY MISMATCH -- recorded honestly; control-failure DISAMBIGUATED.** The proxies have NO phylogeny; the R1 target (Rate4Site per-site rate) IS phylo-corrected; the entropy baseline captures what the proxies CAN see (per-column composition). So there is a NARROW window between a tautological pass (no control) and a structural FALSE-FAIL (with control -- the proxies penalized for being blind to the phylo-corrected signal). Pre-registered disambiguation: an R1 (or M5) that FAILS the entropy-baseline control is reported as EITHER (a) CONSERVATION-CONFOUNDED (the proxy saw only conservation, which the baseline already captures) OR (b) MEASUREMENT-MISMATCH (the proxy is blind to the phylo-corrected higher-order signal), DISTINGUISHED by whether the proxies capture ANY higher-order structure on the Item-(3) PILOT check. A control-failure is NOT silently read as "metacoherence false"; the two readings are NAMED, pre-committed outcomes.

**(5) FAMILY SELECTION RE-ORIENTATION (do NOT lock the M-CSA-catalytic-heavy pool as-is).** The catalytic seed optimizes TOWARD the tautology (catalytic residues = the most conserved columns). Re-orient selection to REQUIRE higher-order-structure-rich families where a NON-tautological signal can exist:
  - NEW SELECTION AXIS: documented COEVOLUTION / residue-contact structure. FLAGGED PENDING (Benjamin's source choice): (A) PDB-derived CONTACT MAPS (families with solved structures -> residue-residue contacts); (B) EVcouplings / DCA coevolution scores (precomputed coevolution); (C) a combination. The source determines the per-family fetch and the pin (recorded in the manifest).
  - KEEP catalytic coverage for the M5 partition (documented catalytic residues remain the cleanest coherence-bearing class) but do NOT let it DOMINATE; balance against non-catalytic + high-coevolution families.
  - RECORD axis CORRELATION: axis 3 (functional) and axis 4 (catalytic) are CORRELATED (catalytic => enzymatic), so the stratification has ~3 INDEPENDENT dimensions (structural fold; ortholog depth; and a function/catalysis/coevolution composite), NOT 4. Adjust the balancing target accordingly -- do NOT over-fit equal counts to 4 nominally-independent axes.
  - FIX the spurious catalytic mappings: the survey's residue-in-RANGE containment conflated catalytic with binding (e.g. EF-hand `PF13499`, EGF `PF00008` flagged catalytic from single M-CSA entries). REQUIRE, before any family counts as axis-4 CATALYTIC: a residue-in-DOMAIN match (the catalytic residue falls within the Pfam domain's boundaries, not merely the host protein) AND a catalytic-vs-binding check (the M-CSA role is CATALYTIC, not a binding/structural spectator).

**(6) SUBSAMPLE-TO-N RULE -- LOCKED (was deferred).** `alignment:full` reaches 1.05M sequences (PF00069); tree inference + Rate4Site are infeasible at that scale. Pre-register a DETERMINISTIC subsample-to-N: post-90%-redundancy filtering, then if the family still exceeds N sequences, subsample to exactly N with a PINNED seed; record the seed + N in the manifest as pinned inputs (per the software-pinned discipline). Optionally also a SELECTION CAP (exclude families above an `alignment:full` ceiling from the candidate pool entirely). FLAGGED PENDING (Benjamin's numbers): N (the subsample target), the pinned subsample seed, and whether to also impose a selection cap (+ its value). Candidate framing (NOT picked): N in the low-thousands keeps tree+Rate4Site tractable while preserving >=500 post-filter depth; the 36 surveyed oversized families (>50k) are the ones this governs.

**FLAGGED-PENDING SUMMARY (Benjamin rules BEFORE the family lock + pre-reg lock).** (1) R1 contrast margin + M5 contrast margin [+ M5 additive-vs-ratio form]; (3) ortholog-ordering option (i / ii / iii); (5) coevolution-source ((A) PDB contacts / (B) EVcouplings-DCA / (C) combination); (6) subsample N + pinned seed + optional selection cap. STILL OPEN from the prior D2 entry: the family count (20-30) + the re-oriented stratification list; the phylo-correction software/version pins. RECORDED PRE-BUILD GATES (not numeric choices): the Item-(3) pilot decoupling check, and the Item-(5) residue-in-domain catalytic re-check.

**Discipline.** DESIGN + dated amendment ONLY -- NO family lock, NO alignment fetch, NO induction/R1/R2/M5 run, NOTHING data committed (`data/` gitignored; manifest report-only). SUPERSEDES-IN-STATUS (append-only) the prior D2 entry's (d)-control-scope, (a)-selection, and (f)-M5-pass-criterion; no prior lock edited, no constant VALUE changed. The family list is selected and the pre-reg LOCKED only AFTER Benjamin rules on the flagged choices. Append-only, ASCII.

### 2026-06-24 -- v0.7.2 D2 (Pfam) PRE-REG RESOLUTION: pending choices LOCKED -- ortholog order = FIXED (UniProt-acc; phylo REJECTED), entropy-baseline margins = BOOTSTRAP-CI-ON-DIFFERENCE, coevolution selection = PDB CONTACTS (DCA quarantined), subsample-to-N -- plus the (iv) position-as-index WITHDRAWAL [R1/M5 floors, contact cutoff, N, family count still flagged]

**What this is.** A dated, append-only amendment that RESOLVES the FLAGGED-PENDING choices from the conservation-tautology rework (committed `4d7a7c6`) into the locked D2 spec. DESIGN ONLY -- NO family selection, NO alignment fetch, NO induction/R1/R2/M5 run, NO data committed (`data/` gitignored; survey artifacts local-only). Each item below is now DECIDED with rationale EXCEPT a small set explicitly left to Benjamin's NUMBER (the R1 floor, the M5 floor, the contact-distance cutoff, the subsample N, the family count) -- recommended values given, flagged PENDING his confirmation. SUPERSEDES-IN-STATUS (append-only) the corresponding FLAGGED-PENDING placeholders in the rework entry (`4d7a7c6`); no prior lock edited, no constant VALUE changed. The family list is selected and the pre-reg LOCKED only AFTER Benjamin confirms the flagged numbers AND the Item-(3) pilot decoupling gate passes.

**(0) CORRECTION FIRST -- the "position-as-index" reframe (option iv) is WITHDRAWN.** Refuted by Meta-coherence Sec 6.2: the source FIXES features = POSITIONS and the traversed index = ORTHOLOGS, and the ablations remove POSITIONS. R1 = Spearman(`w_position`, tolerance_position) and the M5 partition both REQUIRE a PER-POSITION `w`, which ONLY the source's transposition (positions-as-features, orthologs-as-the-traversed-stream) yields; a position-as-index serialization would forfeit per-position `w` and break both R1 and M5. The source design is RETAINED UNCHANGED on this axis; the earlier-floated position-as-index idea is recorded as WITHDRAWN, not adopted.

**(#3) ORTHOLOG ORDERING = FIXED DETERMINISTIC (UniProt accession, ascending), pinned; PHYLO-ORDER REJECTED.** Orthologs are an exchangeable-ish sample, so the STATEFUL proxies (K3 GRU hidden state, K4 HMM latent state) converge to the family's JOINT position-distribution -- which carries the cross-position COEVOLUTION signal -- regardless of order; order perturbs only transient early predictions, negligible at `N >= 2000`. So a fixed deterministic key (UniProt accession ascending) is pinned and sufficient.
  - PHYLO-TREE ORDER REJECTED (recorded with reason): it injects phylogenetic AUTOCORRELATION between adjacent orthologs that the sequential proxies can exploit AND that is CORRELATED with the Rate4Site (phylo-derived) R1 TARGET -> circularity between predictor and target (a "pass" manufactured by the ordering tracking the target's own phylogeny). Fixed order avoids this; the modest cost to the sequential proxies is acceptable and is itself part of the decoupling signal below.
  - EXPECTED PER-ESTIMATOR SPLIT (a feature, not a bug): K2 (per-position n-gram over the ortholog index) has an UNINFORMATIVE context for exchangeable orthologs, so it COLLAPSES toward the per-column marginal == the entropy baseline, and is EXPECTED to FAIL the entropy-baseline control NON-PATHOLOGICALLY (coverage-limited, exactly as K1 misses property D on D1). The metacoherence test therefore rests on the COEVOLUTION-CAPABLE proxies -- K3/K4 (joint/latent, see cross-position coevolution), and K1/K5 per their serialization -- BEATING the baseline AND CONVERGING; the joint/latent-vs-factorized (K3/K4 vs K2) contrast IS a genuine cross-philosophy decoupling axis.
  - SHARPENED Item-(3) PILOT DECOUPLING GATE (the already-on-record pre-build gate, made concrete): on 1-2 coevolution-bearing pilot families, verify (a) K3/K4 BEAT the entropy baseline under the fixed order, AND (b) the grid does NOT collapse to all-marginal (cross-philosophy decoupling SURVIVES -- the proxies stay distinguishable). If even K3/K4 cannot clear the baseline, the SERIALIZATION needs rework BEFORE any family locks (the gate fails closed).

**(#1) ENTROPY-BASELINE MARGINS = BOOTSTRAP-CI ON THE DIFFERENCE (not hand-set magic numbers).**
  - R1: a proxy BEATS the baseline iff the ORTHOLOG-RESAMPLING bootstrap 95% CI on `(proxy_R1 - baseline_R1)` EXCLUDES 0, AND the point estimate clears a small a-priori FLOOR. `baseline_R1 = Spearman(entropy_w, inverse-tolerance)`, where `entropy_w` = a monotone map of NEGATIVE per-column entropy (low-entropy/conserved column -> high baseline `w`). FLAGGED (Benjamin's number): the R1 floor; RECOMMENDED `+0.05` Spearman.
  - M5: use the LOG-RATIO form (scale-free, well-behaved): a proxy BEATS the baseline iff the bootstrap 95% CI on `[ log(proxy_bearing/noise_ratio) - log(baseline_bearing/noise_ratio) ]` EXCLUDES 0, plus a small FLOOR. Preferred OVER a raw ratio-of-ratios. FLAGGED (Benjamin's number): the M5 log-ratio floor (a small positive value; recommendation deferred to him).
  - DISCONFIRMER (carried from the rework, unchanged): a result clearing R1/M5 on RAW conservation but NOT above the entropy baseline (CI on the difference includes 0 / below floor) is recorded CONSERVATION-CONFOUNDED, NOT a pass.

**(#5) COEVOLUTION SELECTION SIGNAL = PDB-DERIVED CONTACT MAPS (structurally independent); DCA QUARANTINED.**
  - LOCK: the higher-order-structure selection axis uses PDB-derived residue CONTACT MAPS (residue pairs within a pinned distance cutoff, Cb-Cb) from the family's representative structure(s) -- structurally INDEPENDENT of the MSA the proxies compress. FLAGGED (Benjamin's number): the distance cutoff; RECOMMENDED `8A Cb-Cb`.
  - DCA / EVcouplings QUARANTINE (recorded): DCA is permitted ONLY as a SUPPLEMENTARY SELECTION filter (to identify families that HAVE coevolution); it MUST NOT be used as a VALIDATION TARGET or a reference comparison, because it is computed from the SAME MSA the proxies compress (circular). The validation target stays Rate4Site tolerance; the independent selection signal stays PDB contacts.
  - Selection REQUIRES coevolution-RICH families (non-trivial contact density BEYOND sequence-local i,i+/-k) so the stateful proxies have higher-order structure to beat the baseline with; catalytic-conservation-ONLY families must NOT dominate. Axes 3 (functional) and 4 (catalytic) are CORRELATED (catalytic => enzymatic) -> ~3 INDEPENDENT stratification dimensions (structural fold; ortholog depth; a function/catalysis/coevolution composite); balance to ~3 dims, not a forced 4.
  - SPURIOUS-CATALYTIC FIX (the Item-5 pre-build gate, concrete): before a family counts as axis-4 CATALYTIC, require a residue-in-DOMAIN match (the M-CSA catalytic residue falls within the Pfam domain boundaries, not merely the host protein) AND a catalytic-vs-binding check (M-CSA role = CATALYTIC, not a binding/structural spectator). The survey's residue-in-RANGE containment misflagged EF-hand `PF13499` and EGF `PF00008` (binding, not catalytic) -- these and their kind are excluded from the catalytic count until they pass.

**(#6) SUBSAMPLE-TO-N = deterministic random subsample, PINNED seed, post-90%-redundancy.** Any family exceeding N sequences after the 90%-redundancy filter is randomly subsampled to EXACTLY N with a pinned seed (recorded in the manifest). FLAGGED (Benjamin's number): N; RECOMMENDED `N = 2000`, within `1500-3000` -- `>= 1500` so the upper depth bucket is not truncated below its defining threshold, `<= ~3000` to keep tree + Rate4Site tractable. NO separate hard selection cap is needed (subsample makes any family tractable). Recorded caveat: very large families may be clade-skewed; mitigated by the redundancy filter + the random subsample.

**(FAMILY COUNT + PINS).** FLAGGED (Benjamin's number): the family count; RECOMMENDED the LOW end `20-22`, given the thin non-catalytic half + the coevolution re-orientation -- a smaller well-balanced set beats a forced larger one. PINNED phylo stack (deterministic, recorded in the manifest at lock): tree tool + version (FastTree OR IQ-TREE, fixed seed), Rate4Site version, the `>=90%` redundancy tool + version, and the contact-map source + PDB release. These pins instantiate the software-pinned (not bit-exact) D2/D3 reproducibility discipline.

**FLAGGED-PENDING SUMMARY (Benjamin's NUMBER; recommended defaults in brackets).** R1 floor [`+0.05` Spearman]; M5 log-ratio floor [small positive, his call]; contact-distance cutoff [`8A Cb-Cb`]; subsample N [`2000`, range `1500-3000`]; family count [`20-22`]. GATES (pass/fail, not numbers): the Item-(3) pilot decoupling gate (K3/K4 beat baseline + no all-marginal collapse) and the Item-(5) residue-in-domain catalytic re-check -- both must pass BEFORE the family lock. DECIDED + LOCKED this entry (no longer open): ortholog ordering (fixed/UniProt-acc; phylo rejected), the entropy-baseline margin MECHANISM (bootstrap-CI-on-difference; M5 log-ratio form), the coevolution selection SOURCE (PDB contacts; DCA quarantined), and the subsample MECHANISM (pinned-seed random, post-redundancy). The (iv) position-as-index reframe is WITHDRAWN.

**Discipline.** DESIGN + dated amendment ONLY -- NO family lock, NO alignment fetch, NO induction/R1/R2/M5 run, NOTHING data committed (`data/` gitignored). Supersedes-in-status (append-only) the rework entry's flagged-pending placeholders; no prior lock edited, no constant VALUE changed. The family list is selected and the pre-reg LOCKED only AFTER Benjamin confirms the flagged numbers AND the Item-(3) pilot decoupling gate passes. Append-only, ASCII.

### 2026-06-24 -- v0.7.2 D2 (Pfam) REDESIGN: dual-transposition DECIDING PILOT (framing S vs framing P) pre-registered before any family lock; D1-cross-tab-grounded coevolution-confound finding; ortholog order -> PINNED RANDOM PERMUTATION

**What this is.** A dated, append-only amendment that PRE-REGISTERS a DECIDING PILOT (1-2 families, framing S vs framing P) BEFORE any family-list lock, in response to an adversarial stress-test grounded in D1's OWN recorded cross-tab. DESIGN + a SMALL pilot build/run only -- NO family-list lock, NO full 20-family grid, NO induction at scale; pilot data gitignored. SUPERSEDES-IN-STATUS (append-only, no prior lock edited): the resolution entry's implicit "framing S is adequate" endorsement (CORRECTED below) and its ortholog-ORDER KEY (UniProt-acc ascending -> a pinned random permutation); the fixed-deterministic-and-PHYLO-REJECTED ruling STANDS. No constant VALUE changed.

**THE FINDING (D1-grounded; the redesign's rationale).** D2's non-tautological persistence signal = COEVOLUTION (cross-position coalition structure -- contacting/coevolving residues conserved as PAIRS), the signal that beats the conservation baseline. D1's recorded cross-tab proves WHICH proxies can see cross-position COALITION structure: K5 {A,B,C,D}, K1 {A,C}, K2/K3/K4 {A,D} -- the FACTORIZED TRIO (K2/K3/K4) MISSED property C (the coalition); ONLY the byte-stream pair {K1,K5} caught it. Therefore, under the source's traverse-ORTHOLOGS transposition (framing S), D2 coevolution is PREDICTED to be caught ONLY by {K1,K5} (shared byte encoding) and MISSED by {K2,K3,K4}. That reproduces the D1 R2 REPRESENTATION CONFOUND AND makes any R1 "pass" carried by {K1,K5} alone a REPRESENTATION-CONFOUNDED signal, NOT cross-philosophy method-invariance -- so D2 risks being a SECOND INSTANCE of D1's coverage finding, not the independent confirmation R1 was elevated to provide. CORRECTION TO THE RECORD: the prior endorsement of framing S as adequate is WRONG ON THIS POINT -- it relied on K3/K4 capturing coevolution, which D1 FALSIFIED (K3/K4 sit in the {A,D} trio that missed the C coalition). The fixed-order-vs-phylo-order ruling STILL STANDS; this supersedes only the "S is adequate" framing.

**TWO CANDIDATE TRANSPOSITIONS (pre-registered; DECIDED BY THE PILOT, not picked blind).**
  - FRAMING S (source, Sec 6.2): stream index = ORTHOLOGS, features ablated = POSITIONS, `w` per-position. Coevolution reachable ONLY via the joint/byte proxies + A2/A3 (the D1 lesson).
  - FRAMING P (NEW; erratum-class deviation from Sec 6.2; DISTINCT from the withdrawn option iv): stream index = POSITIONS along the backbone (ORDERED), each position represented by its COLUMN CONTENT (the across-ortholog residue profile/vector at that position), features ablated = POSITIONS, `w` per-position -- so R1 = Spearman(`w_position`, inverse-tolerance) and M5 are SATISFIED (option iv failed EXACTLY here by forfeiting per-position `w`; P does NOT, because positions remain the ablated unit). Rationale: local coevolution becomes a SEQUENTIAL BACKBONE DEPENDENCY that the factorized/sequential proxies (K2/K3/K5) CAN catch, giving the factorized family a real shot at the signal and a chance to BREAK the {K1,K5}-only pattern. Recorded: the source's traverse-orthologs RATIONALE ("evolutionary recoverability = structure RECURRING across the ortholog set") is itself CONSERVATION re-stated -- which is WHY S is tautology-prone and P is the candidate fix.
  - Both framings KEEP everything else already locked: per-position `w`; the Rate4Site inverse-tolerance R1 target; the entropy-baseline control as the PRIMARY gate (R1 + M5, bootstrap-CI-on-difference); the conservation-tautology disconfirmer; Pfam-not-adjudicator; subsample-to-N.

**ORTHOLOG ORDER -> PINNED RANDOM PERMUTATION (corrects the resolution entry's KEY).** Change the locked ortholog order from "UniProt accession ascending" to a PINNED RANDOM PERMUTATION (seeded): accession order has weak TAXONOMIC clustering that can re-introduce the phylo-autocorrelation the resolution REJECTED; a seeded shuffle is PROVABLY structure-free AND equally reproducible. Applies to framing S, and to framing P's within-position column representation wherever ortholog order matters. Supersedes-in-status the resolution's ortholog-KEY ONLY; the fixed-deterministic + phylo-rejected RULING stands; the permutation seed is a pinned manifest input.

**THE DECIDING PILOT (pre-committed; runs on 1-2 families; now answers "can D2 escape D1's confound AT ALL," not merely "does the apparatus work").**
  - PILOT FAMILIES (picked data-drivenly from the catalytic shortlist; coevolution-rich = contact-dense folds with abundant solved structures): (1) `PF13354` (Beta-lactamase2) -- ALPHA-BETA (CATH class 3), `alignment:full` 10129, 774 PDB structures, 7 M-CSA catalytic residues; a CANONICAL coevolution/DCA benchmark with rich long-range alpha-beta tertiary contacts and a tractable subsample. (2) `PF00026` (aspartic protease / pepsin-like) -- ALL-BETA (CATH class 2), `alignment:full` 43779, 1711 PDB structures (the most in the pool), 7 catalytic residues; classic, with rich all-beta long-range strand-pairing contacts, CONTRASTING the fold class. RATIONALE for EXCLUDING all-alpha (CATH 1): helical folds carry mostly LOCAL (i,i+3/4) contacts and weak long-range coevolution, the WORST stress for the "can factorized proxies catch coevolution" question; the two contact-rich classes (alpha-beta, all-beta) maximize the signal the pilot must detect.
  - FETCH (gitignored): each family's full alignment (subsample to N, pinned seed) + the representative-structure CONTACT MAP (residue pairs within the pinned Cb-Cb cutoff).
  - RUN the FULL 5-proxy grid (K1-K5; A1 at least, A3 if cheap) under BOTH framing S and framing P on each pilot family -> per-position `w` per (proxy, framing).
  - PRE-COMMITTED DIAGNOSTICS (fixed BEFORE any number is looked at):
    (1) ENTROPY-BASELINE CONTRAST per proxy: does proxy `w` beat the column-entropy baseline at predicting INVERSE-TOLERANCE (ortholog-resampling bootstrap CI on the DIFFERENCE excludes 0)? Report WHICH proxies pass. [TOOLING NOTE, recorded: the locked R1 target is Rate4Site; if the Rate4Site + tree pipeline is unavailable at pilot time, diagnostic (1) is DEFERRED to the build and the pilot VERDICT rests on (2)+(3) -- the Rate4Site-FREE, structure-grounded coevolution test, which is the load-bearing axis for the S-vs-P decision.]
    (2) COEVOLUTION RECOVERY: does proxy `w` (or A3's clusters) CONCENTRATE on PDB-contacting / high-coevolution positions ABOVE non-contacting (bootstrap)? Report which proxies recover it.
    (3) CROSS-PHILOSOPHY SPREAD: are the proxies that clear (1)/(2) CONFINED to {K1,K5} (representation-confounded) or do the factorized {K2,K3,K4} ALSO clear it?
  - PRE-COMMITTED DECISION RULE (written BEFORE the numbers):
    * If under framing S only {K1,K5} clear the baseline/coevolution -> S reproduces the D1 confound -> S is REJECTED for D2.
    * If under framing P the factorized {K2,K3,K4} ALSO clear it (the factorized family is no longer monopolized by byte-stream) -> P breaks the confound -> P is ADOPTED.
    * If NEITHER framing lets the factorized proxies clear it -> record that D2 CANNOT escape the coverage/representation confound; D2 is pre-registered as EXPECTED-COVERAGE-CAPPED: R2 diagnostic-only, R1 reported PER-ESTIMATOR with the EXPLICIT caveat that a {K1,K5}-only pass is representation-confounded and does NOT establish cross-domain method-invariance.
    * If BOTH framings work -> prefer S (less source deviation); record P as the fallback.

**Discipline.** DESIGN + dated amendment; the pilot is a SMALL 1-2-family build/run (data gitignored), NOT a family-list lock and NOT the full 20-family grid, NOT an R1/R2/M5 production run. The transposition (S vs P) and the family list are LOCKED only AFTER the pilot verdict + Benjamin's sign-off. Supersedes-in-status (append-only) the resolution entry's "S adequate" endorsement + the ortholog-KEY; no prior lock edited, no constant VALUE changed. Append-only, ASCII.

### 2026-06-24 -- v0.7.2 D2 (Pfam) COUPLING PILOT (intermediate) + B' PRE-REGISTRATION: edge-valued coevolution vs node-valued induced-w; the B target self-corrected

**What this is.** A dated, append-only amendment recording the D2 beta-direction COUPLING PILOT outcome (PF13354) and PRE-REGISTERING the next check B' with thresholds FIXED here, BEFORE B' is run (sec 8: pre-register before implementation; this entry is committed + pushed before the B' run). DESIGN + a standalone measurement that REUSES pinned artifacts only (`data/pfam/pilotS_PF13354_matrix.npy`, `iq_PF13354.rate`, PDB `1djc`); it does NOT touch the KxA grid or the proxies. Nothing in `data/` is committed (gitignored). Context: the framing-S premise check found the marginal-relative proxies EMPTY (K2/K3 perfectly flat, K1/K4 near-flat; w orthogonal to conservation); this entry tests whether the beta SIGNAL (cross-position coupling) EXISTS to induce w toward.

**(a) COUPLING-PILOT OUTCOME (PF13354; `scripts/pilot_d2_coupling.py`).** Meff = 1522 / 2000; mapping 244 / 248 columns -> `1djc:A`; contacts 644 (Cb-Cb < 8A, |i-j| >= 5); MIp APC-corrected (raw-MI mean 0.275 -> MIp mean ~0). Contacts + MIp enter as COMPARISON-COMPRESSIONS (Meta-Coherence Sec 6.4 idiom), NOT a ground-truth oracle.
  - A (top-L MIp PAIR precision) = 0.131 vs base rate 0.022 vs conservation-product 0.016 -> PASS.
  - C (Spearman(s_i, conservation)) = -0.338; s_i vs inverse-tolerance +0.016 -> PASS.
  - B (Spearman(s_i, contact_degree)) = +0.101 vs conservation's +0.430 -> FAIL.
  - VERDICT: INTERMEDIATE. The pairwise coevolution signal is REAL, STRONG, and conservation-INDEPENDENT (A, C); the per-position SUM s_i is a WEAK contact-DEGREE predictor (B). Neither the strict HOLD (A and B and C) nor the explicit collapse-to-alpha trigger (C >= 0.7, or A at base rate) fired.

**(b) DIAGNOSIS (hypotheses, NOT conclusions).** (i) The naive SUM is a poor edge->node projection: APC-centering plus sparse strong partners buried under many near-zero MIp terms means s_i = sum_j MIp(i,j) is noise-dominated. (ii) contact_degree is BURIAL-confounded: buried residues are BOTH more conserved AND higher contact-degree, so conservation's +0.430 is largely BURIAL, not coupling. Both hypotheses motivate B'.

**(c) SELF-CORRECTION on pre-registration (sec 8, honest).** The pre-committed B target (contact_degree) was BURIAL-loaded and structurally favored conservation. B as-registered FAILED and is NOT silently redefined; B' (below) is a NEW pre-registered check, recorded as a successor, NOT a retcon of B.

**(d) STRUCTURAL OPEN QUESTION.** Coevolution is EDGE-valued (a property of position PAIRS); CIT induced-w is NODE-valued (Sec 6.2 per-position w). The edge->node projection is the CENTRAL beta risk: if no faithful node-projection of the coupling signal exists, Sec 6.2's per-position-w construction is under strain for D2. beta stays a CANDIDATE direction GATED on B' -- NOT locked into the D2 design.

**(e) B' PRE-REGISTRATION (thresholds FIXED here, before running).**
  - Node aggregations from the existing MIp matrix (`data/pfam/pilot_coupling_PF13354.npz`):
      s_max(i)  = max_j MIp(i,j);
      s_top5(i) = mean of the top-5 MIp(i,j) over j;
      s_cnt(i)  = #{ j : MIp(i,j) > q99 }, where q99 = the 99th percentile of off-diagonal MIp.
  - Burial proxy = Cb HALF-SPHERE EXPOSURE (`Bio.PDB.HSExposure.HSExposureCB` on `1djc:A`; no external binary). PINNED.
  - Targets: T1 = contact_degree (continuity with B); T2 = BURIAL-CONTROLLED = partial Spearman(s_agg, contact_degree | burial) vs partial Spearman(conservation, contact_degree | burial).
  - B'-PASS iff AT LEAST ONE aggregation has partial-Spearman(s_agg, contact_degree | burial) BOTH > 0 AND > conservation's partial-Spearman. (Also report the raw Spearman of each aggregation vs contact_degree, and vs the original B, for the record.)
  - DECISION RULE: B'-PASS -> beta buildable at per-position granularity -> next step is JOINT-PROXY design (SEPARATE, not now). B'-FAIL -> the edge->node loss is real -> ESCALATE the Sec 6.2 per-position-w question to Benjamin; do NOT build past it.

**Discipline.** DESIGN + dated amendment + a standalone reused-artifact measurement; NO KxA grid, NO proxy changes, NO joint-proxy build; nothing in `data/` committed (gitignored). The pre-registration (this entry) is committed + pushed BEFORE B' is run. Append-only, ASCII.

### 2026-06-24 -- v0.7.2 D2 (Pfam) B' FAIL recorded + B2 graph-projection PRE-REGISTRATION: the LAST node-valued attempt before edge-valued w (branch A)

**What this is.** A dated, append-only amendment recording that the pre-registered B' check FAILED (no NAIVE partner-aggregation of the MIp coupling signal -- sum/max/top5/count -- beats burial-controlled conservation; result `B'-FAIL` in `scripts/pilot_d2_bprime.py`: s_max +0.020 / s_top5 +0.026 / s_cnt -0.012 all < conservation's burial-controlled partial +0.143) and PRE-REGISTERING B2 -- graph-STRUCTURAL node projections of the coupling graph -- with thresholds FIXED here, BEFORE B2 is run (sec 8: pre-register before implementation; committed + pushed before the B2 run). DESIGN + a standalone measurement that REUSES the existing MIp `.npz` (`data/pfam/pilot_coupling_PF13354.npz`; NO MIp recompute); SAME family PF13354, SAME mapped-244 positions, SAME burial control. B2 is the LAST node-valued attempt before an EDGE-VALUED `w` (branch A) is FORCED. Nothing in `data/` committed.

**(a) B2 = graph-structural node projections.** Motivated by B'-FAIL on NAIVE partner-aggregations: B2 tests whether the coupling-GRAPH TOPOLOGY (not per-node partner summaries) recovers a node-valued `w`, BEFORE conceding Sec 6.2 and forcing an edge-valued `w`.

**(b) Projections (node-valued; from MIp with weights = max(APC-MIp, 0), diagonal 0).**
  - g_eig = EIGENVECTOR CENTRALITY (leading eigenvector of the weighted adjacency; numpy).
  - g_pr = PAGERANK (power iteration, damping 0.85; numpy).
  - g_topL = per-position MEMBERSHIP COUNT in the top-L MIp pairs (L = #positions) -- node degree in the top-L coevolution graph; the direct A->node bridge.

**(c) Bar (IDENTICAL to B').** Burial = `HSExposureCB` on `1djc:A`; B2-PASS iff AT LEAST ONE projection has partial-Spearman(g, contact_degree | burial) BOTH > 0 AND > conservation's burial-controlled partial (computed IN-RUN, NOT hardcoded). Report raw + partial per projection + the conservation reference.

**(d) SPECIFIC PREDICTION (recorded, NOT gating).** The GLOBAL centralities g_eig / g_pr likely FAIL by the same sparse-strong-pair washout that sank the naive aggregations; g_topL is the only one with a real chance (it RESTRICTS to the contact-enriched top-L pairs, where pilot check A passed).

**(e) DECISION RULE.**
  - B2-PASS -> Sec 6.2 NODE-VALUED `w` SURVIVES; beta node-buildable via the passing projection; NEXT = node-valued joint-proxy design (SEPARATE; confirm on >= 1 more coevolution-rich family BEFORE any lock).
  - B2-FAIL -> the node-projection space is EXHAUSTED; an EDGE-VALUED `w` (branch A) is FORCED; NEXT = a corpus-admissibility check for an edge-valued `w` (boundedness / monotonicity / coarse-graining / Shannon-recovery at `w=1`) BEFORE any edge design; escalate to Benjamin.

**Discipline.** DESIGN + dated amendment + a standalone reused-`.npz` measurement; NO KxA grid, NO joint-proxy, NO edge-valued-`w` build; nothing in `data/` committed (gitignored). The pre-registration (this entry) is committed + pushed BEFORE B2 is run. Append-only, ASCII.

### 2026-06-24 -- v0.7.2 D2 (Pfam) SECOND-FAMILY REPLICATION + EDGE-M5 formalization: discharge the B2 confirm-clause (generalization test + node-retirement hardening)

**What this is.** A dated, append-only amendment that (i) records the B2 RESULT and (ii) PRE-REGISTERS a SECOND-FAMILY replication + an EDGE-M5 AUROC statistic, with the second family/PDB/chain LOCKED HERE pre-computation and all thresholds FIXED here, committed + pushed BEFORE the Phase-2 run (sec 8). B2 RESULT recap (PF13354, `scripts/pilot_d2_b2.py`): B2-PASS but NARROWLY -- only g_pr (PageRank, damping 0.85) cleared the bar, partial-Spearman(g_pr, contact_degree | burial) = +0.151 vs conservation's burial-controlled +0.143 (margin +0.008); g_eig +0.092 and g_topL +0.052 BOTH FAILED; the recorded prediction was INVERTED (g_topL was the predicted passer, the global PageRank flow passed). So Sec 6.2's NODE-VALUED `w` SURVIVED, but on a razor-thin, single-family, prediction-inverted pass -- the B2 pre-reg confirm-clause therefore REQUIRES replication on >= 1 more coevolution-rich family BEFORE any node-valued lock. This entry DISCHARGES that clause on ONE more family AND FORMALIZES the edge signal into a pre-registered statistic. PILOT replication; does NOT lock the D2 family list. Nothing in `data/` committed (gitignored).

**(a) SECOND-FAMILY SELECTION (outcome-independent rule + resolved lock).**
  - RULE (fixed BEFORE any coupling computation; final form). From `data/pfam/candidate_pool.tsv`, rows with catalytic=YES, oversized=False, depth '1500+', fold PURE 'all-a' or 'all-b' (does NOT contain 'a-b/a+b' -> a DIFFERENT fold from PF13354's a-b/a+b), AND Pfam-domain length >= 150 match columns. Ascending Pfam accession. SELECT the first family with a USABLE representative PDB: experiment x-ray, resolution <= 2.5 A, Pfam fragment CONTINUOUS and spanning >= 0.8 * (median Pfam-domain length over the family's PDBs), on a chain bearing EXACTLY ONE copy of the domain AND no other Pfam domain (the 'single-chain domain' requirement; resolved via the InterPro structure endpoint + PDBe SIFTS). PDB sub-rule (recorded): best resolution, tie-break lowest PDB accession; chain = 'A' if present among the mapped chains else lowest chain id. Family tie-break: lowest Pfam accession.
  - REFINEMENT NOTE (outcome-independent; recorded for transparency). The '>= 150 match columns' floor was ADDED to the rule at selection time (Benjamin's sign-off) to ensure a coevolution-RICH, PF13354-comparable single-domain target. Without it the literal lowest-accession hit is PF00024 (PAN_1, all-b) / 3hms:A -- a structurally CLEAN single domain (HGF N-terminal PAN, x-ray 1.7 A) but an ~82-column, weakly-catalytic (1 M-CSA residue), disulfide-DOMINATED tandem MODULE whose coevolution is the conserved Cys scaffold (edge-M5 would pass TRIVIALLY). Domain length and catalytic count are knowable PRE-coupling, so the floor is an outcome-independent WELL-SPECIFICATION, NOT a result-dodge; the rule is being committed NOW, so this finalizes its form BEFORE the lock. (PF00024/3hms recorded as the excluded-by-floor literal hit.)
  - RESOLVED LOCK (pre-computation). FAMILY = PF00026 (Asp; InterPro 'Eukaryotic aspartyl protease'; pepsin-like ASPARTIC PROTEASE), fold all-b, depth 1500+, 52,348 proteins, M-CSA 7 catalytic residues. PDB = 4y9w (Sapp2 aspartic proteinase, Candida parapsilosis), chain A, x-ray 0.82 A; SIFTS PF00026 -> chain A residues 13-323 (311-residue single CONTINUOUS domain; SOLE Pfam domain on the chain; chain B is a 6-residue peptide ligand, EXCLUDED). Alignment source = InterPro full alignment (`https://www.ebi.ac.uk/interpro/api/entry/pfam/PF00026/?annotation=alignment:full`). WHY = lowest-accession pure-all-b catalytic non-oversized 1500+ family with domain >= 150 cols and a usable CLEAN single-domain x-ray <= 2.5 A structure.
  - DISCHARGE + HARD STOP. A PASS/FAIL on this ONE family discharges the B2 confirm-clause ('confirm on >= 1 more coevolution-rich family before any node-valued lock'). HARD STOP = TWO families total (PF13354 + PF00026); this does NOT lock the D2 family list.

**(b) EDGE-M5 STATISTIC (pre-registered; thresholds fixed here).** Pair classes over mapped columns, |i-j| >= 5: COHERENCE-BEARING = CONTACT pairs (Cb-Cb < 8 A; Ca for Gly); NOISE = non-contact eligible pairs. Statistic = AUROC = P(a random contact pair outranks a random non-contact pair) under THREE scores: (1) MIp, (2) conservation-product cons_i * cons_j, (3) burial-product burial_i * burial_j. Report OVERALL and LONG-RANGE (|i-j| >= 12) separately. Bootstrap CI by RESAMPLING PAIRS (B = 1000). EDGE-M5 PASS iff MIp-AUROC > BOTH conservation-product-AUROC AND burial-product-AUROC, AND MIp-AUROC CI excludes 0.5 -- with EMPHASIS on the LONG-RANGE split (the burial/conservation-independent regime where a genuine coupling signal must show).

**(c) HARDENED node-retirement test (carries B2's robustness lesson).** On PF00026 run B' (naive aggregations s_max / s_top5 / s_cnt) AND B2 (g_eig / g_pr / g_topL), method identical to PF13354. For g_pr report partial-Spearman(g_pr, contact_degree | burial) vs BOTH conservation references: (i) COLUMN-ENTROPY conservation AND (ii) PHYLO-CORRECTED inverse-tolerance (IQ-TREE LG+G4 per-site rate) -- WITH a bootstrap CI on the MARGIN (g_pr_partial - conservation_partial). A node 'pass' counts as ROBUST only if g_pr beats the PHYLO-CORRECTED reference with the margin-CI EXCLUDING 0. (B2's PF13354 pass was razor-thin +0.008, single-family, prediction-inverted; this hardening is the bar a node-valued `w` must clear to survive a second family.)

**(d) DECISION RULES (pre-committed).**
  - EDGE GENERALIZES iff PF00026 shows (check A: top-L MIp PAIR precision >> contact base rate) AND (edge-M5 PASS per (b)).
  - NODE-FAIL GENERALIZES iff B' FAILS (no naive aggregation beats burial-controlled conservation) AND g_pr is NOT ROBUST per (c).
  - EDGE generalizes + NODE-FAIL generalizes -> the relational direction is DE-RISKED; node-valued `w` is RETIRED on 2 families -> proceed to the RELATIONAL build (an R2-EDGE statistic is what the build adds). [SEPARATE step; not now.]
  - EDGE does NOT generalize -> STOP; the edge signal was PF13354-specific; REASSESS the whole beta direction.
  - NODE 'pass' replicates ROBUSTLY (g_pr beats phylo-conservation, margin-CI excludes 0) -> node-valued `w` MAY survive; RECONSIDER before any edge build.

**(e) PF13354 EDGE-M5 FOLD-IN (formalization).** ALSO compute edge-M5 on PF13354 (reuse its pinned artifacts `data/pfam/pilot_coupling_PF13354.npz`; RE-DERIVE contacts from `1djc:A`) to FORMALIZE the coupling pilot's qualitative A/B/C result into the SAME AUROC statistic. This is a formalization of the EXISTING PF13354 finding, NOT a new family.

**PINS (Phase-2 run; method UNCHANGED -- reuse the existing scripts parameterized by (acc, pdb, chain)).** N = 2000 (subsample seed 0); 80%-identity sequence reweighting; 21-letter alphabet (gap = 20); MIp APC-corrected; contacts Cb-Cb < 8 A (Ca for Gly), |i-j| >= 5; IQ-TREE LG+G4 per-site rates (phylo-corrected inverse-tolerance); HSExposureCB burial (EXP_HSE_B_U); q99 = 99th-pct off-diagonal MIp (B' s_cnt); PageRank damping 0.85; BLOSUM62 PDB->consensus mapping. NO locked-constant VALUE is changed by this entry.

**Discipline.** DESIGN + dated amendment; the second family/PDB/chain + all edge-M5 / node thresholds are LOCKED HERE, pre-computation; committed + pushed BEFORE the Phase-2 run (sec 8). PILOT replication of TWO families total; does NOT lock the D2 family list; NO KxA grid, NO joint / edge build. This DISCHARGES (does NOT edit) the B2 confirm-clause. Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) SECOND-FAMILY REPLICATION + EDGE-M5 RESULT: edge GENERALIZES; node-valued w does NOT clear the hardened bar (branch adjudication HELD)

**What this is.** A dated, append-only RESULT record for the Phase-2 run pre-registered immediately above (the second-family replication + edge-M5). Apparatus = `scripts/run_d2_family2.py` (parameterizes the pinned coupling / B' / B2 method by (acc, pdb, chain) + adds the edge-M5 AUROC; the matrix-build recipe was pinned BIT-EXACT to the PF13354 pilot -- VERIFIED: rebuilding PF13354's matrix from the alignment reproduced `pilotS_PF13354_matrix.npy` exactly: match-state columns by case, gap-fraction < 0.5 on the `np.random.default_rng(0).choice(n,2000,replace=False)`-sorted subsample, AA 'ACDEFGHIKLMNPQRSTVWY' -> 0..19, else -> 20). No pin or constant VALUE changed; nothing in `data/` committed (gitignored). NO branch decision is taken here -- the adjudication is HELD for Benjamin.

**(a) SETUP (PF00026, Asp / 4y9w:A).** Full alignment 43,779 seqs -> seed-0 2000-subsample -> L = 312 match columns; Meff = 1438.6; PDB mapping coverage 293 / 312 (94%); 811 contacts (Cb-Cb < 8 A, |i-j| >= 5).

**(b) EDGE -- GENERALIZES (strongly; cleaner than PF13354).**
  - Check A (top-L MIp PAIR precision) = 0.160 vs contact base rate 0.019 (8.2x) vs conservation-product 0.020 -> PASS (PF13354 was 0.131 vs 0.022).
  - EDGE-M5 (PF00026) OVERALL: AUROC MIp = 0.802 (CI 0.789-0.814) > conservation-product 0.442 AND > burial-product 0.685; CI excludes 0.5. LONG-RANGE (|i-j| >= 12): MIp = 0.794 (CI 0.779-0.808) > 0.424 AND > 0.700. -> EDGE-M5 PASS on both splits (MIp beats BOTH controls incl. burial, even long-range).
  - DECISION-RULE (d): EDGE GENERALIZES = YES (check A pass AND edge-M5 pass).

**(c) PF13354 EDGE-M5 FOLD-IN (formalization).** OVERALL: MIp = 0.698 (CI 0.674-0.720) BEATS conservation-product 0.419 but NOT burial-product 0.716. LONG: MIp = 0.673 (CI 0.648-0.698) vs burial-product 0.720. -> on PF13354 MIp does NOT beat burial -> edge-M5 'fails' the burial comparison. So the edge signal is REAL on both families, but its MARGIN OVER BURIAL is family-dependent: it LOSES to burial on the small a-b/a+b PF13354 (0.70 < 0.72) and WINS decisively on the larger all-b PF00026 (0.80 > 0.69). The decision rule keys EDGE-GENERALIZES on the SECOND family (PF00026), which passes.

**(d) NODE -- does NOT robustly survive the hardened bar.**
  - References (partial-Spearman | burial, 293 positions): entropy-conservation = +0.091; phylo-corrected inverse-tolerance = +0.134.
  - B' naive aggregations: s_max +0.099, s_top5 +0.118, s_cnt +0.113 -- ALL beat entropy-conservation (so B' did NOT fail on PF00026, UNLIKE PF13354) but NONE beat the phylo reference.
  - B2 projections: g_eig -0.032 (fail), g_pr +0.127, g_topL +0.152.
  - HARDENED g_pr test (the pre-registered bar): margin vs entropy = +0.036 (CI -0.119,+0.180 -- INCLUDES 0); margin vs PHYLO = -0.007 (CI -0.154,+0.129 -- INCLUDES 0, point estimate NEGATIVE) -> ROBUST node pass = FALSE. The B2 PF13354 g_pr narrow-pass did NOT robustly replicate.
  - Non-replication of WHICH projection wins: g_pr passed on PF13354 / g_topL is strongest on PF00026 / g_pr is borderline-fail on PF00026 -> the node-valued projection is NOT stably identifiable across families.

**(e) DECISION-RULE MAPPING (pre-committed (d); MIXED -> HELD).**
  - EDGE GENERALIZES = YES.
  - NODE robust pass (g_pr beats phylo, CI excludes 0) = NO.
  - NODE-FAIL GENERALIZES (B' fails AND g_pr not-robust) = NO *strictly* -- only because B' beat the WEAKER entropy reference on PF00026 (the entropy bar dropped +0.143 [PF13354] -> +0.091 [PF00026] between families; the g_pr-not-robust half IS satisfied).
  - So the outcome lands BETWEEN branch-1 ('edge generalizes + node-fail generalizes -> retire node-valued w, relational build', blocked only by the B'-vs-entropy technicality) and branch-3 ('robust node pass -> node may survive', which the HARDENED phylo+margin-CI bar -- pre-registered AS the bar precisely because B2 was thin -- FAILS). The hardened bar is the one that fails.

**(f) DISCHARGE + STATUS.** The B2 confirm-clause is DISCHARGED on a second coevolution-rich family: the EDGE direction is DE-RISKED (generalizes, and on family 2 beats the burial confound PF13354 could not); the NODE-valued w does NOT clear the hardened bar on family 2 and its winning projection is unstable. The clean branch ('edge generalizes + node-fail generalizes -> relational/edge build') is met in spirit by the HARDENED bar but not by the strict B'-vs-entropy clause -> BRANCH ADJUDICATION HELD for Benjamin. HARD STOP = TWO families; the D2 family list is NOT locked; NO joint / edge build is started here.

**Discipline.** RESULT record + apparatus commit (`scripts/run_d2_family2.py`); the Phase-1 pre-registration (above) was committed + pushed BEFORE this run (sec 8). NO pin / constant VALUE changed; NO KxA grid, NO joint / edge build, NO family-list lock; NO branch decision taken (HELD). Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 1: node-valued w RETIRED -> edge-valued w ADOPTED; R2-edge premise (MIp vs MDL-compression; DCA EXCLUDED as Pearlian per corpus)

**BRANCH ADJUDICATION (Benjamin's decision, taken on the two-family record above).** The node-valued `w` is RETIRED: it failed the HARDENED phylo bar on BOTH families (PF13354 g_pr pass razor-thin + prediction-inverted; PF00026 g_pr margin vs phylo-conservation -0.007, CI includes 0; winning projection unstable g_pr/g_topL). The EDGE-valued `w` is ADOPTED: corpus-aligned (coevolution is a DENSE entangled coupling FIELD, not a sparse direct-edge graph) AND empirically supported (edge-M5 GENERALIZES; on PF00026 MIp beats both conservation- and burial-product even long-range). The edge-vs-burial margin is FOLD-DEPENDENT (lost to burial on PF13354), so burial MUST be controlled. This entry pre-registers the FIRST relational component: an edge-`w` formalism framing + an R2-EDGE convergence premise across two of CIT's OWN distinct DENSE paradigms. DESIGN + dated amendment; thresholds FIXED here; committed + pushed BEFORE the Phase-2 run (sec 8). Nothing in `data/` committed.

**CORPUS GROUNDING (load-bearing).** Coevolutionary coupling is a DENSE, entangled field. DCA / inverse-covariance / direct-coupling is the PEARLIAN direct-vs-indirect CUT the corpus deconstructs ("Cult of Causality"; "From Causation to Coherence", see [[cit-corpus-lineage]]) -- it is NOT used here as an R2 convergence partner or a validation standard. R2-edge tests convergence across CIT's OWN distinct paradigms (statistical / Shannon plug-in vs algorithmic / MDL), BOTH DENSE. DCA may return LATER as a SEPARATE, non-adjudicating "Pearlian-contrast" diagnostic -- NOT here.

**(a) EDGE-W FORMALISM (framing).** `w` on position-PAIRS = the CIT per-symbol `w` applied to the JOINT pair-symbol over the PRODUCT alphabet (A x A, here 21 x 21 = 441) -> it enters H_w / I_w exactly as the per-symbol weight does, with the pair-symbol as the source symbol. Shannon-recovery (w=1 over pair-symbols collapses to the joint Shannon quantity), coarse-graining (pair -> marginal), and monotonicity are FLAGGED for a SEPARATE formal-admissibility check (corpus-admissibility of an edge-valued `w`) and are NOT gating this run.

**(b) R2-EDGE ESTIMATORS (DENSE paradigm; genuinely distinct inductive bias).**
  - K_MI = APC-corrected MIp (statistical / Shannon plug-in; REUSE the saved MIp `.npz`, no recompute).
  - K_comp = a COMPRESSION / MDL edge coupling (algorithmic): per pair (i, j), the description-length SAVING of coding the JOINT pair-symbol vs coding i and j INDEPENDENTLY -- marginal-relative (the locked CIT proxy idiom; the EDGE analog of K1 compression-delta / K2 MDL). Concretely K_comp(i,j) = L(col_i) + L(col_j) - L(joint_ij), where L is a stochastic-complexity codelength (Krichevsky-Trofimov / KT, the parameter-free sequential-MDL codelength of a multinomial; gammaln via `math.lgamma`, numpy-only). The KT COMPLEXITY PENALTY (larger alphabet for the joint -> 441 vs 21) is what makes K_comp ALGORITHMICALLY DISTINCT from the plug-in MI (which has no complexity penalty and overestimates coupling for sparse pairs). REUSE each family's saved matrix; sequence reweighting (80%-id, deterministic) RECOMPUTED from the matrix via the locked `reweight()` (reproduces the saved weights; NOT an MIp recompute) so K_MI and K_comp differ ONLY in PARADIGM, not preprocessing.
  - EXPLICITLY EXCLUDED as a convergence partner: DCA / inverse-covariance / any direct-vs-indirect SPARSIFIER (Pearlian; corpus-critiqued). May return LATER as a separate, non-adjudicating Pearlian-contrast diagnostic, NOT here.

**(c) CONVERGENCE STATISTIC (both families PF13354 + PF00026; thresholds fixed here).**
  - (i) Spearman(K_MI, K_comp) over eligible pairs (|i-j| >= 5) AND long-range (|i-j| >= 12).
  - (ii) top-L edge OVERLAP (Jaccard) of the top-L pairs by K_MI vs the top-L by K_comp (L = #mapped positions, the pilot-A convention).
  - (iii) SUBSTRATE-INFORMATIVE: contact precision of the CONSENSUS edges (in BOTH top-L sets) vs each estimator's top-L ALONE.
  - (iv) CONFOUND control: the convergence must SURVIVE partialling pair conservation-product (cons_i * cons_j) AND burial-product (burial_i * burial_j) -- partial Spearman(K_MI, K_comp | cons-product, burial-product) -- OR hold on the long-range split. Else it is the trivial "agree on conserved / buried pairs" null (the Sec-2 homogeneous-family trap).

**(d) R2-EDGE PASS iff ALL (keying on holding for BOTH families).**
  - Spearman(K_MI, K_comp) >= 0.5 on the LONG-RANGE split; AND
  - consensus contact precision >= each estimator's top-L alone; AND
  - convergence SURVIVES the conservation / burial control (partial holds, or long-range holds).

**(e) CONTACTS = one sparse cut of the coupling field -- the falsifiable ANCHOR, NOT its totality.** MIp-high non-contact pairs are a QUESTION for R1-edge (allostery / long-range coupling), NOT defined as noise here. Held at CIT's falsifiable tier (PDB contacts are the empirical anchor); NO unfalsifiable "indirect coupling is real" license is taken.

**PINS (Phase-2 run; numpy-only; reuse saved artifacts).** REUSE each family's saved matrix (`pilotS_{acc}_matrix.npy`) + the saved APC-MIp (`pilot_coupling_{acc}.npz`; NO MIp refetch / recompute). K_comp = KT stochastic-complexity codelength (Dirichlet-1/2 / Krichevsky-Trofimov), 21-symbol marginals + 441-symbol joint, on the deterministically-RECOMPUTED 80%-id reweighted effective counts; gammaln via `math.lgamma`. Eligible pairs |i-j| >= 5; long-range |i-j| >= 12; L = #mapped positions; contacts Cb-Cb < 8 A (Ca for Gly) from the locked PDB (`1djc:A` / `4y9w:A`); burial = HSExposureCB EXP_HSE_B_U; conservation = gap-excluded column entropy (negated). Standalone `scripts/r2_edge.py`; outputs -> `data/pfam/` (gitignored). NO locked-constant VALUE changed.

**(f) HARD STOPS.** TWO families; reuse saved matrices + MIp (no refetch / recompute MIp); numpy-only; DENSE estimators only (NO sparse / DCA); NO R1-edge / R3-edge; NO grid; NO family-list lock; nothing in `data/` committed. The Phase-1 pre-registration (this entry) is committed + pushed BEFORE the Phase-2 run (sec 8). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 1 RESULT: R2-EDGE PASSES on BOTH families (the dense paradigms converge; confound control STRENGTHENS it)

**What this is.** A dated, append-only RESULT record for the R2-edge premise pre-registered immediately above. Apparatus = `scripts/r2_edge.py` (reuses `run_d2_family2.py`'s locked method; K_comp = KT/Krichevsky-Trofimov stochastic-complexity codelength, joint-vs-independent, on the deterministically-recomputed 80%-id reweighted effective counts; `math.lgamma`, numpy-only; APC-MIp REUSED from the saved `.npz`, no recompute). VALIDATION: K_comp returns ~+1674 bits for a perfectly-coupled synthetic pair and ~-27 bits for an independent pair (the KT complexity penalty on the 441-symbol joint drives independent pairs to ~0/negative -- the algorithmic distinction from the plug-in MI). No pin / constant VALUE changed; nothing in `data/` committed (gitignored). NO decision past the premise is taken here.

**(a) RESULT TABLE (thresholds from (c)/(d) above).**
  | metric | PF13354 (1djc:A) | PF00026 (4y9w:A) |
  | --- | --- | --- |
  | (i) Spearman(K_MI,K_comp) all \|i-j\|>=5 | +0.586 | +0.772 |
  | (i) Spearman LONG-RANGE \|i-j\|>=12 (PASS >= 0.5) | **+0.542** | **+0.745** |
  | (ii) top-L Jaccard | 0.146 (62/L) | 0.236 (112/L) |
  | (iii) contact precision K_MI / K_comp / CONSENSUS (base) | 0.131 / 0.086 / **0.242** (0.022) | 0.160 / 0.150 / **0.214** (0.019) |
  | (iv) confound control raw -> partial(\|cons-prod,burial-prod) | +0.583 -> **+0.651** | +0.775 -> **+0.852** |
  | (iv) long-range raw -> partial | +0.540 -> +0.610 | +0.748 -> +0.833 |
  | R2-EDGE PASS (family) | **YES** | **YES** |

**(b) VERDICT = R2-EDGE PASS (both families).** All three (d) conditions hold on BOTH PF13354 and PF00026: (1) long-range Spearman >= 0.5; (2) consensus contact precision >= each estimator alone; (3) survives the conservation/burial control.

**(c) READING.**
  - The two genuinely-distinct DENSE paradigms (Shannon plug-in MIp vs algorithmic KT/MDL coupling) CONVERGE -- long-range Spearman 0.54 (PF13354) / 0.75 (PF00026), both clearing 0.5.
  - The convergence is NOT a confound artifact: partialling out pair conservation-product AND burial-product does not merely preserve it, it STRENGTHENS it (+0.583 -> +0.651; +0.775 -> +0.852). So the agreement is on genuine coupling structure, not the trivial "agree on conserved / buried pairs" null (the Sec-2 homogeneous-family trap is cleared).
  - SUBSTRATE-INFORMATIVE: the CONSENSUS edges (top-L in BOTH) predict PDB contacts BETTER than either estimator alone (0.242 vs 0.131/0.086; 0.214 vs 0.160/0.150; ~11x base) -- cross-paradigm agreement isolates real structure.

**(d) CAVEATS (honest).** (i) top-L Jaccard is MODEST (0.15 / 0.24) -- the estimators rank the full edge set differently in detail; the Spearman reflects BROAD agreement, not near-identical top-L (expected + desirable for genuinely distinct estimators -- near-perfect overlap would mean they are the same method; the consensus-precision win shows the agreement that exists is substantive). (ii) TWO families, no grid, no lock -- a premise check, not the full R2-edge. (iii) DCA stayed EXCLUDED (Pearlian); MIp-high non-contact pairs logged as an R1-edge question, NOT noise.

**Discipline.** RESULT record + apparatus commit (`scripts/r2_edge.py`); the Phase-1 pre-registration (above) was committed + pushed BEFORE this run (sec 8). NO pin / constant VALUE changed; numpy-only; DENSE estimators only (NO DCA); NO R1/R3-edge, NO grid, NO family-list lock; NO decision past the premise. Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 2: edge-w FORMAL-ADMISSIBILITY check (extension-not-fork) PRE-REGISTRATION

**What this is.** A VERIFICATION (not a hypothesis test) that the edge-valued `w` = CIT-per-symbol-`w`-on-the-JOINT-pair-symbol (over the 21x21 = 441 product alphabet; ref `design/relational_edge_w.md` Sec 1/4/5/9) is an EXTENSION of the existing H_w / I_w machinery, NOT a fork. PRE-FIXED pass criteria (below), evaluated on BOTH pilot families (PF13354 / 1djc:A, PF00026 / 4y9w:A) and BOTH dense estimators (K_MI = APC-MIp; K_comp = KT/MDL codelength) unless a check is estimator-independent. DESIGN + dated amendment; criteria FIXED here; committed + pushed BEFORE the Phase-2 run (sec 8). Nothing in `data/` committed.

**KEY RISK PROBED.** Pair-features OVERLAP: each position appears in L-1 pairs, so the pair representation is NOT a partition of the stream. The induced-weights commitments must SURVIVE that overlap; where one fails, that failure is a NAMED finding about where the overlapping representation strains the formalism (informs whether edge-`w` needs an accounting normalization vs is a clean extension).

**PROVISIONAL induced edge-`w` (for these checks ONLY).** `w(i,j) = sigma(beta * z(C_hat(i,j)))`, beta = 4.0 (LOCKED), `z` = standardize the edge estimator C_hat over eligible pairs (|i-j| >= 5), sigma = logistic. A full edge-ABLATION (the rho step) is a SEPARATE later step and is NOT needed to test admissibility of the FORMALISM; this provisional map is the minimal `C_hat -> w` needed to exercise boundedness / monotonicity.

**CHECKS + PRE-FIXED PASS CRITERIA (both families; both estimators unless noted).**
  - (A) BOUNDEDNESS: every provisional edge-`w` lies in [0,1]. PASS = exact (numerically verified).
  - (B) SHANNON RECOVERY (the generalization license; ESTIMATOR-INDEPENDENT -- it tests the H_w/I_w machinery on the pair joint distribution, not K). On a pair's joint-symbol column, with `w == 1`: H_w == H(joint) AND I_w(X_i;X_j) == I(X_i;X_j). PASS = |H_w - H| < 1e-9 AND |I_w - I| < 1e-9 (bit-level), over a sample of pairs spanning high- and low-coupling.
  - (C) COARSE-GRAINING CONSISTENCY (the substantive check of the overlapping representation). Remap the 20 AA to the Dayhoff-6 classes {C},{AGPST},{DENQ},{RHK},{ILMV},{FWY} (gap stays its OWN class -> 7 symbols), RECOMPUTE the estimator on the coarse alphabet (a LEGITIMATE recompute -- a DIFFERENT alphabet, NOT the locked full-alphabet MIp), and check rank-consistency vs the full-alphabet estimator over eligible pairs. PASS = Spearman >= 0.7 (report the value; < 0.7 = an alphabet-FRAGILITY finding, recorded honestly).
  - (D) MONOTONICITY: the provisional `w` is monotone in C_hat (sigma is monotone) -> ZERO rank inversions in the C_hat -> w map. PASS = 0 inversions (Spearman(C_hat, w) == 1).
  - (E) INTERPRETIVE / RELABEL INVARIANCE (domain-translation admissibility + an R3 interpretive pre-check). Permute amino acids WITHIN Dayhoff/BLOSUM-equivalence classes; the COUNT-based estimators must be EXACTLY invariant. PASS = Spearman == 1.0 (within 1e-9). NOTE: trivially-exact here is a POSITIVE result (the estimator is STRUCTURAL, not symbolic) and PRE-VALIDATES R3's interpretive arm (||Delta w|| ~ 0 under a meaning-preserving relabel).
  - (F) RECURSIVE / RESAMPLING STABILITY: rank-stability of the edge estimator across 100 ORTHOLOG bootstraps (resample sequences with replacement, RE-reweight, RE-compute the estimator -- a legitimate recompute on a DIFFERENT sample, NOT the locked full-sample baseline). PASS = mean Spearman(bootstrap, full) >= 0.8 over eligible pairs.

**VERDICT RULE.** Edge-`w` is ADMISSIBLE-AS-EXTENSION iff A-F ALL pass (both families, both estimators where applicable). Any fail is a NAMED finding locating where the overlapping pair-representation strains the formalism (-> does edge-`w` need an accounting normalization, or is it a clean extension?). This is a VERIFICATION with pre-fixed criteria, not a falsifiable hypothesis test.

**PINS (Phase-2 run; numpy + `math.lgamma` only).** REUSE each family's saved matrix (`pilotS_{acc}_matrix.npy`) + the saved full-alphabet APC-MIp baseline (`pilot_coupling_{acc}.npz`; NEVER recompute the locked full-alphabet MIp). RECOMPUTES are confined to: the COARSE alphabet (C), the RELABELED alphabet (E), and the BOOTSTRAP resamples (F) -- each a different alphabet or a different sample, NOT the locked baseline. K_comp = KT codelength (Dirichlet-1/2), reweighting via the locked `reweight()`. Dayhoff-6 + gap = 7 coarse symbols. Standalone `scripts/admissibility_edge.py`; outputs -> `data/pfam/` (gitignored). NO locked-constant VALUE changed.

**Discipline.** DESIGN + dated amendment; criteria LOCKED HERE pre-computation; committed + pushed BEFORE the Phase-2 run (sec 8). TWO families; reuse matrices + the locked full-alphabet MIp baseline (recompute ONLY for the coarse/relabel alphabets + the bootstrap resamples); numpy-only; NO DCA; NO edge-ablation/R1/R3-edge build, NO grid, NO family-list lock. Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 2 RESULT: edge-w ADMISSIBLE-AS-EXTENSION (A-F all pass; adversarially verified; two formal follow-ups flagged)

**What this is.** A dated, append-only RESULT record for the edge-w formal-admissibility check pre-registered immediately above. Apparatus = `scripts/admissibility_edge.py` (numpy + `math.lgamma`; reuses saved matrices + the saved full-alphabet MIp baseline; recompute confined to the coarse/relabel alphabets + the bootstrap resamples). All A-F results were ADVERSARIALLY VERIFIED by an independent multi-agent workflow (6 from-scratch verifiers + a synthesis critic); every reported number was reproduced by clean-room re-derivation. No pin / constant VALUE changed; nothing in `data/` committed (gitignored).

**(a) RESULT (both families, both estimators K_MI = APC-MIp, K_comp = KT/MDL).**
  | check | criterion | PF13354 (K_MI / K_comp) | PF00026 (K_MI / K_comp) |
  | --- | --- | --- | --- |
  | A boundedness | w in [0,1] exact | PASS / PASS | PASS / PASS |
  | B Shannon recovery (w=1) | \|dH\|,\|dI\| < 1e-9 | 0.0 / 0.0 | 0.0 / 0.0 |
  | C coarse-grain (Dayhoff-6) | Spearman >= 0.7 | 0.966 / 0.865 | 0.980 / 0.845 |
  | D monotonicity | 0 inversions | PASS / PASS | PASS / PASS |
  | E relabel-invariance | == 1.0 (1e-9) | 1.000 / 1.000 | 1.000 / 1.000 |
  | F bootstrap stability (100x) | mean Spearman >= 0.8 | 0.993 / 0.991 | 0.993 / 0.986 |

**(b) VERDICT = edge-`w` ADMISSIBLE-AS-EXTENSION.** A-F ALL pass on both families and both estimators. The pre-registered KEY RISK (pair-features OVERLAP -- each position in L-1 pairs) did NOT break boundedness, Shannon-recovery, coarse-grain stability, monotonicity, relabel-invariance, or resampling-stability. Edge-w = CIT-on-the-joint-pair-symbol is a clean EXTENSION of the H_w / I_w machinery, NOT a fork, for the formal properties tested.

**(c) ADVERSARIAL VERIFICATION (6 verifiers, all CONFIRM; every number reproduced clean-room).** `estimators()` APC-MIp is BIT-EXACT to the saved baseline (max abs diff = 0.0); the matmul-shared joint-count trick matches `np.add.at` to <= 5e-13; K_comp matches `scripts/r2_edge.py` to 1.5e-11 (float-ordering only). No threshold was weakened (C is `>= 0.7`, F is `>= 0.8`); no REFUTE; no blocking bug.

**(d) HONEST CAVEATS the verification surfaced (recorded, NOT folded into the PASS).**
  - (i) Check B is ALGEBRAICALLY TAUTOLOGICAL as-coded (the inline H_w/I_w hardcode w via `np.ones_like`, so 0.0 is guaranteed by construction; it does NOT exercise the canonical `cit/information.py` `coherence_weighted_*` routines). Shannon recovery IS real -- the verifier confirmed it AGAINST the canonical functions (|dH|=0, |dI| <= 1.1e-16) -- but that guarantee comes from the independent check, not from B's code path. FOLLOW-UP: rewire B through `cit/information.py`.
  - (ii) The I_w WEIGHTING CONVENTION is invisible at w=1: edge-w is stated over the 441 joint product-alphabet symbols, but canonical I_w weights the 21-symbol source marginal; these diverge off-boundary and coincide only at w=1. So `H_w`-over-the-joint-pair-symbol is confirmed a clean extension, but WHERE the edge weight attaches in I_w(X_i;X_j) is an OPEN formal point (not a blocker). FOLLOW-UP: pin the I_w-on-edges convention explicitly.
  - (iii) The pre-registered KEY RISK (overlap -> not a partition -> possible accounting normalization) is NOT actually PROBED by A-F (all six treat eligible pairs as a flat independent list). Admissibility-as-extension is established for the formal properties tested; the edge-overlap / partition-of-unity ACCOUNTING is the next adjudication, LEFT OPEN. FOLLOW-UP: a partition-of-unity / overlap-accounting check.
  - (iv) PIN literal deviation (minor, DEFENSIBLE): the script recomputes the full-alphabet MIp and uses it as the E/F reference (the pin says reuse the saved baseline). Adjudicated NON-substantive -- the recompute is BIT-EXACT to the saved array (diff 0.0), A/C/D + the K_MI baseline use the SAVED array, the saved npz is untouched, and E re-verified DIRECTLY against the saved MIp still holds to 3e-16. Plus one harmless dead line (`admissibility_edge.py:125`, an unused inv proxy; D correctly uses `|Spearman-1| < 1e-9`).

**Discipline.** RESULT record + apparatus commit (`scripts/admissibility_edge.py`, committed as-verified; the dead line + the B-rewire are recorded follow-ups, deliberately NOT applied here). The Phase-1 pre-registration (above) was committed + pushed BEFORE this run (sec 8). NO pin / constant VALUE changed; numpy-only; NO DCA; NO edge-ablation / R1 / R3-edge build, NO grid, NO family-list lock; NO decision past admissibility. Nothing in `data/` committed (gitignored). Append-only, ASCII.



### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 3: RETRACT the joint-symbol edge-w object + the step-2 admissibility PASS; INSTALL the relational coherence-weighted functional (I_w_rel); PRE-REGISTER the stress-test (S1-S8)

**What this is.** A dated, append-only RETRACTION + correction + pre-registration. It (i) RETRACTS the prior edge-w object (w on the 441-symbol joint pair-symbol) AND the step-2 formal-admissibility PASS recorded above; (ii) installs the corrected RELATIONAL coherence-weighted functional; (iii) pre-registers an adversarial stress-test S1-S8 with pass criteria FIXED HERE, to be run only AFTER this amendment is committed + pushed (sec 8). Ref `design/relational_edge_w.md` Sec 4 (corrected) + `design/relational_formalism.md` (full derivation with arguments). Nothing in `data/` committed.

**(i) RETRACTION (prior edge-w object + step-2 admissibility PASS).** The prior definition -- w(i,j) = the CIT per-symbol weight on the JOINT pair-symbol (x_i,x_j) over the 21x21 = 441 product alphabet, "an EXTENSION not a fork" -- is WRONG and is RETRACTED, and with it the step-2 admissibility PASS (it verified the wrong object). FOUR reasons:
  1. It COLLAPSES to single-source node-w on a merged 441-symbol node. It weights joint symbol-VALUES, not the RELATION. Not relational (violates P2). It does NOT vanish at independence (the relational signature it lacks).
  2. Canonical I_w (`cit/information.py:coherence_weighted_mutual_information`) weights the SOURCE MARGINAL: `contribution = pxy * w[:,None]`, w length n_x = 21. A 441-length joint weight is not even shape-admissible -- it fails `_check_weights`.
  3. The source corpus defines w ONLY single-source (w: X -> [0,1]) and is SILENT on edge/pair weighting. So this is a real FORMAL GAP, not a recast.
  4. The step-2 admissibility "PASS" was FALSE COMFORT: check B hardcoded `np.ones_like` (an x*1 == x tautology that never called the canonical routines), E/F referenced same-code recompute (not the saved baseline), and the pre-registered KEY RISK (pair overlap / non-partition) was never probed.

**(ii) CORRECTED OBJECT (the relational coherence-weighted functional).** Positions 1..L are discrete variables X_1..X_L over alphabet A (|A| = 21). Edges = the DENSE complete graph E = {(i,j): i < j} (no sparsification -- P3). I(X_i; X_j) is the RAW pairwise mutual information (computed via canonical `cit/information.py` at w = ones). w(i,j) in [0,1] is the edge weight.
  - RELATIONAL coherence-weighted information:  I_w_rel = sum_{(i,j) in E} w(i,j) * I(X_i; X_j).
  - SHANNON RECOVERY (a REAL reduction): w == 1 => I_w_rel = sum I(X_i; X_j) = total pairwise coupling on the graph.
  - BOUNDED relational coherence: C_rel = I_w_rel / sum_{(i,j) in E} I(X_i; X_j) in [0,1], = 1 at w == 1.
  - NODE-INDUCED coherence: c_i = sum_{j != i} w(i,j) * I(X_i; X_j).
  - OVERLAP / NON-PARTITION accounting -- HANDSHAKE IDENTITY: sum_i c_i = 2 * I_w_rel (each edge sits in exactly two node-loads). This is the bookkeeping that makes the non-partition pair-representation consistent.
  - INDUCTION (formal/induced split): edge proxy K: stream -> Chat(i,j) (K_MI = APC-MIp, or K_comp); edge relevance rho(i,j) (marginal-relative); w(i,j) = sigma(beta * z(rho(i,j))), beta = 4.0 (LOCKED). The FORMAL object is built on RAW I(X_i; X_j) (clean Shannon boundary); w is INDUCED from MARGINAL-RELATIVE proxies -- the SAME split single-source CIT already uses. Do not conflate.
  - RECURSIVE / MULTI-SCALE: pairwise is order k = 2 (FIRST ORDER). General: hyperedge weights w(S) on k-subsets weight order-k interaction; C_rel_k = sum_{|S| = k} w(S) TC(S) / sum TC(S) (TC = total correlation). Build k = 2 now; higher-order deferred.
  - OPEN CHOICES (PENDING Benjamin -- the stress-test INFORMS, does NOT decide): (c1) normalizer for C_rel (sum I [recommended] vs |E| vs max); (c3) base (RAW I [recommended -- clean boundary, >= 0] vs MIp [beyond-marginal, can be negative]); (c-merge) node-merge coarse-graining rule (merge i,j: drop edge (i,j), union other edges, combine weights by coupling-weighted average).

**(iii) PRE-REGISTERED STRESS-TEST (S1-S8; pass criteria FIXED HERE).** Standalone `scripts/relational_formalism_test.py`; outputs -> `data/pfam/` (gitignored). Both families (PF13354, PF00026); eligible pairs |i-j| >= 5; reuse the saved matrices + saved MIp. DISCIPLINE (carry the step-2 lessons): I(X_i; X_j) computed via CANONICAL `cit/information.py` (NO hardcoded-ones reimplementation); test at w != 1 (not only w == 1); any "saved" comparison referenced against the saved npz baseline (not same-code recompute); no dead code.
  - S1 SHANNON RECOVERY (real, non-tautological): build I_w_rel from I(X_i; X_j) via canonical `coherence_weighted_mutual_information(joint_ij, ones21)`. At w == 1: |I_w_rel - sum I| < 1e-9. CONTROL: at random w in [0,1] AND at induced w: I_w_rel == hand-sum sum w(i,j) I(i,j) (< 1e-9) AND I_w_rel != sum I. PASS = recovery exact AND non-trivial weight response.
  - S2 NON-COLLAPSE (alpha != beta; the relational signature): for ~independent pairs (I ~ 0) the alpha edge-contribution w*I ~ 0 regardless of marginals, while the beta quantity (canonical single-source H_w on the 441-joint merged node) ~ H(X_i) + H(X_j) >> 0. Report both for 3 low-I and 3 high-I pairs. PASS = alpha ~ 0 at independence while beta >> 0 (demonstrates alpha weights the RELATION; beta = the retracted object does not).
  - S3 HANDSHAKE / OVERLAP (the previously-unprobed risk): compute all c_i and I_w_rel; |sum_i c_i - 2 I_w_rel| < 1e-9 at w == 1, random w, induced w. PASS = exact at all three.
  - S4 MONOTONICITY: perturb a single w(i,j) up by delta; assert I_w_rel increases by exactly delta * I(i,j) (>= 0); zero inversions across a sample. PASS = analytic match.
  - S5 BOUNDEDNESS: C_rel in [0,1] for w == 1, random w, induced w; == 1 at w == 1. PASS = exact.
  - S6 RELABEL / DOMAIN-TRANSLATION INVARIANCE: at FIXED w, permute amino acids within Dayhoff/BLOSUM-equivalence classes, recompute I(X_i; X_j), assert I_w_rel invariant (< 1e-9). PASS = invariant.
  - S7 BASE-CHOICE EVIDENCE (informs c3, NO pass/fail): I_w_rel at w == 1 under RAW-I base (= sum I, all >= 0) vs MIp base (= sum MIp, may be negative); report the count of negative-MIp edges.
  - S8 NORMALIZER EVIDENCE (informs c1, NO pass/fail): C_rel under the three normalizers (sum I, |E|, max) at induced w, both families.

**VERDICT RULE.** The corrected relational functional is an ADMISSIBLE RELATIONAL OBJECT -- the formal GAP CLOSED, overlap ACCOUNTED -- iff S1-S6 ALL pass on both families. S7/S8 are EVIDENCE for Benjamin's c1/c3 rulings, NOT pass/fail. No decision on the open choices (Benjamin rules); no further build; no commits past this Phase-1 pre-registration.

**Discipline.** DESIGN + dated amendment; criteria LOCKED HERE pre-computation; committed + pushed BEFORE the Phase-2 stress-test run (sec 8). TWO families; reuse saved matrices/MIp; canonical `cit/information.py` for I (NO hardcoded-ones reimplementation); numpy + `math.lgamma` only. NO DCA; NO edge-ablation / R1 / R3-edge build, NO grid, NO family-list lock; NO decision past the gap-closure verdict. Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 3 RESULT: relational functional I_w_rel is an ADMISSIBLE RELATIONAL OBJECT (S1-S6 PASS both families; the formal GAP is CLOSED)

**What this is.** A dated, append-only RESULT record for the relational-functional stress-test pre-registered immediately above. Apparatus = `scripts/relational_formalism_test.py` (numpy + `math.lgamma`; reuses each family's saved matrix + saved APC-MIp; every raw pairwise I(X_i; X_j) is taken from the CANONICAL `cit/information.py` routines at w = ones -- NO hardcoded-ones reimplementation, the step-2 tautology trap; tested at w != 1). Both pilot families (PF13354, PF00026); eligible pairs |i-j| >= 5; raw-I base. NO pin / constant VALUE changed; nothing in `data/` committed (gitignored).

**(a) RESULT (both families).**
  | check | criterion | PF13354 | PF00026 |
  | --- | --- | --- | --- |
  | S1 Shannon recovery + weight response | \|I_w_rel - sum I\| < 1e-9 at w=1; hand-sum match; != sum I off-boundary | PASS (0.0; resp 5722/4878 bits) | PASS (3.6e-12; resp 7498/6064) |
  | S2 non-collapse (alpha vs merged-node beta) | low-I alpha/beta < 0.20 AND beta > 1 bit | PASS (low alpha/beta 0.001-0.002, beta 1.5-1.8b; high 0.21-0.30) | PASS (low 0.001, beta 1.3-2.0b; high 0.19-0.20) |
  | S3 handshake / overlap (sum_i c_i = 2 I_w_rel) | < 1e-9 at w=1, random w, induced w | PASS (<= 1.8e-12) | PASS (<= 7.3e-12) |
  | S4 monotonicity | single-w perturb = exactly delta*I, 0 inversions | PASS (err 8.8e-13, 0/500) | PASS (err 1.6e-12, 0/500) |
  | S5 boundedness | C_rel in [0,1], = 1 at w=1 | PASS (1.000000/0.500/0.574) | PASS (1.000000/0.499/0.595) |
  | S6 relabel / domain-translation invariance | \|dI_w_rel\| < 1e-9 within Dayhoff | PASS (0.0) | PASS (0.0) |

**(b) VERDICT = GAP CLOSED (both families).** S1-S6 ALL pass. The corrected functional is an ADMISSIBLE RELATIONAL OBJECT: (i) Shannon recovery is REAL -- exercised through the canonical `coherence_weighted_*` routines (NOT a hardcoded-ones tautology), AND the functional genuinely RESPONDS to w (I_w_rel - sum I = 4878-7498 bits off-boundary), the two senses the retracted step-2 PASS failed; (ii) it WEIGHTS THE RELATION -- the relational contribution alpha = w*I ~ 0 at independence (alpha/beta ~ 0.001) where the RETRACTED merged-node object beta = H(X_i,X_j) stays large (1.3-2.0 bits), exactly the property the old object LACKED; (iii) the previously-UNPROBED pair-overlap is closed EXACTLY by the handshake sum_i c_i = 2 I_w_rel (residual <= 7e-12 at three distinct weight fields). The formal GAP named in the step-3 retraction is CLOSED on the CORRECT (relational) object.

**(c) EVIDENCE for Benjamin's open rulings (S7/S8; NO pass/fail).**
  - c3 (BASE): sum raw-I >= 0 (11440 bits PF13354 / 14961 bits PF00026). sum MIp is NEGATIVE (-300 / -438 bits) with ~60% of eligible edges MIp < 0 (17671/29646; 28446/47278). An MIp base would push C_rel OUTSIDE [0,1] -> EVIDENCE FAVORS the recommended RAW-I base (clean classical boundary).
  - c1 (NORMALIZER): C_rel under sum-I = 0.574 / 0.595 (clean "fraction of coupling retained", in [0,1]); under /|E| = 0.221 / 0.188 bits/edge; under /max-I ~ 5114 / 7643 (not in [0,1]) -> EVIDENCE FAVORS the recommended sum-I normalizer.

**(d) OPEN (NOT decided here).** c1 / c3 / c-merge are Benjamin's rulings (the stress-test INFORMS, does not decide). The next relational component (R1-edge / M5-edge / graded R3-edge / K_pred) is Benjamin's call. This admissibility is established on the CORRECTED relational object and REPLACES the retracted step-2 PASS.

**Discipline.** RESULT record + apparatus commit (`scripts/relational_formalism_test.py`). The Phase-1 pre-registration (above) was committed + pushed BEFORE this run (sec 8, HEAD 017a7e4). NO pin / constant VALUE changed; numpy + `math.lgamma` only; canonical `cit/information.py` for I; NO DCA; NO edge-ablation / R1 / R3-edge build, NO grid, NO family-list lock; NO decision past gap-closure. Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 4: c3/c1 RULED (raw-I base + base/weight-separation principle; c3-gamma RETRACTED) + R1-EDGE (coupling persistence) PRE-REGISTRATION

**What this is.** A dated, append-only amendment that (i) records Benjamin's c3/c1 rulings on the relational functional + the governing base/weight-separation principle (and the c3-gamma retraction); (ii) PRE-REGISTERS R1-EDGE -- the PRIMARY cross-domain signature (does estimator-induced edge-w predict phylogeny-corrected coupling PERSISTENCE) -- with thresholds FIXED HERE, to be run only AFTER this amendment is committed + pushed (sec 8). Ref `design/relational_formalism.md` Sec 7 + `design/relational_edge_w.md` P7 / Sec 4. Nothing in `data/` committed.

**(i) c3 RULED -- BASE = RAW I(X_i; X_j), NOT beyond-marginal MIp.** GOVERNING PRINCIPLE (base/weight separation; recorded as foundation P7): CIT places RAW INFORMATION in the functional base and COHERENCE in w. Single-source H_w = sum p(x) w(x) [-log p(x)] puts raw surprisal in the base, coherence in w; the relational object mirrors this -- base = raw I(X_i; X_j), coherence (beyond-marginal AND beyond-background) lives in w(i,j), induced from the estimators (K_MI = APC-MIp, K_comp). RATIONALE: (a) raw MI is ALREADY beyond-marginal -- I = 0 at independence regardless of the columns' marginals (a conserved-but-independent pair scores ~ 0; S2 confirmed), so the corpus's beyond-marginal commitment is met by MI in the base; (b) APC's ADDITIONAL beyond-BACKGROUND step (subtract phylogenetic/background coupling) is mildly PEARLIAN (a soft direct-vs-indirect move) and belongs in w via the estimators, NEVER in the base -- a base transform double-counts background with w, is less P3-dense, and breaks the single-source parallel; (c) c3-gamma (a non-negative-beyond-background base, e.g. max(MIp, 0)) is RETRACTED as a category error for the same reasons, and the MIp base also breaks boundedness empirically (S7: ~60% of edges MIp < 0, sum MIp < 0 -> C_rel leaves [0,1]).

**(i) c1 RULED -- NORMALIZER for C_rel = sum I.** The only choice giving C_rel in [0,1] (S5/S8) and the natural partner of the raw base ("fraction of the graph's coupling retained"). **c-merge** (node-merge coarse-grain rule) DEFERRED until coarse-graining is exercised.

**(ii) R1-EDGE PRE-REGISTRATION (thresholds FIXED HERE).** Standalone `scripts/r1_edge.py`; outputs -> `data/pfam/` (gitignored). Both families (PF13354, PF00026); eligible pairs |i-j| >= 5, long-range |i-j| >= 12. Reuse the saved matrices (`pilotS_{acc}_matrix.npy`) + saved whole-set APC-MIp (`pilot_coupling_{acc}.npz["MIp"]`) + saved whole-set K_comp (`r2_edge_{acc}.npz["K_comp"]`) + the fixed family tree (`iq_{acc}.treefile`) + burial via the locked `map_pdb` (PDB `1djc`/`4y9w`). Raw MI strictly via canonical `cit/information.py`; numpy + `math.lgamma` only; NO MIp/K_comp recompute.
  - GOAL: does estimator-induced edge-w predict PHYLOGENY-CORRECTED coupling PERSISTENCE -- a coupling maintained as constraint while the residues turn over (conservation-INDEPENDENT)? The Adaptive-Realism cash-out; the persistence measure is the substrate's evolutionary readout (a comparison-compression per Meta-Coherence sec 6.4, NOT an oracle).
  - PERSISTENCE MEASURE (phylogeny-decorrelated): cut the fixed tree into K = 8 approximately-balanced, phylogenetically-INDEPENDENT subclades; within each subclade reweight (80%-id, WITHIN-clade, the locked `reweight`) and compute RAW MI per eligible pair via canonical `cit/information.py`. persistence(i,j) = MEDIAN across the subclades of the within-subclade raw MI (a coupling that PERSISTS recurs across independent lineages -> high median; a single-clade phylo artifact -> low median). PINNED: K = 8, the tree-cut rule (below), the median statistic. Cross-clade variance reported as secondary.
  - TREE-CUT RULE (pinned, deterministic, no RNG): use `iq_{acc}.treefile` as the fixed tree; midpoint-root it (`Bio.Phylo` `root_at_midpoint`). Greedy top-down K-partition: groups = {root}; while |groups| < K, select the group with the MOST terminal leaves that has >= 2 child clades (ties broken by the smallest member matrix-row index) and REPLACE it with its direct child clades; stop at K = 8. Map each subclade to matrix rows by leaf name (leaf `seqN` / `sN` -> row N; both pilot trees carry all 2000 leaves 1:1 with the matrix rows). Any subclade with < 25 mapped rows is merged into the nearest remaining subclade (by tree distance) so every retained subclade is MI-estimable; report the realized subclade count K_eff and sizes (expected K_eff = 8).
  - NON-CIRCULARITY: edge-w is induced from WHOLE-SET APC-MIp / K_comp (phylo-confounded); persistence is cross-INDEPENDENT-subclade consistency (phylo-decorrelated). They differ EXACTLY on the phylo confound, so a high-w edge that ALSO persists is real constraint, not phylo shadow.
  - STATISTIC (R1 SPEC GUARD = PER-ESTIMATOR validity, NOT cross-estimator agreement): for EACH of K_MI-induced w and K_comp-induced w (induced w = sigma(beta * z(rho)), beta = 4.0, z = standardize rho over eligible pairs), compute Spearman(w, persistence) over all eligible pairs AND long-range, AND the PARTIAL controlling conservation-product AND burial-product (precision-matrix partial, as R2-edge), the partial taken over mapped eligible pairs with conservation-product and burial-product defined (the R2-edge confound subset). Bootstrap CI by resampling PAIRS with replacement (B = 1000, seed 0; 95% percentile CI 2.5/97.5).
  - R1-EDGE PASS (per estimator, per family) iff the LONG-RANGE partial-Spearman(w, persistence | cons-prod, burial-prod) > 0 with its bootstrap 95% CI excluding 0; the all-eligible partial + raw Spearmans reported alongside (emphasis long-range). CONTEXT number reported: Spearman(whole-set MIp, persistence) over eligible + long-range -- to show the phylo correction BITES (whole-set MIp is the phylo-confounded coupling; if persistence merely echoed it, the correction would be vacuous).
  - VERDICT RULE: R1-EDGE supports the PRIMARY signature on a (family, estimator) iff its PASS holds; aggregate PER-ESTIMATOR across families. Per the spec guard this is PER-ESTIMATOR functional validity (each w predicts persistence) AGGREGATED, NOT cross-estimator agreement on which edges persist.

**Discipline.** DESIGN + dated amendment; criteria LOCKED HERE pre-computation; committed + pushed BEFORE the Phase-2 run (sec 8). TWO families; reuse saved matrices / MIp / K_comp / trees; raw MI via canonical `cit/information.py`; numpy + `math.lgamma` only. Persistence is phylo-DECORRELATED (independent subclades), NOT a bootstrap resample. NO DCA; NO grid, NO family-list lock; NO decision past the R1-edge verdict. `beta = 4.0` carried (no new locked-constant VALUE). Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 5 / R1-EDGE RESULT: coupling-persistence PASS (pre-registered) + adversarial-verification upgrades (product-leak / CI / complementary arms)

**What this is.** Dated, append-only RESULT for the R1-edge pre-registration (step 4, above). Apparatus `scripts/r1_edge.py` (numpy + `math.lgamma`; raw MI per pair via CANONICAL `cit/information.py`; reuses saved matrices + saved APC-MIp/K_comp + the fixed iq trees + HSExposureCB burial). ADVERSARIALLY VERIFIED by a 6-agent workflow: every reported number reproduced bit-exact via independent clean-room paths (persistence to 5e-16; partial-Spearman to 5 dp; tree-cut/merge mechanics identical). The PASS survives every stress test; recorded with BOTH the pre-registered statistics AND three honest upgrades (NOT a silent swap; per sec 8). No pin/constant VALUE changed; nothing in `data/` committed.

**(a) PRE-REGISTERED RESULT (all 4 family x estimator cells PASS).** Long-range partial-Spearman(induced-w, persistence | conservation-PRODUCT, burial-PRODUCT) > 0 with pair-bootstrap 95% CI excluding 0: K_MI +0.454 / +0.417, K_comp +0.523 / +0.433 (PF13354 / PF00026). Context Spearman(whole-set MIp, persistence) long = +0.341 / +0.356 (well below 1.0 -> the phylo decorrelation BITES; persistence is not a re-measurement of the inducing estimator). Persistence = median over K=8 phylo-independent subclades of within-subclade raw MI (PF13354 K_eff=7, balanced; PF00026 K_eff=5, caterpillar tree with one 91% clade).

**(b) UPGRADE 1 -- the conservation-PRODUCT control LEAKS; the SEPARATED control is the default.** A pure conservation-product null-w (zero coupling information) PASSES the product control HARDER than the real coupling-w (+0.665 / +0.595 long), then COLLAPSES under a SEPARATED control (conservation_i, conservation_j, burial_i, burial_j as DISTINCT covariates -> +0.320 / +0.254). The REAL signal SURVIVES separated: K_MI +0.426 / +0.418, K_comp +0.567 / +0.477. So "survives conservation" via the product control certifies less than it appears; the SEPARATED control is the DEFAULT going forward. (Real w_mi is conservation-orthogonal -- upgrade 3 -- so the real pass is genuine; the product control merely under-suppresses by construction.)

**(c) UPGRADE 2 -- the pair-bootstrap CI is ~10x too tight; POSITION-BLOCK is the default.** Resampling PAIRS treats ~30-47k pairs as independent, but they are built from only L=248/312 positions, so the CI widths (~+-0.01) badly understate uncertainty. A POSITION-BLOCK bootstrap (resample positions; pair multiplicity cnt_i*cnt_j) widens the K_MI separated-control CI to ~[+0.38, +0.47] -- wider, but the lower bound still clears 0. The substantive evidence is the MAGNITUDE (+0.42..+0.57 long-range separated partial), NOT the CI. Position-block is the DEFAULT going forward.

**(d) UPGRADE 3 -- the two arms' weaknesses are COMPLEMENTARY; the convergence is the argument.** K_MI is conservation-CLEAN (Spearman(w_mi, cons-product) = +0.015 / +0.054 ~ 0) but MIp-CIRCULAR (w_mi = sigma(beta z(MIp)) is monotone in MIp, so its raw Spearman EQUALS the context number identically). K_comp is MI-INDEPENDENT (algorithmic compression coupling) but conservation-LOADED (Spearman(w_comp, cons-product) = +0.449 / +0.491), YET survives the separated control (+0.567 / +0.477). Their weaknesses do NOT overlap and BOTH clear the separated control -> the cross-paradigm CONVERGENCE is the argument, not either arm alone.

**(e) STATUS = pilot/calibration PASS, NOT a locked result.** The signal is genuine COUPLING (NOT the conservation-circularity that sank node-valued w -- w_mi is conservation-orthogonal), conservation-clean on K_MI, cross-paradigm-corroborated by K_comp. ONE real weakness remains -- generalization: PF13354's partition is clean (K_eff=7) but PF00026's is a degenerate caterpillar (K_eff=5, one 91% clade), so phylo-decorrelation rests on ~1.5 families. GATE before any R1-edge LOCK: replicate on a clean-tree THIRD family (pre-registered in the adjacent block). The upgrade numbers (b/c/d) come from the adversarial-verification reanalysis; the SEPARATED-control + POSITION-BLOCK statistics are implemented for the third-family run.

**Discipline.** RESULT record + apparatus commit (`scripts/r1_edge.py`; unused `rank` import removed). The step-4 R1 pre-registration was committed + pushed (`02c87f8`) BEFORE the run (sec 8). Pre-registered statistics AND the upgrades both recorded (no silent swap). NO pin/constant VALUE changed; numpy + `math.lgamma` only; canonical `cit/information.py` for I; NO DCA. Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 5 / clean-tree THIRD-FAMILY R1-EDGE replication PRE-REGISTRATION + LOCK

**What this is.** Dated, append-only PRE-REGISTRATION of the clean-tree third-family R1-edge replication, with the family/PDB/chain RESOLVED + LOCKED HERE by a deterministic outcome-independent selection (pre-computation), and the UPGRADED statistics (separated control + position-block bootstrap) FIXED as defaults. To be run only AFTER this is committed + pushed (sec 8). Apparatus `scripts/select_third_family.py` (selection) + `scripts/r1_edge.py` (run). Nothing in `data/` committed.

**(i) FAMILY SELECTION (deterministic, outcome-independent; LOCKED).** From candidate_pool.tsv, the lowest Pfam accession meeting ALL of: catalytic=YES, oversized=False, depth 1500+, NOT PF13354/PF00026, AND (g1) >= 150 match columns under the pinned `build_matrix` recipe; (g2) a clean single-domain PDB <= 2.5A x-ray (InterPro: ONLY this Pfam family on the whole structure, single domain fragment on the chosen chain); (g3) BALANCED tree -- the K=8 greedy cut (midpoint-rooted; subclades <25 merged into nearest by tree distance, the `r1_edge` rule) gives K_eff >= 6 with NO subclade > 40% of the 2000 seqs. Tree balance is a property of the BUILT tree (data-quality), NOT an R1 result; g3 is screened on the fast VeryFastTree tree and CONFIRMED on the pinned IQ tree for the winner. Pathological alignments (VeryFastTree ML build > 300s -> pinned-pipeline-incompatible) are a deterministic skip.
  LOCKED WINNER = **PF00348 (polyprenyl_synt; trans-prenyltransferase, all-alpha)**, PDB **8a7c:A @ 1.2 A**, L = 242 match columns; tree balance K_eff = 6, max_frac = 0.321, subclade sizes [148,199,266,296,450,641] -- IDENTICAL on the VeryFastTree and the confirming IQ tree. 27 candidates SKIPPED before it (full reasons in `data/pfam/third_family_lock.json`): 9 g1 cols<150 (PF00024/039/043/051/062/068/080/127/190); 1 pathological-tree timeout (PF00141 peroxidase, VeryFastTree ML > 300s); 2 g2 no-clean-PDB (PF00185, PF00251); 15 g3 tree-unbalanced (PF00162/180/182/199/206/215/221/224/245/264/285/295/303/305/342 -- caterpillar or K_eff<6). The balance gate did its job (most large catalytic families have laddery trees; PF00348 is the first balanced clean-tree one). [Matrix recipe / 80%-id reweight / canonical-MI / APC-MIp / KT-MDL K_comp / HSExposureCB burial / BLOSUM62 PDB-map / IQ-TREE LG+G4 are pinned EXACTLY as the prior families.]

**(ii) STATISTICS (UPGRADED defaults, FIXED here).** persistence = cross-subclade median raw MI (K=8 tree-cut of `iq_PF00348.treefile`, K_eff >= 6 by selection; within-subclade 80%-id reweight; raw MI via canonical `cit/information.py`). For EACH estimator (K_MI = APC-MIp, K_comp = KT/MDL), induced w = sigma(beta z(rho)), beta = 4.0:
  - Spearman(w, persistence) overall + long-range;
  - PARTIAL via the SEPARATED control: partial-Spearman(w, persistence | conservation_i, conservation_j, burial_i, burial_j) (4 DISTINCT covariates, precision-matrix partial), overall + long-range, on the burial-defined mapped subset;
  - POSITION-BLOCK bootstrap CI: resample the L positions with replacement (seed 0, B = 1000); a pair (i,j) enters with multiplicity cnt_i * cnt_j; 95% percentile CI of the separated-partial.
  Also report: Spearman(w, conservation-product) per estimator (the conservation-orthogonality check); the context Spearman(whole-set MIp, persistence); and the conservation-PRODUCT null-w under BOTH the product and the separated control (to confirm the product control leaks / the separated control catches it on this family too).

**(iii) R1-EDGE GENERALIZES (verdict rule) iff** on PF00348 the LONG-RANGE SEPARATED partial-Spearman(w, persistence) > 0 with position-block 95% CI excluding 0, PER ESTIMATOR (R1 spec guard = per-estimator validity), with the conservation-CLEAN K_MI arm as the load-bearing pass and K_comp corroborating. A clean-tree pass on a third, phylogenetically-balanced family firms the PRIMARY cross-domain signature (removes the ~1.5-family generalization weakness).

**Discipline.** DESIGN + dated amendment; family/PDB/stats LOCKED HERE pre-computation; committed + pushed BEFORE the Phase-2 run (sec 8). Reuse the pinned pipeline; raw MI via canonical `cit/information.py`; numpy + `math.lgamma` only; the tree-balance gate is data-quality NOT result-selection. NO DCA; NO grid, NO family-list lock beyond this single replication. beta = 4.0 carried (no new locked-constant VALUE). Nothing in `data/` committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 6 (CORRECTED) / R1-EDGE honest result: narrowing (i) STANDS, narrowing (ii) RETRACTED (K_comp is DISTINCT from MIp, not redundant) + pinv->OLS apparatus fix

**What this is.** Dated, append-only RESULT amendment correcting the step-6 framing. The step-6 working premise ("K_comp ~= MIp, the multi-proxy construct is near-empty") was an ADVISOR ERROR, falsified against the saved files (OLS-residual, long-range, 3 families). Records ONLY what the data supports (the user's "do not overstate" directive). Apparatus: scripts/r1_edge.py + r1_edge_family3.py + r2_edge.py (the pinv->OLS fix). No pin/constant VALUE changed; nothing in data/ committed.

**(a) NARROWING (i) STANDS.** The sigma-induction w = sigma(beta * z(C_hat)) is a strictly monotone (RANK) transform of the estimator C_hat, so every rank-based signature (R1/R2/M5; all Spearman / partial-Spearman) tests the ESTIMATOR, not the induced weight MAGNITUDES. The magnitudes enter ONLY the I_w_rel / C_rel functional, which remains empirically UNTESTED (a non-rank test exercising the functional is owed -- flagged, not run here).

**(b) NARROWING (ii) RETRACTED.** The step-6 claim "K_comp ~= MIp; collapses to -0.095 once MIp is controlled; carries NO MIp-orthogonal persistence" is FALSE. The "-0.095" was a partial on the BEYOND-MARGINAL persistence target (an A3-diagnostic), NOT the main raw-MI persistence target -- it conflated a beyond-marginal-target result with the main target. Validated (long-range, OLS-residual, both conservation + burial controlled):
  | family | Spearman(w_cp, MIp) | K_comp \| APC-MIp+cons+bur | K_comp \| RAW-MI+cons+bur | w_mi \| RAW-MI+cons+bur |
  | --- | --- | --- | --- | --- |
  | PF13354 | +0.542 | +0.433 | +0.338 | +0.152 |
  | PF00026 | +0.745 | +0.260 | +0.175 | +0.065 |
  | PF00348 | +0.403 | +0.400 | +0.394 | +0.100 |
  K_comp is CORRELATED with MIp (Spearman 0.40-0.75) but NOT redundant: it retains a substantial positive persistence partial after controlling whole-set APC-MIp (+0.26..+0.43) AND after controlling RAW whole-set MI (+0.18..+0.39). INVERSION: w_mi (APC-MIp) mostly REDUCES to raw MI for persistence (residual after controlling raw MI = +0.15/+0.07/+0.10), while K_comp carries the robust beyond-MI signal. (w_mi | APC-MIp+cons+bur = +0.001/-0.009/-0.001, definitional -- w_mi is monotone in APC-MIp.)

**(c) STATUS.** There IS a real persistence signal; the multi-proxy construct is NOT near-empty (K_comp is a genuinely distinct proxy that converges with MIp on persistence). K_comp's signal SURVIVES controlling RAW whole-set MI -> it is NOT merely the raw-MI / phylogenetic-background component. LIVE HYPOTHESIS (NOT established): the MDL/compression coupling K_comp tracks cross-subclade PERSISTENCE (parsimony ~= persistent coupling) BEYOND raw information -> would support corpus principle P4 (compression is the coherence estimator). This is exactly what the structured-noise null probe (adjacent block) tests.

**(d) APPARATUS FIX (validated).** partial_sep (r1_edge_family3.py) + partial_multi (r2_edge.py) replace pinv-on-the-rank-correlation-matrix with OLS-residual regression on ranks -- robust to collinear covariates. The pinv form returns garbage when a covariate is collinear with x; the step-5 "+0.903 conservation-product-null leak" was exactly this artifact (OLS-residual gives +0.031, ~0). The LOAD-BEARING cells are UNCHANGED (pinv == OLS when well-conditioned): PF00348 K_MI sep4 +0.298, K_comp sep4 +0.479; K_MI is conservation-clean (|APC-MIp+cons+bur = -0.001 definitional, |sep4+consprod = +0.339 unmoved). The unused `rank` / `STATES` imports were removed.

**Discipline.** RESULT record + apparatus fix commit. Records ONLY data-supported claims (the near-empty premise RETRACTED as an advisor error). NO pin/constant VALUE changed; OLS-residual partials (never pinv); raw MI via canonical cit/information.py; numpy + math.lgamma only; NO DCA. Nothing in data/ committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 6 (CORRECTED) / STRUCTURED-NOISE NULL probe of K_comp's beyond-raw-MI persistence signal -- PRE-REGISTRATION

**What this is.** Dated, append-only PRE-REGISTRATION of a structured-noise null that subjects the one positive step-6 finding -- K_comp's beyond-raw-MI persistence signal (1a(b)/(c)) -- to the within-domain null every signal needs. QUESTION: is the beyond-raw-MI K_comp -> persistence partial genuine COUPLING, or a marginal-bias / generic-statistics artifact of the conservation + phylogeny structure the target is built from? Thresholds FIXED here; run only AFTER this is committed + pushed (sec 8). Apparatus scripts/r1_null_probe.py. Nothing in data/ committed.

**SURROGATE (preserves marginals + subclade phylogeny; DESTROYS coupling).** Reuse the SAME cut_into_subclades(acc) partition (deterministic; the r1_edge K=8 cut on iq_{acc}.treefile). For surrogate seed s (s = 0..N_SURR-1; rng = np.random.default_rng(s)): within EACH subclade, permute EACH column's residues independently among the sequences in that subclade. This PRESERVES (i) per-(subclade, column) marginals, (ii) the whole-set per-column marginals -> conservation UNCHANGED, (iii) subclade membership; and DESTROYS within-subclade cross-column coupling. Burial is a structural (PDB) property -> reuse the REAL burial.

**STATISTIC.** On each surrogate, recompute raw whole-set MI, K_comp (KT/MDL), and persistence (cross-subclade median raw MI); compute the SAME OLS-residual partial(K_comp, persistence | raw-whole-set-MI, cons_i, cons_j, bur_i, bur_j), long-range (|i-j| >= 12), on the burial-defined mapped subset. N_SURR = 20 seeded replicates, ALL 3 families. The REAL value is the 1a(b) "K_comp | RAW-MI+cons+bur" = +0.338 / +0.175 / +0.394 (PF13354 / PF00026 / PF00348). [Raw MI + K_comp use the VECTORIZED plug-in MI / KT codelength -- bit-identical to canonical cit/information.py (verified step-3 to 5e-16) + the locked KT recipe -- required for feasibility across 20 x 3 surrogate recomputations; the per-pair canonical path produced the REAL/saved raw MI.]

**PRE-COMMITTED FORK (per family).**
  - REAL >> surrogate null (REAL > 95th percentile of the 20 surrogates AND the surrogate distribution centered near 0) -> the beyond-raw-MI signal REQUIRES real coupling: a genuine compression-specific coherence signal, the first thing in this arc BEYOND re-describing the field's MI (candidate P4 support). NEXT: characterize it / K_pred as a third-proxy strengthening test.
  - surrogate null ~= REAL (both > 0) -> the signal is a marginal-bias / generic-statistics artifact, NOT coupling-specific. CONCEDE the beyond-MI finding is within-domain noise; the decisive test is cross-DISJOINT-domain transfer with a structured-noise null (the standing circularity prior), not another within-domain proxy.

**Report.** Per family: REAL beyond-raw-MI partial vs the 20-surrogate null (mean, 95th pct, z = (REAL - mean)/std, percentile-of-REAL), mapped to the fork; state plainly which branch fired on each family.

**Discipline.** DESIGN + dated amendment; criteria LOCKED HERE pre-computation; committed + pushed BEFORE the Phase-2 run (sec 8). THREE families; reuse the pinned pipeline + the subclade cut; OLS-residual partials (never pinv); the surrogate destroys coupling while preserving marginals + subclade phylogeny; raw MI bit-identical to canonical cit/information.py. NO DCA; NO K_pred build, NO grid, NO decisions past the fork. Nothing in data/ committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL BUILD step 6 (CORRECTED) / STRUCTURED-NOISE NULL probe RESULT: K_comp's beyond-raw-MI persistence signal is a MARGINAL-BIAS ARTIFACT (FALSIFIED); K_comp ~= raw MI (Spearman +0.99)

**What this is.** Dated, append-only RESULT for the structured-noise null pre-registered immediately above. Apparatus scripts/r1_null_probe.py (vectorized raw MI + KT/MDL K_comp, bit-identical to canonical cit/information.py [verified] + the locked KT recipe; the surrogate destroys within-subclade coupling while preserving marginals + subclade phylogeny). ADVERSARIALLY VERIFIED by a 4-agent workflow (every load-bearing number reproduced bit-exact; estimators canonical to ~1e-15; the surrogate confirmed valid + CONSERVATIVE -- it destroys coupling to the finite-sample bias floor, not past it). No pin/constant VALUE changed; nothing in data/ committed.

**(a) RESULT (all 3 families = MARGINAL-BIAS ARTIFACT).** REAL beyond-raw-MI partial(K_comp, persistence | raw-MI, cons_i, cons_j, bur_i, bur_j) long-range vs the 20-surrogate null:
  | family | REAL | surrogate mean (std) | 95th pct | z | fork |
  | --- | --- | --- | --- | --- | --- |
  | PF13354 | +0.338 | +0.274 (0.010) | +0.290 | +6.26 | marginal-bias artifact |
  | PF00026 | +0.175 | +0.220 (0.006) | +0.229 | -7.32 | marginal-bias artifact |
  | PF00348 | +0.394 | +0.463 (0.006) | +0.469 | -11.71 | marginal-bias artifact |
  On ALL three families the coupling-destroyed surrogate null is FAR from 0 (+0.22..+0.46) and at-or-ABOVE the REAL value (PF00026/PF00348 REAL falls BELOW the null) -> the fork's coupling-specific clause (REAL > 95th pct AND |surrogate mean| < 0.10) FAILS; the marginal-bias / generic-statistics branch fires. Robust controls: REAL +0.338 == canonical saved; UNWEIGHTED control +0.369 vs +0.295 (not a weighting artifact); within-subclade mean raw MI collapses real 0.33 -> surrogate 0.16 (coupling destroyed to the bias floor).

**(b) MECHANISM (verified): K_comp ~= raw MI.** Spearman(raw whole-set MI, K_comp) = +0.996 / +0.992 / +0.993. K_comp (KT/MDL compression coupling) is a NEAR-MONOTONE transform of plug-in raw MI -- NOT a genuinely distinct algorithmic paradigm. So the "beyond-raw-MI K_comp" partial regresses out a control ~collinear with the predictor -> the residual is DEGENERATE noise whose real-vs-surrogate sign is incidental (this is why PF00026/PF00348 land below the null without it being anti-signal). The +0.27/+0.22/+0.46 surrogate null is a genuine finite-sample MARGINAL-BIAS channel (persistence = cross-subclade median raw MI is dominated by the plug-in MI bias floor, which varies by subclade size + marginals; surrogate within-subclade MI sits at that floor ~0.27, not 0); the raw-MI/cons/burial controls FAIL to absorb it, and K_comp (marginal / effective-alphabet sensitive) tracks it. The REAL statistic rides the SAME channel.

**(c) WHAT THIS DISSOLVES + WHAT SURVIVES.** DISSOLVED: the step-6 LIVE HYPOTHESIS (K_comp tracks persistence BEYOND raw information -> candidate P4 support) is FALSIFIED -- no coupling-specific compression signal beyond MI. It also REFINES the R2-edge "two genuinely distinct DENSE paradigms converge" framing (step 1): at the RAW level K_comp ~= MIp (Spearman raw +0.99; APC-MIp is raw MI minus the APC background), so the R2-edge convergence is REAL but is APC-MIp vs near-raw-MI -- the SAME Shannon-plug-in paradigm differing by the APC correction, NOT two genuinely distinct philosophies. Within a single domain K_comp and MIp CANNOT be teased apart (rho +0.99, shared finite-sample bias). SURVIVES (untouched): the primary K_MI/MIp coupling-PERSISTENCE (PF00348 + pilots, conservation/burial-clean) is real and a genuine improvement over node-w's conservation-circularity -- but it is the field's STANDARD MI coevolution signal re-described across phylo-independent subclades, NOT a compression-specific or multi-proxy coherence signal beyond MI.

**(d) CONCLUSION (the pre-registered fork, on data).** CONCEDE the beyond-MI compression finding as within-domain noise. The decisive test of the multi-proxy coherence construct is CROSS-DISJOINT-DOMAIN TRANSFER with a structured-noise null (the standing circularity prior) -- NOT another within-domain proxy (K_pred would be wrong: within one domain everything collapses to MIp + shared bias). A clean falsification on data ("vulnerable in the right way").

**Discipline.** RESULT record + apparatus commit (scripts/r1_null_probe.py). The Phase-1 pre-registration (above) was committed + pushed (4eb6cba) BEFORE this run (sec 8). NO pin/constant VALUE changed; OLS-residual partials; raw MI bit-identical to canonical cit/information.py; numpy + math.lgamma only; NO DCA; NO K_pred build; NO decisions past the fork. Nothing in data/ committed (gitignored). Append-only, ASCII.

### 2026-06-25 -- v0.7.2 D2 (Pfam) RELATIONAL line CLOSED as a FALSIFICATION: K_comp ~= raw MI (THEOREM, affine); R2-edge cross-paradigm convergence ILLUSORY; arc ledger (within-domain coherence-beyond-MI NOT FOUND)

**What this is.** Dated, append-only amendment that CLOSES the D2 relational line. It deepens the step-6 null-probe RESULT (immediately above): the structured-noise null FALSIFIED K_comp's beyond-raw-MI persistence as a marginal-bias artifact AND the mechanism (K_comp ~= raw MI, Spearman +0.99) is now established as an algebraic THEOREM, which in turn makes the step-1 R2-edge "two distinct paradigms converge" framing ILLUSORY. RE-RETRACTS the step-6 narrowing-(ii) correction ("K_comp genuinely DISTINCT"). Apparatus = scripts/r1_null_probe.py (estimators_whole) + the step-7 affine/residual verification (numpy + math.lgamma; reuses saved matrices + saved APC-MIp; raw MI bit-consistent with canonical cit/information.py). ADVERSARIALLY VERIFIED: independent from-scratch K_comp reimplementation (NOT the project apparatus) reproduces the affine fit + the penalty correction. No pin/constant VALUE changed; nothing in data/ committed.

**(a) FALSIFICATION (recap, the decisive within-domain test).** Structured-noise null: within each of the K=8 phylo-independent subclades, permute EACH column independently among that subclade's sequences -> within-subclade coupling DESTROYED, per-(subclade,column) marginals + subclade membership PRESERVED EXACTLY (conservation unchanged). The coupling-destroyed surrogates REPRODUCE ~79% of the real beyond-raw-MI partial on PF13354 (REAL +0.338 vs surrogate +0.266 == 79%) and on PF00026/PF00348 the REAL value falls BELOW the surrogate null (z -7.32 / -11.71). The pre-registered fork (coupling-specific iff REAL > 95th pct AND |surrogate mean| < 0.10) fires the MARGINAL-BIAS / generic-statistics ARTIFACT branch on all three families. Unweighted control + two independent verifier agents (bit-exact) confirm.

**(b) THEOREM (the deeper finding): K_comp is an AFFINE transform of raw MI -- NOT a distinct estimator.** For a FIXED 21x21 alphabet, K_comp(i,j) = L_KT(marg_i) + L_KT(marg_j) - L_KT(joint_ij) satisfies, per family:
  | family | Spearman(rawMI, K_comp) | OLS K_comp = a + b*MI: R^2 | slope b / N_eff | intercept a (bits) |
  | --- | --- | --- | --- | --- |
  | PF13354 | +0.9966 | 0.9937 | 1559.5 / 1522.0 = 1.025 | -735.3 |
  | PF00026 | +0.9926 | 0.9866 | 1498.0 / 1438.6 = 1.041 | -721.5 |
  | PF00348 | +0.9930 | 0.9880 | 1405.5 / 1326.2 = 1.060 | -721.4 |
  This is an EXACT algebraic IDENTITY, not merely a high-R^2 regression: the KT codelength expands as L_KT(c) = N_eff*Hhat(c) + pen(c), so K_comp = N_eff*(Hhat_i + Hhat_j - Hhat_ij) + (pen_i + pen_j - pen_ij) = N_eff*MI + net_penalty, verified to <= 7e-12 per pair. The slope b == N_eff exactly (b/N_eff in 1.02-1.06; the 2-6% excess is the second-order/finite-count discrepancy): the codelength saving is N_eff*MI in NATS, and converting BOTH codelength and MI to bits divides each by ln2 -- the two factors cancel, so the bits-vs-bits slope is N_eff (NOT N_eff/ln2). The offset net_penalty has only SMALL pair-variation (it carries ~0.6% of K_comp's variance and is itself MI-correlated via joint occupancy), so the OLS affine fit absorbs it into a near-constant intercept (R^2 0.987-0.994; the <1% residual IS the structured KT penalty, NOT a distinct estimator axis -- adding the distinct-joint-cell count to the OLS lifts R^2 to 0.99997). K_comp is NOT a distinct estimator; its rank-convergence with MI (Spearman +0.99) is an algebraic identity, and the residual carries no estimator-specific persistence signal (it is the degenerate noise the null probe isolated). Both the affine fit AND the exact decomposition were reproduced by an independent from-scratch reimplementation (bit-exact to the apparatus, max |diff| 5.5e-12) and survived an adversarial break-search (no subregime degrades the fit; top/bottom-decile-MI Spearman +0.98 / +0.975).

**(c) PENALTY-MAGNITUDE CORRECTION (a recorded over-statement in the step-7 brief, fixed against data).** The briefed mechanism "the penalty is pair-constant -200*log2 N" is the right SHAPE (pair-constant) but the WRONG MAGNITUDE: the naive asymptotic -200*log2(N_eff) = -2114 / -2098 / -2075 bits, whereas the empirical intercept is -735 / -722 / -721 bits (a stable ratio ~0.345x across all three families). The -200*log2(N) form presumes the FULL 441-cell joint pays the (k-1)/2 log2(N) two-part-MDL model cost with k=441 (-(440/2)log2 N ~ -2300, of which -200 log2 N is a stand-in). But at N_eff ~ 1300-1500 the 21x21 joint is ~62% EMPTY (mean OCCUPIED cells 166 / 173 / 138 of 441; empty-fraction 0.62 / 0.61 / 0.69): KT charges only for the REALIZED support because empty cells contribute lgamma(0.5) terms that CANCEL in the marginal-minus-joint difference. The realized-occupancy estimate -(mean_occ - 1)/2 * log2(N_eff) = -871 / -902 / -712 bits BRACKETS the actual intercept (-735 / -721 / -721); more precisely the per-pair net_penalty (b) scales with the EFFECTIVE-parameter count (occ_joint - occ_i - occ_j + 1) at -0.5*log2(N_eff) per parameter (Spearman -0.999 with the actual per-pair penalty, mean ~ -680 to -720), NOT the saturated (k-1)/2 alphabet count. Joint SPARSITY -- not the 440-df asymptote -- sets the constant. The CONCLUSION (K_comp = affine(MI), near-constant occupancy-set offset, rank-preserving -> not distinct) is UNCHANGED; only the offset magnitude is corrected from the asymptote to the sparsity-realized ~-720 bits.

**(d) RE-RETRACT step-6 narrowing-(ii).** The step-6-CORRECTED amendment recorded "K_comp is genuinely DISTINCT from MIp, not redundant" (it retracted an advisor's earlier near-empty/redundant premise, then over-corrected toward distinctness). That distinctness reading is ITSELF wrong: K_comp's apparent distinctness from APC-MIp was JUST the APC background subtraction (K_comp ~= raw MI; APC-MIp = raw MI - APC background), not a second algorithmic paradigm. K_comp and MIp are ONE estimator family (Shannon plug-in), differing only by APC. Both step-6 framings (redundant-with-MIp AND genuinely-distinct) are now superseded by the affine theorem: K_comp ~= raw MI exactly; APC-MIp ~= raw MI minus a background term.

**(e) ANNOTATE the step-1 R2-edge RESULT (append, prior record NOT deleted).** The R2-edge headline -- "two philosophically-distinct DENSE paradigms (K_MI = APC-MIp vs K_comp = MDL/compression) CONVERGE", long-range Spearman(K_MI, K_comp) +0.542 / +0.745 -- is ILLUSORY as a cross-paradigm result. That Spearman is just Spearman(rawMI, rawMI - APC): Spearman(K_MI, rawMI) = +0.555 / +0.786 ~= the headline, and Spearman(K_comp, rawMI) = +0.996 / +0.992. Removing raw MI from BOTH arms leaves a NEGATIVE residual correlation = -0.147 / -0.445 (long-range), i.e. there is NO second paradigm underneath the shared raw-MI -- the APC residual on the K_MI side is anti-correlated with the degenerate K_comp residual. The R2-edge "convergence" REAL content is: APC-corrected MI and (near-)raw MI agree on coevolving pairs, which they must. (The step-1 contact-precision improvement of the consensus edge over each arm survives as an APC-vs-no-APC ensembling effect, not cross-paradigm corroboration.)

**(f) ANNOTATE foundation P4 ("compression is distinct from information").** P4 is UNSUPPORTED in D2: the KT/MDL edge proxy collapses to MI for a fixed finite alphabet ((b) above), so the D2 estimator selection was MIS-SPECIFIED for a coherence-beyond-MI test -- a compression proxy that is analytically affine in MI cannot witness compression-distinct-from-information. P4 may still hold for D1's zstd / Lempel-LZ proxies (which are NOT analytic MI), but it was not tested by an MI-independent estimator in D2. (Lesson carried to cross-domain: the coherence MEASURE must be CHECKED for collinearity/identity with the domain's single generic statistic BEFORE any claim.)

**(g) ARC LEDGER (D2 relational line, final).**
  FALSIFIED / ILLUSORY:
   - R2-edge cross-paradigm convergence ((e)) -- one Shannon-plug-in family, not two paradigms.
   - K_comp-as-distinct-estimator ((b),(d)) -- affine in MI, theorem.
   - P4-in-D2 ((f)) -- the MDL edge proxy collapses to MI for fixed finite alphabet.
   - any coherence-beyond-MI in proteins ((a)) -- the one positive (K_comp beyond-MI persistence) is a marginal-bias artifact.
  SURVIVES:
   - the relational FORMALISM (I_w_rel / handshake / Shannon-recovery admissible -- step 3, S1-S6; a T2 formal result) -- BUT sigma-induction is a rank no-op (step-6 narrowing-(i), STANDS), so the weight MAGNITUDES of I_w_rel / C_rel remain UNTESTED empirically.
   - the node-w FALSIFICATION (node-valued w retired, fails the hardened phylo bar both families -- the branch adjudication holds).
   - M5: standard MI -> contact AUROC ~0.80 (the field's coevolution-contact prediction; not coherence-specific).
   - R1 (deflated): "MIp coevolution replicates across phylo-independent subclades, conservation-clean" -- the field's standard pairwise-MI coevolution signal, re-described.
  NET: D2 recovered the field's pairwise-MI coevolution construct and NOTHING beyond it. A clean "vulnerable in the right way" FALSIFICATION on data: the within-domain protein program is EXHAUSTED as a coherence test. The non-circular claim (metacoherence as a TRANSMISSIBLE pattern across DISJOINT-prior domains) is untouched by D2 and is the next test -- CROSS-DISJOINT-DOMAIN TRANSFER with a structured-noise null, NOT another within-domain proxy. Design draft: design/cross_domain_transfer.md (v0.7.3, OPEN).

**Discipline.** FALSIFICATION record + apparatus commit (scripts/r1_null_probe.py). NO new run beyond the step-7 affine/residual verification (read-only on saved matrices/MIp). Records ONLY data-supported claims; the briefed -200*log2 N magnitude is CORRECTED against data ((c)), not transcribed. NO pin/constant VALUE changed; OLS-residual partials; raw MI bit-consistent with canonical cit/information.py; numpy + math.lgamma only; NO DCA; NO cross-domain build / fetch / lock (the v0.7.3 design is a DRAFT only). Nothing in data/ committed (gitignored). Append-only, ASCII.
