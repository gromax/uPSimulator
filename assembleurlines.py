"""
.. module:: assembleurlines
:synopsis: définition d'un objet contenant une ligne du code assembleur
"""

from typing import Tuple, Union, List, Optional

from errors import *
from litteral import Litteral
from variable import Variable
from label import Label

class AsmLine:
    """Ligne de code assembleur.
    Stocke les informations relatives à une ligne :

    * opérandes
    * opcode
    * label

    et calcule le code binaire correspondant
    """
    _label:Optional[Label] = None
    _specialOperand:Union[Variable, Label, Litteral, None] = None
    _lineNumber = -1

    def __init__(self, lineNumber:int, label:Optional[Label], opcode:str, asmCommand:str, regOperands:Tuple[int,...], specialOperand:Union[Variable, Label, Litteral, None]):
        """Constructeur

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: étiquette
        :type label: Optional[Label]
        :param opcode: opcode de la commande, vide pour commande vide
        :type opcode: str
        :param asmCommand: commande assembleur, vide pour commande vide
        :type asmCommand: str
        :param regOperands: opérandes de type registre
        :type regOperands: tuple[int]
        :param specialOperand: opérande spéciale. str pour label, Variable pour échange mémoire, Litteral. None si aucune.
        :type specialOperand: Label / Variable / Litteral / None
        """
        self._lineNumber = lineNumber
        if isinstance(label, Label):
            self._label = label
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._regOperands = regOperands
        for op in self._regOperands:
            assert isinstance(op,int)
        if not specialOperand is None:
            self._specialOperand = specialOperand

    @property
    def lineNumber(self) -> int:
        """Accesseur

        :return: numéro de la ligne d'origine
        :rtype: int

        :Example:
          >>> AsmLine(12,"Lab1", "1111", "ADD", (0,2), None).lineNumber
          12
        """
        return self._lineNumber

    @property
    def label(self) -> Optional[Label]:
        """Accesseur
        :return: étiquette
        :rtype: Label
        """
        return self._label

    @staticmethod
    def _stringifyRegOperand(operand:int) -> str:
        """Facile la création du texte associé à un registre.

        :param operand: numéro du registre
        :type operand: int
        :return: nom du registre sous forme r + numéro
        :rtype: int

        :Example:
          >>> AsmLine._stringifyRegOperand(2)
          'r2'
        """
        return "r"+str(operand)

    def __str__(self) -> str:
        strOperands = [ AsmLine._stringifyRegOperand(ope) for ope in self._regOperands]
        if self._label is None:
            strLabel = ""
        else:
            strLabel = str(self._label)
        if self._specialOperand != None:
            strOperands.append(str(self._specialOperand))
        if len(strOperands) > 0:
            operands = ", ".join(strOperands)
            return "{}\t{} {}".format(strLabel, self._asmCommand, operands)
        return "{}\t{}".format(strLabel, self._asmCommand)

    def getLastOperandSize(self, wordSize:int, regSize:int) -> int:
        """Retourne le nombre de bits laissés pour le codage binaire d'un éventuel dernier argument spécial (Litteral, Variable ou str pour label)

        :param wordSize: taille du mot en mémoire
        :type wordSize: int
        :param regSize: taille des opérandes de type registre
        :type regSize: int
        :return: nombre de bits laissés après les registres
        :rtype: int

        :Example:
          >>> AsmLine(-1,"", "1111", "ADD", (0,2), None).getLastOperandSize(16,3)
          6
        """
        return wordSize - len(self._opcode) - len(self._regOperands) * regSize

    def getElementsToCode(self) -> List[Union[int, str, Label, Variable, Litteral]]:
        """Retourne une liste d'éléments à coder

        :return: liste des éléments à coder
        :rtype: List[Union[int, str, Variable, Litteral]]
        """
        # construction liste des éléments à coder
        listElements:List[Union[int, str, Label, Variable, Litteral]] = [ self._opcode ]
        for reg in self._regOperands:
            listElements.append(reg)
        if not self._specialOperand is None:
            listElements.append(self._specialOperand)
        return listElements

    def getSizeInMemory(self) -> int:
        """Détermine  le nombre de lignes mémoires nécessaires pour cette ligne assembleur.

        :return: 1 pour ligne ordinaire
        :rtype: int

        :Example:
          >>> AsmLine(-1,"", "ADD", "111", (0,2,3), None).getSizeInMemory()
          1
        """

        return 1

if __name__=="__main__":
    import doctest
    doctest.testmod()

