import numpy as np
from .statevector import StatevectorVisualizer

class ProbabilitiesVisualizer:
    @staticmethod
    def compute(circuit):
        state = StatevectorVisualizer.compute(circuit)
        probs = np.abs(state)**2
        return probs

    @staticmethod
    def display(probs, max_bars=20):
        n = len(probs)
        if n == 0:
            return "(no qubits)"
        lines = []
        # Find top max_bars
        indices = sorted(range(n), key=lambda i: probs[i], reverse=True)
        shown = 0
        for i in indices:
            if probs[i] < 0.01 and shown >= 10:
                break
            if probs[i] > 0.001:
                bar_len = int(probs[i] * 50)  # scale to 50 chars max
                lines.append(f"|{i:0{int(np.log2(n))}b}⟩: {'█' * bar_len} {probs[i]*100:.2f}%")
                shown += 1
        if not lines:
            return "(all zero)"
        return "\n".join(lines)
