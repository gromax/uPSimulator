'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from litteral import Litteral
from variable import Variable
from assembleurlines import *

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
        asmLine = AsmStoreLine(self, "", opcode, asmCommand, source, destination)
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
        asmLine = AsmLoadLine(self, "", opcode, asmCommand, source, destination)
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
                    self.__lines.append(AsmMoveLine(self, "", opcode, asmCommand, source, destination))
                    return
                if self.__engine.bigLitteralIsNextLine():
                    self.__lines.append(AsmMoveLine(self, "", opcode, asmCommand, Litteral(maxSize+1), destination))
                    self.__lines.append(AsmLitteralLine(self, source))
                    return
            self.__pushMemory(source)
            self.pushLoad(source, destination)
            return
        opcode = self.__engine.getOpcode("move")
        asmCommand = self.__engine.getAsmCommand("move")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour move dans le modèle de processeur.")
        self.__lines.append(AsmMoveLine(self, "", opcode, asmCommand, source, destination))

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
                    self.__lines.append(AsmUalLine(self, "", opcode, asmCommand, destination, operands))
                    return
                if self.__engine.bigLitteralIsNextLine():
                    operands = operands[:-1]+(Litteral(maxSize+1),)
                    self.__lines.append(AsmUalLine(self, "", opcode, asmCommand, destination, operands))
                    self.__lines.append(AsmLitteralLine(self, source))
                    return
                raise CompilationError(f"Litteral trop grand pour {operator}")
            raise CompilationError(f"Pas de commande pour {operator} avec litteral dans le modèle de processeur")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == None or opcode == None:
            raise AttributeError(f"Pas de commande pour {operator} dans le modèle de processeur.")
        self.__lines.append(AsmUalLine(self, "", opcode, asmCommand, destination, operands))

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
        self.__lines.append(AsmCmpLine(self, "", opcode, asmCommand, (operand1, operand2)))

    def pushInput(self, destination):
        '''
        destination = Variable
        '''
        assert isinstance(destination,Variable)
        opcode = self.__engine.getOpcode("input")
        asmCommand = self.__engine.getAsmCommand("input")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour input dans le modèle de processeur.")
        self.__lines.append(AsmInputLine(self, "", opcode, asmCommand, destination))

    def pushPrint(self, source):
        '''
        source = int (registre)
        '''
        assert isinstance(source,int)
        opcode = self.__engine.getOpcode("print")
        asmCommand = self.__engine.getAsmCommand("print")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour print dans le modèle de processeur.")
        self.__lines.append(AsmPrintLine(self, "", opcode, asmCommand, source))

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
        self.__lines.append(AsmJumpLine(self, "", opcode, asmCommand, cible))

    def pushHalt(self):
        opcode = self.__engine.getOpcode("halt")
        asmCommand = self.__engine.getAsmCommand("halt")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour halt dans le modèle de processeur.")
        self.__lines.append(AsmHaltLine(self, "", opcode, asmCommand))

    def pushLabel(self, label):
        '''
        label = chaîne de caractère
        '''
        self.__lines.append(AsmLabelLine(self, label))

    def getBinary(self):
        regSize = self.__engine.getRegBits()
        wordSize = self.__engine.getDataBits()
        binaryList = [item.getBinary(wordSize, regSize) for item in self.__lines if not isinstance(item, AsmLabelLine)]
        return "\n".join(binaryList)

    def getAsmSize(self):
        return len([item for item in self.__lines if not isinstance(item, AsmLabelLine)])

    def getMemAbsPos(self,item):
        return [str(var) for var in self.__memoryData].index(str(item)) + self.getAsmSize()

    def __str__(self):
        listStr = [str(item) for item in self.__lines]
        codePart = "\n".join(listStr)
        variablesStr = [str(item) + "\tDATA" for item in self.__memoryData if isinstance(item,Variable)]
        litterauxStr = [str(item) + "\t" + str(item.getValue()) for item in self.__memoryData if isinstance(item,Litteral)]
        return codePart + "\n" + "\n".join(litterauxStr + variablesStr)

    def getLineLabel(self, label):
        index = 0
        for item in self.__lines:
            if item.getLabel() == label:
                return index
            if not isinstance(item, AsmLabelLine):
                index += 1
        return None


