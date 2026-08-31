from ..core.models import CircuitAST, GateType

class MyQLMTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "from qat.lang.AQASM import Program, H, X, Y, Z, S, T, RX, RY, RZ, CNOT, CZ, SWAP, CCX, PH, I, BARRIER, RESET, MEASURE",
            "from qat.lang.AQASM import Program",
            "",
            "prog = Program()",
            f"qbits = prog.qalloc({ast.num_qubits})"
        ]

        for gate in ast.operations:
            if gate.type == GateType.H:
                lines.append(f"prog.apply(H, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.CX:
                lines.append(f"prog.apply(CNOT, qbits[{gate.qubits[0]}], qbits[{gate.qubits[1]}])")
            elif gate.type == GateType.CZ:
                lines.append(f"prog.apply(CZ, qbits[{gate.qubits[0]}], qbits[{gate.qubits[1]}])")
            elif gate.type == GateType.SWAP:
                lines.append(f"prog.apply(SWAP, qbits[{gate.qubits[0]}], qbits[{gate.qubits[1]}])")
            elif gate.type == GateType.CCX:
                lines.append(f"prog.apply(CCX, qbits[{gate.qubits[0]}], qbits[{gate.qubits[1]}], qbits[{gate.qubits[2]}])")
            elif gate.type == GateType.X:
                lines.append(f"prog.apply(X, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.Y:
                lines.append(f"prog.apply(Y, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.Z:
                lines.append(f"prog.apply(Z, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.S:
                lines.append(f"prog.apply(S, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.SDG:
                lines.append(f"prog.apply(S.dag(), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.T:
                lines.append(f"prog.apply(T, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.TDG:
                lines.append(f"prog.apply(T.dag(), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.SX:
                # SX is sqrt(X) - use RX(pi/2)
                lines.append(f"prog.apply(RX(3.14159/2), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.I:
                lines.append(f"prog.apply(I, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"prog.apply(RX({gate.params[0]}), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"prog.apply(RY({gate.params[0]}), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"prog.apply(RZ({gate.params[0]}), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"prog.apply(PH({gate.params[0]}), qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                lines.append(f"prog.apply(MEASURE, qbits[{q}])")
            elif gate.type == GateType.RESET:
                lines.append(f"prog.apply(RESET, qbits[{gate.qubits[0]}])")
            elif gate.type == GateType.BARRIER:
                lines.append(f"prog.apply(BARRIER, qbits[{gate.qubits[0]}])")

        lines.append("")
        lines.append("circuit = prog.to_circ()")
        lines.append("")
        lines.append("# To simulate:")
        lines.append("from qat.qpus import get_default_qpu")
        lines.append("qpu = get_default_qpu()")
        lines.append("job = circuit.to_job(nbshots=1024)")
        lines.append("result = qpu.submit(job)")
        lines.append("for sample in result:")
        lines.append("    print(sample)")

        return "\n".join(lines)
