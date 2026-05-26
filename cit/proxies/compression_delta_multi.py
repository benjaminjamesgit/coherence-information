"""K_1 multi-feature proxy: zstd compression ratio on byte-packed stream.

Implements `compression_delta_proxy_multi`, the v0.5 multi-feature variant
of K_1 (v0.3 `compression_delta_proxy`). Each step encoded as a 2-byte
uint16 with feature 0 as LSB; full byte stream compressed with zstd at
level 3. zstd handles joint correlation structure natively through its
dictionary mechanism -- no explicit dependency modeling required.

Per design/multi_feature_substrate.md (Q4, Q7, locked 2026-05-26):
- Encoding: uint16 per step, 10 active bits + 6 padding zeros (for n=10)
- Compressor: zstd level 3 (matches v0.3 K_1 compressor spec)
- Formula: C_hat = 1 - len(compressed) / len(uncompressed), clipped to [0, 1]
"""

from __future__ import annotations

import numpy as np
import zstandard

__all__ = ["compression_delta_proxy_multi"]

ZSTD_LEVEL = 3


def compression_delta_proxy_multi(stream, n_features=None):
    """K_1 multi-feature: zstd compression ratio on byte-packed stream.

    Parameters
    ----------
    stream : ndarray of shape (n_steps, n_features), binary uint8
        Multi-feature substrate stream.
    n_features : int, optional
        Must match stream.shape[1] if provided. Inferred otherwise.

    Returns
    -------
    C_hat : float in [0, 1]
        Coherence estimate from byte-level compression ratio.
        1 = maximally compressible; 0 = incompressible.
    """
    arr = np.asarray(stream, dtype=np.int64)
    if arr.ndim != 2:
        raise ValueError(f"stream must be 2-D; got ndim={arr.ndim}")
    T, n = arr.shape
    if n_features is not None and n_features != n:
        raise ValueError(f"n_features={n_features} != stream.shape[1]={n}")
    if T < 1:
        raise ValueError(f"need at least 1 step; got T={T}")
    if n < 1 or n > 16:
        raise ValueError(
            f"v0.5 K_1 byte encoding supports 1-16 features; got n={n}"
        )

    # Encode each step as a uint16 with feature 0 as LSB.
    # For n < 10, unused high bits are 0; for n = 10, exactly 6 padding zeros.
    weights = (1 << np.arange(n)).astype(np.int64)
    stream_int = (arr * weights).sum(axis=1)
    encoded = stream_int.astype(np.uint16).tobytes()

    cctx = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
    compressed = cctx.compress(encoded)

    C_hat = 1.0 - len(compressed) / len(encoded)
    return float(np.clip(C_hat, 0.0, 1.0))
