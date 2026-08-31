from ..core.models import CircuitAST, GateType

class CUDAQTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "import cudaq",
            "",
            "@cudaq.kernel",
            "def circuit():",
            f"    q = cudaq.qvector({ast.num_qubits})"
        ]

        for gate in ast.operations:
            indent = "    "
            if gate.type == GateType.H:
                lines.append(f"{indent}h(q[{gate.qubits[0]}])")
            elif gate.type == GateType.CX:
                lines.append(f"{indent}cx(q[{gate.qubits[0]}], q[{gate.qubits[1]}])")
            elif gate.type == GateType.CZ:
                lines.append(f"{indent}cz(q[{gate.qubits[0]}], q[{gate.qubits[1]}])")
            elif gate.type == GateType.SWAP:
                lines.append(f"{indent}swap(q[{gate.qubits[0]}], q[{gate.qubits[1]}])")
            elif gate.type == GateType.CCX:
                lines.append(f"{indent}ccx(q[{gate.qubits[0]}], q[{gate.qubits[1]}], q[{gate.qubits[2]}])")
            elif gate.type == GateType.X:
                lines.append(f"{indent}x(q[{gate.qubits[0]}])")
            elif gate.type == GateType.Y:
                lines.append(f"{indent}y(q[{gate.qubits[0]}])")
            elif gate.type == GateType.Z:
                lines.append(f"{indent}z(q[{gate.qubits[0]}])")
            elif gate.type == GateType.S:
                lines.append(f"{indent}s(q[{gate.qubits[0]}])")
            elif gate.type == GateType.SDG:
                lines.append(f"{indent}sdg(q[{gate.qubits[0]}])")
            elif gate.type == GateType.T:
                lines.append(f"{indent}t(q[{gate.qubits[0]}])")
            elif gate.type == GateType.TDG:
                lines.append(f"{indent}tdg(q[{gate.qubits[0]}])")
            elif gate.type == GateType.SX:
                lines.append(f"{indent}sx(q[{gate.qubits[0]}])")
            elif gate.type == GateType.I:
                # CUDA-Q doesn't have identity, skip
                pass
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"{indent}rx({gate.params[0]}, q[{gate.qubits[0]}])")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"{indent}ry({gate.params[0]}, q[{gate.qubits[0]}])")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"{indent}rz({gate.params[0]}, q[{gate.qubits[0]}])")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"{indent}phase({gate.params[0]}, q[{gate.qubits[0]}])")
            elif gate.type == GateType.MEASURE:
                lines.append(f"{indent}mz(q[{gate.qubits[0]}])")
            elif gate.type == GateType.RESET:
                # Not directly supported
                pass
            elif gate.type == GateType.BARRIER:
                # Not directly supported
                pass

        lines.append("")
        lines.append("# To simulate:")
        lines.append("result = cudaq.sample(circuit, shots_count=1024)")
        lines.append("print(result)")

        return "\n".join(lines)
