from ..core.models import CircuitAST, GateType

class CirqTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "import cirq",
            f"qubits = cirq.LineQubit.range({ast.num_qubits})",
            "circuit = cirq.Circuit()"
        ]

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"circuit.append(cirq.H(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.CX:
                lines.append(f"circuit.append(cirq.CNOT(qubits[{gate.qubits[0]}], qubits[{gate.qubits[1]}]))")
            elif gate.type == GateType.CZ:
                lines.append(f"circuit.append(cirq.CZ(qubits[{gate.qubits[0]}], qubits[{gate.qubits[1]}]))")
            elif gate.type == GateType.SWAP:
                lines.append(f"circuit.append(cirq.SWAP(qubits[{gate.qubits[0]}], qubits[{gate.qubits[1]}]))")
            elif gate.type == GateType.CCX:
                lines.append(f"circuit.append(cirq.CCNOT(qubits[{gate.qubits[0]}], qubits[{gate.qubits[1]}], qubits[{gate.qubits[2]}]))")
            elif gate.type == GateType.X:
                lines.append(f"circuit.append(cirq.X(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.Y:
                lines.append(f"circuit.append(cirq.Y(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.Z:
                lines.append(f"circuit.append(cirq.Z(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.S:
                lines.append(f"circuit.append(cirq.S(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.SDG:
                lines.append(f"circuit.append(cirq.S**-1(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.T:
                lines.append(f"circuit.append(cirq.T(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.TDG:
                lines.append(f"circuit.append(cirq.T**-1(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.SX:
                lines.append(f"circuit.append(cirq.X**0.5(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.I:
                lines.append(f"circuit.append(cirq.I(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"circuit.append(cirq.rx({gate.params[0]})(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"circuit.append(cirq.ry({gate.params[0]})(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"circuit.append(cirq.rz({gate.params[0]})(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"circuit.append(cirq.rz({gate.params[0]})(qubits[{gate.qubits[0]}]))")  # Phase is RZ in Cirq
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                c = gate.classical_bits[0] if gate.classical_bits else q
                lines.append(f"circuit.append(cirq.measure(qubits[{q}], key='result_{c}'))")
            elif gate.type == GateType.RESET:
                lines.append(f"circuit.append(cirq.ResetChannel()(qubits[{gate.qubits[0]}]))")
            elif gate.type == GateType.BARRIER:
                lines.append(f"circuit.append(cirq.barrier(qubits[{gate.qubits[0]}]))")

        lines.append("")
        lines.append("# To simulate:")
        lines.append("simulator = cirq.Simulator()")
        lines.append("result = simulator.run(circuit, repetitions=1024)")
        lines.append("counts = result.histogram(key='result')")

        return "\n".join(lines)
