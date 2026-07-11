import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.q_aad import QAAD, encode_state
from src.ablf import AdaptiveBlockchainLedger
from src.qecl import QECL, von_neumann_entropy, random_density_matrix
from src.biqpc import QuantumEventProvenanceLedger
from src.pipeline import QIDARPipeline


def test_encode_state_is_normalized():
    state = encode_state(np.array([3.0, 4.0]))
    assert np.isclose(np.linalg.norm(state), 1.0)


def test_q_aad_score_in_reasonable_range():
    q = QAAD(seed=1)
    score = q.anomaly_score(np.array([0.2, 0.4, 0.1, 0.9, 0.3, 0.6]))
    assert isinstance(score, float)


def test_ablf_chain_integrity():
    ledger = AdaptiveBlockchainLedger()
    ledger.log_event({"event": "power_spike", "device": "thermostat-01"})
    ledger.log_event({"event": "unexpected_reboot", "device": "thermostat-01"})
    assert ledger.verify_chain() is True
    ledger.chain[0].forensic_data["event"] = "tampered"
    assert ledger.verify_chain() is False


def test_qecl_roundtrip():
    qecl = QECL()
    sealed = qecl.seal('{"event": "test"}')
    assert qecl.unseal(sealed) == '{"event": "test"}'


def test_von_neumann_entropy_nonnegative():
    d = random_density_matrix(4, seed=7)
    assert von_neumann_entropy(d) >= 0


def test_biqpc_lineage_valid():
    ledger = QuantumEventProvenanceLedger()
    ledger.anchor_event("score=0.91", "camera-02", "sig-a1")
    ledger.anchor_event("score=0.88", "camera-02", "sig-b2")
    assert ledger.verify_lineage() is True


def test_pipeline_flags_and_logs_anomaly():
    pipeline = QIDARPipeline(anomaly_threshold=0.0)  # force anomaly path
    result = pipeline.process_event("smart-lock-07", np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4]))
    assert result["is_anomaly"] is True
    assert "block_hash" in result
    assert "provenance_anchor" in result
    audit = pipeline.audit()
    assert audit["ledger_valid"] is True
    assert audit["provenance_valid"] is True
