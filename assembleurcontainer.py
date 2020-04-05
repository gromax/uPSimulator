'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

from typing import Union, Tuple, Optional, List

from errors import CompilationError, AttributesError
from litteral import Litteral
from variable import Variable
from assembleurlines import AsmLine
from processorengine import ProcessorEngine

class AssembleurContainer:
    __lines:List[AsmLine]
    __memoryData:List[Variable]
    def __init__(self, engine:ProcessorEngine):
        """
        Constructeur

        :param engine: objet modèle de procèsseur
        :type engine: ProcessorEngine
        """
        self.__engine = engine
        self.__lines = []
        self.__memoryData = []

    def __pushMemory(self, item:Union[Variable,Litteral]) -> Variable:
        """
        Réserve un espace mémoire pour une variable ou un littéral

        :param item: item pour lequel réserver une mémoire
        :type item: Litteral / Variable
        :return: variable créée en mémoire
        :rtype: Variable
        """
        isLitteral = False
        if isinstance(item, Litteral):
            itemValue = item.value
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

    def __memoryToBinary(self) -> List[str]:
        """
        Produit le code binaire correspondant à l'intialisation des variables mémoires.

        Les littéraux sont codés en CA2.

        :return: code binaire
        :rtype: List[str]
        """
        wordSize = self.__engine.dataBits
        return [ item.getValueBinary(wordSize) for item in self.__memoryData]

    def pushStore(self, lineNumber:int, source:int, destination:Variable) -> None:
        """
        Ajoute une commande STORE dans l'assembleur.

        Réserve l'espace mémoire pour la variable.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param source: registre source
        :type source: int
        :param destination: variable destination
        :type destination: Variable
        """
        opcode = self.__engine.getOpcode("store")
        asmCommand = self.__engine.getAsmCommand("store")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour store dans le modèle de processeur.", {"lineNumber": lineNumber})
        memoryItem = self.__pushMemory(destination)
        asmLine = AsmLine(self, lineNumber, "", opcode, asmCommand, (source,), memoryItem)
        self.__lines.append(asmLine)

    def getLineNumber(self, indexAsmLine:int) -> int:
        '''index ligne asm -> index ligne origine
        :param indexAsmLine: index ligne assembleur
        :type indexAsmLine: int
        :return: index ligne origine, -1 par défaut
        :rtype: int
        '''
        if indexAsmLine >= len(self.__lines):
            return -1
        return self.__lines[indexAsmLine].lineNumber


    def pushLoad(self, lineNumber:int, source:Union[Variable,Litteral], destination:int) -> None:
        """
        Ajoute une commande LOAD dans l'assembleur.

        Réserve l'espace mémoire pour la source.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param destination: registre destination
        :type destination: int
        :param source: variable ou littéral source
        :type source: Litteral / Variable
        """
        opcode = self.__engine.getOpcode("load")
        asmCommand = self.__engine.getAsmCommand("load")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour load dans le modèle de processeur.", {"lineNumber": lineNumber})
        if not self.__engine.valueFitsInMemory(source.value, False):
            raise CompilationError(f"Valeur {source.value} trop grande pour le modèle de processeur.", {"lineNumber": lineNumber})
        memoryItem = self.__pushMemory(source)
        asmLine = AsmLine(self, lineNumber, "", opcode, asmCommand, (destination,), memoryItem)
        self.__lines.append(asmLine)

    def pushMoveLitteral(self, lineNumber:int, source:Litteral, destination:int) -> None:
        """
        Ajoute une commande MOVE avec littéral dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param destination: registre destination
        :type destination: int
        :param source: littéral source
        :type source: Litteral
        """
        assert isinstance(source, Litteral)
        opcode = self.__engine.getLitteralOpcode("move")
        asmCommand = self.__engine.getLitteralAsmCommand("move")
        if opcode != "" and asmCommand != "":
            maxSize = self.__engine.getLitteralMaxSizeIn("move")
            if source.isBetween(0,maxSize):
                moveOperands = (destination, source)
                self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (destination,), source))
                return
        self.pushLoad(lineNumber, source, destination)

    def pushMove(self, lineNumber:int, source:int, destination:int) -> None:
        """
        Ajoute une commande MOVE dans l'assembleur

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param destination: registre destination
        :type destination: int
        :param source: registre source
        :type source: int
        """
        opcode = self.__engine.getOpcode("move")
        asmCommand = self.__engine.getAsmCommand("move")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour move dans le modèle de processeur.", {"lineNumber": lineNumber})
        moveOperands = (destination, source)
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, moveOperands, None))

    def pushUal(self, lineNumber:int, operator:str, destination:int, regOperands:Tuple[int,...], littOperand:Optional[Litteral] = None) -> None:
        """
        Ajoute une commande de calcul UAL dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param destination: registre destination
        :type destination: int
        :param operator: opérateur
        :type operator: string
        :param regOperands: opérandes de type registre
        :type regOperands: tuple[int]
        :param littOperand: opérande de type littéral
        :type littOperand: Optional[Litteral]
        """
        for ope in regOperands:
            assert isinstance(ope,int)
        if destination !=0 and not self.__engine.ualOutputIsFree():
            raise CompilationError(f"Calcul {operator} stocké dans le registre {destination}.", {"lineNumber": lineNumber})
        if self.__engine.ualOutputIsFree():
            regOperands = (destination,) + regOperands
        if isinstance(littOperand, Litteral):
            opcode = self.__engine.getLitteralOpcode(operator)
            asmCommand = self.__engine.getLitteralAsmCommand(operator)
            if opcode != "" and asmCommand != "":
                maxSize = self.__engine.getLitteralMaxSizeIn(operator)
                if not littOperand.isBetween(0,maxSize):
                    raise CompilationError(f"Litteral trop grand pour {operator}", {"lineNumber": lineNumber})
                self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, regOperands, littOperand))
                return
            raise CompilationError(f"Pas de commande pour {operator} avec litteral dans le modèle de processeur", {"lineNumber": lineNumber})
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == "" or opcode == "":
            raise AttributesError(f"Pas de commande pour {operator} dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, regOperands, None))

    def pushCmp(self, lineNumber:int, operand1:int, operand2:int) -> None:
        """
        Ajoute une commande CMP, comparaison, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param operand1: registre premier opérande
        :type operand1: int
        :param operand2: registre second opérande
        :type operand2: int

        .. note:: Une telle commande doit précéder l'utilisation d'un saut conditionnel.
        """
        assert isinstance(operand1,int)
        assert isinstance(operand2,int)
        opcode = self.__engine.getOpcode("cmp")
        asmCommand = self.__engine.getAsmCommand("cmp")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour cmp dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (operand1, operand2), None))

    def pushInput(self, lineNumber:int, destination:Variable) -> None:
        """
        Ajoute une commande INPUT, lecture entrée, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param destination: variable cible
        :type destination: Variable
        """
        assert isinstance(destination,Variable)
        opcode = self.__engine.getOpcode("input")
        asmCommand = self.__engine.getAsmCommand("input")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour input dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (), destination))

    def pushPrint(self, lineNumber:int, source:int) -> None:
        """
        Ajoute une commande PRINT, affichage à l'écran, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param source: registre dont on doit afficher le contenu
        :type source: int
        """
        assert isinstance(source,int)
        opcode = self.__engine.getOpcode("print")
        asmCommand = self.__engine.getAsmCommand("print")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour print dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (source,), None))

    def pushJump(self, lineNumber:int, cible:str, operator:Optional[str] = None) -> None:
        """
        Ajoute une commande JUMP, saut conditionnel ou non, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param cible: étiquette cible
        :type cible: str
        :param operator: comparaison parmi <, <=, >=, >, ==, !=. None pour Jump inconditionnel
        :type operator: str / None
        """
        cible = str(cible)
        if operator == None:
            operator = "goto"
        assert operator in ("<", "<=", ">", ">=", "==", "!=", "goto")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == "" or opcode == "":
            raise AttributesError(f"Pas de commande pour {operator} dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(self, lineNumber, "", opcode, asmCommand, (), cible))

    def pushHalt(self) -> None:
        """Ajoute une commande HALT, fin de programme, à l'assembleur.
        """
        opcode = self.__engine.getOpcode("halt")
        asmCommand = self.__engine.getAsmCommand("halt")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour halt dans le modèle de processeur.")
        self.__lines.append(AsmLine(self, -1, "", opcode, asmCommand, (), None))

    def pushLabel(self, lineNumber:int, label:str) -> None:
        """Ajoute une ligne vide avec étiquette.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: étiquette
        :type label: str
        """
        self.__lines.append(AsmLine(self, lineNumber, label, "", "", (), None))

    def getBinary(self) -> str:
        """Produit le code binaire correspondant au code assembleur.

        :return: code binaire
        :rtype: str
        """
        wordSize = self.__engine.dataBits
        regSize = self.__engine.regBits
        binaryList = [item.getBinary(wordSize, regSize) for item in self.__lines if not item.isEmpty()]
        memoryBinary = self.__memoryToBinary()
        return "\n".join(binaryList + memoryBinary)

    def getDecimal(self) -> List[int]:
        """Produit une version int du code binaire.

        :return: code assembleur sous forme d'une liste d'entier
        :rtype: List[int]
        """
        binaryLines = self.getBinary().split("\n")
        return [int(item,2) for item in binaryLines]

    def getAsmSize(self) -> int:
        """Calcule le nombre de lignes instructions.

        :return: nombre de lignes
        :rtype: int
        """
        return sum([item.getSizeInMemory() for item in self.__lines])

    def getMemAbsPos(self,item:Variable) -> Union[int,None]:
        """Calcule l'adresse mémoire d'une variable.

        :param item: variable recherchée
        :type item: Variable
        :return: adresse de la mémoire. None si elle n'est pas trouvée.
        :rtype: Union[int,None]
        """
        nameList = [str(var) for var in self.__memoryData]
        nameSearched = str(item)
        if nameSearched in nameList:
            return nameList.index(nameSearched) + self.getAsmSize()
        else:
            return None

    def __str__(self) -> str:
        """Transtypage -> str

        Fournit le code assembleur.

        :return: code assembleur
        :rtype: str
        """

        listStr = [str(item) for item in self.__lines]
        codePart = "\n".join(listStr)
        memStr = [str(item) + "\t" + str(item.value) for item in self.__memoryData]
        return codePart + "\n" + "\n".join(memStr)

    def getLineLabel(self, label:str) -> Union[int,None]:
        """Calcul l'adresse d'une étiquette.

        :param label: étiquette recherchée
        :type label: str
        :return: adresse de l'étiquette. None si elle n'est pas trouvée.
        :rtype: Union[int,None]
        """
        lineAdresse = 0
        for item in self.__lines:
            if item.getLabel() == label:
                return lineAdresse
            lineAdresse += item.getSizeInMemory()
        return None

if __name__=="__main__":
    from assembleurcontainer import *
    from expressionparser import ExpressionParser
    from processorengine import ProcessorEngine
    EP = ExpressionParser()

    engine = ProcessorEngine()
    AsmCont = AssembleurContainer(engine)
    AsmCont.pushMove(0,2,1)
    AsmCont.pushMoveLitteral(0,Litteral(2),1)
    AsmCont.pushUal(0,"+",2,(3,), Litteral(19))
    AsmCont.pushStore(0,1,Variable("x"))
    AsmCont.pushLoad(0,Variable("x"),3)
    AsmCont.pushInput(0,Variable("x"))
    AsmCont.pushPrint(0,1)
    AsmCont.pushHalt()

    print(str(AsmCont))
    print()
    print(AsmCont.getBinary())
    print()
    print(AsmCont.getDecimal())
