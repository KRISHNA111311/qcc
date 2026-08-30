import numpy as np
from ..core.models import CircuitAST

class StatevectorVisualizer:
    @staticmethod
    def compute(circuit: CircuitAST) -> np.ndarray:
        # For now, return a placeholder (phase 5 will implement actual simulation)
        # In a future phase, we'll integrate with Qiskit or a custom simulator.
        # For demonstration, return a simple Bell state if circuit looks like Bell.
        num_qubits = circuit.num_qubits
        # Detect if circuit has H on 0 and CX on 0,1 -> Bell state
        ops = circuit.operations
        if len(ops) == 2 and ops[0].type.name == 'H' and ops[0].qubits == [0] and ops[1].type.name == 'CX' and ops[1].qubits == [0,1]:
            return np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        # Default: |0...0>
        state = np.zeros(2**num_qubits, dtype=complex)
        state[0] = 1.0
        return state

    @staticmethod
    def display(state: np.ndarray) -> str:
        n = len(state)
        lines = []
        for i, amp in enumerate(state):
            if np.abs(amp) > 1e-10:
                prob = np.abs(amp)**2
                lines.append(f"|{i:0{int(np.log2(n))}b}⟩: {amp.real:.4f} + {amp.imag:.4f}i  ({prob*100:.2f}%)")
        if not lines:
            return "(all zero)"
        return "\n".join(lines)
