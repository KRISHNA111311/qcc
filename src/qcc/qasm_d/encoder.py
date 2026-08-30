from ..core.models import CircuitAST, GateType

class QASMDEncoder:
    _reverse_map = {
        GateType.H: '1',
        GateType.CX: '2',
        GateType.X: '3',
        GateType.Y: '4',
        GateType.Z: '5',
        GateType.PHASE: '6',
        GateType.SWAP: '7',
        GateType.RX: '8',
        GateType.RY: '9',
        GateType.MEASURE: 'A',
        GateType.RESET: 'B',
        GateType.BARRIER: 'C',
        GateType.RZ: 'D',
        GateType.U: 'E',
        GateType.CZ: 'F',
        GateType.CCX: 'G',
        GateType.I: 'I',
        GateType.S: 'J',
        GateType.SDG: 'K',
        GateType.T: 'L',
        GateType.TDG: 'M',
        GateType.SX: 'N',
    }

    @classmethod
    def encode(cls, ast: CircuitAST) -> str:
        parts = [str(ast.num_qubits)]

        for gate in ast.operations:
            if gate.type not in cls._reverse_map:
                continue
            code = cls._reverse_map[gate.type]
            # For gates with angles (RX, RY, RZ, PHASE): encode angle as 4-digit integer (scaled by 100)
            if gate.type in (GateType.RX, GateType.RY, GateType.RZ, GateType.PHASE):
                qubit = gate.qubits[0] + 1  # 0-based to 1-based
                angle = int(gate.params[0] * 100) if gate.params else 0
                angle_str = f"{angle:04d}"
                token = code + str(qubit) + angle_str
                parts.append(token)
            else:
                # For other gates, encode qubits and classical bits
                qubits_str = ''.join(str(q + 1) for q in gate.qubits)  # 1-based
                if gate.type == GateType.MEASURE and gate.classical_bits:
                    classical_str = ''.join(str(c + 1) for c in gate.classical_bits)
                    token = code + qubits_str + classical_str
                else:
                    token = code + qubits_str
                parts.append(token)

        parts.append('00')  # measure all
        return '#'.join(parts)
