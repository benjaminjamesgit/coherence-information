"""Shapley-value coherence ablation — operator A₂.

For each candidate symbol x, samples ``n_coalitions`` random non-empty
coalitions S from (alphabet \\ {x}). For each coalition:

- ``stream_with``  — keep (S ∪ {x}) intact; replace positions of all
  other symbols with uniform draws from (S ∪ {x}).
- ``stream_without`` — keep S intact; replace positions of all other
  symbols with uniform draws from S.

The Shapley relevance estimate is the mean marginal contribution:

    ρ(x) ≈ 𝔼_{S ~ random non-empty}[Ĉ(stream_with) − Ĉ(stream_without)]

Interpretation, per cit_engineering.pdf:
- ρ(x) > 0  : x contributes to coherence on average across coalitions.
- ρ(x) ≈ 0  : x is coherence-neutral.
- ρ(x) < 0  : x is coherence-negative.

The replace-with-uniform ablation form matches that of leave-one-out
ablation so cross-ablation comparisons (Spearman ρ between A₁ and A₂)
are on equal operator-form footing.

The v0.4 pre-registration commits to ``n_coalitions = 64`` per
Metacoherence Appendix A.2.

Note on centering
-----------------
The replace-with-uniform-from-kept-set ablation form is chosen to match
the operator used by ``leave_one_out_ablation``, so cross-ablation
agreement tests probe the ablation *strategy* (LOO vs. Shapley sampling)
rather than operator-form drift. Under this operator, adding any symbol
to the kept set enlarges the replacement alphabet at ablated positions,
which mechanically raises entropy there and reduces the proxy. This
"dilution penalty" pushes raw Shapley marginals negative for every
symbol regardless of structural relevance. The rank order across
symbols still encodes relevance — coherence-bearing symbols offset the
dilution penalty more than noise — but absolute signs do not match the
LOO convention.

By default (``center=True``) the function subtracts the cohort-mean raw
estimate, anchoring ρ at zero and recovering canonical signs in the
LOO sense: ρ(x) > 0 iff x is relatively coherence-bearing within its
cohort. Set ``center=False`` to expose raw Shapley estimates for
diagnostic comparison.

References
----------
James, B. (2026). Metacoherence. PhilPapers, Appendix A.2 (A₂ pseudocode).
James, B. (2026). Engineering Induced Coherence Weights for Coherence
    Information Theory. PhilPapers, §"Relevance by ablation".
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cit.proxies.predictive_logloss import predictive_logloss_proxy

__all__ = ["shapley_ablation"]


def _replace_outside_keep_set(
    stream: NDArray[np.int64],
    keep_set: NDArray[np.int64],
    rng: np.random.Generator,
) -> NDArray[np.int64]:
    """Replace stream positions not in keep_set with uniform draws from keep_set."""
    if keep_set.size == 0:
        raise ValueError("keep_set must be non-empty.")
    mask = ~np.isin(stream, keep_set)
    n_replace = int(mask.sum())
    if n_replace == 0:
        return stream
    out = stream.copy()
    out[mask] = rng.choice(keep_set, size=n_replace, replace=True)
    return out


def shapley_ablation(
    stream: ArrayLike,
    symbols_to_ablate: Iterable[int] | None = None,
    alphabet_size: int | None = None,
    proxy: Callable[[Any, int], float] = predictive_logloss_proxy,
    n_coalitions: int = 64,
    center: bool = True,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Compute Shapley-value coherence relevance ρ(x) per symbol.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 2.
    symbols_to_ablate : iterable of int, optional
        Symbols whose Shapley ρ to compute. If None, every symbol that
        appears in the stream is scored.
    alphabet_size : int, optional
        Size of the alphabet K. If None, inferred as ``stream.max() + 1``.
    proxy : callable, optional
        Coherence proxy accepting ``(stream, alphabet_size)`` and
        returning a float in [0, 1]. Default: predictive_logloss_proxy.
    n_coalitions : int, optional
        Number of Monte Carlo coalition samples per symbol. Default 64
        per v0.4 pre-registration.
    rng : np.random.Generator, optional
        Random generator for both coalition sampling and the
        replace-with-uniform ablation. Pass a seeded generator for
        reproducibility.

    Returns
    -------
    dict with keys:
        ``'c_baseline'`` : float
            Coherence proxy on the unaltered stream.
        ``'c_ablated'`` : dict[int, float]
            Implied ablated Ĉ per symbol, defined as
            ``c_baseline − rho[x]`` for API parity with
            ``leave_one_out_ablation``.
        ``'rho'`` : dict[int, float]
            Shapley relevance estimate ρ(x).
        ``'symbols'`` : list[int]
            Sorted symbols that were scored.
        ``'n_coalitions'`` : int
            Number of coalition samples used.

    Notes
    -----
    Computational cost is O(K · n_coalitions) proxy evaluations
    (2 per coalition). With K = 5 and n_coalitions = 64, this is
    640 proxy calls — typically a few seconds for 20k-length streams.
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
    if n_coalitions < 1:
        raise ValueError(f"n_coalitions must be >= 1 (got {n_coalitions}).")

    if symbols_to_ablate is None:
        symbols_list = sorted(int(x) for x in np.unique(s))
    else:
        symbols_list = sorted(set(int(x) for x in symbols_to_ablate))

    if rng is None:
        rng = np.random.default_rng()

    c_baseline = float(proxy(s, alphabet_size))
    all_symbols = np.arange(alphabet_size, dtype=np.int64)

    rho: dict[int, float] = {}
    c_ablated: dict[int, float] = {}

    for x in symbols_list:
        others = all_symbols[all_symbols != x]
        if others.size == 0:
            # Unreachable given alphabet_size >= 2, but defensive.
            rho[x] = 0.0
            c_ablated[x] = c_baseline
            continue
        marginals = np.empty(n_coalitions, dtype=np.float64)
        for i in range(n_coalitions):
            # Sample a non-empty coalition from `others`.
            coalition_size = int(rng.integers(1, others.size + 1))
            idx = rng.choice(others.size, size=coalition_size, replace=False)
            coalition = others[idx]

            # stream_with: keep coalition ∪ {x}
            keep_with = np.concatenate([coalition, np.array([x], dtype=np.int64)])
            stream_with = _replace_outside_keep_set(s, keep_with, rng)

            # stream_without: keep coalition
            stream_without = _replace_outside_keep_set(s, coalition, rng)

            c_with = float(proxy(stream_with, alphabet_size))
            c_without = float(proxy(stream_without, alphabet_size))
            marginals[i] = c_with - c_without

        rho[x] = float(marginals.mean())

    if center and rho:
        mean_rho = sum(rho.values()) / len(rho)
        rho = {x: rho[x] - mean_rho for x in rho}

    c_ablated = {x: c_baseline - rho[x] for x in symbols_list}

    return {
        "c_baseline": c_baseline,
        "c_ablated": c_ablated,
        "rho": rho,
        "symbols": symbols_list,
        "n_coalitions": n_coalitions,
        "centered": center,
    }
