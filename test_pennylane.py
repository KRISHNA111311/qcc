from qcc.core.models import CircuitAST, Gate, GateType
from qcc.execution.backends.pennylane import run_pennylane

# Build a Bell state circuit
ast = CircuitAST(num_qubits=2)
ast.add_gate(Gate(type=GateType.H, qubits=[0]))
ast.add_gate(Gate(type=GateType.CX, qubits=[0,1]))

counts = run_pennylane(ast, shots=1024)
print("Counts:", counts)
