'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from errors import *
from litteral import Litteral
from variable import Variable


class AsmLine:
    _label = ""
    _lineNumber = -1

    def __init__(self, parent, lineNumber, label, opcode, asmCommand, operands):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère - vide pour ligne vide
        asmCommand = chaine de caractère - vide pour ligne vide
        operands = None ou  tuple avec les opérandes, la dernière pouvant être un Litteral ou Variable ou string (label)
        '''
        self._parent = parent
        self._lineNumber = lineNumber
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        if operands == None :
            self._operands = ()
        else:
            self._operands = operands
        if len(self._operands) > 0:
            for op in self._operands[:-1]:
                assert isinstance(op,int)
            lastOpe = self._operands[-1]
            assert isinstance(lastOpe,int) or isinstance(lastOpe,str) or isinstance(lastOpe,Variable) or isinstance(lastOpe,Litteral)

    def isEmpty(self):
        return self._asmCommand == "" or self._opcode == ""

    def stringifyOperand(self, operand):
        if isinstance(operand, Litteral) or isinstance(operand, Variable):
            return str(operand)
        elif isinstance(operand, int):
            # registre
            return "r"+str(operand)
        else:
            # label
            return operand

    def getBinary(self, wordSize, regSize, bigLitteralNext):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        bigLitteralNext = Booléen, indique si un grand booléen doit être placé à la suite
        '''
        if self.isEmpty():
            return ""
        if len(self._operands) == 0:
            return self.__zeroPadding(self._opcode, wordSize)
        # construction liste des items à coder
        bitsForLast = self.__getLastOperandSize(wordSize,regSize)
        items = [ (op,regSize) for op in self._operands[:-1] ]
        lastOperand = self._operands[-1]

        if isinstance(lastOperand, Litteral):
            items.append((lastOperand, bitsForLast))
        elif isinstance(lastOperand,Variable):
            memAbsolutePosition = self._parent.getMemAbsPos(lastOperand)
            if memAbsolutePosition == None:
                raise CompilationError(f"Mémoire {lastOperand} introuvable !")
            items.append((memAbsolutePosition,bitsForLast))
        elif isinstance(lastOperand,str):
            # label
            lineCible = self._parent.getLineLabel(lastOperand)
            if lineCible == None:
                raise CompilationError(f"Label {lastOperand} introuvable !")
            items.append((lineCible, bitsForLast))
        else:
            # registre
            if bitsForLast < regSize:
                raise CompilationError(f"{self} : Plus assez de place pour le dernier opérande !")
            items.append((lastOperand,regSize))
        outStr = self.formatBinary(wordSize, items)

        # il faut prévoir d'ajouter un item en ligne suivante si nécessaire
        if bigLitteralNext and isinstance(lastOperand, Litteral) and not lastOperand.isBetween(0,2**bitsForLast-2):
            return outStr+"\n"+lastOperand.getBinary(wordSize)
        return outStr

    def __zeroPadding(self, binaryCode, wordSize):
        '''
        retourne une version de binaryCode complétée par des 0
        '''
        unusedBits = wordSize - len(binaryCode)
        if unusedBits < 0:
            raise CompilationError(f"{self} : code binaire trop long !")
        return binaryCode + "0"*unusedBits

    def __str__(self):
        strOperands = [ self.stringifyOperand(ope) for ope in self._operands]
        return self._label+"\t"+self._asmCommand+" "+", ".join(strOperands)

    def formatBinary(self, wordSize, items):
        '''
        wordSize = int = nombre de bits que doit contenir le mot
        items = Liste de tuple avec (valeur, taille), valeur = int ou Litteral
        Si taille = 0, occupe tout l'espace disponible
        Erreur si le code final dépasse la taille donné
        Sinon on complète avec des 0
        '''
        strItems = ""
        sizeForItems = wordSize - len(self._opcode)
        for valeur, size in items:
            if size == 0:
                size = sizeForItems - len(strItems)
            if size < 0:
                raise CompilationError("Place allouée à un code binaire négative !")
            if isinstance(valeur, Litteral):
                strItems += valeur.getBinaryForPos(size)
            else:
                strItems += format(valeur, '0'+str(size)+'b')
        return self.__zeroPadding(self._opcode + strItems, wordSize)

    def getLabel(self):
        return self._label

    def __getLastOperandSize(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        if len(self._operands) == 0:
            return 0
        bitsForLast = wordSize - len(self._opcode) - (len(self._operands)-1) * regSize
        if bitsForLast <= 0:
            raise CompilationError(f"{self} : Plus assez de place pour le dernier opérande !")
        return bitsForLast

    def getSizeInMemory(self, wordSize, regSize, bigLitteralNext):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        bigLitteralNext : Booléen. En cas de littéral, peut-on le décaler à la ligne suivante ?
        retourne le ligne mémoire que nécessitera cette ligne :
        - 0 pour ligne vide
        - 1 pour ligne ordinaire
        - 2 pour une commande plaçant un littéral à la suite
        '''
        if self.isEmpty():
            return 0
        if len(self._operands)== 0 or not bigLitteralNext:
            return 1
        lastOperand = self._operands[-1]
        bitsForLast = self.__getLastOperandSize(wordSize, regSize)
        if not isinstance(lastOperand, Litteral) or not lastOperand.isBig(bitsForLast):
            return 1
        return 2


