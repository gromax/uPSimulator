"""
.. module:: processorengine
   :synopsis: classe définissant les attributs d'un modèle de processeur et fournissant les informations utiles aux outils de compilation
"""

from typing import Union, List, Dict, Optional, Tuple, Sequence
from typing_extensions import TypedDict
from abc import ABC, ABCMeta, abstractmethod

from modules.primitives.litteral import Litteral
from modules.primitives.operators import Operator, Operators

Commands = TypedDict('Commands', {
    'opcode': str,
    'asm'   : str
})


class ProcessorEngine(metaclass=ABCMeta):
    _name                  :str
    _register_address_bits :int
    _data_bits             :int
    _freeUalOutput         :bool
    _litteralsCommands     :Dict[Operator,Commands] = {}
    _commands              :Dict[Operator,Commands] = {}
    _litteralMaxSize       :int
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

    def hasNEG(self) -> bool:
        """Le modèle de processeur possède-t-il un - unaire ?

        :return: vrai s'il en possède un
        :rtype: bool
        """
        return Operators.NEG in self._commands

    def hasOperator(self, operator:Operator) -> bool:
        """Le modèle de processeur possède-t-il l'opérateur demandé ?

        :param operator: nom de l'opérateur
        :type operator: Operator
        :return: Vrai s'il le possède
        :rtype: bool
        """
        return operator in self._commands

    def getAsmCommand(self, operator:Operator) -> str:
        """Renvoie le nom de commande assembleur de la commande demandée. ``''`` si introuvable.

        :param operator: nom de la commande
        :type operator: Operator
        :return: commande assembleur
        :rtype: str
        """

        if not operator in self._commands:
            return ""
        itemAttribute = self._commands[operator]
        return itemAttribute["asm"]

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

    def getLitteralAsmCommand(self, operator:Operator) -> str:
        """Renvoie le nom de commande assembleur de la commande demandée, dans sa version acceptant un littéral. ``''`` si introuvable.

        :param operator: nom de la commande
        :type operator: Operator
        :return: commande assembleur
        :rtype: str
        """
        if not operator in self._litteralsCommands:
            return ""
        itemAttribute = self._litteralsCommands[operator]
        return itemAttribute["asm"]

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

    def litteralOperatorAvailable(self, commandDesc:str, litteral:Litteral) -> bool:
        """Teste si la commande peut s'éxécuter dans une version acceptant un littéral, avec ce littéral en particulier. Il faut que la commande accepte les littéraux et que le codage de ce littéral soit possible dans l'espace laissé par cette commande.

        :param commandDesc: commande à utiliser
        :type commandDesc: str
        :param litteral: littéral à utiliser
        :type litteral: Litteral
        :return: vrai si la commande est utilisable avec ce littéral
        :rtype: bool
        """

        if not commandDesc in self._litteralsCommands:
            return False
        maxLitteralSize = self.getLitteralMaxSizeIn(commandDesc)
        return litteral.isBetween(0, maxLitteralSize)

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

    def getLitteralMaxSizeIn(self, commandDesc:str) -> int:
        """Considérant une commande, détermine le nombre de bits utilisés par l'encodage des attributs de la commande et déduit le nombre de bits laissés pour le codage en nombre positif d'un éventuel littéral, et donc la taille maximal de ce littéral.

        :param commandDesc: commande à utiliser
        :type commandDesc: str
        :return: valeur maximale acceptable du littéral
        :rtype: int
        """
        return 2**self._litteralMaxSize - 1

    @property
    def litteralMaxSize(self):
        return self._litteralMaxSize

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


