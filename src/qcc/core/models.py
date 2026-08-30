from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import copy

class GateType(Enum):
    H = "H"; X = "X"; Y = "Y"; Z = "Z"
    CX = "CX"; CZ = "CZ"; SWAP = "SWAP"
    U = "U"; PHASE = "P"; RX = "RX"; RY = "RY"; RZ = "RZ"
    MEASURE = "measure"; RESET = "reset"; BARRIER = "barrier"

@dataclass
class Gate:
    type: GateType
    qubits: List[int]
    params: List[float] = field(default_factory=list)
    classical_bits: List[int] = field(default_factory=list)
    label: Optional[str] = None

@dataclass
class CircuitAST:
    num_qubits: int = 0
    num_classical: int = 0
    operations: List[Gate] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_gate(self, gate: Gate) -> None:
        self.operations.append(gate)

    def get_gate_count(self) -> int:
        return len(self.operations)

    def __deepcopy__(self, memo):
        new_ast = CircuitAST(
            num_qubits=self.num_qubits,
            num_classical=self.num_classical,
            operations=copy.deepcopy(self.operations, memo),
            metadata=copy.deepcopy(self.metadata, memo)
        )
        return new_ast

@dataclass
class ViewSettings:
    theme: str = "default"
    alignment: str = "left"
    show_phase_disks: bool = False
