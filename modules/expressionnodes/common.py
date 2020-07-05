"""
.. module:: modules.expressionnodes.common
:synopsis: assure le lien des modules externes vers les différents types de noeuds
"""

from typing import Union, Any

from modules.expressionnodes.logicexpressionnodes import LogicExpressionNode
from modules.expressionnodes.arithmeticexpressionnodes import ArithmeticExpressionNode
from modules.expressionnodes.comparaisonexpressionnodes import ComparaisonExpressionNode
from modules.primitives.operators import Operator

ExpressionType = Union[LogicExpressionNode, ComparaisonExpressionNode, ArithmeticExpressionNode]
OptExpressionType = Union[LogicExpressionNode, ComparaisonExpressionNode, ArithmeticExpressionNode, None]

def operandNode(operator:Operator, *operands:Any) -> OptExpressionType:
    """Crée un noeud de type adapté

    :param operator: opérateur, or, and ou not
    :type operator: Operator
    :param operands: opérands dont le type sera vérifié
    :type operands: Any
    :return: noeud d'expression logique ou None en cas d'échec
    :rtype: Optionnal[LogicExpressionNode]
    """
    if operator.isLogic:
        return LogicExpressionNode.operandsToNode(operator, *operands)
    if operator.isArithmetic:
        return ArithmeticExpressionNode.operandsToNode(operator, *operands)
    if operator.isComparaison:
        return ComparaisonExpressionNode.operandsToNode(operator, *operands)
    return None   

def valueNode(value:Any) -> OptExpressionType:
    """Crée un noeud de valeur

    :param value: valeur à créer
    :type operator: Any
    :return: noeud d'expression logique ou None en cas d'échec
    :rtype: Optionnal[LogicExpressionNode]
    """
    return ArithmeticExpressionNode.toValueNode(value)