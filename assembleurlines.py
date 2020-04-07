"""
.. module:: assembleurlines
   :synopsis: définition d'un objet contenant une ligne du code assembleur
"""

from typing import Tuple, Union, List

from errors import *
from litteral import Litteral
from variable import Variable

class AsmLine:
    _label = ""
    _lineNumber = -1

    def __init__(self, lineNumber:int, label:str, opcode:str, asmCommand:str, regOperands:Tuple[int,...], specialOperand:Union[Variable, str, Litteral, None]):
        """Constructeur

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: étiquette
        :type label: str
        :param opcode: opcode de la commande, vide pour commande vide
        :type opcode: str
        :param asmCommand: commande assembleur, vide pour commande vide
        :type asmCommand: str
        :param regOperands: opérandes de type registre
        :type regOperands: tuple[int]
        :param specialOperand: opérande spéciale. str pour label, Variable pour échange mémoire, Litteral. None si aucune.
        :type specialOperand: str / Variable / Litteral / None
        """
        self._lineNumber = lineNumber
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._specialOperand = specialOperand
        self._regOperands = regOperands
        for op in self._regOperands:
            assert isinstance(op,int)
        if specialOperand != None:
            assert isinstance(specialOperand,str) or isinstance(specialOperand,Variable) or isinstance(specialOperand,Litteral)

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
    def label(self) -> str:
        """Accesseur

        :return: étiquette
        :rtype: str

        :Example:
          >>> AsmLine(-1,"Lab1", "1111", "ADD", (0,2), None).label
          'Lab1'
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
        if self._specialOperand != None:
            strOperands.append(str(self._specialOperand))
        if len(strOperands) > 0:
            return self._label+"\t"+self._asmCommand+" "+", ".join(strOperands)
        return self._label+"\t"+self._asmCommand

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

    def getElementsToCode(self) -> List[Union[int, str, Variable, Litteral]]:
        """Retourne une liste d'éléments à coder

        :return: liste des éléments à coder
        :rtype: List[Union[int,str, Variable, Litteral]]
        """
        if self.isEmpty():
            return []
        # construction liste des éléments à coder
        listElements = [ self._opcode ]
        for reg in self._regOperands:
            listElements.append(reg)
        if self._specialOperand != None:
            # ajout d'un séparateur
            listElements.append("|")
            listElements.append(self._specialOperand)
        return listElements

    def isEmpty(self) -> bool:
        """La ligne est-elle vide ?

        :return: vrai s'il n'y apas d'opcode ou de commande assembleur
        :rtype: bool

        :Example:
          >>> AsmLine(-1,"", "", "", (), "").isEmpty()
          True

          >>> AsmLine(-1,"", "1111", "LOAD", (), "").isEmpty()
          False
        """
        return self._asmCommand == "" or self._opcode == ""

    def copyNonEmptyLabel(self, labelLine:"AsmLine") -> None:
        """Copie le label de labelLine comme nouveau label de l'item courant,
        si ce la bel n'est pas vide

        :param labelLine: ligne dont on doit récupérer le label
        :type labelLine: AsmLine
        """
        newLabel = labelLine.label
        if newLabel != '':
            self._label = newLabel

    def getJumpCible(self) -> str:
        """Si _specialOperand est str, c'est donc un jump, on retourne la cible

        :return: label de la cible si c'est un saut, '' sinon
        :rtype: str

        :Example:
          >>> AsmLine(-1,"", "", "", (), "Lab1").getJumpCible()
          'Lab1'

          >>> AsmLine(-1,"", "", "", (), "").getJumpCible()
          ''
        """
        if isinstance(self._specialOperand, str):
            return self._specialOperand
        return ''

    def setJumpCible(self, newLabel:str) -> None:
        """Si le _specialOperand est str, donc un label, il est remplacé par newLabel

        :param newLabel: nouveau label cible
        :type newLabel: str
        """

        if isinstance(self._specialOperand, str) and newLabel != '':
            self._specialOperand = newLabel


    def getSizeInMemory(self) -> int:
        """Détermine  le nombre de lignes mémoires nécessaires pour cette ligne assembleur.

        :return: 0 pour ligne vide, 1 pour ligne ordinaire
        :rtype: int

        :Example:
          >>> AsmLine(-1,"", "", "", (), None).getSizeInMemory()
          0

          >>> AsmLine(-1,"", "ADD", "111", (0,2,3), None).getSizeInMemory()
          1
        """
        if self.isEmpty():
            return 0
        return 1

if __name__=="__main__":
    import doctest
    doctest.testmod()

