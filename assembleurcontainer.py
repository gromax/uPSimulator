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
        retourne l'item en mémoire
        '''
        isLitteral = False
        if isinstance(item, Litteral):
            itemValue = item.getValue()
            itemName = str(itemValue)
            item = Variable(itemName, itemValue)
            isLitteral = True
        assert isinstance(item, Variable)
        for item_memory in self.__memoryData:
            if str(item_memory) == str(item):
                return item_memory

        # on place les littéraux devant
        if isLitteral:
            self.__memoryData.insert(0,item)
        else:
            self.__memoryData.append(item)
        return item

    def __memoryToBinary(self):
        '''
        les variables donnent une chaîne de 0
        les littéraux donnent un entienr en CA2
        '''
        wordSize = self.__engine.getDataBits()
        return [ item.getBinary(wordSize) for item in self.__memoryData]

    def pushStore(self, lineNumber, source, destination):
        '''
        lineNumber = int = numéro de la ligne d'origine
        source = int (registre)
        destination = objet Variable
        Ajoute une ligne pour le store
        Ajoute la variable à la zone mémoire
        '''
        opcode = self.__engine.getOpcode("store")
        asmCommand = self.__engine.getAsmCommand("store")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour store dans le modèle de processeur.")
        memoryItem = self.__pushMemory(destination)
        asmLine = AsmLine(self, lineNumber, "", opcode, asmCommand, (source, memoryItem))
        self.__lines.append(asmLine)

    def pushLoad(self, lineNumber, source, destination):
        '''
        lineNumber = int = numéro de la ligne d'origine
        destination = int (registre)
        source = objet Variable
        Ajoute une ligne pour le store
        Ajoute la variable à la zone mémoire
        '''
        opcode = self.__engine.getOpcode("load")
        asmCommand = self.__engine.getAsmCommand("load")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour load dans le modèle de processeur.")
        memoryItem = self.__pushMemory(source)
        asmLine = AsmLine(self, lineNumber, "", opcode, asmCommand, (destination, memoryItem))
        self.__lines.append(asmLine)

    def pushMove(self, lineNumber, source, destination):
        '''
        lineNumber = int = numéro de la ligne d'origine
        destination = int (registre)
        source = int (registre) ou Litteral
        '''
        if isinstance(source, Litteral):
            opcode = self.__engine.getLitteralOpcode("move")
            asmCommand = self.__engine.getLitteralAsmCommand("move")
            if opcode != None and asmCommand != None:
                maxSize = self.__engine.getLitteralMaxSizeIn("move")
                if not source.isBetween(0,maxSize):
                    source.setBig()
                moveOperands = (destination, source)
                self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, moveOperands))
                return
            self.pushLoad(lineNumber, source, destination)
            return
        opcode = self.__engine.getOpcode("move")
        asmCommand = self.__engine.getAsmCommand("move")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour move dans le modèle de processeur.")
        moveOperands = (destination, source)
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, moveOperands))

    def pushUal(self, lineNumber, operator, destination, operands):
        '''
        lineNumber = int = numéro de la ligne d'origine
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
        if destination != None:
            operands = (destination,) + operands
        if isinstance(lastOperand, Litteral):
            opcode = self.__engine.getLitteralOpcode(operator)
            asmCommand = self.__engine.getLitteralAsmCommand(operator)
            if opcode != None and asmCommand != None:
                maxSize = self.__engine.getLitteralMaxSizeIn(operator)
                if not lastOperand.isBetween(0,maxSize):
                    if not self.__engine.bigLitteralIsNextLine():
                        raise CompilationError(f"Litteral trop grand pour {operator}")
                    lastOperand.setBig()
                self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, operands))
                return
            raise CompilationError(f"Pas de commande pour {operator} avec litteral dans le modèle de processeur")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == None or opcode == None:
            raise AttributeError(f"Pas de commande pour {operator} dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, operands))

    def pushCmp(self, lineNumber, operand1, operand2):
        '''
        lineNumber = int = numéro de la ligne d'origine
        operand1 et operand2 = int (registre)
        '''
        assert isinstance(operand1,int)
        assert isinstance(operand2,int)
        opcode = self.__engine.getOpcode("cmp")
        asmCommand = self.__engine.getAsmCommand("cmp")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour cmp dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (operand1, operand2)))

    def pushInput(self, lineNumber, destination):
        '''
        lineNumber = int = numéro de la ligne d'origine
        destination = Variable
        '''
        assert isinstance(destination,Variable)
        opcode = self.__engine.getOpcode("input")
        asmCommand = self.__engine.getAsmCommand("input")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour input dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (destination,)))

    def pushPrint(self, lineNumber, source):
        '''
        lineNumber = int = numéro de la ligne d'origine
        source = int (registre)
        '''
        assert isinstance(source,int)
        opcode = self.__engine.getOpcode("print")
        asmCommand = self.__engine.getAsmCommand("print")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour print dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (source,)))

    def pushJump(self, lineNumber, cible, operator = None):
        '''
        lineNumber = int = numéro de la ligne d'origine
        cible = string (label)
        operator = <, <=, >=, >, ==, != ou None pour Jump inconditionnel
        '''
        cible = str(cible)
        if operator == None:
            operator = "goto"
        assert operator in ("<", "<=", ">", ">=", "==", "!=", "goto")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == None or opcode == None:
            raise AttributeError(f"Pas de commande pour {operator} dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (cible,)))

    def pushHalt(self):
        opcode = self.__engine.getOpcode("halt")
        asmCommand = self.__engine.getAsmCommand("halt")
        if asmCommand == None or opcode == None:
            raise AttributeError("Pas de commande pour halt dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, -1, "", opcode, asmCommand, None))

    def pushLabel(self, lineNumber, label):
        '''
        lineNumber = int = numéro de la ligne d'origine
        label = chaîne de caractère
        '''
        self.__lines.append(AsmLine(self, lineNumber, label, "", "", None))

    def getBinary(self):
        regSize = self.__engine.getRegBits()
        wordSize = self.__engine.getDataBits()
        bigLitteralNext = self.__engine.bigLitteralIsNextLine()
        binaryList = [item.getBinary(wordSize, regSize, bigLitteralNext) for item in self.__lines if not item.isEmpty()]
        memoryBinary = self.__memoryToBinary()
        return "\n".join(binaryList + memoryBinary)

    def getDecimal(self):
        binaryLines = self.getBinary().split("\n")
        return [int(item,2) for item in binaryLines]

    def getAsmSize(self):
        regSize = self.__engine.getRegBits()
        wordSize = self.__engine.getDataBits()
        bigLitteralNext = self.__engine.bigLitteralIsNextLine()
        return sum([item.getSizeInMemory(wordSize, regSize, bigLitteralNext) for item in self.__lines])

    def getMemAbsPos(self,item):
        nameList = [str(var) for var in self.__memoryData]
        nameSearched = str(item)
        if nameSearched in nameList:
            return nameList.index(nameSearched) + self.getAsmSize()
        else:
            return None

    def __str__(self):
        listStr = [str(item) for item in self.__lines]
        codePart = "\n".join(listStr)
        memStr = [str(item) + "\t" + str(item.getValue()) for item in self.__memoryData]
        return codePart + "\n" + "\n".join(memStr)

    def getLineLabel(self, label):
        regSize = self.__engine.getRegBits()
        wordSize = self.__engine.getDataBits()
        bigLitteralNext = self.__engine.bigLitteralIsNextLine()
        lineAdresse = 0
        for item in self.__lines:
            if item.getLabel() == label:
                return lineAdresse
            lineAdresse += item.getSizeInMemory(wordSize, regSize, bigLitteralNext)
        return None

if __name__=="__main__":
    from assembleurcontainer import *
    from expressionparser import ExpressionParser
    from processorengine import ProcessorEngine
    EP = ExpressionParser()

    engine = ProcessorEngine()
    AsmCont = AssembleurContainer(engine)
    AsmCont.pushMove(2,1)
    AsmCont.pushMove(Litteral(2),1)
    AsmCont.pushUal("+",2,(3,Litteral(1089)))
    AsmCont.pushStore(1,Variable("x"))
    AsmCont.pushLoad(Variable("x"),3)
    AsmCont.pushInput(Variable("x"))
    AsmCont.pushPrint(1)
    AsmCont.pushHalt()

    print(str(AsmCont))
    print()
    print(AsmCont.getBinary())
    print()
    print(AsmCont.getDecimal())
