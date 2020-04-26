"""
.. module:: comparaisonexpressionodes
:synopsis: définition des noeuds de comparaison intervenant dans les expressions logiques : not, and, or.

.. note:: Les noeuds ne sont jamais modifiés. toute modification entraîne la création de clones.
"""

from typing import Dict, List, Sequence, Union

#from errors import *
#from processorengine import ProcessorEngine
#from compileexpressionmanager import CompileExpressionManager
from arithmeticexpressionnodes import *

class ComparaisonExpressionNode:
    _KNOWN_OPERATORS: Sequence[str] = ('<', '>', '<=', '>=', '==', '!=')
    _NEGATE_OPERATORS: Dict[str, str] = { "<":">=", ">":"<=", "<=":">", ">=":"<", "==":"!=", "!=":"==" }
    _MIRRORED_OPERATORS: Dict[str, str] = { "<":">", ">":"<", "<=":">=", ">=":"<=", "!=":"!=", "==":"==" }
    _NEGATE_MIRRORED_OPERATORS: Dict[str, str] = { "<":"<=", ">":">=", "<=":"<", ">=":">", "==":"!=", "!=":"==" }

    _inversed: bool = False
    _operator: str
    _operand1: ArithmeticExpressionNode
    _operand2: ArithmeticExpressionNode

    def __init__(self, operator:str, operand1:ArithmeticExpressionNode, operand2:ArithmeticExpressionNode):
        """Constructeur

        :param operator: opérateur du noeud, parmi <, <=, >, >=, ==, !=
        :type operator: str
        :param operand1: premier opérande
        :type operand1: ArithmeticExpressionNode
        :param operand2: deuxième opérande
        :type operand2: ArithmeticExpressionNode
        """

        assert operator in self._KNOWN_OPERATORS
        self._operator = operator
        self._operand1 = operand1
        self._operand2 = operand2

    def logicNegateClone(self) -> 'ComparaisonExpressionNode':
        """Complément

        :return: noeud dont les l'expression est complémentaire, ou le noeud lui même si pas de changement
        :rtype: ComparaisonExpressionNode

        :Example:
            >>> from arithmeticexpressionnodes import ValueNode
            >>> from variable import Variable
            >>> from litteral import Litteral
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

    def adjustConditionClone(self,csl:List[str]) -> 'ComparaisonExpressionNode':
        """Ajustement des opérateurs de tests en fonction des symboles de comparaison disponibles

        :param csl: symboles de comparaison disponibles
        :type csl: list[str]
        :return: clone dont l'expression est adaptée
        :rtype: ComparaisonExpressionNode
        :raises: AttributesErrors si aucun opérateur ne convient

        :Example:
            >>> from arithmeticexpressionnodes import ValueNode
            >>> from variable import Variable
            >>> from litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(4))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('>', oLitteral, oVariable)
            >>> oComp2 = oComp.adjustConditionClone(['<', '=='])
            >>> str(oComp2)
            '(@x < #4)'

            >>> from arithmeticexpressionnodes import ValueNode
            >>> from variable import Variable
            >>> from litteral import Litteral
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

        mirroredOperator = self._MIRRORED_OPERATORS[self._operator]
        if mirroredOperator in csl:
            return ComparaisonExpressionNode(mirroredOperator, self._operand2, self._operand1)

        negateOperator = self._NEGATE_OPERATORS[self._operator]
        if negateOperator in csl:
            compNode = ComparaisonExpressionNode(negateOperator, self._operand1, self._operand2)
            compNode._inversed = not self._inversed
            return compNode

        mirroredNegateOperator = self._NEGATE_MIRRORED_OPERATORS[self._operator]
        if mirroredNegateOperator in csl:
            compNode = ComparaisonExpressionNode(mirroredNegateOperator, self._operand2, self._operand1)
            compNode._inversed = not self._inversed
            return compNode

        raise AttributesError(f"Aucun opérateur pour {self._operator} dans le modèle de processeur.")

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
        return self._operator

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud sous sa forme str, entièrement parenthèsé
        :rtype: str

        :Example:
            >>> from arithmeticexpressionnodes import ValueNode
            >>> from variable import Variable
            >>> from litteral import Litteral
            >>> oLitteral = ValueNode(Litteral(1))
            >>> oVariable = ValueNode(Variable('x'))
            >>> oComp = ComparaisonExpressionNode('<', oLitteral, oVariable)
            >>> str(oComp)
            '(#1 < @x)'
        """
        if self._inversed:
            return 'not ({} {} {})'.format(self._operand1, self._operator, self._operand2)
        return '({} {} {})'.format(self._operand1, self._operator, self._operand2)

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcul du nombre de registre nécessaires pour évaluer ce noeud

        :param engine: modèle de processeur
        :type engine: ProcessorEngine
        :return: nombre de registres
        :rtype: int

        :Example:
            >>> engine = ProcessorEngine()
            >>> from arithmeticexpressionnodes import ValueNode, BinaryArithmeticNode
            >>> from litteral import Litteral
            >>> oLitteral1 = ValueNode(Litteral(4))
            >>> oLitteral2 = ValueNode(Litteral(-15))
            >>> oLitteral3 = ValueNode(Litteral(-47))
            >>> oAdd1 = BinaryArithmeticNode('+', oLitteral1, oLitteral2)
            >>> oAdd2 = BinaryArithmeticNode('+', oLitteral2, oLitteral3)
            >>> oComp = ComparaisonExpressionNode('<', oAdd1, oAdd2)
            >>> oComp.getRegisterCost(engine)
            2

            >>> engine = ProcessorEngine('12bits')
            >>> from arithmeticexpressionnodes import ValueNode, BinaryArithmeticNode
            >>> from litteral import Litteral
            >>> oLitteral1 = ValueNode(Litteral(4))
            >>> oLitteral2 = ValueNode(Litteral(-15))
            >>> oLitteral3 = ValueNode(Litteral(-47))
            >>> oAdd1 = BinaryArithmeticNode('+', oLitteral1, oLitteral2)
            >>> oAdd2 = BinaryArithmeticNode('+', oLitteral2, oLitteral3)
            >>> oComp = ComparaisonExpressionNode('<', oAdd1, oAdd2)
            >>> oComp.getRegisterCost(engine)
            3
        """
        costOperand1 = self._operand1.getRegisterCost(engine)
        costOperand2 = self._operand2.getRegisterCost(engine)
        return min(max(costOperand1, costOperand2+1), max(costOperand1+1, costOperand2))

    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Procédure d'exécution de la compilation

        :param CEMObject: objet prenant en charge la compilation d'une expression
        :type CEMObject: CompileExpressionManager
        """
        engine = CEMObject.engine
        myCost = self.getRegisterCost(engine)
        needUAL = False
        CEMObject.getNeededRegisterSpace(myCost, needUAL)

        if self._operand1.getRegisterCost(engine) >= self._operand2.getRegisterCost(engine):
            firstToCalc = self._operand1
            secondToCalc = self._operand2
        else:
            firstToCalc = self._operand2
            secondToCalc = self._operand1
        firstToCalc.compile(CEMObject)
        secondToCalc.compile(CEMObject)
        goodOrder = (firstToCalc == self._operand1)
        CEMObject.pushBinaryOperator("cmp", goodOrder)

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


if __name__=="__main__":
    import doctest
    doctest.testmod()
