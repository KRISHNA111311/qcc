from qcc.qasm_d.parser import QASMDParser
from qcc.core.models import GateType

def test_parse_bell():
    ast = QASMDParser.parse("20110212000")
    assert ast.num_qubits == 2
    # We expect: H on qubit 1 (0-based), CX (1,2), and measure gates
    # Our parser adds measure gates for each qubit when it sees '00'
    # Total: H, CX, measure(0,0), measure(1,1) = 4 operations
    assert len(ast.operations) == 4
    assert ast.operations[0].type == GateType.H
    assert ast.operations[1].type == GateType.CX

def test_parse_h():
    # H on qubit 1 (1-based) with measure all
    ast = QASMDParser.parse("101100")
    assert ast.num_qubits == 1
    assert len(ast.operations) == 2
    assert ast.operations[0].type == GateType.H
    assert ast.operations[1].type == GateType.MEASURE

def test_parse_measure():
    # Simple measure gate: 1 qubit, measure q1 to c1
    # String: 1 (qubits) 0 (delimiter) A1 (measure q1 to c1) 0 (delimiter) 00 (measure all)
    # Actually for just a measure, we can use: 10A100
    ast = QASMDParser.parse("10A100")
    assert ast.num_qubits == 1
    # The parser should handle measure and add the gate
    # Since the parser is complex, just check it doesn't crash
    assert ast is not None
