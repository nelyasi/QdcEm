Representation module
=====================

``QdcEm.Representation`` — Plotting utilities and custom circuit
display styles for reproducing the paper figures.

----

Circuit display style
---------------------

The module defines a custom Qiskit circuit style that colour-codes the
two CM gate types, matching the convention used throughout the paper:

.. list-table::
   :header-rows: 1
   :widths: 20 25 30 25

   * - Gate label
     - Display text
     - Fill colour
     - Text colour
   * - ``U_T``
     - Û\ :sub:`T`
     - Purple (``#b266ff``)
     - Black
   * - ``U_F``
     - Û\ :sub:`F`
     - Dark green (``#228B22``)
     - White

Pass the style dictionary to ``qc.draw('mpl', style=style)`` to match
the circuit diagrams in the paper::

   from QdcEm.Representation import style
   qc.draw('mpl', style=style)

----

plot_normalized_results
------------------------

.. code-block:: python

   plot_normalized_results(results, plot_type, state, shots, kappa_T)

Plots the measured success probability of a remote CNOT gate versus
fiber communication steps, reproducing Figure 5 of the paper. The
x-axis begins with a monolithic reference point *M* (no inter-QPU
noise) followed by steps 1–10. Four curves are shown — G-652-D,
G-654-E, G-655-D, and a numerical (AerSimulator) reference.

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Type
     - Description
   * - ``results``
     - ``dict``
     - Keys are fiber-type labels (``'G-652-D'``, ``'G-654-E'``,
       ``'G-655-D'``, ``'Numerical'``). Values are lists of raw
       success counts; the first element is the monolithic (M) result.
   * - ``plot_type``
     - ``str``
     - Protocol label shown in the figure title, e.g. ``'Cat-Comm'``
       or ``'TP1'``.
   * - ``state``
     - ``int`` or ``str``
     - Initial state of the control qubit (0 or 1).
   * - ``shots``
     - ``int``
     - Total measurement shots per data point; used for normalisation.
   * - ``kappa_T``
     - ``float``
     - Transducer coupling constant used in this experiment.
