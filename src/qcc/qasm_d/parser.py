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
        'D': GateType.RZ,
        'E': GateType.U,
        'F': GateType.CZ,
    }

    @classmethod
    def parse(cls, s: str) -> CircuitAST:
        if not s:
            raise ParseError("Empty string")

        delim_pos = s.find('0')
        if delim_pos == -1:
            raise ParseError("Missing delimiter after qubit count")
        try:
            num_qubits = int(s[:delim_pos])
        except ValueError:
            raise ParseError("Invalid qubit count")
        s = s[delim_pos+1:]

        ast = CircuitAST(num_qubits=num_qubits)

        while s:
            next_delim = s.find('0')
            if next_delim == -1:
                token = s
                s = ''
            else:
                token = s[:next_delim]
                s = s[next_delim+1:]

            if not token:
                continue

            if token == '0':
                continue
            elif token == '00':
                for q in range(num_qubits):
                    ast.add_gate(Gate(type=GateType.MEASURE, qubits=[q], classical_bits=[q]))
                break
            else:
                gate_code = token[0]
                if gate_code not in cls._gate_map:
                    raise ParseError(f"Unknown gate code: {gate_code}")
                gate_type = cls._gate_map[gate_code]
                params_str = token[1:]
                params = []
                if params_str:
                    for ch in params_str:
                        if ch.isdigit():
                            params.append(int(ch))
                        else:
                            raise ParseError(f"Invalid parameter character: {ch}")
                # Convert 1-based indices to 0-based
                params = [p - 1 for p in params]

                if gate_type == GateType.H:
                    if len(params) != 1:
                        raise ParseError(f"H requires 1 qubit, got {len(params)}")
                    ast.add_gate(Gate(type=gate_type, qubits=params))
                elif gate_type in (GateType.CX, GateType.SWAP, GateType.CZ):
                    if len(params) != 2:
                        raise ParseError(f"{gate_type.value} requires 2 qubits, got {len(params)}")
                    ast.add_gate(Gate(type=gate_type, qubits=params))
                elif gate_type == GateType.U:
                    if len(params) != 3:
                        raise ParseError(f"U requires 3 parameters, got {len(params)}")
                    ast.add_gate(Gate(type=gate_type, qubits=[params[0]], params=[float(p) for p in params[1:]]))
                elif gate_type in (GateType.RX, GateType.RY, GateType.RZ, GateType.PHASE):
                    if len(params) < 2:
                        raise ParseError(f"{gate_type.value} requires at least 2 parameters (qubit and angle)")
                    ast.add_gate(Gate(type=gate_type, qubits=[params[0]], params=[float(params[1])]))
                else:
                    if len(params) != 1:
                        raise ParseError(f"{gate_type.value} requires 1 qubit, got {len(params)}")
                    ast.add_gate(Gate(type=gate_type, qubits=params))

        return ast
