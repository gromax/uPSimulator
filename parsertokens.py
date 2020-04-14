"""
.. module:: parsertokens
   :synopsis: tokens pour le parse des expressions arithmétiques et logiques

"""

from typing import List, Union

from errors import *
from litteral import Litteral
from variable import Variable
from arithmeticexpressionnodes import *
from comparaisonexpressionnodes import *
from logicexpressionnodes import *
import re
from abc import ABC, ABCMeta, abstractmethod


class Token(metaclass=ABCMeta):
    """Classe abstraite qui ne devrait pas être instanciée
    """
    regex:str

    @classmethod
    def test(cls, expression:str) -> bool:
        """Chaque type de noeud est associé à une expression régulière

        :param expression: expression à tester
        :type expression: str
        :return: vrai si l'expression valide l'expression régulière
        :rtype: bool

        :Example:
            >>> TokenBinaryOperator.test("+")
            True
            >>> TokenBinaryOperator.test("2 + 3")
            False
        """
        return re.match("^"+cls.regex+"$", expression.strip()) != None

    def isOperand(self) -> bool:
        """Le token est-il une opérande ?

        :return: vrai le token est un nombre ou une variable
        :rtype: bool

        :Example:
            >>> TokenBinaryOperator("or").isOperand()
            False
            >>> TokenVariable("x").isOperand()
            True
        """
        return isinstance(self,TokenVariable) or isinstance(self,TokenNumber)

    def isOperator(self) -> bool:
        """Le token est-il une opérateur de calcul ?

        :return: vrai le token est un opérateur, binaire ou unaire
        :rtype: bool

        :Example:
            >>> TokenBinaryOperator("or").isOperator()
            True
            >>> TokenVariable("x").isOperator()
            False
        """
        return isinstance(self,TokenBinaryOperator) or isinstance(self,TokenUnaryOperator)

    def getPriority(self) -> int:
        """Fonction par défaut

        :return: priorité de l'opérateur
        :rtype: int

        :Example:
            >>> TokenVariable("x").getPriority()
            0
        """
        return 0


class TokenBinaryOperator(Token):
    regex:str = "<=|==|>=|!=|[\^<>+\-*\/%&|]|and|or"
    _LOGIC = ("and", "or")
    _COMPARAISON = ("<=", "==", ">=", "!=", "<", ">")
    def __init__(self,operator:str):
        """Constructeur

        :param operator: operateur
        :type operator: str
        """
        self._operator = operator.strip()

    @property
    def operator(self) -> str:
        """Accesseur

        :return: opérateur
        :rtype: str

        :Example:
            >>> TokenBinaryOperator("or").operator
            'or'
            >>> TokenBinaryOperator("+").operator
            '+'
        """
        return self._operator

    def getPriority(self) -> int:
        """
        :return: priorité de l'opérateur
        :rtype: int

        :Example:
            >>> TokenBinaryOperator("or").getPriority()
            1
            >>> TokenBinaryOperator("and").getPriority()
            3
            >>> TokenBinaryOperator("<").getPriority()
            4
            >>> TokenBinaryOperator("+").getPriority()
            5
            >>> TokenBinaryOperator("|").getPriority()
            6
        """
        if self._operator == "and":
            return 3
        elif self._operator in "<==>":
            return 4
        elif self._operator in "+-":
            return 5
        elif self._operator == "|":
            return 6
        elif self._operator in "*/&^":
            return 7
        elif self._operator == "%":
            return 8
        else:
            # cas du or
            return 1

    def toNode(self, operandsList:List[Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode]]) -> Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]:
        """Conversion en objet noeud

        :param operandsList: opérandes enfants
        :type operandsList: List[Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]]
        :return: noeud binaire expression correspondant
        :rtype: Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]
        """
        if len(operandsList) <2:
            return None
        operand2 = operandsList.pop()
        operand1 = operandsList.pop()

        if self._operator in self._LOGIC:
            if not isinstance(operand2, (LogicExpressionNode, ComparaisonExpressionNode)):
                return None
            if not isinstance(operand1, (LogicExpressionNode, ComparaisonExpressionNode)):
                return None
            if self._operator == "and":
                return AndNode(operand1, operand2)
            if self._operator == "or":
                return OrNode(operand1, operand2)
            return None
        if not isinstance(operand2, ArithmeticExpressionNode):
            return None
        if not isinstance(operand1, ArithmeticExpressionNode):
            return None

        if self._operator in self._COMPARAISON:
            return ComparaisonExpressionNode(self._operator, operand1, operand2)
        return BinaryArithmeticNode(self._operator, operand1, operand2)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str

        :Example:
            >>> str(TokenBinaryOperator("+"))
            '+'
            >>> str(TokenBinaryOperator("and"))
            'and'
        """
        return str(self._operator)

class TokenUnaryOperator(Token):
    regex:str = "~|not"

    def __init__(self,operator:str):
        """Constructeur

        :param operator: operateur
        :type operator: str
        """
        self._operator = operator.strip()

    @property
    def operator(self) -> str:
        """Accesseur

        :return: opérateur
        :rtype: str

        :Example:
            >>> TokenUnaryOperator("not").operator
            'not'
            >>> TokenUnaryOperator("-").operator
            '-'
        """
        return self._operator

    def getPriority(self) -> int:
        """
        :return: priorité de l'opérateur
        :rtype: int

        :Example:
            >>> TokenUnaryOperator("not").getPriority()
            2
            >>> TokenUnaryOperator("~").getPriority()
            6
        """
        if self._operator == "not":
            return 2
        return 6


    def toNode(self, operandsList:List[Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode]]) -> Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]:
        """Conversion en objet noeud

        :param operandsList: opérandes enfants
        :type operandsList: list[Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode]]
        :return: noeud unaire ou valeur correspondant
        :rtype: Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]

        .. note:

        un - unaire sur un littéral est aussitôt convertit en l'opposé de ce littéral
        """
        if len(operandsList) == 0:
            return None
        operand = operandsList.pop()
        # Le cas NEG sur litteral devrait se contenter de prendre l'opposé du littéral
        if self._operator == "neg" and isinstance(operand, ValueNode) and isinstance(operand.value, Litteral):
            negLitt = operand.value.negClone()
            return ValueNode(negLitt)

        if self._operator == "not":
            if not isinstance(operand, (LogicExpressionNode, ComparaisonExpressionNode)):
                return None
            return NotNode(operand)

        if not isinstance(operand, ArithmeticExpressionNode):
            return None

        if self._operator == "neg":
            return NegNode(operand)

        if self._operator == "~":
            return InverseNode(operand)

        return None

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str

        :Example:
            >>> str(TokenUnaryOperator("-"))
            '-'
            >>> str(TokenUnaryOperator("~"))
            '~'
        """
        return str(self._operator)


class TokenVariable(Token):
    RESERVED_NAMES = ("and", "or", "not", "while", "if", "else", "elif")
    regex:str = "[a-zA-Z][a-zA-Z_0-9]*"

    def __init__(self, name):
        """Constructeur

        :param name: nom de la variable
        :type name: str
        """
        self._name = name.strip()

    @classmethod
    def test(cls, expression:str) -> bool:
        """Teste si l'expression correspond à nom de variable valide

        :param expression: expression à tester
        :type expression: str
        :return: vrai si l'expression valide l'expression régulière
        :rtype: bool

        .. note: Les mots and, not, or vont valider l'expression régulière mais doivent être rejetés

        :Example:
            >>> TokenVariable.test("x")
            True
            >>> TokenVariable.test("if")
            False
            >>> TokenVariable.test("x+y")
            False
        """

        expression_stripped = expression.strip()
        if expression_stripped in cls.RESERVED_NAMES:
            return False
        return super().test(expression_stripped)

    @property
    def value(self) -> str:
        """Accesseur

        :return: expression
        :rtype: str

        :Example:
            >>> TokenVariable("x").value
            'x'
        """
        return self._name

    def toNode(self):
        """Conversion en objet noeud

        .. note:: Crée un objet Variable correspondant

        :return: noeud valeur correspondant
        :rtype: ValueNode
        """
        nomVariable = self._name
        variableObject = Variable(nomVariable)
        return ValueNode(variableObject)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str

        :Example:
            >>> str(TokenVariable("x"))
            'x'
        """
        return str(self._name)

class TokenNumber(Token):
    regex:str = "[0-9]+"
    _value:int

    def __init__(self, expression):
        """Constructeur

        :param expression: chaîne de texte représentannt le nombre
        :type operator: str
        """
        self._value = int(expression.strip())

    @property
    def value(self) -> int:
        """Accesseur

        :return: valeur
        :rtype: int

        :Example:
            >>> TokenNumber("17").value
            17
        """
        return self._value

    def toNode(self):
        """Conversion en objet noeud

        .. note:: Crée un objet Litteral correspondant

        :return: noeud valeur correspondant
        :rtype: ValueNode
        """
        litteralObject = Litteral(self._value)
        return ValueNode(litteralObject)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str

        :Example:
            >>> str(TokenNumber("17"))
            '17'
        """
        return str(self._value)


class TokenParenthesis(Token):
    regex:str = "\(|\)"

    def __init__(self, expression):
        """Constructeur

        :param expression: expression
        :type expression: str
        """
        self._isOpening = (expression == '(')

    def isOpening(self) -> bool:
        """

        :return: vrai si la parenthèse est ouvrante
        :rtype: bool

        :Example:
            >>> TokenParenthesis("(").isOpening()
            True
            >>> TokenParenthesis(")").isOpening()
            False
        """
        return self._isOpening

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str

        :Example:
            >>> str(TokenParenthesis("("))
            '('
        """
        if self._isOpening:
            return "("
        return ")"
