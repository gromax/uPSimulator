"""
.. module:: lineparser
   :synopsis: Objets gérant le parse d'une ligne du programme d'origine
"""

from typing import List, Union, Optional
import re

from modules.errors import ParseError
from modules.parser.expression import ExpressionParser
from modules.primitives.variable import Variable
from modules.expressionnodes.arithmetic import ArithmeticExpressionNode
from modules.expressionnodes.comparaison import ComparaisonExpressionNode
from modules.expressionnodes.logic import LogicExpressionNode

class ParsedLine:
    """
    classe ligne par défaut, pour élément vide
    """
    _lineNumber  : int
    _indentation : int = 0
    _children    : List['ParsedLine']
    _needIndentation = False

    def __init__(self, lineNumber:int):
      self._lineNumber = lineNumber
      self._children = []

    @property
    def lineNumber(self) -> int:
        """Accesseur

        :return: numéro de la ligne
        :rtype: int
        """
        return self._lineNumber

    def needIndentation(self) -> bool:
        """Prédicat

        :return: nécessite une indentation
        :rtype: bool
        """
        return self._needIndentation

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        line = self._parentLineToStr()
        if len(self._children) == 0:
            return line
        return line + "\n" + self._childrenToStr()

    def _childrenToStr(self) -> str:
        """Transtypage -> str des enfants
        """
        brutStrList = [str(c) for c in self._children]
        # on colle et décolle suivant "\n" pour obtenir chaque ligne séparée
        strList = ("\n".join(brutStrList)).split("\n")
        # on ajoute des "  " devant et on recolle
        return "\n".join(["  "+s for s in strList])

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_0 >> Vide".format(self._lineNumber)

    @property
    def indentation(self) -> int:
        """Accesseur

        :return: indentation de la ligne
        :rtype: int
        """
        return self._indentation

    @property
    def empty(self) -> bool:
        """Prédicat

        :return: la ligne est vide
        :rtype: bool
        """
        return type(self) == ParsedLine

    def addChild(self, child:'ParsedLine') -> None:
        """Ajoute un enfant

        :param child: enfant à ajouter
        :type child: ParsedLine
        """
        self._children.append(child)

    def addChildren(self, children:List['ParsedLine']) -> None:
        """Ajoute une liste d'enfants

        :param children: liste d'enfants à ajouter
        :type child: List[ParsedLine]
        """
        for c in children:
            self.addChild(c)

    @property
    def children(self) -> List['ParsedLine']:
        """Accesseur

        :return: liste des enfants
        :rtype: List[ParsedLine]
        """
        return self._children

class ParsedLine_If(ParsedLine):
    KEYWORD = "if"
    _condition: Union[LogicExpressionNode, ComparaisonExpressionNode]
    _needIndentation = True
    def __init__(self, lineNumber:int, indentation:int, condition:Union[LogicExpressionNode, ComparaisonExpressionNode]):
        super().__init__(lineNumber)
        self._condition = condition
        self._indentation = indentation

    @classmethod
    def regex(cls):
        return "^" + cls.KEYWORD + r"\s*("+ ExpressionParser.expressionRegex() + r")\s*:$"

    @classmethod
    def tryNew(cls, lineNumber:int, indentation:int, line:str) -> Optional[ParsedLine]:
        """Teste si la ligne respecte le modèle [mot-clef] condition
        et crée l'item correspondant le cas échéant

        :param lineNumber: numéro de la ligne
        :type lineNumber: int
        :param indentation: indentation de la ligne
        :type indentation: int
        :param line: ligne à analyser
        :type line: str
        :return: noeud du type reconnu ou None
        :rtype: Union[ParsedLine_If, ParsedLine_Elif, ParsedLine_While, None]
        :raises: ParseError si l'expression trouvée n'a pas le bon type
        """

        allGroup = re.search(cls.regex(), line)

        if allGroup is None:
            return None

        firstGroup = allGroup[1] # tout ce qui match après testStructureKeyword et avant les :
        condition = ExpressionParser.buildExpression(firstGroup)
        if not isinstance(condition, (LogicExpressionNode, ComparaisonExpressionNode)) :
            raise ParseError("L'expression <{}> n'est pas une condition.".format(condition), {"lineNumber":lineNumber})
        node = cls(lineNumber, indentation, condition)
        return node

    def needIndentation(self) -> bool:
        """Prédicat

        :return: nécessite une indentation
        :rtype: bool
        """
        return True

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> if {}".format(self._lineNumber, self._indentation, self._condition)

    @property
    def condition(self) -> Union[LogicExpressionNode, ComparaisonExpressionNode]:
        """Accesseur

        :return: condition
        :rtype: Union[LogicExpressionNode, ComparaisonExpressionNode]
        """
        return self._condition

class ParsedLine_Elif(ParsedLine_If):
    KEYWORD = "elif"
    _condition: Union[LogicExpressionNode, ComparaisonExpressionNode]

    def __init__(self, lineNumber:int, indentation:int, condition:Union[LogicExpressionNode, ComparaisonExpressionNode]):
        super().__init__(lineNumber, indentation, condition)

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> elif {}".format(self._lineNumber, self._indentation, self._condition)

    def toElseIf(self) -> 'ParsedLine_Else':
        """Transforme le noeud en noeud Else If (lors de la conversion elif en else if)

        :return: le noeud en else
        :rtype: ParsedLine_Else
        """
        newElse = ParsedLine_Else(self._lineNumber, self._indentation)
        newIf = ParsedLine_If(self._lineNumber, self._indentation, self._condition)
        newIf.addChildren(self._children)
        newElse.addChild(newIf)
        return newElse

class ParsedLine_Else(ParsedLine):
    KEYWORD = "else"
    _needIndentation = True
    def __init__(self, lineNumber:int, indentation:int):
        super().__init__(lineNumber)
        self._indentation = indentation

    @classmethod
    def regex(cls):
        return "^" + cls.KEYWORD + r"\s*:$"

    @classmethod
    def tryNew(cls, lineNumber:int, indentation:int, line:str) -> Optional[ParsedLine]:
        """Teste si la ligne respecte le modèle else
        et crée l'item correspondant le cas échéant

        :param lineNumber: numéro de la ligne
        :type lineNumber: int
        :param indentation: indentation de la ligne
        :type indentation: int
        :param line: ligne à analyser
        :type line: str
        :return: noeud du type else ou None
        :rtype: Optional[ParsedLine_Else]
        """

        if re.match(cls.regex(), line) == None :
            return None
        return ParsedLine_Else(lineNumber, indentation)

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> else".format(self._lineNumber, self._indentation)

class ParsedLine_While(ParsedLine_If):
    KEYWORD= "while"
    _condition: Union[LogicExpressionNode, ComparaisonExpressionNode]
    def __init__(self, lineNumber:int, indentation:int, condition:Union[LogicExpressionNode, ComparaisonExpressionNode]):
        super().__init__(lineNumber, indentation, condition)

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> while {}".format(self._lineNumber, self._indentation, self._condition)

class ParsedLine_Print(ParsedLine):
    KEYWORD = "print"
    _expression: ArithmeticExpressionNode
    def __init__(self, lineNumber:int, indentation:int, expression:ArithmeticExpressionNode):
        super().__init__(lineNumber)
        self._expression = expression
        self._indentation = indentation

    @classmethod
    def regex(cls):
        return "^" + cls.KEYWORD + r"\s*\((" + ExpressionParser.expressionRegex() + r")\)$"

    @classmethod
    def tryNew(cls, lineNumber:int, indentation:int, line:str) -> Optional[ParsedLine]:
        """Teste si la ligne respecte le modèle print
        et crée l'item correspondant le cas échéant

        :param lineNumber: numéro de la ligne
        :type lineNumber: int
        :param indentation: indentation de la ligne
        :type indentation: int
        :param line: ligne à analyser
        :type line: str
        :return: noeud du type print ou None
        :rtype: Optional[ParsedLine_Print]
        :raises: ParseError si l'expression détectée n'est pas du bon type
        """

        allGroup = re.search(cls.regex(), line)
        if allGroup is None:
            return None
        firstGroup = allGroup[1] # tout ce qui match dans les ( )
        expr = ExpressionParser.buildExpression(firstGroup)
        if not isinstance(expr, ArithmeticExpressionNode):
            raise ParseError("L'expression <{}> est incorrecte.".format(expr), {"lineNumber": lineNumber})
        return ParsedLine_Print(lineNumber, indentation, expr)

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> print {}".format(self._lineNumber, self._indentation, self._expression)

    @property
    def expression(self) -> ArithmeticExpressionNode:
        """Accesseur

        :return: expression
        :rtype: ArithmeticExpressionNode
        """
        return self._expression

class ParsedLine_Input(ParsedLine):
    KEYWORD = "input"
    _variable: Variable
    def __init__(self, lineNumber:int, indentation:int, variable:Variable):
        super().__init__(lineNumber)
        self._variable = variable
        self._indentation = indentation

    @classmethod
    def regex(cls):
        return "^(" + ExpressionParser.variableRegex() + r")\s*=\s*" + cls.KEYWORD + r"\s*\(\s*\)$"

    @classmethod
    def tryNew(cls, lineNumber:int, indentation:int, line:str) -> Optional[ParsedLine]:
        """Teste si la ligne respecte le modèle print
        et crée l'item correspondant le cas échéant

        :param lineNumber: numéro de la ligne
        :type lineNumber: int
        :param indentation: indentation de la ligne
        :type indentation: int
        :param line: ligne à analyser
        :type line: str
        :return: noeud du type print ou None
        :rtype: Optional[ParsedLine_Print]
        :raises: ParseError si la variable n'a pas la bonne forme
        """
        allGroup = re.search(cls.regex(), line)
        if allGroup is None:
            return None
        variableName = allGroup[1].strip() # la variable

        if not ExpressionParser.strIsVariableName(variableName):
            raise ParseError("La variable <{}> est incorrecte.".format(variableName), {"lineNumber":lineNumber})
        return ParsedLine_Input(lineNumber, indentation, Variable(variableName))


    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> {} = input()".format(self._lineNumber, self._indentation, str(self._variable))

    @property
    def variable(self) -> Variable:
        """Accesseur

        :return: variable
        :rtype: Variable
        """
        return self._variable

class ParsedLine_Affectation(ParsedLine):
    _variable: Variable
    _expression: ArithmeticExpressionNode

    def __init__(self, lineNumber:int, indentation:int, variable:Variable, expression:ArithmeticExpressionNode):
        super().__init__(lineNumber)
        self._variable = variable
        self._expression = expression
        self._indentation = indentation

    @classmethod
    def regex(cls):
        return "^(" + ExpressionParser.variableRegex() + r")\s*=\s*(" + ExpressionParser.expressionRegex() + ")$"

    @classmethod
    def tryNew(cls, lineNumber:int, indentation:int, line:str) -> Optional[ParsedLine]:
        """Teste si la ligne respecte le modèle variable = expression
        et crée l'item correspondant le cas échéant

        :param lineNumber: numéro de la ligne
        :type lineNumber: int
        :param indentation: indentation de la ligne
        :type indentation: int
        :param line: ligne à analyser
        :type line: str
        :return: noeud du type print ou None
        :rtype: Optional[ParsedLine_Print]
        :raises: ParseError si l'expression ou variable détectée n'ont pas la bonne forme
        """
        allGroup = re.search(cls.regex(), line)
        if allGroup is None:
            return None
        variableName = allGroup[1].strip() # la variable
        expressionStr = allGroup[2] # tout ce qu'il y a dans les ( ) de l'input
        if not ExpressionParser.strIsVariableName(variableName):
            raise ParseError("La variable <{}> est incorrecte.".format(variableName), {"lineNumber":lineNumber})
        expr = ExpressionParser.buildExpression(expressionStr)
        if not isinstance(expr, ArithmeticExpressionNode):
            raise ParseError("L'expression <{}> est incorrecte.".format(expr), {"lineNumber":lineNumber})
        return ParsedLine_Affectation(lineNumber, indentation, Variable(variableName), expr)

    def _parentLineToStr(self) -> str:
        """Transtypage -> str

        :return: représentation texte.
        :rtype: str
        """
        return "#{}_{} >> {} = {}".format(self._lineNumber, self._indentation, str(self._variable), str(self._expression))

    @property
    def variable(self) -> Variable:
        """Accesseur

        :return: variable
        :rtype: Variable
        """
        return self._variable

    @property
    def expression(self) -> ArithmeticExpressionNode:
        """Accesseur

        :return: expression
        :rtype: ArithmeticExpressionNode
        """
        return self._expression
