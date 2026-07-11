"""
Evaluation metrics introduced in Section V of the QIDAR paper.

These are reference implementations of the *definitions* given in the paper's
prose (Forensic Convergence Efficiency, Quantum Anomaly Resolution Precision,
Tamper-Resistant Ledger Index, Distributed Forensic Resilience Score, Forensic
Lineage Verifiability Index). The paper does not give closed-form formulas for
all of them, so these implementations follow the described components and are
intended as a starting point for reproducing/benchmarking, not a verbatim
transcription of unpublished formulas.
"""
from __future__ import annotations


def tamper_resistant_ledger_index(ledger_depth: float, entropy_loss: float,
                                   logging_overhead: float,
                                   w_depth: float = 1.0, w_entropy: float = 1.0,
                                   w_overhead: float = 1.0) -> float:
    """TRLI: rewards ledger validation depth, penalizes entropy loss (EL) and
    logging overhead. Matches the ordering in Table VI (higher depth / lower
    EL & overhead => higher TRLI)."""
    numerator = w_depth * ledger_depth
    denominator = 1.0 + w_entropy * entropy_loss + w_overhead * logging_overhead
    return round(numerator / denominator, 2)


def distributed_forensic_resilience_score(consensus_integrity: float,
                                           ledger_validation_redundancy: float,
                                           anomaly_detection_rate: float,
                                           entropy_preservation_rate: float) -> float:
    """DFRS: composite of Consensus Integrity Factor (CIF), Ledger Validation
    Redundancy (LVR), Anomaly Detection Rate (ADR, 0-1), and Entropy
    Preservation Rate (EPR, 0-1), per Section V discussion of Fig. 3."""
    return round(
        consensus_integrity * ledger_validation_redundancy *
        anomaly_detection_rate * entropy_preservation_rate, 2
    )


def forensic_lineage_verifiability_index(quantum_anchor_confidence: float,
                                          state_information_entropy: float,
                                          traceable_lineage_depth: float) -> float:
    """FLVI (Table VII): rewards Quantum Anchor Confidence (QAC, 0-1) and
    Traceable Lineage Depth (TLD), penalizes State Information Entropy (SIE)."""
    return round(
        100 * quantum_anchor_confidence * traceable_lineage_depth /
        (traceable_lineage_depth + 100 * state_information_entropy), 2
    )


def forensic_convergence_efficiency(baseline_time_s: float, qidar_time_s: float) -> float:
    """FCE as a percentage reduction in time-to-verifiable-resolution,
    consistent with the paper's 'temporal reduction of reconstruction
    entropy' framing and the reported 72% investigation-time reduction."""
    if baseline_time_s <= 0:
        raise ValueError("baseline_time_s must be positive")
    return round(100 * (1 - qidar_time_s / baseline_time_s), 2)


def quantum_anomaly_resolution_precision(true_positive: int, false_positive: int,
                                          false_negative: int) -> float:
    """QARP approximated as an F1-style precision/recall fusion (0-100 scale),
    consistent with the paper's confusion-matrix-based accuracy reporting
    (Fig. 6: <2.5% FPR, <3% FNR per class)."""
    if (true_positive + false_positive) == 0 or (true_positive + false_negative) == 0:
        return 0.0
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return round(100 * f1, 2)
