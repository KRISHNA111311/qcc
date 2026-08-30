from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
import os
from ..core.session import SessionState
from ..core.models import Gate, GateType, CircuitAST

class QCCRepl:
    def __init__(self):
        self.session = SessionState()
        self.commands = {
            "new": self.cmd_new,
            "add": self.cmd_add,
            "list": self.cmd_list,
            "undo": self.cmd_undo,
            "redo": self.cmd_redo,
            "draw": self.cmd_draw,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "import-d": self.cmd_import_d,
            "export-d": self.cmd_export_d,
            "qiskit": self.cmd_qiskit,
            "qasm": self.cmd_qasm,
            "statevector": self.cmd_statevector,
            "probs": self.cmd_probs,
            "bloch": self.cmd_bloch,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "help": self.cmd_help,
        }
        self.completer = WordCompleter(list(self.commands.keys()), ignore_case=True)

    def run(self):
        session = PromptSession(
            history=FileHistory(os.path.expanduser("~/.qcc_history")),
            auto_suggest=AutoSuggestFromHistory(),
        )
        print("Quantum Circuit Composer v0.1.0 (Phase 5)")
        print("Type 'help' for commands. Type 'exit' to quit.")

        while True:
            try:
                user_input = session.prompt("qcc> ", completer=self.completer)
                if not user_input.strip():
                    continue
                parts = user_input.strip().split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"Unknown command: {cmd}. Type 'help' for list.")
            except KeyboardInterrupt:
                print("\nType 'exit' to quit.")
            except EOFError:
                print("\nGoodbye!")
                break

    # ----- Command Handlers -----

    def cmd_new(self, args):
        self.session.circuit = CircuitAST()
        self.session.commit()
        print("✅ New blank circuit created.")

    def cmd_add(self, args):
        if len(args) < 2:
            print("Usage: add <gate> <q0> [q1] [param...]")
            return
        gate_name = args[0].upper()
        try:
            qubits = [int(q) for q in args[1:] if q.replace('-', '').isdigit()]
        except ValueError:
            print("Invalid qubit indices. Use numbers.")
            return

        gate_type = None
        for g in GateType:
            if g.value == gate_name:
                gate_type = g
                break
        if gate_type is None:
            print(f"Unknown gate: {gate_name}. Available: {[g.value for g in GateType]}")
            return

        gate = Gate(type=gate_type, qubits=qubits)
        self.session.circuit.add_gate(gate)

        # Update num_qubits based on the highest qubit index
        if qubits:
            max_q = max(qubits)
            if self.session.circuit.num_qubits <= max_q:
                self.session.circuit.num_qubits = max_q + 1

        # Update num_classical if measure gate
        if gate_type == GateType.MEASURE and gate.classical_bits:
            max_c = max(gate.classical_bits)
            if self.session.circuit.num_classical <= max_c:
                self.session.circuit.num_classical = max_c + 1

        self.session.commit()
        print(f"✅ Added {gate_name} on qubits {qubits}.")

    def cmd_list(self, args):
        ops = self.session.circuit.operations
        if not ops:
            print("(empty circuit)")
            return
        for i, op in enumerate(ops):
            print(f"{i}: {op.type.value} {op.qubits} {op.params}")

    def cmd_undo(self, args):
        try:
            self.session.undo()
            print("✅ Undo successful.")
        except Exception as e:
            print(f"❌ {e}")

    def cmd_redo(self, args):
        try:
            self.session.redo()
            print("✅ Redo successful.")
        except Exception as e:
            print(f"❌ {e}")

    def cmd_draw(self, args):
        from ..visualizers.ascii_circuit import AsciiCircuit
        print(AsciiCircuit.draw(self.session.circuit))

    def cmd_save(self, args):
        if len(args) < 1:
            print("Usage: save <filename.json>")
            return
        from ..persistence.file_manager import FileManager
        FileManager.save_json(self.session.circuit, args[0])
        print(f"✅ Circuit saved to {args[0]}")

    def cmd_load(self, args):
        if len(args) < 1:
            print("Usage: load <filename.json>")
            return
        from ..persistence.file_manager import FileManager
        self.session.circuit = FileManager.load_json(args[0])
        self.session.commit()
        print(f"✅ Circuit loaded from {args[0]}")

    def cmd_import_d(self, args):
        if len(args) < 1:
            print("Usage: import-d <qasm_d_string>")
            return
        from ..qasm_d.parser import QASMDParser
        try:
            self.session.circuit = QASMDParser.parse(args[0])
            self.session.commit()
            print("✅ Circuit imported from QASM-D")
        except Exception as e:
            print(f"❌ {e}")

    def cmd_export_d(self, args):
        from ..qasm_d.encoder import QASMDEncoder
        try:
            s = QASMDEncoder.encode(self.session.circuit)
            print(f"QASM-D: {s}")
        except Exception as e:
            print(f"❌ {e}")

    def cmd_qiskit(self, args):
        from ..translators.qiskit import QiskitTranslator
        try:
            code = QiskitTranslator.generate(self.session.circuit)
            print(code)
        except Exception as e:
            print(f"❌ {e}")

    def cmd_qasm(self, args):
        from ..translators.qasm3 import QASM3Translator
        try:
            code = QASM3Translator.generate(self.session.circuit)
            print(code)
        except Exception as e:
            print(f"❌ {e}")

    def cmd_statevector(self, args):
        from ..visualizers.statevector import StatevectorVisualizer
        try:
            state = StatevectorVisualizer.compute(self.session.circuit)
            print(StatevectorVisualizer.display(state))
        except Exception as e:
            print(f"❌ {e}")

    def cmd_probs(self, args):
        from ..visualizers.probabilities import ProbabilitiesVisualizer
        try:
            probs = ProbabilitiesVisualizer.compute(self.session.circuit)
            print(ProbabilitiesVisualizer.display(probs))
        except Exception as e:
            print(f"❌ {e}")

    def cmd_bloch(self, args):
        from ..visualizers.bloch import BlochVisualizer
        try:
            # Ensure num_qubits is set from the circuit
            if self.session.circuit.num_qubits == 0:
                max_q = -1
                for op in self.session.circuit.operations:
                    if op.qubits:
                        max_q = max(max_q, max(op.qubits))
                if max_q >= 0:
                    self.session.circuit.num_qubits = max_q + 1
                else:
                    self.session.circuit.num_qubits = 1
            # Compute statevector using BlochVisualizer
            state = BlochVisualizer.compute_statevector(self.session.circuit)
            vectors = BlochVisualizer.compute_bloch_vectors(state)
            filename = args[0] if args else "bloch.png"
            BlochVisualizer.plot(vectors, save_path=filename)
        except Exception as e:
            print(f"❌ {e}")

    def cmd_exit(self, args):
        print("Goodbye!")
        raise EOFError

    def cmd_help(self, args):
        help_text = """
Available commands:
  new               – Create a new blank circuit
  add <gate> <q>   – Add a gate (e.g., add H 0, add CX 0 1)
  list              – Show all gates
  undo              – Undo the last action
  redo              – Redo the last undone action
  draw              – Draw circuit in ASCII
  save <file.json>  – Save circuit to JSON file
  load <file.json>  – Load circuit from JSON file
  import-d <str>    – Import circuit from QASM-D string
  export-d          – Export circuit as QASM-D string
  qiskit            – Generate Qiskit Python code
  qasm              – Generate OpenQASM 3.0 code
  statevector       – Display the statevector
  probs             – Display probability distribution (ASCII bar chart)
  bloch [filename]  – Generate Bloch sphere (saves to filename or bloch.png)
  exit / quit       – Exit the REPL
  help              – Show this help
"""
        print(help_text)
