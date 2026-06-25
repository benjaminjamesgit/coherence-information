# coherence-information

[![tests](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml/badge.svg)](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20399412.svg)](https://doi.org/10.5281/zenodo.20399412)

Open-source Python implementation of **Coherence-Weighted Entropy** and the **Coherence Information Theory (CIT)** pipeline.

## What this is

CIT extends Shannon's information theory by attaching a bounded weight `w(x) ∈ [0, 1]` to each source symbol, where the weight measures that symbol's contribution to recursive structural stability. The three core formal quantities:H(X)        = -Σ p(x) log p(x)                          (Shannon entropy)
H_w(X)      = Σ p(x) w(x) [-log p(x)]                   (coherence-weighted entropy)
I_w(X; Y)   = Σ p(x,y) w(x) log[p(x,y) / p(x) p(y)]     (coherence-weighted MI)

### The boundary condition

When `w(x) = 1` for all x, every coherence-weighted quantity collapses exactly to its Shannon counterpart. This is what licenses CIT as a **generalization** of classical information theory, not a replacement.

The Shannon-recovery test in `tests/test_shannon_recovery.py` enforces this collapse empirically across uniform, skewed, near-deterministic, and sample-based distributions, plus the analogous collapse for mutual information.

### Where w(x) comes from

Weights can be user-supplied for direct use of `H_w` and `I_w`, or **induced from data** via the v0.2 pipeline from James (2026):stream → Ĉ (predictive log-loss proxy) → ρ(x) (leave-one-out ablation) → w(x) = σ(β · ρ(x)) `cit.induce.induce_weights` orchestrates the full pipeline with the pre-registered β = 4.0. Proxy and ablation operators are deliberately swappable; the v0.3 roadmap adds compression-delta proxies (form A), Shapley ablation (k=64 coalitions), and the K₁–K₅ estimator robustness harness.

## Status

Current suite: **272 fast / 100 slow / 18 very_slow = 390** (1 xfail). The per-row counts below are as-of-ship snapshots, not the live total.

| Version | Contents |
|---------|----------|
| **v0.7.3** *(in progress — unreleased)* | **Cross-domain transfer — DESIGN DRAFT (open; no build, no data, no lock).** Opened by the D₂ falsification: within a single domain CIT recovers that domain's *existing* field construct (D₂ → MI coevolution), so the non-circular claim is **metacoherence** — coherence as a pattern *transmissible across domains whose field-priors are disjoint*, a property of the **map between** datasets, not *in* any one. The draft [`design/cross_domain_transfer.md`](design/cross_domain_transfer.md) transcribes the four non-negotiable constraints (disjoint field-priors; a structured-noise null the surrogates must *fail*; the test is the **transfer**, never within-domain recovery; **no MI-collapse trap** — check the coherence measure for collinearity with a single generic statistic *before* any claim, the K_comp=affine(MI) lesson), scopes three candidate architectures (weight-transfer / invariant-matching / domain-translation φ) and 2–3 disjoint-prior domain *pairs* (substrate + coherence computation + buildable surrogate each), and flags the deep open problem: the flat first-order measure reduces to the field statistic, so the transmissible representation is likely the **recursive / multi-scale** coherence — the cross-domain question and the multi-scale question may be the *same* question. **OPEN — architecture / domain pair / what counts as "transmit" / the multi-scale dependency all pending Benjamin + advisor.** Suite unchanged at **272 / 100 / 18 = 390** (1 xfail) |
| **v0.7.2** *(concluded — D₂ relational line FALSIFIED; unreleased)* | **D₂ (Pfam) cross-domain validation — the relational (edge-valued `w`) line, closed as a falsification.** In active pre-registration, not yet tagged; CC0 Pfam alignments via the InterPro REST API, two pilot families (PF13354 β-lactamase, PF00026 *Asp* aspartic protease). The framing-S marginal-relative proxies measured **empty**; a coupling-signal pilot was **intermediate** (pairwise coevolution real + conservation-independent, the per-position projection weak); the pre-registered **B′** check (burial-controlled edge→node) **failed**, escalating the Sec 6.2 per-position-`w` question; the **B2** graph-projection check **passed narrowly** (PageRank). The **second-family replication** then showed the **edge signal generalizes** (edge-M5 MIp-AUROC **0.80** beats both conservation- *and* burial-product, even long-range) while the **node-valued `w` fails the phylo-hardened bar** (PageRank margin −0.007, CI includes 0; B2 did not replicate) — so the branch was **adjudicated: node-valued `w` retired, edge-valued `w` adopted** (corpus-aligned — coupling is a *dense entangled field*; DCA/inverse-covariance **excluded** as the Pearlian cut). Relational **step 1 (R2-edge)** passed both families: two genuinely distinct *dense* paradigms — APC-MIp vs an MDL/compression edge coupling — **converge** (long-range Spearman +0.54 / +0.75), their consensus edges **out-predict either alone** on contacts, and the convergence **strengthens** under a conservation/burial control (not the agree-on-conserved-pairs null). Relational **step 2 (formal-admissibility)** was **retracted by step 3**: it had verified the *wrong object* — edge-`w` recast as the CIT per-symbol weight on the 441-symbol *joint* pair-symbol, which collapses to single-source node-`w` on a merged node (weighting joint symbol-*values*, not the *relation*, and not even shape-admissible against the canonical 21-symbol source-marginal `I_w`) — and that PASS was *tautological* (check B hardcoded `np.ones`; the pair-overlap risk was never probed). **Step 3** retracts that object and installs the corrected **relational functional** `I_w_rel = Σ w(i,j)·I(Xᵢ;Xⱼ)` over the dense complete graph — raw pairwise MI via the **canonical** `cit/information.py` at `w=1` (clean Shannon boundary), `w` induced from marginal-relative proxies, with `C_rel ∈ [0,1]` and an exact handshake `Σᵢ cᵢ = 2·I_w_rel` closing the overlap. Its pre-registered stress-test **S1–S6 passes both families — the formal gap is closed**: real Shannon recovery (through canonical code, *with* a non-trivial weight response), non-collapse (the relational contribution vanishes at independence where the retracted merged-node object stays large), the handshake exact to ≤7e-12, monotonicity, boundedness, relabel-invariance. The two step-2 follow-ups are *discharged* (the 441-vs-21 convention is moot — a scalar edge weight now; `I` via canonical; overlap closed by the handshake); S7/S8 evidence favors the recommended **raw-I base + sum-I normalizer** (sum MIp is negative, ~60% of edges have MIp<0), with the base/normalizer/merge rulings left open. Then **steps 4–6 put the multi-proxy claim to the test.** The choices were **ruled** (c3: the functional base is *raw* I with coherence in `w` — new foundation P7; c1: the `Σ I` normalizer; c-merge deferred). **R1-edge** — does induced edge-`w` predict *phylogeny-corrected* coupling **persistence** (median raw MI across K=8 phylo-independent subclades)? — gave a **pilot pass** on all three families, including a deliberately selected **clean-tree third family** (PF00348 polyprenyl-synthetase, 8a7c:A @1.2 Å, balanced K_eff=6 vs PF00026's caterpillar), with the load-bearing **conservation-clean K_MI arm** clearing a long-range separated partial > 0 (position-block CI excluding 0). But the **decisive within-domain null** then **falsified** the one apparently-novel finding: K_comp's *beyond-raw-MI* persistence signal is a **marginal-bias artifact** on all three families — a structured-noise surrogate that destroys coupling while preserving marginals + subclade phylogeny **reproduces or exceeds** the real partial (REAL +0.34/+0.18/+0.39 vs surrogate +0.27/+0.22/+0.46). The mechanism (adversarially verified): **K_comp ≈ raw MI** (Spearman +0.99) — *not* a genuinely distinct algorithmic paradigm, so the step-1 "two distinct paradigms converge" is real but is APC-MIp vs near-raw-MI (the *same* Shannon-plug-in paradigm differing by the APC correction). **What survives:** MIp coevolution persists across phylo-independent subclades, conservation-clean — a genuine improvement over node-`w`'s conservation-circularity, but the field's *standard* MI coevolution signal re-described, **not** a compression-specific coherence signal. **Conclusion (the pre-registered fork, on data):** concede the beyond-MI finding as within-domain noise; the decisive test of the multi-proxy construct is **cross-disjoint-domain transfer** with a structured-noise null — not another within-domain proxy. **Step 7 closes the line as a falsification.** A within-domain *theorem* makes the deflation exact — **K_comp = N_eff·(raw MI) − KT_penalty**, an exact algebraic identity (verified to 7e-12; OLS R² 0.987–0.994, slope/N_eff 1.02–1.06, Spearman +0.99; the offset is set by joint *sparsity*, ~62% empty cells, not the briefed −200·log₂N asymptote, which overshoots 3×). So K_comp is **not a distinct estimator** (re-retracting the step-6 "genuinely distinct" reading), and the step-1 **R2-edge "two paradigms converge" is illusory** — the headline Spearman is just Spearman(rawMI, rawMI−APC), and the residual after removing raw MI from *both* arms is **negative** (−0.15 / −0.45): no second paradigm underneath. **Foundation P4** ("compression distinct from information") is therefore **unsupported in D₂** (the MDL edge proxy collapses to MI for a fixed finite alphabet — the estimator was mis-specified for a coherence-beyond-MI test; P4 may still hold for D₁'s non-analytic zstd/LZ proxies). **Arc ledger** — *falsified/illusory:* the R2-edge convergence, K_comp-as-distinct, P4-in-D₂, and any coherence-beyond-MI in proteins; *survives:* the relational **formalism** (admissible, a T2 formal result — but σ-induction is a rank no-op, so the `I_w_rel`/`C_rel` weight *magnitudes* stay untested), the **node-`w` falsification**, M5's standard-MI→contact AUROC ~0.80, and the deflated **R1** ("MI coevolution replicates across phylo-independent subclades, conservation-clean"). **Net: D₂ recovered the field's pairwise-MI coevolution construct and nothing beyond it — a clean "vulnerable in the right way" falsification; the within-domain protein program is exhausted as a coherence test.** The non-circular claim (metacoherence as a *transmissible* pattern across disjoint-prior domains) is untouched by D₂ and is the next test (→ **v0.7.3**). Pilot apparatus only — **no committed tests yet**; suite unchanged at **272 fast / 100 slow / 18 very_slow = 390** (1 xfail) |
| **v0.7.1** | **Cross-domain validation (Metacoherence) — the D₁ instrument-calibration tier**, shipped + tagged 2026-06-24. Packages the D₁ synthetic-HSMM substrate, the categorical marginal-relative K₁–K₅ × A₁–A₃ grid + R2/cross-tab machinery, the decoupling control (verdict inconclusive), and R1 persistence — plus the D₂ (Pfam) R1 pre-registration. Status recorded, not tuned: **R2 reclassified a non-falsifying diagnostic** (cross-extractor `w` agreement certifies only shared coverage), **R1 + the v0.6.2 functional win elevated to primary** (per-estimator validity, not cross-estimator agreement). **R1 on D₁ closed as calibration** — necessary-not-sufficient, mechanism-confounded: the generator's regime path is emission-independent, so D₁ persistence is regime-inference structure with a D-led (concentration-biased) cost, and a partial d-matrix (K₁ fails, K₂ passes) shows a pass weights the sharp feature, not persistence. The load-bearing R1 is D₂/D₃, behind a pre-registered concentration-homogeneity check. (The D₂ Pfam relational line built on this tier is unreleased — see the **v0.7.2** row above.) Suite **272 fast + 100 slow + 18 very_slow = 390** (1 xfail) |
| **v0.6.2** | **Selective Compression empirics** — the falsifiable win-margin, completing the v0.6 operational-theorem program. On coherence-structured sources the corrected selective coder (v0.6.1) compresses **31–49% below** the weight-blind lossless rate while reproducing every coherence-bearing symbol exactly (zero retention cost), and the saving **collapses to exactly 0** at the boundary (`w ≡ 1`, nothing to discard). Two-sided falsifiable claim, locked: arithmetic `Δ_frac = (rate_blind − rate_selective)/rate_blind ≥ WIN_MARGIN = 0.20` on each structured substrate **and** `Δ = 0` at `S_δ = X` **and** lossless on `S_δ` throughout. Three seeded substrates (N=100k): i.i.d., Gilbert–Elliott (memory), TCUN (toggle + uniform noise); measured `Δ_frac` 0.492 / 0.411 / 0.307 (margin set below the 0.307 floor, calibrated like `T_NOISE`). 194 fast + 75 slow + 18 very_slow (1 xfail); 12 new empirics tests, all fast |
| **v0.6.1** | **Selective compression coder** — repairs the Selective Compression Theorem (Thm 5.1), which an adversarially-verified analysis (confirmed against the paper text) found **unsound for non-constant w**: `L ≤ H_w` is unachievable, and the typical-set cardinality bound `|T| ≤ 2^{n(H_w+ε)}` fails because w-typicality constrains the *weighted* log-prob while `|T|` is set by the *raw* one (enumerated counterexamples; the paper's own Sec 5.4 binary example is the counterexample). `H_w` is recast as a **measure** ("bits that matter"), not a compression rate. The corrected, sound theorem compresses to the **merged-source entropy `H(Z)`** — reproduce every must-preserve symbol (`w(x) > δ`) exactly, collapse all don't-cares into one token. Coder (`cit/coders/selective.py`): merge → entropy-code, a bit-exact 32-bit arithmetic coder (rate → `H(Z) + ε`; measured +0.001 bits/sym over `H(Z)` at N=200k) plus a practical zstd variant. **Boundary spine**: `S_δ = X` (e.g. `w ≡ 1`) collapses to Shannon `H(X)`. Coherence saving ≈ 0.9 bits/sym vs the weight-blind coder. 182 fast + 75 slow + 18 very_slow (1 xfail); 23 new coder tests, all fast |
| **v0.6.0** | **Coherence capacity estimator** — first operational-theorem deliverable. `C_C = max_{p(x)} I_w(X;Y)` over the input simplex (reusing `I_w`) via a deterministic projected-gradient multi-start simplex maximizer (centroid + vertices + resolution-20 lattice; analytic gradient; no RNG, bit-exact). **Boundary spine**: `w ≡ 1` recovers Shannon channel capacity exactly (BSC, Z-channel). **Sec 6 erratum** — the paper's closed-form Binary Coherence Channel value `C_C(ε) = 0.5(1+ε)` is `I_w` at the *uniform* input, a lower bound, **not** the capacity; uniform is not optimal for ε < 1 (maximizer at `q* < 0.5`), so the true capacity is strictly higher (ε=0 → `1/(e·ln2) ≈ 0.5307` at `q* = 1/e`; ε=1 → 1; interior grid-verified). Concavity of `I_w` in `p(x)` recorded **open** — multi-start agreement is the empirical uniqueness stand-in. 159 fast + 75 slow + 18 very_slow (1 xfail); 32 new capacity tests, all fast (no new slow tier) |
| **v0.5.5** | **Capstone** — noise-only counterfactual falsifiability + Seam 1 resolution. The full 15-pair {K}×{A} structured convergence matrix (form B, K₁–K₅) is consolidated, and the noise-only counterfactual is operationalized and asserted: each off-diagonal pair clears Spearman ρ ≥ 0.5 on the structured substrate **and** drops below ρ < 0.3 (`T_NOISE`) on the structure-free stream. Asserted on A₁ + A₃ for all 15 pairs; A₂ (Shapley) sampled on the 3 cheap-proxy pairs. Calibration: noise-only ρ ≤ 0.000 across every ablation vs structured ρ ≥ 0.571 — independent coherence proxies converge on real structure and stop converging on noise (the construct is not circular). **Seam 1 resolved, `(K₅, K₂)`-specific**: of all `(X, K₂)` pairs under A₂ Shapley only K₅ misses (0.491); K₃, K₄ (0.830), form B, K₁ all clear — the framework's operating envelope is not restricted, seam stays `xfail`. 127 fast + 75 slow + 18 very_slow (1 xfail); 33 new noise-only falsifiability tests, no new very_slow tier. A₃ cluster-recovery ARI remains observational |
| **v0.5.4** | Adds K₄ (MDL-HMM — factorized-Bernoulli emission HMM with two-part MDL model selection over hidden-state cardinality H∈{1,2,3,4}, fit by deterministic Baum-Welch EM, `HMM_SEED=0`) as the fifth-and-final multi-feature proxy before the capstone. `C_K4 = 1 − (L_data(H*) + L_model(H*)) / (T·n)`, H\* the MDL-selected cardinality; on the structured substrate C_K4 = 0.075 selecting H\*=2 (recovers the ground-truth 2-state generator), on noise-only C_K4 = 0 selecting H\*=1. Cross-proxy R2 extended: `(K₄, *)` for each of `{form B multi, K₁ multi, K₂, K₅, K₃}` under A₁, A₂, A₃ (15 pairs); all measured pairs clear Spearman ρ ≥ 0.5. The pre-registered at-risk pair `(K₄, K₂)` under A₂ Shapley — the structural twin of Seam 1 — measured ρ = 0.830, so **no new seam**; this is evidence Seam 1 is `(K₅, K₂)`-specific rather than a general Shapley/coupled-vs-factorized law. 121 fast + 48 slow + 18 very_slow (1 xfail). K₄ Shapley (A₂) ≈ 2.1 h/fixture (1,280 proxy calls), under the 6 h hosted ceiling (unlike K₃); hosted very_slow runs the K₄ + K₅ families (`-k "not K3"`), with `(K₄, K₃)` under A₂ local-gated. Determinism: deterministic seeded EM init, CPU/numpy |
| **v0.5.3** | Adds K₃ (neural prequential cross-entropy — single-layer GRU, hidden=64, per-feature factorized sigmoid heads, strict online prequential SGD with `NEURAL_SEED=7`) as fifth multi-feature proxy. `C_K3 = 1 - H_pred / H_iid`, H_pred = mean per-step per-feature BCE in bits, H_iid = 1.0 bit/feature/step. Cross-proxy R2 extended: `(K₃, *)` for each of `{form B multi, K₁ multi, K₂, K₅}` under A₁, A₂, A₃ — all 12 pairs clear Spearman ρ ≥ 0.5; no new seam surfaced. 121 fast + 30 slow + 11 very_slow (1 xfail). K₃ Shapley (A₂) is ~4.3h/fixture (1,280 proxy calls), local-gated as it exceeds the 6h hosted-runner ceiling; hosted very_slow runs K₅ family only (`-k "not K3"`). Determinism: `torch.use_deterministic_algorithms(True)`, CPU-only |
| **v0.5.2** | Adds K₅ (Lempel parsing, bit-level LZ76 on unpacked byte stream via numba `@njit` Kaspar-Schuster) as fourth multi-feature proxy. Cross-proxy R2 extended: `(K₅, form B multi)` and `(K₅, K₁ multi)` under A₁, A₂, A₃ all clear Spearman ρ ≥ 0.5; `(K₅, K₂)` clears under A₁, A₃; under A₂ Shapley the pair sits at Spearman 0.491 — pre-registered as Seam 1, deferred to v0.5.5 capstone, mechanically xfail-marked `strict=True`. Two-tier slow gating introduced: `slow` (LOO + CorrCluster K₅ + proxy invariants, ~5–10 min) and `very_slow` (Shapley K₅, ~135 min, workflow_dispatch only); 121 fast tests unchanged + 14 slow + 5 very_slow (1 xfail). Bit-level parsing amendment locks K₅ as parsing-not-coding family |
| **v0.5.1** | Adds K₂ (n-gram MDL, per-feature factorized bigram with 2-part MDL penalty) as third multi-feature proxy. Cross-proxy R2 extended to 9 asserted pairs: `(form B multi, K₁ multi)`, `(K₂, form B multi)`, `(K₂, K₁ multi)` under each of A₁, A₂, A₃; all clear Spearman ρ ≥ 0.5. 121 tests |
| **v0.5.0** | Multi-feature substrate (shared HMM, C=2, marginal-matched, 4 coherent + 6 noise features); form B multi + K₁ multi proxies; feature-level A₁, A₂ + multi-feature-native A₃ (correlation-cluster); `induce_weights_multi` orchestrator; cross-proxy R2 invariant Spearman ρ ≥ 0.5 on multi-feature substrate; 105 tests |
| v0.4 | Shapley ablation (A₂, k=64, cohort-mean centered); cross-ablation convergence invariants (per-symbol sign agreement + Spearman ρ ≥ 0.7 across A₁ and A₂); 77 tests |
| v0.3 | Compression-delta proxy (form A / K₁) via zstd; cross-proxy validation invariants (Spearman ρ ≥ 0.7 across form B and K₁); 69 tests |
| v0.2 | Predictive log-loss proxy (form B); replace-with-uniform leave-one-out ablation (A₁); induction pipeline `stream → Ĉ → ρ → w`; labeled synthetic substrate; 57 tests |
| v0.1 | Formal quantities `H`, `H_w`, `I_w`; synthetic test substrate; Shannon-recovery spine test; 27 tests |

## Quick start

```bash
git clone git@github.com:benjaminjamesgit/coherence-information.git
cd coherence-information
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Minimal usage:

```python
import numpy as np
from cit.information import H, H_w, I_w

p = np.array([0.5, 0.3, 0.15, 0.05])
w = np.array([1.0, 0.8, 0.5, 0.1])

print(H(p))                          # Shannon entropy in bits
print(H_w(p, w))                     # Coherence-weighted entropy
print(H_w(p, np.ones(4)) == H(p))    # True — the boundary condition
```

Induce weights from data (v0.2):

```python
import numpy as np
from cit.data.synthetic import labeled_coherence_stream
from cit.induce import induce_weights

# Stream where symbols {0, 1} are coherence-bearing (sticky Markov)
# and symbols {2, 3, 4} are i.i.d. noise.
stream, labels = labeled_coherence_stream(
    n_steps=20_000, n_coherent=2, n_noise=3,
    rng=np.random.default_rng(42),
)

result = induce_weights(
    stream, alphabet_size=5,
    rng=np.random.default_rng(123),
)

for x in sorted(result["w"]):
    kind = "coherent" if x in labels["coherence_bearing"] else "noise"
    print(f"w({x}) = {result['w'][x]:.3f}   rho({x}) = {result['rho'][x]:+.4f}   ({kind})")
# Coherent symbols → w > 0.5, noise symbols → w < 0.5.
```

## Theoretical references

The implementation faithfully follows the formal definitions and pipeline specifications in the following papers, archived on PhilPapers:

- James, B. (2025). *Beyond Shannon: Coherence Information Theory and the Future of Communication.* PhilPapers. https://philpapers.org/rec/JAMBSC
- James, B. (2025). *Formal Foundations of Coherence Information Theory: Capacity and Compression Theorems.* PhilPapers. https://philpapers.org/rec/JAMFFO-2
- James, B. (2026). *Engineering Induced Coherence Weights for Coherence Information Theory.* PhilPapers. https://philpapers.org/rec/JAMEIC-2
- James, B. (2026). *Formal Foundation of Induced Coherence Weights: Compression-based Coherence and Operational Information Measures.* PhilPapers. https://philpapers.org/rec/JAMFFO3

## Reproducibility

This project follows pre-registered protocols: random seeds, the weight-mapping sensitivity parameter `β`, and threshold values are committed in [`pre_registration.md`](pre_registration.md) **before any results are produced**. The framework is falsifiable in the sense of James (2026) only if commitments precede outcomes; that file is the structural record.

## License

Apache License, Version 2.0. See [LICENSE](LICENSE).

## Citation

If you use this implementation in academic work, please cite both the software and the underlying papers. See [`CITATION.cff`](CITATION.cff) for the structured citation entry; GitHub will render a "Cite this repository" button once the file is in place.
