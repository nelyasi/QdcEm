
# Standard library imports
from math import pi, sqrt, exp
from collections import defaultdict

# Third-party imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
from qutip import *
from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister, IfElseOp
from qiskit.circuit.library import UnitaryGate


def M_Unitary(kappa):
    """
    Constructs the unitary operator for a single collision step of the
    Collisional Model (CM) interaction between a system qubit and an
    environment qubit.

    This implements the interaction Hamiltonian from Eq. (2) of the paper:

        H_j = kappa * (sigma_+^FQ ⊗ sigma_-^E + sigma_-^FQ ⊗ sigma_+^E)

    which describes an amplitude-damping (excitation-exchange) process
    between the flying qubit (FQ) and a single environment ancilla.
    The resulting unitary U_j = exp(-i H_j) is used to emulate both
    transduction-induced noise (coupling strength kappa_T) and
    optical-fiber-induced noise (coupling strength kappa_F) on the
    communication channel between QPUs.

    Parameters
    ----------
    kappa : float
        Tunable coupling constant (either kappa_T or kappa_F) defining
        the interaction strength between the system qubit and the
        environment ancilla.

    Returns
    -------
    UnitaryGate
        A Qiskit UnitaryGate object implementing exp(-i H_j) for the
        given kappa, ready to be appended to a QuantumCircuit.
    """
    # Hamiltonian: κ (σ_+^FQ ⊗ σ_-^E + σ_-^FQ ⊗ σ_+^E)
    H = kappa * (tensor(sigmap(), sigmam()) + tensor(sigmam(), sigmap()))
    # Unitary evolution: U = exp(-i H)
    U = (-1j * H).expm()
    return UnitaryGate(U.full())


def remote_cx(qc, control, target, CommA, CommB, ENA, ENB,
               creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote CNOT (CX) gate using the
    Cat-State Communication (Cat-Comm) protocol with CM noise injection,
    as described in Section 2.A and Fig. 4(a) of the paper.

    Noise model (Algorithm 1, lines 4–8):
      1. A Bell pair |Φ+⟩ is generated between CommA and CommB.
      2. One transducer collision (coupling kappa_T) is applied on each
         side; the environment qubit is then reset to enforce the
         Markovian assumption (Eq. 1).
      3. One initial fiber collision (coupling kappa_F) is applied on
         each side.
      4. Steps additional fiber collisions follow, each preceded by an
         environment-qubit reset.  Each collision represents a 10 m
         fiber segment, so the total propagation distance is
         D = 10*(1 + Steps) metres.

    The corrective feed-forward operations after the mid-circuit
    measurements complete the Cat-Comm protocol and restore the
    communication qubits for future use (reset at the end).

    Parameters
    ----------
    qc            : QuantumCircuit
    control       : Qubit  — processing qubit in QPU A (control)
    target        : Qubit  — processing qubit in QPU B (target)
    CommA         : Qubit  — communication qubit in QPU A
    CommB         : Qubit  — communication qubit in QPU B
    ENA           : Qubit  — environment qubit for QPU A (recycled via Reset)
    ENB           : Qubit  — environment qubit for QPU B (recycled via Reset)
    creg          : ClassicalRegister
    creg_index    : int    — base index into creg for mid-circuit measurements
    kappa_Fiber   : float  — fiber coupling constant kappa_F =sqrt(0.01*alpha)
    Steps         : int    — number of additional 10 m fiber collisions
    kappa_Transductor : float  — transducer coupling constant kappa_T = 0.5
    """
    # ── Bell pair generation ───────────────────────────────────────────
    qc.barrier()
    qc.h(CommA)
    qc.cx(CommA, CommB)
    qc.barrier()

    # ── Transducer collision (one per side) ────────────────────────────
    qc.append(M_Unitary(kappa_Transductor), [CommA, ENA])
    qc.append(M_Unitary(kappa_Transductor), [CommB, ENB])
    qc.reset(ENA)
    qc.reset(ENB)

    # ── First fiber collision ──────────────────────────────────────────
    qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
    qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Additional fiber collisions (each 10 m segment) ────────────────
    for _ in range(Steps):
        qc.reset(ENA)
        qc.reset(ENB)
        qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
        qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Cat-Comm protocol for remote CX ───────────────────────────────
    qc.cx(control, CommA)
    qc.measure(CommA, creg[creg_index])

    with qc.if_test((creg[creg_index], 1)):
        qc.x(CommA)
        qc.x(CommB)

    qc.cx(CommB, target)
    qc.h(CommB)
    qc.measure(CommB, creg[creg_index + 1])

    with qc.if_test((creg[creg_index + 1], 1)):
        qc.z(control)

    qc.reset(CommA)
    qc.reset(CommB)


def remote_cx_TP1(qc, control, target, CommA, CommB, ENA, ENB,
                  creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote CNOT (CX) gate using the
    single-teleportation (TP1) protocol with CM noise injection,
    as described in Section 2.A and Fig. 4(b) of the paper.

    Unlike Cat-Comm, TP1 teleports the control qubit's state to QPU B,
    where the CNOT is applied locally.  This avoids the shared cat-like
    state but leaves the teleported state on a communication qubit,
    potentially blocking resources for subsequent remote operations.

    The noise model is identical to remote_cx: one transducer collision
    per side, one initial fiber collision, and `Steps` additional fiber
    collisions, each with an environment-qubit reset.

    Parameters
    ----------
    (Same layout as remote_cx; see that docstring for parameter details.)
    """
    # ── Bell pair generation ───────────────────────────────────────────
    qc.barrier()
    qc.h(CommA)
    qc.cx(CommA, CommB)
    qc.barrier()

    # ── Transducer collision ───────────────────────────────────────────
    qc.append(M_Unitary(kappa_Transductor), [CommA, ENA])
    qc.append(M_Unitary(kappa_Transductor), [CommB, ENB])
    qc.reset(ENA)
    qc.reset(ENB)

    # ── First fiber collision ──────────────────────────────────────────
    qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
    qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Additional fiber collisions ────────────────────────────────────
    for _ in range(Steps):
        qc.reset(ENA)
        qc.reset(ENB)
        qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
        qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── TP1 protocol: teleport control state to CommB ──────────────────
    qc.barrier()
    qc.cx(control, CommA)

    qc.measure(CommA, creg[creg_index])
    with qc.if_test((creg[creg_index], 1)):
        qc.x(CommA)
        qc.x(CommB)

    qc.h(control)
    qc.measure(control, creg[creg_index + 1])
    with qc.if_test((creg[creg_index + 1], 1)):
        qc.x(control)
        qc.z(CommB)

    # ── Apply local CNOT on QPU B (control state now in CommB) ─────────
    qc.barrier()
    qc.cx(CommB, target)
    qc.barrier()


def remote_cp(qc, theta, control, target, CommA, CommB, ENA, ENB,
               creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote controlled-phase (CP) gate using
    the Cat-Comm protocol with CM noise injection.

    The controlled-phase gate applies a phase shift theta to the target
    qubit conditioned on the control qubit being |1⟩.  The noise model is
    identical to remote_cx: one transducer collision per communication
    qubit followed by fiber collisions with environment resets, ensuring
    the same Bell-pair fidelity expression (Eq. 3) applies to every
    remote gate type used in the distributed QFT (Fig. 8c).

    Parameters
    ----------
    theta : float  — phase rotation angle for the CP gate.
    (All other parameters identical to remote_cx.)
    """
    # ── Bell pair generation ───────────────────────────────────────────
    qc.barrier()
    qc.h(CommA)
    qc.cx(CommA, CommB)
    qc.barrier()

    # ── Transducer collision ───────────────────────────────────────────
    qc.append(M_Unitary(kappa_Transductor), [CommA, ENA])
    qc.append(M_Unitary(kappa_Transductor), [CommB, ENB])
    qc.reset(ENA)
    qc.reset(ENB)

    # ── First fiber collision ──────────────────────────────────────────
    qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
    qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Additional fiber collisions ────────────────────────────────────
    for _ in range(Steps):
        qc.reset(ENA)
        qc.reset(ENB)
        qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
        qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Cat-Comm protocol for remote CP ───────────────────────────────
    qc.cx(control, CommA)
    qc.measure(CommA, creg[creg_index])

    with qc.if_test((creg[creg_index], 1)):
        qc.x(CommA)
        qc.x(CommB)

    qc.cp(theta, CommB, target)
    qc.h(CommB)
    qc.measure(CommB, creg[creg_index + 1])

    with qc.if_test((creg[creg_index + 1], 1)):
        qc.z(control)

    qc.reset(CommA)
    qc.reset(CommB)
    qc.barrier()


def remote_cz(qc, control, target, CommA, CommB, ENA, ENB,
               creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote controlled-Z (CZ) gate using
    the Cat-Comm protocol with CM noise injection.

    Noise model identical to remote_cx; only the local gate on CommB–target
    is changed from CNOT to CZ.

    Parameters
    ----------
    (Same as remote_cx.)
    """
    # ── Bell pair generation ───────────────────────────────────────────
    qc.barrier()
    qc.h(CommA)
    qc.cx(CommA, CommB)
    qc.barrier()

    # ── Transducer collision ───────────────────────────────────────────
    qc.append(M_Unitary(kappa_Transductor), [CommA, ENA])
    qc.append(M_Unitary(kappa_Transductor), [CommB, ENB])
    qc.reset(ENA)
    qc.reset(ENB)

    # ── First fiber collision ──────────────────────────────────────────
    qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
    qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Additional fiber collisions ────────────────────────────────────
    for _ in range(Steps):
        qc.reset(ENA)
        qc.reset(ENB)
        qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
        qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Cat-Comm protocol for remote CZ ───────────────────────────────
    qc.cx(control, CommA)
    qc.measure(CommA, creg[creg_index])

    with qc.if_test((creg[creg_index], 1)):
        qc.x(CommA)
        qc.x(CommB)

    qc.cz(CommB, target)
    qc.h(CommB)
    qc.measure(CommB, creg[creg_index + 1])

    with qc.if_test((creg[creg_index + 1], 1)):
        qc.z(control)

    qc.reset(CommA)
    qc.reset(CommB)
    qc.barrier()


def remote_cu(qc, theta, phi, lam, gamma, control, target, CommA, CommB,
              ENA, ENB, creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote controlled-U gate with an
    arbitrary single-qubit target unitary using the Cat-Comm protocol
    with CM noise injection.

    The CNOT and CZ gates are special cases of CU; this function provides
    the general form.  Noise model is identical to all other remote gates
    in this module.

    Parameters
    ----------
    theta, phi, lam, gamma : float
        Parameters of Qiskit's CU gate defining the single-qubit rotation.
    (All other parameters identical to remote_cx.)
    """
    # ── Bell pair generation ───────────────────────────────────────────
    qc.barrier()
    qc.h(CommA)
    qc.cx(CommA, CommB)
    qc.barrier()

    # ── Transducer collision ───────────────────────────────────────────
    qc.append(M_Unitary(kappa_Transductor), [CommA, ENA])
    qc.append(M_Unitary(kappa_Transductor), [CommB, ENB])
    qc.reset(ENA)
    qc.reset(ENB)

    # ── First fiber collision ──────────────────────────────────────────
    qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
    qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Additional fiber collisions ────────────────────────────────────
    for _ in range(Steps):
        qc.reset(ENA)
        qc.reset(ENB)
        qc.append(M_Unitary(kappa_Fiber), [CommA, ENA])
        qc.append(M_Unitary(kappa_Fiber), [CommB, ENB])

    # ── Cat-Comm protocol for remote CU ───────────────────────────────
    qc.cx(control, CommA)
    qc.measure(CommA, creg[creg_index])

    with qc.if_test((creg[creg_index], 1)):
        qc.x(CommA)
        qc.x(CommB)

    qc.cu(theta, phi, lam, gamma, CommB, target)
    qc.h(CommB)
    qc.measure(CommB, creg[creg_index + 1])

    with qc.if_test((creg[creg_index + 1], 1)):
        qc.z(control)

    qc.reset(CommA)
    qc.reset(CommB)
    qc.barrier()
