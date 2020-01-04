from errors import *
from structuresnodes import *
from assembleurcontainer import *
from compileexpressionmanager import CompileExpressionManager

class CompilationManager:
    def __init__(self, engine, structureNodeList):
        '''
        engine = ProcessorEngine object
        structureNodeList = List d'items StructureNode
        '''
        self.__engine = engine
        self.__asm = AssembleurContainer(self.__engine)
        self.__linearList = self.__compile(structureNodeList)
        self.__compileASM()

    def __compile(self, structureNodeList):
        '''
        structureNodeList = List d'items StructureNode
        '''
        comparaisonSymbolsAvailables = self.__engine.getComparaisonSymbolsAvailables()
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

    def __pushExpressionAsm(self, expression):
        '''
        expression : objet Expression
        '''
        if not self.__engine.hasNEG():
            expression = expression.negToSubClone()
        cem = CompileExpressionManager(self.__engine, self.__asm)
        expression.compile(cem)
        return cem.getResultRegister()

    def __pushNodeAsm(self, node):
        if isinstance(node, LabelNode):
            self.__asm.pushLabel(str(node))
            return
        if isinstance(node, AffectationNode):
            expression = node.getExpression()
            cible = node.getCible()
            resultRegister = self.__pushExpressionAsm(expression)
            self.__asm.pushStore(resultRegister, cible)
            return
        if isinstance(node, InputNode):
            cible = node.getCible()
            self.__asm.pushInput(cible)
            return
        if isinstance(node, PrintNode):
            expression = node.getExpression()
            resultRegister = self.__pushExpressionAsm(expression)
            self.__asm.pushPrint(resultRegister)
            return
        if isinstance(node, JumpNode):
            cible = node.getCible()
            condition = node.getCondition()
            if condition == None:
                self.__asm.pushJump(cible)
                return
            comparaisonSymbol = condition.getComparaisonSymbol()
            self.__pushExpressionAsm(condition)
            self.__asm.pushJump(cible, comparaisonSymbol)

    def __compileASM(self):
        for node in self.__linearList:
            self.__pushNodeAsm(node)
        self.__asm.pushHalt()

    def getLinearNodeList(self):
        return [item for item in self.__linearList]

    def getAsm(self):
        return self.__asm

if __name__=="__main__":
    from expressionparser import ExpressionParser
    from processorengine import ProcessorEngine
    EP = ExpressionParser()
    engine = ProcessorEngine()

    varX = Variable('x')
    varY = Variable('y')
    expr = EP.buildExpression('3*x+2')

    affectationX = AffectationNode(4, varX, EP.buildExpression('x+1'))
    affectationY = AffectationNode(5, varY, EP.buildExpression('y+x'))
    structuredList = [
        AffectationNode(1, varX, EP.buildExpression('0')),
        AffectationNode(2, varY, EP.buildExpression('0')),
        WhileNode(3, EP.buildExpression('x < 10 or y < 100'), [affectationX, affectationY]),
        PrintNode(6, EP.buildExpression('y'))
    ]

    cm = CompilationManager(engine, structuredList)
    listCompiled = cm.getLinearNodeList()
    for item in listCompiled:
        print(item)
    print()
    print(cm.getAsm())
