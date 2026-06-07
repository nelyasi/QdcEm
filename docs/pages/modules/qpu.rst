QPU module
==========

``QdcEm.QPU`` — QPU data structure and initial-layout utilities.

----

Make
----

.. code-block:: python

   Make(Comm, EN, Processing_Qubits)

A lightweight data class that bundles the three qubit roles required by
every QPU in the emulation.

**Attributes**

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Type
     - Description
   * - ``Comm``
     - ``Qubit``
     - The communication qubit that mediates the entangled channel.
   * - ``EN``
     - ``Qubit``
     - The environment ancilla qubit, recycled via reset between
       collisions.
   * - ``Processing_Qubits``
     - ``list[Qubit]``
     - One or more processing qubits that hold the algorithm's logical
       state.

**Example**

::

   qpu_A = Make(Comm=qreg[0], EN=qreg[1], Processing_Qubits=[qreg[2], qreg[3]])

----

Get_Initial_Layout
-------------------

.. code-block:: python

   Get_Initial_Layout(QPUs, QRG)

Constructs a Qiskit ``Layout`` object mapping the logical qubit
register to physical device qubits. The layout is built in order:
``Comm``, ``EN``, then each qubit in ``Processing_Qubits``, for each
QPU in the list.

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Name
     - Type
     - Description
   * - ``QPUs``
     - ``list[Make]``
     - Ordered list of QPU objects.
   * - ``QRG``
     - ``QuantumRegister``
     - The circuit's quantum register whose indices are mapped to
       physical qubits.

**Returns** ``Layout`` — Qiskit transpiler layout for use with
``transpile(..., initial_layout=...)``.
