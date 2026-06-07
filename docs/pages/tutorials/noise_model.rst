Noise Model
===========

The QdcEm noise model is based on the **Collisional Model (CM)**
framework. This page describes the physical assumptions, mathematical
formulation, and circuit-level implementation of the CM within the
QdcEm gate primitives.

Physical motivation
-------------------

In a real Quantum Data Center, QPUs communicate via quantum channels
that traverse a microwave-to-optical transducer and an optical fiber
link. Each stage introduces decoherence:

- **Transducer noise** arises from imperfect microwave-to-optical
  conversion, modelled by coupling constant κ\ :sub:`T`.
- **Fiber noise** arises from photon loss along the optical fiber,
  modelled by coupling constant κ\ :sub:`F` = √(0.01 · α), where α is
  the fiber attenuation coefficient (km\ :sup:`-1`).

Interaction Hamiltonian
------------------------

Each collision step between the flying qubit (FQ) and a single
environment ancilla E is governed by:

.. math::

   \hat{H}_j = \kappa \left(
       \hat{\sigma}^-_{\mathrm{FQ}} \otimes \hat{\sigma}^+_E
     + \hat{\sigma}^+_{\mathrm{FQ}} \otimes \hat{\sigma}^-_E
   \right)

This is an excitation-exchange (amplitude-damping) interaction. The
corresponding unitary for a single collision step is:

.. math::

   \hat{U}_j = \exp\!\left(-i\hat{H}_j\right)

This unitary is computed numerically via QuTiP's ``expm()`` routine and
wrapped as a Qiskit ``UnitaryGate`` by ``M_Unitary(kappa)``.

Channel noise sequence
-----------------------

For every remote gate, noise is injected in three stages:

1. **Bell pair generation.** CommA and CommB are prepared in the state
   |Φ\ :sup:`+`\ ⟩ = (|00⟩ + |11⟩)/√2.

2. **Transducer collisions.** One CM collision at strength κ\ :sub:`T`
   is applied to each communication qubit. The environment qubit is
   reset to |0⟩ after each collision to enforce the Markovian
   (memoryless) assumption.

3. **Fiber collisions.** One initial CM collision at strength
   κ\ :sub:`F` is applied per side, followed by ``Steps`` further
   collisions — each preceded by an environment-qubit reset. Each
   collision models a 10 m fiber segment, so the total channel distance
   is D = 10 · (1 + Steps) metres.

Supported fiber grades
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 30 25

   * - ITU-T Grade
     - Attenuation α (km\ :sup:`-1`)
     - κ\ :sub:`F`
   * - G-652-D
     - 0.0415
     - 0.02037
   * - G-654-E
     - 0.0392
     - 0.01980
   * - G-655-D
     - 0.0507
     - 0.02252
   * - Numerical reference
     - 0.0415
     - 0.02037

Implementation
--------------

::

   from QdcEm.RemoteGates import M_Unitary

   # Construct the CM unitary for kappa_T = 0.5
   U_T = M_Unitary(kappa=0.5)

   # Append to a circuit: one collision between CommA and ENA
   qc.append(U_T, [CommA, ENA])
   qc.reset(ENA)   # enforce the Markovian assumption
