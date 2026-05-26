# coherence-information

[![tests](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml/badge.svg)](https://github.com/benjaminjamesgit/coherence-information/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20399413.svg)](https://doi.org/10.5281/zenodo.20399413)

Open-source Python implementation of **Coherence-Weighted Entropy** and the **Coherence Information Theory (CIT)** pipeline.

## What this is

CIT extends Shannon's information theory by attaching a bounded weight `w(x) ∈ [0, 1]` to each source symbol, where the weight measures that symbol's contribution to recursive structural stability. The three core formal quantities:H(X)        = -Σ p(x) log p(x)                          (Shannon entropy)
H_w(X)      = Σ p(x) w(x) [-log p(x)]                   (coherence-weighted entropy)
I_w(X; Y)   = Σ p(x,y) w(x) log[p(x,y) / p(x) p(y)]     (coherence-weighted MI)### The boundary condition

When `w(x) = 1` for all x, every coherence-weighted quantity collapses exactly to its Shannon counterpart. This is what licenses CIT as a **generalization** of classical information theory, not a replacement.

The Shannon-recovery test in `tests/test_shannon_recovery.py` enforces this collapse empirically across uniform, skewed, near-deterministic, and sample-based distributions, plus the analogous collapse for mutual information.

### Where w(x) comes from (planned)

In v0.1 weights are user-supplied. The induction pipeline (`stream → Ĉ → ρ(x) → w(x)`) from James (2026) — proxy coherence via compression-delta or predictive log-loss, symbol relevance by ablation, monotone bounded mapping to `[0, 1]` — lands in v0.2.

## Status

| Version | Contents |
|---------|----------|
| **v0.1** *(current)* | Formal quantities `H`, `H_w`, `I_w`; synthetic test substrate; Shannon-recovery spine test |
| v0.2 *(planned)* | Coherence proxies (compression-delta, predictive log-loss); leave-one-out ablation; induced-weight derivation pipeline |
| v0.3 *(planned)* | Coherence capacity estimator; weighted typical-set coder (Selective Compression empirics); robustness harness across estimator classes K₁–K₅ and ablation operators A₁–A₃ |
| v0.4 *(planned)* | Cross-domain validation architecture (Metacoherence), M5 admissibility gate |

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
