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
from structuresnodes import *
from assembleurcontainer import *

# partie manager

class CompilationManager:
    def __init__(self, engine):
        '''
        engine = ProcessorEngine object
        '''
        self.__engine = engine
    def compile(self, structureNodeList):
        '''
        structureNodeList = List d'items StructureNode
        '''
        comparaisonSymbolsAvailables = engine.getComparaisonSymbolsAvailables()
        for node in structureNodeList:
            assert isinstance(node, StructureNode)
        linearList = []
        for node in structureNodeList:
            linearForNode = node.getLinearStructureList(comparaisonSymbolsAvailables)
            linearList.extend(linearForNode)
        return linearList

    def __str__(self):
        return "\n".join([str(item) for item in self.__linearList])

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

    def getASM(self, engine, vm):
        '''
        engine = EngineProcessor : modèle de processeur
        vm = VariableManager
        '''
        asm = AssembleurContainer()
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
        # extraction des adresses de saut
        labelIndexList = {}
        for index, asmDesc in enumerate(asmDescList):
            if "label" in asmDesc:
                label = asmDesc["label"]
                labelIndexList[label] = index
        variablesList = vm.getVariableForAsm()
        for v in variablesList:
            asmDescList.append({ "data": v })
        for item in asmDescList:
            binaryCode = engine.getBinary(item, vm, baseMemoryIndex, labelIndexList)
            item["binary"] = binaryCode
        for item in asmDescList:
            asm.pushLine(item)

        return asm







'''
class AffectationElement:
    def getAsmDescList(self, engine, vm):
        cem = self.__expression.calcCompile(engine = engine, variablemanager = vm)
        asmDescList = cem.getAsmDescList()
        resultRegister = cem.getResultRegister()
        storeAsmDesc = engine.getAsmDesc({"operator":"store", "operands":(resultRegister, self.__cible), "lineNumber":self.__lineNumber})
        asmDescList.append(storeAsmDesc)
        return asmDescList


class InputElement:
    def getAsmDescList(self, engine, vm):
        operands = (self.__cible,)
        inputAsmDesc = engine.getAsmDesc({"operator":"input", "operands":operands, "lineNumber":self.__lineNumber})
        return [ inputAsmDesc ]

class PrintElement:
    def getAsmDescList(self, engine, vm):
        cem = self.__expression.calcCompile(engine = engine, variablemanager = vm)
        asmDescList = cem.getAsmDescList()
        resultRegister = cem.getResultRegister()
        printASMDesc = engine.getAsmDesc({"operator":"print", "operands":(resultRegister,), "lineNumber":self.__lineNumber})
        asmDescList.append(printASMDesc)
        return asmDescList



class JumpElement:
    def getCible(self):
        return self.__cible

    def getAsmDescList(self, engine, vm):
        cible = self.__cible.getStrLabel()
        jumpAsmDesc = engine.getAsmDesc({"operator":"goto", "operands":(cible,), "lineNumber":self.__lineNumber})
        return [ jumpAsmDesc ]

    def cloneWithReplaceCible(self, nouvelleCible, ciblePrecendente):
        if self.__cible == ciblePrecendente:
            return JumpElement(self.__lineNumber, nouvelleCible)
        return self

class TestElement:



    def getAsmDescList(self, engine, vm):
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
'''

if __name__=="__main__":
    from expressionparser import ExpressionParser
    from variablemanager import VariableManager
    from processorengine import ProcessorEngine
    VM = VariableManager()
    EP = ExpressionParser(VM)
    engine = ProcessorEngine()

    varX = VM.addVariableByName('x')
    varY = VM.addVariableByName('y')
    expr = EP.buildExpression('3*x+2')

    affectationX = AffectationNode(4, varX, EP.buildExpression('x+1'))
    affectationY = AffectationNode(5, varY, EP.buildExpression('y+x'))
    structuredList = [
        AffectationNode(1, varX, EP.buildExpression('0')),
        AffectationNode(2, varY, EP.buildExpression('0')),
        WhileNode(3, EP.buildExpression('x < 10 or y < 100'), [affectationX, affectationY]),
        PrintNode(6, EP.buildExpression('y'))
    ]

    cm = CompilationManager(engine)
    listCompiled = cm.compile(structuredList)
    for item in listCompiled:
        print(item)








    '''
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
    asmCode = c.getASM(engine, VM)
    print()
    print("Version assembleur")
    print()
    print(str(asmCode))
    print(asmCode.getBinary())
    '''



