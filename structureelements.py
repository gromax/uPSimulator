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

from errors import *
from expression import *
from variablemanager import *
from processorengine import *

class Container:
    @staticmethod
    def __constructItemsStructure(itemsDescriptifs):
        if itemsDescriptifs == None:
            return []
        if not isinstance(itemsDescriptifs, list):
            structItem = Container.__makeStructItem(itemsDescriptifs)
            return [structItem]
        return [ Container.__makeStructItem(itemDesc) for itemDesc in itemsDescriptifs ]

    @staticmethod
    def __makeStructItem(itemDescriptif):
        '''
        itemDescriptif = dictionnaire permettant de déterminer le type d'objet à ajouter
        { 'type':'if', 'lineNumber':tuple(integer, integer) ou integerr, 'condition':Expression, children: list ou tuple deux list }
        { 'type':'while', 'lineNumber': integer, 'condition':Expression, children: list}
        { 'type':'affectation', 'lineNumber':integer, 'variable': Variable, 'expression': Expression }
        { 'type':'print', 'lineNumber':integer, 'expression': Expression }
        { 'type':'input', 'lineNumber':integer, 'variable': Variable }
        '''
        assert isinstance(itemDescriptif,dict)
        keys = itemDescriptif.keys()
        assert 'type' in keys

        type = itemDescriptif['type']
        assert type in ['if', 'while', 'affectation', 'print', 'input']

        if 'lineNumber' not in keys:
            lineNumber = None
        else:
            lineNumber = itemDescriptif['lineNumber']

        if type == 'if':
            assert 'condition' in keys
            condition = itemDescriptif['condition']
            if not 'children' in keys:
                childIf = None
                childElse = None
            elif isinstance(itemDescriptif['children'], tuple):
                children = itemDescriptif['children']
                assert len(children) == 2
                childIf, childElse = children
            else:
                childIf = itemDescriptif['children']
                childElse = None
            elem = IfElement(lineNumber, condition, childIf, childElse)
        elif type == 'while':
            assert 'condition' in keys
            condition = itemDescriptif['condition']
            if not 'children' in keys:
                children = None
            else:
                children = itemDescriptif['children']
            elem = WhileElement(lineNumber, condition, children)
        elif type == 'affectation':
            assert 'variable' in keys and 'expression' in keys
            variable = itemDescriptif['variable']
            expression = itemDescriptif['expression']
            elem = AffectationElement(lineNumber, variable, expression)
        elif type == 'print':
            assert 'expression' in keys
            expression = itemDescriptif['expression']
            elem = PrintElement(lineNumber, expression)
        else:
            # cas input
            assert 'variable' in keys
            variable = itemDescriptif['variable']
            elem = InputElement(lineNumber, variable)
        return elem

    def __init__(self, itemsDescriptifs):
        brutItemList = Container.__constructItemsStructure(itemsDescriptifs)
        self.__linearList = []
        for structItem in brutItemList:
            self.__linearList += structItem.getLinearItemsList()

    def __str__(self):
        return "\n".join([str(item) for item in self.__linearList])

    def isEmpty(self):
        return len(self.__linearList) == 0

    def getLinearItemsList(self):
        '''
        Retourne la liste des items d'une version linéaire
        '''
        return self.__linearList

    def __cleanListClone(self, engine):
        '''
        Crée un clone de la liste d'items en faisant quelques ajustements :
        - adaptatation des conditions pour les rendres compatibles avec le modèle de uP
        - suppression des labels inutiles
        - suppression des gotos inutiles
        '''
        cloneList = [item for item in self.__linearList]
        # rectification des tests
        index = 0
        for index in range(len(cloneList)):
            item = cloneList[index]
            if isinstance(item,TestElement):
                cloneList[index] = item.cloneToAdjustCondition(engine)
        # supprime des goto inutiles
        if len(cloneList) > 0:
            lastItem = cloneList[0]
            for index in range(1, len(cloneList)):
                item = cloneList[index]
                if isinstance(lastItem,TestElement) and lastItem.getCibleNon() == item:
                    cloneList[index-1] = lastItem.clearCibleNonClone()
                lastItem = item
        # supprime les labels inutiles
        ciblesList = {} # stocké avec les clés
        testsList = [item for item in cloneList if isinstance(item,TestElement)]
        for item in testsList:
            activeCibles = item.getActiveCibles()
            for c in activeCibles:
                ciblesList[c] = True
        jumpsList = [item for item in cloneList if isinstance(item,JumpElement)]
        for item in jumpsList:
            c = item.getCible()
            ciblesList[c] = True

        index = 0
        while index < len(cloneList):
            item = cloneList[index]
            if isinstance(item, LabelElement) and not item in ciblesList:
                # peut être supprimé
                cloneList.pop(index)
            else:
                index += 1
        return cloneList


    def getASM(self, **options):
        engine = ProcessorEngine(**options)
        cleanList = self.__cleanListClone(engine)
        asmList = [item.getASM(engine = engine) for item in cleanList]
        return "\n".join(asmList)

class IfElement:
    def __init__(self, lineNumber, condition, childrenIf, childrenElse):
        '''
        Entrées :
          lineNumber = tuple contenant 2 int, numéro de ligne d'origine du if et celui du else
            ou un seul int pour if
          condition est un objet Expression
        '''
        assert isinstance(condition, Expression)
        self.__condition = condition
        assert condition.getType() == 'bool'
        self.__ifChildren = Container(childIf)
        self.__elseChildren = Container(childElse)
        if isinstance(lineNumber, tuple):
            self.ifLineNumber, self.elseLineNumber = lineNumber
        else:
            self.ifLineNumber, self.elseLineNumber = lineNumber, None

    def __str__(self):
        if self.__elseChildren.isEmpty():
            return "if ("+str(self.__condition)+") {\n"+str(self.__ifChildren)+"\n}"
        else:
            return "if "+str(self.__condition)+" {\n"+str(self.__ifChildren)+"\n}\nelse {\n"+str(self.__elseChildren)+"\n}"

    def getLinearItemsList(self):
        linearIf = self.__ifChildren.getLinearItemsList()
        labelIf = LabelElement(self.lineNumber, "_if_")
        labelFin = LabelElement(self.lineNumber, "_end_")

        conditionInverse = self.__condition.logicNegateClone()
        if not self.__elseChildren.isEmpty():
            linearElse = self.__elseChildren.getLinearItemsList()
            labelElse = LabelElement(self.lineNumber, "_else_")
            sautFin = JumpElement(self.lineNumber, labelFin)
            test = TestElement.decomposeComplexeCondition(self.lineNumber, conditionInverse, labelElse, labelIf)
            return test + [ labelIf ] + linearIf + [ sautFin, labelElse ] + linearElse + [ labelFin ]
        test = TestElement.decomposeComplexeCondition(self.lineNumber, conditionInverse, labelFin, labelIf)
        return test + [ labelIf ] + linearIf + [ labelFin ]

class WhileElement:
    def __init__(self, lineNumber, condition, children):
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
        self.__children = Container(children)

    def __str__(self):
        return "while "+str(self.__condition)+" {\n"+str(self.__children)+"\n}"

    def getLinearItemsList(self):
        linear = self.__children.getLinearItemsList()
        labelWhile = LabelElement(self.lineNumber, "_while_")
        labelDebut = LabelElement(self.lineNumber, "_begin_")
        labelFin = LabelElement(self.lineNumber, "_end_")
        conditionInverse = self.__condition.logicNegateClone()
        test = TestElement.decomposeComplexeCondition(self.lineNumber, conditionInverse, labelFin, labelDebut)
        saut = JumpElement(self.lineNumber, labelWhile)
        return [ labelWhile ] + test + [ labelDebut ] + linear + [ saut, labelFin ]


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

    def getASM(self, **options):
        assert "engine" in options
        engine = options["engine"]
        cem = self.__expression.calcCompile(**options)
        expressionASM = cem.getASM()
        resultRegister = cem.getResultRegister()
        storeASM = engine.getASM(operator="store", operands=(resultRegister, self.__cible))
        return expressionASM+"\n"+storeASM

    def getLinearItemsList(self):
        return [ self ]

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

    def getASM(self, **options):
        assert "engine" in options
        engine = options["engine"]
        return engine.getASM(operator="input", operand=self.__cible)

    def getLinearItemsList(self):
        return [ self ]

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

    def getASM(self, **options):
        assert "engine" in options
        engine = options["engine"]
        cem = self.__expression.calcCompile(**options)
        expressionASM = cem.getASM()
        resultRegister = cem.getResultRegister()
        printASM = engine.getASM(operator="print", operand=resultRegister)
        return expressionASM+"\n"+printASM

    def getLinearItemsList(self):
        return [ self ]

class LabelElement:
    def __init__(self, lineNumber, label):
        self.__label = label
        self.lineNumber = lineNumber

    def __str__(self):
        return chr(0x2386)+ self.__label + str(self.lineNumber)

    def getASM(self, **options):
        return self.__label + str(self.lineNumber)

    def getLinearItemsList(self):
        return [ self ]

class JumpElement:
    def __init__(self, lineNumber, cible):
        assert isinstance(cible, LabelElement)
        self.lineNumber = lineNumber
        self.__cible = cible

    def __str__(self):
        return "Saut "+str(self.__cible)

    def getCible(self):
        return self.__cible

    def getASM(self, **options):
        assert "engine" in options
        engine = options["engine"]
        cibleASM = self.__cible.getASM()
        jumpASM = engine.getASM(operator="goto", operand=cibleASM)
        return jumpASM

    def getLinearItemsList(self):
        return [ self ]

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
        if not condition.isComplexeCondition():
            # c'est un test élémentaire
            test = TestElement(lineNumber, condition, cibleOUI, cibleNON)
            return [test]
        decomposition = condition.boolDecompose()
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
        assert isinstance(cibleNON, LabelElement) or cibleNON == None
        assert isinstance(condition, Expression)
        assert condition.getType() == 'bool'
        assert not condition.isComplexeCondition()
        self.lineNumber = lineNumber
        self.__condition = condition
        self.__cibleOUI = cibleOUI
        self.__cibleNON = cibleNON

    def __str__(self):
        if self.__cibleNON == None:
            return str(self.__condition)+" OUI : "+str(self.__cibleOUI)
        return str(self.__condition)+" OUI : "+str(self.__cibleOUI)+", NON : "+str(self.__cibleNON)

    def negateClone(self):
        '''
        Crée un clone permuttant la condition et les cibles
        '''
        negConditionClone = self.__condition.logicNegateClone()
        return TestElement(self.lineNumber, negConditionClone, self.__cibleNON, self.__cibleOUI)

    def mirrorClone(self):
        conditionMirrorClone = self.__condition.comparaisonMirrorClone()
        return TestElement(self.lineNumber, conditionMirrorClone, self.__cibleOUI, self.__cibleNON)

    def clearCibleNonClone(self):
        return TestElement(self.lineNumber, self.__condition, self.__cibleOUI, None)

    def getCibleNon(self):
        return self.__cibleNON

    def getActiveCibles(self):
        if self.__cibleNON == None:
            return (self.__cibleOUI,)
        return (self.__cibleOUI, self.__cibleNON)

    def cloneToAdjustCondition(self, engine):
        '''
        Crée un clone dont la condition est adaptée au modèle de microprocesseur
        '''
        comparator = self.__condition.getComparaisonSymbol()
        getModifs = engine.lookForComparaison(comparator)
        if getModifs == None:
            raise AttributeError("Aucune instruction de comparaison dans le microprocesseur !")
        miroir, negation = getModifs
        outClone = self
        if miroir:
            outClone = self.swapClone()
        if negation:
            outClone = outClone.negateClone()
        return outClone

    def getASM(self, **options):
        assert "engine" in options
        engine = options["engine"]
        comparator = self.__condition.getComparaisonSymbol()
        assert engine.hasOperator(comparator)
        cem = self.__condition.calcCompile(**options)
        expressionASM = cem.getASM()
        cibleOuiASM = self.__cibleOUI.getASM()
        conditionalGotoASM = engine.getASM(operator=comparator, operand=cibleOuiASM)
        if self.__cibleNON == None:
            return expressionASM+"\n"+conditionalGotoASM
        cibleNonASM = self.__cibleNON.getASM()
        gotoASM = engine.getASM(operator="goto", operand=cibleNonASM)
        return expressionASM+"\n"+conditionalGotoASM+"\n"+gotoASM

    def getLinearItemsList(self):
        return [ self ]

if __name__=="__main__":
    from expressionparser import *
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

    c = Container(listeObjetsParsed)
    print(c)

    engine = ProcessorEngine()
    asmCode = c.getASM(engine = engine)
    print()
    print("Version assembleur")
    print()
    print(asmCode)



