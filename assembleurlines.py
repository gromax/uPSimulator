'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from errors import *
from litteral import Litteral
from variable import Variable


class AsmLine:
    _label = ""
    _lineNumber = -1
    def stringifyOperand(self, operand):
        if isinstance(operand, Litteral) or isinstance(operand, Variable):
            return str(operand)
        elif isinstance(operand, int):
            # registre
            return "r"+str(operand)
        return "?"

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        return "0"*wordSize

    def __str__(self):
        return "< AsmLine >"

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

class AsmLabelLine(AsmLine):
    def __init__(self, parent, lineNumber, label):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        '''
        self._parent = parent
        self._lineNumber = lineNumber
        self._label = str(label)

    def __str__(self):
        return self._label


class AsmJumpLine(AsmLine):
    def __init__(self, parent, lineNumber, label, opcode, asmCommand, cible):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        cible = string (label)
        '''
        self._parent = parent
        self._lineNumber = lineNumber
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._cible = str(cible)

    def __str__(self):
        return self._label + "\t" + self._asmCommand + " " + str(self._cible)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        lineCible = self._parent.getLineLabel(self._cible)
        if lineCible == None:
            raise CompilationError(f"Label {self._cible} introuvable !")
        return self.formatBinary(wordSize, [(lineCible, 0)])

class AsmStdLine(AsmLine):
    def __init__(self, parent, lineNumber, label, opcode, asmCommand, operands):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        operands = tuple avec les opérandes, la dernière pouvant être un Litteral, ou None
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

    def __str__(self):
        strOperands = [ self.stringifyOperand(ope) for ope in self._operands]
        return self._label+"\t"+self._asmCommand+" "+", ".join(strOperands)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        items = []
        for op in self._operands:
            if isinstance(op, Litteral):
                items.append((op, 0))
            else:
                items.append((op,regSize))
        return self.formatBinary(wordSize, items)

class AsmMemoryLine(AsmLine):
    def __init__(self, parent, lineNumber, label, opcode, asmCommand, register, memory):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        register = entier
        memory = Variable ou Litteral
        '''
        assert isinstance(register,int)
        assert isinstance(memory, Variable) or isinstance(memory, Litteral)
        self._parent = parent
        self._lineNumber = lineNumber
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._register = register
        self._memory = memory

    def __str__(self):
        return self._label + "\t" + self._asmCommand + " r" + str(self._register) + ", " + str(self._memory)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        register = self._register
        memory = self._memory
        memAbsolutePosition = self._parent.getMemAbsPos(memory)
        return self.formatBinary(wordSize, [(register, regSize), (memAbsolutePosition, 0)])


class AsmInputLine(AsmLine):
    def __init__(self, parent, lineNumber, label, opcode, asmCommand, destination):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        destination = Variable
        '''
        assert isinstance(destination, Variable)
        self._parent = parent
        self._lineNumber = lineNumber
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._destination = destination

    def __str__(self):
        return self._label+"\t" + self._asmCommand+" " + str(self._destination)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        dest = self._destination
        memAbsolutePosition = self._parent.getMemAbsPos(dest)
        return self.formatBinary(wordSize, [(memAbsolutePosition, 0)])

class AsmPrintLine(AsmLine):
    def __init__(self, parent, lineNumber, label, opcode, asmCommand, source):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = int (registre)
        '''
        assert isinstance(source, int)
        self._parent = parent
        self._lineNumber = lineNumber
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._source = source

    def __str__(self):
        return self._label+"\t" + self._asmCommand+" r" + str(self._source)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        source = self._source
        return self.formatBinary(wordSize, [(source, regSize)])

class AsmLitteralLine(AsmLine):
    def __init__(self, parent, lineNumber, litteral):
        '''
        parent = objet AssembleurContainer parent
        lineNumber = int = numéro de la ligne d'origine
        litteral = Litteral object
        '''
        assert isinstance(litteral,Litteral)
        self._parent = parent
        self._lineNumber = lineNumber
        self._litteral = litteral

    def __str__(self):
        return "\t"+str(self._litteral)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        return self._litteral.getBinary(wordSize)

