import re
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

        # Find first delimiter
        delim_pos = s.find('0')
        if delim_pos == -1:
            raise ParseError("Missing delimiter after qubit count")
        try:
            num_qubits = int(s[:delim_pos])
        except ValueError:
            raise ParseError("Invalid qubit count")
        s = s[delim_pos+1:]  # remove qubit count and delimiter

        ast = CircuitAST(num_qubits=num_qubits)

        # We'll parse the remaining string by scanning for tokens separated by '0'
        # But we need to detect '00' as a special token (measure all)
        i = 0
        while i < len(s):
            # Skip leading zeros (they are delimiters)
            zero_count = 0
            while i < len(s) and s[i] == '0':
                zero_count += 1
                i += 1
            if zero_count >= 2:
                # Two or more zeros: measure all and stop
                for q in range(num_qubits):
                    ast.add_gate(Gate(type=GateType.MEASURE, qubits=[q], classical_bits=[q]))
                # If there are more characters after, they would be ignored (spec says stop)
                break
            # Now we have a token (non-zero characters)
            token_start = i
            while i < len(s) and s[i] != '0':
                i += 1
            token = s[token_start:i]
            if not token:
                continue

            # Process the token
            gate_code = token[0]
            if gate_code not in cls._gate_map:
                raise ParseError(f"Unknown gate code: {gate_code}")
            gate_type = cls._gate_map[gate_code]
            params_str = token[1:]
            params = []
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
            elif gate_type in (GateType.CX, GateType.CZ, GateType.SWAP):
                if len(params) != 2:
                    raise ParseError(f"{gate_type.value} requires 2 qubits, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            elif gate_type == GateType.U:
                if len(params) < 4:
                    raise ParseError("U requires 4 parameters (qubit, theta, phi, lambda)")
                qubit = params[0]
                theta = float(params[1])
                phi = float(params[2])
                lam = float(params[3])
                ast.add_gate(Gate(type=gate_type, qubits=[qubit], params=[theta, phi, lam]))
            elif gate_type in (GateType.RX, GateType.RY, GateType.RZ, GateType.PHASE):
                if len(params) < 2:
                    raise ParseError(f"{gate_type.value} requires at least 2 parameters (qubit, angle)")
                qubit = params[0]
                angle = float(params[1])
                ast.add_gate(Gate(type=gate_type, qubits=[qubit], params=[angle]))
            elif gate_type == GateType.MEASURE:
                if len(params) < 1:
                    raise ParseError("MEASURE requires at least 1 qubit")
                qubit = params[0]
                classical = params[1] if len(params) > 1 else qubit
                ast.add_gate(Gate(type=gate_type, qubits=[qubit], classical_bits=[classical]))
            else:
                # Single-qubit gates (X, Y, Z, RESET, BARRIER)
                if len(params) != 1:
                    raise ParseError(f"{gate_type.value} requires 1 qubit, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))

        return ast
