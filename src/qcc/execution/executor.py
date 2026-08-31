import asyncio
from typing import Dict, Any
from ..core.models import CircuitAST
from ..qasm_d.parser import QASMDParser
from ..execution.backends.qiskit_aer import run_qiskit_aer
from ..execution.backends.pennylane import run_pennylane
from ..execution.backends.cirq import run_cirq

async def execute_circuit_async(circuit: CircuitAST, shots: int = 1024, backend: str = "qiskit-aer") -> Dict[str, Any]:
    loop = asyncio.get_running_loop()
    if backend == "qiskit-aer":
        result = await loop.run_in_executor(None, run_qiskit_aer, circuit, shots)
    elif backend == "pennylane":
        result = await loop.run_in_executor(None, run_pennylane, circuit, shots)
    elif backend == "cirq":
        result = await loop.run_in_executor(None, run_cirq, circuit, shots)
    else:
        raise ValueError(f"Unsupported backend: {backend}")
    return result

# Sync wrapper for CLI
def execute_circuit_sync(circuit: CircuitAST, shots: int = 1024, backend: str = "qiskit-aer") -> Dict[str, Any]:
    return asyncio.run(execute_circuit_async(circuit, shots, backend))
