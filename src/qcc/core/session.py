from typing import List, Optional
from .models import CircuitAST, ViewSettings
from .exceptions import SessionError

class SessionState:
    def __init__(self):
        self.circuit = CircuitAST()
        self.view_settings = ViewSettings()
        self._history: List[CircuitAST] = []
        self._redo_stack: List[CircuitAST] = []
        self._clipboard: Optional[CircuitAST] = None
        self._max_history = 100

    def commit(self):
        if len(self._history) >= self._max_history:
            self._history.pop(0)
        self._history.append(self.circuit)
        self._redo_stack.clear()

    def undo(self) -> CircuitAST:
        if not self._history:
            raise SessionError("Nothing to undo.")
        self._redo_stack.append(self.circuit)
        self.circuit = self._history.pop()
        return self.circuit

    def redo(self) -> CircuitAST:
        if not self._redo_stack:
            raise SessionError("Nothing to redo.")
        self._history.append(self.circuit)
        self.circuit = self._redo_stack.pop()
        return self.circuit

    def clear(self):
        self.circuit = CircuitAST()
        self._history.clear()
        self._redo_stack.clear()
