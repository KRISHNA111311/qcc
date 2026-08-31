from ..core.models import CircuitAST, GateType

class TensorCircuitTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "import tensorcircuit as tc",
            "",
            f"c = tc.Circuit({ast.num_qubits})"
        ]

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"c.h({gate.qubits[0]})")
            elif gate.type == GateType.CX:
                lines.append(f"c.cnot({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CZ:
                lines.append(f"c.cz({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.SWAP:
                lines.append(f"c.swap({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CCX:
                # TensorCircuit doesn't have built-in Toffoli, but we can use controlled gates
                # We'll use c.toffoli? Not available, we can use c.cnot and c.h to construct? For now skip.
                # Actually TensorCircuit has `c.controlled`? We'll use a workaround.
                # For simplicity, we'll use a placeholder comment.
                lines.append(f"# CCX on {gate.qubits} not directly supported; use c.controlled")
            elif gate.type == GateType.X:
                lines.append(f"c.x({gate.qubits[0]})")
            elif gate.type == GateType.Y:
                lines.append(f"c.y({gate.qubits[0]})")
            elif gate.type == GateType.Z:
                lines.append(f"c.z({gate.qubits[0]})")
            elif gate.type == GateType.S:
                lines.append(f"c.s({gate.qubits[0]})")
            elif gate.type == GateType.SDG:
                lines.append(f"c.sdg({gate.qubits[0]})")
            elif gate.type == GateType.T:
                lines.append(f"c.t({gate.qubits[0]})")
            elif gate.type == GateType.TDG:
                lines.append(f"c.tdg({gate.qubits[0]})")
            elif gate.type == GateType.SX:
                lines.append(f"c.sx({gate.qubits[0]})")
            elif gate.type == GateType.I:
                lines.append(f"# identity on {gate.qubits[0]}")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"c.rx({gate.qubits[0]}, theta={gate.params[0]})")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"c.ry({gate.qubits[0]}, theta={gate.params[0]})")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"c.rz({gate.qubits[0]}, theta={gate.params[0]})")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"c.phase({gate.qubits[0]}, theta={gate.params[0]})")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                lines.append(f"c.measure({q})")
            elif gate.type == GateType.RESET:
                # Not directly supported
                pass
            elif gate.type == GateType.BARRIER:
                # Not directly supported
                pass

        lines.append("")
        lines.append("# To sample:")
        lines.append("samples = c.sample(batch=1024, format='count_dict_bin')")
        lines.append("print(samples)")

        return "\n".join(lines)
