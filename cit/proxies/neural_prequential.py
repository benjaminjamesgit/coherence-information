"""K_3 multi-feature proxy: GRU prequential cross-entropy.

Implements `neural_prequential_proxy`, the v0.5.3 neural-online-prediction
proxy. Strict cumulative prequential SGD over a single-layer GRU; per-feature
factorized binary cross-entropy in bits divided by the binary-uniform baseline.

Family identity: neural online cross-entropy, no coding stage. No codebook,
no entropy coder, no MDL prior, no phrase dictionary. The output is the mean
negative log-likelihood under the GRU's online predictive distribution. K_3
shares its underlying substrate with K_1 / K_2 / K_5 but consumes float32
feature vectors directly -- no byte/bit packing, no vocabulary.

Per design/multi_feature_substrate.md K_3 protocol (locked 2026-05-28) and
pre_registration.md "K_3 (neural prequential cross-entropy) protocol lock":
- Input: n-feature substrate stream, cast to float32 in [0, 1]
- Architecture: single-layer GRU, hidden_dim=64
- Init: PyTorch GRU default under torch.manual_seed(NEURAL_SEED=7)
- Output head: Linear(hidden_dim, n_features) + sigmoid (per-feature binary)
- Loss: per-feature BCE in nats (BCEWithLogitsLoss, reduction='sum'),
  accumulated in bits via division by ln(2)
- Optimizer: SGD lr=0.01, momentum=0, weight_decay=0
- Training: strict cumulative prequential, single SGD step per timestep,
  truncated BPTT(1) via h.detach() before next GRU forward
- H_pred = (1 / (T * n_features)) * sum_t sum_i BCE_bits(x_{i,t}, P_{i,t})
- H_iid = 1.0 bit per feature per step (binary uniform)
- C_K3 = 1 - H_pred / H_iid, clipped to [0, 1]
- Determinism: torch.manual_seed + use_deterministic_algorithms(True),
  CPU-only execution. Global deterministic flag is save/set/restore-scoped
  to avoid polluting the caller's torch state.
"""

from __future__ import annotations

import math
import numpy as np
import torch

__all__ = ["neural_prequential_proxy"]

NEURAL_SEED = 7
HIDDEN_DIM = 64
LEARNING_RATE = 0.01

_LN2 = math.log(2.0)


def neural_prequential_proxy(stream, n_features=None):
    """K_3: GRU prequential cross-entropy on multi-feature binary stream.

    Strict online prequential SGD over a single-layer GRU. At each step t,
    predict x_t from h_{t-1}, observe x_t, accumulate per-feature BCE in
    bits, take a single SGD step on the per-step loss, then advance the
    hidden state by processing x_t. Mean per-feature per-step cross-entropy
    divided by binary-uniform baseline (1.0 bit/feature/step) yields C_K3.

    Parameters
    ----------
    stream : ndarray of shape (n_steps, n_features), binary uint8 or float
        Multi-feature substrate stream. Values must be in {0, 1} (or [0, 1]
        after cast).
    n_features : int, optional
        Must match stream.shape[1] if provided. Inferred otherwise.

    Returns
    -------
    C_K3 : float in [0, 1]
        Coherence estimate. 1 = perfect predictability (zero cross-entropy);
        0 = uniform-random cross-entropy or worse.
    """
    if n_features is None:
        n_features = stream.shape[1]
    elif n_features != stream.shape[1]:
        raise ValueError(
            f"n_features={n_features} does not match stream.shape[1]={stream.shape[1]}"
        )

    T = stream.shape[0]
    if T < 2:
        return 0.0

    # Save and restore the global deterministic flag to avoid side effects
    prev_deterministic = torch.are_deterministic_algorithms_enabled()
    torch.use_deterministic_algorithms(True)
    try:
        torch.manual_seed(NEURAL_SEED)

        # Locked architecture: 1-layer GRU + linear output head, CPU-only
        gru = torch.nn.GRU(
            input_size=n_features, hidden_size=HIDDEN_DIM, num_layers=1
        )
        linear = torch.nn.Linear(HIDDEN_DIM, n_features)
        bce_loss = torch.nn.BCEWithLogitsLoss(reduction="sum")
        optimizer = torch.optim.SGD(
            list(gru.parameters()) + list(linear.parameters()),
            lr=LEARNING_RATE,
            momentum=0.0,
            weight_decay=0.0,
        )

        # Cast stream to float32 tensor (binary uint8 -> {0.0, 1.0})
        stream_tensor = torch.from_numpy(stream.astype(np.float32))

        # Prequential loop, h_{-1} = zeros
        h = torch.zeros(1, 1, HIDDEN_DIM)
        total_loss_bits = 0.0

        for t in range(T):
            # Predict x_t from h (= h_{t-1}); shape (1, n_features)
            logits_t = linear(h.squeeze(0))
            x_t = stream_tensor[t:t + 1]

            # Per-feature BCE in nats, summed across features
            loss_nats = bce_loss(logits_t, x_t)
            total_loss_bits += loss_nats.item() / _LN2

            # Single SGD step on per-step loss; truncated BPTT window = 1
            optimizer.zero_grad()
            loss_nats.backward()
            optimizer.step()

            # Advance hidden state with x_t; detach severs the graph for
            # the next iteration (TBPTT(1)).
            x_t_input = x_t.unsqueeze(0)  # (seq=1, batch=1, n_features)
            _, h = gru(x_t_input, h.detach())

        H_pred = total_loss_bits / (T * n_features)
        H_iid = 1.0  # binary uniform baseline (bits per feature per step)

        C_K3 = 1.0 - H_pred / H_iid
        return float(np.clip(C_K3, 0.0, 1.0))
    finally:
        torch.use_deterministic_algorithms(prev_deterministic)
