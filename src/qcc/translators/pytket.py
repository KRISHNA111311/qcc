from ..core.models import CircuitAST, GateType

class PyTketTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "from pytket import Circuit",
            f"circ = Circuit({ast.num_qubits}, {ast.num_classical})"
        ]

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"circ.H({gate.qubits[0]})")
            elif gate.type == GateType.CX:
                lines.append(f"circ.CX({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CZ:
                lines.append(f"circ.CZ({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.SWAP:
                lines.append(f"circ.SWAP({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CCX:
                lines.append(f"circ.CCX({gate.qubits[0]}, {gate.qubits[1]}, {gate.qubits[2]})")
            elif gate.type == GateType.X:
                lines.append(f"circ.X({gate.qubits[0]})")
            elif gate.type == GateType.Y:
                lines.append(f"circ.Y({gate.qubits[0]})")
            elif gate.type == GateType.Z:
                lines.append(f"circ.Z({gate.qubits[0]})")
            elif gate.type == GateType.S:
                lines.append(f"circ.S({gate.qubits[0]})")
            elif gate.type == GateType.SDG:
                lines.append(f"circ.Sdg({gate.qubits[0]})")
            elif gate.type == GateType.T:
                lines.append(f"circ.T({gate.qubits[0]})")
            elif gate.type == GateType.TDG:
                lines.append(f"circ.Tdg({gate.qubits[0]})")
            elif gate.type == GateType.SX:
                lines.append(f"circ.SX({gate.qubits[0]})")
            elif gate.type == GateType.I:
                lines.append(f"circ.I({gate.qubits[0]})")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"circ.Rx({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"circ.Ry({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"circ.Rz({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"circ.Phase({gate.params[0]}, {gate.qubits[0]})")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                c = gate.classical_bits[0] if gate.classical_bits else q
                lines.append(f"circ.Measure({q}, {c})")
            elif gate.type == GateType.RESET:
                lines.append(f"circ.Reset({gate.qubits[0]})")
            elif gate.type == GateType.BARRIER:
                lines.append(f"circ.Barrier({gate.qubits[0]})")

        lines.append("")
        lines.append("# To simulate using AerBackend:")
        lines.append("from pytket.extensions.qiskit import AerBackend")
        lines.append("backend = AerBackend()")
        lines.append("compiled_circ = backend.get_compiled_circuit(circ)")
        lines.append("handle = backend.process_circuit(compiled_circ, n_shots=1024)")
        lines.append("result = backend.get_result(handle)")
        lines.append("counts = result.get_counts()")
        lines.append("print(counts)")

        return "\n".join(lines)
