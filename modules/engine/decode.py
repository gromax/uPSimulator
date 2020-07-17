"""
.. module:: modules.engine.decode
   :synopsis: assure le décodage d'un mot binaire
"""

from typing import List, Tuple
from typing_extensions import TypedDict
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum

import re

from modules.primitives.operators import Operator, Operators

class ArgsType(Enum):
    ADRESSE  = 1
    REGISTRE = 2
    LITTERAL = 3

ArgItem = Tuple[ArgsType, int]
Decoded = TypedDict('Decoded', {'operator':Operator, 'args':List[ArgItem]})

DefaultDecoded = {'operator':Operators.HALT, 'args':[]}


class Decodeur(metaclass=ABCMeta):
    _opcode: str # précise des bits à 0, à 1, des bits ignorés (X) et des bits codant des arguments (#)
    _command: Operator
    _regex: str
    _args: List[ArgItem]
    _argsPos: Tuple[int,...]
    _opcodePos: Tuple[int,...]
    def __init__(self, opcode:str, command:Operator, *args):
        """
        définit la structure de la commande
        :param opcode: opcode sous forme d'une chaîne binaire
        :type opcode: str
        :param command: commande que devra exécuter le processeur
        :type command: Operator
        :param args: liste des items sous forme de tuples type, taille
        :type args: List[Tuple[ActionType, int]]
        """
        self._opcode = opcode
        self._command = command
        
        size_args = len([letter for letter in opcode if letter == "#"])
        for it in args:
            assert isinstance(it, tuple) and len(it) == 2
            t, s = it
            assert t in ArgsType and isinstance(s, int)
            size_args -= s
        self._args = args
        assert size_args == 0, "L'opcode {} n'a pas le bon nombre de slots pour les arguments.".format(opcode)
        self._opcodePos = Tuple([i for i, b in enumerate(opcode) if b in "01"])
        self._argPos = Tuple([i for i, b in enumerate(opcode) if b == "#"])
        self._regex = r"^[01]{" + str(len(opcode)) + r"}$"

    def match(self, binary:str) -> bool:
        """
        vérifie si le code binaire correspond au format
        :param binary: code binaire à analyser
        :type binary: str
        :return: le code correspond
        :rtype: bool
        """
        if not re.match(self._regex, binary):
            return False
        for i in self._opcodePos:
            if binary[i] != self._opcode[i]:
                return False
        return True

    def _getArgs(self, binary:str) -> List[ArgItem]:
        """
        lit les positions des arguments et retourne les arguments
        :param binary: code binaire à analyser
        :type binary: str
        :return: arguments
        :rtype: List[ArgItem]
        """
        assert re.match(self._regex, binary)

        partieCodante = "".join([binary[i] for i in self._argPos])
        out = []
        for t, s in self._args:
            value = int(partieCodante[:s],2)
            out.append((t, value))
            partieCodante = partieCodante[s:]
        return out

    def decode(self, binary:str) -> Decoded:
        """
        lit les positions des arguments et retourne les arguments
        :param binary: code binaire à analyser
        :type binary: str
        :return: opérateur et arguments
        :rtype: Decoded 
        """
        return { "operator":self._command, "args":self._getArgs(binary) }