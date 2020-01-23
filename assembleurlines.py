'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from errors import *
from litteral import Litteral
from variable import Variable

class AsmLine:
    __label = ""
    __lineNumber = -1

    def __init__(self, parent, lineNumber, label, opcode, asmCommand, operands):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère - vide pour ligne vide
        asmCommand = chaine de caractère - vide pour ligne vide
        operands = None ou  tuple avec les opérandes, la dernière pouvant être un Litteral ou Variable ou string (label)
        '''
        self.__parent = parent
        self.__lineNumber = lineNumber
        self.__label = str(label)
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        if operands == None :
            self.__operands = ()
        else:
            self.__operands = operands
        if len(self.__operands) > 0:
            for op in self.__operands[:-1]:
                assert isinstance(op,int)
            lastOpe = self.__operands[-1]
            assert isinstance(lastOpe,int) or isinstance(lastOpe,str) or isinstance(lastOpe,Variable) or isinstance(lastOpe,Litteral)

    def __stringifyOperand(self, operand):
        if isinstance(operand, Litteral) or isinstance(operand, Variable):
            return str(operand)
        elif isinstance(operand, int):
            # registre
            return "r"+str(operand)
        else:
            # label
            return operand

    def __formatBinary(self, item):
        '''
        item = tuple avec (valeur, taille), valeur = int ou Litteral
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

    def __zeroPadding(self, binaryCode, wordSize):
        '''
        retourne une version de binaryCode complétée par des 0
        '''
        unusedBits = wordSize - len(binaryCode)
        if unusedBits < 0:
            raise CompilationError(f"{self} : code binaire trop long !")
        return binaryCode + "0"*unusedBits

    def __getLastOperandSize(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        if len(self.__operands) == 0:
            return 0
        bitsForLast = wordSize - len(self.__opcode) - (len(self.__operands)-1) * regSize
        if bitsForLast <= 0:
            raise CompilationError(f"{self} : Plus assez de place pour le dernier opérande !")
        return bitsForLast

    def __str__(self):
        strOperands = [ self.__stringifyOperand(ope) for ope in self.__operands]
        return self.__label+"\t"+self.__asmCommand+" "+", ".join(strOperands)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        if self.isEmpty():
            return ""
        if len(self.__operands) == 0:
            return self.__zeroPadding(self.__opcode, wordSize)
        # construction liste des items à coder
        bitsForLast = self.__getLastOperandSize(wordSize,regSize)
        items = [ (op,regSize) for op in self.__operands[:-1] ]
        lastOperand = self.__operands[-1]

        if isinstance(lastOperand, Litteral):
            items.append((lastOperand.getValue(), bitsForLast))
        elif isinstance(lastOperand,Variable):
            memAbsolutePosition = self.__parent.getMemAbsPos(lastOperand)
            if memAbsolutePosition == None:
                raise CompilationError(f"Mémoire {lastOperand} introuvable !")
            items.append((memAbsolutePosition,bitsForLast))
        elif isinstance(lastOperand,str):
            # label
            lineCible = self.__parent.getLineLabel(lastOperand)
            if lineCible == None:
                raise CompilationError(f"Label {lastOperand} introuvable !")
            items.append((lineCible, bitsForLast))
        else:
            # registre
            if bitsForLast < regSize:
                raise CompilationError(f"{self} : Plus assez de place pour le dernier opérande !")
            items.append((lastOperand,regSize))

        listStrItems = [self.__formatBinary(item) for item in items]
        strItems = "".join(listStrItems)
        return self.__zeroPadding(self.__opcode + strItems, wordSize)

    def isEmpty(self):
        return self.__asmCommand == "" or self.__opcode == ""

    def getLabel(self):
        return self.__label

    def getSizeInMemory(self):
        '''
        retourne le ligne mémoire que nécessitera cette ligne :
        - 0 pour ligne vide
        - 1 pour ligne ordinaire
        '''
        if self.isEmpty():
            return 0
        return 1


