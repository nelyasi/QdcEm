from qiskit.transpiler import Layout


class Make:
    def __init__(self, Comm, EN, Processing_Qubits):
        self.Comm = Comm
        self.EN = EN
        self.Processing_Qubits = Processing_Qubits


def Get_Initial_Layout(QPUs, QRG):

    initial_layout = {}
    ind = 0

    for qpu in QPUs:

        initial_layout[QRG[ind]] = qpu.Comm
        ind += 1
        initial_layout[QRG[ind]] = qpu.EN


        for pq in qpu.Processing_Qubits:
            ind += 1
            initial_layout[QRG[ind]] = pq
    
    return Layout(initial_layout)


