from typing import List
from ..core.models import CircuitAST, Gate, GateType

class AsciiCircuit:
    @staticmethod
    def draw(circuit: CircuitAST) -> str:
        if not circuit.operations:
            return "(empty circuit)"

        num_qubits = circuit.num_qubits or 1
        lines = [""] * num_qubits
        wire_labels = [f"q[{i}]" for i in range(num_qubits)]

        for i in range(num_qubits):
            lines[i] = f"{wire_labels[i]}: "

        for gate in circuit.operations:
            if gate.type == GateType.H:
                q = gate.qubits[0]
                lines[q] += "───[H]───"
            elif gate.type == GateType.CX:
                c, t = gate.qubits[0], gate.qubits[1]
                lines[c] += "───●────"
                lines[t] += "───[X]───"
            elif gate.type == GateType.X:
                q = gate.qubits[0]
                lines[q] += "───[X]───"
            elif gate.type == GateType.Y:
                q = gate.qubits[0]
                lines[q] += "───[Y]───"
            elif gate.type == GateType.Z:
                q = gate.qubits[0]
                lines[q] += "───[Z]───"
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                lines[q] += "───[M]───"
            else:
                q = gate.qubits[0]
                lines[q] += f"───[{gate.type.value}]───"

        return "\n".join(lines)
