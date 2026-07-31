Installation
============

Requirements
------------

Make sure you have Python 3.9 or higher installed. ::

   $ python3 --version
   Python 3.9.18

Make sure you have pip version 23.0 or higher installed. ::

   $ python3 -m pip --version
   pip 23.3.1

Installing dependencies
-----------------------

QdcEm depends on the following packages. The versions below were used
for all experiments reported in the paper (as of February 27, 2026):

.. list-table::
   :header-rows: 1
   :widths: 30 20

   * - Package
     - Version
   * - ``qiskit``
     - ``2.3.0``
   * - ``qutip``
     - ``5.2.3``
   * - ``matplotlib``
     - ``3.10.8``
   * - ``numpy``
     - ``2.4.2``

Install all dependencies at once::

   $ pip install qiskit==2.3.0 qutip==5.2.3 matplotlib==3.10.8 numpy==2.4.2

For IBM Quantum hardware execution, also install::

   $ pip install qiskit-ibm-runtime qiskit-aer

Cloning the repository
-----------------------

::

   $ git clone https://github.com/nelyasi/QdcEm.git
   $ cd QdcEm

Verifying the installation
---------------------------

Open an interactive Python session and import the package::

   >>> from QdcEm.RemoteGates import remote_cx
   >>> from QdcEm.QPU import Make
   >>> print("QdcEm ready")

This should produce::

   QdcEm ready

Repository structure
--------------------

::

   QdcEm/
   ├── QdcEm/
   │   ├── __init__.py          # Runtime service imports and global setup
   │   ├── QPU.py               # QPU data structure and layout utilities
   │   ├── RemoteGates.py       # Cat-Comm and teleportation remote gate library
   │   ├── Algorithms.py        # Distributed QFT, Grover, entanglement
   │   └── Representation.py    # Plotting utilities and circuit display styles
   ├── Example/                 # Two worked example notebooks
   ├── Calibration_Data/        # IBM Quantum device calibration JSON files
   ├── Jobs/                    # Saved experiment job records
   ├── Plots/                   # Output figures
   ├── QubitSets/               # Pre-defined qubit layout configurations
   ├── Tutorial/                # Step-by-step tutorial notebooks
   ├── Main.ipynb               # Top-level notebook reproducing all paper results
   ├── generate_plots.py        # Script to recreate all paper figures
   └── requirements.txt
