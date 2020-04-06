"""
.. module:: AsmLine
   :platform: Unix, Windows
   :synopsis: définition d'un objet contenant une ligne du code assembleur
"""

from typing import Tuple, Union

from errors import *
from litteral import Litteral
from variable import Variable

class AsmLine:
    _label = ""
    _lineNumber = -1

    def __init__(self, parent, lineNumber:int, label:str, opcode:str, asmCommand:str, regOperands:Tuple[int,...], specialOperand:Union[Variable, str, Litteral, None]):
        """Constructeur

        :param parent: objet contenant l'ensemble du code assembleur
        :type parent: AssembleurContainer
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
        self._parent = parent
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
        '''Accesseur

        :return: numéro de la ligne d'origine
        :rtype: int
        '''
        return self._lineNumber

    def __stringifyRegOperand(self, operand:int) -> str:
        """Facile la création du texte associé à un registre.

        :param operand: numéro du registre
        :type operand: int
        :return: nom du registre sous forme r + numéro
        :rtype: int
        """
        return "r"+str(operand)

    def __formatBinary(self, item:Tuple[int,int]) -> str:
        """Donne la représentation binaire d'un élément de la ligne.

        :param item: paire constituée de la valeur à coder en binaire et du nombre de bits disponibles
        :type item: tuple[int,int]
        :return: code binaire de l'item
        :rtype: str
        :raises:CompilationError si taille négative ou trop faible ou valeur à coder négative.
        """
        value, size = item
        if size <= 0:
            raise CompilationError(f"{self} -> binaire : Place allouée à un code binaire négative !", {"lineNumber":self._lineNumber})
        if value < 0:
            raise CompilationError(f"{self} -> binaire : valeur à coder négative !", {"lineNumber":self._lineNumber})

        strItem = format(value, '0'+str(size)+'b')

        if len(strItem) > size:
            raise CompilationError(f"{self} -> binaire : valeur à coder trop grande !", {"lineNumber":self._lineNumber})
        return strItem

    def __zeroPadding(self, binaryCode:str, wordSize:int) -> str:
        """Retourne le code binaire complété par des 0 si nécessaire

        :param binaryCode: code binaire à compléter
        :type binaryCode: str
        :param wordSize: taille du pot une fois complété
        :type wordSize: int
        :return: mot complété par des "0"
        :rtype: str
        :raises: CompilationError si le mot est trop long
        """

        unusedBits = wordSize - len(binaryCode)
        if unusedBits < 0:
            raise CompilationError(f"{self} : code binaire trop long !", {"lineNumber":self._lineNumber})
        return binaryCode + "0"*unusedBits

    def __getLastOperandSize(self, wordSize:int, regSize:int) -> int:
        """Retourne le nombre de bits laissés pour le codage binaire d'un éventuel dernier argument spécial (Litteral, Variable ou str pour label)

        :param wordSize: taille du mot en mémoire
        :type wordSize: int
        :param regSize: taille des opérandes de type registre
        :type regSize: int
        :return: nombre de bits laissés après les registres
        :rtype: int
        """
        return wordSize - len(self._opcode) - len(self._regOperands) * regSize

    def __str__(self) -> str:
        strOperands = [ self.__stringifyRegOperand(ope) for ope in self._regOperands]
        if self._specialOperand != None:
            strOperands.append(str(self._specialOperand))
        if len(strOperands) > 0:
            return self._label+"\t"+self._asmCommand+" "+", ".join(strOperands)
        return self._label+"\t"+self._asmCommand

    def getBinary(self, wordSize:int, regSize:int) -> str:
        """Retourne le code binaire correspondant à cette commande assembleur

        :param wordSize: taille du mot en mémoire
        :type wordSize: int
        :param regSize: taille des opérandes de type registre
        :type regSize: int
        :return: code binaire
        :rtype: str
        """
        if self.isEmpty():
            return ""
        # construction liste des items à coder
        items = [ (reg,regSize) for reg in self._regOperands ]
        if self._specialOperand != None:
            bitsForLast = self.__getLastOperandSize(wordSize,regSize)

            if isinstance(self._specialOperand, Litteral):
                valueToCode = self._specialOperand.value
            elif isinstance(self._specialOperand,Variable):
                valueToCode = self._parent.getMemAbsPos(self._specialOperand)
                if valueToCode == None:
                    raise CompilationError(f"Mémoire {self._specialOperand} introuvable !", {"lineNumber":self._lineNumber})
            else:
                # label
                valueToCode = self._parent.getLineLabel(self._specialOperand)
                if valueToCode == None:
                    raise CompilationError(f"Label {self._specialOperand} introuvable !", {"lineNumber":self._lineNumber})
            valueToCodeAndSize = (valueToCode, bitsForLast)
            items.append(valueToCodeAndSize)

        listStrItems = [self.__formatBinary(item) for item in items]
        strItems = "".join(listStrItems)
        return self.__zeroPadding(self._opcode + strItems, wordSize)

    def isEmpty(self) -> bool:
        """La ligne est-elle vide ?

        :return: vrai s'il n'y apas d'opcode ou de commande assembleur
        :rtype: bool
        """
        return self._asmCommand == "" or self._opcode == ""

    @property
    def label(self) -> str:
        """Accesseur

        :return: étiquette
        :rtype: str
        """
        return self._label

    def copyNonEmptyLabel(self, labelLine:"AsmLine") -> None:
        """Copie le label de labelLine comme nouveau label de l'item courant,
        si ce la bel n'est pas vide

        :param labelLine: ligne dont on doit récupérer le label
        :type labelLine: AsmLine
        """
        newLabel = labelLine.label
        if newLabel != '':
            self._label = newLabel

    def getSizeInMemory(self) -> int:
        """Détermine  le nombre de lignes mémoires nécessaires pour cette ligne assembleur.

        :return: 0 pour ligne vide, 1 pour ligne ordinaire
        :rtype: int

        :Example:
          >>> AsmLine(None,-1,"", "", "", (), None).getSizeInMemory()
          0

          >>> AsmLine(None,-1,"", "ADD", "111", (0,2,3), None).getSizeInMemory()
          1
        """
        if self.isEmpty():
            return 0
        return 1

if __name__=="__main__":
    import doctest
    doctest.testmod()

