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
from typing_extensions import TypedDict

from modules.errors import CompilationError
from modules.primitives.label import Label
from modules.structuresnodes import StructureNode, StructureNodeList, JumpNode, SimpleNode, TransfertNode
from modules.compileexpressionmanager import CompileExpressionManager
from modules.engine.processorengine import ProcessorEngine
from modules.expressionnodes.arithmetic import ArithmeticExpressionNode
from modules.expressionnodes.comparaison import ComparaisonExpressionNode
from modules.primitives.actionsfifo import ActionsFIFO
from modules.primitives.register import RegistersManager
from modules.primitives.operators import Operators

#from assembleurcontainer import AssembleurContainer
LineAction = TypedDict('LineAction', {'lineNumber': int, 'label':Optional[Label], 'actions': ActionsFIFO})

class CompilationManager:
    _engine:ProcessorEngine
    _linearList:StructureNodeList
    _actionsList: List[LineAction]
    _registers: RegistersManager
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
        self._actionsList = []
        self._engine = engine
        self._registers = RegistersManager(self._engine.registersNumber())
        self._linearList = StructureNodeList(listOfStructureNodes)
        comparaisonSymbolsAvailables = self._engine.getComparaisonSymbolsAvailables()
        self._linearList.linearize(comparaisonSymbolsAvailables)
        self._actionsList = [self._compileNode(node) for node in self._linearList]

    def __str__(self) -> str:
        """Transtypage -> str

        :return: programme linéarisé en version texte
        :rtype: str
        """
        return "\n".join([str(item) for item in self._linearList])

    def _compileNode(self, node:StructureNode) -> LineAction:
        """Exécute la compilation pour un noeud. Le résultat est ajouté à l'objet assembleur.

        :param node: noeud à compiler
        :type node: StructureNode
        :return: le maillon numéro de ligne, label, action fifo
        :rtype: LineAction
        """
        
        if isinstance(node, TransfertNode):
            expression = node.expression
            if not expression is None:
                fifo = expression.getFIFO(self._engine.litteralMaxSize)
                cem = CompileExpressionManager(self._engine, self._registers)
                actionsItem = cem.compile(fifo)
                resultRegister = self._registers.pop()
                cible = node.cible
                if cible is None:
                    actionsItem.append(resultRegister, Operators.PRINT)
                else:
                    actionsItem.append(resultRegister, node.cible, Operators.STORE)
            else:
                cible = node.cible
                assert not cible is None
                actionsItem = ActionsFIFO()
                actionsItem.append(node.cible, Operators.INPUT)
            return {"lineNumber":node.lineNumber, "label":node.label, "actions":actionsItem}

        if isinstance(node, JumpNode):
            labelCible = node.cible.assignLabel()
            condition = node.getCondition()
            if condition is None:
                actionsItem = ActionsFIFO()
            else:
                fifo = condition.getFIFO(self._engine.litteralMaxSize)
                cem = CompileExpressionManager(self._engine, self._registers)
                actionsItem = cem.compile(fifo)
            actionsItem.append(labelCible, Operators.GOTO)
            return {"lineNumber":node.lineNumber, "label":node.label, "actions":actionsItem}

        if isinstance(node, SimpleNode) and not node.operator is None:
            actionsItem = ActionsFIFO()
            actionsItem.append(node.operator)
            return {"lineNumber":node.lineNumber, "label":node.label, "actions":actionsItem}

        raise CompilationError("Noeud non reconnu", {"lineNumber": node.lineNumber})

