"""
.. module:: arithmeticexpressionnodes
:synopsis: définition des noeuds de calcul intervenant dans les expressions arithmétiques.

.. note:: Les noeuds ne sont jamais modifiés. toute modification entraîne la création de clones.
"""

from typing import Optional, List, Union
from abc import ABC, ABCMeta, abstractmethod

from modules.primitives.operators import Operator, Operators
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.actionsfifo import ActionsFIFO

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

    @abstractmethod
    def clone(self) -> 'ArithmeticExpressionNode':
        """Fonction par défaut

        :return: l'objet lui-même
        :rtype: ArithmeticExpressionNode
        """
        return self

    @abstractmethod
    def getFIFO(self, litteralMaxSize:int = 0) -> ActionsFIFO:
        """Produit une file de type polonaise inversée de façon à donner
        l'ordre de calcul le plus efficace

        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: file de tokens, opérandes ou opérateurs
        :rtype: ActionsFIFO
        """
        return ActionsFIFO()

    def cost(self, litteralMaxSize:int = 0) -> int:
        """
        Coût du calcul en registres. Tient compte d'éventuels calculs sur littéraux faisant gagner des registres.
        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: Coût en nombre de registres
        :rtype: int
        """
        return 1


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
        self._replacement_binary_sub = BinaryArithmeticNode(Operators.MINUS.value, zero, self._operand)

    def cost(self, litteralMaxSize:int = 0) -> int:
        """
        Coût du calcul en registres. Tient compte d'éventuels calculs sur littéraux faisant gagner des registres.
        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: Coût en nombre de registres
        :rtype: int
        """
        return self._operand.cost(litteralMaxSize)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation du noeud sous forme d'une chaîne de caractères
        :rtype: str

        .. note:: L'expression est entièrement parenthèsée.
        """
        return " - ({})".format(self._operand)

    def clone(self) -> 'ArithmeticExpressionNode':
        """Crée un noeud clone

        :return: clone
        :rtype: UnaryNode

        .. note:: L'aborescence enfant est également clonée.
        """
        cloneOperand = self._operand.clone()
        return NegNode(cloneOperand)

    def getFIFO(self, litteralMaxSize:int = 0) -> ActionsFIFO:
        """Produit une file de type polonaise inversée de façon à donner
        l'ordre de calcul le plus efficace

        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: file de tokens, opérandes ou opérateurs
        :rtype: ActionsFIFO
        """
        return self._operand.getFIFO().append(Operators.NEG.value)


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

    def cost(self, litteralMaxSize:int = 0) -> int:
        """
        Coût du calcul en registres. Tient compte d'éventuels calculs sur littéraux faisant gagner des registres.
        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: Coût en nombre de registres
        :rtype: int
        """
        return self._operand.cost(litteralMaxSize)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation du noeud sous forme d'une chaîne de caractères
        :rtype: str

        .. note:: L'expression est entièrement parenthèsée.
        """
        return " ~ ({})".format(self._operand)


    def clone(self) -> 'ArithmeticExpressionNode':
        """Crée un noeud clone

        :return: clone
        :rtype: UnaryNode

        .. note:: L'aborescence enfant est également clonée.
        """
        cloneOperand = self._operand.clone()
        return InverseNode(cloneOperand)

    def getFIFO(self, litteralMaxSize:int = 0) -> ActionsFIFO:
        """Produit une file de type polonaise inversée de façon à donner
        l'ordre de calcul le plus efficace

        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: file de tokens, opérandes ou opérateurs
        :rtype: ActionsFIFO
        """
        return self._operand.getFIFO().append(Operators.INVERSE.value)

class BinaryArithmeticNode(ArithmeticExpressionNode):
    """Noeud pour opération arithmétique binaire parmi +, -, *, /, &, |, ^
    """
    _operand1: ArithmeticExpressionNode
    _operand2: ArithmeticExpressionNode
    def __init__(self, operator:Operator, operand1:ArithmeticExpressionNode, operand2:ArithmeticExpressionNode):
        """Constructeur

        :param operator: opérateur du noéud
        :type operator: Operator
        :param operand1: premier opérande
        :type operand1: ArithmeticExpressionNode
        :param operand2: deuxième opérande
        :type operand2: ArithmeticExpressionNode
        """
        assert operator.arity == 2, "Opérateur {} n'a pas une arité de 2.".format(operator)
        assert operator.isArithmetic, "Opérateur {} n'est pas arithmétique.".format(operator)
        self._operator = operator

        # affectation dans l'ordre par défaut
        self._operand1 = operand1
        self._operand2 = operand2

        # En cas d'opération sur littéral positif, place le littéral si possible à droite
        # si deux littéraux, positifs, de préférence le plus petit à droite

        if not operator.isCommutatif:
            return

        op1AsLitteral = ArithmeticExpressionNode._operandAsLitteral(operand1)
        if op1AsLitteral is None or op1AsLitteral.value < 0:
            return

        op2AsLitteral = ArithmeticExpressionNode._operandAsLitteral(operand2)
        if not (op2AsLitteral is None) and (op2AsLitteral.value > 0) and (op2AsLitteral.value <= op1AsLitteral.value):
            # signifie que op2 est un meilleur litteral
            return

        # l'opérateur est commutatif, operande1 est un litteral positif et si operande2 aussi, operande1 est plus petit...
        # placement de operand1 à droite
        self._operand1 = operand2
        self._operand2 = operand1

    def cost(self, litteralMaxSize:int = 0) -> int:
        """
        Coût du calcul en registres. Tient compte d'éventuels calculs sur littéraux faisant gagner des registres.
        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: Coût en nombre de registres
        :rtype: int
        """
        costOp1 = self._operand1.cost(litteralMaxSize)
        costOp2 = self._operand2.cost(litteralMaxSize)
        return min(max(costOp1, costOp2 + 1), max(costOp1 + 1, costOp2))

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

    def clone(self) -> 'BinaryArithmeticNode':
        """Produit un clone de l'objet avec son arborescence

        :return: clone
        :rtype: BinaryArithmeticNode
        """
        cloneOp1 = self._operand1.clone()
        cloneOp2 = self._operand2.clone()
        operator = self._operator
        return BinaryArithmeticNode(operator, cloneOp1, cloneOp2)

    def getFIFO(self, litteralMaxSize:int = 0) -> ActionsFIFO:
        """Produit une file de type polonaise inversée de façon à donner
        l'ordre de calcul le plus efficace

        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: file de tokens, opérandes ou opérateurs
        :rtype: ActionsFIFO
        """
        if self._operand2.cost(litteralMaxSize) > self._operand1.cost(litteralMaxSize):
            fifo = self._operand2.getFIFO().concat(self._operand1.getFIFO())
            if self._operator.isCommutatif:
                return fifo.append(self._operator)
            return fifo.append(Operators.SWAP.value, self._operator)
        return self._operand1.getFIFO().concat(self._operand2.getFIFO()).append(self._operator)

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

    def cost(self, litteralMaxSize:int = 0) -> int:
        """
        Coût du calcul en registres. Tient compte d'éventuels calculs sur littéraux faisant gagner des registres.
        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: Coût en nombre de registres
        :rtype: int
        """
        if isinstance(self._value, Litteral) and self._value.bitMinSize() <= litteralMaxSize:
            return 0
        return 1

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


    def clone(self) -> 'ValueNode':
        """Produit un clone de l'objet

        :return: clone
        :rtype: BinaryNode

        .. note::la valeur étant un objet ne pouvant être modifié, elle n'est pas clonée.
        """
        return ValueNode(self._value)

    def getFIFO(self, litteralMaxSize:int = 0) -> ActionsFIFO:
        """Produit une file de type polonaise inversée de façon à donner
        l'ordre de calcul le plus efficace

        :param litteralMaxSize: taille maximale d'un littéral dans une commande. 0 si pas de telles commandes.
        :type litteralMaxSize: int
        :return: file de tokens, opérandes ou opérateurs
        :rtype: ActionsFIFO
        """
        return ActionsFIFO().append(self._value)

if __name__=="__main__":
    import doctest
    doctest.testmod()
