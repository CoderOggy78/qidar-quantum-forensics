"""
Multi-Modal AI Forensic Reconstruction (MMAFR)
------------------------------------------------
Implements the multi-modal reconstruction loss (Eq. 5) and the attention-weighted
temporal backtracking integral (Eq. 6) from Section III-B.

    L_MMAFR = sum_i || f_r(l_i^(1), ..., l_i^(j)) - X_i ||^2             (Eq. 5)
    Gamma(t) = integral_0^T  psi(t) * dOmega(t)/dt  dt                   (Eq. 6)
"""
from __future__ import annotations

import numpy as np


def fuse_modalities(*modal_latents: np.ndarray) -> np.ndarray:
    """Simple concatenation-based fusion of j modalities (sensor, control, network
    logs, per Table III 'Modal Inputs'). Downstream reconstruction operates on
    the fused representation."""
    return np.concatenate([np.asarray(m).ravel() for m in modal_latents])


def reconstruction_loss(reconstructed: np.ndarray, ground_truth: np.ndarray) -> float:
    """Eq. (5), single-sample term: the squared L2 reconstruction error."""
    r = np.asarray(reconstructed, dtype=np.float64)
    x = np.asarray(ground_truth, dtype=np.float64)
    return float(np.sum((r - x) ** 2))


def batch_reconstruction_loss(reconstructed_batch: list[np.ndarray],
                               ground_truth_batch: list[np.ndarray]) -> float:
    """Full Eq. (5) summed across N forensic samples."""
    return float(sum(reconstruction_loss(r, x)
                      for r, x in zip(reconstructed_batch, ground_truth_batch)))


def temporal_backtrack(memory_states: np.ndarray, attention_weights: np.ndarray,
                        dt: float = 1.0) -> float:
    """Discrete numerical approximation of Eq. (6):

        Gamma(T) ~= sum_t psi(t) * (Omega(t) - Omega(t-1)) / dt * dt

    `memory_states` is Omega(t) sampled at each timestep (length T+1);
    `attention_weights` is psi(t) sampled over the same window (length T).
    """
    omega = np.asarray(memory_states, dtype=np.float64)
    psi = np.asarray(attention_weights, dtype=np.float64)
    d_omega = np.diff(omega) / dt
    n = min(len(psi), len(d_omega))
    return float(np.sum(psi[:n] * d_omega[:n]) * dt)


class MMAFRReconstructor:
    """Bi-directional GRU + attention forensic sequence reconstructor
    (architecture per Table III: latent dim 128, window 20, 4 attention heads).

    This class exposes the *interface* expected by a trained model; plug in a
    real deep-learning backend (e.g. a TensorFlow/PyTorch BiGRU-attention
    network) behind `reconstruct()` for production use.
    """

    def __init__(self, latent_dim: int = 128, window_size: int = 20,
                 attention_heads: int = 4, dropout: float = 0.2):
        self.latent_dim = latent_dim
        self.window_size = window_size
        self.attention_heads = attention_heads
        self.dropout = dropout

    def reconstruct(self, modality_sequence: list[np.ndarray]) -> np.ndarray:
        """Placeholder deterministic reconstruction (mean fusion) — replace
        with a trained BiGRU + attention decoder for real deployments."""
        stacked = np.stack([np.asarray(m, dtype=np.float64) for m in modality_sequence])
        return stacked.mean(axis=0)
