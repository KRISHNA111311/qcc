import re

file_path = "src/qcc/api/circuit.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the parse_circuit function and replace it with the new version
new_func = '''@router.post("/parse")
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

        # Get statevector and qiskit counts (for visualizations)
        counts_qiskit, statevector = run_circuit(ast, request.shots)

        # Use requested backend for counts if not qiskit-aer
        if request.backend != "qiskit-aer":
            try:
                from ..execution.executor import execute_circuit_sync
                result = execute_circuit_sync(ast, request.shots, request.backend)
                counts = result['counts']
                # Convert numpy ints to Python ints if needed
                counts = {k: int(v) for k, v in counts.items()}
            except Exception as e:
                # Fallback to qiskit counts
                counts = counts_qiskit
                # Optionally log the error
        else:
            counts = counts_qiskit

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
        return {"success": False, "error": str(e), "traceback": tb}'''

# Replace the old function
pattern = r'@router\.post\("/parse"\)\s+async def parse_circuit\(.*?\):\s+.*?(?=@router\.post\("/execute"\)|$)'
# Use re.DOTALL to match across lines
new_content = re.sub(pattern, new_func, content, flags=re.DOTALL)
if new_content == content:
    print("Pattern not found. The function may have been modified.")
else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File updated successfully.")
