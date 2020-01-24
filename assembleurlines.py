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
    __label = ""
    __lineNumber = -1

    def __init__(self, parent, lineNumber:int, label:str, opcode:str, asmCommand:str, regOperands:Tuple[int,...], specialOperand:Union[Variable, str, Litteral, None]):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère - vide pour ligne vide
        asmCommand = chaine de caractère - vide pour ligne vide
        regOperands = tuple avec les opérandes de type registre
        specialOperand = opérande spéciale : str pour label, Variable pour échange mémoire, Litteral. None si aucune.
        '''
        self.__parent = parent
        self.__lineNumber = lineNumber
        self.__label = str(label)
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__specialOperand = specialOperand
        self.__regOperands = regOperands
        for op in self.__regOperands:
            assert isinstance(op,int)
        if specialOperand != None:
            assert isinstance(specialOperand,str) or isinstance(specialOperand,Variable) or isinstance(specialOperand,Litteral)

    def __stringifyRegOperand(self, operand:int) -> str:
        return "r"+str(operand)

    def __formatBinary(self, item:Tuple[int,int]) -> str:
        '''
        item = tuple avec (valeur, taille), valeur
        Erreur si le code final dépasse la taille donné
        '''
        value, size = item
        if size <= 0:
            raise CompilationError(f"{self} -> binaire : Place allouée à un code binaire négative !")
        if value < 0:
            raise CompilationError(f"{self} -> binaire : valeur à coder négative !")

        strItem = format(value, '0'+str(size)+'b')

        if len(strItem) > size:
            raise CompilationError(f"{self} -> binaire : valeur à coder trop grande !")
        return strItem

    def __zeroPadding(self, binaryCode:str, wordSize:int) -> str:
        """Retourne le code binaire complété par des 0 si nécessaire
        Args:
           binaryCode (str): code binaire à compléter
           wordSize (int): taille du mot une fois complété

        Returns:
           str.

        Raises:
            CompilationError
        """

        unusedBits = wordSize - len(binaryCode)
        if unusedBits < 0:
            raise CompilationError(f"{self} : code binaire trop long !")
        return binaryCode + "0"*unusedBits

    def __getLastOperandSize(self, wordSize:int, regSize:int) -> int:
        """Retourne le nombre de bits laissés pour le codage binaire d'un éventuel dernier argument spécial (Litteral, Variable ou str pour label)
        Args:
           wordSize (int): taille du mot en mémoire
           wordSize (regSize): taille des opérandes de type registre

        Returns:
           int.
        """
        return wordSize - len(self.__opcode) - len(self.__regOperands) * regSize

    def __str__(self) -> str:
        strOperands = [ self.__stringifyRegOperand(ope) for ope in self.__regOperands]
        if self.__specialOperand != None:
            strOperands.append(str(self.__specialOperand))
        return self.__label+"\t"+self.__asmCommand+" "+", ".join(strOperands)

    def getBinary(self, wordSize:int, regSize:int) -> str:
        """Retourne le code binaire correspondant à cette commande assembleur

        :param wordSize: taille du mot en mémoire
        :type wordSize: int
        :param regSize: taille des opérandes de type registre
        :type regSize: int
        :return:code binaire
        :rtype: str

        :Example:

        >>> 2+2
        4

        .. seealso:: blabla
        .. warning:: Attention
        .. note:: une note
        """
        if self.isEmpty():
            return ""
        # construction liste des items à coder
        items = [ (reg,regSize) for reg in self.__regOperands ]
        if self.__specialOperand != None:
            bitsForLast = self.__getLastOperandSize(wordSize,regSize)

            if isinstance(self.__specialOperand, Litteral):
                valueToCode = self.__specialOperand.getValue()
            elif isinstance(self.__specialOperand,Variable):
                valueToCode = self.__parent.getMemAbsPos(self.__specialOperand)
                if valueToCode == None:
                    raise CompilationError(f"Mémoire {self.__specialOperand} introuvable !")
            else:
                # label
                valueToCode = self.__parent.getLineLabel(self.__specialOperand)
                if valueToCode == None:
                    raise CompilationError(f"Label {self.__specialOperand} introuvable !")
            valueToCodeAndSize = (valueToCode, bitsForLast)
            items.append(valueToCodeAndSize)

        listStrItems = [self.__formatBinary(item) for item in items]
        strItems = "".join(listStrItems)
        return self.__zeroPadding(self.__opcode + strItems, wordSize)

    def isEmpty(self) -> bool:
        return self.__asmCommand == "" or self.__opcode == ""

    def getLabel(self) -> str:
        return self.__label

    def getSizeInMemory(self) -> int:
        '''
        retourne le ligne mémoire que nécessitera cette ligne :
        - 0 pour ligne vide
        - 1 pour ligne ordinaire
        '''
        if self.isEmpty():
            return 0
        return 1


