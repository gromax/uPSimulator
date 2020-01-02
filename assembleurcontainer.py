'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from litteral import Litteral
from variable import Variable


class AsmLine:
    pass

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
            return self.__label+"\t"+self.__asmCommand+" r"+str(self.__destination)+", "+str(self.__source)
        return self.__label+"\t"+self.__asmCommand+" r"+str(self.__destination)+", r"+str(self.__source)

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
        return self.__label+"\t"+self.__asmCommand+" r"+str(source)+", "+str(self.__destination)

class AsmLoadLine(AsmLine):
    def __init__(self, label, opcode, asmCommand, source, destination):
        '''
        label = chaîne de caractère
        opcode = chaine de caractère
        asmCommand = chaine de caractère
        source = objet Variable
        destination = entier
        '''
        assert isinstance(destination,int)
        assert isinstance(source, Variable)
        self.__label = label
        self.__opcode = opcode
        self.__asmCommand = asmCommand
        self.__source = source
        self.__destination = destination

    def __str__(self):
        return self.__label+"\t"+self.__asmCommand+" r"+str(self.__destination)+", "+str(self.__source)


class AsmLitteralLine(AsmLine):
    def __init__(self, litteral):
        '''
        litteral = Literral object
        '''
        assert isinstance(litteral,Litteral)
        self.__litteral = litteral

    def __str__(self):
        return str(self.__litteral)+"\t"+str(self.__litteral.getValue())


class AssembleurLine:
    __label = ""
    __command = ""
    __opcode = ""
    __lineNumber = 0
    __binary = "?"
    __isLitteral = False
    __isData = False
    def __init__(self, attributes):
        if "label" in attributes:
            self.__label = attributes["label"]
        if "command" in attributes:
            self.__command = attributes["command"]
            assert "opcode" in attributes
            self.__opcode = attributes["opcode"]
        if "operands" in attributes:
            self.__operands = attributes["operands"]
        else:
            self.__operands = []
        if "lineNumber" in attributes:
            self.__lineNumber = attributes["lineNumber"]
        if "binary" in attributes:
            self.__binary = attributes["binary"]
        if "litteral" in attributes:
            self.__isLitteral = True
            self.__litteral = attributes["litteral"]
        if "data" in attributes:
            self.__isData = True
            self.__data = attributes["data"]

    def __str__(self):
        if self.__isLitteral:
            return "LITT\t"+str(self.__litteral)
        if self.__isData:
            return "DATA\t"+str(self.__data)
        opeStr = [str(op) for op in self.__operands]
        return self.__label+"\t "+self.__command+" "+", ".join(opeStr)

    def getBinary(self):
        return self.__binary

class AssembleurContainer:
    def __init__(self):
        self.__lines = []
        self.__variables = []
        self.__tempMem = []

    def __pushVariable(self, variable):
        '''
        variable = Variable
        ajoute si nécessaire la variable à la liste
        '''
        for itemVariable in self.__variables:
            if str(itemVariable) == str(variable):
                return
        self.__variables.append(variable)

    def pushStore(self, engine, source, destination):
        '''
        engine = ProcessorEngine
        source = int (registre)
        destination = objet Variable
        Ajoute une ligne pour le store
        Ajoute la variable à la zone mémoire
        '''
        opcode = engine.getOpcode("store")
        asmCommand = engine.getAsmCommand("store")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour store dans le modèle de processeur.")
        asmLine = AsmStoreLine("", opcode, asmCommand, source, destination)
        self.__lines.append(asmLine)
        self.__pushVariable(destination)

    def pushLoad(self, engine, source, destination):
        '''
        engine = ProcessorEngine
        destination = int (registre)
        source = objet Variable
        Ajoute une ligne pour le store
        Ajoute la variable à la zone mémoire
        '''
        opcode = engine.getOpcode("load")
        asmCommand = engine.getAsmCommand("load")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour load dans le modèle de processeur.")
        asmLine = AsmLoadLine("", opcode, asmCommand, source, destination)
        self.__lines.append(asmLine)
        self.__pushVariable(source)

    def pushMove(self, engine, source, destination):
        '''
        engine = ProcessorEngine
        destination = int (registre)
        source = int (registre) ou Litteral
        '''
        if isinstance(source, Litteral):
            littValue = source.getValue()
            opcode = engine.getOpcode("move_l")
            asmCommand = engine.getAsmCommand("move_l")
            if opcode != None and asmCommand != None:
                maxSize = engine.getLitteralMaxSizeIn("move_l")
                if littValue <= maxSize:
                    self.__lines.append(AsmMoveLine("", opcode, asmCommand, source, destination))
                    return
                if engine.bigLitteralIsNextLine():
                    self.__lines.append(AsmMoveLine("", opcode, asmCommand, Litteral(maxSize+1), destination))
                    self.__lines.append(AsmLitteralLine(source))
                    return
            nameForNewVariable = str(littValue)
            variable = Variable(nameForNewVariable, littValue)
            self.__pushVariable(variable)
            self.pushLoad(engine, destination, variable)
            return
        opcode = engine.getOpcode("move")
        asmCommand = engine.getAsmCommand("move")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour move dans le modèle de processeur.")
        self.__lines.append(AsmMoveLine("", opcode, asmCommand, source, destination))

    def pushUal(self, engine, operator, destination, operands):
        '''
        engine = ProcessorEngine
        destination = int (registre)
        operator = string, décrit l'opérateur
        operands = tuple non vide avec int (registre) et éventuellement pour le dernier, litteral
        '''
        assert len(operands) > 0
        for ope in operands[:-1]:
            assert isinstance(ope,int)
        lastOperand = operands[-1]
        if destination !=0 and not engine.ualOutputIsFree():
            raise CompilationError(f"Calcul {operator} stocké dans le registre {destination}.")
        if not engine.ualOutputIsFree():
            destination = None
        if isinstance(lastOperand, Litteral):
            littValue = lastOperand.getValue()
            opcode = engine.getOpcode(operator+"_l")
            asmCommand = engine.getAsmCommand(operator+"_l")
            if opcode != None and asmCommand != None:
                maxSize = engine.getLitteralMaxSizeIn(operator+"_l")
                if littValue <= maxSize:
                    self.__lines.append(AsmUalLine("", opcode, asmCommand, destination, operands))
                    return
                if engine.bigLitteralIsNextLine():
                    operands = operands[:-1]+(Litteral(maxSize+1),)
                    self.__lines.append(AsmUalLine("", opcode, asmCommand, destination, operands))
                    self.__lines.append(AsmLitteralLine(source))
                    return
                raise CompilationError(f"Litteral trop grand pour {operator}")
            raise CompilationError(f"Pas de commande pour {operator} avec litteral dans le modèle de processeur")
        opcode = engine.getOpcode(operator)
        asmCommand = engine.getAsmCommand(operator)
        if asmCommand == None or opcode == None:
            raise AttributeError(f"Pas de commande pour {operator} dans le modèle de processeur.")
        self.__lines.append(AsmUalLine("", opcode, asmCommand, destination, operands))

    def pushCmp(self, engine, operands):
        '''
        engine = ProcessorEngine
        destination = int (registre)
        operator = string, décrit l'opérateur
        operands = tuple non vide avec int (registre) et éventuellement pour le dernier, litteral
        '''
        assert len(operands) == 2
        for ope in operands:
            assert isinstance(ope,int)
        opcode = engine.getOpcode("cmp")
        asmCommand = engine.getAsmCommand("cmp")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour cmp dans le modèle de processeur.")
        self.__lines.append(AsmCmpLine("", opcode, asmCommand, operands))


    def getBinary(self):
        binaryList = [item.getBinary() for item in self.__lines]
        return "\n".join(binaryList)

    def __str__(self):
        listStr = [str(item) for item in self.__lines]
        return "\n".join(listStr)

