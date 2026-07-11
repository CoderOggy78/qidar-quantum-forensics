"""
Quantum-Assisted Anomaly Detection (Q-AAD)
-------------------------------------------
Reference simulation of the detection engine described in Section III-A / Eq. (1)-(2)
of "Quantum-Assisted Cyber-Forensic Techniques for Investigating Security
Vulnerabilities in Smart Consumer Electronics" (Khan et al., IEEE TCE, 2026).

This is a classical *simulation* of the quantum-encoding and scoring behaviour
described in the paper (no real quantum hardware is used). Quantum feature
states are represented as complex, unit-norm vectors in an n-dimensional
Hilbert space; the anomaly score is produced by a differentiable rotation
("unitary transform") of that state followed by a classical sigmoid readout.

    |E_state> = sum_i gamma_i |beta_i>,   sum_i |gamma_i|^2 = 1        (Eq. 1)

    A_QAAD(I) = sigmoid(w.I + b) * Re(<E| U^dagger M U |E>)            (Eq. 2)
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def encode_state(feature_vector: np.ndarray) -> np.ndarray:
    """Encode a classical feature vector into a normalized quantum-style state |E_state>.

    Implements Eq. (1): amplitudes gamma_i are derived from the (real) feature
    vector and normalized so that sum |gamma_i|^2 == 1.
    """
    x = np.asarray(feature_vector, dtype=np.complex128)
    norm = np.linalg.norm(x)
    if norm == 0:
        raise ValueError("feature_vector must be non-zero")
    return x / norm


def random_unitary(dim: int, seed: int | None = None) -> np.ndarray:
    """Generate a random unitary matrix U (dim x dim) via QR decomposition,
    standing in for a parameterized quantum circuit / variational ansatz."""
    rng = np.random.default_rng(seed)
    z = (rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    d = np.diagonal(r)
    ph = d / np.abs(d)
    return q * ph


@dataclass
class QAAD:
    """Quantum-Assisted Anomaly Detection module.

    Parameters mirror Table III of the paper: 6 qubits (=> 2^6 = 64 dim state
    space is the theoretical max; here we operate directly on the feature
    dimension for tractability, consistent with the amplitude-encoding scheme
    of Eq. 1), circuit depth 4, ELU activation.
    """
    num_qubits: int = 6
    circuit_depth: int = 4
    learning_rate: float = 0.001
    weights: np.ndarray | None = None
    bias: float = 0.0
    seed: int | None = 42
    _unitary: np.ndarray = field(init=False, repr=False, default=None)

    def _init_weights(self, dim: int) -> None:
        rng = np.random.default_rng(self.seed)
        if self.weights is None or len(self.weights) != dim:
            self.weights = rng.normal(scale=0.1, size=dim)
        if self._unitary is None or self._unitary.shape[0] != dim:
            u = np.eye(dim, dtype=np.complex128)
            for _ in range(self.circuit_depth):
                u = random_unitary(dim, seed=self.seed) @ u
            self._unitary = u

    def anomaly_score(self, feature_vector: np.ndarray) -> float:
        """Compute A_QAAD(I) for a single event/feature vector (Eq. 2)."""
        x = np.asarray(feature_vector, dtype=np.float64)
        self._init_weights(len(x))

        # Classical branch: sigmoid(w.I + b)
        classical_term = float(_sigmoid(np.dot(self.weights, x) + self.bias))

        # Quantum branch: Re(<E| U^dagger M U |E>) using M = U (Hermitian-conjugate
        # "measurement" projector stand-in), consistent with Eq. 2's structure.
        state = encode_state(x)
        rotated = self._unitary @ state
        measurement = np.vdot(rotated, self._unitary.conj().T @ rotated)
        quantum_term = float(np.real(measurement))

        return classical_term * quantum_term

    def classify(self, feature_vector: np.ndarray, threshold: float = 0.5) -> bool:
        """Return True if the event is flagged as anomalous."""
        return self.anomaly_score(feature_vector) >= threshold

    def batch_score(self, events: np.ndarray) -> np.ndarray:
        return np.array([self.anomaly_score(e) for e in events])
