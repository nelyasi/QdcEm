Examples
========

Two self-contained Jupyter notebooks in ``Example/`` illustrate the
most common workflows. Both notebooks can be run end-to-end against
the ``AerSimulator`` without access to IBM Quantum hardware.

Example 1 — Bell Pair Fidelity Landscape
------------------------------------------

**File:** ``Example/Example1_BellPair_Fidelity_Landscape.ipynb``

This notebook sweeps κ\ :sub:`F` and the number of fiber steps to map
the Bell-state fidelity as a two-dimensional landscape. It
demonstrates how to:

- construct a minimal two-QPU layout using ``Make``,
- call ``remote_cx`` with varying noise parameters inside a loop,
- simulate each circuit on ``AerSimulator`` and extract fidelity from
  the measurement counts, and
- plot the fidelity landscape using the utilities in
  ``Representation.py``.

This is the recommended starting point for understanding how noise
parameters affect channel quality.

Example 2 — Protocol Race: Cat-Comm vs TP1
--------------------------------------------

**File:** ``Example/Example2_Protocol_Race_CatComm_vs_TP1.ipynb``

This notebook runs both ``remote_cx`` (Cat-Comm) and
``remote_cx_TP1`` side by side under identical noise conditions and
plots their fidelity trajectories as a function of fiber distance. It
demonstrates the practical trade-off between the two communication
strategies:

- **Cat-Comm** restores the communication qubits at the end of each
  gate, making them available for subsequent operations.
- **TP1** teleports the control qubit's state to the target QPU, which
  can block communication resources for subsequent remote operations.

Reproducing all paper figures
-------------------------------

All figures from the paper can be reproduced by running::

   $ python generate_plots.py

Output images are written to ``Plots/``. Alternatively, ``Main.ipynb``
walks through every experiment interactively and embeds the figures
inline. Each cell corresponds to a labelled section of the paper and
loads the appropriate calibration snapshot from ``Calibration_Data/``.
