"""
.. module:: assembleurconainer
:synopsis: définition d'un objet gérant l'ensemble du code assembleur
"""

from typing import Union, Tuple, Optional, List

from primitives.errors import CompilationError, AttributesError
from primitives.litteral import Litteral
from primitives.variable import Variable
from primitives.label import Label

from assembleurlines import AsmLine
from processorengine import ProcessorEngine

class AssembleurContainer:
    """Objet contenant les lignes de code assembleur
    et produisant le code binaire correspondant
    """
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

    def pushStore(self, lineNumber:int, label:Optional[Label], source:int, destination:Variable) -> None:
        """
        Ajoute une commande STORE dans l'assembleur.

        Réserve l'espace mémoire pour la variable.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
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
        asmLine = AsmLine(lineNumber, label, opcode, asmCommand, (source,), memoryItem)
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

    def pushLoad(self, lineNumber:int, label:Optional[Label], source:Union[Variable,Litteral], destination:int) -> None:
        """
        Ajoute une commande LOAD dans l'assembleur.

        Réserve l'espace mémoire pour la source.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
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
        asmLine = AsmLine(lineNumber, label, opcode, asmCommand, (destination,), memoryItem)
        self.__lines.append(asmLine)

    def pushMoveLitteral(self, lineNumber:int, label:Optional[Label], source:Litteral, destination:int) -> None:
        """
        Ajoute une commande MOVE avec littéral dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
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
                self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, (destination,), source))
                return
        self.pushLoad(lineNumber, label, source, destination)

    def pushMove(self, lineNumber:int, label:Optional[Label], source:int, destination:int) -> None:
        """
        Ajoute une commande MOVE dans l'assembleur

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
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
        self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, moveOperands, None))

    def pushUal(self, lineNumber:int, label:Optional[Label], operator:str, destination:int, regOperands:Tuple[int,...], littOperand:Optional[Litteral] = None) -> None:
        """
        Ajoute une commande de calcul UAL dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
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
                self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, regOperands, littOperand))
                return
            raise CompilationError(f"Pas de commande pour {operator} avec litteral dans le modèle de processeur", {"lineNumber": lineNumber})
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == "" or opcode == "":
            raise AttributesError(f"Pas de commande pour {operator} dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, regOperands, None))

    def pushCmp(self, lineNumber:int, label:Optional[Label], operand1:int, operand2:int) -> None:
        """
        Ajoute une commande CMP, comparaison, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
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
        self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, (operand1, operand2), None))

    def pushInput(self, lineNumber:int, label:Optional[Label], destination:Variable) -> None:
        """
        Ajoute une commande INPUT, lecture entrée, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
        :param destination: variable cible
        :type destination: Variable
        """
        assert isinstance(destination,Variable)
        opcode = self.__engine.getOpcode("input")
        asmCommand = self.__engine.getAsmCommand("input")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour input dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, (), destination))

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
        self.__lines.append(AsmLine(lineNumber, None, opcode, asmCommand, (source,), None))

    def pushJump(self, lineNumber:int, label:Optional[Label], cible:Label, operator:Optional[str] = None) -> None:
        """
        Ajoute une commande JUMP, saut conditionnel ou non, dans l'assembleur.

        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :param label: label de l'instruction
        :type label: Optional[Label]
        :param cible: étiquette cible
        :type cible: Label
        :param operator: comparaison parmi <, <=, >=, >, ==, !=. None pour Jump inconditionnel
        :type operator: str / None
        """
        if operator == None:
            operator = "goto"
        assert operator in ("<", "<=", ">", ">=", "==", "!=", "goto")
        opcode = self.__engine.getOpcode(operator)
        asmCommand = self.__engine.getAsmCommand(operator)
        if asmCommand == "" or opcode == "":
            raise AttributesError(f"Pas de commande pour {operator} dans le modèle de processeur.", {"lineNumber": lineNumber})
        self.__lines.append(AsmLine(lineNumber, label, opcode, asmCommand, (), cible))

    def pushHalt(self, label:Optional[Label]) -> None:
        """Ajoute une commande HALT, fin de programme, à l'assembleur.

        :param label: label de l'instruction
        :type label: Optional[Label]
        """
        opcode = self.__engine.getOpcode("halt")
        asmCommand = self.__engine.getAsmCommand("halt")
        if asmCommand == "" or opcode == "":
            raise AttributesError("Pas de commande pour halt dans le modèle de processeur.")
        self.__lines.append(AsmLine(-1, label, opcode, asmCommand, (), None))

    def getBinary(self) -> str:
        """Produit le code binaire correspondant au code assembleur.

        :return: code binaire
        :rtype: str
        """
        binaryList = [self.__formatBinaryLine(item) for item in self.__lines]
        memoryBinary = self.__memoryToBinary()
        return "\n".join(binaryList + memoryBinary)

    def __formatBinaryElement(self, value:int, size:int) -> Optional[str]:
        """Donne la représentation binaire d'un élément de la ligne.

        :param value: valeur à coder en binaire
        :type value: int
        :param size: nombre bits disponibles
        :type size: int
        :return: code binaire de l'item
        :rtype: Optional[str]
        """
        if size <= 0:
            return None
        if value < 0:
            return None

        strItem = format(value, '0'+str(size)+'b')
        if len(strItem) > size:
            return None

        return strItem

    def __formatBinaryLine(self, asmItem:AsmLine) -> str:
        """Calcul le code binaire correspondant à un ligne assembleur

        :return: code binaire
        :rtype: str
        :raises:CompilationError si item à coder ne convient pas
        """
        elements = asmItem.getElementsToCode()
        if len(elements) == 0:
            return ""
        regSize = self.__engine.regBits
        wordSize = self.__engine.dataBits
        binaryCode = ""
        for elem in elements:
            if isinstance(elem, int):
                # codage d'un registre
                binaryElem = self.__formatBinaryElement(elem, regSize)
                if binaryElem is None:
                    raise CompilationError(f"{asmItem} -> Codage de r{elem} impossible !", {"lineNumber":asmItem.lineNumber})
                else:
                    binaryCode += binaryElem
                continue
            if isinstance(elem, Litteral):
                # litteral
                litteralSize = asmItem.getLastOperandSize(wordSize, regSize)
                binaryElem = self.__formatBinaryElement(elem.value, litteralSize)
                if binaryElem is None:
                    raise CompilationError(f"{asmItem} -> Codage de {Litteral.value} impossible !", {"lineNumber":asmItem.lineNumber})
                else:
                    binaryCode += binaryElem
                continue
            if isinstance(elem, Variable):
                # variable
                adresseVariableSize = asmItem.getLastOperandSize(wordSize, regSize)
                adresseToCode = self.getMemAbsPos(elem)
                if isinstance(adresseToCode, int):
                    binaryElem = self.__formatBinaryElement(adresseToCode, adresseVariableSize)
                    if binaryElem is None:
                        raise CompilationError(f"{asmItem} -> Codage de l'adresse {elem}[{adresseToCode}] impossible !", {"lineNumber":asmItem.lineNumber})
                    else:
                        binaryCode += binaryElem
                else:
                    raise CompilationError(f"{asmItem} -> Variable {elem.name} introuvable !", {"lineNumber":asmItem.lineNumber})
                continue
            if isinstance(elem, Label):
                # label
                adresseLabelSize = asmItem.getLastOperandSize(wordSize, regSize)
                adresseToCode = self.getLineLabel(elem)
                if isinstance(adresseToCode, int):
                    binaryElem = self.__formatBinaryElement(adresseToCode, adresseLabelSize)
                    if binaryElem is None:
                        raise CompilationError(f"{asmItem} -> Codage du saut {elem}[{adresseToCode}] impossible !", {"lineNumber":asmItem.lineNumber})
                    else:
                        binaryCode += binaryElem
                else:
                    raise CompilationError(f"{asmItem} -> Label {elem} introuvable !", {"lineNumber":asmItem.lineNumber})
                continue
            binaryCode += elem
        if len(binaryCode) > wordSize:
            raise CompilationError(f"{asmItem} -> {binaryCode} : code binaire trop long !", {"lineNumber":asmItem.lineNumber})
        unusedBits = wordSize - len(binaryCode)
        return binaryCode + "0"*unusedBits

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

    def getMemAbsPos(self, item:Variable) -> Union[int,None]:
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

    def getLineLabel(self, label:Label) -> Union[int,None]:
        """Calcul l'adresse d'une étiquette.

        :param label: étiquette recherchée
        :type label: Label
        :return: adresse de l'étiquette. None si elle n'est pas trouvée.
        :rtype: Union[int,None]
        """
        lineAdresse = 0
        for item in self.__lines:
            if item.label == label:
                return lineAdresse
            lineAdresse += item.getSizeInMemory()
        return None

if __name__=="__main__":
    from processor16bits import Processor16Bits

    engine = Processor16Bits()
    asmCont = AssembleurContainer(engine)
    asmCont.pushMove(0,None, 2,1)
    asmCont.pushMoveLitteral(0,None, Litteral(2),1)
    asmCont.pushUal(0,None, "+",2,(3,), Litteral(19))
    asmCont.pushStore(0,None, 1,Variable("x"))
    asmCont.pushLoad(0,None, Variable("x"),3)
    asmCont.pushInput(0,None, Variable("x"))
    asmCont.pushPrint(0,1)
    asmCont.pushHalt(None)

    print(str(asmCont))
    print()
    print(asmCont.getBinary())
    print()
    print(asmCont.getDecimal())
