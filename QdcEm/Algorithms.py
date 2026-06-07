
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


def remote_cz(qc, control, target, CommA, CommB, ENA, ENB,
               creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote controlled-Z (CZ) gate using
    the Cat-State Communication (Cat-Comm) protocol with CM noise injection,
    as described in Section 2.A of the paper.

    Noise model (Algorithm 1, lines 4–8):
      1. A Bell pair is prepared between CommA and CommB.
      2. Each communication qubit undergoes one transducer collision
         (coupling kappa_Transductor) with its environment qubit (ENA/ENB),
         after which the environment qubit is reset to |0⟩.
      3. Each communication qubit then undergoes one initial fiber collision
         (coupling kappa_Fiber), followed by `Steps` additional fiber
         collisions, each preceded by an environment qubit reset.

    This models the progressive entanglement degradation described by
    Eq. (3) and the mapping D(n) = gamma*n/alpha in the paper.

    Parameters
    ----------
    qc : QuantumCircuit
    control : Qubit  — processing qubit in QPU A (control)
    target  : Qubit  — processing qubit in QPU B (target)
    CommA   : Qubit  — communication qubit in QPU A
    CommB   : Qubit  — communication qubit in QPU B
    ENA     : Qubit  — environment qubit for QPU A (recycled via Reset)
    ENB     : Qubit  — environment qubit for QPU B (recycled via Reset)
    creg    : ClassicalRegister
    creg_index    : int  — base index into creg for mid-circuit measurements
    kappa_Fiber   : float  — fiber coupling constant (kappa_F)
    Steps         : int    — number of additional 10 m fiber segments
    kappa_Transductor : float  — transducer coupling constant (kappa_T)
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


def remote_cx(qc, control, target, CommA, CommB, ENA, ENB,
               creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote CNOT (CX) gate using the
    Cat-State Communication (Cat-Comm) protocol with CM noise injection,
    as described in Section 2.A of the paper.

    The noise model is identical to remote_cz: one transducer collision
    per side followed by an initial fiber collision and `Steps` additional
    fiber collisions, each with environment-qubit reset to enforce the
    Markovian (memory-less) assumption of the CM (Eq. 1).

    Parameters
    ----------
    (Same as remote_cz, except the target gate applied on CommB–target
     is a CNOT rather than a CZ.)
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


def remote_cp(qc, theta, control, target, CommA, CommB, ENA, ENB,
               creg, creg_index, kappa_Fiber, Steps, kappa_Transductor):
    """
    Implements a noisy distributed remote controlled-phase (CP) gate using
    the Cat-Comm protocol with CM noise injection.

    The noise model is identical to remote_cx / remote_cz: one transducer
    collision per communication qubit followed by fiber collisions with
    environment resets.  This consistency is required so that the same
    Bell-pair fidelity expression (Eq. 3) applies to every remote gate
    type used in the distributed QFT (Fig. 8c).

    Parameters
    ----------
    theta : float  — phase rotation angle for the CP gate.
    (All other parameters identical to remote_cz.)
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


def qft_circuit(n):
    """
    Constructs the monolithic n-qubit Quantum Fourier Transform (QFT) circuit
    as defined in Section 2.D of the paper.

    The circuit applies, for each qubit j (0 to n-1):
      • a Hadamard gate on qubit j, and
      • controlled-phase rotations R_k with angle 2π/2^k between qubit j
        and each subsequent qubit j+k.
    A final SWAP layer reverses the qubit order to match the standard
    QFT output convention.

    For n = 5 this requires 5 Hadamard gates, 10 controlled-phase
    rotation gates, and 2 SWAP gates (Fig. 8a in the paper).

    Parameters
    ----------
    n : int  — number of qubits.

    Returns
    -------
    QuantumCircuit
        Monolithic QFT circuit (unmeasured).
    """
    qc = QuantumCircuit(n, n)
    for j in range(n):
        qc.h(j)
        for k in range(1, n - j):
            qc.cp(2 * pi / 2 ** (k + 1), j + k, j)
    # Reverse qubit order (SWAP layer)
    for i in range(n // 2):
        qc.swap(i, n - i - 1)
    qc.name = "QFT"
    return qc


def qft_5qubit_annotated_Distributed(Steps, kappa_Fiber, kappa_Transductor):
    """
    Constructs the distributed 5-qubit QFT circuit across two logical QPUs,
    as described in Section 2.D and illustrated in Fig. 8(c) of the paper.

    Qubit layout (9 physical qubits total):
      QPU A: QA1 (q0), QA2 (q1), ENA (q2), CommA (q3)
      QPU B: CommB (q4), ENB (q5), QB1 (q6), QB2 (q7), QB3 (q8)

    Logical qubit assignment:
      QA2 → q5 (most significant, appears first after reordering)
      QA1 → q1
      QB1 → q2
      QB2 → q3
      QB3 → q4

    To avoid the SWAP layer present in the monolithic circuit (Fig. 8a),
    the qubit order in the circuit is rearranged so that q5 appears first,
    yielding the new circuit order: q5, q1, q2, q3, q4 (Fig. 8b).
    Measurements are taken in the original logical order q1…q5.

    Cross-QPU controlled-phase gates are realised as noisy remote_cp
    calls; intra-QPU controlled-phase gates remain local.  Communication
    uses G-654-E fiber (lowest attenuation, alpha = 0.0392 km⁻¹) and
    transducer noise kappa_T = 0.5 (consistent with all other experiments
    in the paper).

    The classical register has 10 bits: bits 0–7 are consumed (two per
    remote_cp call) by the four remote gates; bits 8–9 are spare.

    Parameters
    ----------
    Steps            : int   — number of additional 10 m fiber segments
    kappa_Fiber      : float — fiber coupling constant derived from alpha
                               via kappa_F = sqrt(0.01 * alpha)
    kappa_Transductor: float — transducer coupling constant (kappa_T = 0.5)

    Returns
    -------
    QuantumCircuit
        Distributed 5-qubit QFT circuit (unmeasured processing qubits).
    """
    q = QuantumRegister(9, 'q')
    c = ClassicalRegister(10, 'c')
    qc = QuantumCircuit(q, c)

    # QPU A qubits: QA1 (logical q1), QA2 (logical q5), ENA, CommA
    QA1, QA2, ENA, CommA = q[0], q[1], q[2], q[3]
    # QPU B qubits: CommB, ENB, QB1 (logical q2), QB2 (logical q3), QB3 (logical q4)
    CommB, ENB, QB1, QB2, QB3 = q[4], q[5], q[6], q[7], q[8]

    # ── QFT on reordered qubits: q5, q1, q2, q3, q4 ──────────────────
    # Processing order: QA2 (q5) first, then QA1 (q1), QB1 (q2), QB2 (q3), QB3 (q4)

    # --- QA2 (logical q5) ---
    qc.h(QA2)
    # R_2 between QA2 and QB1 (cross-QPU)  → remote_cp, angle = pi/2
    remote_cp(qc, pi / 2,   QB1, QA2, CommA, CommB, ENA, ENB, c, 0, kappa_Fiber, Steps, kappa_Transductor)
    # R_3 between QA2 and QB2 (cross-QPU)  → remote_cp, angle = pi/4
    remote_cp(qc, pi / 4,   QB2, QA2, CommA, CommB, ENA, ENB, c, 2, kappa_Fiber, Steps, kappa_Transductor)
    # R_4 between QA2 and QB3 (cross-QPU)  → remote_cp, angle = pi/8
    remote_cp(qc, pi / 8,   QB3, QA2, CommA, CommB, ENA, ENB, c, 4, kappa_Fiber, Steps, kappa_Transductor)
    # R_5 between QA2 and QA1 (intra-QPU A) → local cp, angle = pi/16
    qc.cp(pi / 16, QA1, QA2)

    # --- QB1 (logical q2) ---
    qc.h(QB1)
    # R_2 between QB1 and QB2 (intra-QPU B) → local cp, angle = pi/2
    qc.cp(pi / 2, QB2, QB1)
    # R_3 between QB1 and QB3 (intra-QPU B) → local cp, angle = pi/4
    qc.cp(pi / 4, QB3, QB1)
    # R_4 between QB1 and QA1 (cross-QPU)  → remote_cp, angle = pi/8
    remote_cp(qc, pi / 8,   QA1, QB1, CommA, CommB, ENA, ENB, c, 6, kappa_Fiber, Steps, kappa_Transductor)

    # --- QB2 (logical q3) ---
    qc.h(QB2)
    # R_2 between QB2 and QB3 (intra-QPU B) → local cp, angle = pi/2
    qc.cp(pi / 2, QB3, QB2)
    # R_3 between QB2 and QA1 (cross-QPU)  → remote_cp, angle = pi/4
    remote_cp(qc, pi / 4,   QA1, QB2, CommA, CommB, ENA, ENB, c, 8, kappa_Fiber, Steps, kappa_Transductor)

    # --- QB3 (logical q4) ---
    qc.h(QB3)
    # R_2 between QB3 and QA1 (cross-QPU) — would be remote; included for completeness
    # remote_cp(qc, pi/2, QA1, QB3, CommA, CommB, ENA, ENB, c, 10, kappa_Fiber, Steps, kappa_Transductor)

    # --- QA1 (logical q1) ---
    qc.h(QA1)

    # ── No SWAP layer needed (qubit order already reversed by reordering) ──

    return qc


def grover_2qubit_annotated_Distributed(marked_states, kappa_Fiber, Steps, kappa_Transductor):
    """
    Constructs the distributed 2-qubit Grover's search algorithm circuit
    across two logical QPUs, as described in Section 2.C and Fig. 7(b)
    of the paper.

    Each QPU holds one processing qubit (QPUA and QPUB).  Remote gates
    are implemented via the Cat-Comm protocol with CM noise injection.
    The 6-qubit register layout is:

        q[0] = QPUA   (processing qubit, QPU A)
        q[1] = ENA    (environment qubit, QPU A — dashed in diagrams)
        q[2] = CommA  (communication qubit, QPU A)
        q[3] = CommB  (communication qubit, QPU B)
        q[4] = ENB    (environment qubit, QPU B — dashed in diagrams)
        q[5] = QPUB   (processing qubit, QPU B)

    The oracle uses remote_cz to implement the phase-flip on the marked
    state; the diffusion operator uses remote_cx for the multi-controlled
    reflection.  For 2 qubits and 1 marked state a single Grover iteration
    maximises the success probability (Fig. 7a).

    Parameters
    ----------
    marked_states     : list[str]  — list of 2-bit strings, e.g. ['00']
    kappa_Fiber       : float      — fiber coupling constant (kappa_F)
    Steps             : int        — number of additional 10 m fiber segments
    kappa_Transductor : float      — transducer coupling constant (kappa_T)

    Returns
    -------
    QuantumCircuit
        Distributed Grover circuit with final measurement on QPUA and QPUB
        stored in classical bits c[4] and c[5].
    """
    if not all(len(s) == 2 for s in marked_states):
        raise ValueError("All marked states must be 2-bit strings (e.g., '01', '11')")

    num_iterations = int(np.floor((np.pi / 4) * np.sqrt(4 / len(marked_states))))

    q = QuantumRegister(6, 'q')
    c = ClassicalRegister(6, 'c')
    qc = QuantumCircuit(q, c)

    QPUA, ENA, CommA, CommB, ENB, QPUB = q

    # ── Initial equal superposition ────────────────────────────────────
    qc.h([QPUA, QPUB])
    qc.barrier(label='Start Superposition')

    def apply_oracle(qc, marked_states, QPUA, QPUB, CommA, CommB,
                     ENA, ENB, c, index, kappa_Fiber, Steps, kappa_Transductor):
        """Phase-flip oracle: flips the sign of the marked state amplitude."""
        for state in marked_states:
            qc.barrier(label='Oracle')
            if state[0] == '0':
                qc.x(QPUA)
            if state[1] == '0':
                qc.x(QPUB)
            remote_cz(qc, QPUA, QPUB, CommA, CommB, ENA, ENB,
                      c, index, kappa_Fiber, Steps, kappa_Transductor)
            if state[0] == '0':
                qc.x(QPUA)
            if state[1] == '0':
                qc.x(QPUB)

    def apply_diffusion(qc, QPUA, QPUB, CommA, CommB,
                        ENA, ENB, c, index, kappa_Fiber, Steps, kappa_Transductor):
        """Grover diffusion operator: amplitude reflection about the mean."""
        qc.barrier(label='Diffusion')
        qc.h([QPUA, QPUB])
        qc.x([QPUA, QPUB])
        qc.h(QPUB)
        remote_cx(qc, QPUA, QPUB, CommA, CommB, ENA, ENB,
                  c, index, kappa_Fiber, Steps, kappa_Transductor)
        qc.h(QPUB)
        qc.x([QPUA, QPUB])
        qc.h([QPUA, QPUB])

    for _ in range(num_iterations):
        apply_oracle(qc, marked_states, QPUA, QPUB, CommA, CommB,
                     ENA, ENB, c, 0, kappa_Fiber, Steps, kappa_Transductor)
        apply_diffusion(qc, QPUA, QPUB, CommA, CommB,
                        ENA, ENB, c, 2, kappa_Fiber, Steps, kappa_Transductor)

    qc.barrier(label='Measurement')
    qc.measure([QPUA, QPUB], [4, 5])

    return qc
