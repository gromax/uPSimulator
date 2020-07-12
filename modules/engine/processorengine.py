"""
.. module:: processorengine
   :synopsis: classe définissant les attributs d'un modèle de processeur et fournissant les informations utiles aux outils de compilation
"""

from typing import Union, List, Dict, Optional, Tuple, Sequence, Any
from abc import ABC, ABCMeta, abstractmethod

from modules.errors import CompilationError
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.primitives.operators import Operator, Operators
from modules.primitives.actionsfifo import ActionsFIFO, ActionType
from modules.engine.asmgenerator import AsmGenerator




class ProcessorEngine(metaclass=ABCMeta):
    _name                  :str
    _register_address_bits :int
    _data_bits             :int
    _freeUalOutput         :bool
    
    _asmGenerators       : List[AsmGenerator]
    _comparaisonOperators: List[Operator]
    _litteralDomain      :Tuple[int, int]

    def __init__(self):
        """Constructeur

        :param name: nom du modèle de processeur utilisé
        :type name: str
        """
        if self.ualOutputIsFree():
            destReg = 1
        else:
            destReg = 0
        self.__opNumber = {
            "neg":  1 + destReg,
            "move": 2,
            "+":    2 + destReg,
            "-":    2 + destReg,
            "*":    2 + destReg,
            "/":    2 + destReg,
            "%":    2 + destReg,
            "&":    2 + destReg,
            "|":    2 + destReg,
            "^":    2 + destReg,
            "~":    1 + destReg,
        }

    @property
    def name(self):
        return self._name

    def registersNumber(self) -> int:
        """Calcul le nombre de registres considérant l'adressage disponible

        :return: nombre de registre
        :rtype: int
        """
        return 2**self._register_address_bits

    def ualOutputIsFree(self) -> bool:
        """Accesseur

        :return: Vrai si on peut choisir le registre de sortie de l'UAL
        :rtype: bool
        """
        return self._freeUalOutput
    '''
    def getOpcode(self, operator:Operator) -> str:
        """Renvoie l'opcode de la commande demandée. ``''`` si introuvable.

        :param operator: nom de la commande
        :type operator: Operator
        :return: opcode sous forme binaire
        :rtype: str
        """

        if not operator in self._commands:
            return ""
        itemAttribute = self._commands[operator]
        return itemAttribute["opcode"]


    def getLitteralOpcode(self, operator:Operator) -> str:
        """Renvoie l'opcode de la commande demandée dans sa version acceptant un littéral. ``''`` si introuvable.

        :param operator: nom de la commande
        :type operator: Operator
        :return: opcode sous forme binaire
        :rtype: str
        """

        if not operator in self._litteralsCommands:
            return ""
        itemAttribute = self._litteralsCommands[operator]
        return itemAttribute["opcode"]
    '''

    def litteralOperatorAvailable(self, operator:Operator, litteral:Litteral) -> bool:
        """Teste si la commande peut s'éxécuter dans une version acceptant un littéral, avec ce littéral en particulier. Il faut que la commande accepte les littéraux et que le codage de ce littéral soit possible dans l'espace laissé par cette commande.

        :param operator: commande à utiliser
        :type operator: Operator
        :param litteral: littéral à utiliser
        :type litteral: Litteral
        :return: vrai si la commande est utilisable avec ce littéral
        :rtype: bool
        """
        # pas de littéral par défaut
        return False

    '''
    def instructionDecode(self, binary:Union[int,str]) -> Tuple[str, Sequence[int], int, int]:
        """Pour une instruction, fait le décodage en renvoyant le descriptif commande, les opérandes registres et un éventuel opérande non registre

        :param binary: code binaire
        :type binary: int ou str
        :result: tuple contenant la commande, les opérandes registres et l'éventuel opérande spéciale (adresse ou littéral), -1 si pas de spéciale, taille en bits de l'éventuel littéral.
        :rtype: Tuple[str, Tuple[int], int, int]

        """
        if isinstance(binary, int):
            strBinary = format(binary, '0'+str(self._data_bits)+'b')
        else:
            strBinary = binary
        for name, attr in self._commands.items():
            opcode = attr["opcode"]
            if strBinary[:len(opcode)] == opcode:
                opeBinary = strBinary[len(opcode):]
                if name == "halt":
                    return ("halt",(),-1, 0)
                if name == "nop":
                    return ("nop", (), -1, 0)
                if name in ("goto", "!=", "==", "<", "<=", ">=", ">", "input"):
                    cible = int(opeBinary,2)
                    return (name, (), cible, len(opeBinary))
                if name in ("store", "load"):
                    reg = int(opeBinary[:self._register_address_bits],2)
                    strCible = opeBinary[self._register_address_bits:]
                    cible = int(strCible,2)
                    return (name, (reg,), cible, len(strCible))
                if name in ("cmp", "move"):
                    reg1 = int(opeBinary[:self._register_address_bits],2)
                    reg2 = int(opeBinary[self._register_address_bits:2*self._register_address_bits],2)
                    return (name, (reg1, reg2), -1, 0)
                if name == "print":
                    reg = int(opeBinary[:self._register_address_bits],2)
                    return ("print", (reg,), -1, 0)
                opNumber = self.__opNumber[name]
                regs = tuple([ int(opeBinary[self._register_address_bits*i:self._register_address_bits*(i+1)],2) for i in range(opNumber)])
                if not self.ualOutputIsFree():
                    regs = (0,) + regs
                return (name, regs, -1, 0)
        for name, attr in self._litteralsCommands.items():
            opcode = attr["opcode"]
            if strBinary[:len(opcode)] == opcode:
                opeBinary = strBinary[len(opcode):]
                if name == "move":
                    reg = int(opeBinary[:self._register_address_bits],2)
                    strLitt = opeBinary[self._register_address_bits:]
                    litt = int(strLitt,2)
                    return ("move", (reg,), litt, len(strLitt))
                opNumber = self.__opNumber[name]
                regs = tuple([ int(opeBinary[self._register_address_bits*i:self._register_address_bits*(i+1)],2) for i in range(opNumber-1)])
                strLitteral = opeBinary[self._register_address_bits*opNumber:]
                litt = int(strLitteral,2)
                sizeLitt = len(strLitteral)
                if not self.ualOutputIsFree():
                    regs = (0,) + regs
                return (name, regs, litt, sizeLitt)
        # par défaut, retour halt
        return ("halt",(),-1, 0)
    '''

    @property
    def litteralDomain(self) -> Tuple[int, int]:
        return self._litteralDomain

    def valueFitsInMemory(self, value:int, posValue:bool) -> bool:
        """Teste si une valeur a une valeur qui pourra être codée en mémoire

        :param value: valeur à tester
        :type value: int
        :param posValue: la valeur doit être codée en nombre positif
        :type posValue: bool
        :return: la valeur peut être codée en mémoire
        :rtype: bool
        """
        nb = self._data_bits
        if posValue:
            # peut aller de 0 à 2^nb - 1
            return 0 <= value < 2**nb
        # peut aller de -2^(nb-1) à 2^(nb-1)-1
        if value >=0:
            return value < 2**(nb - 1)
        return value >= 2**(nb - 1)

    def getComparaisonSymbolsAvailables(self) -> List[Operator]:
        """Accesseur

        :return: liste des symboles de comparaison disponibles avec ce modèle de processeur
        :rtype: list[Operator]
        """

        return [item for item in self._comparaisonOperators if item.isComparaison]

    @property
    def regBits(self) -> int:
        """Accesseur

        :return: nombre de bits utilisés pour l'encodage de l'adresse d'un registre
        :rtype: int
        """
        return self._register_address_bits

    @property
    def dataBits(self) -> int:
        """Accesseur

        :return: nombre de bits utilisés pour l'encodage d'une donnée en mémoire
        :rtype: int
        """
        return self._data_bits
    
    # fonctions -> ASM
    def _operatorToAsm(self, operator:Operator, operands:List[ActionType]) -> List[str]:
        """
        :param operator: Opérateur en cours
        :type operator: Operator 
        :param operands: opérandes de l'opération en cours
        :type operands: List[ActionType]
        :return: code asm
        :rtype: List[str]
        :raise: CompilationError
        """
        for asmGen in self._asmGenerators:
            if asmGen.operator != operator or not asmGen.sastifyConditions(operands):
                continue
            return asmGen.asm(operands)
        strOperands = ", ".join([str(it) for it in operands])
        raise CompilationError("Aucun opérateur asm disponible pour la séquence : {} -> [{}]".format(strOperands, operator))

    def _actionToAsm(self, fifo:ActionsFIFO) -> List[str]:
        """
        :param fifo: file des actions produite par la compilation
        :type fifo: ActionsFIFO
        :return: code asm
        :rtyp: List[str]
        :raises: CompilationError
        """

        lines: List[str] = []
        currentActionItems:List[ActionType] = []
        while not fifo.empty:
            lastItem = fifo.pop()
            if (not isinstance(lastItem, Operator)) or lastItem.isComparaison:
                currentActionItems.append(lastItem)
                continue
            lines.extend(self._operatorToAsm(lastItem, currentActionItems))
            currentActionItems = []

        if len(currentActionItems) > 0:
            raise CompilationError("La séquence devrait terminer par un opérateur.", {"lineNumber":fifo.lineNumber})

        return lines

    def _getVariablesStrList(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]]) -> List[str]:
        """
        :param fifos: file d'actions
        :type fifos: Union[ActionsFIFO, List[ActionsFIFO]]
        :return: liste des noms de variables
        :rtype: List[str]
        """
        if isinstance(fifos, ActionsFIFO):
            return fifos.getVariablesStrList()
        variablesList:List[str] = []
        for fifo in fifos:
            variablesList = fifo.getVariablesStrList(variablesList)
        return variablesList

    def _getVariablesBinary(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]]) -> List[str]:
        """
        :param fifos: file d'actions
        :type fifos: Union[ActionsFIFO, List[ActionsFIFO]]
        :return: liste des noms de variables
        :rtype: List[str]
        """
        variablesList = self._getVariablesStrList(fifos)
        return [Variable.binary(name, self.dataBits) for name in variablesList]

    def getAsm(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]], withVariables:bool=False) -> str:
        """
        :param fifos: file des actions produite par la compilation
        :type fifos: ActionsFIFO
        :param withVariables: Faut-il joindre les variables au code asm
        :type withVariables: bool
        :return: code asm
        :rtype: str
        :raises: CompilationError
        """
        if isinstance(fifos, ActionsFIFO):
            fifoAsmlines = self._actionToAsm(fifos.clone())
            outAsm = "\n".join(fifos.prependStrLabel(fifoAsmlines))
        else:
            listFifoAsmLines = ["\n".join(fifo.prependStrLabel(self._actionToAsm(fifo.clone()))) for fifo in fifos]
            outAsm = "\n".join(listFifoAsmLines)
        if not withVariables:
            return outAsm
        variablesAsm = "\n".join([Variable.asm(name) for name in self._getVariablesStrList(fifos)])
        return "\n".join([outAsm, variablesAsm])
        
    # Fonction -> code
    def _getAdresses(self, fifos:List[ActionsFIFO]) -> Dict[str,int]:
        """
        :param fifos: file des actions produite par la compilation
        :type fifos: ActionsFIFO
        :param withVariables: Faut-il joindre les variables au code asm
        :type withVariables: bool
        :return: liste des labels et variables avec numéro de ligne dans le code
        :rtyp: Dict[str,int]
        """
        # il faut identifier les numéros de ligne qui accueilleront les variables et les labels
        variablesListWithoutLine = self._getVariablesStrList(fifos)
        addressList:Dict[str,int] = {}
        lineCount = 0
        for act in fifos:
            if not act.label is None:
                addressList[str(act.label)] = lineCount
            asmLines = self._actionToAsm(act.clone())
            lineCount += len(asmLines)
        for v in variablesListWithoutLine:
            addressList[v] = lineCount
            lineCount += 1
        return addressList

    def _operatorToBinary(self, operator:Operator, operands:List[ActionType], addressList:Dict[str,int]) -> List[str]:
        """
        :param operator: Opérateur en cours
        :type operator: Operator 
        :param operands: opérandes de l'opération en cours
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[str,int]
        :return: code binaire
        :rtype: List[str]
        :raise: CompilationError
        """
        for asmGen in self._asmGenerators:
            if asmGen.operator != operator or not asmGen.sastifyConditions(operands):
                continue
            return asmGen.binary(operands,addressList)
        strOperands = ", ".join([str(it) for it in operands])
        raise CompilationError("Aucun opérateur asm disponible pour la séquence : {} -> [{}]".format(strOperands, operator))

    def _actionToBinary(self, fifo:ActionsFIFO, addressList:Dict[str,int]) -> List[str]:
        """
        :param fifo: file des actions produite par la compilation
        :type fifo: ActionsFIFO
        :param addressList: adresses de variables et labels
        :type addressList: Dict[str,int]
        :return: code binaire
        :rtyp: List[str]
        """

        lines: List[str] = []
        currentActionItems:List[ActionType] = []
        while not fifo.empty:
            lastItem = fifo.pop()
            if (not isinstance(lastItem, Operator)) or lastItem.isComparaison:
                currentActionItems.append(lastItem)
                continue
            lines.extend(self._operatorToBinary(lastItem, currentActionItems, addressList))
            currentActionItems = []

        if len(currentActionItems) > 0:
            raise CompilationError("La séquence devrait terminer par un opérateur.", {"lineNumber":fifo.lineNumber})

        return lines


    def getBinary(self, fifos:List[ActionsFIFO]) -> List[str]:
        """
        :param fifos: file des actions produite par la compilation
        :type fifos: List[ActionsFIFO]
        :param withVariables: Faut-il joindre les variables au code asm
        :type withVariables: bool
        :return: code binaire
        :rtype: List[str]
        """
        addressList = self._getAdresses(fifos)
        outCode = []
        variablesCode = self._getVariablesBinary(fifos) 
        for fifo in fifos:
            outCode.extend(self._actionToBinary(fifo.clone(), addressList))
        outCode.extend(variablesCode)
        return outCode
            

