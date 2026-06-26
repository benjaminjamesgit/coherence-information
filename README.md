# Coherence Information Theory (CIT)

[![tests](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml/badge.svg)](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20399412.svg)](https://doi.org/10.5281/zenodo.20399412)

**An empirical program testing whether "coherence" is a measurable quantity beyond classical information theory — and a record of how it falsified its own central claim.**

CIT is the empirical arm of the Recursive / Adaptive Coherence framework. It operationalizes coherence as a *coherence-weighted information measure* with an *induced per-symbol weight*, and asks one question across synthetic and real domains, under pre-registration and structured-noise nulls:

> Does the induced coherence weight carry structure **beyond known statistical information**?

**Result (v0.7.x, terminal): No — and necessarily so.** As a measurable, coherence reduces to statistical information (the entropy rate). The instrument that operationalizes coherence is itself a statistical estimator, so "coherence beyond statistical information" has no operationalization that could detect it — the claim is ill-posed at this level, not merely unconfirmed. The formal apparatus survives as a consistent *weighted generalization of Shannon*; the novel-measurable claim does not.

The full pre-registered lab notebook is [`pre_registration.md`](pre_registration.md); the operational anatomy is `coherence_operational_skeleton.md`.

## The formal core (theorems)

A per-symbol weight `w(x) ∈ [0,1]` is placed on Shannon's quantities:

- **Coherence entropy** `H_w(X) = Σ p(x) w(x) [−log p(x)]` and **weighted mutual information** `I_w(X;Y) = Σ p(x,y) w(x) log[p(x,y) / (p(x) p(y))]`. Both **reduce exactly to their Shannon counterparts at `w ≡ 1`** — the boundary condition enforced empirically by `tests/test_shannon_recovery.py`.
- **Coherence-Capacity Theorem:** `C_C = max_p I_w(X;Y)` over the input simplex; at `w ≡ 1` it recovers the ordinary Shannon channel capacity (verified on the BSC and Z-channel). *(Erratum on record: the paper's closed-form Binary-Coherence-Channel value `0.5(1+ε)` is `I_w` at the uniform input — a lower bound, not the maximum.)*
- **Selective-Compression Theorem (repaired):** the paper's original Theorem 5.1 — that the minimum code length preserving every `w(x) > δ` symbol equals `H_w(X)` — is **unsound for non-constant `w`** (it holds only at `w ≡ 1`). `H_w` is recast as a "bits that matter" *measure*, not a compression rate. The corrected, achievable floor is the **merged-source entropy `H(Z)`**: reproduce every `w(x) > δ` symbol exactly and collapse the rest into a single don't-care token; this reduces to Shannon `H(X)` at the boundary `S_δ = X`.

**Status:** a consistent *weighted generalization* of Shannon (prior art: weighted entropy, Belis–Guiașu 1968; cost-constrained coding) — internally consistent, with the selective-compression theorem repaired as above. The entire novelty rests on the **induced weight** `w = σ(β·ρ)`, with `ρ` a compression/MDL relevance (the codelength increase when a symbol is ablated). Everything else is a standard form (logistic squashing, logistic/autocatalytic dynamics, a Gibbs choice rule, dimensional RG scaling) with a coherence symbol substituted in — see `coherence_operational_skeleton.md`.

Two theorems made the program falsifiable:
- **`K_comp = affine(MI)`** — for a fixed alphabet, the analytic (KT) compression coupling equals `N·MI − const`, hence rank-equivalent to mutual information.
- **Order-collapse generalization** — the KT codelength of a *k*-way joint is `N·(order-k information) + penalty`; any fixed-order compression coupling equals the corresponding information statistic. Higher order relocates the identity, it does not escape it.

## The empirical arc — tested → found

| stage | test | outcome |
|---|---|---|
| v0.6 formal + selective compression | do the weighted theorems hold and reduce to Shannon? | **VERIFIED** (capacity on BSC/Z); selective-compression theorem **repaired** — its original `H_w` floor is unsound for non-constant `w`, corrected to `H(Z)` |
| v0.7.0–0.7.1 D1 synthetic + R1 persistence | do the proxies recover *planted* structure? | **VERIFIED — internal validity only** (recovers what is planted; cannot show coherence is a natural kind) |
| v0.7.2 D2 proteins (within-domain) | does the induced edge-weight beat the field's MI coevolution construct? | **FALSIFIED** — it *is* that construct; `K_comp = affine(MI)`, a theorem |
| v0.7.3 flow object (cross-scale / RG escape) | does a renormalization-flow object capture cross-scale structure MI misses? | **CLOSED** — the corpus "RG flow" is dimensional analysis, not Wilsonian RG; the apparatus recovered only a generic timescale label |
| v0.7.3 D-cal-w synthetic | does the weight carry structure beyond its full statistical base? | **deflationary** — reduces to the base (base tuned to the plant: an SMB illustration) |
| v0.7.3 D-cal-w real (Moby Dick × human chr22) | does the weight beat a *blind* statistical base on real, non-stationary, disjoint-prior data? | **FALSIFIED / ill-posed** — every "beyond-base" signal was an estimator/representation artifact |

## The result — the terminal close

The induced weight reduces to statistical information across every operationalization, **necessarily**: it is built from compression/predictive relevance, so it *is* an entropy-rate estimator, and anything a statistical estimator measures is statistical by construction. The wall appeared three times:

1. **Analytic** — `K_comp = affine(MI)` (theorem; D2).
2. **Entropy-rate-estimator** — a real compressor's codelength and any explicit `−log P` model are not entropy-rate-class-matched at finite scale (the LZ-vs-PPM fairness gate fails in opposite directions on text vs DNA).
3. **Combinatorial-statistic** — a compressor's per-position relevance does not cleanly reduce to the sequence's longest-match statistic either; the residue is compressor-implementation artifact and long-range repeat placement — the sequence's own statistics, not an emergent quantity.

**Honest scope.** This is a *theory-led* close, not a clean finite-scale empirical equality — "the statistical information at a position" is estimator-dependent, so there is nothing unique to confirm `w` equals. It rests on **Shannon–McMillan–Breiman** (a universal compressor's rate → the entropy rate for stationary sources), the **exhaustion of operationalizations** above, and the **ill-posedness** of the alternative. No result reopened it: every "escape-leaning" signal was traced to a mismatch and none survived a statistics-matched null.

## What holds, what was falsified

**Holds / verified:** the coherence-weighted information theorems, as a consistent *generalization of Shannon* (with the selective-compression theorem repaired above); the induced-weight pipeline as a faithful operationalization; synthetic internal-validity calibrations (D1).

**Falsified / closed:** coherence as a *novel measurable beyond information* (within-domain D2, cross-scale flow object, cross-domain D-cal-w); the *compression-relevance ≠ statistical-information* crack (asymptotically empty by SMB; finitely, only estimator artifacts).

## Why the negatives are trustworthy

Every stage was **pre-registered** (forks fixed before the run, append-only), tested against **structured-noise nulls**, and had every load-bearing number **independently re-derived from scratch**. Confounds and amendments are recorded in [`pre_registration.md`](pre_registration.md) rather than smoothed away.

## Scope

CIT is the **measurable** arm only. The framework's value as a *unifying conceptual frame*, and its semiotic/applied readings, are not measurable claims and are out of scope here — neither verified nor falsified. What is settled is narrow and precise: *as a measurable quantity, coherence is statistical information.*

## Repo map

- [`pre_registration.md`](pre_registration.md) — the pre-registered lab notebook (every test, result, confound, amendment).
- `coherence_operational_skeleton.md` — equation/theorem inventory + operational anatomy.
- `cit/` — the library; `scripts/` — the experiments (D1, D2 relational, the D-cal cross-domain series, the real-domain apparatus); `design/` — the cross-domain design notes; `tests/` — unit + property tests.

## Quick start

```bash
git clone git@github.com:benjaminjamesgit/coherence-information.git
cd coherence-information
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Minimal usage — the formal core and its boundary condition:

```python
import numpy as np
from cit.information import H, H_w, I_w

p = np.array([0.5, 0.3, 0.15, 0.05])
w = np.array([1.0, 0.8, 0.5, 0.1])

print(H(p))                          # Shannon entropy in bits
print(H_w(p, w))                     # Coherence-weighted entropy
print(H_w(p, np.ones(4)) == H(p))    # True — the w ≡ 1 boundary condition
```

Induce weights from data (the v0.2 pipeline `stream → Ĉ → ρ → w`, pre-registered `β = 4.0`):

```python
import numpy as np
from cit.data.synthetic import labeled_coherence_stream
from cit.induce import induce_weights

stream, labels = labeled_coherence_stream(
    n_steps=20_000, n_coherent=2, n_noise=3,
    rng=np.random.default_rng(42),
)
result = induce_weights(stream, alphabet_size=5, rng=np.random.default_rng(123))
# Coherence-bearing symbols → w > 0.5, noise symbols → w < 0.5.
```

## Theoretical references

The implementation follows the formal definitions and pipeline specifications in the following papers, archived on PhilPapers:

- James, B. (2025). *Beyond Shannon: Coherence Information Theory and the Future of Communication.* https://philpapers.org/rec/JAMBSC
- James, B. (2025). *Formal Foundations of Coherence Information Theory: Capacity and Compression Theorems.* https://philpapers.org/rec/JAMFFO-2
- James, B. (2026). *Engineering Induced Coherence Weights for Coherence Information Theory.* https://philpapers.org/rec/JAMEIC-2
- James, B. (2026). *Formal Foundation of Induced Coherence Weights: Compression-based Coherence and Operational Information Measures.* https://philpapers.org/rec/JAMFFO3

Where the implementation found a source theorem unsound (the Selective-Compression Theorem) or a closed form in error (the Sec 6 capacity erratum), the corrected statement is the one above and in [`pre_registration.md`](pre_registration.md).

## Reproducibility

This project follows pre-registered protocols: random seeds, the weight-mapping sensitivity parameter `β`, and threshold values are committed in [`pre_registration.md`](pre_registration.md) **before any results are produced**. The framework is falsifiable in the sense of James (2026) only if commitments precede outcomes; that file is the structural record.

## License

Apache License, Version 2.0. See [LICENSE](LICENSE).

## Citation

If you use this implementation in academic work, please cite both the software and the underlying papers. See [`CITATION.cff`](CITATION.cff) for the structured citation entry.
