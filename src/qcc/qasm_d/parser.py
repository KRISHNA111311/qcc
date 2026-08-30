from typing import List, Tuple
from ..core.models import CircuitAST, Gate, GateType
from ..core.exceptions import ParseError

class QASMDParser:
    _gate_map = {
        '1': GateType.H,
        '2': GateType.CX,
        '3': GateType.X,
        '4': GateType.Y,
        '5': GateType.Z,
        '6': GateType.PHASE,
        '7': GateType.SWAP,
        '8': GateType.RX,
        '9': GateType.RY,
        'A': GateType.MEASURE,
        'B': GateType.RESET,
        'C': GateType.BARRIER,
    }

    @classmethod
    def parse(cls, s: str) -> CircuitAST:
        if not s:
            raise ParseError("Empty string")

        tokens = []
        i = 0
        # First token is qubit count
        while i < len(s) and s[i] != '0':
            tokens.append(s[i])
            i += 1
        if i >= len(s):
            raise ParseError("Missing delimiter after qubit count")
        i += 1  # skip '0'

        try:
            num_qubits = int(''.join(tokens))
        except ValueError:
            raise ParseError("Invalid qubit count")

        ast = CircuitAST(num_qubits=num_qubits)

        # Parse operations
        while i < len(s):
            if s[i] == '0':
                # End of circuit or measure all
                if i + 1 < len(s) and s[i+1] == '0':
                    # '00' = measure all
                    for q in range(num_qubits):
                        gate = Gate(type=GateType.MEASURE, qubits=[q], classical_bits=[q])
                        ast.add_gate(gate)
                    i += 2
                    continue
                else:
                    # single '0' – separator, skip
                    i += 1
                    continue

            # Read operation token (could be multiple digits like '10' for H on qubit 0)
            op_start = i
            while i < len(s) and s[i] != '0':
                i += 1
            op_str = s[op_start:i]

            if not op_str:
                continue

            # First char is gate type, rest are parameters (qubit indices)
            gate_code = op_str[0]
            if gate_code not in cls._gate_map:
                raise ParseError(f"Unknown gate code: {gate_code}")
            gate_type = cls._gate_map[gate_code]

            # Parse parameters
            params = []
            for ch in op_str[1:]:
                if ch.isdigit():
                    params.append(int(ch))
                else:
                    raise ParseError(f"Invalid parameter character: {ch}")

            if gate_type == GateType.H:
                if len(params) != 1:
                    raise ParseError(f"H requires 1 qubit, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            elif gate_type in (GateType.CX, GateType.SWAP):
                if len(params) != 2:
                    raise ParseError(f"{gate_type.value} requires 2 qubits, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            else:
                # Single-qubit gates
                if len(params) != 1:
                    raise ParseError(f"{gate_type.value} requires 1 qubit, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))

        return ast
