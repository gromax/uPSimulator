"""
.. module:: arithmeticexpressionnodes
:synopsis: définition des noeuds de calcul intervenant dans les expressions arithmétiques.

.. note:: Les noeuds ne sont jamais modifiés. toute modification entraîne la création de clones.
"""

from typing import Optional, Sequence, Union
from abc import ABC, ABCMeta, abstractmethod

from errors import *
from litteral import Litteral
from variable import Variable
from processorengine import ProcessorEngine
from compileexpressionmanager import CompileExpressionManager

class ArithmeticExpressionNode(metaclass=ABCMeta):
    """Classe abstraite définissant les propriétés des noeuds arithmétiques
    """
    @staticmethod
    def _operandAsLitteral(operand:'ArithmeticExpressionNode') -> Optional[Litteral]:
        """
        :return: Si l'opérande est littéral, renvoie ce littéral, None sinon
        :rtype: Optional[Litteral]
        """
        if not isinstance(operand, ValueNode):
            return None
        opValue = operand.value
        if not isinstance(opValue, Litteral):
            return None
        return opValue

    @staticmethod
    def _engineHasLitteralIntruction(engine:ProcessorEngine, operator:str, operand:'ArithmeticExpressionNode') -> bool:
        """Calcule le nombre de registre nécessaire pour l'évaluation d'un noeud

        :param engine: modèle de processeur
        :type engine: ProcessorEngine
        :param operator: opération
        :type operator: str
        :param operand: valeur à tester
        :type operand: ArithmeticExpressionNode
        :return: vrai si l'opération c'est une possible opération sur littéral
        :rtype: bool
        """
        opValue = ArithmeticExpressionNode._operandAsLitteral(operand)
        if opValue is None:
            return False
        if not engine.litteralOperatorAvailable(operator, opValue):
            return False
        return True

    @staticmethod
    def _tryPushLitteralInstruction(CEMObject:CompileExpressionManager, operator:str, operand:'ArithmeticExpressionNode') -> bool :
        """Ajoute une opération avec littéral si possible

        :param CEMObject: gestionnaire de compilation pour une expression
        :type CEMObject: CompileExpressionManager
        :param operator: opération
        :type operator: str
        :param operand: valeur à tester
        :type operand: ArithmeticExpressionNode
        :return: vrai si l'opération a réussi
        :rtype: bool
        """
        opValue = ArithmeticExpressionNode._operandAsLitteral(operand)
        if opValue is None:
            return False
        if not CEMObject.engine.litteralOperatorAvailable(operator, opValue):
            return False
        CEMObject.pushUnaryOperatorWithLitteral(operator, opValue)
        return True

    @abstractmethod
    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Exécute la compilation

        :param CEMObject: gestionnaire de compilation pour une expression
        :type CEMObject: CompileExpressionManager
        """
        pass

    @abstractmethod
    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcule le nombre de registre nécessaire pour l'évaluation d'un noeud

        :return: nombre de registres
        :rtype: int
        """
        return 1

    @abstractmethod
    def clone(self) -> 'ArithmeticExpressionNode':
        """Fonction par défaut

        :return: l'objet lui-même
        :rtype: ArithmeticExpressionNode
        """
        return self

    def _precompile(self, CEMObject:CompileExpressionManager) -> None:
        """Calculs communs en amont de la compilation

        :param CEMObject: gestionnaire de compilation pour une expression
        :type CEMObject: CompileExpressionManager
        """
        myCost = self.getRegisterCost(CEMObject.engine)
        needUAL = True
        CEMObject.getNeededRegisterSpace(myCost, needUAL)


class NegNode(ArithmeticExpressionNode):
    """Noeud pour soustraction unaire
    """
    _operand: ArithmeticExpressionNode
    _replacement_binary_sub: ArithmeticExpressionNode
    def __init__(self, operand:ArithmeticExpressionNode):
        """Constructeur

        :param operand: opérande
        :type operand: ArithmeticExpressionNode
        """

        self._operand = operand
        zero = ValueNode(Litteral(0))
        self._replacement_binary_sub = BinaryArithmeticNode("-", zero, self._operand)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation du noeud sous forme d'une chaîne de caractères
        :rtype: str

        .. note:: L'expression est entièrement parenthèsée.
        """
        return " - ({})".format(self._operand)

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcul le nombre de registre nécessaire pour l'évaluation d'un noeud

        :return: nombre de registres
        :rtype: int

        .. note:: L'opérande étant placée dans un registre, on peut envisager de placer le résultat au même endroit.
          L'opération ne nécessite alors pas de registres supplémentaire.

        :Example:
            >>> engine = ProcessorEngine()
            >>> oLitteral1 = ValueNode(Litteral(4))
            >>> oLitteral2 = ValueNode(Litteral(-15))
            >>> oAdd = BinaryArithmeticNode('+', oLitteral1, oLitteral2)
            >>> oNeg = NegNode(oAdd)
            >>> oNeg.getRegisterCost(engine)
            1

            >>> engine = ProcessorEngine('12bits')
            >>> oLitteral1 = ValueNode(Litteral(4))
            >>> oLitteral2 = ValueNode(Litteral(-15))
            >>> oAdd = BinaryArithmeticNode('+', oLitteral1, oLitteral2)
            >>> oNeg = NegNode(oAdd)
            >>> oNeg.getRegisterCost(engine)
            2
        """
        if engine.hasNEG():
            return self._operand.getRegisterCost(engine)
        return self._replacement_binary_sub.getRegisterCost(engine)

    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Exécute la compilation

        :param CEMObject: gestionnaire de compilation pour une expression
        :type CEMObject: compileExpressionManager
        :return: None
        """
        if not CEMObject.engine.hasNEG():
            self._replacement_binary_sub.compile(CEMObject)
            return

        self._precompile(CEMObject)
        if not ArithmeticExpressionNode._tryPushLitteralInstruction(CEMObject, "neg", self._operand):
            self._operand.compile(CEMObject)
            CEMObject.pushUnaryOperator("neg")

    def clone(self) -> 'ArithmeticExpressionNode':
        """Crée un noeud clone

        :return: clone
        :rtype: UnaryNode

        .. note:: L'aborescence enfant est également clonée.
        """
        cloneOperand = self._operand.clone()
        return NegNode(cloneOperand)

class InverseNode(ArithmeticExpressionNode):
    """Noeud pour inversion logique
    """
    _operand: ArithmeticExpressionNode
    def __init__(self, operand:ArithmeticExpressionNode):
        """Constructeur

        :param operand: opérande
        :type operand: ArithmeticExpressionNode
        """

        self._operand = operand

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation du noeud sous forme d'une chaîne de caractères
        :rtype: str

        .. note:: L'expression est entièrement parenthèsée.
        """
        return " ~ ({})".format(self._operand)

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcul le nombre de registre nécessaire pour l'évaluation d'un noeud

        :return: nombre de registres
        :rtype: int

        .. note:: L'opérande étant placée dans un registre, on peut envisager de placer le résultat au même endroit.
          L'opération ne nécessite alors pas de registres supplémentaire.
        """
        return self._operand.getRegisterCost(engine)

    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Exécute la compilation

        :param CEMObject: gestionnaire de compilation pour une expression
        :type CEMObject: compileExpressionManager
        """
        self._precompile(CEMObject)
        if not ArithmeticExpressionNode._tryPushLitteralInstruction(CEMObject, "~", self._operand):
            self._operand.compile(CEMObject)
            CEMObject.pushUnaryOperator("~")

    def clone(self) -> 'ArithmeticExpressionNode':
        """Crée un noeud clone

        :return: clone
        :rtype: UnaryNode

        .. note:: L'aborescence enfant est également clonée.
        """
        cloneOperand = self._operand.clone()
        return InverseNode(cloneOperand)

class BinaryArithmeticNode(ArithmeticExpressionNode):
    """Noeud pour opération arithmétique binaire parmi +, -, *, /, &, |, ^
    """
    _KNOWN_OPERATORS:Sequence[str] = ('+', '-', '*', '/', '%', '&', '|', '^')
    _SYMETRIC_OPERATORS:Sequence[str] = ('+', '*', '&', '|', '^')
    _operand1: ArithmeticExpressionNode
    _operand2: ArithmeticExpressionNode
    def __init__(self, operator:str, operand1:ArithmeticExpressionNode, operand2:ArithmeticExpressionNode):
        """Constructeur

        :param operator: opérateur du noéud, parmi +, -, *, /, %, and, or, &,  |, ^, <, <=, >, >=, ==, !=
        :type operator: str
        :param operand1: premier opérande
        :type operand1: ArithmeticExpressionNode
        :param operand2: deuxième opérande
        :type operand2: ArithmeticExpressionNode
        """

        assert operator in self._KNOWN_OPERATORS
        self._operator = operator

        # affectation dans l'ordre par défaut
        self._operand1 = operand1
        self._operand2 = operand2

        if not operator in self._SYMETRIC_OPERATORS:
            return

        op1AsLitteral = ArithmeticExpressionNode._operandAsLitteral(operand1)
        if op1AsLitteral is None or op1AsLitteral.value < 0:
            return

        op2AsLitteral = ArithmeticExpressionNode._operandAsLitteral(operand2)
        if not (op2AsLitteral is None) and (op2AsLitteral.value > 0) and (op2AsLitteral.value <= op1AsLitteral.value):
            return

        # placement de operand1 à droite
        self._operand1 = operand2
        self._operand2 = operand1

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud sous sa forme str, entièrement parenthèsé
        :rtype: str

        :Example:
            >>> oLitteral = ValueNode(Litteral(1))
            >>> oVariable = ValueNode(Variable("x"))
            >>> oAdd = BinaryArithmeticNode("+", oLitteral, oVariable)
            >>> str(oAdd)
            '(@x + #1)'
        """

        return '({} {} {})'.format(self._operand1, self._operator, self._operand2)

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcul du nombre de registre nécessaires pour évaluer ce noeud

        :param engine: modèle de processeur
        :type engine: ProcessorEngine
        :return: nombre de registres
        :rtype: int

        :Example:
            >>> engine = ProcessorEngine()
            >>> oLitteral1 = ValueNode(Litteral(4))
            >>> oLitteral2 = ValueNode(Litteral(-15))
            >>> oLitteral3 = ValueNode(Litteral(-47))
            >>> oAdd1 = BinaryArithmeticNode('+', oLitteral1, oLitteral2)
            >>> oAdd2 = BinaryArithmeticNode('+', oLitteral2, oLitteral3)
            >>> oMult = BinaryArithmeticNode('*', oAdd1, oAdd2)
            >>> oMult.getRegisterCost(engine)
            2

            >>> engine = ProcessorEngine('12bits')
            >>> oLitteral1 = ValueNode(Litteral(4))
            >>> oLitteral2 = ValueNode(Litteral(-15))
            >>> oLitteral3 = ValueNode(Litteral(-47))
            >>> oAdd1 = BinaryArithmeticNode('+', oLitteral1, oLitteral2)
            >>> oAdd2 = BinaryArithmeticNode('+', oLitteral2, oLitteral3)
            >>> oMult = BinaryArithmeticNode('*', oAdd1, oAdd2)
            >>> oMult.getRegisterCost(engine)
            3
        """

        if ArithmeticExpressionNode._engineHasLitteralIntruction(engine, self._operator, self._operand2):
            return self._operand1.getRegisterCost(engine)
        costOperand1 = self._operand1.getRegisterCost(engine)
        costOperand2 = self._operand2.getRegisterCost(engine)
        return min(max(costOperand1, costOperand2+1), max(costOperand1+1, costOperand2))

    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Procédure d'exécution de la compilation

        :param CEMObject: objet prenant en charge la compilation d'une expression
        :type CEMObject: CompileExpressionManager
        :return: None
        """
        self._precompile(CEMObject)
        engine = CEMObject.engine
        if ArithmeticExpressionNode._engineHasLitteralIntruction(engine, self._operator, self._operand2):
            firstToCalc = self._operand1
            secondToCalc = self._operand2
        elif self._operand1.getRegisterCost(engine) >= self._operand2.getRegisterCost(engine):
            firstToCalc = self._operand1
            secondToCalc = self._operand2
        else:
            firstToCalc = self._operand2
            secondToCalc = self._operand1
        firstToCalc.compile(CEMObject)
        if not ArithmeticExpressionNode._tryPushLitteralInstruction(CEMObject, self._operator, self._operand2):
            secondToCalc.compile(CEMObject)
            goodOrder = (firstToCalc == self._operand1)
            CEMObject.pushBinaryOperator(self._operator, goodOrder)

    def clone(self) -> 'BinaryArithmeticNode':
        """Produit un clone de l'objet avec son arborescence

        :return: clone
        :rtype: BinaryArithmeticNode
        """
        cloneOp1 = self._operand1.clone()
        cloneOp2 = self._operand2.clone()
        operator = self._operator
        return BinaryArithmeticNode(operator, cloneOp1, cloneOp2)


class ValueNode(ArithmeticExpressionNode):
    def __init__(self, value:Union[Litteral, Variable]):
        """Constructeur

        :param value: valeur du noeud
        :type value: Union[Litteral, Variable]
        """
        self._value = value

    @property
    def value(self) -> Union[Variable,Litteral]:
        """Accesseur

        :return: valeur
        :rtype: Union[Variable,Litteral]
        """
        return self._value

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud sous forme str
        :rtype: str

        :Example:
            >>> oLitteral = Litteral(5)
            >>> oValueNode = ValueNode(oLitteral)
            >>> str(oValueNode)
            '#5'

            >>> oVariable = Variable('x')
            >>> oValueNode = ValueNode(oVariable)
            >>> str(oValueNode)
            '@x'
        """
        return str(self._value)

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcule le nombre de registre nécessaire pour l'évaluation d'un noeud

        :return: nombre de registres
        :rtype: int

        :Example:
            >>> v = ValueNode(Litteral(5))
            >>> v.getRegisterCost(ProcessorEngine())
            1
        """
        return 1

    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Procédure d'exécution de la compilation

        :param CEMObject: objet prenant en charge la compilation d'une expression
        :type CEMObject: CompileExpressionManager
        :return: None
        """
        self._precompile(CEMObject)
        CEMObject.pushValue(self._value)

    def clone(self) -> 'ValueNode':
        """Produit un clone de l'objet

        :return: clone
        :rtype: BinaryNode

        .. note::la valeur étant un objet ne pouvant être modifié, elle n'est pas clonée.
        """
        return ValueNode(self._value)

if __name__=="__main__":
    import doctest
    doctest.testmod()
