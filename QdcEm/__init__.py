# Importing necessary functions and constants
from math import pi, sqrt, exp  # Importing pi, sqrt, and exp functions/constants from math module
import matplotlib.pyplot as plt
# Importing Qiskit Aer Simulator from qiskit_aer package
from qiskit_aer import AerSimulator
from qiskit.transpiler import Layout

import numpy as np
from qutip import *
from collections import defaultdict
# Importing IBMProvider and QiskitRuntimeService from qiskit_ibm_provider and qiskit_ibm_runtime packages

from qiskit.circuit.library import UnitaryGate
from qiskit_ibm_runtime import QiskitRuntimeService