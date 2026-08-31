from ..core.models import CircuitAST, GateType

class StimTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "import stim",
            "",
            "circuit = stim.Circuit(\"\"\""
        ]

        # For Stim, we generate operations as strings inside the circuit.
        stim_lines = []
        for gate in ast.operations:
            if gate.type == GateType.H:
                stim_lines.append(f"    H {gate.qubits[0]}")
            elif gate.type == GateType.CX:
                stim_lines.append(f"    CX {gate.qubits[0]} {gate.qubits[1]}")
            elif gate.type == GateType.CZ:
                stim_lines.append(f"    CZ {gate.qubits[0]} {gate.qubits[1]}")
            elif gate.type == GateType.SWAP:
                stim_lines.append(f"    SWAP {gate.qubits[0]} {gate.qubits[1]}")
            elif gate.type == GateType.CCX:
                stim_lines.append(f"    CCX {gate.qubits[0]} {gate.qubits[1]} {gate.qubits[2]}")
            elif gate.type == GateType.X:
                stim_lines.append(f"    X {gate.qubits[0]}")
            elif gate.type == GateType.Y:
                stim_lines.append(f"    Y {gate.qubits[0]}")
            elif gate.type == GateType.Z:
                stim_lines.append(f"    Z {gate.qubits[0]}")
            elif gate.type == GateType.S:
                stim_lines.append(f"    S {gate.qubits[0]}")
            elif gate.type == GateType.SDG:
                stim_lines.append(f"    S_DAG {gate.qubits[0]}")
            elif gate.type == GateType.T:
                stim_lines.append(f"    T {gate.qubits[0]}")
            elif gate.type == GateType.TDG:
                stim_lines.append(f"    T_DAG {gate.qubits[0]}")
            elif gate.type == GateType.SX:
                stim_lines.append(f"    SX {gate.qubits[0]}")
            elif gate.type == GateType.I:
                stim_lines.append(f"    I {gate.qubits[0]}")
            elif gate.type == GateType.RX:
                if gate.params:
                    # Stim doesn't have RX; we can approximate but for now skip
                    pass
            elif gate.type == GateType.RY:
                pass
            elif gate.type == GateType.RZ:
                pass
            elif gate.type == GateType.PHASE:
                pass
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                stim_lines.append(f"    M {q}")
            elif gate.type == GateType.RESET:
                stim_lines.append(f"    R {gate.qubits[0]}")
            elif gate.type == GateType.BARRIER:
                stim_lines.append(f"    DEPOLARIZE1(0) {gate.qubits[0]}  # Barrier approximated")

        lines.extend(stim_lines)
        lines.append("\"\"\")")
        lines.append("")
        lines.append("# To simulate:")
        lines.append("sampler = circuit.compile_sampler()")
        lines.append("samples = sampler.sample(shots=1024)")
        lines.append("print(samples)")

        return "\n".join(lines)
