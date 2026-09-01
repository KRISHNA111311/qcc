"""PennyLane execution backend for QCC circuits (Phase 0.2)."""
from typing import Any, Dict

from ...core.models import CircuitAST, GateType


def _apply_gate(gate) -> None:
    """Queue a single QCC Gate onto the current PennyLane tape."""
    import pennylane as qml

    t, q, p = gate.type, gate.qubits, gate.params
    if t == GateType.H:
        qml.Hadamard(wires=q[0])
    elif t == GateType.X:
        qml.PauliX(wires=q[0])
    elif t == GateType.Y:
        qml.PauliY(wires=q[0])
    elif t == GateType.Z:
        qml.PauliZ(wires=q[0])
    elif t == GateType.I:
        qml.Identity(wires=q[0])
    elif t == GateType.S:
        qml.S(wires=q[0])
    elif t == GateType.SDG:
        qml.adjoint(qml.S)(wires=q[0])
    elif t == GateType.T:
        qml.T(wires=q[0])
    elif t == GateType.TDG:
        qml.adjoint(qml.T)(wires=q[0])
    elif t == GateType.SX:
        qml.SX(wires=q[0])
    elif t == GateType.CX:
        qml.CNOT(wires=[q[0], q[1]])
    elif t == GateType.CZ:
        qml.CZ(wires=[q[0], q[1]])
    elif t == GateType.SWAP:
        qml.SWAP(wires=[q[0], q[1]])
    elif t == GateType.CCX:
        qml.Toffoli(wires=[q[0], q[1], q[2]])
    elif t == GateType.RX and p:
        qml.RX(p[0], wires=q[0])
    elif t == GateType.RY and p:
        qml.RY(p[0], wires=q[0])
    elif t == GateType.RZ and p:
        qml.RZ(p[0], wires=q[0])
    elif t == GateType.PHASE and p:
        qml.PhaseShift(p[0], wires=q[0])
    elif t in (GateType.RESET, GateType.BARRIER, GateType.MEASURE):
        pass  # no shot-based effect; QASM-D always appends a measure-all
    # unknown gate types are silently skipped, matching the translators


def run_pennylane(circuit: CircuitAST, shots: int) -> Dict[str, Any]:
    """Execute a CircuitAST on PennyLane's local default.qubit simulator.

    Returns a Qiskit-Aer-shaped result so the API layer can render
    counts/histograms identically regardless of backend:
        {"counts": {"00": 512, "11": 512}, "statevector": None}
    """
    import pennylane as qml

    num_qubits = max(circuit.num_qubits or 1, 1)
    shots = max(int(shots or 1), 1)
    dev = qml.device("default.qubit", wires=num_qubits)

    @qml.set_shots(shots=shots)
    @qml.qnode(dev)
    def circuit_fn():
        for gate in circuit.operations:
            _apply_gate(gate)
        return qml.counts()

    raw_counts = circuit_fn()
    counts = {str(state): int(count) for state, count in raw_counts.items()}
    return {"counts": counts, "statevector": None}