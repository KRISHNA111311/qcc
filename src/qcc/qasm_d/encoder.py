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
    }

    @classmethod
    def encode(cls, ast: CircuitAST) -> str:
        parts = [str(ast.num_qubits), '0']

        for gate in ast.operations:
            if gate.type not in cls._reverse_map:
                # Skip unknown gates
                continue
            code = cls._reverse_map[gate.type]
            qubits_str = ''.join(str(q) for q in gate.qubits)
            if gate.type == GateType.MEASURE:
                # For measure, we use code + qubit + classical bit
                if gate.classical_bits:
                    qubits_str += str(gate.classical_bits[0])
            parts.append(code + qubits_str)
            parts.append('0')

        # End with '00' to indicate measurement and run
        parts.append('00')
        return ''.join(parts)
