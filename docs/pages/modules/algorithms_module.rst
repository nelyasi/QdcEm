Algorithms module
=================

``QdcEm.Algorithms`` — Distributed quantum algorithm circuits built on
top of the ``RemoteGates`` library.

----

grover_2qubit_annotated_Distributed
-------------------------------------

.. code-block:: python

   grover_2qubit_annotated_Distributed(marked_states, kappa_Fiber,
                                        Steps, kappa_Transductor)

Constructs the distributed 2-qubit Grover's search circuit across two
logical QPUs, as described in Section 2.C and Figure 7(b) of the
paper. Each QPU holds one processing qubit. The oracle applies a phase
flip on the marked state via ``remote_cz``; the diffusion operator
uses ``remote_cx``.

For a single marked state, one Grover iteration maximises the success
probability (Figure 7a of the paper).

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Type
     - Description
   * - ``marked_states``
     - ``list[str]``
     - List of 2-bit strings to be marked, e.g. ``['11']`` or
       ``['00', '11']``.
   * - ``kappa_Fiber``
     - ``float``
     - Fiber coupling constant κ\ :sub:`F`.
   * - ``Steps``
     - ``int``
     - Number of additional 10 m fiber segments.
   * - ``kappa_Transductor``
     - ``float``
     - Transducer coupling constant κ\ :sub:`T`.

**Returns** ``QuantumCircuit`` — 6-qubit distributed Grover circuit
with final measurements on QPUA (``c[4]``) and QPUB (``c[5]``).

----

qft_5qubit_annotated_Distributed
----------------------------------

.. code-block:: python

   qft_5qubit_annotated_Distributed(Steps, kappa_Fiber, kappa_Transductor)

Constructs the distributed 5-qubit QFT circuit across two logical
QPUs, as described in Section 2.D and Figure 8(c) of the paper.
QPU A holds QA1 and QA2; QPU B holds QB1, QB2, and QB3. Cross-QPU
controlled-phase rotations are implemented as noisy ``remote_cp``
calls using G-654-E fiber (α = 0.0392 km\ :sup:`-1`).

To avoid the SWAP layer present in the standard monolithic circuit
(Figure 8a), the qubit order is rearranged so that QA2 (the most
significant qubit) appears first, yielding a SWAP-free implementation
(Figure 8b). Measurements are taken in the original logical order.

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Type
     - Description
   * - ``Steps``
     - ``int``
     - Number of additional 10 m fiber segments per remote gate.
   * - ``kappa_Fiber``
     - ``float``
     - Fiber coupling constant κ\ :sub:`F`.
   * - ``kappa_Transductor``
     - ``float``
     - Transducer coupling constant κ\ :sub:`T`.

**Returns** ``QuantumCircuit`` — 9-qubit distributed QFT circuit with
processing qubits unmeasured.
