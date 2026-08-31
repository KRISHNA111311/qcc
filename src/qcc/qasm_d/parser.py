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
        'G': GateType.CCX,
        'I': GateType.I,
        'J': GateType.S,
        'K': GateType.SDG,
        'L': GateType.T,
        'M': GateType.TDG,
        'N': GateType.SX,
    }

    @classmethod
    def parse(cls, s: str) -> CircuitAST:
        if not s:
            raise ParseError("Empty string")

        parts = s.split('#')
        if len(parts) < 2:
            raise ParseError("Invalid format: missing delimiter after qubit count")
        
        try:
            num_qubits = int(parts[0])
        except ValueError:
            raise ParseError("Invalid qubit count")
        
        ast = CircuitAST(num_qubits=num_qubits)
        tokens = parts[1:]

        for token in tokens:
            if token == '00':
                for q in range(num_qubits):
                    ast.add_gate(Gate(type=GateType.MEASURE, qubits=[q], classical_bits=[q]))
                break

            if not token:
                continue

            if len(token) < 1:
                continue

            gate_code = token[0]
            if gate_code not in cls._gate_map:
                raise ParseError(f"Unknown gate code: {gate_code}")
            gate_type = cls._gate_map[gate_code]
            params_str = token[1:]

            if gate_type in (GateType.RX, GateType.RY, GateType.RZ, GateType.PHASE):
                if len(params_str) < 5:
                    raise ParseError(f"{gate_type.value} requires qubit and 4-digit angle, got {params_str}")
                qubit = int(params_str[0]) - 1
                angle_str = params_str[1:5]
                try:
                    angle = float(angle_str) / 100.0
                except ValueError:
                    raise ParseError(f"Invalid angle format for {gate_type.value}: {angle_str}")
                if qubit < 0 or qubit >= num_qubits:
                    raise ParseError(f"Qubit index {qubit+1} out of range")
                ast.add_gate(Gate(type=gate_type, qubits=[qubit], params=[angle]))
                continue

            params = []
            for ch in params_str:
                if ch.isdigit():
                    params.append(int(ch))
                else:
                    raise ParseError(f"Invalid parameter character: {ch}")
            params = [p - 1 for p in params]

            if gate_type == GateType.H:
                if len(params) != 1:
                    raise ParseError(f"H requires 1 qubit, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            elif gate_type in (GateType.CX, GateType.CZ, GateType.SWAP):
                if len(params) != 2:
                    raise ParseError(f"{gate_type.value} requires 2 qubits, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            elif gate_type == GateType.CCX:
                if len(params) != 3:
                    raise ParseError("CCX requires 3 qubits (control1, control2, target)")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            elif gate_type == GateType.U:
                if len(params) < 4:
                    raise ParseError("U requires 4 parameters (qubit, theta, phi, lambda)")
                qubit = params[0]
                theta = float(params[1])
                phi = float(params[2])
                lam = float(params[3])
                ast.add_gate(Gate(type=gate_type, qubits=[qubit], params=[theta, phi, lam]))
            elif gate_type in (GateType.I, GateType.S, GateType.SDG, GateType.T, GateType.TDG, GateType.SX):
                if len(params) != 1:
                    raise ParseError(f"{gate_type.value} requires 1 qubit, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))
            elif gate_type == GateType.MEASURE:
                if len(params) < 1:
                    raise ParseError("MEASURE requires at least 1 qubit")
                qubit = params[0]
                classical = params[1] if len(params) > 1 else qubit
                ast.add_gate(Gate(type=gate_type, qubits=[qubit], classical_bits=[classical]))
            else:
                if len(params) != 1:
                    raise ParseError(f"{gate_type.value} requires 1 qubit, got {len(params)}")
                ast.add_gate(Gate(type=gate_type, qubits=params))

        if ast.num_qubits == 0:
            max_q = -1
            for op in ast.operations:
                if op.qubits:
                    max_q = max(max_q, max(op.qubits))
            if max_q >= 0:
                ast.num_qubits = max_q + 1

        return ast
