import json
from pathlib import Path
from ..core.models import CircuitAST, Gate, GateType

class FileManager:
    @staticmethod
    def save_json(circuit: CircuitAST, path: str) -> None:
        data = {
            "num_qubits": circuit.num_qubits,
            "num_classical": circuit.num_classical,
            "operations": [
                {
                    "type": g.type.value,
                    "qubits": g.qubits,
                    "params": g.params,
                    "classical_bits": g.classical_bits
                }
                for g in circuit.operations
            ],
            "metadata": circuit.metadata
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_json(path: str) -> CircuitAST:
        with open(path, 'r') as f:
            data = json.load(f)

        ast = CircuitAST(
            num_qubits=data.get("num_qubits", 0),
            num_classical=data.get("num_classical", 0),
            metadata=data.get("metadata", {})
        )

        for op_data in data.get("operations", []):
            gate_type = None
            for g in GateType:
                if g.value == op_data["type"]:
                    gate_type = g
                    break
            if gate_type:
                gate = Gate(
                    type=gate_type,
                    qubits=op_data.get("qubits", []),
                    params=op_data.get("params", []),
                    classical_bits=op_data.get("classical_bits", [])
                )
                ast.add_gate(gate)

        return ast
