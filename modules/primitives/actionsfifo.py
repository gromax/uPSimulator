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
    _lineNumber:int = 0
    _label:Optional[Label] = None
    def __init__(self):
        self._actions = tuple()

    def setLabel(self, label:Label):
        self._label = label
    
    def setLineNumber(self, lineNumber:int):
        self._lineNumber = lineNumber

    @property
    def lineNumber(self) -> int:
        """Accesseur
        :return: label s'il existe ou None
        :rtype: Optional[Label]
        """
        return self._label
    
    @property
    def label(self) -> Optional[Label]:
        """Accesseur
        :return: numéro de ligne correspondant à la file
        :rtype: int
        """
        return self._lineNumber


    def append(self, *actions:ActionType) -> 'ActionsFIFO':
        self._actions = self._actions + actions
        return self

    def concat(self, actionfile:'ActionsFIFO'):
        self._actions = self._actions + actionfile._actions
        return self

    def __str__(self) -> str:
        if len(self._actions) == 0:
            return ""
        lines:List[str] = []
        currentLine:List[str] = []
        for item in self._actions:
            currentLine.append(str(item))
            if isinstance(item, Operator):
                lines.append(" ".join(currentLine))
                currentLine = []
        if not self._label is None:
            lines[0] = str(self._label) + "\t" + lines[0]
        else:
            lines[0] = "\t" + lines[0]
        for i in range(1,len(lines)):
            lines[i] = "\t" + lines[i]
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
