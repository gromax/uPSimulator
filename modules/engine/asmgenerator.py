"""
.. module:: asmgenarator
   :synopsis: classe générant le code assembleur pour une commande élémentaire donnée
"""

from typing import List, Any, Dict, Union
from abc import ABC, ABCMeta, abstractmethod

from modules.primitives.operators import Operator, Operators
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.actionsfifo import ActionsFIFO, ActionType


class AsmGenerator(metaclass=ABCMeta):
    _operandsType:List[Any] = []
    _operator:Operator
    _slots   :List[int]
    _binary  :str

    def __init__(self, operator:Operator, asm:str, binary:str, **options):
        self._operator = operator
        self._binary = AsmGenerator._zeroPadding(binary)

    @staticmethod
    def _zeroPadding(formatStr:str) -> str:
        """
        :param formatStr: chaîne de forme 'xxx#5' où 5 signifie qu'il faut compléter par 5 0
        :type formatStr: str
        :return: chaîne complétée par des 0
        :rtype: str
        """
        listeStr = formatStr.split("#")
        for i in range(len(listeStr)):
            if i % 2 == 0:
                continue
            l = int(listeStr[i])
            listeStr[i] = "0"*l
        return "".join(listeStr)

    @property
    def operator(self) -> Operator:
        return self._operator

    @abstractmethod
    def asm(self, operands:List[ActionType]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: List[str]
        """
        return []
    
    @abstractmethod
    def binary(self, operands:List[ActionType], addressList:Dict[Union[Label, Variable],int]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label, Variable],int]
        :return: code binaire
        :rtype: List[str]
        """
        return []
    
    def sastifyConditions(self, operands:List[ActionType]) -> bool:
        """Prédicat

        :param operands: opérandes fournies
        :type operands: List[ActionType]
        :return: Les conditions sont satisfaites
        :rtype: bool
        """
        if len(operands) != len(self._operandsType):
            return False
        for i, opType in enumerate(self._operandsType):
            op = operands[i]
            if not isinstance(op, opType):
                return False
        return True

    def _operandsToInt(self, operands:List[ActionType], addressList:Dict[Union[Label, Variable],int]) -> List[int]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label, Variable],int]
        :return: code binaire
        :rtype: List[str]
        """
        #chaque opérande va être associée à un entier selon son type
        intOps = []
        for op in operands:
            if isinstance(op,Litteral):
                intOps.append(op.value)
            elif isinstance(op,(Variable, Label)):
                assert op in addressList, "Variable/Label {} n'est pas référencée dans les adresses.".format(op)
                intOps.append(addressList[op])
            elif isinstance(op, Register):
                intOps.append(op.rank)
            # tout autre type de variable peut être ignoré
        return intOps

    def _intToBinary(self, operands:List[int]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[int]
        :return: code binaire
        :rtype: List[str]
        """
        #chaque opérande va être associée à un entier selon son type
        assert len(self._slots) == len(operands)
        return [format(operands[i], "0"+str(size)+"b") for i, size in enumerate(self._slots) if size > 0]
   


# Formes standards
class AsmGenerator_SINGLE(AsmGenerator):
    _asm   : str
    def __init__(self, operator:Operator, asm:str, binary:str, **options):
        super().__init__(operator, asm, binary, **options)
        self._slots = []
        self._asm = asm

    def asm(self, operands:List[ActionType]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: List[str]
        """
        assert self.sastifyConditions(operands)
        return [self._asm]

    def binary(self, operands:List[ActionType], addressList:Dict[Union[Label, Variable],int]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label, Variable],int]
        :return: code binaire
        :rtype: List[str]
        """
        assert self.sastifyConditions(operands)
        return [self._binary]   

class AsmGenerator_TRANSFERT(AsmGenerator):
    _asm         :str
    _opcode      :str
    _operandsType:List[ActionType]
    def __init__(self, operator:Operator, asm:str, binary:str, **options):
        super().__init__(operator, asm, binary, **options)
        self._asm = asm
        binaryDecode = self._binary.split(".")
        self._opcode = binaryDecode[0]
        self._slots = [int(it) for it in binaryDecode[1:]]
        assert "operands" in options and isinstance(options["operands"], list), "<AsmGenerator_TRANSFERT> requiert une option 'operands'."
        self._operandsType = options["operands"]
        assert len(self._operandsType) > 0, "Le type <AsmGenerator_TRANSFERT> requiert au moins 1 opérande."
        assert len(self._slots) == len(self._operandsType)

    def asm(self, operands:List[ActionType]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: List[str]
        """
        assert self.sastifyConditions(operands)
        # on met toujours la cible à gauche
        opsGoodOrder = [operands[-1]] + operands[:-1]
        return [self._asm + " " + ", ".join([str(op) for op in opsGoodOrder])]

    def binary(self, operands:List[ActionType], addressList:Dict[Union[Label, Variable],int]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label, Variable],int]
        :return: code binaire
        :rtype: List[str]
        """
        assert self.sastifyConditions(operands)
        
        # on met toujours la cible à gauche
        opsGoodOrder = [operands[-1]] + operands[:-1]

        intValues = self._operandsToInt(opsGoodOrder, addressList)
        binaryStr = self._opcode + "".join(self._intToBinary(intValues))
        return [binaryStr]

class AsmGenerator_CONDITIONAL_GOTO(AsmGenerator):
    _asmForCompare:str
    _asmForGoto:str
    _opCodeForCompare:str
    _opCodeForGoto:str
    _comparaisonOperator:Operator
    _operandsType:List[Any] = [Register, Register, Operator, Label]

    def __init__(self, operator:Operator, asm:str, binary:str, **options):
        super().__init__(operator, asm, binary, **options)
        asmSplit = asm.split(";")
        assert len(asmSplit) == 2, "Pour <AsmGenerator_CONDITIONAL_GOTO>, 'asm' doit être de la forme 'code compare;code goto'"
        self._asmForCompare, self._asmForGoto = asmSplit
        assert "comparator" in options and isinstance(options["comparator"], Operator), "<AsmGenerator_CONDITIONAL_GOTO> requiert une option 'comparator'."
        self._comparaisonOperator = options["comparator"]
        binaryListStr = self._binary.split(".")
        assert len(binaryListStr) == 5, "<AsmGenerator_CONDITIONAL_GOTO> requiert un attribut binary avec exactement 5 slots"
        self._opCodeForCompare = binaryListStr[0]
        self._slots = [int(binaryListStr[i]) for i in [1, 2, 4]]
        self._opCodeForGoto = binaryListStr[3]

    # hérité
    def sastifyConditions(self, operands:List[ActionType]) -> bool:
        """Prédicat

        :param operands: opérandes fournies
        :type operands: List[ActionType]
        :return: Les conditions sont satisfaites
        :rtype: bool
        """
        if not super().sastifyConditions(operands):
            return False
        return operands[2] == self._comparaisonOperator

    def asm(self, operands:List[ActionType]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :return: commande assembleur
        :rtype: List[str]
        """
        assert self.sastifyConditions(operands)
        register1 = operands[0]
        register2 = operands[1]
        cible     = operands[3]

        return [
            "{} {}, {}".format(self._asmForCompare, register1, register2),
            "{} {}".format(self._asmForGoto, cible)
        ]

    def binary(self, operands:List[ActionType], addressList:Dict[Union[Label, Variable],int]) -> List[str]:
        """
        :param operands: Opérandes
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label, Variable],int]
        :return: code binaire
        :rtype: List[str]
        """
        assert self.sastifyConditions(operands)
        opsInt = self._operandsToInt(operands, addressList)
        opsBinary = self._intToBinary(opsInt)
        return [
            self._opCodeForCompare + opsBinary[0] + opsBinary[1],
            self._opCodeForGoto + opsBinary[2]
        ]
