import numpy as np
from ..core.models import CircuitAST, GateType
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

class StatevectorVisualizer:
    @staticmethod
    def compute(ast: CircuitAST) -> np.ndarray:
        num_qubits = ast.num_qubits
        if num_qubits == 0:
            max_q = -1
            for gate in ast.operations:
                if gate.qubits:
                    max_q = max(max_q, max(gate.qubits))
            if max_q >= 0:
                num_qubits = max_q + 1
            else:
                num_qubits = 1
        qc = QuantumCircuit(num_qubits)
        for gate in ast.operations:
            if gate.type == GateType.H:
                qc.h(gate.qubits[0])
            elif gate.type == GateType.CX:
                qc.cx(gate.qubits[0], gate.qubits[1])
            elif gate.type == GateType.CZ:
                qc.cz(gate.qubits[0], gate.qubits[1])
            elif gate.type == GateType.SWAP:
                qc.swap(gate.qubits[0], gate.qubits[1])
            elif gate.type == GateType.X:
                qc.x(gate.qubits[0])
            elif gate.type == GateType.Y:
                qc.y(gate.qubits[0])
            elif gate.type == GateType.Z:
                qc.z(gate.qubits[0])
            elif gate.type == GateType.U:
                if len(gate.params) >= 3:
                    qc.u(gate.params[0], gate.params[1], gate.params[2], gate.qubits[0])
            elif gate.type == GateType.RX:
                if gate.params:
                    qc.rx(gate.params[0], gate.qubits[0])
            elif gate.type == GateType.RY:
                if gate.params:
                    qc.ry(gate.params[0], gate.qubits[0])
            elif gate.type == GateType.RZ:
                if gate.params:
                    qc.rz(gate.params[0], gate.qubits[0])
            elif gate.type == GateType.PHASE:
                if gate.params:
                    qc.p(gate.params[0], gate.qubits[0])
            elif gate.type == GateType.MEASURE:
                # ignore for statevector
                pass
        simulator = AerSimulator()
        qc.save_statevector()
        result = simulator.run(qc).result()
        return result.get_statevector()

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
