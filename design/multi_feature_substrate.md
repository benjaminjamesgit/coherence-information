# Multi-feature synthetic substrate — design memo

**Status**: locked 2026-05-26 (all 7 design questions resolved).
**Created**: 2026-05-26.
**Required for**: v0.5.0 (substrate + A₃), v0.5.1+ (K₂–K₅ on multi-feature streams).

## Purpose

The multi-feature synthetic substrate is the falsifiability backbone for two structurally independent additions:

1. **A₃ (correlation-cluster ablation)** — requires feature-stream Pearson clustering, which single-symbol streams cannot expose by construction.
2. **K₂–K₅ estimators evaluated beyond single-symbol replay** — multi-feature observation regimes are where these estimators' structural distinctness from K₁ and form B becomes empirically meaningful.

This memo records substrate design decisions **before substrate code is written**, so the parameters bind interpretation of v0.5.0+ test outcomes. Once resolved, the locked parameters propagate into `pre_registration.md` as a new subsection under the v0.5 commitment.

## Sub-version sequencing (Option B locked 2026-05-26)

- **v0.5.0**: multi-feature substrate + A₃ — closes the ablation axis at the multi-feature level.
- **v0.5.1**: K₂ (n-gram MDL) — lowest-cost estimator extension.
- **v0.5.2**: K₅ (Lempel parsing — non-coding registrant) — sequenced second so the structurally most distant convergence signal is established early.
- **v0.5.3**: K₃ (transformer prequential).
- **v0.5.4**: K₄ (MDL-HMM).
- **v0.5.5**: full `{K} × {A}` robustness harness — capstone publishing the 15-cell convergence matrix.

Each sub-version gets its own Zenodo version DOI under the existing concept DOI (10.5281/zenodo.20399412).

## Open questions to resolve before locking

### 1. Feature count and semantics

- How many features?
  - Lower bound: enough to expose A₃ clustering (≥ 6 to allow ≥ 2 clusters of ≥ 3 features) and enough to test K-estimator convergence on multi-feature input.
  - Upper bound: tractable Shapley computation (k = 64 coalitions over n features), deterministic seeded reproduction.
- Feature type: binary indicators (Bernoulli per step), categorical with shared alphabet, real-valued, mixed?
- Observation density: feature observed at every step, or sparse?

**Locked 2026-05-26**:
- `n_features = 10`
- `n_coherent_features = 4`, `n_noise_features = 6` (preserves v0.4's 2/3 coherence/noise ratio at 2x scale)
- Feature type: binary indicators (Bernoulli per step, alphabet `K = 2` per feature)
- Observation density: dense (every feature observed at every step)

**Rationale**. A_3 correlation-cluster ablation requires >= 2 clusters of >= 3 features each, fixing a lower bound near n=10. A_2 Shapley at k=64 covers ~6.25% of 1,024 possible coalitions at n=10 -- adequate sampling without runaway compute. Binary indicators keep the per-step state space PMF-estimable (2^10 = 1024) given T >= 20,000, give K_5 a clean fixed-width byte encoding, and stay in the discrete-substrate family of v0.2-v0.4. Dense observation matches v0.2-v0.4 stream semantics; sparse observation would introduce missingness as a substrate-side confound. The 4/6 partition preserves v0.4's minority-signal framing so the existing test invariants (`min rho(coherent) > max rho(noise)`, `w(coherent) > 0.5`, `|w - 0.5| < 0.2`) scale forward without semantic shift. Richer per-feature dynamics (K > 2) and sparsity are deferred to v0.7 cross-domain validation, where substrate variation is itself the test.

### 2. Latent structure driving feature-level correlation

Options for what generates the correlation among coherence-bearing features:

- **Shared HMM**: one hidden state per step drives observable feature emissions. Most theory-canonical; aligns with K₄.
- **Coupled Markov chains**: each coherence-bearing feature is its own Markov chain with explicit transition coupling. Mid complexity.
- **Latent-class mixture**: each step samples a latent class which activates a specific feature cluster. Simplest ground truth.
- **Continuous latent variable with feature-specific decoders**: most flexible, hardest to label.

Trade-off: HMM is canonical but adds estimator complexity; latent-class mixture is simplest with clearest ground truth and lowest substrate-side ambiguity.

**Locked 2026-05-26**: Shared HMM (option a).

**Concrete specification**:
- Hidden state count: `C = 2`
- Transition matrix: symmetric sticky with `self_transition_prob = 0.9` (matches v0.2-v0.4 single-symbol Markov self-transition rate)
- Initial state distribution: stationary (uniform under symmetric transition matrix)
- Emission matrix for the 4 coherent features:
  - Features 0, 1: `p(x=1 | state=0) = 0.8`, `p(x=1 | state=1) = 0.2`
  - Features 2, 3: `p(x=1 | state=0) = 0.2`, `p(x=1 | state=1) = 0.8`
- Noise features (indices 4 through 9): `p(x=1) = 0.5` independent of state and of each other

**Marginal-matching property**. Under the stationary distribution `(0.5, 0.5)` over hidden states, each coherent feature has marginal `p(x_j=1) = 0.5 * 0.8 + 0.5 * 0.2 = 0.5`. Noise features have marginal `p(x_j=1) = 0.5` by construction. All ten features have identical marginal distributions; discrimination is purely structural (temporal coherence + cross-feature correlation), not marginal. No estimator can shortcut to the answer via per-feature marginal statistics; the v0.4 marginal-matching invariant carries forward unchanged.

**K_4 structural-advantage mitigation**. K_4 (MDL-HMM) by construction matches the substrate's data-generating process. `C = 2` keeps the model class minimal -- K_4 gets a bounded representational advantage, but K_2 (n-gram), K_3 (transformer prequential), and K_5 (Lempel parsing) recover the temporal regularity through their own mechanisms. The cross-estimator R2 test then asks whether structurally different estimator families converge on the same rho signal despite their architectural differences -- that is the genuine empirical content. Substrates with no preferred model class are illusory; any generator has some preferred class. The test is whether non-matching estimators still converge.

**Ground-truth cluster geometry**. Features {0, 1} form one positively-correlated cluster (both biased toward state 0). Features {2, 3} form a second positively-correlated cluster (both biased toward state 1). Across clusters, features are anti-correlated (one biased to state 0, the other to state 1). Noise features {4, 5, 6, 7, 8, 9} are mutually uncorrelated and uncorrelated with any coherent feature. This geometry is the falsifiability target for A_3 (correlation-cluster ablation).

### 3. Coherence-bearing vs noise feature partition

- Ground-truth labels: every feature is labeled `coherence_bearing` or `noise` at substrate construction time.
- Coherence-bearing features participate in the latent structure; noise features are i.i.d. at a locked rate matching the marginal distribution of coherent features (so the difference is structural, not marginal).
- Locked partition size: e.g. `n_coh_features = 4`, `n_noise_features = 6` — these become pre-registered parameters.

**Locked 2026-05-26**: Option Z. Expose sub-cluster ground truth via the substrate's returned label dict; assert only the binary coherent/noise distinction at v0.5.0; compute and log sub-cluster recovery as observational evidence without making it pass/fail. Promotable to a required invariant in a later sub-version (candidate: v0.5.5 capstone) once A_3's sensitivity characteristics are empirically understood.

**Partition** (locked by Q1 + Q2):
- Coherent feature indices: 0, 1, 2, 3 (`n_coh_features = 4`)
- Noise feature indices: 4, 5, 6, 7, 8, 9 (`n_noise_features = 6`)

**Matching-marginal protocol**. Every feature has marginal `p(x_j=1) = 0.5` under the stationary distribution. This is locked by the Q2 emission matrix plus the uniform stationary distribution of the symmetric sticky transition matrix. Noise features achieve marginal 0.5 via independent `Bernoulli(0.5)` at every step; coherent features achieve it via the marginalization `0.5 * 0.8 + 0.5 * 0.2 = 0.5` over hidden states. Discrimination is purely structural (temporal coherence + cross-feature correlation), never marginal -- v0.4's marginal-matching invariant carries forward unchanged.

**Ground-truth label dict** (returned by `labeled_multi_feature_stream`):

```python
labels = {
    "coherence_bearing": {0, 1, 2, 3},
    "noise": {4, 5, 6, 7, 8, 9},
    "clusters": {
        "cluster_A": {0, 1},   # both biased toward hidden state 0
        "cluster_B": {2, 3},   # both biased toward hidden state 1
    },
}
```

**v0.5.0 test invariants (asserted)**:
- Coherent features `rho > 0`; noise features `rho < 0` (canonical signs under form B, K_1, A_1, A_2, A_3)
- `min rho(coherent) > max rho(noise)` (strict class separation)
- `w(coherent) > 0.5`; `w(noise) < 0.5`; `|w - 0.5| < 0.2` (matches v0.4 invariant directly)

**v0.5.0 observational invariants (computed, logged, NOT asserted)**:
- A_3 cluster-membership recovery: Adjusted Rand Index between A_3's recovered partition of the coherent features and the ground-truth `clusters` dict. Logged in test output; not a pass/fail criterion at v0.5.0.
- Cross-cluster anti-correlation signal: average pairwise Pearson correlation between cluster_A features and cluster_B features (expected negative under the Q2 emission matrix).

**Promotion path**. The `clusters` key is returned by the substrate generator at v0.5.0; promoting sub-cluster recovery to a required invariant in v0.5.5 (or wherever empirical readiness lands) requires only adding test assertions against the same dict structure. No substrate redesign needed.

### 4. Backward compatibility with single-symbol-stream proxies

`predictive_logloss_proxy` (form B) and `compression_delta_proxy` (K₁) currently expect `(stream, alphabet_size) → float` where `stream` is 1-D. Multi-feature stream is 2-D `(T × n_features)`.

Options:

- **Signature overload**: each proxy accepts both 1-D and 2-D inputs with documented branching.
- **Defined reduction**: multi-feature stream reduced to 1-D via a canonical operator (concatenation? feature-vector hashing? marginal selection?) before being passed.
- **Variant proxies**: each proxy gets a `_multi_feature` variant.

Affects how cross-proxy convergence is tested on multi-feature streams. Affects whether the v0.3 cross-proxy R2 invariant carries forward unchanged or needs an amendment.

**Locked 2026-05-26**: variant functions.

**Implementation strategy**. New multi-feature variants live alongside the existing 1-D proxies; v0.1-v0.4 proxies stay exactly as-is (zero changes to existing API contracts, zero risk of regression in the 77-test suite). Modular ablation operators dispatch on substrate type. The 1-D and 2-D code paths are structurally distinct algorithms -- Markov on K-alphabet vs. autoregressive on binary vectors for form B; raw integer compression vs. bit-packed byte encoding for K_1 -- and separate function names enforce that separation explicitly.

**Naming convention**:
- `predictive_logloss_proxy_multi(stream_2d, n_features)` -- form B multi
- `compression_delta_proxy_multi(stream_2d, n_features)` -- K_1 multi
- `_multi` suffix locked as the convention. K_2-K_5 are native multi-feature estimators and do not require the suffix; they have no 1-D analog to disambiguate against.

**form B multi -- concrete specification (Option alpha)**:
- Autoregressive joint factorization: `p(v_t^j | v_{t-1})` for each feature `j` given the entire previous vector.
- First-order context (matches v0.2 form B first-order Markov model).
- Parameter count: `n * 2^n = 10,240` cells, vs. `2^(2n) = 1,048,576` under integer-encoding. ~99% compression of parameter space while preserving joint conditioning structure.
- Laplace smoothing matching v0.2 form B.
- Coherence aggregation: average per-feature predictability across `j`, normalized to `[0, 1]`.

**K_1 multi -- concrete specification (Option alpha')**:
- Encoding: each step encoded as 2 bytes -- 10 active bits in the first 10 positions, 6 padding zeros at the end. Fixed-width, deterministic, parseable.
- Compressor: zstd at level 3 (matches v0.3 K_1 compressor specification).
- Formula: `C_hat = 1 - len(compressed) / len(uncompressed)`, clipped to `[0, 1]` for very-short-stream regimes.
- zstd handles joint correlation structure natively through its dictionary-building mechanism -- no explicit dependency modeling needed.

**Cross-proxy R2 invariant -- version partitioning**:
- v0.3 cross-proxy R2 invariant (Spearman rho across form B 1-D and K_1 1-D >= 0.7 on single-symbol substrate) **stays at v0.3**. Continues to apply unchanged to the v0.2-v0.4 single-symbol substrate. Does NOT carry forward to multi-feature.
- v0.5 locks a NEW cross-proxy R2 invariant: Spearman rho across `predictive_logloss_proxy_multi` and `compression_delta_proxy_multi` rho vectors >= 0.7 on the multi-feature substrate.
- As K_2-K_5 land at v0.5.1-v0.5.4, the multi-feature cross-proxy invariant expands to a 5-vector all-pairs Spearman matrix where every off-diagonal pair must clear 0.7. The full 15-pair convergence matrix becomes the v0.5.5 capstone test.

**Ablation operator dispatch**. A_1, A_2, A_3 each accept a proxy callable and operate on the substrate the callable consumes. Single-symbol substrate -> 1-D proxies -> existing A_1/A_2 implementations unchanged. Multi-feature substrate -> multi proxies -> ablation operators extended to feature-level (not symbol-level) ablation. This is mostly transparent to A_1, A_2 (substitute feature for symbol); A_3 is multi-feature-native by construction (correlation clustering only makes sense on multi-feature input).

### 5. Forward compatibility for K₂–K₅

Each new estimator needs an explicit multi-feature consumption protocol:

- **K₂ (n-gram MDL)**: native input is a 1-D sequence. Either flatten the multi-feature step (concat + tokenize) or define a per-feature n-gram model with a combining rule.
- **K₃ (transformer prequential)**: can natively consume feature vectors as input embeddings, but requires bounded vocabularies. Tokenization scheme needs specification.
- **K₄ (MDL-HMM)**: natural fit for multi-feature observations. HMM observation model needs explicit factorization (independent emissions per feature? joint emission over feature vector?).
- **K₅ (Lempel parsing)**: byte-level operator. Encoding of each multi-feature step → bytes needs specification (canonical byte order, fixed-width per feature).

**Locked 2026-05-26**: per-estimator protocols below. All four are native multi-feature; no `_multi` suffix since they have no 1-D analog (K_2-K_5 are introduced at v0.5).

**K_2 (n-gram MDL) protocol** (amended 2026-05-26 -- see `pre_registration.md`):
- Per-feature factorized bigram: condition each feature on its own previous value, `p(v_t^j | v_{t-1}^j)`. No cross-feature conditioning.
- 2-part MDL code: `L(total) = L(data | model) + L(model)`.
- Model: `2 * n_features` parameters (one Bernoulli emission per (previous_value, feature)).
- Model description length: Rissanen universal prior, `L(model) = (1/2) * num_params * log2(T)` bits.
- Data description length: plug-in negative log-likelihood under Laplace-smoothed bigram, converted to bits.
- Baseline: `L_iid_uniform = T * n_features * log2(2) = T * n_features` bits.
- Coherence: `C_K2 = 1 - L(total) / L_iid_uniform`, clipped to `[0, 1]`.
- Aggregation: scalar (single MDL number for the whole stream).
- Family identity: per-feature marginal temporal predictability with explicit MDL penalty. Distinct from form B (joint conditioning `p(v_t^j | v_{t-1})`, no penalty) and K_1 (universal compression on byte stream, implicit model).
- Amendment rationale: the original joint-bigram formulation produced `C_K2 = 0` (clipped) on the locked substrate because the model penalty (~53,600 bits at ~7,500 active cells) dwarfed the data savings (~18,000 bits at form B saturation ~0.09). Factorization restores per-feature differential signal while preserving K_2's MDL family identity.

**K_3 (transformer prequential) protocol**:
- Architecture: 2-layer transformer, 32 hidden dim, 4 attention heads, GELU activation.
- Input embedding: each feature-vector `v_t` mapped to a 32-dim embedding via a 1024-row lookup table (one row per possible vector).
- Output head: softmax over 1024 outcomes (joint distribution over the next feature vector).
- Training: prequential -- at step `t`, predict `v_{t+1}` from `(v_1, ..., v_t)`; accumulate cross-entropy; single SGD step per `t`.
- Coherence: `C_K3 = 1 - mean_cross_entropy / log(1024)`, clipped to `[0, 1]`.
- Family identity: neural online prediction. No model penalty, no model selection.

**K_3 runtime caveat**: K_3 is the heaviest of the five estimators. v0.5.3 implementation may need to reduce T or use a smaller transformer to keep the CI matrix job under 60s. Architectural lock stands; runtime tuning is a v0.5.3 implementation-time scope question, not a substrate-design question.

**K_4 (MDL-HMM) protocol**:
- Model class: factorized Bernoulli emission HMM. `p(v_t | h_t) = prod_j p(v_t^j | h_t)` -- emissions factorize per feature given hidden state.
- Hidden state count `H` searched over `[1, 8]`.
- Fit method: Baum-Welch with 5 random restarts, 50 EM iterations each, best by data log-likelihood.
- MDL: `L(H) = -log P(data | HMM_H) + (1/2) * (H^2 + n*H) * log(T)` where `n = 10`.
- Selected H: `H* = argmin_H L(H)`.
- Coherence: `C_K4 = 1 - L(H*) / L_iid`, clipped to `[0, 1]`.
- Family identity: hidden-state generative model with explicit MDL-based model selection. Structurally aligned with the substrate's true generator (C=2 HMM) but mitigated: K_4 must discover H, not receive it.

**K_5 (Lempel parsing) protocol**:
- Encoding: same 2-byte-per-step encoding as K_1 multi (10 active bits + 6 padding zeros). Reuses the K_1 multi encoder.
- Parser: LZ76 parsing on the byte sequence.
- Phrase count: `c(byte_stream)` = number of distinct phrases in the LZ parse.
- iid baseline: `c_iid = T_bytes / log_2(T_bytes)` (asymptotic Lempel complexity of uniform random sequences).
- Coherence: `C_K5 = 1 - c(byte_stream) / c_iid`, clipped to `[0, 1]`.
- Family identity: non-coding pattern counting. K_5 shares its byte encoding with K_1 multi but **never invokes zstd or any entropy coder** -- structurally distinct via the parsing/coding boundary. The shared encoder is intentional: it ensures K_1 and K_5 operate on the same byte representation so their structural differences trace to the parsing/coding distinction rather than to representation drift.

**Cross-family distinctness summary**:

| K | Family | Penalty type | Output basis |
|---|--------|--------------|--------------|
| K_1 | Universal compression | Implicit (zstd) | Compressed byte ratio |
| K_2 | Explicit MDL | Explicit model + data | Total code length |
| K_3 | Neural online | None | Online cross-entropy |
| K_4 | HMM with model selection | Explicit + searched H | Best MDL across H |
| K_5 | Non-coding pattern counting | None | LZ phrase count |

Five structurally distinct families. The 15-pair Spearman rank correlation matrix asks whether all five recover the same per-feature rho ranks despite architectural differences. Convergence at >= 0.7 across every off-diagonal pair is the v0.5.5 capstone empirical claim.

### 6. Falsifiability invariants

The substrate is useful only if it can falsify the methods. Required invariants:

- **A₃ falsifiability**: A₃ must correctly group coherence-bearing features into one or more clusters distinct from noise features on this substrate, and must FAIL to find structure on a noise-only ablation of the same substrate. If A₃ trivially recovers ground truth no matter the substrate construction, the substrate doesn't constrain A₃.
- **K-proxy convergence falsifiability**: cross-proxy R2 threshold ≥ 0.7 must hold across the 5 estimators on the multi-feature substrate when ground-truth coherence-bearing features are present, AND must drop significantly on a noise-only stream of matched marginal distribution. Convergence is supposed to be a property of the structure, not the estimators — the noise-only control test is what makes this empirically meaningful.

**Locked 2026-05-26**. The substrate-side falsifiability claim crystallizes into three operationally testable assertions:

**1. A_3 cluster recovery (observational at v0.5.0; asserted at v0.5.5 capstone)**.
A_3 must recover the ground-truth cluster partition `{0,1}` vs `{2,3}` from the substrate when applied to coherence-bearing features. Measured via Adjusted Rand Index between A_3's recovered partition and the ground-truth `clusters` dict. At v0.5.0, ARI is computed and logged but not asserted (per Q3 Option Z). At v0.5.5 capstone, ARI is asserted at >= a threshold determined empirically from v0.5.0-v0.5.4 observations.

**2. Cross-K convergence (partial at v0.5.0-v0.5.4; full at v0.5.5 capstone)**.
The 15-pair Spearman rank correlation matrix across the 5 K-estimators must satisfy:
  (a) Every off-diagonal pair `>= 0.7` on the structured multi-feature substrate.
  (b) Every off-diagonal pair drops significantly on a noise-only control stream of matched marginal distribution.
At v0.5.0, only the `(K_1_multi, form B multi)` pair from Q4 is testable. Each subsequent sub-version v0.5.1-v0.5.4 adds new pairs to the matrix. The full 5x5 matrix and the noise-only control test are asserted at v0.5.5 capstone.

**3. Marginal-matching invariance**.
By construction (locked Q2 + Q3), all 10 features have identical marginal `p(x_j=1) = 0.5`. No estimator can shortcut to the correct classification via per-feature marginal statistics. Any estimator achieving the v0.4 invariants (`min rho(coherent) > max rho(noise)`, `w(coherent) > 0.5`, `w(noise) < 0.5`, `|w - 0.5| < 0.2`) does so via temporal coherence + cross-feature correlation exclusively.

**Noise-only control stream protocol (locked v0.5.0)**.
The falsifiability claim requires generating a matched-marginal noise-only counterfactual at the substrate level. Specification:
- Same `n_features = 10`, `T`, and seed machinery as the labeled substrate.
- ALL 10 features are i.i.d. `Bernoulli(0.5)` -- including indices 0-3 (no hidden states, no emission matrix, no temporal coupling).
- Returned by a separate function: `noise_only_multi_feature_stream(n_features, n_steps, rng)`.
- The ground-truth label dict is omitted (or returned with all features labeled `noise`).
- Used in v0.5.0+ tests as the `structure absent` counterfactual against which the structured substrate is compared.

**Why the noise-only control matters structurally**. Without it, the cross-K convergence claim is circular: if all five K-estimators converge on the structured substrate, the convergence could be a property of the estimators (they all model temporal data similarly) rather than a property of the structure (they all detect the same underlying signal). The control test isolates which. Convergence on structured but not on noise-only implies estimators are tracking structure, not each other. This is the operational form of the M5 admissibility gate from Metacoherence -- a substrate must enable a counterfactual that breaks the convergence claim if the claim is vacuous.

### 7. Pre-registered substrate parameters (locked before substrate code)

**Locked 2026-05-26**. Canonical parameter assembly. Propagates into `pre_registration.md` as `### Multi-feature substrate parameters (locked v0.5.0)`.

#### Seeds (carried from v0.2-v0.4)

| Parameter | Value |
|-----------|-------|
| `STREAM_SEED` | `42` |
| `ABLATION_SEED` | `123` |

#### Stream shape (Q1)

| Parameter | Value |
|-----------|-------|
| `n_steps` | `20_000` |
| `n_features` | `10` |
| `n_coh_features` | `4` |
| `n_noise_features` | `6` |
| Coherent feature indices | `{0, 1, 2, 3}` |
| Noise feature indices | `{4, 5, 6, 7, 8, 9}` |
| Feature type | binary indicators, alphabet `K = 2` per feature |
| Observation density | dense (every feature observed every step) |

#### Hidden Markov generator (Q2)

| Parameter | Value |
|-----------|-------|
| Hidden state count `C` | `2` |
| Transition matrix | symmetric sticky, `self_transition_prob = 0.9` |
| Initial state distribution | stationary (uniform) |
| Emission features 0, 1 | `p(x=1|s=0) = 0.8`, `p(x=1|s=1) = 0.2` |
| Emission features 2, 3 | `p(x=1|s=0) = 0.2`, `p(x=1|s=1) = 0.8` |
| Emission features 4-9 | `p(x=1) = 0.5` i.i.d., state-independent |
| Stationary marginal | `p(x_j=1) = 0.5` for all `j` (marginal-matching invariant) |

#### Ground-truth label dict (Q3)

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

#### Proxy specifications (Q4 + Q5)

| Estimator | Function | Locked parameters |
|-----------|----------|-------------------|
| form B multi | `predictive_logloss_proxy_multi` | autoregressive joint factorization `p(v_t^j | v_{t-1})`, first-order, Laplace smoothing, 10,240-cell parameter space |
| K_1 multi | `compression_delta_proxy_multi` | 2-byte fixed-width encoding (10 active + 6 padding), zstd level 3 |
| K_2 | `ngram_mdl_proxy` | per-feature factorized bigram `p(v_t^j | v_{t-1}^j)`, 2-part MDL with Rissanen prior `(1/2)*num_params*log2(T)` bits, Laplace smoothing (amended 2026-05-26) |
| K_3 | `transformer_prequential_proxy` | 2-layer transformer, 32 hidden, 4 heads, GELU, 1024-class softmax, 32-dim vector embedding, single SGD step per `t` |
| K_4 | `mdl_hmm_proxy` | factorized Bernoulli HMM, `H in [1, 8]`, Baum-Welch with 5 restarts x 50 EM iter, MDL `L(H) = -log P(data) + (1/2)*(H^2 + n*H)*log(T)` |
| K_5 | `lempel_parsing_proxy` | LZ76 parse on K_1 byte encoding, `c_iid = T_bytes / log_2(T_bytes)` baseline |

All proxy outputs are scalars in `[0, 1]`. Coherence aggregation per Q5 specifications.

#### Ablation operators

| Operator | Function | Status |
|----------|----------|--------|
| A_1 | `leave_one_out_ablation` | Locked v0.2; extended to feature-level at v0.5.0 |
| A_2 | `shapley_ablation` (`k = 64`, `center = True`) | Locked v0.4; extended to feature-level at v0.5.0 |
| A_3 | `correlation_cluster_ablation` | New at v0.5.0; multi-feature-native (no 1-D analog) |

#### Asserted test invariants (v0.5.0)

Carry forward from v0.4 with symbol -> feature substitution:

- Canonical signs: `rho(coherent) > 0`, `rho(noise) < 0`
- Strict class separation: `min rho(coherent) > max rho(noise)`
- Weight separation: `w(coherent) > 0.5`, `w(noise) < 0.5`
- Weight band: `|w - 0.5| < 0.2`
- Per-feature sign agreement: A_1 vs A_2 on every feature (v0.4 carry)
- Multi-feature cross-proxy R2: Spearman `rho(form B multi, K_1 multi) >= 0.7`

#### Observational invariants (v0.5.0, logged not asserted)

- A_3 cluster recovery: Adjusted Rand Index between A_3 partition of coherent features and ground-truth `clusters` dict
- Cross-cluster anti-correlation: average pairwise Pearson `corr(cluster_A, cluster_B)` (expected negative)

#### Cross-K convergence threshold (sub-version progression)

| Sub-version | New pairs asserted |
|-------------|---------------------|
| v0.5.0 | `(form B multi, K_1 multi)` |
| v0.5.1 | `(K_2, *)` for each of `{form B multi, K_1 multi}` |
| v0.5.2 | `(K_5, *)` for each of `{form B multi, K_1 multi, K_2}` |
| v0.5.3 | `(K_3, *)` for each of `{form B multi, K_1 multi, K_2, K_5}` |
| v0.5.4 | `(K_4, *)` for each of `{form B multi, K_1 multi, K_2, K_5, K_3}` |
| v0.5.5 capstone | Full 15-pair off-diagonal matrix every pair `>= 0.7`; noise-only control test asserted (every pair drops significantly on noise-only stream) |

#### Noise-only control stream (Q6)

| Parameter | Value |
|-----------|-------|
| Function | `noise_only_multi_feature_stream(n_features, n_steps, rng)` |
| Generation | All features i.i.d. `Bernoulli(0.5)`, including indices 0-3 |
| Label dict | omitted, or all features labeled `noise` |
| Use | counterfactual at v0.5.5 capstone for falsifiability of cross-K convergence |

#### A_3 cluster recovery promotion (deferred to v0.5.5)

ARI threshold for required-invariant status is empirically determined from v0.5.0-v0.5.4 observations. Locked in `pre_registration.md` amendment before v0.5.5 release.

## Resolution protocol

This memo is filled in collaboratively across one or more sessions, then committed as the locked design. Once locked:

1. Substrate parameters propagate into `pre_registration.md` as `### Multi-feature substrate parameters (locked v0.5.0)`.
2. The memo's status changes from `skeleton, awaiting resolution` to `locked YYYY-MM-DD`.
3. Substrate code may begin.

No substrate code is written before the memo is locked. No exceptions — this is the structural discipline that pre_registration enforces extended one layer outward to substrate construction.

