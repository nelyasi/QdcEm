![BatSim Package Overview](postercode.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-1.0-brightgreen.svg)]()

# Quantum Data Centers on Single-Chip Quantum Computers (QdcEm)

## Overview

This repository contains the code, data, and analysis scripts supporting the paper:

> **"Emulation of Quantum Data Centers on Digital Quantum Computers"**  
> *Seyed Navid Elyasi, Paolo Monti. Jun Li, Rui Lin*  

In this work, we present a **hardware-compatible framework** for emulating **Quantum Data Centers (QDCs)** entirely within a single superconducting quantum processor.  
Our approach partitions the chip’s coupling map into **virtual Quantum Processing Units (QPUs)** and uses an **experimentally grounded Collisional Model (CM)** to emulate noisy quantum communication channels such as optical fibers and transducers.  

The repository provides:
- **Implementation of Remote Gates (RGs)** including CNOT, Controlled-Phase, CZ, and Controlled-U gates over virtual QPUs.
- **Noise modeling** via CM to emulate both transduction and fiber-induced decoherence.
- **Demonstrations of distributed quantum algorithms** such as Grover’s Search and the Quantum Fourier Transform (QFT).
- **All plotting scripts** to recreate figures from the paper.

---

## Package Structure

The `QDCEm` package consists of the following core modules:

1. **Remote Gates**
   - **Cat-State Communication (Cat-Com)**  
     - Remote CNOT (CX)  
     - Remote Controlled-Phase (CPhase)
   - **Teleportation Protocols**  
     - TP1  
     - TP2  
     - TP-Safe  
   These protocols are implemented with tunable CM-based noise to study fidelity degradation under realistic communication conditions.

2. **Examples**
   - Remote Gate execution workflows and benchmark cases demonstrating the interaction of communication and processing qubits across virtual QPUs.

3. **Algorithms**
   - **Entanglement Generation**  
     Cross-QPU Bell state creation using noisy RGs.
   - **Grover’s Search**  
     Distributed 2-qubit Grover’s algorithm executed across virtual QPUs, validated against experimental ion-trap results.
   - **Quantum Fourier Transform (QFT)**  
     5-qubit QFT partitioned across QPUs, with fidelity analysis via quantum state tomography.

---

## Usage 

```bash
from qdcem import remote_cx

remote_cx(qc, control, target, CommA, CommB, ENA, ENB, creg, creg_index,
          kappa_Fiber=0.05, Steps=3, kappa_Transductor=0.1)
```
control and target are indices of processing qubits.

CommA and CommB are communication qubits in QPU A and QPU B.

ENA, ENB are environment qubits recycled for CM noise injection.

## Method Summary

The CM-based noise model used here follows the interaction Hamiltonian:

$$
\hat{H} = \kappa \left( \sigma^- \otimes \sigma^+ + \sigma^+ \otimes \sigma^- \right)
$$

- **$\kappa_{\text{Transducer}}$** models conversion inefficiencies between microwave and optical domains.  
- **$\kappa_{\text{Fiber}}$** models optical attenuation over discrete fiber segments.

Mid-circuit measurement and feed-forward logic enable **non-local operations** between processing qubits located in different virtual QPUs — matching the Cat-Comm protocol outlined in Section III-A of the paper.

---

## Dependencies & Versions

To use this repository, you need to download and install the following required packages (**as of February 27, 2026**):

| Package        | Version     |
|----------------|-------------|
| **qiskit**       | `2.3.0`      |
| **qutip**        | `5.2.3`      |
| **matplotlib**   | `3.10.8`     |
| **numpy**        | `2.4.2`      |

### Installation
```bash
**pip install qiskit==0.52.0 qutip==5.0.1 matplotlib==3.9.1 numpy==1.27.0**
```


## Toturial on How to Use this Repository(Video Format) 
[![Watch the video](https://img.youtube.com/vi/your-video-id/0.jpg)](https://www.youtube.com/watch?v=your-video-id)

---

## Citation

If you use this work in your research, please cite our paper:

**A Framework for Quantum Data Center Emulation Using Digital Quantum Computers**  
S. N. Elyasi, P. Monti, J. Li, R. Lin  
_arXiv preprint arXiv:2509.04029 (2025)_

### 🔹 BibTeX

Add the following entry to your `.bib` file:

```bibtex
@article{elyasi2025quantum,
  title={A Framework for Quantum Data Center Emulation Using Digital Quantum Computers},
  author={Elyasi, S. N. and Monti, P. and Li, J. and Lin, R.},
  journal={arXiv preprint arXiv:2509.04029},
  year={2025},
  url={https://arxiv.org/abs/2509.04029}
}


