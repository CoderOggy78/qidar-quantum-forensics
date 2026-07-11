# Source Paper

**Title:** Quantum-Assisted Cyber-Forensic Techniques for Investigating Security
Vulnerabilities in Smart Consumer Electronics

**Authors:** Surbhi B. Khan, Karthick Raghunath K M, Mahesh T R, Ahmed Alyahya,
Fatima Asiri, Ahlam Almusharraf

**Venue:** IEEE Transactions on Consumer Electronics (2026)
**DOI:** 10.1109/TCE.2026.3666000

## Summary

The paper proposes **QIDAR** (Quantum-Driven Intrusion Detection and Anomaly
Resolution), a cyber-forensic framework for smart consumer electronics (IoT
appliances, smart thermostats, connected kitchen devices, wearables, etc.)
combining:

| Module | Role |
|---|---|
| **Q-AAD** — Quantum-Assisted Anomaly Detection | Encodes appliance telemetry as quantum-style states and scores anomalies with a hybrid quantum/classical model (Eq. 1–2). |
| **ABLF** — Adaptive Blockchain Ledger Forensics | Hashes and chains forensic events into an append-only ledger, validated by smart-contract consensus (Eq. 3–4, Table I). |
| **MMAFR** — Multi-Modal AI Forensic Reconstruction | Fuses sensor, control, and network-log modalities to reconstruct attack chronology (Eq. 5–6). |
| **QECL** — Quantum-Enhanced Cryptographic Logging | Seals forensic logs with entropy-derived, quantum-one-time-pad-style encryption (Eq. 7–8). |
| **BIQPC** — Blockchain-Integrated Quantum Provenance Chain | Anchors event lineage into a quantum-hash provenance ledger validated by consensus and zero-knowledge proofs (Eq. 9). |

## Reported results (Sections IV–V)

| Metric | QIDAR | Best baseline | Baseline value |
|---|---|---|---|
| Forensic Convergence Efficiency (FCE) | 87.2% | QRL | 67.5% |
| Quantum Anomaly Resolution Precision (QARP) | 98.5% | QRL | 89.2% |
| Tamper-Resistant Ledger Index (TRLI) | 93.2 | QRL | 80.5 |
| Distributed Forensic Resilience Score (DFRS) | highest (bar chart, Fig. 3) | — | — |
| Forensic Lineage Verifiability Index (FLVI) | 97.8 | QRL | 56.2 |
| Anomaly detection efficiency | 98.5% | — | — |
| Forensic investigation time reduction | 72% | — | — |
| Data-log tamper-resistance improvement | 67% | — | — |

Baselines compared against: F-QDPoS, Q-BOA, EQCNN, QDICP, VQC, HQ-CINN, QSVM, QRL.

## Experimental setup (Table III, Section IV)

- **Simulation stack:** Qiskit v0.45.0 (quantum circuits), TensorFlow v2.13.0
  (DL components), Solidity v0.8.21 + Ganache CLI v7.8.0 (blockchain), Python 3.10.
- **Hardware:** Intel i9, NVIDIA RTX 3080 (32GB RAM), Ubuntu 22.04 LTS.
- **Q-AAD:** 6 qubits, circuit depth 4, ELU activation, Adam optimizer, lr 0.001, 50 epochs.
- **ABLF:** 2s block confirmation, 5,000,000 gas limit, 2/3 validator threshold, 1MB blocks, SHA-3.
- **MMAFR:** 3 modalities, 128-dim latent space, 20-step memory window, Bi-GRU, 4 attention heads, 0.2 dropout.
- **QECL:** 256-bit keys, 3-level entanglement depth, 15-minute key refresh, Quantum One-Time Pad, von Neumann entropy source.

## Relationship of this repository to the paper

This repository is an **independent, unofficial companion implementation**.
It translates the paper's mathematical definitions and pseudocode (Table I,
Table II) into runnable, tested Python and Solidity — using classical
simulation (NumPy) to stand in for real quantum hardware/QKD, exactly as the
paper itself does via Qiskit simulation. It does not reproduce the paper's
text, figures, or full experimental results, and all numeric benchmarks shown
in the demo website are the values reported in the paper itself, not
independently re-derived. See `LICENSE` for the copyright note on the source
paper.
