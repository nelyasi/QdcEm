RemoteGates module
==================

``QdcEm.RemoteGates`` — Cat-State Communication and teleportation-based
distributed gate library.

----

M_Unitary
---------

.. code-block:: python

   M_Unitary(kappa)

Constructs the unitary operator for a single CM collision step between
a system qubit and an environment qubit. Implements the interaction
Hamiltonian:

.. math::

   \hat{H}_j = \kappa \left(
       \hat{\sigma}^-_{\mathrm{FQ}} \otimes \hat{\sigma}^+_E
     + \hat{\sigma}^+_{\mathrm{FQ}} \otimes \hat{\sigma}^-_E
   \right)

The resulting unitary Û\ :sub:`j` = exp(−i Ĥ\ :sub:`j`) is used to
emulate both transduction-induced noise (κ\ :sub:`T`) and
optical-fiber-induced noise (κ\ :sub:`F`).

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Name
     - Type
     - Description
   * - ``kappa``
     - ``float``
     - Coupling constant — either κ\ :sub:`T` (transducer) or
       κ\ :sub:`F` (fiber).

**Returns** ``UnitaryGate`` — Qiskit gate implementing
exp(−i Ĥ\ :sub:`j`).

----

remote_cx
---------

.. code-block:: python

   remote_cx(qc, control, target, CommA, CommB, ENA, ENB,
             creg, creg_index, kappa_Fiber, Steps, kappa_Transductor)

Implements a noisy distributed remote CNOT (CX) gate using the
Cat-State Communication (Cat-Comm) protocol with CM noise injection,
as described in Section 2.A and Figure 4(a) of the paper.

The noise sequence is: one transducer collision per communication
qubit, one initial fiber collision, and ``Steps`` additional fiber
collisions each preceded by an environment-qubit reset. The corrective
feed-forward operations after the mid-circuit measurements complete the
Cat-Comm protocol and restore the communication qubits for future use.

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Name
     - Type
     - Description
   * - ``qc``
     - ``QuantumCircuit``
     - Circuit to which operations are appended.
   * - ``control``
     - ``Qubit``
     - Processing qubit in QPU A (control).
   * - ``target``
     - ``Qubit``
     - Processing qubit in QPU B (target).
   * - ``CommA`` / ``CommB``
     - ``Qubit``
     - Communication qubits in QPU A and QPU B.
   * - ``ENA`` / ``ENB``
     - ``Qubit``
     - Environment ancillae, reset between collisions to enforce the
       Markovian assumption.
   * - ``creg``
     - ``ClassicalRegister``
     - Classical register for mid-circuit measurements.
   * - ``creg_index``
     - ``int``
     - Base index into ``creg``; two consecutive bits are consumed.
   * - ``kappa_Fiber``
     - ``float``
     - Fiber coupling constant κ\ :sub:`F` = √(0.01 · α).
   * - ``Steps``
     - ``int``
     - Number of additional 10 m fiber segments beyond the first.
   * - ``kappa_Transductor``
     - ``float``
     - Transducer coupling constant κ\ :sub:`T` (typical value: 0.5).

----

remote_cz
---------

.. code-block:: python

   remote_cz(qc, control, target, CommA, CommB, ENA, ENB,
             creg, creg_index, kappa_Fiber, Steps, kappa_Transductor)

Implements a noisy distributed remote CZ gate using Cat-Comm. The
noise model is identical to ``remote_cx``; the local gate applied on
CommB–target is a CZ rather than a CNOT.

All parameters are identical to :ref:`remote_cx`.

----

remote_cp
---------

.. code-block:: python

   remote_cp(qc, theta, control, target, CommA, CommB, ENA, ENB,
             creg, creg_index, kappa_Fiber, Steps, kappa_Transductor)

Implements a noisy distributed remote controlled-phase (CP) gate using
Cat-Comm. Used as the building block for the distributed QFT.

**Additional parameter**

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Name
     - Type
     - Description
   * - ``theta``
     - ``float``
     - Phase rotation angle for the CP gate.

All other parameters are identical to :ref:`remote_cx`.

----

remote_cx_TP1
--------------

.. code-block:: python

   remote_cx_TP1(qc, control, target, CommA, CommB, ENA, ENB,
                 creg, creg_index, kappa_Fiber, Steps, kappa_Transductor)

Implements a noisy distributed remote CNOT using the single-teleportation
(TP1) protocol. Unlike Cat-Comm, TP1 teleports the control qubit's
state to QPU B where the CNOT is applied locally. The teleported state
remains on a communication qubit until explicitly reset, which may
block resources for subsequent remote operations.

All parameters are identical to :ref:`remote_cx`.

----

remote_cu
---------

.. code-block:: python

   remote_cu(qc, theta, phi, lam, gamma, control, target,
             CommA, CommB, ENA, ENB,
             creg, creg_index, kappa_Fiber, Steps, kappa_Transductor)

Implements a noisy distributed remote controlled-U gate with an
arbitrary single-qubit target unitary using Cat-Comm. The CNOT and CZ
gates are special cases of this function.

**Additional parameters**

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Name
     - Type
     - Description
   * - ``theta``, ``phi``, ``lam``, ``gamma``
     - ``float``
     - Parameters of Qiskit's ``CUGate`` defining the single-qubit
       rotation.

All other parameters are identical to :ref:`remote_cx`.
