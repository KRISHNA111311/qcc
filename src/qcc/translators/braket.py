from ..core.models import CircuitAST, GateType

class BraketTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "from braket.circuits import Circuit",
            "",
            "circuit = Circuit()"
        ]

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"circuit.h({gate.qubits[0]})")
            elif gate.type == GateType.CX:
                lines.append(f"circuit.cnot({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CZ:
                lines.append(f"circuit.cz({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.SWAP:
                lines.append(f"circuit.swap({gate.qubits[0]}, {gate.qubits[1]})")
            elif gate.type == GateType.CCX:
                lines.append(f"circuit.ccnot({gate.qubits[0]}, {gate.qubits[1]}, {gate.qubits[2]})")
            elif gate.type == GateType.X:
                lines.append(f"circuit.x({gate.qubits[0]})")
            elif gate.type == GateType.Y:
                lines.append(f"circuit.y({gate.qubits[0]})")
            elif gate.type == GateType.Z:
                lines.append(f"circuit.z({gate.qubits[0]})")
            elif gate.type == GateType.S:
                lines.append(f"circuit.s({gate.qubits[0]})")
            elif gate.type == GateType.SDG:
                lines.append(f"circuit.si({gate.qubits[0]})")
            elif gate.type == GateType.T:
                lines.append(f"circuit.t({gate.qubits[0]})")
            elif gate.type == GateType.TDG:
                lines.append(f"circuit.ti({gate.qubits[0]})")
            elif gate.type == GateType.SX:
                lines.append(f"circuit.sx({gate.qubits[0]})")
            elif gate.type == GateType.I:
                lines.append(f"circuit.i({gate.qubits[0]})")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"circuit.rx({gate.qubits[0]}, {gate.params[0]})")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"circuit.ry({gate.qubits[0]}, {gate.params[0]})")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"circuit.rz({gate.qubits[0]}, {gate.params[0]})")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"circuit.phase({gate.qubits[0]}, {gate.params[0]})")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                lines.append(f"circuit.measure({q})")
            elif gate.type == GateType.RESET:
                lines.append(f"circuit.reset({gate.qubits[0]})")
            elif gate.type == GateType.BARRIER:
                lines.append(f"circuit.barrier({gate.qubits[0]})")

        lines.append("")
        lines.append("# To simulate:")
        lines.append("from braket.devices import LocalSimulator")
        lines.append("device = LocalSimulator()")
        lines.append("task = device.run(circuit, shots=1024)")
        lines.append("result = task.result()")
        lines.append("counts = result.measurement_counts")
        lines.append("print(counts)")

        return "\n".join(lines)
