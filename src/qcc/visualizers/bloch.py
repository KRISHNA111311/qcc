import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import partial_trace

class BlochVisualizer:
    @staticmethod
    def compute_statevector(ast):
        num_qubits = ast.num_qubits
        if num_qubits == 0:
            max_q = -1
            for gate in ast.operations:
                if gate.qubits:
                    max_q = max(max_q, max(gate.qubits))
            if max_q >= 0:
                num_qubits = max_q + 1
            else:
                num_qubits = 1
        qc = QuantumCircuit(num_qubits)
        for gate in ast.operations:
            if gate.type.name == 'H':
                qc.h(gate.qubits[0])
            elif gate.type.name == 'CX':
                qc.cx(gate.qubits[0], gate.qubits[1])
            elif gate.type.name == 'X':
                qc.x(gate.qubits[0])
            elif gate.type.name == 'Y':
                qc.y(gate.qubits[0])
            elif gate.type.name == 'Z':
                qc.z(gate.qubits[0])
        simulator = AerSimulator()
        qc.save_statevector()
        result = simulator.run(qc).result()
        statevector = result.get_statevector()
        print(f"[Debug] Statevector: {statevector}")
        return statevector

    @staticmethod
    def compute_bloch_vectors(statevector):
        """Compute Bloch vectors for each qubit."""
        import numpy as np
        n_qubits = int(np.log2(len(statevector)))
        vectors = []
        
        for qubit in range(n_qubits):
            if n_qubits == 1:
                # Direct computation for single qubit
                alpha = statevector[0]
                beta = statevector[1]
                x = 2 * np.real(alpha * np.conj(beta))
                y = 2 * np.imag(alpha * np.conj(beta))
                z = np.abs(alpha)**2 - np.abs(beta)**2
                vectors.append((x, y, z))
                print(f"[Debug] Qubit {qubit} Bloch vector: ({x:.3f}, {y:.3f}, {z:.3f})")
            else:
                # Partial trace for multi-qubit
                rho_full = np.outer(statevector, np.conj(statevector))
                trace_out = [i for i in range(n_qubits) if i != qubit]
                rho_q = partial_trace(rho_full, trace_out)
                X = np.array([[0, 1], [1, 0]])
                Y = np.array([[0, -1j], [1j, 0]])
                Z = np.array([[1, 0], [0, -1]])
                x = np.real(np.trace(rho_q @ X))
                y = np.real(np.trace(rho_q @ Y))
                z = np.real(np.trace(rho_q @ Z))
                vectors.append((x, y, z))
                print(f"[Debug] Qubit {qubit} Bloch vector: ({x:.3f}, {y:.3f}, {z:.3f})")
        
        return vectors

    @staticmethod
    def plot(vectors, save_path="bloch.png"):
        if not vectors:
            print("No qubits to plot.")
            return
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = np.cos(u)*np.sin(v)
        y = np.sin(u)*np.sin(v)
        z = np.cos(v)
        ax.plot_wireframe(x, y, z, color='gray', alpha=0.2)
        ax.quiver(0, 0, 0, 1.2, 0, 0, color='r', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 1.2, 0, color='g', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 0, 1.2, color='b', arrow_length_ratio=0.1)
        ax.text(1.3, 0, 0, 'X')
        ax.text(0, 1.3, 0, 'Y')
        ax.text(0, 0, 1.3, 'Z')
        for i, (x, y, z) in enumerate(vectors):
            ax.quiver(0, 0, 0, x, y, z, color='red', arrow_length_ratio=0.2)
            ax.text(x*1.1, y*1.1, z*1.1, f'q{i}')
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_axis_off()
        plt.tight_layout()
        full_path = os.path.abspath(save_path)
        try:
            plt.savefig(full_path, bbox_inches='tight', dpi=150)
            print(f"✅ Bloch sphere saved to: {full_path}")
        except Exception as e:
            print(f"❌ Failed to save: {e}")
        finally:
            plt.close(fig)
