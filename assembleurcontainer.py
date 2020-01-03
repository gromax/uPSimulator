'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from litteral import Litteral
from variable import Variable


class AsmLine:
    pass

class AsmLabelLine(AsmLine):
    def __init__(self, label):
        '''
        label = chaîne de caractère
        '''
        self.__label = label
    def __str__(self):
        return self.__label

class AsmJumpLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, cible):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        cible = string (label)
        '''
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__cible = cible
    def __str__(self):
        return self.__label + "\t" + self.__asmCommand + " " + str(self.__cible)


class AsmCmpLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, operands):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        operands = tuple de 2 opérandes
        '''
        assert len(operands) == 2
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__operands = operands
    def __str__(self):
        strOperands = ["r"+str(ope) for ope in self.__operands]
        return self.__label+"\t"+self.__asmCommand+" "+", ".join(strOperands)

class AsmUalLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, destination, operands):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        destination = int (registre) ou None si pas nécessaire
        operands = tuple non vide avec les opérandes, la dernière pouvant être un Litteral
        '''
        assert len(operands) != 0
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__destination = destination
        self.__operands = operands
    def __str__(self):
        lastOperand = self.__operands[-1]
        if isinstance(lastOperand, Litteral):
            strLastOperand = str(lastOperand)
        else:
            strLastOperand = "r"+str(lastOperand)
        strOperands = ["r"+str(ope) for ope in self.__operands[:-1]]
        strOperands.append(strLastOperand)
        if self.__destination == None:
            return self.__label+"\t"+self.__asmCommand+" "+", ".join(strOperands)
        return self.__label+"\t"+self.__asmCommand+" r"+str(self.__destination)+", "+", ".join(strOperands)

class AsmMoveLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, source, destination):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = entier (registre) ou Litteral
        destination = entier (registre)
        '''
        assert isinstance(source,int) or isinstance(source,Litteral)
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__source = source
        self.__destination = destination

    def __str__(self):
        if isinstance(self.__source, Litteral):
            return self.__label + "\t" + self.__asmCommand + " r" + str(self.__destination) + ", " + str(self.__source)
        return self.__label + "\t" + self.__asmCommand + " r" + str(self.__destination) + ", r"+str(self.__source)

class AsmStoreLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, source, destination):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = entier
        destination = Variable
        '''
        assert isinstance(source,int)
        assert isinstance(destination, Variable)
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__source = source
        self.__destination = destination

    def __str__(self):
        return self.__label + "\t" + self.__asmCommand + " r" + str(self.__source) + ", " + str(self.__destination)

class AsmLoadLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, source, destination):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = objet Variable ou Litteral (alors stocké comme variable)
        destination = entier
        '''
        assert isinstance(destination,int)
        assert isinstance(source, Variable) or isinstance(source, Litteral)
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__source = source
        self.__destination = destination

    def __str__(self):
        return self.__label + "\t" + self.__asmCommand + " r" + str(self.__destination) + ", " + str(self.__source)

class AsmInputLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, destination):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        destination = Variable
        '''
        assert isinstance(destination, Variable)
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__destination = destination

    def __str__(self):
        return self.__label+"\t" + self.__asmCommand+" " + str(self.__destination)

class AsmPrintLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, source):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = int (registre)
        '''
        assert isinstance(source, int)
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__source = source

    def __str__(self):
        return self.__label+"\t" + self.__asmCommand+" r" + str(self.__source)

class AsmHaltLine(AsmLine):
    def __init__(self, label, opcode, asmCommand):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        '''
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand

    def __str__(self):
        return self.__label + "\t" + self.__asmCommand

class AsmLitteralLine(AsmLine):
    def __init__(self, litteral):
        '''
        litteral = Litteral object
        '''
        assert isinstance(litteral,Litteral)
        self.__litteral = litteral

    def __str__(self):
        return str(self.__litteral)+"\t"+str(self.__litteral.getValue())


class AssembleurContainer:
    def __init__(self, engine):
        '''
        engine = ProcessorEngine
        '''
        self.__engine = engine
        self.__lines = []
        self.__memoryData = []

    def __pushMemory(self, item):
        '''
        item = Variable ou Litteral
        ajoute si nécessaire l'item à la liste
        '''
        assert isinstance(item,Variable) or isinstance(item,Litteral)
        for item in self.__memoryData:
            if str(item) == str(item):
                return
        self.__memoryData.append(item)

    def pushStore(self, source, destination):
        '''
        source = int (registre)
        destination = objet Variable
        Ajoute une ligne pour le store
        Ajoute la variable à la zone mémoire
        '''
        opcode = self.__engine.getOpcode("store")
        asmCommand = self.__engine.getAsmCommand("store")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour store dans le modèle de processeur.")
        asmLine = AsmStoreLine("", opcode, asmCommand, source, destination)
        self.__lines.append(asmLine)
        self.__pushMemory(destination)

    def pushLoad(self, source, destination):
        '''
        destination = int (registre)
        source = objet Variable
        Ajoute une ligne pour le store
        Ajoute la variable à la zone mémoire
        '''
        opcode = self.__engine.getOpcode("load")
        asmCommand = self.__engine.getAsmCommand("load")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour load dans le modèle de processeur.")
        asmLine = AsmLoadLine("", opcode, asmCommand, source, destination)
        self.__lines.append(asmLine)
        self.__pushMemory(source)

    def pushMove(self, source, destination):
        '''
        destination = int (registre)
        source = int (registre) ou Litteral
        '''
        if isinstance(source, Litteral):
            littValue = source.getValue()
            opcode = self.__engine.getOpcode("move_l")
            asmCommand = self.__engine.getAsmCommand("move_l")
            if opcode != None and asmCommand != None:
                maxSize = self.__engine.getLitteralMaxSizeIn("move_l")
                if littValue <= maxSize:
                    self.__lines.append(AsmMoveLine("", opcode, asmCommand, source, destination))
                    return
                if self.__engine.bigLitteralIsNextLine():
                    self.__lines.append(AsmMoveLine("", opcode, asmCommand, Litteral(maxSize+1), destination))
                    self.__lines.append(AsmLitteralLine(source))
                    return
            self.__pushMemory(source)
            self.pushLoad(source, destination)
            return
        opcode = self.__engine.getOpcode("move")
        asmCommand = self.__engine.getAsmCommand("move")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour move dans le modèle de processeur.")
        self.__lines.append(AsmMoveLine("", opcode, asmCommand, source, destination))

    def pushUal(self, operator, destination, operands):
        '''
        destination = int (registre)
        operator = string, décrit l'opérateur
        operands = tuple non vide avec int (registre) et éventuellement pour le dernier, litteral
        '''
        assert len(operands) > 0
        for ope in operands[:-1]:
            assert isinstance(ope,int)
        lastOperand = operands[-1]
        if destination !=0 and not self.__engine.ualOutputIsFree():
            raise CompilationError(f"Calcul {operator} stocké dans le registre {destination}.")
        if not self.__engine.ualOutputIsFree():
            destination = None
        if isinstance(lastOperand, Litteral):
            littValue = lastOperand.getValue()
            opcode = self.__engine.getOpcode(operator+"_l")
            asmCommand = self.__engine.getAsmCommand(operator+"_l")
            if opcode != None and asmCommand != None:
                maxSize = self.__engine.getLitteralMaxSizeIn(operator+"_l")
                if littValue <= maxSize:
                    self.__lines.append(AsmUalLine("", opcode, asmCommand, destination, operands))
                    return
                if self.__engine.bigLitteralIsNextLine():
                    operands = operands[:-1]+(Litteral(maxSize+1),)
                    self.__lines.append(AsmUalLine("", opcode, asmCommand, destination, operands))
                    self.__lines.append(AsmLitteralLine(source))
                    return
                raise CompilationError(f"Litteral trop grand pour {operator}")
            raise CompilationError(f"Pas de commande pour {operator} avec litteral dans le modèle de processeur")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == None or opcode == None:
            raise AttributeError(f"Pas de commande pour {operator} dans le modèle de processeur.")
        self.__lines.append(AsmUalLine("", opcode, asmCommand, destination, operands))

    def pushCmp(self, operand1, operand2):
        '''
        operand1 et operand2 = int (registre)
        '''
        assert isinstance(operand1,int)
        assert isinstance(operand2,int)
        opcode = self.__engine.getOpcode("cmp")
        asmCommand = self.__engine.getAsmCommand("cmp")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour cmp dans le modèle de processeur.")
        self.__lines.append(AsmCmpLine("", opcode, asmCommand, (operand1, operand2)))

    def pushInput(self, destination):
        '''
        destination = Variable
        '''
        assert isinstance(destination,Variable)
        opcode = self.__engine.getOpcode("input")
        asmCommand = self.__engine.getAsmCommand("input")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour input dans le modèle de processeur.")
        self.__lines.append(AsmInputLine("", opcode, asmCommand, destination))

    def pushPrint(self, source):
        '''
        source = int (registre)
        '''
        assert isinstance(source,int)
        opcode = self.__engine.getOpcode("print")
        asmCommand = self.__engine.getAsmCommand("print")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour print dans le modèle de processeur.")
        self.__lines.append(AsmPrintLine("", opcode, asmCommand, source))

    def pushJump(self, cible, operator = None):
        '''
        cible = string (label)
        operator = <, <=, >=, >, ==, != ou None pour Jump inconditionnel
        '''
        if operator == None:
            operator = "goto"
        assert operator in ("<", "<=", ">", ">=", "==", "!=", "goto")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == None or opcode == None:
            raise AttributeError(f"Pas de commande pour {operator} dans le modèle de processeur.")
        self.__lines.append(AsmJumpLine("", opcode, asmCommand, cible))

    def pushHalt(self):
        opcode = self.__engine.getOpcode("halt")
        asmCommand = self.__engine.getAsmCommand("halt")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour halt dans le modèle de processeur.")
        self.__lines.append(AsmHaltLine("", opcode, asmCommand))

    def pushLabel(self, label):
        '''
        label = chaîne de caractère
        '''
        self.__lines.append(AsmLabelLine(label))

    def getBinary(self):
        binaryList = [item.getBinary() for item in self.__lines]
        return "\n".join(binaryList)

    def __str__(self):
        listStr = [str(item) for item in self.__lines]
        codePart = "\n".join(listStr)
        variablesStr = [str(item) + "\tDATA" for item in self.__memoryData if isinstance(item,Variable)]
        litterauxStr = [str(item) + "\t" + str(item.getValue()) for item in self.__memoryData if isinstance(item,Litteral)]
        return codePart + "\n" + "\n".join(litterauxStr + variablesStr)
