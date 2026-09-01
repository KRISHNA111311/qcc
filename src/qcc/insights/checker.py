from typing import List, Dict, Any
import numpy as np
from ..core.models import CircuitAST, GateType

def check_measurement_before_gates(ast: CircuitAST) -> List[Dict[str, Any]]:
    """Detect gates after a measurement (measurement should be at the end)."""
    errors = []
    seen_measure = False
    for gate in ast.operations:
        if gate.type == GateType.MEASURE:
            seen_measure = True
        elif seen_measure:
            errors.append({
                "type": "measurement_then_gate",
                "message": f"Gate '{gate.type.value}' appears after a measurement; it will have no effect.",
                "gate": gate.type.value,
                "qubits": gate.qubits
            })
    return errors

def check_missing_entanglement(ast: CircuitAST) -> List[Dict[str, Any]]:
    """Warn if multi‑qubit circuit has no multi‑qubit gates."""
    if ast.num_qubits < 2:
        return []
    has_multi = any(len(g.qubits) > 1 for g in ast.operations)
    if not has_multi:
        return [{
            "type": "missing_entanglement",
            "message": "Circuit has 2+ qubits but no entangling gates (CX, CZ, SWAP, CCX). Consider adding entanglement."
        }]
    return []

def check_qubit_indices(ast: CircuitAST) -> List[Dict[str, Any]]:
    """Ensure all qubit indices are within valid range."""
    errors = []
    for gate in ast.operations:
        for q in gate.qubits:
            if q < 0 or q >= ast.num_qubits:
                errors.append({
                    "type": "qubit_index_error",
                    "message": f"Qubit index {q} out of range (0..{ast.num_qubits-1})",
                    "gate": gate.type.value,
                    "qubits": gate.qubits
                })
    return errors

def check_missing_measurement(ast: CircuitAST) -> List[Dict[str, Any]]:
    """Warn if no measurement gates exist."""
    has_measure = any(g.type == GateType.MEASURE for g in ast.operations)
    if not has_measure:
        return [{
            "type": "missing_measurement",
            "message": "No measurement gates found. Execution will auto‑measure all qubits."
        }]
    return []

def check_unbalanced_state(statevector: np.ndarray) -> List[Dict[str, Any]]:
    """Check if statevector is normalized (within tolerance)."""
    norm = np.linalg.norm(statevector)
    if abs(norm - 1.0) > 1e-10:
        return [{
            "type": "invalid_state",
            "message": f"Statevector not normalized (norm={norm:.6f})."
        }]
    return []

def get_circuit_errors(ast: CircuitAST, statevector: np.ndarray = None) -> List[Dict[str, Any]]:
    """Aggregate all error checks."""
    errors = []
    errors.extend(check_measurement_before_gates(ast))
    errors.extend(check_missing_entanglement(ast))
    errors.extend(check_qubit_indices(ast))
    errors.extend(check_missing_measurement(ast))
    if statevector is not None:
        errors.extend(check_unbalanced_state(statevector))
    return errors
