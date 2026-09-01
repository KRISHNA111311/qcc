from qcc.core.models import CircuitAST, Gate, GateType
from qcc.execution.executor import execute_circuit_sync

ast = CircuitAST(num_qubits=2)
ast.add_gate(Gate(type=GateType.H, qubits=[0]))
ast.add_gate(Gate(type=GateType.CX, qubits=[0,1]))

result = execute_circuit_sync(ast, shots=1024, backend="pennylane")
print(result)
