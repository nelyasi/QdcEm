Quickstart
==========

A brief introduction to using QdcEm to emulate a distributed quantum
gate across two virtual QPUs on a single superconducting chip. We
illustrate this by constructing a two-QPU layout and applying a noisy
remote CNOT gate.

- `Download the Main notebook <https://github.com/<your-org>/QdcEm/blob/main/Main.ipynb>`__, or
- read through the text below and code along.

**Contents:**

- `1. Imports`_
- `2. Define qubit registers`_
- `3. Apply a noisy remote CNOT`_
- `4. Run on the Aer simulator`_

1. Imports
----------

First, import the necessary Qiskit and QdcEm components::

   from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
   from QdcEm.QPU import Make, Get_Initial_Layout
   from QdcEm.RemoteGates import remote_cx

2. Define qubit registers
--------------------------

Create a five-qubit register and assign roles. Each QPU requires one
**communication qubit**, one **environment qubit**, and one or more
**processing qubits**. ::

   qreg = QuantumRegister(5, 'q')
   creg = ClassicalRegister(4, 'c')
   qc   = QuantumCircuit(qreg, creg)

   # QPU A: processing on q[2], communication on q[0], environment on q[1]
   qpu_A = Make(Comm=qreg[0], EN=qreg[1], Processing_Qubits=[qreg[2]])

   # QPU B: communication on q[3], environment on q[4]
   qpu_B = Make(Comm=qreg[3], EN=qreg[4], Processing_Qubits=[])

3. Apply a noisy remote CNOT
-----------------------------

The ``remote_cx`` function appends the full Cat-Comm protocol — Bell
pair generation, CM noise injection, mid-circuit measurements, and
feed-forward corrections — directly to the circuit. ::

   remote_cx(
       qc,
       control           = qreg[2],   # processing qubit in QPU A
       target            = qreg[3],   # processing qubit in QPU B
       CommA             = qpu_A.Comm,
       CommB             = qpu_B.Comm,
       ENA               = qpu_A.EN,
       ENB               = qpu_B.EN,
       creg              = creg,
       creg_index        = 0,
       kappa_Fiber       = 0.05,      # sqrt(0.01 * alpha), one 10 m segment
       Steps             = 3,         # three additional 10 m fiber collisions
       kappa_Transductor = 0.1,
   )

   qc.measure(qreg[2], creg[2])
   qc.measure(qreg[3], creg[3])

4. Run on the Aer simulator
----------------------------

::

   from qiskit_aer import AerSimulator

   simulator = AerSimulator()
   job = simulator.run(qc, shots=1024)
   result = job.result()
   counts = result.get_counts()
   print(counts)

.. note::

   To run on real IBM hardware, replace ``AerSimulator()`` with a
   backend obtained via ``QiskitRuntimeService`` and pass the
   ``initial_layout`` produced by ``Get_Initial_Layout`` at transpile
   time.
