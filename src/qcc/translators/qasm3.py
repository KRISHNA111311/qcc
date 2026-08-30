from ..core.models import CircuitAST, GateType

class QASM3Translator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "OPENQASM 3.0;",
            'include "stdgates.inc";',
            f"qubit[{ast.num_qubits}] q;"
        ]
        if ast.num_classical > 0:
            lines.append(f"bit[{ast.num_classical}] c;")
        lines.append("")

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"h q[{gate.qubits[0]}];")
            elif gate.type == GateType.CX:
                lines.append(f"cx q[{gate.qubits[0]}], q[{gate.qubits[1]}];")
            elif gate.type == GateType.X:
                lines.append(f"x q[{gate.qubits[0]}];")
            elif gate.type == GateType.Y:
                lines.append(f"y q[{gate.qubits[0]}];")
            elif gate.type == GateType.Z:
                lines.append(f"z q[{gate.qubits[0]}];")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                c = gate.classical_bits[0] if gate.classical_bits else q
                lines.append(f"c[{c}] = measure q[{q}];")
            elif gate.type == GateType.SWAP:
                lines.append(f"swap q[{gate.qubits[0]}], q[{gate.qubits[1]}];")
            elif gate.type == GateType.PHASE:
                if len(gate.params) > 0:
                    lines.append(f"p({gate.params[0]}) q[{gate.qubits[0]}];")

        # If no measure, add measure_all
        has_measure = any(g.type == GateType.MEASURE for g in ast.operations)
        if not has_measure and ast.num_classical > 0:
            lines.append(f"c = measure q;")

        return "\n".join(lines)
