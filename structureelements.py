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
from assembleurcontainer import *

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
        ciblesList = {} # stocké avec les clés, les valeurs seront les items origines
        for item in cloneList:
            if isinstance(item, LabelElement):
                ciblesList[item] = []
        for item in cloneList:
            if isinstance(item, TestElement):
                cibles = item.getCibles()
                for c in cibles:
                    assert c in ciblesList
                    ciblesList[c].append(item)
            elif isinstance(item, JumpElement):
                c = item.getCible()
                assert c in ciblesList
                ciblesList[c].append(item)
        # on peut supprimer les cibles qui n'ont aucun élément origine
        # et fusionner les doublons consécutifs
        index = 0
        while index < len(cloneList):
            item = cloneList[index]
            if item in ciblesList and len(ciblesList[item]) == 0:
                # peut être supprimé
                cloneList.pop(index)
                del ciblesList[item]
            elif item in ciblesList and index + 1 < len(cloneList) and cloneList[index+1] in ciblesList:
                # le label consécutif peut être supprimé
                itemSuivant = cloneList[index+1]

                if len(ciblesList[itemSuivant]) == 0:
                    # on peut le supprimer directement
                    cloneList.pop(index + 1)
                    del ciblesList[itemSuivant]
                else:
                    # il faut fusionner
                    for index, origine in enumerate(cloneList):
                        if origine in ciblesList[itemSuivant]:
                            newOrigine = origine.cloneWithReplaceCible(item, itemSuivant)
                            ciblesList[item].append(newOrigine)
                            cloneList[index] = newOrigine
                    cloneList.pop(index+1)
                    del ciblesList[itemSuivant]
            else:
                index += 1

        return cloneList

    def getASM(self, engine):
        asm = AssembleurContainer()
        vm = VariableManager()
        cleanList = self.__cleanListClone(engine)
        asmDescList = []
        for item in cleanList:
            asmDescList += item.getAsmDescList(engine, vm)
        haltAsmDesc = engine.getAsmDesc({"operator":"halt"})
        asmDescList.append(haltAsmDesc)
        # à ce stade les seuls ayant un label n'ont pas d'opération,
        # on peut poursser le label sur le suivant
        index = 0
        while index < len(asmDescList)-1:
            item = asmDescList[index]
            if "label" in item:
                itemSuivant = asmDescList[index+1]
                itemSuivant["label"] = item["label"]
                asmDescList.pop(index)
            index += 1
        # extraction des grands littéraux
        index = 0
        while index < len(asmDescList):
            item = asmDescList[index]
            if "litteralNextLine" in item:
                litteral = item["litteralNextLine"]
                lineNumber = item["lineNumber"]
                newItem = { "litteral": litteral, "lineNumber":lineNumber }
                del item["litteralNextLine"]
                asmDescList.insert(index+1, newItem)
            index += 1
        baseMemoryIndex = len(asmDescList)
        for item in asmDescList:
            binaryCode = engine.getBinary(item, vm, baseMemoryIndex)
            if binaryCode != None:
                item["binary"] = binaryCode
        variablesList = vm.getVariableForAsm()
        for v in variablesList:
            asmDescList.append({ "variable": v})
        for item in asmDescList:
            asm.pushLine(item)

        return asm

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
            self.__ifLineNumber, self.__elseLineNumber = lineNumber
        else:
            self.__ifLineNumber, self.__elseLineNumber = lineNumber, None

    def __str__(self):
        if self.__elseChildren.isEmpty():
            return "if ("+str(self.__condition)+") {\n"+str(self.__ifChildren)+"\n}"
        else:
            return "if "+str(self.__condition)+" {\n"+str(self.__ifChildren)+"\n}\nelse {\n"+str(self.__elseChildren)+"\n}"

    def getLinearItemsList(self):
        linearIf = self.__ifChildren.getLinearItemsList()
        labelIf = LabelElement(self.__ifLineNumber, "_i")
        labelFin = LabelElement(self.__ifLineNumber, "_ie")

        conditionInverse = self.__condition.logicNegateClone()
        if not self.__elseChildren.isEmpty():
            linearElse = self.__elseChildren.getLinearItemsList()
            labelElse = LabelElement(self.__elseLineNumber, "_el")
            sautFin = JumpElement(self.__ifLineNumber, labelFin)
            test = TestElement.decomposeComplexeCondition(self.__ifLineNumber, conditionInverse, labelElse, labelIf)
            return test + [ labelIf ] + linearIf + [ sautFin, labelElse ] + linearElse + [ labelFin ]
        test = TestElement.decomposeComplexeCondition(self.__ifLineNumber, conditionInverse, labelFin, labelIf)
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
        self.__lineNumber = lineNumber
        self.__condition = condition
        assert condition.getType() == 'bool'
        self.__children = Container(children)

    def __str__(self):
        return "while "+str(self.__condition)+" {\n"+str(self.__children)+"\n}"

    def getLinearItemsList(self):
        linear = self.__children.getLinearItemsList()
        labelWhile = LabelElement(self.__lineNumber, "_w")
        labelDebut = LabelElement(self.__lineNumber, "_wb")
        labelFin = LabelElement(self.__lineNumber, "_we")
        conditionInverse = self.__condition.logicNegateClone()
        test = TestElement.decomposeComplexeCondition(self.__lineNumber, conditionInverse, labelFin, labelDebut)
        saut = JumpElement(self.__lineNumber, labelWhile)
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
        self.__lineNumber = lineNumber
        self.__cible = variableCible
        assert expression.getType() == 'int'
        self.__expression = expression

    def __str__(self):
        return str(self.__cible)+" "+chr(0x2190)+" "+str(self.__expression)

    def getAsmDescList(self, engine, vm):
        '''
        engine = ProcessorEngine
        vm = VariableManager
        '''
        cem = self.__expression.calcCompile(engine = engine, variablemanager = vm)
        asmDescList = cem.getAsmDescList()
        resultRegister = cem.getResultRegister()
        storeAsmDesc = engine.getAsmDesc({"operator":"store", "operands":(resultRegister, self.__cible), "lineNumber":self.__lineNumber})
        asmDescList.append(storeAsmDesc)
        return asmDescList

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
        self.__lineNumber = lineNumber
        self.__cible = variableCible

    def __str__(self):
        return str(self.__cible)+" "+chr(0x2190)+" Input"

    def getAsmDescList(self, engine, vm):
        '''
        engine = ProcessorEngine
        vm = VariableManager
        '''
        operands = (self.__cible,)
        inputAsmDesc = engine.getAsmDesc({"operator":"input", "operands":operands, "lineNumber":self.__lineNumber})
        return [ inputAsmDesc ]

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
        self.__lineNumber = lineNumber
        assert expression.getType() == 'int'
        self.__expression = expression

    def __str__(self):
        return str(self.__expression)+" "+chr(0x2192)+" Affichage"

    def getAsmDescList(self, engine, vm):
        '''
        engine = ProcessorEngine
        vm = VariableManager
        '''
        cem = self.__expression.calcCompile(engine = engine, variablemanager = vm)
        asmDescList = cem.getAsmDescList()
        resultRegister = cem.getResultRegister()
        printASMDesc = engine.getAsmDesc({"operator":"print", "operands":(resultRegister,), "lineNumber":self.__lineNumber})
        asmDescList.append(printASMDesc)
        return asmDescList

    def getLinearItemsList(self):
        return [ self ]

class LabelElement:
    def __init__(self, lineNumber, label):
        self.__label = label
        self.__lineNumber = lineNumber

    def __str__(self):
        return chr(0x2386)+ self.getStrLabel()

    def getAsmDescList(self, engine, vm):
        '''
        engine = ProcessorEngine
        vm = VariableManager
        '''
        labelAsmDesc = { "label": self.getStrLabel() }
        return [ labelAsmDesc ]

    def getLinearItemsList(self):
        return [ self ]

    def getStrLabel(self):
        return self.__label + str(self.__lineNumber)

class JumpElement:
    def __init__(self, lineNumber, cible):
        assert isinstance(cible, LabelElement)
        self.__lineNumber = lineNumber
        self.__cible = cible

    def __str__(self):
        return "Saut "+str(self.__cible)

    def getCible(self):
        return self.__cible

    def getAsmDescList(self, engine, vm):
        '''
        engine = ProcessorEngine
        vm = VariableManager
        '''
        cible = self.__cible.getStrLabel()
        jumpAsmDesc = engine.getAsmDesc({"operator":"goto", "operands":(cible,), "lineNumber":self.__lineNumber})
        return [ jumpAsmDesc ]

    def getLinearItemsList(self):
        return [ self ]

    def cloneWithReplaceCible(self, nouvelleCible, ciblePrecendente):
        if self.__cible == ciblePrecendente:
            return JumpElement(self.__lineNumber, nouvelleCible)
        return self

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
        self.__lineNumber = lineNumber
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
        return TestElement(self.__lineNumber, negConditionClone, self.__cibleNON, self.__cibleOUI)

    def mirrorClone(self):
        conditionMirrorClone = self.__condition.comparaisonMirrorClone()
        return TestElement(self.__lineNumber, conditionMirrorClone, self.__cibleOUI, self.__cibleNON)

    def clearCibleNonClone(self):
        return TestElement(self.__lineNumber, self.__condition, self.__cibleOUI, None)

    def getCibleNon(self):
        return self.__cibleNON

    def getCibles(self):
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

    def getAsmDescList(self, engine, vm):
        '''
        engine = ProcessorEngine
        vm = VariableManager
        '''
        comparator = self.__condition.getComparaisonSymbol()
        assert engine.hasOperator(comparator)
        cem = self.__condition.calcCompile(engine = engine, variablemanager = vm)
        asmDescList = cem.getAsmDescList()
        cibleOui = self.__cibleOUI.getStrLabel()
        conditionalGotoAsmDesc = engine.getAsmDesc({"operator":comparator, "operands":(cibleOui,), "lineNumber":self.__lineNumber})
        asmDescList.append(conditionalGotoAsmDesc)
        if self.__cibleNON == None:
            return asmDescList
        cibleNon = self.__cibleNON.getStrLabel()
        gotoAsmDesc = engine.getAsmDesc({"operator":"goto", "operands":(cibleNon,), "lineNumber":self.__lineNumber})
        asmDescList.append(gotoAsmDesc)
        return asmDescList

    def getLinearItemsList(self):
        return [ self ]

    def cloneWithReplaceCible(self, nouvelleCible, ciblePrecendente):
        if self.__cibleOUI != ciblePrecendente and self.__cibleNON != ciblePrecendente:
            return self
        if self.__cibleOUI == ciblePrecendente:
            nouvelleCibleOui = nouvelleCible
        else:
            nouvelleCibleOui = self.__cibleOUI
        if self.__cibleNON == ciblePrecendente:
            nouvelleCibleNon = nouvelleCible
        else:
            nouvelleCibleNon = self.__cibleNON
        return TestElement(self.__lineNumber, self.__condition, nouvelleCibleOui, nouvelleCibleNon)

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
    print(str(asmCode))



