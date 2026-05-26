# Multi-feature synthetic substrate — design memo

**Status**: skeleton, awaiting resolution.
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

**Decision needed**: __

### 2. Latent structure driving feature-level correlation

Options for what generates the correlation among coherence-bearing features:

- **Shared HMM**: one hidden state per step drives observable feature emissions. Most theory-canonical; aligns with K₄.
- **Coupled Markov chains**: each coherence-bearing feature is its own Markov chain with explicit transition coupling. Mid complexity.
- **Latent-class mixture**: each step samples a latent class which activates a specific feature cluster. Simplest ground truth.
- **Continuous latent variable with feature-specific decoders**: most flexible, hardest to label.

Trade-off: HMM is canonical but adds estimator complexity; latent-class mixture is simplest with clearest ground truth and lowest substrate-side ambiguity.

**Decision needed**: __

### 3. Coherence-bearing vs noise feature partition

- Ground-truth labels: every feature is labeled `coherence_bearing` or `noise` at substrate construction time.
- Coherence-bearing features participate in the latent structure; noise features are i.i.d. at a locked rate matching the marginal distribution of coherent features (so the difference is structural, not marginal).
- Locked partition size: e.g. `n_coh_features = 4`, `n_noise_features = 6` — these become pre-registered parameters.

**Decision needed**: partition sizes and matching-marginal protocol.

### 4. Backward compatibility with single-symbol-stream proxies

`predictive_logloss_proxy` (form B) and `compression_delta_proxy` (K₁) currently expect `(stream, alphabet_size) → float` where `stream` is 1-D. Multi-feature stream is 2-D `(T × n_features)`.

Options:

- **Signature overload**: each proxy accepts both 1-D and 2-D inputs with documented branching.
- **Defined reduction**: multi-feature stream reduced to 1-D via a canonical operator (concatenation? feature-vector hashing? marginal selection?) before being passed.
- **Variant proxies**: each proxy gets a `_multi_feature` variant.

Affects how cross-proxy convergence is tested on multi-feature streams. Affects whether the v0.3 cross-proxy R2 invariant carries forward unchanged or needs an amendment.

**Decision needed**: __

### 5. Forward compatibility for K₂–K₅

Each new estimator needs an explicit multi-feature consumption protocol:

- **K₂ (n-gram MDL)**: native input is a 1-D sequence. Either flatten the multi-feature step (concat + tokenize) or define a per-feature n-gram model with a combining rule.
- **K₃ (transformer prequential)**: can natively consume feature vectors as input embeddings, but requires bounded vocabularies. Tokenization scheme needs specification.
- **K₄ (MDL-HMM)**: natural fit for multi-feature observations. HMM observation model needs explicit factorization (independent emissions per feature? joint emission over feature vector?).
- **K₅ (Lempel parsing)**: byte-level operator. Encoding of each multi-feature step → bytes needs specification (canonical byte order, fixed-width per feature).

**Decision needed per estimator**: one paragraph each.

### 6. Falsifiability invariants

The substrate is useful only if it can falsify the methods. Required invariants:

- **A₃ falsifiability**: A₃ must correctly group coherence-bearing features into one or more clusters distinct from noise features on this substrate, and must FAIL to find structure on a noise-only ablation of the same substrate. If A₃ trivially recovers ground truth no matter the substrate construction, the substrate doesn't constrain A₃.
- **K-proxy convergence falsifiability**: cross-proxy R2 threshold ≥ 0.7 must hold across the 5 estimators on the multi-feature substrate when ground-truth coherence-bearing features are present, AND must drop significantly on a noise-only stream of matched marginal distribution. Convergence is supposed to be a property of the structure, not the estimators — the noise-only control test is what makes this empirically meaningful.

### 7. Pre-registered substrate parameters (locked before substrate code)

To be filled in after questions 1–6 are resolved:

- Random seeds for substrate generation: __
- `n_steps`, `n_features`, partition sizes (`n_coh_features`, `n_noise_features`): __
- Latent-structure parameters (transition rates, mixture weights, emission probabilities): __
- Test invariants v0.5.0 will assert: minimum A₃ cluster purity, A₃ cluster recovery threshold against ground-truth labels, K-proxy R2 differential between structured and noise-only streams: __

## Resolution protocol

This memo is filled in collaboratively across one or more sessions, then committed as the locked design. Once locked:

1. Substrate parameters propagate into `pre_registration.md` as `### Multi-feature substrate parameters (locked v0.5.0)`.
2. The memo's status changes from `skeleton, awaiting resolution` to `locked YYYY-MM-DD`.
3. Substrate code may begin.

No substrate code is written before the memo is locked. No exceptions — this is the structural discipline that pre_registration enforces extended one layer outward to substrate construction.

