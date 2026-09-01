"""Cirq execution backend for QCC circuits (Phase 0.2)."""
from typing import Any, Dict

from ...core.models import CircuitAST, GateType


def run_cirq(circuit: CircuitAST, shots: int) -> Dict[str, Any]:
    """Execute a CircuitAST on Cirq's built-in state-vector simulator.

    Returns a Qiskit-Aer-shaped result:
        {"counts": {"00": 512, "11": 512}, "statevector": None}
    """
    import cirq

    num_qubits = max(circuit.num_qubits or 1, 1)
    shots = max(int(shots or 1), 1)
    qubits = cirq.LineQubit.range(num_qubits)
    c = cirq.Circuit()

    for gate in circuit.operations:
        t, q, p = gate.type, gate.qubits, gate.params
        if t == GateType.MEASURE:
            continue  # a single terminal measurement is appended below
        elif t == GateType.H:
            c.append(cirq.H(qubits[q[0]]))
        elif t == GateType.X:
            c.append(cirq.X(qubits[q[0]]))
        elif t == GateType.Y:
            c.append(cirq.Y(qubits[q[0]]))
        elif t == GateType.Z:
            c.append(cirq.Z(qubits[q[0]]))
        elif t == GateType.I:
            c.append(cirq.I(qubits[q[0]]))
        elif t == GateType.S:
            c.append(cirq.S(qubits[q[0]]))
        elif t == GateType.SDG:
            c.append((cirq.S**-1)(qubits[q[0]]))
        elif t == GateType.T:
            c.append(cirq.T(qubits[q[0]]))
        elif t == GateType.TDG:
            c.append((cirq.T**-1)(qubits[q[0]]))
        elif t == GateType.SX:
            c.append((cirq.X**0.5)(qubits[q[0]]))
        elif t == GateType.CX:
            c.append(cirq.CNOT(qubits[q[0]], qubits[q[1]]))
        elif t == GateType.CZ:
            c.append(cirq.CZ(qubits[q[0]], qubits[q[1]]))
        elif t == GateType.SWAP:
            c.append(cirq.SWAP(qubits[q[0]], qubits[q[1]]))
        elif t == GateType.CCX:
            c.append(cirq.CCNOT(qubits[q[0]], qubits[q[1]], qubits[q[2]]))
        elif t == GateType.RX and p:
            c.append(cirq.rx(p[0])(qubits[q[0]]))
        elif t == GateType.RY and p:
            c.append(cirq.ry(p[0])(qubits[q[0]]))
        elif t == GateType.RZ and p:
            c.append(cirq.rz(p[0])(qubits[q[0]]))
        elif t == GateType.PHASE and p:
            # cirq has no bare "phase" gate matching Qiskit's p(lambda);
            # rz(lambda) differs only by an unobservable global phase, so
            # measurement statistics (all this backend reports) match.
            c.append(cirq.rz(p[0])(qubits[q[0]]))
        elif t == GateType.RESET:
            c.append(cirq.reset(qubits[q[0]]))
        elif t == GateType.BARRIER:
            pass

    c.append(cirq.measure(*qubits, key="result"))
    simulator = cirq.Simulator()
    result = simulator.run(c, repetitions=shots)
    raw_hist = result.histogram(key="result")

    counts: Dict[str, int] = {}
    for value, count in raw_hist.items():
        bitstring = format(value, f"0{num_qubits}b")
        counts[bitstring] = counts.get(bitstring, 0) + int(count)
    return {"counts": counts, "statevector": None}