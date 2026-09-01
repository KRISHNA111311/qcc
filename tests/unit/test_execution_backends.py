"""Unit tests for the PennyLane and Cirq execution backends (Phase 0.2)."""
from qcc.core.models import CircuitAST, Gate, GateType
from qcc.execution.backends.pennylane import run_pennylane
from qcc.execution.backends.cirq import run_cirq


def _bell_circuit() -> CircuitAST:
    ast = CircuitAST(num_qubits=2)
    ast.add_gate(Gate(type=GateType.H, qubits=[0]))
    ast.add_gate(Gate(type=GateType.CX, qubits=[0, 1]))
    return ast


def _rotation_circuit() -> CircuitAST:
    ast = CircuitAST(num_qubits=1)
    ast.add_gate(Gate(type=GateType.X, qubits=[0]))
    ast.add_gate(Gate(type=GateType.RY, qubits=[0], params=[3.14159265358979]))
    return ast


class TestPennyLaneBackend:
    def test_bell_state_only_correlated_outcomes(self):
        result = run_pennylane(_bell_circuit(), shots=500)
        counts = result["counts"]
        assert set(counts.keys()) <= {"00", "11"}
        assert sum(counts.values()) == 500

    def test_shot_count_preserved_single_qubit(self):
        result = run_pennylane(_rotation_circuit(), shots=200)
        assert sum(result["counts"].values()) == 200


class TestCirqBackend:
    def test_bell_state_only_correlated_outcomes(self):
        result = run_cirq(_bell_circuit(), shots=500)
        counts = result["counts"]
        assert set(counts.keys()) <= {"00", "11"}
        assert sum(counts.values()) == 500

    def test_shot_count_preserved_single_qubit(self):
        result = run_cirq(_rotation_circuit(), shots=200)
        assert sum(result["counts"].values()) == 200