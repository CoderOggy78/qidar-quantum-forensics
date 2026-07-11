"""
Adaptive Blockchain Ledger Forensics (ABLF)
--------------------------------------------
Implements the tamper-resistant block-hash chain (Eq. 3) and the smart-contract
forensic validation score (Eq. 4) from Section III-A of the QIDAR paper.

    B_i^t = h( FD^t || T^t || B_i^(t-1) )                              (Eq. 3)
    V_SC  = closed-contour integral [ phi(state_x) * Theta(x) ] dx      (Eq. 4)

Eq. 4 is approximated numerically as a weighted sum over the discrete set of
forensic entries currently under review (the "state space" C in the paper),
since a literal contour integral has no closed-form discrete analogue.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


def hash_block(forensic_data: dict[str, Any], timestamp: float, previous_hash: str) -> str:
    """Eq. (3): B_i^t = h(FD^t || T^t || B_i^(t-1)) using SHA-3 (per Table III)."""
    payload = json.dumps(forensic_data, sort_keys=True).encode() + \
        f"{timestamp}".encode() + previous_hash.encode()
    return hashlib.sha3_256(payload).hexdigest()


@dataclass
class ForensicBlock:
    index: int
    forensic_data: dict[str, Any]
    timestamp: float
    previous_hash: str
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.hash = hash_block(self.forensic_data, self.timestamp, self.previous_hash)


class AdaptiveBlockchainLedger:
    """Decentralized, append-only forensic ledger with smart-contract-style
    2-of-3 validator consensus, mirroring Table I / Table III parameters."""

    GENESIS_HASH = "0" * 64

    def __init__(self, validator_threshold: float = 2 / 3, num_validators: int = 3):
        self.chain: list[ForensicBlock] = []
        self.validator_threshold = validator_threshold
        self.num_validators = num_validators

    def log_event(self, forensic_data: dict[str, Any]) -> ForensicBlock:
        previous_hash = self.chain[-1].hash if self.chain else self.GENESIS_HASH
        block = ForensicBlock(
            index=len(self.chain),
            forensic_data=forensic_data,
            timestamp=time.time(),
            previous_hash=previous_hash,
        )
        self.chain.append(block)
        return block

    def verify_chain(self) -> bool:
        """Zero-trust auditing: recompute each hash and confirm forward integrity."""
        prev = self.GENESIS_HASH
        for block in self.chain:
            if hash_block(block.forensic_data, block.timestamp, prev) != block.hash:
                return False
            prev = block.hash
        return True

    def validation_score(self, trust_weights: list[float], validity_flags: list[int]) -> float:
        """Discrete approximation of Eq. (4): V_SC = sum_x phi(state_x) * Theta(x).

        `validity_flags` are phi(state_x) in {0, 1}; `trust_weights` are Theta(x).
        """
        if len(trust_weights) != len(validity_flags):
            raise ValueError("trust_weights and validity_flags must be the same length")
        return float(sum(w * v for w, v in zip(trust_weights, validity_flags)))

    def consensus_reached(self, votes: list[bool]) -> bool:
        """2/3 validator agreement, per Table III smart-contract threshold logic."""
        if not votes:
            return False
        return (sum(votes) / len(votes)) >= self.validator_threshold
