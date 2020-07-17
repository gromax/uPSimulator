"""
.. module:: modules.parser.tokens
   :synopsis: tokens pour le parse des expressions arithmétiques et logiques

"""

from typing import List
from abc import ABC, ABCMeta, abstractmethod
import re

from modules.primitives.operators import Operator, Operators

class Token(metaclass=ABCMeta):
    """Classe abstraite qui ne devrait pas être instanciée
    """
    _operators: List[Operator] = []

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
        return re.match("^"+cls.regex()+"$", expression.strip()) != None

    @classmethod
    def regex(cls):
        return "|".join([op.regex for op in cls._operators if op.regex != ""])

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
    _operators:List[Operator] = Operators.expressionBinaryOps()
    def __init__(self,operator:Operator):
        """Constructeur

        :param operator: operateur
        :type operator: Operator
        """
        operator = operator.strip()
        for op in TokenBinaryOperator._operators:
            if op.symbol == operator:
                self._operator = op
                return
        # par défaut on retourne un +
        self._operator = Operators.ADD

    @property
    def operator(self) -> Operator:
        """Accesseur

        :return: opérateur
        :rtype: Operator

        :Example:
            >>> str(TokenBinaryOperator("or").operator)
            'or'
            >>> str(TokenBinaryOperator("+").operator)
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
        return self._operator.priority

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
    _operators:List[Operator] = Operators.expressionUnaryOps()

    @staticmethod
    def makeFromOperator(operator:Operator) -> 'TokenUnaryOperator':
        assert operator.arity == 1
        return TokenUnaryOperator(operator.symbol)

    def __init__(self,strOperator:str):
        """Constructeur

        :param strOperator: operateur
        :type strOperator: str
        """
        strOperator = strOperator.strip()
        for op in TokenUnaryOperator._operators:
            if op.symbol == strOperator:
                self._operator = op
                return
        # par défaut on retourne un ~
        self._operator = Operators.INVERSE

    @property
    def operator(self) -> str:
        """Accesseur

        :return: opérateur
        :rtype: str

        :Example:
            >>> str(TokenUnaryOperator("not").operator)
            'not'
            >>> str(TokenUnaryOperator("-").operator)
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
        return self._operator.priority

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
    RESERVED_NAMES = ("while", "if", "else", "elif") + tuple([op.symbol for op in Operators.list()])
    _name : str
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

    @classmethod
    def regex(cls):
        return "[a-zA-Z][a-zA-Z_0-9]*"

    @property
    def name(self) -> str:
        """Accesseur

        :return: name
        :rtype: str

        :Example:
            >>> TokenVariable("x").value
            'x'
        """
        return self._name

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
    _value:int

    def __init__(self, expression):
        """Constructeur

        :param expression: chaîne de texte représentannt le nombre
        :type operator: str
        """
        self._value = int(expression.strip())

    @classmethod
    def regex(cls):
        return "[0-9]+"

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
    def __init__(self, expression):
        """Constructeur

        :param expression: expression
        :type expression: str
        """
        self._isOpening = (expression == '(')

    @classmethod
    def regex(cls):
        return r"\(|\)"

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
