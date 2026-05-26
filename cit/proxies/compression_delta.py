"""Compression-delta coherence proxy — K₁ from Metacoherence §3.1.

Implements proxy form A from cit_engineering.pdf using zstd compression
as the complexity estimator:

    Ĉ = 1 − len(zstd(stream_bytes)) / len(stream_bytes)

Higher values mean more compressible, hence more structurally
predictable. Uniform i.i.d. streams encoded as uint8 carry residual
encoding redundancy (high bits always zero for small alphabets) so
their absolute Ĉ is not 0 — but cross-stream and cross-ablation
*ranking* is what matters for the v0.3 cross-philosophy convergence
test, not absolute values.

The v0.3 pre-registration commits to this proxy as the K₁ estimator
class. The cross-proxy R2 test (Spearman ρ rankings agree between
form A and form B at threshold 0.7) is the operational form of
Metacoherence §3.1's cross-philosophy convergence at the within-domain
level.

References
----------
James, B. (2026). Engineering Induced Coherence Weights for Coherence
    Information Theory. PhilPapers, §"Coherence proxy", form A.
James, B. (2026). Metacoherence. PhilPapers, §3.1 (K₁ specification).
"""

from __future__ import annotations

import numpy as np
import zstandard as zstd
from numpy.typing import ArrayLike

__all__ = [
    "compression_delta_proxy",
    "encode_stream_to_bytes",
]

# zstd level 3 is the library default — fast and effective for most inputs.
_ZSTD_LEVEL = 3


def _smallest_uint_dtype(alphabet_size: int):
    """Smallest unsigned integer dtype that can hold ``alphabet_size`` symbols."""
    if alphabet_size <= 1 << 8:
        return np.uint8
    if alphabet_size <= 1 << 16:
        return np.uint16
    if alphabet_size <= 1 << 32:
        return np.uint32
    return np.uint64


def encode_stream_to_bytes(
    stream: ArrayLike,
    alphabet_size: int | None = None,
) -> bytes:
    """Encode an integer symbol stream into a byte string for compression.

    Uses the smallest unsigned-integer dtype that fits the alphabet:
    uint8 for K ≤ 256, uint16 for K ≤ 65536, etc.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 1. Values must be in [0, alphabet_size).
    alphabet_size : int, optional
        Size of the alphabet K. If None, inferred as ``stream.max() + 1``.

    Returns
    -------
    bytes
        The byte-encoded stream.
    """
    s = np.asarray(stream, dtype=np.int64)
    if s.ndim != 1 or s.size < 1:
        raise ValueError(f"stream must be 1D non-empty (got shape {s.shape}).")
    observed_max = int(s.max())
    if alphabet_size is None:
        alphabet_size = observed_max + 1
    if alphabet_size < 1:
        raise ValueError(f"alphabet_size must be >= 1 (got {alphabet_size}).")
    if int(s.min()) < 0 or observed_max >= alphabet_size:
        raise ValueError(
            f"stream contains symbols outside [0, {alphabet_size})."
        )
    dtype = _smallest_uint_dtype(alphabet_size)
    return s.astype(dtype).tobytes()


def compression_delta_proxy(
    stream: ArrayLike,
    alphabet_size: int | None = None,
) -> float:
    """Coherence proxy via zstd compression ratio (form A / K₁).

    Encodes the stream to bytes using the smallest unsigned dtype that
    fits the alphabet, compresses with zstd, and returns:

        Ĉ = 1 − len(compressed) / len(uncompressed)

    Higher = more compressible = more structurally predictable.

    Parameters
    ----------
    stream : array-like of int
        Symbol stream of length >= 2.
    alphabet_size : int, optional
        Size of the alphabet K. If None, inferred from the stream max.
        Pass explicitly to keep the byte-encoding dtype fixed across
        baseline and ablated streams.

    Returns
    -------
    float
        Coherence proxy Ĉ, clipped to [0, 1]. Clipping handles the
        very-short-stream regime where zstd frame-header overhead can
        push the compression ratio above 1.

    Notes
    -----
    Absolute values are not comparable to predictive-log-loss Ĉ because
    the two proxies operate in different reference frames (byte-level
    entropy coding vs. symbol-level Markov prediction). What is testable
    is *ranking* agreement — verified by the cross-proxy R2 test in
    ``tests/test_cross_proxy_validation.py``.
    """
    s = np.asarray(stream, dtype=np.int64)
    if s.ndim != 1 or s.size < 2:
        raise ValueError(
            f"stream must be 1D with length >= 2 (got shape {s.shape})."
        )
    raw = encode_stream_to_bytes(s, alphabet_size=alphabet_size)
    compressor = zstd.ZstdCompressor(level=_ZSTD_LEVEL)
    compressed = compressor.compress(raw)
    ratio = len(compressed) / len(raw)
    return float(np.clip(1.0 - ratio, 0.0, 1.0))
