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
    _engine:ProcessorEngine
    _linearList:StructureNodeList
    _asm:AssembleurContainer
    def __init__(self, engine:ProcessorEngine, listOfStructureNodes:List[StructureNode]):
        """Constructeur

        :param engine: objet décrivant le modèle de processeur
        :type engine: ProcessorEngine
        :param listOfStructureNodes: liste de noeuds décrivant le programme à compiler
        :type listOfStructureNodes: list[StructureNode]

        .. note::

        Fait immédiatement la compilation et crée un objet assembleur pour stocker le résultat.
        la liste fournie n'est pas stockée, on en produit une forme linéaire (while et if transformé) aussitôt.
        """
        self._engine = engine
        self._asm = AssembleurContainer(self._engine)
        self._linearList = StructureNodeList(listOfStructureNodes)
        comparaisonSymbolsAvailables = self._engine.getComparaisonSymbolsAvailables()
        self._linearList.linearize(comparaisonSymbolsAvailables)
        self.__compileASM()

    def __str__(self) -> str:
        """Transtypage -> str

        :return: programme linéarisé en version texte
        :rtype: str
        """
        return "\n".join([str(item) for item in self._linearList])

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
        if not self._engine.hasNEG():
            expression = expression.negToSubClone()
        cem = CompileExpressionManager(self._engine, self._asm, lineNumber, label)
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
            self._asm.pushStore(lineNumber, None, resultRegister, node.cible)
            return
        if isinstance(node, InputNode):
            self._asm.pushInput(lineNumber, node.label, node.cible)
            return
        if isinstance(node, PrintNode):
            resultRegister = self.__pushExpressionAsm(lineNumber, node.label, node.expression)
            self._asm.pushPrint(lineNumber, resultRegister)
            return
        if isinstance(node, JumpNode):
            labelCible = node.cible.label
            condition = node.getCondition()
            if not isinstance(condition,ExpressionNode):
                self._asm.pushJump(lineNumber, node.label, labelCible)
                return
            comparaisonSymbol = condition.getComparaisonSymbol()
            self.__pushExpressionAsm(lineNumber, node.label, condition)
            self._asm.pushJump(lineNumber, None, labelCible, comparaisonSymbol)
        if isinstance(node, SimpleNode) and node.snType == 'halt':
            self._asm.pushHalt(node.label)

    def __compileASM(self) -> None:
        """Produit le code assembleur et conclut par HALT.
        Le résultat est stocké directement dans l'objet assembleur créé à l'initialisation.

        :return: pas de retour
        """
        for node in self._linearList.toList():
            self.__pushNodeAsm(node)

    @property
    def asm(self) -> AssembleurContainer:
        """Accesseur

        :return: objet assembleur contenant le résultat de la compilation
        :rtype: AssembleurContainer
        """
        return self._asm

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
    print(cm.asm)
    print()
    print(cm.asm.getBinary())
