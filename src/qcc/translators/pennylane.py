from ..core.models import CircuitAST, GateType

class PennyLaneTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "import pennylane as qml",
            "",
            f"dev = qml.device('default.qubit', wires={ast.num_qubits}, shots=1024)",
            "",
            "@qml.qnode(dev)",
            "def circuit():"
        ]

        # Indent all gate operations inside the QNode
        for gate in ast.operations:
            indent = "    "
            if gate.type == GateType.H:
                lines.append(f"{indent}qml.Hadamard(wires={gate.qubits[0]})")
            elif gate.type == GateType.CX:
                lines.append(f"{indent}qml.CNOT(wires=[{gate.qubits[0]}, {gate.qubits[1]}])")
            elif gate.type == GateType.CZ:
                lines.append(f"{indent}qml.CZ(wires=[{gate.qubits[0]}, {gate.qubits[1]}])")
            elif gate.type == GateType.SWAP:
                lines.append(f"{indent}qml.SWAP(wires=[{gate.qubits[0]}, {gate.qubits[1]}])")
            elif gate.type == GateType.CCX:
                lines.append(f"{indent}qml.Toffoli(wires=[{gate.qubits[0]}, {gate.qubits[1]}, {gate.qubits[2]}])")
            elif gate.type == GateType.X:
                lines.append(f"{indent}qml.PauliX(wires={gate.qubits[0]})")
            elif gate.type == GateType.Y:
                lines.append(f"{indent}qml.PauliY(wires={gate.qubits[0]})")
            elif gate.type == GateType.Z:
                lines.append(f"{indent}qml.PauliZ(wires={gate.qubits[0]})")
            elif gate.type == GateType.S:
                lines.append(f"{indent}qml.S(wires={gate.qubits[0]})")
            elif gate.type == GateType.SDG:
                lines.append(f"{indent}qml.S(wires={gate.qubits[0]}).inv()")
            elif gate.type == GateType.T:
                lines.append(f"{indent}qml.T(wires={gate.qubits[0]})")
            elif gate.type == GateType.TDG:
                lines.append(f"{indent}qml.T(wires={gate.qubits[0]}).inv()")
            elif gate.type == GateType.SX:
                lines.append(f"{indent}qml.SX(wires={gate.qubits[0]})")
            elif gate.type == GateType.I:
                lines.append(f"{indent}qml.Identity(wires={gate.qubits[0]})")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"{indent}qml.RX({gate.params[0]}, wires={gate.qubits[0]})")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"{indent}qml.RY({gate.params[0]}, wires={gate.qubits[0]})")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"{indent}qml.RZ({gate.params[0]}, wires={gate.qubits[0]})")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"{indent}qml.PhaseShift({gate.params[0]}, wires={gate.qubits[0]})")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                c = gate.classical_bits[0] if gate.classical_bits else q
                # PennyLane counts returns all measurements
                # We'll collect all measure gates and return counts at the end
                # For simplicity, we'll just add a measure for each qubit
                lines.append(f"{indent}qml.measure(wires={q})")
            elif gate.type == GateType.RESET:
                lines.append(f"{indent}qml.Reset(wires={gate.qubits[0]})")
            elif gate.type == GateType.BARRIER:
                lines.append(f"{indent}qml.Barrier(wires={gate.qubits[0]})")

        lines.append("    return qml.counts()")
        lines.append("")
        lines.append("# Run the circuit")
        lines.append("counts = circuit()")
        lines.append("print(counts)")

        return "\n".join(lines)
