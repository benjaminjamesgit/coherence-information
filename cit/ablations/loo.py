"""Leave-one-out (LOO) coherence ablation — operator A₁.

For each candidate symbol x, replace every occurrence of x with a
uniformly random symbol drawn from the alphabet excluding x, then
recompute the coherence proxy on the modified stream. The coherence
relevance is:

    ρ(x) = Ĉ(X) − Ĉ(X with each x replaced by uniform non-x noise)

Interpretation, per cit_engineering.pdf:
- ρ(x) > 0  : removing x reduces predictability → x is coherence-bearing.
- ρ(x) ≈ 0  : removing x has no measurable effect → coherence-neutral.
- ρ(x) < 0  : removing x INCREASES predictability → x is coherence-negative.

The v0.2 pre-registration commits to leave-one-out semantics; we
instantiate the ablation by replace-with-uniform. Pure removal was
considered but biases the proxy on shrinking alphabets: dropping any
symbol concentrates the contracted stream on the remaining predictable
structure, inverting the canonical sign convention. Replacement
preserves stream length and destroys the temporal role x played
without distorting the marginal predictor.

A₂ (Shapley, k=64 sampled coalitions) and A₃ (correlation-cluster
group ablation) land in v0.3.

References
----------
James, B. (2026). Engineering Induced Coherence Weights for Coherence
    Information Theory. PhilPapers, §"Relevance by ablation: ρ(x)".
James, B. (2026). Formal Foundation of Induced Coherence Weights.
    PhilPapers, Step C.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from cit.proxies.predictive_logloss import predictive_logloss_proxy

__all__ = ["leave_one_out_ablation"]


def leave_one_out_ablation(
    stream: ArrayLike,
    symbols_to_ablate: Iterable[int] | None = None,
    alphabet_size: int | None = None,
    proxy: Callable[[Any, int], float] = predictive_logloss_proxy,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Compute leave-one-out coherence relevance ρ(x) per symbol.

    Uses replace-with-uniform ablation: for each occurrence of the
    target symbol x, substitute a uniformly drawn symbol from the
    alphabet excluding x. Stream length is preserved.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 2.
    symbols_to_ablate : iterable of int, optional
        Symbols whose ρ to compute. If None, every symbol that appears in
        the stream is ablated once.
    alphabet_size : int, optional
        Size of the alphabet K. If None, inferred as ``stream.max() + 1``.
    proxy : callable, optional
        Coherence proxy accepting ``(stream, alphabet_size)`` and
        returning a float in [0, 1]. Default: predictive_logloss_proxy.
    rng : np.random.Generator, optional
        Random generator for the replacement draw. If None, a fresh
        default_rng() is created. Pass a seeded generator for
        reproducibility.

    Returns
    -------
    dict with keys:
        ``'c_baseline'`` : float
            Coherence proxy on the unaltered stream.
        ``'c_ablated'`` : dict[int, float]
            Coherence proxy on each ablated stream.
        ``'rho'`` : dict[int, float]
            ρ(x) = c_baseline − c_ablated[x].
        ``'symbols'`` : list[int]
            Sorted list of symbols that were ablated.
    """
    s = np.asarray(stream, dtype=np.int64)
    if s.ndim != 1 or s.size < 2:
        raise ValueError(
            f"stream must be 1D with length >= 2 (got shape {s.shape})."
        )
    if alphabet_size is None:
        alphabet_size = int(s.max()) + 1
    if alphabet_size < 2:
        raise ValueError(f"alphabet_size must be >= 2 (got {alphabet_size}).")

    if symbols_to_ablate is None:
        symbols_list = sorted(int(x) for x in np.unique(s))
    else:
        symbols_list = sorted(set(int(x) for x in symbols_to_ablate))

    if rng is None:
        rng = np.random.default_rng()

    c_baseline = float(proxy(s, alphabet_size))

    c_ablated: dict[int, float] = {}
    rho: dict[int, float] = {}
    for x in symbols_list:
        mask = s == x
        n_to_replace = int(mask.sum())
        if n_to_replace == 0:
            # Symbol doesn't appear; ablation is a no-op.
            c_ablated[x] = c_baseline
            rho[x] = 0.0
            continue
        other_symbols = np.array(
            [i for i in range(alphabet_size) if i != x], dtype=np.int64
        )
        replacements = rng.choice(other_symbols, size=n_to_replace, replace=True)
        ablated = s.copy()
        ablated[mask] = replacements
        c_x = float(proxy(ablated, alphabet_size))
        c_ablated[x] = c_x
        rho[x] = c_baseline - c_x

    return {
        "c_baseline": c_baseline,
        "c_ablated": c_ablated,
        "rho": rho,
        "symbols": symbols_list,
    }
