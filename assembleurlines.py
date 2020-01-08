'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from errors import *
from litteral import Litteral
from variable import Variable


class AsmLine:
    _label = ""
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
        items = Liste de tuple avec (valeur, taille)
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
            strItems += format(valeur, '0'+str(size)+'b')
        unusedBits = sizeForItems - len(strItems)
        if unusedBits < 0:
            raise CompilationError(f"Le code {code} dépasse la taille limit de {wordSize} bits.")
        return self._opcode + strItems + "0"*unusedBits

    def getLabel(self):
        return self._label

class AsmLabelLine(AsmLine):
    def __init__(self, parent, label):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        '''
        self._parent = parent
        self._label = str(label)

    def __str__(self):
        return self._label


class AsmJumpLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, cible):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        cible = string (label)
        '''
        self._parent = parent
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

class AsmCmpLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, operands):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        operands = tuple de 2 opérandes
        '''
        assert len(operands) == 2
        self._parent = parent
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._operands = operands
    def __str__(self):
        strOperands = ["r"+str(ope) for ope in self._operands]
        return self._label+"\t"+self._asmCommand+" "+", ".join(strOperands)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        r1, r2 = self._operands
        return self.formatBinary(wordSize, [(r1, regSize), (r2, regSize)])


class AsmUalLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, destination, operands):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        destination = int (registre) ou None si pas nécessaire
        operands = tuple non vide avec les opérandes, la dernière pouvant être un Litteral
        '''
        assert len(operands) != 0
        self._parent = parent
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._destination = destination
        self._operands = operands
    
    def __str__(self):
        lastOperand = self._operands[-1]
        if isinstance(lastOperand, Litteral):
            strLastOperand = str(lastOperand)
        else:
            strLastOperand = "r"+str(lastOperand)
        strOperands = ["r"+str(ope) for ope in self._operands[:-1]]
        strOperands.append(strLastOperand)
        if self._destination == None:
            return self._label+"\t"+self._asmCommand+" "+", ".join(strOperands)
        return self._label+"\t"+self._asmCommand+" r"+str(self._destination)+", "+", ".join(strOperands)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        items = []
        if self._destination != None:
            items.append((self._destination, regSize))
        for op in self._operands:
            if isinstance(op, Litteral):
                items.append((op.getValue(), 0))
            else:
                items.append((op,regSize))
        return self.formatBinary(wordSize, items)

class AsmMoveLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, source, destination):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = entier (registre) ou Litteral
        destination = entier (registre)
        '''
        assert isinstance(source,int) or isinstance(source,Litteral)
        self._parent = parent
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._source = source
        self._destination = destination

    def __str__(self):
        if isinstance(self._source, Litteral):
            return self._label + "\t" + self._asmCommand + " r" + str(self._destination) + ", " + str(self._source)
        return self._label + "\t" + self._asmCommand + " r" + str(self._destination) + ", r"+str(self._source)
    
    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        source = self._source
        dest = self._destination
        if isinstance(self._source, Litteral):
            return self.formatBinary(wordSize, [(dest, regSize), (source.getValue(), 0)])
        return self.formatBinary(wordSize, [(dest, regSize), (source, regSize)])

class AsmStoreLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, source, destination):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = entier
        destination = Variable
        '''
        assert isinstance(source,int)
        assert isinstance(destination, Variable)
        self._parent = parent
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._source = source
        self._destination = destination

    def __str__(self):
        return self._label + "\t" + self._asmCommand + " r" + str(self._source) + ", " + str(self._destination)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        source = self._source
        dest = self._destination
        memAbsolutePosition = self._parent.getMemAbsPos(dest)
        return self.formatBinary(wordSize, [(source, regSize), (memAbsolutePosition, 0)])

class AsmLoadLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, source, destination):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = objet Variable ou Litteral (alors stocké comme variable)
        destination = entier
        '''
        assert isinstance(destination,int)
        assert isinstance(source, Variable) or isinstance(source, Litteral)
        self._parent = parent
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand
        self._source = source
        self._destination = destination

    def __str__(self):
        return self._label + "\t" + self._asmCommand + " r" + str(self._destination) + ", " + str(self._source)

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        source = self._source
        dest = self._destination
        memAbsolutePosition = self._parent.getMemAbsPos(source)
        return self.formatBinary(wordSize, [(dest, regSize), (memAbsolutePosition, 0)])

class AsmInputLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand, destination):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        destination = Variable
        '''
        assert isinstance(destination, Variable)
        self._parent = parent
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
    def __init__(self, parent, label, opcode, asmCommand, source):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = int (registre)
        '''
        assert isinstance(source, int)
        self._parent = parent
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
        return self.formatBinary(wordSize, [(source, 0)])

class AsmHaltLine(AsmLine):
    def __init__(self, parent, label, opcode, asmCommand):
        '''
        parent = objet AssembleurContainer parent
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        '''
        self._parent = parent
        self._label = str(label)
        self._opcode = opcode
        self._asmCommand = asmCommand

    def __str__(self):
        return self._label + "\t" + self._asmCommand

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        return self.formatBinary(wordSize, [])

class AsmLitteralLine(AsmLine):
    def __init__(self, parent, litteral):
        '''
        parent = objet AssembleurContainer parent
        litteral = Litteral object
        '''
        assert isinstance(litteral,Litteral)
        self._parent = parent
        self._litteral = litteral

    def __str__(self):
        return str(self._litteral)+"\t"+str(self._litteral.getValue())

    def getBinary(self, wordSize, regSize):
        '''
        regSize = int : nbre de bits pour les registres
        wordSize = int : nbre de bits pour l'ensemble
        '''
        return format(self._litteral.getValue(), '0'+str(wordSize)+'b')

