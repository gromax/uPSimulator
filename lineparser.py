import re
from errors import *
from expressionparser import *
from variablemanager import *

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
        variable    : contient un objet VariableManager s'il s'agit d'une affectation ou d'un input
    Une méthode getCaracs() pour retourne le dictionnaire __caracteristiques
    """

    def __init__(self, originalLine, lineNumber, variableManagerObject=None): # Constructeur
        if variableManagerObject == None:
            self.__variableManager = VariableManager()
        else:
            assert isinstance(variableManagerObject, VariableManager)
            self.__variableManager = variableManagerObject
        # Pour faire le lien avec variablemanager général, expressionparser utilisé pour construire les expressions
        self.__expressionParser = ExpressionParser(self.__variableManager)

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
        if self.__isIf(line): return True
        if self.__isElif(line): return True
        if self.__isWhile(line): return True
        if self.__isElse(line): return True
        if self.__isPrint(line): return True
        if self.__isInput(line): return True
        if self.__isAffectation(line): return True
        raise LineError(f"Struture de ligne incorrecte <{line}>")
        return False

    def __isIf(self, line):
        motif = "if"
        regex = "^\s*" + motif + "\s*(("+ ExpressionParser.regex() +"|\s*|\"*)+)\s*(:*)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match après le motif et avant les :
        lastGroup = allGroup[len(allGroup.groups())] # le dernier groupe, normalement les :
        if lastGroup != ":" :
            raise LineError(f"Absence de ':' en fin de ligne <{motif}> condition <{firstGroup}>")
            return False
        # print(firstGroup)
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'bool' :
            raise LineError(f"L'expression <{expr}> n'est pas une condition")
            return False
        self.__caracteristiques["type"] = motif
        self.__caracteristiques["condition"] = expr
        return True

    def __isElif(self, line):
        motif = "elif"
        regex = "^\s*" + motif + "\s*(("+ ExpressionParser.regex() +"|\s*|\"*)+)\s*(:*)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match après le motif et avant les :
        lastGroup = allGroup[len(allGroup.groups())] # le dernier groupe, normalement les :
        if lastGroup != ":" :
            raise LineError(f"Absence de ':' en fin de ligne <{motif}> condition <{firstGroup}>")
            return False
        # print(firstGroup)
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'bool' :
            raise LineError(f"L'expression <{expr}> n'est pas une condition")
            return False
        self.__caracteristiques["type"] = motif
        self.__caracteristiques["condition"] = expr
        return True

    def __isWhile(self, line):
        motif = "while"
        regex = "^\s*" + motif + "\s*(("+ ExpressionParser.regex() +"|\s*|\"*)+)\s*(:*)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match après le motif et avant les :
        lastGroup = allGroup[len(allGroup.groups())] # le dernier groupe, normalement les :
        if lastGroup != ":" :
            raise LineError(f"Absence de ':' en fin de ligne <{motif}> condition <{firstGroup}>")
            return False
        # print(firstGroup)
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'bool' :
            raise LineError(f"L'expression <{expr}> n'est pas une condition")
            return False
        self.__caracteristiques["type"] = motif
        self.__caracteristiques["condition"] = expr
        return True

    def __isElse(self, line):
        motif = "else"
        regex = "^\s*" + motif + "\s*(("+ ExpressionParser.regex() +"|\s*|\"*)+)\s*(:*)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match après le motif et avant les :
        lastGroup = allGroup[len(allGroup.groups())] # le dernier groupe, normalement les :
        if lastGroup != ":" :
            raise LineError(f"Absence de ':' en fin de ligne <{motif}>")
            return False
        if len(firstGroup) > 0 :
            raise LineError(f"La ligne <{motif}:> ne doit contenir rien d'autre. Présence de <{firstGroup}>")
            return False
        self.__caracteristiques["type"] = motif
        return True

    def __isPrint(self, line): # print que d'une variable, pas de texte ! buildExpression ne traite pas les string ""
        motif = "print"
        regex = "^\s*" + motif + "\s*\((("+ ExpressionParser.regex() +"|\s*)+)\)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # tout ce qui match dans les ( )
        # print(firstGroup)
        expr = self.__expressionParser.buildExpression(firstGroup)
        if expr.getType() != 'int' :
            raise LineError(f"L'expression <{expr}> est incorrecte")
            return False
        self.__caracteristiques["type"] = motif
        self.__caracteristiques["expression"] = expr
        return True

    def __isInput(self, line):
        motif = "input"
        regex = "^\s*("+ ExpressionParser.regex() +")\s*=\s*" + motif + "\s*\((.*)\)$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # la variable
        lastGroup = allGroup[len(allGroup.groups())] # tout ce qu'il y a dans les ( ) de l'input
        # print(firstGroup)
        # print(lastGroup)
        self.__caracteristiques["type"] = motif
        self.__caracteristiques["variable"] = self.__variableManager.addVariableByName(firstGroup)
        return True

    def __isAffectation(self, line):
        motif = "affectation"
        regex = "^\s*("+ ExpressionParser.regex() +")\s*=\s*(.*)\s*$"
        if re.match(regex,line) == None :
            return False
        allGroup = re.search(regex,line)
        firstGroup = allGroup[1] # la variable
        lastGroup = allGroup[len(allGroup.groups())] # tout ce qu'il y a dans les ( ) de l'input
        # print(firstGroup)
        # print(lastGroup)
        expr = self.__expressionParser.buildExpression(lastGroup)
        if expr.getType() == None :
            raise LineError(f"L'expression <{expr}> est incorrecte")
            return False
        self.__caracteristiques["type"] = motif
        self.__caracteristiques["variable"] = self.__variableManager.addVariableByName(firstGroup)
        self.__caracteristiques["expression"] = expr
        return True

    def getCaracs(self):
        return self.__caracteristiques


if __name__=="__main__":
    #Exemple pour tester LineParser
    # txt = '    while ( A < B) : #comment'
    # txt = 'if (A==B):'
    # txt = 'print(x)  #comment'
    ## txt = 'A=" mon  texte "' #buildExpression ne traite pas les string ""
    # txt = 'A=A+1  #comment'
    # txt = 'variable = input("valeur ?")'
    txt = '    x=x+1'
    #txt = 'if (x < 10 or y < 100):'

    ligne = LineParser(txt,1)
    caract = ligne.getCaracs()
    print(caract)
    # print(caract['condition'])
    print(caract['expression'])
    print(caract['expression']._Expression__rootNode._BinaryNode__operands[0]._ValueNode__value.getName)
    print(caract['variable'].getName)