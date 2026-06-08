<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0f62fe&height=220&section=header&text=QdcEm&fontSize=72&fontColor=ffffff&fontAlignY=38&fontAlign=50&desc=Quantum%20Data%20Centers%20on%20Single-Chip%20Quantum%20Computers&descAlignY=60&descSize=16&descAlign=50&animation=fadeIn" width="100%"/>

<br/>

<img src="https://img.shields.io/badge/License-MIT-42be65?style=flat-square&labelColor=161616"/>
<img src="https://img.shields.io/badge/version-1.0-42be65?style=flat-square&labelColor=161616"/>
<img src="https://img.shields.io/badge/arXiv-2509.04029-da1e28?style=flat-square&labelColor=161616"/>
<img src="https://img.shields.io/badge/Python-3.9%2B-0f62fe?style=flat-square&labelColor=161616"/>
<img src="https://img.shields.io/badge/Qiskit-2.3.0-8a3ffc?style=flat-square&labelColor=161616"/>

<br/><br/>

> **Emulation of Quantum Data Centers on Digital Quantum Computers**
> *Seyed Navid Elyasi · Paolo Monti · Jun Li · Rui Lin — Chalmers University of Technology*

<br/>

</div>

---

## `01` &nbsp; Overview

This repository contains the code, data, and analysis scripts supporting research on **hardware-compatible emulation of Quantum Data Centers (QDCs)** within a single superconducting quantum processor.

The approach partitions a chip's coupling map into **virtual Quantum Processing Units (QPUs)** and uses an experimentally grounded **Collisional Model (CM)** to emulate noisy quantum communication channels — optical fibers and microwave-to-optical transducers — all on a single device.

```
 ┌─────────────────────────────────────────────────────────────┐
 │                    Single Quantum Chip                      │
 │                                                             │
 │   ┌──────────────┐    Fiber + Transducer    ┌─────────────┐ │
 │   │    QPU A     │  ══════════════════════  │    QPU B    │ │
 │   │  P  P  C  E  │  κ_Fiber  κ_Transducer   │  E  C  P  P │ │
 │   └──────────────┘                          └─────────────┘ │
 │                                                             │
 │   P = Processing qubit   C = Communication qubit            │
 │   E = Environment qubit (CM noise injection)                │
 └─────────────────────────────────────────────────────────────┘
```

---

## `02` &nbsp; Key Contributions

| &nbsp; | Contribution | Description |
|:---:|---|---|
| ⚙ | **Remote Gate Implementation** | CNOT, Controlled-Phase, CZ, and Controlled-U gates across virtual QPUs |
| ∿ | **Collisional Model Noise** | Experimentally grounded noise for fiber attenuation and transducer inefficiency |
| ◈ | **Distributed Algorithms** | Grover's Search and QFT demonstrated across partitioned QPUs |
| ⊞ | **Full Reproducibility** | All plotting scripts to recreate every figure from the paper |

---

## `03` &nbsp; Package Structure

```
QdcEm/
│
├── remote_gates/
│   ├── cat_com/
│   │   ├── remote_cx.py          # Remote CNOT via Cat-State Communication
│   │   └── remote_cphase.py      # Remote Controlled-Phase
│   └── teleportation/
│       ├── tp1.py                # Teleportation Protocol 1
│       ├── tp2.py                # Teleportation Protocol 2
│       └── tp_safe.py            # TP-Safe (measurement-error resilient)
│
├── noise/
│   └── collisional_model.py      # CM Hamiltonian: H = κ(σ⁻⊗σ⁺ + σ⁺⊗σ⁻)
│
├── algorithms/
│   ├── entanglement.py           # Cross-QPU Bell state generation
│   ├── grover.py                 # Distributed 2-qubit Grover's search
│   └── qft.py                   # 5-qubit QFT across virtual QPUs
│
└── examples/
    └── remote_gate_demo.py       # Workflow demonstration
```

---

## `04` &nbsp; Noise Model

$$\hat{H} = \kappa \left( \sigma^- \otimes \sigma^+ + \sigma^+ \otimes \sigma^- \right)$$

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| Transducer coupling | `κ_Transducer` | Microwave-to-optical conversion inefficiency |
| Fiber coupling | `κ_Fiber` | Optical attenuation over discrete fiber segments |
| CM steps | `N_steps` | Number of discrete environment interactions |

---

## `05` &nbsp; Installation

```bash
pip install qiskit==2.3.0 qutip==5.2.3 matplotlib==3.10.8 numpy==2.4.2
```

---

## `06` &nbsp; Quick Start

```python
from QdcEm import remote_cx

remote_cx(
    qc,
    control,          # index of control processing qubit
    target,           # index of target processing qubit
    CommA,            # communication qubit in QPU A
    CommB,            # communication qubit in QPU B
    ENA,              # environment qubit in QPU A (CM noise)
    ENB,              # environment qubit in QPU B (CM noise)
    creg,
    creg_index,
    kappa_Fiber=0.05,
    Steps=3,
    kappa_Transductor=0.1
)
```

```bash
python examples/grover_demo.py        # Distributed Grover's search
python examples/qft_demo.py           # 5-qubit distributed QFT
python examples/remote_gate_demo.py   # Remote CNOT fidelity sweep
```

---

## `07` &nbsp; Demonstrated Algorithms

<table>
<tr>
<td width="33%" valign="top">

**🔵 &nbsp; Grover's Search**

Distributed 2-qubit Grover's algorithm across virtual QPUs, validated against ion-trap experimental results.

</td>
<td width="33%" valign="top">

**🟣 &nbsp; Quantum Fourier Transform**

5-qubit QFT partitioned across QPUs with fidelity characterization via quantum state tomography.

</td>
<td width="33%" valign="top">

**🔴 &nbsp; Entanglement Generation**

Cross-QPU Bell state creation using noisy remote gates over CM-modeled communication channels.

</td>
</tr>
</table>

---

## `08` &nbsp; Dependencies

| Package | Version | Role |
|---------|---------|------|
| [qiskit](https://qiskit.org/) | `2.3.0` | Circuit construction and execution |
| [qutip](https://qutip.org/) | `5.2.3` | Collisional model simulation |
| [matplotlib](https://matplotlib.org/) | `3.10.8` | Figure plotting |
| [numpy](https://numpy.org/) | `2.4.2` | Numerical computation |

---

---

## `09` &nbsp; Tutorials

<table>
<tr>
<td width="50%" align="center" valign="top">

### Concepts, Theory, and Paper Background

<a href="https://youtu.be/hbQn5vrRxDE">
  <img src="./Tutorial/Concepts.png" alt="Concepts, Theory, and Paper Background Tutorial" width="100%"/>
</a>

<br/>

<a href="https://youtu.be/hbQn5vrRxDE">
  Watch Tutorial
</a>

</td>
<td width="50%" align="center" valign="top">

### How to Use the Repository

<a href="https://youtu.be/F_b91hB_YSM">
  <img src="./Tutorial/Github.png" alt="How to Use the QdcEm Repository Tutorial" width="100%"/>
</a>

<br/>

<a href="https://youtu.be/F_b91hB_YSM">
  Watch Tutorial
</a>

</td>
</tr>
</table>

--

## `10` &nbsp; Citation

```bibtex
@article{elyasi2025quantum,
  title   = {A Framework for Quantum Data Center Emulation Using Digital Quantum Computers},
  author  = {Elyasi, S. N. and Monti, P. and Li, J. and Lin, R.},
  journal = {arXiv preprint arXiv:2509.04029},
  year    = {2025},
  url     = {https://arxiv.org/abs/2509.04029}
}
```

---

<div align="center">

Made at **Chalmers University of Technology**

<img src="https://capsule-render.vercel.app/api?type=waving&color=0f62fe&height=100&section=footer" width="100%"/>

</div>
