from ..core.models import CircuitAST, GateType

class AzureTranslator:
    @staticmethod
    def generate(ast: CircuitAST) -> str:
        lines = [
            "// Q# code for Azure Quantum",
            "namespace QCC {",
            "    open Microsoft.Quantum.Intrinsic;",
            "    open Microsoft.Quantum.Measurement;",
            "",
            "    operation RunCircuit() : (Result[], Result[]) {",
            f"        use q = Qubit[{ast.num_qubits}];"
        ]

        # Need to map operations to Q# syntax
        for gate in ast.operations:
            indent = "        "
            if gate.type == GateType.H:
                lines.append(f"{indent}H(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.CX:
                lines.append(f"{indent}CNOT(q[{gate.qubits[0]}], q[{gate.qubits[1]}]);")
            elif gate.type == GateType.CZ:
                lines.append(f"{indent}CZ(q[{gate.qubits[0]}], q[{gate.qubits[1]}]);")
            elif gate.type == GateType.SWAP:
                lines.append(f"{indent}SWAP(q[{gate.qubits[0]}], q[{gate.qubits[1]}]);")
            elif gate.type == GateType.CCX:
                lines.append(f"{indent}CCNOT(q[{gate.qubits[0]}], q[{gate.qubits[1]}], q[{gate.qubits[2]}]);")
            elif gate.type == GateType.X:
                lines.append(f"{indent}X(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.Y:
                lines.append(f"{indent}Y(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.Z:
                lines.append(f"{indent}Z(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.S:
                lines.append(f"{indent}S(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.SDG:
                lines.append(f"{indent}Adjoint S(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.T:
                lines.append(f"{indent}T(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.TDG:
                lines.append(f"{indent}Adjoint T(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.SX:
                # Not standard, approximate with Rx(pi/2)
                lines.append(f"{indent}Rx(PI()/2.0, q[{gate.qubits[0]}]);")
            elif gate.type == GateType.I:
                # Identity, do nothing
                pass
            elif gate.type == GateType.RX:
                if gate.params:
                    lines.append(f"{indent}Rx({gate.params[0]}, q[{gate.qubits[0]}]);")
            elif gate.type == GateType.RY:
                if gate.params:
                    lines.append(f"{indent}Ry({gate.params[0]}, q[{gate.qubits[0]}]);")
            elif gate.type == GateType.RZ:
                if gate.params:
                    lines.append(f"{indent}Rz({gate.params[0]}, q[{gate.qubits[0]}]);")
            elif gate.type == GateType.PHASE:
                if gate.params:
                    lines.append(f"{indent}R1({gate.params[0]}, q[{gate.qubits[0]}]);")
            elif gate.type == GateType.MEASURE:
                q = gate.qubits[0]
                lines.append(f"{indent}let res{q} = M(q[{q}]);")
            elif gate.type == GateType.RESET:
                lines.append(f"{indent}Reset(q[{gate.qubits[0]}]);")
            elif gate.type == GateType.BARRIER:
                # No barrier in Q# standard
                pass

        # Return results if measurements exist
        has_measure = any(g.type == GateType.MEASURE for g in ast.operations)
        if has_measure:
            res_list = [f"res{i}" for i in range(ast.num_qubits) if any(g.type == GateType.MEASURE and g.qubits[0] == i for g in ast.operations)]
            if res_list:
                lines.append(f"        return ({', '.join(res_list)});")
        else:
            lines.append("        return ();")

        lines.append("    }")
        lines.append("}")

        return "\n".join(lines)
