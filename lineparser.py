import re
from errors import *
from expressionparser import *

class LineParser: # Définition classe
    """Classe LineParser
    Une ligne qui passe par LineParser :
    .originalLine (contient la ligne d'origine)
    .cleanLine (contient la ligne épurée des commentaires et des éventuels espaces en fin de ligne)
    .indent (contient le nombre d'espace pour l'indentation)
    .lineNumber (contient le n° de ligne traitée, passé en paramètre au constructeur)
    .emptyLine (True si ligne est vide, False sinon)
    .type (correspond au motif identifié)
    .condition (contient un objet EP.buildExpression s'il s'agit d'un motif attendant une expression)
    .variable (contient lenom de la variable s'il s'agit d'une affectation avec ou sans input)
    .expression (contient un objet EP.buildExpression s'il s'agit d'une affectation, sinon un string si input ou print)
    .result (contient True si l'identification s'est bien déroulée, sinon False)
    """

    def __init__(self, originalLine, lineNumber): # Constructeur

        self.originalLine = originalLine
        self.cleanLine = self.suppCommentsAndEndSpaces(self.originalLine)
        self.indent = self.countIndentation(self.cleanLine)
        self.lineNumber = lineNumber
        self.emptyLine = self.cleanLine == ""
        self.type = None
        self.result = False
        self.condition = None
        self.variable = None
        self.expression = None
        if not self.emptyLine :
            self.type, self.result = self.identificationMotif(self.cleanLine)

    def suppCommentsAndEndSpaces(self, line):
        return re.sub("\s*(\#.*)?$","",line) # suppression espace terminaux ainsi que les éventuels commentaires

    def countIndentation(self, line):
        return len(re.findall("^\s*",line)[0])

    def identificationMotif(self, line):
        EP = ExpressionParser()
        listMotif = ['print','while','if','elif','else']
        #Parcours des motifs
        for motif in listMotif:
            regex = "^\s*" + motif + "\s*(("+ EP.regex() +"|\s*|\"*)+)\s*(:*)$"
            if re.match(regex,line) != None :
                allGroup = re.search(regex,line)
                firstGroup = allGroup[1]
                lastGroup = allGroup[len(allGroup.groups())]
                if motif in ['while','if','elif'] :
                    if lastGroup != ":" :
                        raise ParseError(f"Absence de ':' en fin de ligne <{motif}> condition <{firstGroup}>")
                        return motif, False
                    else:
                        expr = EP.buildExpression(firstGroup)
                        if expr.getType() != 'bool' :
                            raise ParseError(f"L'expression <{expr}> n'est pas une condition")
                            return motif, False
                        else:
                            self.condition = expr
                            return motif, True
                elif motif in ['else'] :
                    if lastGroup != ":" :
                        raise ParseError(f"Absence de ':' en fin de ligne <{motif}>")
                        return motif, False
                    else:
                        if len(firstGroup) > 0 :
                            raise ParseError(f"La ligne <{motif}:> ne doit contenir rien d'autre")
                            return motif, False
                        else:
                            return motif, True
                elif motif in ['print'] :
                    #buildExpression ne traite pas les string ""
                    #expr = EP.buildExpression(firstGroup)
                    #self.expression = expr
                    #Contrôle des ( )
                    if firstGroup[0] == '(' and firstGroup[-1] == ')' :
                        self.expression = firstGroup
                        return motif, True
                    else:
                        raise ParseError(f"L'expression après le <print> '{firstGroup}' doit être entre paranthèses")
                        return motif, False
                else:
                    raise ParseError(f"Motif <{motif}> non traité !")
                    return motif, False

        #Si ce n'est pas un motif c'est probablement une affectation
        if re.match("^\s*" + EP.regex(),line) != None :
            regex = "^\s*("+ EP.regex() +")\s*=\s*(.*)\s*$"
            allGroup = re.search(regex,line)
            firstGroup = allGroup[1]
            lastGroup = allGroup[len(allGroup.groups())]
            self.variable = firstGroup
            #Contrôle si input
            regex = "^\s*input\s*(("+ EP.regex() +"|\s*|\"*|\?*)+)\s*$"
            if re.match(regex,lastGroup) != None :
                allGroup = re.search(regex,lastGroup)
                firstGroup = allGroup[1]
                #Contrôle des ( )
                if firstGroup[0] == '(' and firstGroup[-1] == ')' :
                    self.expression = firstGroup
                    return "input", True
                else:
                    raise ParseError(f"L'expression après le <input> '{firstGroup}' doit être entre paranthèses")
                    return 'input', False
            #Sinon affectation, mais il faut que ce soit une expression et non pas un string
            else:
                expr = EP.buildExpression(lastGroup)
                self.expression = expr
                return 'affectation', True
        else:
            raise ParseError(f"Struture de ligne incorrecte <{line}>")
            return 'unknow', False


if __name__=="__main__":
    #Exemple pour tester LineParser
    #txt = '    while ( A < B) : #comment'
    #txt = 'if (A==B):'
    # txt = 'print("coucou")  #comment'
    ## txt = 'A=" mon  texte "' #buildExpression ne traite pas les string ""
    # txt = 'A=A+1  #comment'
    # txt = 'variable = input("valeur ?")'
    txt = '    x=x+1'

    ligne = LineParser(txt,1)
    print(f"indent : {ligne.indent}")
    print(f"lineNumber : {ligne.lineNumber}")
    print(f"type : {ligne.type}")
    print(f"result : {ligne.result}")
    print(f"condition : {ligne.condition}")
    print(f"variable : {ligne.variable}")
    print(f"expression : {ligne.expression}")
