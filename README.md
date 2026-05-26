# coherence-information

[![tests](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml/badge.svg)](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20399412.svg)](https://doi.org/10.5281/zenodo.20399412)

Open-source Python implementation of **Coherence-Weighted Entropy** and the **Coherence Information Theory (CIT)** pipeline.

## What this is

CIT extends Shannon's information theory by attaching a bounded weight `w(x) ∈ [0, 1]` to each source symbol, where the weight measures that symbol's contribution to recursive structural stability. The three core formal quantities:H(X)        = -Σ p(x) log p(x)                          (Shannon entropy)
H_w(X)      = Σ p(x) w(x) [-log p(x)]                   (coherence-weighted entropy)
I_w(X; Y)   = Σ p(x,y) w(x) log[p(x,y) / p(x) p(y)]     (coherence-weighted MI)### The boundary condition

When `w(x) = 1` for all x, every coherence-weighted quantity collapses exactly to its Shannon counterpart. This is what licenses CIT as a **generalization** of classical information theory, not a replacement.

The Shannon-recovery test in `tests/test_shannon_recovery.py` enforces this collapse empirically across uniform, skewed, near-deterministic, and sample-based distributions, plus the analogous collapse for mutual information.

### Where w(x) comes from

Weights can be user-supplied for direct use of `H_w` and `I_w`, or **induced from data** via the v0.2 pipeline from James (2026):stream → Ĉ (predictive log-loss proxy) → ρ(x) (leave-one-out ablation) → w(x) = σ(β · ρ(x)) `cit.induce.induce_weights` orchestrates the full pipeline with the pre-registered β = 4.0. Proxy and ablation operators are deliberately swappable; the v0.3 roadmap adds compression-delta proxies (form A), Shapley ablation (k=64 coalitions), and the K₁–K₅ estimator robustness harness.

## Status

| Version | Contents |
|---------|----------|
| **v0.4** *(current)* | Shapley ablation (A₂, k=64, cohort-mean centered); cross-ablation convergence invariants (per-symbol sign agreement + Spearman ρ ≥ 0.7 across A₁ and A₂, Metacoherence §3.1 R2 at the ablation axis); 77 tests |
| v0.3 | Compression-delta proxy (form A / K₁) via zstd; cross-proxy validation invariants (Spearman ρ ≥ 0.7 across form B and K₁); 69 tests |
| v0.2 | Predictive log-loss proxy (form B); replace-with-uniform leave-one-out ablation (A₁); induction pipeline `stream → Ĉ → ρ → w`; labeled synthetic substrate; 57 tests |
| v0.1 | Formal quantities `H`, `H_w`, `I_w`; synthetic test substrate; Shannon-recovery spine test; 27 tests |
| v0.5 *(planned)* | K₂ (n-gram MDL), K₃ (transformer prequential), K₄ (MDL-HMM), K₅ (Lempel parsing, non-coding registrant); A₃ correlation-cluster ablation; multi-feature synthetic substrate; full {K} × {A} robustness harness |
| v0.6 *(planned)* | Coherence capacity estimator `C_C = max_{p(x)} I_w(X;Y)`; weighted typical-set coder + Selective Compression empirics |
| v0.7 *(planned)* | Cross-domain validation architecture (Metacoherence); M5 admissibility gate |

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
