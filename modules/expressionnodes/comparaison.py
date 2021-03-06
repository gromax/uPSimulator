"""
.. module:: modules.expressionnodes.comparaisonexpressionodes
:synopsis: définition des noeuds de comparaison intervenant dans les expressions logiques : not, and, or.

.. note:: Les noeuds ne sont jamais modifiés. toute modification entraîne la création de clones.
"""

from typing import List, Union, Optional, Any, Tuple

from modules.errors import AttributesError

from modules.primitives.operators import Operator, Operators
from modules.primitives.actionsfifo import ActionsFIFO

from modules.expressionnodes.arithmetic import ArithmeticExpressionNode


class ComparaisonExpressionNode:
    _inversed: bool = False
    _operator: Operator
    _operand1: ArithmeticExpressionNode
    _operand2: ArithmeticExpressionNode

    @staticmethod
    def negateOperator(operator:Operator) -> Operator:
        assert operator.isComparaison
        if operator == Operators.INF:
            return Operators.SUPOREQ
        if operator == Operators.SUP:
            return Operators.INFOREQ
        if operator == Operators.INFOREQ:
            return Operators.SUP
        if operator == Operators.SUPOREQ:
            return Operators.INF
        if operator == Operators.EQ:
            return Operators.NOTEQ
        return Operators.EQ

    @staticmethod
    def mirroredOperator(operator:Operator) -> Operator:
        assert operator.isComparaison
        if operator == Operators.INF:
            return Operators.SUP
        if operator == Operators.SUP:
            return Operators.INF
        if operator == Operators.INFOREQ:
            return Operators.SUPOREQ
        if operator == Operators.SUPOREQ:
            return Operators.INFOREQ
        if operator == Operators.EQ:
            return Operators.EQ
        return Operators.NOTEQ

    @staticmethod
    def negateMirroredOperator(operator:Operator) -> Operator:
        assert operator.isComparaison
        if operator == Operators.INF:
            return Operators.INFOREQ
        if operator == Operators.SUP:
            return Operators.SUPOREQ
        if operator == Operators.INFOREQ:
            return Operators.INF
        if operator == Operators.SUPOREQ:
            return Operators.SUP
        if operator == Operators.EQ:
            return Operators.NOTEQ
        return Operators.EQ

    @staticmethod
    def operandsToNode(operator:Operator, *operands:Any) -> Optional['ComparaisonExpressionNode']:
        """Crée un noeud de type adapté

        :param operator: opérateur, <=, ==, ...
        :type operator: Operator
        :param operands: opérands dont le type sera vérifié
        :type operands: Any
        :return: noeud d'expression logique ou None en cas d'échec
        :rtype: Optionnal[ArithmeticExpressionNode]
        """
        if (not operator.isComparaison) or (operator.arity != len(operands)):
            return None
        for operand in operands:
            if not isinstance(operand, ArithmeticExpressionNode):
                return None
        if len(operands) == 2:
            return ComparaisonExpressionNode(operator, operands[0], operands[1])
        
        return None

    def __init__(self, operator:Operator, operand1:ArithmeticExpressionNode, operand2:ArithmeticExpressionNode):
        """Constructeur

        :param operator: opérateur du noeud, parmi <, <=, >, >=, ==, !=
        :type operator: Operator
        :param operand1: premier opérande
        :type operand1: ArithmeticExpressionNode
        :param operand2: deuxième opérande
        :type operand2: ArithmeticExpressionNode
        """

        assert operator.isComparaison, "{} n'est pas une comparaison.".format(operator)
        self._operator = operator
        self._operand1 = operand1
        self._operand2 = operand2

    def logicNegateClone(self) -> 'ComparaisonExpressionNode':
        """Complément

        :return: noeud dont les l'expression est complémentaire, ou le noeud lui même si pas de changement
        :rtype: ComparaisonExpressionNode

        :Example:
            >>> from modules.expressionnodes.arithmetic import ValueNode
            >>> from modules.primitives.variable import Variable
            >>> from modules.primitives.litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(4))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('>', oLitteral, oVariable)
            >>> oComp2 = oComp.logicNegateClone()
            >>> str(oComp2)
            'not (#4 > @x)'
        """
        oComp = self.clone()
        oComp._inversed = not self._inversed
        return oComp

    def adjustConditionClone(self, csl:List[Operator]) -> 'ComparaisonExpressionNode':
        """Ajustement des opérateurs de tests en fonction des symboles de comparaison disponibles

        :param csl: symboles de comparaison disponibles
        :type csl: list[Operator]
        :return: clone dont l'expression est adaptée
        :rtype: ComparaisonExpressionNode
        :raises: AttributesErrors si aucun opérateur ne convient

        :Example:
            >>> from modules.expressionnodes.arithmetic import ValueNode
            >>> from modules.primitives.variable import Variable
            >>> from modules.primitives.litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(4))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('>', oLitteral, oVariable)
            >>> oComp2 = oComp.adjustConditionClone(['<', '=='])
            >>> str(oComp2)
            '(@x < #4)'

            >>> from modules.expressionnodes.arithmetic import ValueNode
            >>> from modules.primitives.variable import Variable
            >>> from modules.primitives.litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(4))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('>=', oLitteral, oVariable)
            >>> oComp2 = oComp.adjustConditionClone(['<', '=='])
            >>> str(oComp2)
            'not (#4 < @x)'
        """

        if self._operator in csl:
            # opérateur pris en charge, pas de changement
            return self

        mirroredOperator = ComparaisonExpressionNode.mirroredOperator(self._operator)
        if mirroredOperator in csl:
            return ComparaisonExpressionNode(mirroredOperator, self._operand2, self._operand1)

        negateOperator = ComparaisonExpressionNode.negateOperator(self._operator)
        if negateOperator in csl:
            compNode = ComparaisonExpressionNode(negateOperator, self._operand1, self._operand2)
            compNode._inversed = not self._inversed
            return compNode

        mirroredNegateOperator = ComparaisonExpressionNode.negateMirroredOperator(self._operator)
        if mirroredNegateOperator in csl:
            compNode = ComparaisonExpressionNode(mirroredNegateOperator, self._operand2, self._operand1)
            compNode._inversed = not self._inversed
            return compNode

        raise AttributesError("Aucun opérateur pour {} dans le modèle de processeur.".format(self._operator))

    @property
    def inversed(self):
        """Accesseur

        :return: la comparaison doit être inversée
        :rtype: bool
        """
        return self._inversed

    @property
    def comparaisonSymbol(self) -> str:
        """Accesseur

        :return: symbole de comparaison
        :rtype: str
        """
        return self._operator.symbol

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud sous sa forme str, entièrement parenthèsé
        :rtype: str

        :Example:
            >>> from modules.expressionnodes.arithmetic import ValueNode
            >>> from modules.primitives.variable import Variable
            >>> from modules.primitives.litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(1))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('<', oLitteral, oVariable)
            >>> str(oComp)
            '(#1 < @x)'
        """
        if self._inversed:
            return 'not ({} {} {})'.format(self._operand1, self._operator, self._operand2)
        return '({} {} {})'.format(self._operand1, self._operator, self._operand2)

    def getFIFO(self, litteralDomain:Tuple[int,int]) -> ActionsFIFO:
        """Produit une file de type polonaise inversée de façon à donner
        l'ordre de calcul le plus efficace

        :param litteralDomain: bornes inf et max des littéraux acceptés dans les opérations
        :type litteralDomain: Tuple[int,int]
        :return: file de tokens, opérandes ou opérateurs
        :rtype: ActionsFIFO
        """
        if self._operand2.cost(litteralDomain) > self._operand1.cost(litteralDomain):
            fifo = self._operand2.getFIFO(litteralDomain).concat(self._operand1.getFIFO(litteralDomain))
            if self._operator.isCommutatif:
                return fifo.append(self._operator)
            return fifo.append(Operators.SWAP, self._operator)
        return self._operand1.getFIFO(litteralDomain).concat(self._operand2.getFIFO(litteralDomain)).append(self._operator)

    def clone(self) -> 'ComparaisonExpressionNode':
        """Produit un clone de l'objet avec son arborescence

        :return: clone
        :rtype: ComparaisonExpressionNode
        """
        cloneOp1 = self._operand1.clone()
        cloneOp2 = self._operand2.clone()
        oComp = ComparaisonExpressionNode(self._operator, cloneOp1, cloneOp2)
        oComp._inversed = self._inversed
        return oComp

