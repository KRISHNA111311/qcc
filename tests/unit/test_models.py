from src.qcc.core.models import Gate, GateType, CircuitAST

class TestCircuitAST:
    def test_add_gate(self):
        ast = CircuitAST()
        gate = Gate(type=GateType.H, qubits=[0])
        ast.add_gate(gate)
        assert ast.get_gate_count() == 1
        assert ast.operations[0].type == GateType.H

    def test_gate_creation(self):
        gate = Gate(type=GateType.CX, qubits=[0, 1])
        assert gate.type == GateType.CX
        assert gate.qubits == [0, 1]
