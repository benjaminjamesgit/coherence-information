"""K_5 multi-feature proxy: LZ76 phrase count on bit-unpacked stream.

Implements `lempel_parsing_proxy`, the v0.5.2 sequence-parsing-complexity
proxy. Uses the shared K_1 multi byte encoder (`encode_multi_to_bytes`)
and unpacks to bits via `numpy.unpackbits` before LZ76 parsing -- per the
2026-05-26 bit-level parsing amendment.

Family identity: non-coding pattern counting. K_5 shares its underlying
encoded information with K_1 multi (same bits, same encoder) but never
invokes zstd or any entropy coder. The K_1 vs K_5 contrast traces to
the parsing/coding boundary, not to representation drift.

Per design/multi_feature_substrate.md K_5 protocol (amended 2026-05-26):
- Encoder: shared with K_1 multi (2-byte-per-step, 10 active + 6 padding)
- Unpack: numpy.unpackbits -> T_bits = 8 * T_bytes = 16 * n_steps
- Parser: LZ76 production complexity, Kaspar-Schuster algorithm, numba JIT
- iid baseline: c_iid = T_bits / log2(T_bits)
- Formula: C_K5 = 1 - c(bit_stream) / c_iid, clipped to [0, 1]

The Kaspar-Schuster state-machine is JIT-compiled via numba.njit. This
makes the otherwise-O(n^2)-worst-case algorithm tractable for n ~ 10^5
to 10^6 bit streams (typical case near-linear under numba, with sub-second
per-call latency on the v0.5 substrate).
"""

from __future__ import annotations

import math
import numpy as np
from numba import njit

from cit.proxies.compression_delta_multi import encode_multi_to_bytes

__all__ = ["lempel_parsing_proxy"]


@njit(cache=True)
def _lz76_complexity(bits):
    """LZ76 production complexity via Kaspar-Schuster (1987), JIT-compiled.

    Reference: Kaspar & Schuster, "Easily calculable measure for the
    complexity of spatiotemporal patterns", Phys. Rev. A 36, 842 (1987).

    Parameters
    ----------
    bits : np.ndarray of uint8
        Sequence of 0/1 values.

    Returns
    -------
    int
        Number of phrases in the LZ76 parse.
    """
    n = len(bits)
    if n == 0:
        return 0
    if n == 1:
        return 1

    c = 1
    l = 1
    i = 0
    k = 1
    k_max = 1

    while True:
        if bits[i + k - 1] == bits[l + k - 1]:
            k += 1
            if l + k > n:
                c += 1
                break
        else:
            if k > k_max:
                k_max = k
            i += 1
            if i == l:
                c += 1
                l += k_max
                if l + 1 > n:
                    break
                i = 0
                k = 1
                k_max = 1
            else:
                k = 1
    return c


def lempel_parsing_proxy(stream, n_features=None):
    """K_5: LZ76 phrase count on bit-unpacked byte encoding.

    Parameters
    ----------
    stream : ndarray of shape (n_steps, n_features), binary uint8
        Multi-feature substrate stream.
    n_features : int, optional
        Must match stream.shape[1] if provided. Inferred otherwise.

    Returns
    -------
    C_K5 : float in [0, 1]
        Coherence estimate from LZ76 phrase count vs uniform-binary
        asymptotic baseline. 1 = maximally compressible/repetitive;
        0 = approaches uniform-random complexity.
    """
    encoded = encode_multi_to_bytes(stream, n_features=n_features)

    byte_arr = np.frombuffer(encoded, dtype=np.uint8)
    bit_arr = np.unpackbits(byte_arr)

    n_bits = len(bit_arr)
    if n_bits < 2:
        return 0.0

    c = _lz76_complexity(bit_arr)
    c_iid = n_bits / math.log2(n_bits)

    C_K5 = 1.0 - c / c_iid
    return float(np.clip(C_K5, 0.0, 1.0))
