"""
.. module:: compilemanager
:synopsis: gestion de la compilation. La classe CompilationManager reçoit une liste
    d'instructions sous une forme structurée StructureNode, comprenant des noeuds d'affectation,
    affichage, saisie clavier, et des noeuds de structure if, else et while.

    * Le compilateur transforme les if, else, while en des suites de sauts
    * les expression arithmétiques sont transformées en suite d'instruction exécutable par
        le processeur
    * les conditions logiques composées sont découpées en comparaisons élémentaires et
        assurées par des jeux de sauts conditionnels adéquats
    * CompilationManager produit un objet AssembleurContainer contenant le code assembleur

.. note:: CompilationManager délègue à CompileExpressionManager la compilation des
    expressions arithmétiques.
"""
from typing import List, Dict, Optional, Tuple

from primitives.label import Label

from structuresnodes import StructureNode, StructureNodeList, JumpNode, InputNode, SimpleNode, AffectationNode, PrintNode

from assembleurcontainer import AssembleurContainer
from compileexpressionmanager import CompileExpressionManager
from processorengine import ProcessorEngine
from arithmeticexpressionnodes import ArithmeticExpressionNode
from comparaisonexpressionnodes import ComparaisonExpressionNode


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
        print(self._linearList)
        self._linearList.linearize(comparaisonSymbolsAvailables)
        self._compileASM()

    def __str__(self) -> str:
        """Transtypage -> str

        :return: programme linéarisé en version texte
        :rtype: str
        """
        return "\n".join([str(item) for item in self._linearList])

    def _pushArithmeticAsm(self, lineNumber:int, label:Optional[Label], expression:ArithmeticExpressionNode) -> int:
        """Gère la compilation d'une expression arithmétique

        :param lineNumber: numéro de ligne d'origine de l'expression
        :type lineNumber: int
        :param label: label du début de l'expression
        :type label: Optional[Label]
        :param expression: expression à compiler
        :type expression: ArithmeticExpressionNode
        :return: numéro du registre résultat ou -1 si inutile (comparaison)
        :rtype: int
        """
        fifo = expression.getFIFO(self._engine.litteralMaxSize)
        cem = CompileExpressionManager(self._engine, lineNumber)
        cem.compile(fifo)
        return cem.getResultRegister()

    def _pushComparaisonAsm(self, lineNumber:int, label:Optional[Label], condition:ComparaisonExpressionNode) -> None:
        """Gère la compilation d'une expression de comparaison

        :param lineNumber: numéro de ligne d'origine de l'expression
        :type lineNumber: int
        :param label: label du début de l'expression
        :type label: Optional[Label]
        :param condition: comparaison à compiler
        :type condition: ComparaisonExpressionNode
        """
        fifo = condition.getFIFO(self._engine.litteralMaxSize)
        cem = CompileExpressionManager(self._engine, lineNumber)
        cem.compile(fifo)

    def _pushNodeAsm(self, node:StructureNode) -> None:
        """Exécute la compilation pour un noeud. Le résultat est ajouté à l'objet assembleur.

        :param node: noeud à compiler
        :type node: StructureNode
        :return: pas de retour.
        """
        lineNumber = node.lineNumber
        if isinstance(node, AffectationNode):
            resultRegister = self._pushArithmeticAsm(lineNumber, node.label, node.expression)
            self._asm.pushStore(lineNumber, None, resultRegister, node.cible)
            return
        if isinstance(node, InputNode):
            self._asm.pushInput(lineNumber, node.label, node.cible)
            return
        if isinstance(node, PrintNode):
            resultRegister = self._pushArithmeticAsm(lineNumber, node.label, node.expression)
            self._asm.pushPrint(lineNumber, resultRegister)
            return
        if isinstance(node, JumpNode):
            labelCible = node.cible.assignLabel()
            condition = node.getCondition()
            if not isinstance(condition, ComparaisonExpressionNode):
                self._asm.pushJump(lineNumber, node.label, labelCible)
                return
            comparaisonSymbol = condition.comparaisonSymbol
            self._pushComparaisonAsm(lineNumber, node.label, condition)
            self._asm.pushJump(lineNumber, None, labelCible, comparaisonSymbol)
        if isinstance(node, SimpleNode) and node.snType == 'halt':
            self._asm.pushHalt(node.label)

    def _compileASM(self) -> None:
        """Produit le code assembleur et conclut par HALT.
        Le résultat est stocké directement dans l'objet assembleur créé à l'initialisation.

        :return: pas de retour
        """
        for node in self._linearList.toList():
            self._pushNodeAsm(node)

    @property
    def asm(self) -> AssembleurContainer:
        """Accesseur

        :return: objet assembleur contenant le résultat de la compilation
        :rtype: AssembleurContainer
        """
        return self._asm

if __name__=="__main__":
    from expressionparser import ExpressionParser as EP
    from processor16bits import Processor16Bits
    from primitives.variable import Variable
    from structuresnodes import WhileNode
    from codeparser import CodeParser

    engine = Processor16Bits()

    varX = Variable('x')
    varY = Variable('y')

    affectationX = AffectationNode(4, varX, EP.buildExpression('-3*x+1')) # mypy: ignore
    affectationY = AffectationNode(5, varY, EP.buildExpression('y+x')) # mypy: ignore
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

    print()
    print()
    code = CodeParser.parse(filename = "example2.code")
    cm = CompilationManager(engine, code)
    print(cm.asm)