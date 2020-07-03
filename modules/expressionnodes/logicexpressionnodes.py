"""
.. module:: logicexpressionnodes
    :synopsis: définition des noeuds logiques intervenant dans les expressions logiques : not, and, or

.. note:: Les noeuds ne sont jamais modifiés. toute modification entraîne la création de clones.
"""

from typing import Union, Tuple
from abc import ABC, ABCMeta, abstractmethod

from modules.expressionnodes.comparaisonexpressionnodes import ComparaisonExpressionNode

class LogicExpressionNode(metaclass=ABCMeta):
    @abstractmethod
    def logicNegateClone(self) -> Union[ComparaisonExpressionNode, 'LogicExpressionNode']:
        """Calcul la négation logique de l'expression.
        Dans le cas not, consiste à enlever le not.

        Si pas un not, alors c'est un noeud arithmétique qui n'est pas modifié.

        :return: clone pour obtenir une négation logique
        :rtype: Union[ComparaisonExpressionNode, LogicExpressionNode]

        .. note:: Un clone est systèmatiquement créé
        """

    @abstractmethod
    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation du noeud sous forme d'une chaîne de caractères
        :rtype: str

        .. note:: L'expression est entièrement parenthèsée.
        """
        return ""

    @abstractmethod
    def clone(self) -> 'LogicExpressionNode':
        """Crée un noeud clone

        :return: clone
        :rtype: LogicExpressionNode

        .. note:: L'aborescence enfant est également clonée.
        """

class NotNode(LogicExpressionNode):
    _operand: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
    def __init__(self, operand:Union['LogicExpressionNode', 'ComparaisonExpressionNode']):
        """Constructeur

        :param operator: opérateur parmi not, ~ et - (unaire)
        :type operator: str
        :param operand: opérande
        :type operand: Union['LogicBinaryNode', 'LogicUnaryNode', 'ComparaisonNode']
        """

        self._operand = operand

    def logicNegateClone(self) -> Union[ComparaisonExpressionNode, 'LogicExpressionNode']:
        """Calcul la négation logique de l'expression.
        Dans le cas not, consiste à enlever le not.

        Si pas un not, alors c'est un noeud arithmétique qui n'est pas modifié.

        :return: clone pour obtenir une négation logique
        :rtype: Union[ComparaisonExpressionNode, 'LogicExpressionNode']

        .. note:: Un clone est systèmatiquement créé

        :Example:
            >>> from arithmeticexpressionnodes import ValueNode
            >>> from variable import Variable
            >>> from litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(1))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('<', oLitteral, oVariable)
            >>> oNot = NotNode(oComp)
            >>> negateONot = oNot.logicNegateClone()
            >>> str(negateONot)
            '(#1 < @x)'
        """

        return self._operand.clone()

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation du noeud sous forme d'une chaîne de caractères
        :rtype: str

        .. note:: L'expression est entièrement parenthèsée.

        :Example:
            >>> from arithmeticexpressionnodes import ValueNode
            >>> from variable import Variable
            >>> from litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(1))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('<', oLitteral, oVariable)
            >>> oNot = NotNode(oComp)
            >>> str(oNot)
            'not (#1 < @x)'
        """

        return "not {}".format(self._operand)

    def clone(self) -> 'LogicExpressionNode':
        """Crée un noeud clone

        :return: clone
        :rtype: LogicExpressionNode

        .. note:: L'aborescence enfant est également clonée.
        """
        cloneOperand = self._operand.clone()
        return NotNode(cloneOperand)

    @property
    def operand(self) -> Union['LogicExpressionNode', ComparaisonExpressionNode]:
        """Accesseur

        :return: operand
        :rtype: Union[LogicExpressionNode, ComparaisonExpressionNode]
        """
        return self._operand


class AndNode(LogicExpressionNode):
    _operand1: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
    _operand2: Union['LogicExpressionNode', 'ComparaisonExpressionNode']

    def __init__(self, operand1:Union['LogicExpressionNode', 'ComparaisonExpressionNode'], operand2:Union['LogicExpressionNode', 'ComparaisonExpressionNode']):
        """Constructeur

        :param operand1: premier opérande
        :type operand1: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
        :param operand2: deuxième opérande
        :type operand2: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
        """

        self._operand1 = operand1
        self._operand2 = operand2

    def logicNegateClone(self) -> Union[ComparaisonExpressionNode, 'LogicExpressionNode']:
        """Complément

        :return: noeud dont les l'expression est complémentaire, ou le noeud lui même si pas de changement
        :rtype: Union[ComparaisonExpressionNode, 'LogicExpressionNode']
        """
        negCloneOp1 = self._operand1.logicNegateClone()
        negCloneOp2 = self._operand2.logicNegateClone()
        return OrNode(negCloneOp1, negCloneOp2)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud sous sa forme str, entièrement parenthèsé
        :rtype: str
        """
        return '({} and {})'.format(self._operand1, self._operand2)

    def clone(self) -> 'LogicExpressionNode':
        """Produit un clone de l'objet avec son arborescence

        :return: clone
        :rtype: LogicExpressionNode
        """
        cloneOp1 = self._operand1.clone()
        cloneOp2 = self._operand2.clone()
        return AndNode(cloneOp1, cloneOp2)

    @property
    def operands(self) -> Tuple[Union['LogicExpressionNode', ComparaisonExpressionNode],Union['LogicExpressionNode', ComparaisonExpressionNode]]:
        """Accesseur

        :return: operand
        :rtype: Union[LogicExpressionNode, ComparaisonExpressionNode]
        """
        return (self._operand1, self._operand2)

class OrNode(LogicExpressionNode):
    _operand1: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
    _operand2: Union['LogicExpressionNode', 'ComparaisonExpressionNode']

    def __init__(self, operand1:Union['LogicExpressionNode', 'ComparaisonExpressionNode'], operand2:Union['LogicExpressionNode', 'ComparaisonExpressionNode']):
        """Constructeur

        :param operand1: premier opérande
        :type operand1: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
        :param operand2: deuxième opérande
        :type operand2: Union['LogicExpressionNode', 'ComparaisonExpressionNode']
        """

        self._operand1 = operand1
        self._operand2 = operand2

    def logicNegateClone(self) -> Union[ComparaisonExpressionNode, 'LogicExpressionNode']:
        """Complément

        :return: noeud dont les l'expression est complémentaire, ou le noeud lui même si pas de changement
        :rtype: Union[ComparaisonExpressionNode, 'LogicExpressionNode']
        """
        negCloneOp1 = self._operand1.logicNegateClone()
        negCloneOp2 = self._operand2.logicNegateClone()
        return AndNode(negCloneOp1, negCloneOp2)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud sous sa forme str, entièrement parenthèsé
        :rtype: str
        """
        return '({} or {})'.format(self._operand1, self._operand2)

    def clone(self) -> 'LogicExpressionNode':
        """Produit un clone de l'objet avec son arborescence

        :return: clone
        :rtype: LogicExpressionNode
        """
        cloneOp1 = self._operand1.clone()
        cloneOp2 = self._operand2.clone()
        return OrNode(cloneOp1, cloneOp2)

    @property
    def operands(self) -> Tuple[Union['LogicExpressionNode', ComparaisonExpressionNode],Union['LogicExpressionNode', ComparaisonExpressionNode]]:
        """Accesseur

        :return: operand
        :rtype: Union[LogicExpressionNode, ComparaisonExpressionNode]
        """
        return (self._operand1, self._operand2)

if __name__=="__main__":
    import doctest
    doctest.testmod()
