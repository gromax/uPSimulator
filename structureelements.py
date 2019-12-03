'''
Définition des classes constituant les éléments structurels de programmation.
On comptera les classe suivantes :
Produire en fin de parse une liste d'objets (les objets eux-mêmes seront définis en Demande #240)
IfElement
  .condition = Objet Expression
  .ifChildren = liste d'objets (comme ceux donnés ici)
  .ifLineNumber = numéro de ligne programme où le if apparaît
  .elseChildren = liste d'objets (comme ceux donnés ici) éventuellement vide
  .ifElseLineNumber = numéro de ligne programme où le else apparaît (None si pas de else)
WhileElement
  .lineNumber = numéro de ligne programme où le while apparaît
  .condition = Objet Expression
  .children = liste d'objets (comme ceux donnés ici)
AffectationElement
  .lineNumber = numéro de ligne programme où le while apparaît
  .nomCible = string nom de la variable affectée
  .expression = objet Expression
InputElement
  .lineNumber = numéro de ligne programme où le while apparaît
  .nomCible = string nom de la variable cible
PrintElement
  .lineNumber = numéro de ligne programme où le while apparaît
  .expression = objet Expression
'''

from expression import *

class Container:
    def __init__(self, items = None):
        self.__itemsList = []
        if items != None:
            self.appendList(items)

    def append(self, item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.__appendItem)
        '''
        if isinstance(item, list):
            for item in items:
                self.__append(item)
        else:
            return self.__append(item)

    def __appendItem(self, item):
        '''
        item = dictionnaire permettant de déterminer le type d'objet à ajouter
        { 'type':'if', 'lineNumber':integer, ifChildren: list, elseChildren: list }
        { 'type':'while', 'lineNumber':tuple(integer, integer) ou integer, children: list, elseChildren: list }
        { 'type':'affectation', 'lineNumber':integer, 'variable': Variable, 'expression': Expression }
        { 'type':'print', 'lineNumber':integer, 'expression': Expression }
        { 'type':'input', 'lineNumber':integer, 'variable': Variable }
        '''
        assert isinstance(item,dict)
        keys = item.keys()
        assert 'type' in keys

        type = item['type']
        assert type in ['if', 'while', 'affectation', 'print', 'input']

        if 'lineNumber' not in keys:
            lineNumber = None
        else:
            lineNumber = item['lineNumber']

        if type == 'if':
            assert 'condition' in keys
            condition = item['condition']
            elem = IfElement(lineNumber, condition)
        elif type == 'while':
            assert 'condition' in keys
            condition = item['condition']
            elem = WhileElement(lineNumber, condition)
        elif type == 'affectation':
            assert 'variable' in keys and 'expression' in keys
            variable = item['variable']
            expression = item['expression']
            elem = AffectationElement(lineNumber, variable, expression)
        elif type == 'print':
            assert 'expression' in keys
            expression = item['expression']
            elem = PrintElement(lineNumber, expression)
        else:
            # cas input
            assert 'variable' in keys
            variable = item['variable']
            elem = AffectationElement(lineNumber, variable)
        self.__itemsList.append(elem)
        return elem

    def __str__(self):
        return "\n".join([str(item) for item in self.__itemsList])

class IfElement:
    def __init__(self, lineNumber, condition):
        '''
        Entrées :
          lineNumber = tuple contenant 2 int, numéro de ligne d'origine du if et celui du else
            ou un seul int pour if
          condition est un objet Expression
        '''
        assert isinstance(condition, Expression)
        self.condition = condition
        assert condition.getType() == 'bool'
        self.ifChildren = Container()
        self.elseChildren = Container()
        if isinstance(lineNumber, tuple):
            self.ifLineNumber, self.elseLineNumber = lineNumber
        else:
            self.ifLineNumber, self.elseLineNumber = lineNumber, None

    def appendToIf(self, item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.append
        '''
        return self.ifChildren.append(item)

    def appendToElse(self, item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.append
        '''
        return self.elseChildren.append(item)

    def __str__(self):
        return "if ("+str(self.condition)+") {\n"+str(self.ifChildren)+"\n}"


class WhileElement:
    def __init__(self, lineNumber, condition):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine du while
          condition est un objet Expression
          children = liste des enfants, vide par défaut
        '''
        assert isinstance(condition, Expression)
        self.lineNumber = lineNumber
        self.condition = condition
        assert condition.getType() == 'bool'
        self.children = Container()

    def append(self,item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.append
        '''
        return self.children.append(item)

    def __str__(self):
        return "while ("+str(self.confition)+") {\n"+str(self.children)+"\n}"

class AffectationElement:
    def __init__(self, lineNumber, variableCible, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          nomCible = string nom de la variable cible
          expression est un objet Expression
        '''
        assert isinstance(expression, Expression)
        assert isinstance(variableCible, Variable)
        self.lineNumber = lineNumber
        self.cible = variableCible
        assert condition.getType() == 'int'
        self.expression = expression

class InputElement:
    def __init__(self, lineNumber, variableCible):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          nomCible = string nom de la variable cible
        '''
        assert isinstance(variableCible, Variable)
        self.lineNumber = lineNumber
        self.cible = variableCible

class PrintElement:
    def __init__(self, lineNumber, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          expression est un objet Expression
        '''
        assert isinstance(expression, Expression)
        self.lineNumber = lineNumber
        assert condition.getType() == 'int'
        self.expression = expression
