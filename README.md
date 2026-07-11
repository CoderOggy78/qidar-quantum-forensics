
# QIDAR — Quantum-Driven Intrusion Detection & Anomaly Resolution

> A reference implementation of a quantum-assisted cyber-forensic framework
> for smart consumer electronics: quantum-encoded anomaly detection,
> blockchain-anchored forensic logging, multi-modal attack reconstruction,
> and a quantum provenance chain — with a companion interactive site.

[![Tests](https://img.shields.io/badge/tests-passing-4FE3C1)](#testing)
[![License: MIT](https://img.shields.io/badge/license-MIT-8B7FE8)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#requirements)

📄 Companion research paper: *"Quantum-Assisted Cyber-Forensic Techniques for
Investigating Security Vulnerabilities in Smart Consumer Electronics"*,
Khan et al., IEEE Transactions on Consumer Electronics, 2026.
DOI: [10.1109/TCE.2026.3666000](https://doi.org/10.1109/TCE.2026.3666000)
— see [`docs/PAPER_SUMMARY.md`](docs/PAPER_SUMMARY.md) for a full breakdown.

---

## What is QIDAR?

Smart appliances — thermostats, locks, cameras, kitchen hubs — are always
transmitting data, which makes them attractive, under-defended targets.
Existing forensic tooling tends to be either purely reactive (post-event log
analysis) or purely predictive (anomaly detection with no tamper-evident
trail). **QIDAR** closes that gap by chaining five modules into a single
pipeline that detects, logs, reconstructs, encrypts, and provenances a
security incident from first anomaly to court-admissible evidence:

```
   telemetry
       │
       ▼
 ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
 │  Q-AAD    │───▶│  ABLF     │───▶│  MMAFR    │───▶│  QECL     │───▶│  BIQPC    │
 │ quantum   │    │ blockchain│    │ multi-    │    │ quantum-  │    │ quantum   │
 │ anomaly   │    │ ledger    │    │ modal     │    │ safe log  │    │ provenance│
 │ detection │    │ forensics │    │ recon.    │    │ encryption│    │ chain     │
 └───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘
```

| Module | What it does | Key equation |
|---|---|---|
| **Q-AAD** | Encodes appliance features into a quantum-style state and scores anomalies via a hybrid quantum/classical readout | `A(I) = σ(w·I+b) · Re⟨E\|U†MU\|E⟩` |
| **ABLF** | Hash-chains flagged events into an append-only ledger with 2-of-3 smart-contract consensus | `B(t) = SHA3(FD(t) ‖ T(t) ‖ B(t−1))` |
| **MMAFR** | Fuses sensor / control / network-log modalities to reconstruct attack chronology | `L = Σ‖f_r(l¹,…,lʲ) − X‖²` |
| **QECL** | Seals logs behind an entropy-derived, quantum-one-time-pad-style cipher | `S = −tr(d·log d)`, `E(I_F) = key ⊕ I_F` |
| **BIQPC** | Anchors event lineage into a ZKP-validated quantum provenance ledger | `Q_p = f_h[Q_event ⊕ f_h(e_t,S_t,δ)]` |

## Repository structure

```
qidar-quantum-forensics/
├── src/
│   ├── q_aad.py       # Quantum-Assisted Anomaly Detection
│   ├── ablf.py         # Adaptive Blockchain Ledger Forensics
│   ├── mmafr.py        # Multi-Modal AI Forensic Reconstruction
│   ├── qecl.py          # Quantum-Enhanced Cryptographic Logging
│   ├── biqpc.py         # Blockchain-Integrated Quantum Provenance Chain
│   ├── metrics.py       # FCE / QARP / TRLI / DFRS / FLVI evaluation metrics
│   └── pipeline.py      # End-to-end orchestrator (Table II algorithm)
├── contracts/
│   └── ForensicValidator.sol   # Smart contract from Table I
├── website/
│   └── index.html       # Interactive project site (animated, single-file)
├── docs/
│   └── PAPER_SUMMARY.md # Full breakdown of the source paper
├── tests/
│   └── test_pipeline.py
├── demo.py               # Runnable end-to-end simulation
├── requirements.txt
└── LICENSE
```

## Quickstart

```bash
git clone https://github.com/<your-username>/qidar-quantum-forensics.git
cd qidar-quantum-forensics
pip install -r requirements.txt

python demo.py       # simulate a telemetry sweep through the full pipeline
pytest tests/ -v      # run the test suite
```

### Minimal usage

```python
from src.pipeline import QIDARPipeline
import numpy as np

pipeline = QIDARPipeline(anomaly_threshold=0.06)

result = pipeline.process_event(
    device_id="kitchen-hub-03",
    feature_vector=np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4]),
)

print(result["is_anomaly"])         # True
print(result["block_hash"])         # SHA-3 forensic block hash (ABLF)
print(result["provenance_anchor"])  # Quantum provenance anchor (BIQPC)

print(pipeline.audit())
# {'ledger_valid': True, 'provenance_valid': True}
```

### Individual modules

```python
from src.q_aad import QAAD
from src.qecl import QECL
from src.biqpc import QuantumEventProvenanceLedger

q = QAAD(num_qubits=6, circuit_depth=4)
score = q.anomaly_score([0.2, 0.4, 0.1, 0.9, 0.3, 0.6])

qecl = QECL(key_size_bits=256)
sealed = qecl.seal('{"event": "unexpected_reboot"}')
assert qecl.unseal(sealed) == '{"event": "unexpected_reboot"}'

ledger = QuantumEventProvenanceLedger()
record = ledger.anchor_event("score=0.91", "camera-02", "sig-a1")
assert ledger.verify_lineage()
```

## The website

`website/index.html` is a single-file, dependency-free interactive site:
a quantum-particle hero animation, a live simulated hash-chain ticker, the
five-stage pipeline, and animated benchmark charts reproducing the paper's
reported metrics (FCE, QARP, TRLI, FLVI). Open it directly in a browser —
no build step required:

```bash
open website/index.html   # macOS
# or just double-click the file / serve with `python -m http.server`
```

## Design & implementation notes

- **This is a classical simulation**, exactly as the source paper's own
  experiments were (via Qiskit's simulator, not physical quantum hardware).
  `src/q_aad.py` and `src/qecl.py` model quantum states as complex NumPy
  vectors/matrices; swap in a real backend (Qiskit, PennyLane, physical QKD)
  behind the same interfaces for production or research use.
- **Smart contract** (`contracts/ForensicValidator.sol`) is a direct,
  compilable implementation of the pseudocode in the paper's Table I,
  targeting Solidity ^0.8.21 (tested against Ganache CLI in the original work).
- **Metrics** (`src/metrics.py`) implement the *definitions* given in the
  paper's prose; the paper does not publish closed-form formulas for all of
  them, so treat these as a reproducible starting point rather than a
  verbatim transcription.

## Testing

```bash
pytest tests/ -v
```

Covers state encoding/normalization, Q-AAD scoring, ABLF hash-chain
integrity (including tamper detection), QECL encrypt/decrypt round-trips,
von Neumann entropy computation, BIQPC lineage verification, and full
pipeline execution + audit.

## Requirements

- Python 3.10+
- `numpy`, `pytest` (see `requirements.txt`)
- No GPU, quantum hardware, or blockchain node required — everything runs
  as a local simulation.

## Roadmap

- [ ] Swap `random_unitary` stand-in for a real parameterized quantum circuit (Qiskit/PennyLane backend)
- [ ] Train a real Bi-GRU + attention model for `MMAFRReconstructor`
- [ ] Deploy `ForensicValidator.sol` to a local Hardhat/Ganache node with an integration test
- [ ] Add quantum error correction (per the paper's stated future work)
- [ ] Publish benchmark reproduction scripts for FCE / QARP / TRLI / DFRS / FLVI

## Citation

```bibtex
@article{khan2026qidar,
  title   = {Quantum-Assisted Cyber-Forensic Techniques for Investigating
             Security Vulnerabilities in Smart Consumer Electronics},
  author  = {Khan, Surbhi B. and Raghunath K M, Karthick and T R, Mahesh and
             Alyahya, Ahmed and Asiri, Fatima and Almusharraf, Ahlam},
  journal = {IEEE Transactions on Consumer Electronics},
  year    = {2026},
  doi     = {10.1109/TCE.2026.3666000}
}
```

## License

Code in this repository is released under the [MIT License](LICENSE). The
source paper is © 2026 IEEE and is referenced, not reproduced — this is an
independent, unofficial, clean-room implementation of the algorithms it
describes, created for research and educational purposes.
