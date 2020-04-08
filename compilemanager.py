"""
.. module:: compilemanager
    :synopsis: gestion de la compilation
"""
from typing import List, Dict, Optional, Tuple

from errors import *
from structuresnodes import *
from assembleurcontainer import AssembleurContainer
from compileexpressionmanager import CompileExpressionManager
from processorengine import ProcessorEngine

class CompilationManager:
    __engine:ProcessorEngine
    __linearList:List[StructureNode]
    __asm:AssembleurContainer
    def __init__(self, engine:ProcessorEngine, structureNodeList:List[StructureNode]):
        """Constructeur

        :param engine: objet décrivant le modèle de processeur
        :type engine: ProcessorEngine
        :param structureNodeList: liste de noeuds décrivant le programme à compiler
        :type structureNodeList: list(StructureNode)

        .. note::

        Fait immédiatement la compilation et crée un objet assembleur pour stocker le résultat.
        la liste fournie n'est pas stockée, on en produit une forme linéaire (while et if transformé) aussitôt.
        """
        self.__engine = engine
        self.__asm = AssembleurContainer(self.__engine)
        self.__linearList = self.__compile(structureNodeList)
        self.__compileASM()

    def __compile(self, structureNodeList:List[StructureNode]) -> List[StructureNode]:
        """Linéarise le programme fourni. Les while et if sont transformés en itilisant des sauts conditionnels ou non.

        :param structureNodeList: liste de noeuds décrivant le programme à compiler
        :type structureNodeList: list[StructureNode]
        :return: programme sous sa forme linéaire.
        :rtype: list[StructureNode]

        .. note::

        La création des sauts conditionnels suppose de connaître les possibilités du processeur concernant les tests disponibles. On demande donc au modèle de processeur les tests disponibles.
        """
        comparaisonSymbolsAvailables = self.__engine.getComparaisonSymbolsAvailables()
        for node in structureNodeList:
            assert isinstance(node, StructureNode)
        linearList = []
        for node in structureNodeList:
            linearForNode = node.getLinearStructureList(comparaisonSymbolsAvailables)
            linearList.extend(linearForNode)
        self.__cleanList(linearList)
        self.__plugLabels(linearList)
        return linearList

    def __str__(self) -> str:
        """Transtypage -> str

        :return: programme linéarisé en version texte
        :rtype: str
        """
        return "\n".join([str(item) for item in self.__linearList])

    def __getLabels(self, linearList:List[StructureNode]) -> Dict[LabelNode,List[JumpNode]]:
        """Fournit un dictionnaire donnant toutes les étiquettes jointes à tous les sauts pointant sur elles.

        :param linearList: liste de noeuds de la version linéaire
        :type linearList: list[StructureNode]
        :return: dictionnaire de forme étiquette -> liste des sauts pointant sur cette étiquette
        :rtype: dict[LabelNode,list[JumpNode]]
        """
        labels:Dict[LabelNode,List[JumpNode]] = {}
        for node in linearList:
            if isinstance(node,LabelNode):
                labels[node] = []
        # association jump -> label
        for node in linearList:
            if isinstance(node,JumpNode):
                cible = node.cible
                if not cible in labels:
                    raise CompilationError("Saut vers label inconnu : "+str(cible), {"lineNumber":node.lineNumber})
                labels[cible].append(node)
        return labels

    def __delJumpToNextLine(self, linearList:List[StructureNode]) -> bool:
        """Efface les sauts, conditionnels ou non, consistant à sauter à la ligne suivante.
        En effet, le déroulement normal du programme est de passer à la ligne suivante, de tels
        sauts sont donc superflus.
        :param linearList: liste de noeuds de la version linéaire
        :type linearList: list[StructureNode]
        :return: vrai si un changement a été effectué
        :rtype: bool
        """
        flagActionDone = False
        if len(linearList) < 2:
            return False
        index = 0
        while index < len(linearList)-1:
            currentNode = linearList[index]
            nextNode = linearList[index+1]
            if isinstance(currentNode,JumpNode) and currentNode.cible == nextNode:
                linearList.pop(index)
                flagActionDone = True
            else:
                index += 1
        return flagActionDone

    def __delNotUseLabel(self, linearList:List[StructureNode]) -> bool:
        """Efface les étiquettes qui ne sont jamais utilisées. ie : qui ne sont la cible d'aucun saut.
        :param linearList: liste de noeuds de la version linéaire
        :type linearList: list[StructureNode]
        :return: vrai si un changement a été fait
        :rtype: bool
        """
        flagActionDone = False
        labels = self.__getLabels(linearList)
        for label, listeJumps in labels.items():
            if len(listeJumps) == 0:
                flagActionDone = True
                indexToDel = linearList.index(label)
                linearList.pop(indexToDel)
        return flagActionDone

    def __cleanList(self, linearList:List[StructureNode]) -> None:
        """Nettoie la liste linéaire en
        supprimant les étiquettes non utilisées,
        supprimant les sauts pointant vers la ligne suivante.

        :param linearList: liste de noeuds de la version linéaire
        :type linearList: list[StructureNode]
        :return: pas de retour, liste modifiée en place
        """
        goOnFlag = True
        while goOnFlag:
            goOnFlag = False
            goOnFlag = self.__delNotUseLabel(linearList) or goOnFlag
            goOnFlag = self.__delJumpToNextLine(linearList) or goOnFlag

    def __plugLabels(self, linearList:List[StructureNode]) -> None:
        """Branche les noeuds labels au noeud suivant
        dans le but de fusionner les noeuds consécutifs

        :param linearList: liste de noeuds de la version linéaire
        :type linearList: list[StructureNode]
        """
        for index in range(len(linearList)-1):
            item = linearList[index]
            if isinstance(item, LabelNode):
                nextItem = linearList[index+1]
                if not item.plugTo(nextItem):
                    raise CompilationError("Branchement noeud impossible ", {"lineNumber":item.lineNumber})

    def __pushExpressionAsm(self, lineNumber:int, label:Optional[Label], expression:ExpressionNode) -> int:
        """Gère la compilation d'une expression arithmétique ou logique

        :param lineNumber: numéro de ligne d'origine de l'expression
        :type lineNumber: int
        :param label: label du début de l'expression
        :type label: Optional[Label]
        :param expression: expression à compiler
        :type expression: ExpressionNode
        :return: numéro du registre résultat ou -1 si inutile (comparaison)
        :rtype: int
        """
        if not self.__engine.hasNEG():
            expression = expression.negToSubClone()
        cem = CompileExpressionManager(self.__engine, self.__asm, lineNumber, label)
        expression.compile(cem)
        if expression.getType() == 'int':
            return cem.getResultRegister()
        return -1

    def __pushNodeAsm(self, node:StructureNode) -> None:
        """Exécute la compilation pour un noeud. Le résultat est ajouté à l'objet assembleur.

        :param node: noeud à compiler
        :type node: StructureNode
        :return: pas de retour.
        """
        lineNumber = node.lineNumber
        if isinstance(node, AffectationNode):
            resultRegister = self.__pushExpressionAsm(lineNumber, node.label, node.expression)
            self.__asm.pushStore(lineNumber, None, resultRegister, node.cible)
            return
        if isinstance(node, InputNode):
            self.__asm.pushInput(lineNumber, node.label, node.cible)
            return
        if isinstance(node, PrintNode):
            resultRegister = self.__pushExpressionAsm(lineNumber, node.label, node.expression)
            self.__asm.pushPrint(lineNumber, resultRegister)
            return
        if isinstance(node, JumpNode):
            labelCible = node.cible.label
            condition = node.getCondition()
            if not isinstance(condition,ExpressionNode):
                self.__asm.pushJump(lineNumber, node.label, labelCible)
                return
            comparaisonSymbol = condition.getComparaisonSymbol()
            self.__pushExpressionAsm(lineNumber, node.label, condition)
            self.__asm.pushJump(lineNumber, None, labelCible, comparaisonSymbol)

    def __compileASM(self) -> None:
        """Produit le code assembleur et conclut par HALT.
        Le résultat est stocké directement dans l'objet assembleur créé à l'initialisation.

        :return: pas de retour
        """
        for node in self.__linearList:
            self.__pushNodeAsm(node)
        haltLabel = None
        if len(self.__linearList)>0:
            lastItem = self.__linearList[-1]
            if isinstance(lastItem, LabelNode) and lastItem.isUnplugged():
                haltLabel = lastItem.label
        self.__asm.pushHalt(haltLabel)

    def getLinearNodeList(self) -> List[StructureNode]:
        """Accesseur

        :return: programme sous forme linéaire
        :rtype: list[StructureNode]
        """
        return [item for item in self.__linearList]

    def getAsm(self) -> AssembleurContainer:
        """Accesseur

        :return: objet assembleur contenant le résultat de la compilation
        :rtype: AssembleurContainer
        """
        return self.__asm

if __name__=="__main__":
    from expressionparser import ExpressionParser
    from processorengine import ProcessorEngine
    EP = ExpressionParser()
    engine = ProcessorEngine()

    varX = Variable('x')
    varY = Variable('y')

    affectationX = AffectationNode(4, varX, EP.buildExpression('-3*x+1'))
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
    print()
    print(cm.getAsm().getBinary())
