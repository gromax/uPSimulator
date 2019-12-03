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

class IfElement:
    __init__(self, lineNumbers, condition, ifChildren=[], elseChildren=[]):
        '''
        Entrées :
          lineNumbers = tuple contenant 2 int, numéro de ligne d'origine du if et celui du else (None si pas de Else)
          condition est un objet Expression
          ifChildren = liste des enfants du if, vide par défaut
          elseChildren = liste des enfants du , vide par défaut
        '''
        assert isinstance(condition, Expression)
        self.condition = condition
        self.ifChildren = ifChildren
        self.elseChildren = elseChildren
        self.ifLineNumber, self.elseLineNumber = lineNumbers

class WhileElement:
    __init__(self, lineNumber, condition, children=[]):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine du while
          condition est un objet Expression
          children = liste des enfants, vide par défaut
        '''
        assert isinstance(condition, Expression)
        self.lineNumber = lineNumber
        self.condition = condition
        self.children = children

class AffectationElement:
    __init__(self, lineNumber, nomCible, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          nomCible = string nom de la variable cible
          expression est un objet Expression
        '''
        assert isinstance(expression, Expression)
        # ajouter test que nomCible est bien valalble
        self.lineNumber = lineNumber
        self.nomCible = condition
        self.expression = children
        
class InputElement:
    __init__(self, lineNumber, nomCible):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          nomCible = string nom de la variable cible
        '''
        # ajouter test que nomCible est bien valalble
        self.lineNumber = lineNumber
        self.nomCible = condition

class PrintElement:
    __init__(self, lineNumber, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          expression est un objet Expression
        '''
        assert isinstance(expression, Expression)
        self.lineNumber = lineNumber
        self.expression = children
        