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
  .lineNumber = numéro de ligne programme où l'affectation apparaît
  .nomCible = string nom de la variable affectée
  .expression = objet Expression
InputElement
  .lineNumber = numéro de ligne programme où le input apparaît
  .nomCible = string nom de la variable cible
PrintElement
  .lineNumber = numéro de ligne programme où le print apparaît
  .expression = objet Expression
'''

from expression import *
from variablemanager import *

class Container:
    def __init__(self, items = None):
        if items != None:
            self.__itemsList = items
        else:
            self.__itemsList = []

    def append(self, item_s):
        '''
        item_s = item ou liste d'items à ajouter dans le container (voir fonctions Container.__appendItem)
        '''
        if isinstance(item_s, list):
            for item in item_s:
                self.__appendItem(item)
        else:
            return self.__appendItem(item_s)

    def __appendItem(self, item):
        '''
        item = dictionnaire permettant de déterminer le type d'objet à ajouter
        { 'type':'if', 'lineNumber':tuple(integer, integer) ou integerr, 'condition':Expression, children: list ou tuple deux list }
        { 'type':'while', 'lineNumber': integer, 'condition':Expression, children: list}
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
            if 'children' in keys:
                children = item['children']
                if isinstance(children,'tuple'):
                    # c'est un tuple de liste pour if et else
                    childrenIf, childrenElse = children
                    elem.appendToIf(childrenIf)
                    elem.appendToElse(childrenElse)
                else:
                    elem.appendToIf(children)
        elif type == 'while':
            assert 'condition' in keys
            condition = item['condition']
            elem = WhileElement(lineNumber, condition)
            if 'children' in keys:
                children = item['children']
                elem.append(children)
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
            elem = InputElement(lineNumber, variable)
        self.__itemsList.append(elem)
        return elem

    def __str__(self):
        return "\n".join([str(item) for item in self.__itemsList])

    def isEmpty(self):
        return len(self.__itemsList) == 0

    def getLinearized(self):
        '''
        Transforme la structure arborescente en une structure linéaire avec sauts et labels
        '''
        listLineaire = self.getListVersion()
        labelRank = 0
        for item in listLineaire:
            if isinstance(item, LabelElement):
                item.assignRank(labelRank)
                labelRank += 1
        return Container(listLineaire)

    def getListVersion(self):
        '''
        Retourne la liste des items d'une version linéaire
        '''
        linearizedItemsList = []
        for item in self.__itemsList:
            if isinstance(item, IfElement):
                test, labelIf, linearIf, sautFin, labelElse, linearElse, labelFin = item.getListVersion()
                linearizedItemsList += test
                linearizedItemsList.append(labelIf)
                linearizedItemsList += linearIf
                if sautFin != None:
                    linearizedItemsList.append(sautFin)
                    linearizedItemsList.append(labelElse)
                    linearizedItemsList += linearElse
                    linearizedItemsList.append(labelFin)
            elif isinstance(item,WhileElement):
                labelWhile, test, labelDebut, linear, labelFin = item.getListVersion()
                linearizedItemsList.append(labelWhile)
                linearizedItemsList += test
                linearizedItemsList.append(labelDebut)
                linearizedItemsList += linear
                linearizedItemsList.append(labelFin)
            else:
                linearizedItemsList.append(item)
        return linearizedItemsList

class IfElement:
    def __init__(self, lineNumber, condition):
        '''
        Entrées :
          lineNumber = tuple contenant 2 int, numéro de ligne d'origine du if et celui du else
            ou un seul int pour if
          condition est un objet Expression
        '''
        assert isinstance(condition, Expression)
        self.__condition = condition
        assert condition.getType() == 'bool'
        self.__ifChildren = Container()
        self.__elseChildren = Container()
        if isinstance(lineNumber, tuple):
            self.ifLineNumber, self.elseLineNumber = lineNumber
        else:
            self.ifLineNumber, self.elseLineNumber = lineNumber, None

    def appendToIf(self, item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.append
        '''
        return self.__ifChildren.append(item)

    def appendToElse(self, item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.append
        '''
        return self.__elseChildren.append(item)

    def __str__(self):
        if self.__elseChildren.isEmpty():
            return "if ("+str(self.__condition)+") {\n"+str(self.__ifChildren)+"\n}"
        else:
            return "if "+str(self.__condition)+" {\n"+str(self.__ifChildren)+"\n}\nelse {\n"+str(self.__elseChildren)+"\n}"

    def getListVersion(self):
        linearIf = self.__ifChildren.getListVersion()
        linearElse = self.__elseChildren.getListVersion()
        labelIf = LabelElement(self.lineNumber, "bloc if")
        labelFin = LabelElement(self.lineNumber, "fin")

        if len(linearElse)>0:
            labelElse = LabelElement(self.lineNumber, "bloc else")
            sautFin = JumpElement(self.lineNumber, labelFin)
            test = TestElement.decomposeComplexeCondition(self.lineNumber, self.__condition, labelIf, labelElse)
        else:
            labelElse = None
            sautFin = None
            test = TestElement.decomposeComplexeCondition(self.lineNumber, self.__condition, labelIf, labelFin)
        return test, labelIf, linearIf, sautFin, labelElse, linearElse, labelFin


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
        self.__condition = condition
        assert condition.getType() == 'bool'
        self.__children = Container()

    def append(self,item):
        '''
        item = item ou liste d'items à ajouter dans le container (voir fonctions Container.append
        '''
        return self.__children.append(item)

    def __str__(self):
        return "while "+str(self.__condition)+" {\n"+str(self.__children)+"\n}"

    def getListVersion(self):
        linear = self.__children.getListVersion()
        labelWhile = LabelElement(self.lineNumber, "while")
        labelDebut = LabelElement(self.lineNumber, "début")
        labelFin = LabelElement(self.lineNumber, "fin")
        test = TestElement.decomposeComplexeCondition(self.lineNumber, self.__condition, labelDebut, labelFin)
        return labelWhile, test, labelDebut, linear, labelFin


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
        self.__cible = variableCible
        assert expression.getType() == 'int'
        self.__expression = expression

    def __str__(self):
        return str(self.__cible)+" "+chr(0x2190)+" "+str(self.__expression)

class InputElement:
    def __init__(self, lineNumber, variableCible):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          nomCible = string nom de la variable cible
        '''
        assert isinstance(variableCible, Variable)
        self.lineNumber = lineNumber
        self.__cible = variableCible

    def __str__(self):
        return str(self.__cible)+" "+chr(0x2190)+" Input"

class PrintElement:
    def __init__(self, lineNumber, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          expression est un objet Expression
        '''
        assert isinstance(expression, Expression)
        self.lineNumber = lineNumber
        assert expression.getType() == 'int'
        self.__expression = expression

    def __str__(self):
        return str(self.__expression)+" "+chr(0x2192)+" Affichage"

class LabelElement:
    def __init__(self, lineNumber, label):
        self.__label = label
        self.lineNumber = lineNumber
        self.__rank = -1
    def assignRank(self, value):
        self.__rank = value
    def __str__(self):
        if self.__rank < 0:
            return chr(0x2386)+" "+self.__label
        else:
            return chr(0x2386)+" ["+str(self.__rank)+"] "+self.__label

class JumpElement:
    def __init__(self, lineNumber, cible):
        assert isinstance(cible, LabelElement)
        self.lineNumber = lineNumber
        self.__cible = cible
    def __str__(self):
        return "Saut "+str(self.__cible)

class TestElement:
    @staticmethod
    def decomposeComplexeCondition(lineNumber, condition, cibleOUI, cibleNON):
        '''
        lineNumber : numéro de la ligne à l'origine de ce test
        condition : objet Expression de type bool. Si c'est un and, or, not, décompose en élément plus petit
          jusqu'à obtenir des tests élémentaires en <, <=, >, >=, ==, !=
        cibleOUI, cibleNON : cible LabelElement en cas de OUI et en cas de NON
        Sortie : liste de TestElement et de LabelElement
        '''
        assert isinstance(condition, Expression)
        assert condition.getType() == 'bool'
        decomposition = condition.boolDecompose()
        if decomposition == None:
            # c'est un test élémentaire
            test = TestElement(lineNumber, condition, cibleOUI, cibleNON)
            return [test]
        if decomposition[0] == "not":
            # c'est un not, il faudra inverser OUI et NON et traiter la condition enfant
            conditionEnfant = decomposition[1]
            return TestElement.decomposeComplexeCondition(lineNumber, decompositionEnfant, cibleNON, cibleOUI)
        # c'est un OR ou AND
        cibleInter = LabelElement(lineNumber,"")
        operator, conditionEnfant1, conditionEnfant2 = decomposition
        if operator == "and":
            enfant1 = TestElement.decomposeComplexeCondition(lineNumber, conditionEnfant1, cibleInter, cibleNON)
            enfant2 = TestElement.decomposeComplexeCondition(lineNumber, conditionEnfant2, cibleOUI, cibleNON)
        else:
            enfant1 = TestElement.decomposeComplexeCondition(lineNumber, conditionEnfant1, cibleOUI, cibleInter)
            enfant2 = TestElement.decomposeComplexeCondition(lineNumber, conditionEnfant2, cibleOUI, cibleNON)
        return enfant1 + [cibleInter] + enfant2
    def __init__(self, lineNumber, condition, cibleOUI, cibleNON):
        assert isinstance(cibleOUI, LabelElement)
        assert isinstance(cibleNON, LabelElement)
        assert isinstance(condition, Expression)
        assert condition.getType() == 'bool'
        self.lineNumber = lineNumber
        self.__condition = condition
        self.__cibleOUI = cibleOUI
        self.__cibleNON = cibleNON
    def __str__(self):
        return str(self.__condition)+" OUI : "+str(self.__cibleOUI)+", NON : "+str(self.__cibleNON)


if __name__=="__main__":
    VM = VariableManager()
    EP = ExpressionParser(VM)

    varX = VM.addVariableByName('x')
    varY = VM.addVariableByName('y')
    expr = EP.buildExpression('3*x+2')
    condition = EP.buildExpression('3*x+2<4')

    listeObjetsParsed = [
      { 'type':'affectation', 'lineNumber':1, 'variable': varX, 'expression': EP.buildExpression('0') },
      { 'type':'affectation', 'lineNumber':2, 'variable': varY, 'expression': EP.buildExpression('0') },
      { 'type':'while', 'lineNumber':3, 'condition':EP.buildExpression('x < 10 or y < 100'), 'children':[
        { 'type':'affectation', 'lineNumber':4, 'variable': varX, 'expression': EP.buildExpression('x + 1') },
        { 'type':'affectation', 'lineNumber':5, 'variable': varY, 'expression': EP.buildExpression('y + x') }
      ]},
      { 'type':'print', 'lineNumber':6, 'expression': EP.buildExpression('y') }
    ]

    c = Container()
    c.append(listeObjetsParsed)
    print(c)
    print()
    print("Version linéarisée :")
    print()
    lC = c.getLinearized()
    print(lC)

