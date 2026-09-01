from qcc.core.models import CircuitAST, Gate, GateType
from qcc.execution.executor import execute_circuit_sync

def bell():
    ast = CircuitAST(num_qubits=2)
    ast.add_gate(Gate(type=GateType.H, qubits=[0]))
    ast.add_gate(Gate(type=GateType.CX, qubits=[0, 1]))
    return ast

for backend in ["pennylane", "cirq"]:
    print(f"--- {backend} ---")
    result = execute_circuit_sync(bell(), shots=512, backend=backend)
    print("counts:", result["counts"])
    print("statevector:", result["statevector"])
