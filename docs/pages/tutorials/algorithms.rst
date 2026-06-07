Distributed Algorithms
=======================

The ``Algorithms`` module provides three complete distributed quantum
algorithms that compose the remote gates defined in ``RemoteGates``.

Bell-state entanglement generation
------------------------------------

Cross-QPU Bell-state creation using a single noisy remote CNOT. This
serves as the foundational benchmark: the measured Bell-state fidelity
directly characterises channel quality as a function of fiber length
and fiber type, reproducing Figure 5 of the paper.

Grover's Search
----------------

A two-qubit Grover's algorithm partitioned across two virtual QPUs.
Each QPU holds one processing qubit. The oracle applies a phase flip
via ``remote_cz``; the diffusion operator uses ``remote_cx``. For a
single marked state, one Grover iteration maximises the success
probability.

Qubit register layout (6 physical qubits)::

   q[0] = QPUA   (processing qubit, QPU A)
   q[1] = ENA    (environment qubit, QPU A)
   q[2] = CommA  (communication qubit, QPU A)
   q[3] = CommB  (communication qubit, QPU B)
   q[4] = ENB    (environment qubit, QPU B)
   q[5] = QPUB   (processing qubit, QPU B)

::

   from QdcEm.Algorithms import grover_2qubit_annotated_Distributed

   qc = grover_2qubit_annotated_Distributed(
       marked_states     = ['11'],
       kappa_Fiber       = 0.05,
       Steps             = 2,
       kappa_Transductor = 0.5,
   )

Results are validated against published ion-trap experimental data in
Section 2.C of the paper.

Quantum Fourier Transform (QFT)
---------------------------------

A five-qubit QFT split across two virtual QPUs. QPU A holds two
processing qubits (QA1, QA2); QPU B holds three (QB1, QB2, QB3). Each
controlled-phase rotation that crosses the QPU boundary is implemented
as a noisy ``remote_cp`` call. Fidelity is evaluated via quantum state
tomography and compared against both the noiseless ideal and a
monolithic baseline.

To avoid the SWAP layer present in the standard monolithic circuit, the
qubit order is rearranged so that QA2 (the most significant qubit)
appears first in the circuit, eliminating the final reversal at no
extra gate cost. ::

   from QdcEm.Algorithms import qft_5qubit_annotated_Distributed

   qc = qft_5qubit_annotated_Distributed(
       Steps             = 3,
       kappa_Fiber       = 0.04,
       kappa_Transductor = 0.5,
   )

.. note::

   All three algorithms return an unmeasured ``QuantumCircuit``. Add
   measurement gates and submit to ``AerSimulator`` or a live backend
   as shown in the :doc:`quickstart`.
