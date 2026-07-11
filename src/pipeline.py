"""
QIDAR end-to-end pipeline
---------------------------
Wires together Q-AAD -> ABLF -> MMAFR -> QECL -> BIQPC, following the
workflow described in Section III-D and Table II ("Algorithmic Procedures
of QIDAR") of the paper.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .q_aad import QAAD
from .ablf import AdaptiveBlockchainLedger
from .mmafr import MMAFRReconstructor, fuse_modalities
from .qecl import QECL
from .biqpc import QuantumEventProvenanceLedger


@dataclass
class QIDARPipeline:
    """High-level orchestrator implementing Table II, steps 1-11."""

    anomaly_threshold: float = 0.5
    q_aad: QAAD = field(default_factory=QAAD)
    ledger: AdaptiveBlockchainLedger = field(default_factory=AdaptiveBlockchainLedger)
    reconstructor: MMAFRReconstructor = field(default_factory=MMAFRReconstructor)
    qecl: QECL = field(default_factory=QECL)
    provenance: QuantumEventProvenanceLedger = field(default_factory=QuantumEventProvenanceLedger)

    def process_event(self, device_id: str, feature_vector: np.ndarray,
                       modality_sequence: list[np.ndarray] | None = None) -> dict[str, Any]:
        """Run one smart-appliance event through the full QIDAR pipeline.

        Steps (Table II):
          1-2. Encode + score with Q-AAD
          3-4. Hash + smart-contract log via ABLF (only if anomalous)
          5-6. Reconstruct attack context via MMAFR (only if anomalous)
          7-8. Generate entropic key + encrypt log via QECL
          9-11. Anchor provenance + validate via BIQPC / consensus
        """
        score = self.q_aad.anomaly_score(feature_vector)
        is_anomaly = score >= self.anomaly_threshold

        result: dict[str, Any] = {
            "device_id": device_id,
            "anomaly_score": score,
            "is_anomaly": is_anomaly,
        }

        if not is_anomaly:
            return result

        forensic_record = {
            "device_id": device_id,
            "feature_vector": list(np.asarray(feature_vector, dtype=float)),
            "anomaly_score": score,
        }
        block = self.ledger.log_event(forensic_record)
        result["block_hash"] = block.hash

        if modality_sequence:
            reconstruction = self.reconstructor.reconstruct(modality_sequence)
            result["reconstruction"] = reconstruction.tolist()

        sealed_log = self.qecl.seal(json.dumps(forensic_record))
        result["sealed_log_hex"] = sealed_log.hex()

        record = self.provenance.anchor_event(
            anomaly_state_repr=f"score={score:.6f}",
            source_id=device_id,
            phase_signature=block.hash,
        )
        result["provenance_anchor"] = record.anchor
        result["zk_proof"] = record.zk_proof

        return result

    def audit(self) -> dict[str, bool]:
        """Full-system integrity check: blockchain hash chain + provenance lineage."""
        return {
            "ledger_valid": self.ledger.verify_chain(),
            "provenance_valid": self.provenance.verify_lineage(),
        }
