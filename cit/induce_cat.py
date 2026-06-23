"""Categorical (alphabet-A) induction pipeline: stream -> C_hat -> rho -> w (v0.7).

The alphabet-A analog of `induce_weights_multi` (cit.induce_multi), for the cross-domain
program. Orchestrates a marginal-relative categorical proxy (cit.proxies.categorical) and a
categorical ablation (cit.ablations.categorical):

    stream_2d (T, n), values in [0, A)
        --> proxy(stream, n, alphabet=A) gives C_hat (scalar)
        --> ablation(stream, proxy_fixed, n, alphabet=A, rng) gives per-feature rho
        --> w(j) = sigmoid(beta * rho(j)),  beta = 4.0 locked from v0.2

The alphabet is fixed once and threaded to BOTH the proxy (so its marginal baseline uses
the true alphabet, not the inferred max+1 of an ablated stream) and the ablation (for the
uniform-over-A replacement). beta carries from v0.2; v0.5 induce_weights_multi is unchanged.
"""

from __future__ import annotations

import numpy as np

from cit.induce_multi import BETA

__all__ = ["induce_weights_cat", "BETA"]


def induce_weights_cat(stream, alphabet=None, *, proxy, ablation, rng=None, beta=BETA):
    """Categorical multi-feature weight induction: stream -> rho -> w.

    Parameters
    ----------
    stream : ndarray (n_steps, n_features), integer in [0, alphabet)
    alphabet : int, optional
        Alphabet size; inferred (max+1) if None. Fixed and threaded to proxy and ablation.
    proxy : callable
        Categorical proxy `proxy(stream_2d, n_features, alphabet=) -> float`.
    ablation : callable
        Categorical ablation accepting positional (stream, proxy_fixed) and keyword
        (n_features=, alphabet=, rng=).
    rng : np.random.Generator | None
        Threaded into the ablation operator.
    beta : float, default 4.0
        Sigmoid steepness, locked at 4.0 by v0.2.

    Returns
    -------
    dict with keys "rho", "w", "c_ablated", "centered" (+ any extra the ablation returns,
    e.g. "clusters" for A3).
    """
    arr = np.asarray(stream)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if alphabet is None:
        alphabet = int(arr.max()) + 1
    if rng is None:
        rng = np.random.default_rng()

    def proxy_fixed(s, nf=None):
        return proxy(s, nf, alphabet=alphabet)

    result = ablation(arr, proxy_fixed, n_features=n, alphabet=alphabet, rng=rng)
    rho = result["rho"]
    w = {f: float(1.0 / (1.0 + np.exp(-beta * v))) for f, v in rho.items()}

    out = {"rho": rho, "w": w, "c_ablated": result["c_ablated"], "centered": result.get("centered", True)}
    if "clusters" in result:
        out["clusters"] = result["clusters"]
    return out
