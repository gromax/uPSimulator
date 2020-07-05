"""
.. module:: actionsfifo
:synopsis: File des opérations constituant le programme
"""

from typing import Union, List, Optional, Tuple

from modules.primitives.variable import Variable
from modules.primitives.litteral import Litteral
from modules.primitives.label import Label
from modules.primitives.operators import Operator
from modules.primitives.register import Register


ActionType = Union[Operator, Variable, Litteral, Register, Label]

class ActionsFIFO:
    _actions:Tuple[ActionType,...]
    def __init__(self):
        self._actions = tuple()

    def append(self, *actions:ActionType) -> 'ActionsFIFO':
        self._actions = self._actions + actions
        return self

    def concat(self, actionfile:'ActionsFIFO'):
        self._actions = self._actions + actionfile._actions
        return self

    def __str__(self) -> str:
        lines:List[str] = []
        currentLine:List[str] = []
        for item in self._actions:
            currentLine.append(str(item))
            if isinstance(item, Operator):
                lines.append(" ".join(currentLine))
                currentLine = []
        return "\n".join(lines)

    def inlineStr(self) -> str:
        return ", ".join([str(item) for item in self._actions])

    @property
    def empty(self):
        return len(self._actions) == 0

    def pop(self) -> ActionType:
        if len(self._actions) == 0:
            raise IndexError("ActionsFIFO.pop : index out of range")
        action = self._actions[0]
        self._actions = self._actions[1:]
        return action

    def readNext(self) -> Optional[ActionType]:
        if len(self._actions) == 0:
            return None
        return self._actions[0]


if __name__=="__main__":
    pass
