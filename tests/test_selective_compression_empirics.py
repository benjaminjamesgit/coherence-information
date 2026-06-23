"""v0.6.2 Selective Compression empirics -- the falsifiable win-margin.

Locks (pre_registration.md, 2026-06-23 v0.6.2 amendment): the corrected
selective coder (v0.6.1, compress to H(Z)) compresses strictly below the
weight-blind lossless rate at ZERO coherence-retention cost on coherence-
structured sources, and the saving VANISHES at the boundary.

Two-sided falsifiable claim, per pre-registered substrate:
  (i)   arithmetic Delta_frac = (rate_blind - rate_selective) / rate_blind
        >= WIN_MARGIN = 0.20  on each STRUCTURED substrate,
  (ii)  every must-preserve symbol (w(x) > delta) reproduced exactly, and
  (iii) Delta = 0 exactly at the boundary (S_delta = X, e.g. w == 1).

Weight-blind baseline = the same coder with delta below all weights (so
S_delta = X, no merge, full lossless coding). zstd savings are logged
(observational; the 0.20 margin is asserted on the arithmetic coder only).

Substrates (locked seeds, N = 100_000): i.i.d., Gilbert-Elliott (memory),
TCUN (toggle-cycle + uniform noise). All fast tier.

References
----------
James, B. (2025). Capacity and Compression Theorems. PhilPapers. (Selective
    Compression, repaired -- see the 2026-06-23 v0.6.1/v0.6.2 amendments.)
"""

from __future__ import annotations

import numpy as np
import pytest

from cit.coders.selective import (
    rate_bits_per_symbol,
    selective_decode,
    selective_encode,
    selective_encode_zstd,
)

N = 100_000
DELTA = 0.5
BLIND_DELTA = -0.1  # below all weights => S_delta = X => no merge (weight-blind)
WIN_MARGIN = 0.20


# ---------------------------------------------------------------------------
# Locked substrate generators (exact seeds/params -> the calibration streams)
# ---------------------------------------------------------------------------
def gen_iid():
    p = np.array([0.5, 0.18, 0.14, 0.1, 0.08])
    return np.random.default_rng(42).choice(5, size=N, p=p)


def gen_gilbert_elliott():
    """2-state memory source: good -> structural {0,1}; bad -> uniform noise."""
    r = np.random.default_rng(1)
    state = 0  # 0 = good, 1 = bad
    out = np.empty(N, dtype=np.int64)
    for i in range(N):
        if r.random() > 0.95:  # self-transition prob 0.95
            state ^= 1
        out[i] = r.choice([0, 1], p=[0.7, 0.3]) if state == 0 else r.choice([2, 3, 4, 5])
    return out


def gen_tcun():
    """Toggle-cycle {0,1} structure with uniform-noise injection."""
    r = np.random.default_rng(2)
    out = np.empty(N, dtype=np.int64)
    tog = 0
    for i in range(N):
        if r.random() < 0.35:  # injection_prob
            out[i] = r.choice([2, 3, 4, 5])
        else:
            out[i] = tog
            tog ^= 1
    return out


SUBSTRATES = {
    "iid": (gen_iid, np.array([1.0, 0.0, 0.0, 0.0, 0.0])),
    "gilbert_elliott": (gen_gilbert_elliott, np.array([1.0, 1.0, 0.0, 0.0, 0.0, 0.0])),
    "tcun": (gen_tcun, np.array([1.0, 1.0, 0.0, 0.0, 0.0, 0.0])),
}


@pytest.fixture(scope="module")
def results():
    """Generate + encode every substrate once; tests assert on the values."""
    out = {}
    for name, (gen, w) in SUBSTRATES.items():
        x = gen()
        must = np.isin(x, [i for i, wi in enumerate(w) if wi > DELTA])

        sel_blob = selective_encode(x, w, DELTA)
        r_sel = rate_bits_per_symbol(sel_blob, N)
        r_blind = rate_bits_per_symbol(selective_encode(x, w, BLIND_DELTA), N)
        x_hat = selective_decode(sel_blob)

        rz_sel = rate_bits_per_symbol(selective_encode_zstd(x, w, DELTA), N)
        rz_blind = rate_bits_per_symbol(selective_encode_zstd(x, w, BLIND_DELTA), N)

        # boundary: all weights = 1 => S_delta = X => no merge for either delta
        ones = np.ones(len(w))
        bnd_sel = selective_encode(x, ones, DELTA)
        bnd_blind = selective_encode(x, ones, BLIND_DELTA)

        out[name] = {
            "delta_frac": (r_blind - r_sel) / r_blind,
            "lossless": bool(np.all(x_hat[must] == x[must])),
            "zstd_delta_frac": (rz_blind - rz_sel) / rz_blind,
            "boundary_identical": bnd_sel == bnd_blind,
            "boundary_delta_frac": (
                rate_bits_per_symbol(bnd_blind, N) - rate_bits_per_symbol(bnd_sel, N)
            )
            / rate_bits_per_symbol(bnd_blind, N),
        }
    return out


@pytest.mark.parametrize("name", list(SUBSTRATES))
class TestWinMargin:
    def test_arithmetic_saving_clears_margin(self, results, name):
        # (i) structured substrate compresses >= 20% below weight-blind
        assert results[name]["delta_frac"] >= WIN_MARGIN

    def test_lossless_on_must_preserve(self, results, name):
        # (ii) zero coherence-retention cost: every S_delta symbol exact
        assert results[name]["lossless"]

    def test_boundary_saving_is_zero(self, results, name):
        # (iii) w == 1 (everything matters) => no merge => exactly no saving
        assert results[name]["boundary_identical"]
        assert results[name]["boundary_delta_frac"] == 0.0

    def test_zstd_also_saves(self, results, name):
        # observational (not the locked margin): the practical coder saves too
        assert results[name]["zstd_delta_frac"] > 0.0
