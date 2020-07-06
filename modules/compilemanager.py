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

from modules.errors import CompilationError
from modules.primitives.label import Label
from modules.structuresnodes import StructureNode, StructureNodeList, JumpNode, SimpleNode, TransfertNode
from modules.compileexpressionmanager import CompileExpressionManager
from modules.engine.processorengine import ProcessorEngine
from modules.primitives.actionsfifo import ActionsFIFO
from modules.primitives.register import RegistersManager
from modules.primitives.operators import Operators

#from assembleurcontainer import AssembleurContainer

class CompilationManager:
    _engine:ProcessorEngine
    _linearList:StructureNodeList
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
        self._linearList = StructureNodeList(listOfStructureNodes)
        comparaisonSymbolsAvailables = self._engine.getComparaisonSymbolsAvailables()
        self._linearList.linearize(comparaisonSymbolsAvailables)

    def compile(self) -> List[ActionsFIFO]:
        registers = RegistersManager(self._engine.registersNumber())
        return [self._compileNode(node, registers) for node in self._linearList]

    def __str__(self) -> str:
        """Transtypage -> str

        :return: programme linéarisé en version texte
        :rtype: str
        """
        return "\n".join([str(item) for item in self._linearList])

    def _compileNode(self, node:StructureNode, registers:RegistersManager) -> ActionsFIFO:
        """Exécute la compilation pour un noeud. Le résultat est ajouté à l'objet assembleur.

        :param node: noeud à compiler
        :type node: StructureNode
        :param registers: gestionnaire de registres
        :type registers: RegostersManager
        :return: le maillon numéro de ligne, label, action fifo
        :rtype: ActionsFIFO
        """
        
        if isinstance(node, TransfertNode):
            expression = node.expression
            if not expression is None:
                fifo = expression.getFIFO(self._engine.litteralMaxSize)
                cem = CompileExpressionManager(self._engine, registers)
                actionsItem = cem.compile(fifo)
                resultRegister = registers.pop()
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

        elif isinstance(node, JumpNode):
            labelCible = node.cible.assignLabel()
            condition = node.getCondition()
            if condition is None:
                actionsItem = ActionsFIFO()
            else:
                fifo = condition.getFIFO(self._engine.litteralMaxSize)
                cem = CompileExpressionManager(self._engine, registers)
                actionsItem = cem.compile(fifo)
            actionsItem.append(labelCible, Operators.GOTO)

        elif isinstance(node, SimpleNode) and not node.operator is None:
            actionsItem = ActionsFIFO()
            actionsItem.append(node.operator)

        else:
            raise CompilationError("Noeud non reconnu", {"lineNumber": node.lineNumber})

        actionsItem.setLabel(node.label)
        actionsItem.setLineNumber(node.lineNumber)
        return actionsItem

