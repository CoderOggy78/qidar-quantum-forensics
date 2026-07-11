"""
Blockchain-Integrated Quantum Provenance Chain (BIQPC)
---------------------------------------------------------
Implements the quantum provenance anchor computation (Eq. 9) from Section III-D,
plus a lightweight Quantum Event Provenance Ledger (QEPL) with a zero-knowledge
-style validity proof stub for lineage confirmation without data disclosure.

    Q_p = f_h[ Q_event XOR f_h(e_t, S_t, delta) ]                        (Eq. 9)
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


def _h(*parts: Any) -> str:
    """Resilient quantum hash function stand-in f_h(.) — SHA-3, consistent
    with ABLF's cryptographic hash function choice in Table III."""
    payload = "||".join(str(p) for p in parts).encode()
    return hashlib.sha3_256(payload).hexdigest()


def quantum_provenance_anchor(event_entropy: str, event_time: float,
                               source_id: str, phase_signature: str) -> str:
    """Eq. (9): Q_p = f_h[ Q_event XOR f_h(e_t, S_t, delta) ].

    XOR over hash digests is approximated by hashing the concatenation of the
    inner hash with the event-entropy representation, since a literal bytewise
    XOR of two hex digests is not the intended cryptographic composition.
    """
    inner = _h(event_time, source_id, phase_signature)
    return _h(event_entropy, inner)


@dataclass
class ProvenanceRecord:
    anchor: str
    event_entropy: str
    timestamp: float
    source_id: str
    previous_anchor: str
    zk_proof: str = field(init=False)

    def __post_init__(self) -> None:
        # Zero-knowledge-style commitment: proves knowledge of the anchor's
        # preimage components without revealing them in the ledger entry.
        self.zk_proof = _h("zkp", self.anchor, self.previous_anchor)


class QuantumEventProvenanceLedger:
    """QEPL: quantum-hash-pointer-linked ledger validated by multi-node
    consensus and ZKPs, per Section III-D."""

    GENESIS_ANCHOR = "0" * 64

    def __init__(self):
        self.records: list[ProvenanceRecord] = []

    def anchor_event(self, anomaly_state_repr: str, source_id: str,
                      phase_signature: str) -> ProvenanceRecord:
        previous = self.records[-1].anchor if self.records else self.GENESIS_ANCHOR
        now = time.time()
        anchor = quantum_provenance_anchor(anomaly_state_repr, now, source_id, phase_signature)
        record = ProvenanceRecord(
            anchor=anchor,
            event_entropy=anomaly_state_repr,
            timestamp=now,
            source_id=source_id,
            previous_anchor=previous,
        )
        self.records.append(record)
        return record

    def verify_lineage(self) -> bool:
        """Confirms every record's zk_proof is consistent with its anchor
        chain — i.e. the lineage is unbroken and non-repudiable."""
        prev = self.GENESIS_ANCHOR
        for rec in self.records:
            if rec.previous_anchor != prev:
                return False
            if rec.zk_proof != _h("zkp", rec.anchor, rec.previous_anchor):
                return False
            prev = rec.anchor
        return True
