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

    def isEmpty(self):
        return self._asmCommand == "" or self._opcode == ""

    def stringifyOperand(self, operand):
        if isinstance(operand, Litteral) or isinstance(operand, Variable):
            return str(operand)
        elif isinstance(operand, int):
            # registre
            return "r"+str(operand)
        elif isinstance(operand, str):
            # label
            return operand
        return "?"

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        if self.isEmpty():
            return ""
        bigLitteralToAddNext = None
        items = []
        for op in self._operands:
            if isinstance(op, Litteral):
                items.append((op, 0))
                if op.isBig():
                    bigLitteralToAddNext = op
            elif isinstance(op,Variable):
                memAbsolutePosition = self._parent.getMemAbsPos(op)
                if memAbsolutePosition == None:
                    raise CompilationError(f"Mémoire {op} introuvable !")
                items.append((memAbsolutePosition,0))
            elif isinstance(op,str):
                # label
                lineCible = self._parent.getLineLabel(op)
                if lineCible == None:
                    raise CompilationError(f"Label {op} introuvable !")
                items.append((lineCible, 0))
            else:
                # registre
                items.append((op,regSize))
        outStr = self.formatBinary(wordSize, items)
        if bigLitteralToAddNext == None:
            return outStr
        return outStr+"\n"+bigLitteralToAddNext.getBinary(wordSize)

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
                strItems += valeur.getBinary(size)
            else:
                strItems += format(valeur, '0'+str(size)+'b')
        unusedBits = sizeForItems - len(strItems)
        if unusedBits < 0:
            raise CompilationError(f"Le code {code} dépasse la taille limit de {wordSize} bits.")
        return self._opcode + strItems + "0"*unusedBits

    def getLabel(self):
        return self._label

    def getSizeInMemory(self):
        '''
        retourne le ligne mémoire que nécessitera cette ligne :
        - 0 pour ligne vide
        - 1 pour ligne ordinaire
        - 2 pour une commande plaçant un littéral à la suite
        '''
        if self.isEmpty():
            return 0
        if len(self._operands)== 0:
            return 1
        lastOperand = self._operands[-1]
        if not isinstance(lastOperand, Litteral) or not lastOperand.isBig():
            return 1
        return 2


