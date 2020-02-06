"""
.. module:: lineparser
   :synopsis: gestion du parse d'une ligne du programme d'origine
"""

from typing import List
from typing_extensions import TypedDict

import re
from errors import ParseError
from expressionparser import ExpressionParser
from variable import Variable
from expressionnodes import ExpressionNode

Caracteristiques = TypedDict('Caracteristiques', {
    'lineNumber': int,
    'indentation': int,
    'type': str,
    'condition': ExpressionNode,
    'expression': ExpressionNode,
    'emptyLine': bool,
    'variable': Variable,
    'children':List
}, total = False)

class LineParser: # Définition classe
    """Classe LineParser
    Une ligne qui passe par LineParser :
    .__originalLine (contient la ligne d'origine)
    .__cleanLine (contient la ligne épurée des commentaires et des éventuels espaces en fin de ligne)
    .__caracteristiques dictonnaire
        lineNumber  : contient le n° de ligne traitée, passé en paramètre au constructeur
        indentation : contient le nombre d'espace pour l'indentation
        emptyLine   : True si ligne est vide, False sinon
        type        : correspond au motif identifié (if, elif, while, else, print, input, affectation)
        condition   : contient un objet ExpressionNode de type bool pout les motifs attendant une condition
        expression  : contient un objet ExpressionNode s'il s'agit d'une affectation ou d'un print
        variable    : contient un objet Variable s'il s'agit d'une affectation ou d'un input
    Une méthode getCaracs() pour retourne le dictionnaire __caracteristiques
    """
    __lineNumber: int
    __originalLine: str
    __cleanLine: str
    __expressionParser: ExpressionParser
    __caracteristiques: Caracteristiques
    def __init__(self, originalLine:str, lineNumber:int): # Constructeur
        """Constructeur

        :param originalLine: ligne d'origine
        :type originalLine: str
        :param lineNumber: numéro de la ligne d'origine
        :type line Number: int
        """
        self.__expressionParser = ExpressionParser()
        self.__lineNumber = lineNumber
        self.__originalLine = originalLine
        self.__cleanLine = self.__suppCommentsAndEndSpaces(self.__originalLine)
        self.__caracteristiques = {
            "lineNumber": lineNumber,
            "indentation": self.__countIndentation(self.__cleanLine),
            "emptyLine": self.__cleanLine == ""
        }

        if not self.__caracteristiques["emptyLine"]:
            self.__identificationMotif(self.__cleanLine)

    def __suppCommentsAndEndSpaces(self, line:str) -> str:
        """
        :param line: ligne d'origine
        :type line: str
        :return: ligne sans les espaces terminaux ainsi que les éventuels commentaires
        :rtype: str
        """
        return re.sub("\s*(\#.*)?$","",line)

    def __countIndentation(self, line:str) -> int:
        """
        :param line: ligne dont il faut compter l'indentation
        :type line: str
        :return: nombre d'espaces d'indentation
        :rtype: int
        """
        return len(re.findall("^\s*",line)[0])

    def __identificationMotif(self, line:str) -> bool:
        """Identifie le type de ligne

        :param line: ligne dont il faut tester le type
        :type line: str
        :return: vrai si un type compatible a été trouvé
        :rtype: bool
        :raises: ParseError si aucun type n'est trouvé
        """
        if self.__isTestStructure("if",line): return True
        if self.__isTestStructure("elif",line): return True
        if self.__isTestStructure("while",line): return True
        if self.__isElse(line): return True
        if self.__isPrint(line): return True
        if self.__isInput(line): return True
        if self.__isAffectation(line): return True
        raise ParseError(f"Erreur de syntaxe #{self.__lineNumber} : <{line}>")
        return False

    def __isTestStructure(self, testStructureKeyword:str, line:str) -> bool:
        """Teste si la ligne respecte le modèle [mot-clef] condition:

        :param line: ligne qu'il faut tester
        :type line: str
        :param testStructureKeyword: mot clef de la structure, **if**, **elif** ou **while**
        :type testStructureKeyword: str
        :return: vrai si la structure liée au mot-clef est bien reconnue
        :rtype: bool
        :raises: ParseError si aucun type n'est trouvé
        """
        assert testStructureKeyword in ("if", "elif", "while")
        regex = "^\s*" + testStructureKeyword + "\s("+ ExpressionParser.expressionRegex() +")\s*:$"
        allGroup = re.search(regex,line)
        if not isinstance(allGroup,re.Match):
            return False
        firstGroup = allGroup[1] # tout ce qui match après testStructureKeyword et avant les :
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'bool' :
            raise ParseError(f"L'expression <{expr}> n'est pas une condition")
            return False
        self.__caracteristiques["type"] = testStructureKeyword
        self.__caracteristiques["condition"] = expr
        return True

    def __isElse(self, line:str) -> bool:
        """Teste si la ligne respecte le modèle else:

        :param line: ligne qu'il faut tester
        :type line: str
        :return: vrai si un else est bien reconnu
        :rtype: bool
        """
        motif = "else"
        regex = "^\s*else\s*:$"
        if re.match(regex,line) == None :
            return False
        self.__caracteristiques["type"] = "else"
        return True

    def __isPrint(self, line:str) -> bool:
        """Teste si la ligne respecte le modèle print(expression):

        :param line: ligne qu'il faut tester
        :type line: str
        :return: vrai si un print est bien reconnu
        :rtype: bool
        :raises: ParseError si l'expression détectée n'est pas de type ``int``
        """
        regex = "^\s*print\s*\(("+ ExpressionParser.expressionRegex() +")\)$"
        allGroup = re.search(regex,line)
        if not isinstance(allGroup,re.Match):
            return False
        firstGroup = allGroup[1] # tout ce qui match dans les ( )
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'int' :
            raise ParseError(f"L'expression <{expr}> est incorrecte")
            return False
        self.__caracteristiques["type"] = "print"
        self.__caracteristiques["expression"] = expr
        return True

    def __isInput(self, line:str) -> bool:
        """Teste si la ligne respecte le modèle input(variable):

        :param line: ligne qu'il faut tester
        :type line: str
        :return: vrai si un input est bien reconnu
        :rtype: bool
        :raises: ParseError si la variable détectée est invalide
        """
        regex = "^\s*(" + ExpressionParser.variableRegex() +")\s*=\s*input\s*\(\)$"
        allGroup = re.search(regex,line)
        if not isinstance(allGroup,re.Match):
            return False
        variableName = allGroup[1].strip() # la variable
        if not ExpressionParser.strIsVariableName(variableName):
            raise ParseError(f"La variable <{variableName}> est incorrecte")
        self.__caracteristiques["type"] = "input"
        self.__caracteristiques["variable"] = Variable(variableName)
        return True

    def __isAffectation(self, line:str) -> bool:
        """Teste si la ligne respecte le modèle variable = expression

        :param line: ligne qu'il faut tester
        :type line: str
        :return: vrai si une affectation est bien reconnue
        :rtype: bool
        :raises: ParseError si la variable détectée est invalide ou l'expression n'est pas de type ``int``
        """
        regex = "^\s*(" + ExpressionParser.variableRegex() + ")\s*=\s*(" + ExpressionParser.expressionRegex() + ")$"
        allGroup = re.search(regex,line)
        if not isinstance(allGroup,re.Match):
            return False
        variableName = allGroup[1].strip() # la variable
        expressionStr = allGroup[2] # tout ce qu'il y a dans les ( ) de l'input
        if not ExpressionParser.strIsVariableName(variableName):
            raise ParseError(f"La variable <{variableName}> est incorrecte")
        expr = self.__expressionParser.buildExpression(expressionStr)
        if expr.getType() != 'int' :
            raise ParseError(f"L'expression <{expr}> est incorrecte")
            return False
        self.__caracteristiques["type"] = "affectation"
        self.__caracteristiques["variable"] = Variable(variableName)
        self.__caracteristiques["expression"] = expr
        return True

    def getCaracs(self) -> Caracteristiques:
        """Accesseur

        :return: caractéristiques de la ligne
        :rtype: Caracteristiques
        """
        return self.__caracteristiques

    def __str__(self) -> str:
        """Transtypage -> str

        :return: représentation texte des caractéristiques.
        :rtype: str
        """

        if self.__caracteristiques["type"] in ("if", "elif", "while"):
            return f"#{self.__lineNumber}_{self.__caracteristiques['indentation']} >> {self.__caracteristiques['type']} {self.__caracteristiques['condition']}"
        elif self.__caracteristiques["type"] == "else":
            return f"#{self.__lineNumber}_{self.__caracteristiques['indentation']} >> else"
        elif self.__caracteristiques["type"] == "input":
            return f"#{self.__lineNumber}_{self.__caracteristiques['indentation']} >> {self.__caracteristiques['variable']} = input()"
        elif self.__caracteristiques["type"] == "print":
            return f"#{self.__lineNumber}_{self.__caracteristiques['indentation']} >> print({str(self.__caracteristiques['expression'])})"
        elif self.__caracteristiques["type"] == "affectation":
            return f"#{self.__lineNumber}_{self.__caracteristiques['indentation']} >> {self.__caracteristiques['variable']} = {str(self.__caracteristiques['expression'])}"
        else:
            return f"#{self.__lineNumber}_{self.__caracteristiques['indentation']} >> Erreur !"


if __name__=="__main__":
    listExemples = [
      '    while ( x < y) : #comment',
      'if (A==B):',
      'print(x)  #comment',
      'A = 15',
      'A = A + 1  #comment',
      'variable = input()',
      '    x=x+1',
      'if x < 10 or y < 100:'
    ]
    for i,exemple in enumerate(listExemples):
      print(LineParser(exemple,i))
