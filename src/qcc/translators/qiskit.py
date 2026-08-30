from ..core.models import CircuitAST, GateType

class QiskitTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "from qiskit import QuantumCircuit",
            f"qc = QuantumCircuit({ast.num_qubits}, {ast.num_classical})"
        ]

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"qc.h({gate.qubits[0]})")
            elif gate.type == GateType.CX:
                lines.append(f"qc.cx({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.X:
                lines.append(f"qc.x({gate.qubits[0]})")
            elif gate.type == GateType.Y:
                lines.append(f"qc.y({gate.qubits[0]})")
            elif gate.type == GateType.Z:
                lines.append(f"qc.z({gate.qubits[0]})")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                c = gate.classical_bits[0] if gate.classical_bits else q
                lines.append(f"qc.measure({q}, {c})")
            elif gate.type == GateType.SWAP:
                lines.append(f"qc.swap({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.PHASE:
                if len(gate.params) > 0:
                    lines.append(f"qc.p({gate.params[0]}, {gate.qubits[0]})")
            # Add more gates as needed

        # If no measure gates, add measure_all
        has_measure = any(g.type == GateType.MEASURE for g in ast.operations)
        if not has_measure and ast.num_classical > 0:
            lines.append("qc.measure_all()")

        return "\n".join(lines)
