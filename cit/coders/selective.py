"""Selective compression coder (v0.6.1) -- the corrected Selective Compression
Theorem operationalized.

Background. The paper's Selective Compression Theorem 5.1 (compress to the
coherence entropy H_w while exactly reproducing every symbol with w(x) > delta)
is UNSOUND for non-constant w -- it holds only at w = 1 (see the 2026-06-23
v0.6.1 amendment in pre_registration.md). H_w is a *measure* ("bits that
matter"), not an achievable compression rate.

The corrected, sound theorem (Option A). Under the threshold criterion only the
must-preserve set S_delta = {x : w(x) > delta} need be reproduced exactly. The
fundamental limit is then the entropy of the MERGED source

    Z = (S_delta union {*}),   Z = x for x in S_delta,   Z = * otherwise,

i.e. keep the coherence-bearing symbols distinct and collapse every don't-care
into a single token *. Converse: any uniquely-decodable code reproducing every
S_delta symbol exactly must convey Z losslessly, so L >= H(Z). Achievability: an
entropy coder on Z reaches L <= H(Z) + eps. Boundary: when S_delta = X (e.g.
w = 1, or delta < min_x w(x)) the merge is trivial, Z = X, and H(Z) = H(X) --
the coder collapses to ordinary Shannon lossless coding.

This module implements the coder as "merge -> entropy-code":
  - PRIMARY (theorem-faithful): a static 32-bit arithmetic coder (Witten-Neal-
    Cleary) on the merged stream, whose rate approaches H(Z) + eps. Deterministic
    and bit-exact (the round-trip is verified in tests/test_selective_coder.py).
  - PRACTICAL variant: zstd on the merged byte stream (reuses the K1 encoding
    idea), reported alongside.

H(Z) is partition-driven: it depends on S_delta (via delta), not on the graded
weight values. The graded weights live in the H_w *measure*
(cit.information.coherence_weighted_entropy), not in the compression rate.

References
----------
James, B. (2025). Capacity and Compression Theorems. PhilPapers. (Thm 5.1,
    repaired here; see pre_registration.md 2026-06-23 v0.6.1 amendment.)
"""

from __future__ import annotations

import struct

import numpy as np
import zstandard as zstd
from numpy.typing import ArrayLike, NDArray

from cit.information import shannon_entropy

__all__ = [
    "must_preserve_indices",
    "merged_source_entropy",
    "selective_encode",
    "selective_decode",
    "selective_encode_zstd",
    "selective_decode_zstd",
    "rate_bits_per_symbol",
    "ZSTD_LEVEL",
]

# Locked practical-variant compressor level (v0.6.1).
ZSTD_LEVEL = 19

# --- 32-bit Witten-Neal-Cleary arithmetic coder constants ---
_CODE_BITS = 32
_TOP = (1 << _CODE_BITS) - 1
_HALF = 1 << (_CODE_BITS - 1)
_QUARTER = 1 << (_CODE_BITS - 2)
_THREE_Q = 3 << (_CODE_BITS - 2)


# ---------------------------------------------------------------------------
# bit I/O
# ---------------------------------------------------------------------------
class _BitWriter:
    __slots__ = ("_out", "_acc", "_n")

    def __init__(self) -> None:
        self._out = bytearray()
        self._acc = 0
        self._n = 0

    def bit(self, b: int) -> None:
        self._acc = (self._acc << 1) | (b & 1)
        self._n += 1
        if self._n == 8:
            self._out.append(self._acc)
            self._acc = 0
            self._n = 0

    def bit_plus_pending(self, b: int, pending: int) -> None:
        self.bit(b)
        nb = b ^ 1
        for _ in range(pending):
            self.bit(nb)

    def getvalue(self) -> bytes:
        if self._n > 0:
            self._acc <<= 8 - self._n
            self._out.append(self._acc)
            self._acc = 0
            self._n = 0
        return bytes(self._out)


class _BitReader:
    __slots__ = ("_d", "_pos", "_len")

    def __init__(self, data: bytes) -> None:
        self._d = data
        self._pos = 0
        self._len = len(data) * 8

    def bit(self) -> int:
        if self._pos >= self._len:
            return 0  # past end: the WNC flush is padded with zeros
        byte = self._d[self._pos >> 3]
        b = (byte >> (7 - (self._pos & 7))) & 1
        self._pos += 1
        return b


def _cumulative(freqs: list[int]) -> list[int]:
    cum = [0] * (len(freqs) + 1)
    for i, f in enumerate(freqs):
        cum[i + 1] = cum[i] + f
    return cum


def _encode_arithmetic(labels, freqs: list[int]) -> bytes:
    total = sum(freqs)
    cum = _cumulative(freqs)
    low, high, pending = 0, _TOP, 0
    bw = _BitWriter()
    for s in labels:
        s = int(s)
        rng = high - low + 1
        high = low + (rng * cum[s + 1]) // total - 1
        low = low + (rng * cum[s]) // total
        while True:
            if high < _HALF:
                bw.bit_plus_pending(0, pending)
                pending = 0
            elif low >= _HALF:
                bw.bit_plus_pending(1, pending)
                pending = 0
                low -= _HALF
                high -= _HALF
            elif low >= _QUARTER and high < _THREE_Q:
                pending += 1
                low -= _QUARTER
                high -= _QUARTER
            else:
                break
            low <<= 1
            high = (high << 1) | 1
    pending += 1
    bw.bit_plus_pending(0 if low < _QUARTER else 1, pending)
    return bw.getvalue()


def _decode_arithmetic(data: bytes, freqs: list[int], n: int) -> NDArray[np.int64]:
    total = sum(freqs)
    cum = _cumulative(freqs)
    br = _BitReader(data)
    low, high, value = 0, _TOP, 0
    for _ in range(_CODE_BITS):
        value = (value << 1) | br.bit()
    out = np.empty(n, dtype=np.int64)
    for i in range(n):
        rng = high - low + 1
        scaled = (((value - low + 1) * total) - 1) // rng
        s = 0
        while cum[s + 1] <= scaled:
            s += 1
        out[i] = s
        high = low + (rng * cum[s + 1]) // total - 1
        low = low + (rng * cum[s]) // total
        while True:
            if high < _HALF:
                pass
            elif low >= _HALF:
                low -= _HALF
                high -= _HALF
                value -= _HALF
            elif low >= _QUARTER and high < _THREE_Q:
                low -= _QUARTER
                high -= _QUARTER
                value -= _QUARTER
            else:
                break
            low <<= 1
            high = (high << 1) | 1
            value = (value << 1) | br.bit()
    return out


# ---------------------------------------------------------------------------
# merge + theorem quantities
# ---------------------------------------------------------------------------
def must_preserve_indices(weights: ArrayLike, delta: float) -> list[int]:
    """S_delta = {x : w(x) > delta}, sorted ascending."""
    w = np.asarray(weights, dtype=np.float64)
    return [int(x) for x in range(w.shape[0]) if w[x] > delta]


def merged_source_entropy(probs: ArrayLike, weights: ArrayLike, delta: float) -> float:
    """H(Z): entropy of the merged source (the corrected compression floor).

    Z keeps each S_delta symbol distinct and collapses all don't-cares into one
    token of probability 1 - p(S_delta). Equals H(X) when S_delta = X.
    """
    p = np.asarray(probs, dtype=np.float64)
    S = must_preserve_indices(weights, delta)
    q = float(sum(p[x] for x in S))
    pz = [float(p[x]) for x in S]
    if 1.0 - q > 1e-15:
        pz.append(1.0 - q)
    return shannon_entropy(np.array(pz))


def _merge_labels(stream: NDArray, S: list[int]) -> NDArray[np.int64]:
    """Map each symbol to its S-label (0..|S|-1), or to the STAR token |S|."""
    label_of = {x: i for i, x in enumerate(S)}
    star = len(S)
    return np.fromiter(
        (label_of.get(int(v), star) for v in stream),
        dtype=np.int64,
        count=len(stream),
    )


def _placeholder_symbol(S: list[int], alphabet_size: int) -> int:
    """A fixed don't-care symbol emitted for collapsed (*) positions."""
    sset = set(S)
    for x in range(alphabet_size):
        if x not in sset:
            return x
    return 0  # S_delta == X: no * positions occur; value is irrelevant


def _pack_header(n, S, freqs, placeholder) -> bytes:
    parts = [struct.pack("<III", n, len(S), placeholder)]
    parts += [struct.pack("<I", int(x)) for x in S]
    parts += [struct.pack("<I", int(f)) for f in freqs]
    return b"".join(parts)


def _unpack_header(blob, off):
    n, n_s, placeholder = struct.unpack_from("<III", blob, off)
    off += 12
    S = []
    for _ in range(n_s):
        (v,) = struct.unpack_from("<I", blob, off)
        off += 4
        S.append(v)
    freqs = []
    for _ in range(n_s + 1):
        (f,) = struct.unpack_from("<I", blob, off)
        off += 4
        freqs.append(f)
    return n, S, freqs, placeholder, off


# ---------------------------------------------------------------------------
# arithmetic coder (PRIMARY, theorem-faithful)
# ---------------------------------------------------------------------------
def selective_encode(stream: ArrayLike, weights: ArrayLike, delta: float) -> bytes:
    """Encode `stream` with the merge -> arithmetic-code selective coder.

    Losslessly preserves every symbol with w(x) > delta; collapses all
    don't-cares. The encoded blob is self-contained (header carries the
    merged-source model and the S_delta -> original-symbol map).
    """
    stream = np.asarray(stream).ravel()
    w = np.asarray(weights, dtype=np.float64)
    K = w.shape[0]
    S = must_preserve_indices(w, delta)
    z = _merge_labels(stream, S)
    freqs = np.bincount(z, minlength=len(S) + 1).astype(np.int64).tolist()
    placeholder = _placeholder_symbol(S, K)
    payload = _encode_arithmetic(z, freqs)
    header = _pack_header(len(stream), S, freqs, placeholder)
    return header + struct.pack("<I", len(payload)) + payload


def selective_decode(blob: bytes) -> NDArray[np.int64]:
    """Decode a `selective_encode` blob.

    Reproduces every S_delta symbol exactly; emits the fixed placeholder for
    every collapsed (*) position (don't-cares are not reconstructed).
    """
    n, S, freqs, placeholder, off = _unpack_header(blob, 0)
    (plen,) = struct.unpack_from("<I", blob, off)
    off += 4
    payload = blob[off : off + plen]
    labels = _decode_arithmetic(payload, freqs, n)
    # label -> original symbol; the STAR label (= len(S)) maps to the placeholder
    s_arr = np.array(S + [placeholder], dtype=np.int64)
    return s_arr[labels]


# ---------------------------------------------------------------------------
# zstd coder (PRACTICAL variant)
# ---------------------------------------------------------------------------
def selective_encode_zstd(stream: ArrayLike, weights: ArrayLike, delta: float) -> bytes:
    """Merge -> zstd. Practical variant; alphabet of Z must be <= 256."""
    stream = np.asarray(stream).ravel()
    w = np.asarray(weights, dtype=np.float64)
    K = w.shape[0]
    S = must_preserve_indices(w, delta)
    if len(S) + 1 > 256:
        raise ValueError("zstd variant requires merged alphabet <= 256 symbols.")
    z = _merge_labels(stream, S).astype(np.uint8)
    placeholder = _placeholder_symbol(S, K)
    comp = zstd.ZstdCompressor(level=ZSTD_LEVEL).compress(z.tobytes())
    header = _pack_header(len(stream), S, [0] * (len(S) + 1), placeholder)
    return header + struct.pack("<I", len(comp)) + comp


def selective_decode_zstd(blob: bytes) -> NDArray[np.int64]:
    n, S, _freqs, placeholder, off = _unpack_header(blob, 0)
    (clen,) = struct.unpack_from("<I", blob, off)
    off += 4
    comp = blob[off : off + clen]
    z = np.frombuffer(zstd.ZstdDecompressor().decompress(comp), dtype=np.uint8)
    star = len(S)
    s_arr = np.array(S + [placeholder], dtype=np.int64)
    return s_arr[z.astype(np.int64)]


def rate_bits_per_symbol(blob: bytes, n: int) -> float:
    """Total encoded size in bits per source symbol (header included)."""
    return 8.0 * len(blob) / n
