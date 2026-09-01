import sys
import os
import traceback
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import json
import base64
import io
import matplotlib.pyplot as plt

# Qiskit imports for visualization
from qiskit.visualization import plot_histogram, plot_bloch_multivector, plot_state_qsphere

# Import QCC core
from qcc.qasm_d.parser import QASMDParser
from qcc.translators.qiskit import QiskitTranslator
from qcc.translators.qasm3 import QASM3Translator
from qcc.translators.cirq import CirqTranslator
from qcc.translators.pennylane import PennyLaneTranslator
from qcc.translators.braket import BraketTranslator
from qcc.translators.pytket import PyTketTranslator
from qcc.translators.stim import StimTranslator
from qcc.translators.cudaq import CUDAQTranslator
from qcc.translators.azure import AzureTranslator
from qcc.translators.tensorcircuit import TensorCircuitTranslator
from qcc.translators.myqlm import MyQLMTranslator

# Import auth and database
from qcc.api.auth import router as auth_router
from qcc.db.session import engine
from qcc.db.models import Base

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="QCC - Quantum Circuit Composer API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

class ParseRequest(BaseModel):
    qasm_d: str
    shots: int = 1024
    backend: str = "qiskit-aer"

# ============ Helper Functions ============

def run_circuit(ast, shots):
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    
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
    """Convert matplotlib figure to base64 PNG."""
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

@app.post("/api/parse")
async def parse_circuit(request: ParseRequest):
    try:
        logger.info(f"Received QASM-D: {request.qasm_d}")
        logger.info(f"Shots: {request.shots}")
        
        ast = QASMDParser.parse(request.qasm_d)
        logger.debug(f"AST parsed: num_qubits={ast.num_qubits}, ops={len(ast.operations)}")
        
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
        
        logger.debug(f"After ensure: num_qubits={ast.num_qubits}, num_classical={ast.num_classical}")
        
        counts, statevector = run_circuit(ast, request.shots)
        
        # Code generation for all SDKs
        code = {
            "qiskit": QiskitTranslator.generate(ast),
            "qasm3": QASM3Translator.generate(ast),
            "cirq": CirqTranslator.generate(ast),
            "pennylane": PennyLaneTranslator.generate(ast),
            "braket": BraketTranslator.generate(ast),
            "pytket": PyTketTranslator.generate(ast),
            "stim": StimTranslator.generate(ast),
            "cudaq": CUDAQTranslator.generate(ast),
            "azure": AzureTranslator.generate(ast),
            "tensorcircuit": TensorCircuitTranslator.generate(ast),
            "myqlm": MyQLMTranslator.generate(ast),
        }
        
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
        return JSONResponse(response)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error: {e}\n{tb}")
        return JSONResponse({"success": False, "error": str(e), "traceback": tb}, status_code=400)

@app.get("/")
async def root():
    html_content = """
    <h1>QCC API</h1>
    <p>Use POST /api/parse with JSON {"qasm_d": "your_qasm_d_string"}</p>
    <p>Example: {"qasm_d": "2#11#212#00"}</p>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
