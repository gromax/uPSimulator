import re
from errors import *
from expressionparser import ExpressionParser
from variable import Variable

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
        condition   : contient un objet Expression de type bool pout les motifs attendant une condition
        expression  : contient un objet Expression s'il s'agit d'une affectation ou d'un print
        variable    : contient un objet Variable s'il s'agit d'une affectation ou d'un input
    Une méthode getCaracs() pour retourne le dictionnaire __caracteristiques
    """

    def __init__(self, originalLine, lineNumber): # Constructeur
        self.__expressionParser = ExpressionParser()
        self.__lineNumber = lineNumber
        self.__originalLine = originalLine
        self.__cleanLine = self.__suppCommentsAndEndSpaces(self.__originalLine)
        self.__caracteristiques = {}
        self.__caracteristiques["lineNumber"] = lineNumber
        self.__caracteristiques["indentation"] = self.__countIndentation(self.__cleanLine)
        self.__caracteristiques["emptyLine"] = self.__cleanLine == ""
        if not self.__caracteristiques["emptyLine"]:
            self.__identificationMotif(self.__cleanLine)

    def __suppCommentsAndEndSpaces(self, line):
        return re.sub("\s*(\#.*)?$","",line) # suppression espaces terminaux ainsi que les éventuels commentaires

    def __countIndentation(self, line):
        return len(re.findall("^\s*",line)[0]) # dénombre les espaces en début de ligne

    def __identificationMotif(self, line):
        if self.__isTestStructure("if",line): return True
        if self.__isTestStructure("elif",line): return True
        if self.__isTestStructure("while",line): return True
        if self.__isElse(line): return True
        if self.__isPrint(line): return True
        if self.__isInput(line): return True
        if self.__isAffectation(line): return True
        raise ParseError(f"Erreur de syntaxe #{self.__lineNumber} : <{line}>")
        return False

    def __isTestStructure(self, testStructureKeyword, line):
        '''
        testStructureKeyword = string. Un choix parmi "if", "elif", "while"
        '''
        assert testStructureKeyword in ("if", "elif", "while")
        regex = "^\s*" + testStructureKeyword + "\s("+ ExpressionParser.expressionRegex() +")\s*:$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match après testStructureKeyword et avant les :
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'bool' :
            raise ParseError(f"L'expression <{expr}> n'est pas une condition")
            return False
        self.__caracteristiques["type"] = testStructureKeyword
        self.__caracteristiques["condition"] = expr
        return True

    def __isElse(self, line):
        motif = "else"
        regex = "^\s*else\s*:$"
        if re.match(regex,line) == None :
            return False
        self.__caracteristiques["type"] = "else"
        return True

    def __isPrint(self, line): # print que d'une variable, pas de texte ! buildExpression ne traite pas les string ""
        regex = "^\s*print\s*\(("+ ExpressionParser.expressionRegex() +")\)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match dans les ( )
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'int' :
            raise ParseError(f"L'expression <{expr}> est incorrecte")
            return False
        self.__caracteristiques["type"] = "print"
        self.__caracteristiques["expression"] = expr
        return True

    def __isInput(self, line):
        regex = "^\s*(" + ExpressionParser.variableRegex() +")\s*=\s*input\s*\(\)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        variableName = allGroup[1].strip() # la variable
        if not ExpressionParser.strIsVariableName(variableName):
            raise ParseError(f"La variable <{variableName}> est incorrecte")
        self.__caracteristiques["type"] = "input"
        self.__caracteristiques["variable"] = Variable(variableName)
        return True

    def __isAffectation(self, line):
        regex = "^\s*(" + ExpressionParser.variableRegex() + ")\s*=\s*(" + ExpressionParser.expressionRegex() + ")$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        variableName = allGroup[1].strip() # la variable
        expressionStr = allGroup[2] # tout ce qu'il y a dans les ( ) de l'input
        if not ExpressionParser.strIsVariableName(variableName):
            raise ParseError(f"La variable <{variableName}> est incorrecte")
        expr = self.__expressionParser.buildExpression(expressionStr)
        if expr.getType() == None :
            raise ParseError(f"L'expression <{expr}> est incorrecte")
            return False
        self.__caracteristiques["type"] = "affectation"
        self.__caracteristiques["variable"] = Variable(variableName)
        self.__caracteristiques["expression"] = expr
        return True

    def getCaracs(self):
        return self.__caracteristiques

    def __str__(self):
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
