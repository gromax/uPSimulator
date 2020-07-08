"""
.. module:: processorengine
   :synopsis: classe définissant les attributs d'un modèle de processeur et fournissant les informations utiles aux outils de compilation
"""

from typing import Union, List, Dict, Optional, Tuple, Sequence
from typing_extensions import TypedDict
from abc import ABC, ABCMeta, abstractmethod

from modules.errors import CompilationError
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.primitives.operators import Operator, Operators
from modules.primitives.actionsfifo import ActionsFIFO, ActionType

Commands = TypedDict('Commands', {
    'opcode': str,
    'asm'   : str
})


class ProcessorEngine(metaclass=ABCMeta):
    _name                  :str
    _register_address_bits :int
    _data_bits             :int
    _freeUalOutput         :bool
    _litteralArithmeticsCommands: Dict[Operator,Commands]
    _arithmeticsCommands: Dict[Operator,Commands]
    
    _litteralsCommands     :Dict[Operator,Commands] = {}
    _commands              :Dict[Operator,Commands] = {}
    _litteralDomain        :Tuple[int, int]

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

    def litteralOperatorAvailable(self, operator:Operator, litteral:Litteral) -> bool:
        """Teste si la commande peut s'éxécuter dans une version acceptant un littéral, avec ce littéral en particulier. Il faut que la commande accepte les littéraux et que le codage de ce littéral soit possible dans l'espace laissé par cette commande.

        :param operator: commande à utiliser
        :type operator: Operator
        :param litteral: littéral à utiliser
        :type litteral: Litteral
        :return: vrai si la commande est utilisable avec ce littéral
        :rtype: bool
        """

        if not ((operator in self._litteralsCommands) or (operator in self._litteralArithmeticsCommands)):
            return False
        minVal, maxVal = self._litteralDomain
        return litteral.isBetween(minVal, maxVal)

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

        return [item for item in self._commands if item.isComparaison]

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
    
    def _getArithmeticAsmCode(self, operator:Operator, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operator: Opérateur arithmétique
        :type operateor: Operator
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        assert operator.arity == len(operands) - 1, "Nombre d'opérandes [{}] inadapté à l'opétateur {}.".format(len(operands)-1, operator)
        assert operator.isArithmetic, "Opérateur {} n'est pas arithmétique.".format(operator)
        destRegister = operands[-1]
        assert isinstance(destRegister, Register), "La destination n'est pas un registre."

        if operator.arity == 0:
            assert operator in self._arithmeticsCommands, "Ce modèle de processeur n'a pas de commande arithmétique pour {}.".format(operator)
            commande = self._arithmeticsCommands[operator]
            return commande["asm"]

        ops = operands[:-1]       
        for op in ops[:-1]:
            assert isinstance(op, Register), "Les premières opérandes de {} doivent être des registres".format(operator)
 
        if isinstance(ops[-1], Litteral):
            # opération sur littéral
            assert operator in self._litteralArithmeticsCommands, "Ce modèle de processeur n'a pas de variante littérale pour {}.".format(operator)
            commande = self._litteralArithmeticsCommands[operator]
            asm = commande["asm"]
        else:
            # opération totalement sur registre
            assert operator in self._arithmeticsCommands, "Ce modèle de processeur n'a pas de commande arithmétique pour {}.".format(operator)
            commande = self._arithmeticsCommands[operator]
            asm = commande["asm"]

        strOps = ", ".join([str(op) for op in ops])
        return "{} {}, {}".format(asm, destRegister, strOps)


    def _getCommandAsmCode(self, operator:Operator, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operator: Opérateur arithmétique
        :type operateor: Operator
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """

        if operator == Operators.HALT:
            return self._commands[operator]
        if operator == Operators.PRINT:
            assert (len(operands) == 1) and isinstance(operands[0], Register), "Print ne doit avoir qu'un opérande registre"
            asmCommand = self._commands[operator]
            register = operands[0]
            return "{} {}".format(asmCommand, register)

    def _getAsmCode_HALT(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        assert Operators.HALT in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.HALT)
        assert len(operands) == 0, "La commande {} n'a pas d'opérandes.".format(Operators.HALT)
        command = self._commands[Operators.HALT]
        asmCommand = command["asm"]
        return asmCommand

    def _getAsmCode_PRINT(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        assert Operators.PRINT in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.PRINT)
        assert len(operands) == 1, "La commande {} n'a pas d'opérandes.".format(Operators.PRINT)
        command = self._commands[Operators.PRINT]
        asmCommand = command["asm"]
        register = operands[0]
        assert isinstance(register, Register), "La commande {} doit avoir une opérande de type Register.".format(Operators.PRINT)
        return "{} {}".format(asmCommand, register)

    def _getAsmCode_INPUT(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        assert Operators.INPUT in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.INPUT)
        assert len(operands) == 1, "La commande {} n'a pas d'opérandes.".format(Operators.INPUT)
        command = self._commands[Operators.INPUT]
        asmCommand = command["asm"]
        variabe = operands[0]
        assert isinstance(variabe, Variable), "La commande {} doit avoir une opérande de type Variable.".format(Operators.INPUT)
        return "{} {}".format(asmCommand, variabe)


    def _getAsmCode_STORE(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        assert Operators.STORE in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.STORE)
        assert len(operands) == 2, "La commande {} a deux opérandes.".format(Operators.STORE)
        command = self._commands[Operators.STORE]
        asmCommand = command["asm"]
        register, variable = operands
        assert isinstance(variable, Variable), "La commande {} doit avoir une deuxième opérande de type Variable.".format(Operators.STORE)
        assert isinstance(register, Register), "La commande {} doit avoir une première opérande de type Register.".format(Operators.STORE)
        return "{} {}, {}".format(asmCommand, register, variable)

    def _getAsmCode_LOAD(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        assert Operators.LOAD in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.LOAD)
        assert len(operands) == 2, "La commande {} a deux opérandes.".format(Operators.LOAD)
        command = self._commands[Operators.LOAD]
        asmCommand = command["asm"]
        variable, register = operands
        assert isinstance(variable, Variable), "La commande {} doit avoir une première opérande de type Variable.".format(Operators.LOAD)
        assert isinstance(register, Register), "La commande {} doit avoir une deuxième opérande de type Register.".format(Operators.LOAD)
        return "{} {}, {}".format(asmCommand, register, variable)

    def _getAsmCode_MOVE(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        
        assert len(operands) == 2, "La commande {} a deux opérandes.".format(Operators.MOVE)
        source, cible = operands        
        assert isinstance(cible, Register), "La commande {} doit avoir une deuxième opérande de type Register.".format(Operators.MOVE)
        if isinstance(source, Litteral):
            assert Operators.MOVE in self._litteralsCommands, "Le modèle de processeur n'a pas d'instruction littérale pour {}.".format(Operators.MOVE)
            command = self._litteralsCommands[Operators.MOVE]
        else:
            assert Operators.MOVE in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.MOVE)
            assert isinstance(source, Register), "La commande {} doit avoir une première opérande de type Register ou Litteral.".format(Operators.MOVE)
            command = self._commands[Operators.MOVE]
        asmCommand = command["asm"]
        return "{} {}, {}".format(asmCommand, cible, source)

    def _getAsmCode_GOTO(self, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        if len(operands) == 1:
            # cas d'un GOTO direct
            cible = operands[0]
            assert Operators.GOTO in self._commands, "Le modèle de processeur n'a pas d'instruction pour {}.".format(Operators.GOTO)
            assert isinstance(cible, Label), "La commande {} doit avoir une opérande de type Label.".format(Operators.GOTO)
            command = self._commands[Operators.GOTO]
            asmCommand = command["asm"]
            return "{} {}".format(asmCommand, cible)
        # en cas conditionnel, il faut au moins 3 opérandes : 2 registres + un opérateur de comparaison
        assert len(operands) == 4, "La commande {} doit avoir avoir 1 ou 4 opérandes.".format(Operators.GOTO)
        register1, register2, comparator, cible = operands
        assert isinstance(register1, Register), "La commande {} doit avoir une première opérande de type Register.".format(Operators.GOTO)
        assert isinstance(register2, Register), "La commande {} doit avoir une deuxième opérande de type Register.".format(Operators.GOTO)
        assert isinstance(comparator, Operator) and comparator.isComparaison, "La commande {} doit avoir une troisème opérande de type Comparaison.".format(Operators.GOTO)
        assert isinstance(cible, Label), "La commande {} doit avoir une quatrième opérande de type Label.".format(Operators.GOTO)
        assert comparator in self._commands, "Le modèle de processeur n'a pas de commande pour la comparaison {}.".format(comparator)
        comparatorCommand = self._commands[comparator]
        asmComparator = comparatorCommand["asm"]
        # par défaut j'utilise CMP
        assert Operators.CMP in self._commands, "Le modèle de processeur n'a pas de commande pour {}.".format(Operators.CMP)
        cmpCommand = self._commands[Operators.CMP]
        asmCMP = cmpCommand["asm"]
        return [
            "{} {}, {}".format(asmCMP, register1, register2),
            "{} {}".format(asmComparator, cible)
        ]

    
    def _getAsmCode_OTHER(self, operator:Operator, operands:List[ActionType]) -> Union[List[str], str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: Union[List[str], str]
        """
        return ""

    def getAsmCode(self, actions:ActionsFIFO) -> str:
        """
        :param actionsList: file des actions produite par la compilation
        :type actionsList: ActionsFIFO
        :return: code asm
        :rtyp: str
        :raises: CompilationError
        """
        extension:Union[List[str], str]
        lines: List[str] = []
        currentActionItems:List[ActionType] = []
        while not actions.empty:
            lastItem = actions.pop()
            if (not isinstance(lastItem, Operator)) or lastItem.isComparaison:
                currentActionItems.append(lastItem)
                continue
            if lastItem.isArithmetic:
                extension = self._getArithmeticAsmCode(lastItem, currentActionItems)
            elif lastItem == Operators.HALT:
                extension = self._getAsmCode_HALT(currentActionItems)
            elif lastItem == Operators.PRINT:
                extension = self._getAsmCode_PRINT(currentActionItems)
            elif lastItem == Operators.INPUT:
                extension = self._getAsmCode_INPUT(currentActionItems)
            elif lastItem == Operators.STORE:
                extension = self._getAsmCode_STORE(currentActionItems)
            elif lastItem == Operators.LOAD:
                extension = self._getAsmCode_LOAD(currentActionItems)
            elif lastItem == Operators.MOVE:
                extension = self._getAsmCode_MOVE(currentActionItems)
            elif lastItem == Operators.GOTO:
                extension = self._getAsmCode_GOTO(currentActionItems)
            else:
                extension = self._getAsmCode_OTHER(lastItem, currentActionItems)
                if extension == "":
                    raise CompilationError("Commande [{}] inattendue.".format(lastItem), {"lineNumber":actions.lineNumber})
            if isinstance(extension, list):
                lines.extend(extension)
            else:
                lines.append(extension)
            currentActionItems = []

        if len(currentActionItems) > 0:
            raise CompilationError("La séquence devrait terminer par un opérateur.", {"lineNumber":actions.lineNumber})

        return "\n".join(actions.prependStrLabel(lines))


