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

    def compile(self, structureNodeList, variableManager):
        '''
        structureNodeList = List d'items StructureNode
        variableManager = objet VariableManager
        '''
        comparaisonSymbolsAvailables = engine.getComparaisonSymbolsAvailables()
        for node in structureNodeList:
            assert isinstance(node, StructureNode)
        linearList = []
        for node in structureNodeList:
            linearForNode = node.getLinearStructureList(comparaisonSymbolsAvailables)
            linearList.extend(linearForNode)
        self.__cleanList(linearList)
        return linearList

    def __str__(self):
        return "\n".join([str(item) for item in self.__linearList])

    def __delJumpToNextLine(self, linearList):
        '''
        linearList = liste de noeuds de types :
            LabelNode, AffectationNode, InputNode, PrintNode, JumpNode
        Sortie : True si un changement a été effectué
        '''
        flagActionDone = False
        if len(linearList) < 2:
            return linearList, False
        index = 0
        while index < len(linearList)-1:
            currentNode = linearList[index]
            nextNode = linearList[index+1]
            if isinstance(currentNode,JumpNode) and currentNode.getCible() == nextNode:
                linearList.pop(index)
                flagActionDone = True
            else:
                index += 1
        return flagActionDone

    def __delNotUseLabel(self, linearList):
        '''
        linearList = liste de noeuds de types :
            LabelNode, AffectationNode, InputNode, PrintNode, JumpNode
        Sortie : True si un changement a été effectué
        '''
        flagActionDone = False
        labels = self.__getLabels(linearList)
        for label, listeJumps in labels.items():
            if len(listeJumps) == 0:
                flagActionDone = True
                indexToDel = linearList.index(label)
                linearList.pop(indexToDel)
        return flagActionDone

    def __fusionNodeLabel(self, linearList, label, labelToDel):
        '''
        linearList = liste de noeuds de types :
            LabelNode, AffectationNode, InputNode, PrintNode, JumpNode
        label, labelToDel = LabelNode
        tout jumpNode pointant vers labelToDel est redirigé vers label
        labelToDel supprimé de la liste
        Sortie = True si un changement a été effectué
        '''
        flagActionDone = False
        for index in range(len(linearList)):
            node = linearList(index)
            if isinstance(node,JumpNode) and node.getCible() == labelToDel:
                flagActionDone = True
                linearList[index] = node.assignNewCibleClone(label)
        if labelToDel in linearList:
            indexToDel = linearList.index(labelToDel)
            linearList.pop(indexToDel)
            flagActionDone = True
        return flagActionDone

    def __getLabels(self, linearList):
        '''
        linearList = liste de noeuds de types :
            LabelNode, AffectationNode, InputNode, PrintNode, JumpNode
        Sortie : dict clé = LabelNode, value = list des JumpNode pointant vers ce LabelNode
        '''
        labels = {}
        for node in linearList:
            if isinstance(node,LabelNode):
                labels[node] = []
        # association jump -> label
        for node in linearList:
            if isinstance(node,JumpNode):
                cible = node.getCible()
                if not cible in labels:
                    raise CompilationError("Saut vers label inconnu : "+str(cible))
                labels[cible].append(node)
        return labels

    def __getConsecutivesLabel(self, linearList):
        '''
        linearList = liste de noeuds de types :
            LabelNode, AffectationNode, InputNode, PrintNode, JumpNode
        Sortie : tuple contenant une succession de deux NodeLabel, None si aucun
        '''
        for index in range(len(linearList)-1):
            node = linearList[index]
            nodeSuivant = linearList[index + 1]
            if isinstance(node, LabelNode) and isinstance(nodeSuivant, LabelNode):
                return (node,nodeSuivant)
        return None

    def __cleanList(self, linearList):
        '''
        linearList = liste de noeuds de types :
            LabelNode, AffectationNode, InputNode, PrintNode, JumpNode
        Sortie : liste "nettoyée" :
        - suppression des labels inutiles
        - suppression des gotos inutiles
        '''
        goOnFlag = True
        while goOnFlag:
            goOnFlag = False
            labelsSuccessifs = self.__getConsecutivesLabel(linearList)
            if labelsSuccessifs != None:
                label, labelToDel = labelsSuccessifs
                goOnFlag = self.__fusionNodeLabel(linearList, label, labelToDel)
            goOnFlag = self.__delNotUseLabel(linearList) or goOnFlag
            goOnFlag = self.__delJumpToNextLine(linearList) or goOnFlag


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

    def getAsmDescList(self, engine, vm):
        cible = self.__cible.getStrLabel()
        jumpAsmDesc = engine.getAsmDesc({"operator":"goto", "operands":(cible,), "lineNumber":self.__lineNumber})
        return [ jumpAsmDesc ]


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
    listCompiled = cm.compile(structuredList, VM)
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



