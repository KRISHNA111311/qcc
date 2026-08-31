import sys
import os
import traceback
import logging
import base64
import io
import matplotlib.pyplot as plt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Qiskit imports
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector, plot_state_qsphere

# QCC imports (relative to this file)
from ..qasm_d.parser import QASMDParser
from ..translators.qiskit import QiskitTranslator
from ..translators.qasm3 import QASM3Translator
from ..translators.cirq import CirqTranslator
from ..translators.pennylane import PennyLaneTranslator
from ..translators.braket import BraketTranslator
from ..translators.pytket import PyTketTranslator
from ..translators.stim import StimTranslator
# Optional SDKs (may fail if not installed, but we keep them)
try:
    from ..translators.cudaq import CUDAQTranslator
except ImportError:
    CUDAQTranslator = None
try:
    from ..translators.azure import AzureTranslator
except ImportError:
    AzureTranslator = None
try:
    from ..translators.tensorcircuit import TensorCircuitTranslator
except ImportError:
    TensorCircuitTranslator = None
try:
    from ..translators.myqlm import MyQLMTranslator
except ImportError:
    MyQLMTranslator = None

router = APIRouter(prefix="/api", tags=["circuit"])

class ParseRequest(BaseModel):
    qasm_d: str
    shots: int = 1024
    backend: str = "qiskit-aer"

# ---------- Helper Functions (from old api.py) ----------
def run_circuit(ast, shots):
    num_qubits = ast.num_qubits or 1
    num_classical = ast.num_classical or 0
    qc = QuantumCircuit(num_qubits, num_classical)

    for gate in ast.operations:
        if gate.type.name == 'H':
            qc.h(gate.qubits[0])
        elif gate.type.name == 'CX':
            qc.cx(gate.qubits[0], gate.qubits[1])
        elif gate.type.name == 'CZ':
            qc.cz(gate.qubits[0], gate.qubits[1])
        elif gate.type.name == 'SWAP':
            qc.swap(gate.qubits[0], gate.qubits[1])
        elif gate.type.name == 'CCX':
            qc.ccx(gate.qubits[0], gate.qubits[1], gate.qubits[2])
        elif gate.type.name == 'X':
            qc.x(gate.qubits[0])
        elif gate.type.name == 'Y':
            qc.y(gate.qubits[0])
        elif gate.type.name == 'Z':
            qc.z(gate.qubits[0])
        elif gate.type.name == 'S':
            qc.s(gate.qubits[0])
        elif gate.type.name == 'SDG':
            qc.sdg(gate.qubits[0])
        elif gate.type.name == 'T':
            qc.t(gate.qubits[0])
        elif gate.type.name == 'TDG':
            qc.tdg(gate.qubits[0])
        elif gate.type.name == 'SX':
            qc.sx(gate.qubits[0])
        elif gate.type.name == 'I':
            qc.i(gate.qubits[0])
        elif gate.type.name == 'RX' and gate.params:
            qc.rx(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'RY' and gate.params:
            qc.ry(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'RZ' and gate.params:
            qc.rz(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'PHASE' and gate.params:
            qc.p(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'MEASURE':
            q = gate.qubits[0]
            c = gate.classical_bits[0] if gate.classical_bits else q
            qc.measure(q, c)

    if not any(g.type.name == 'MEASURE' for g in ast.operations):
        qc.measure_all()

    simulator = AerSimulator()
    transpiled = transpile(qc, simulator)
    result = simulator.run(transpiled, shots=shots).result()
    counts = result.get_counts()

    # Statevector (without measurements)
    qc_sv = QuantumCircuit(num_qubits)
    for gate in ast.operations:
        if gate.type.name == 'MEASURE':
            continue
        if gate.type.name == 'H':
            qc_sv.h(gate.qubits[0])
        elif gate.type.name == 'CX':
            qc_sv.cx(gate.qubits[0], gate.qubits[1])
        elif gate.type.name == 'CZ':
            qc_sv.cz(gate.qubits[0], gate.qubits[1])
        elif gate.type.name == 'SWAP':
            qc_sv.swap(gate.qubits[0], gate.qubits[1])
        elif gate.type.name == 'CCX':
            qc_sv.ccx(gate.qubits[0], gate.qubits[1], gate.qubits[2])
        elif gate.type.name == 'X':
            qc_sv.x(gate.qubits[0])
        elif gate.type.name == 'Y':
            qc_sv.y(gate.qubits[0])
        elif gate.type.name == 'Z':
            qc_sv.z(gate.qubits[0])
        elif gate.type.name == 'S':
            qc_sv.s(gate.qubits[0])
        elif gate.type.name == 'SDG':
            qc_sv.sdg(gate.qubits[0])
        elif gate.type.name == 'T':
            qc_sv.t(gate.qubits[0])
        elif gate.type.name == 'TDG':
            qc_sv.tdg(gate.qubits[0])
        elif gate.type.name == 'SX':
            qc_sv.sx(gate.qubits[0])
        elif gate.type.name == 'I':
            qc_sv.i(gate.qubits[0])
        elif gate.type.name == 'RX' and gate.params:
            qc_sv.rx(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'RY' and gate.params:
            qc_sv.ry(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'RZ' and gate.params:
            qc_sv.rz(gate.params[0], gate.qubits[0])
        elif gate.type.name == 'PHASE' and gate.params:
            qc_sv.p(gate.params[0], gate.qubits[0])
    qc_sv.save_statevector()
    sv_result = simulator.run(qc_sv).result()
    statevector = sv_result.get_statevector()

    return counts, statevector

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_histogram(counts):
    fig = plot_histogram(counts)
    return fig_to_base64(fig)

def generate_bloch_multivector(statevector):
    fig = plot_bloch_multivector(statevector)
    return fig_to_base64(fig)

def generate_qsphere(statevector):
    fig = plot_state_qsphere(statevector, show_state_labels=True, show_state_phases=True)
    return fig_to_base64(fig)

def format_statevector(statevector):
    import numpy as np
    n = len(statevector)
    result = []
    for i, amp in enumerate(statevector):
        if np.abs(amp) > 1e-10:
            prob = np.abs(amp)**2
            result.append({
                "state": format(i, f'0{int(np.log2(n))}b'),
                "amplitude": f"{amp.real:.4f}+{amp.imag:.4f}i",
                "probability": prob
            })
    return result

def calculate_depth(ast):
    depth = 0
    last_positions = {}
    for gate in ast.operations:
        for q in gate.qubits:
            if q in last_positions:
                depth = max(depth, last_positions[q] + 1)
            last_positions[q] = depth
        depth += 1
    return depth

# ---------- Endpoint ----------
@router.post("/parse")
async def parse_circuit(request: ParseRequest):
    try:
        ast = QASMDParser.parse(request.qasm_d)
        # Ensure num_qubits and num_classical are set
        if ast.num_qubits == 0:
            max_q = -1
            for op in ast.operations:
                if op.qubits:
                    max_q = max(max_q, max(op.qubits))
            if max_q >= 0:
                ast.num_qubits = max_q + 1
        if ast.num_classical == 0:
            max_c = -1
            for op in ast.operations:
                if op.type.name == 'MEASURE' and op.classical_bits:
                    max_c = max(max_c, max(op.classical_bits))
            if max_c >= 0:
                ast.num_classical = max_c + 1

        counts, statevector = run_circuit(ast, request.shots)

        # Code generation for all SDKs (including optional ones)
        code = {
            "qiskit": QiskitTranslator.generate(ast),
            "qasm3": QASM3Translator.generate(ast),
            "cirq": CirqTranslator.generate(ast),
            "pennylane": PennyLaneTranslator.generate(ast),
            "braket": BraketTranslator.generate(ast),
            "pytket": PyTketTranslator.generate(ast),
            "stim": StimTranslator.generate(ast),
        }
        # Add optional SDKs if available
        if CUDAQTranslator:
            code["cudaq"] = CUDAQTranslator.generate(ast)
        if AzureTranslator:
            code["azure"] = AzureTranslator.generate(ast)
        if TensorCircuitTranslator:
            code["tensorcircuit"] = TensorCircuitTranslator.generate(ast)
        if MyQLMTranslator:
            code["myqlm"] = MyQLMTranslator.generate(ast)

        hist_img = generate_histogram(counts)
        bloch_img = generate_bloch_multivector(statevector)
        qsphere_img = generate_qsphere(statevector)

        response = {
            "success": True,
            "data": {
                "metadata": {
                    "num_qubits": ast.num_qubits,
                    "num_classical": ast.num_classical,
                    "depth": calculate_depth(ast),
                    "operations": [
                        {"type": g.type.value, "qubits": g.qubits, "params": g.params}
                        for g in ast.operations
                    ]
                },
                "results": {
                    "counts": counts,
                    "statevector": format_statevector(statevector)
                },
                "visualizations": {
                    "histogram": hist_img,
                    "bloch": bloch_img,
                    "qsphere": qsphere_img,
                },
                "code": code,
            }
        }
        return response
    except Exception as e:
        tb = traceback.format_exc()
        return {"success": False, "error": str(e), "traceback": tb}

@router.post("/execute")
async def execute_circuit(request: ParseRequest):
    # Alias for backward compatibility
    return await parse_circuit(request)

@router.get("/health")
async def health():
    return {"status": "ok"}