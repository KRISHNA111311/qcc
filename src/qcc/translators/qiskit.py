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
            elif gate.type == GateType.CZ:
                lines.append(f"qc.cz({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.SWAP:
                lines.append(f"qc.swap({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CCX:
                lines.append(f"qc.ccx({gate.qubits[0]}, {gate.qubits[1]}, {gate.qubits[2]})")
            elif gate.type == GateType.I:
                lines.append(f"qc.i({gate.qubits[0]})")
            elif gate.type == GateType.S:
                lines.append(f"qc.s({gate.qubits[0]})")
            elif gate.type == GateType.SDG:
                lines.append(f"qc.sdg({gate.qubits[0]})")
            elif gate.type == GateType.T:
                lines.append(f"qc.t({gate.qubits[0]})")
            elif gate.type == GateType.TDG:
                lines.append(f"qc.tdg({gate.qubits[0]})")
            elif gate.type == GateType.SX:
                lines.append(f"qc.sx({gate.qubits[0]})")
            elif gate.type == GateType.X:
                lines.append(f"qc.x({gate.qubits[0]})")
            elif gate.type == GateType.Y:
                lines.append(f"qc.y({gate.qubits[0]})")
            elif gate.type == GateType.Z:
                lines.append(f"qc.z({gate.qubits[0]})")
            elif gate.type == GateType.U:
                if len(gate.params) >= 3:
                    lines.append(f"qc.u({gate.params[0]}, {gate.params[1]}, {gate.params[2]}, {gate.qubits[0]})")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"qc.rx({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"qc.ry({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"qc.rz({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"qc.p({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                c = gate.classical_bits[0] if gate.classical_bits else q
                lines.append(f"qc.measure({q}, {c})")

        if not any(g.type == GateType.MEASURE for g in ast.operations):
            lines.append("qc.measure_all()")

        return "\n".join(lines)
