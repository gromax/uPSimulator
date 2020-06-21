"""
.. module:: structuresnodes
   :synopsis: définition des noeuds constituant le programme dans sa version structurée : Instructions simples, conditions, boucles. Contribue à la transformation d'une version où les conditions et boucles sont assurés par des sauts inconditionnels / conditionnels. Cette version est qualifiée de version linéaire.
"""
from typing import List, Optional, Union, cast

#from arithmeticexpressionnodes import ArithmeticExpressionNode
#from comparaisonexpressionnodes import ComparaisonExpressionNode
#from logicexpressionnodes import LogicExpressionNode, NotNode, AndNode, OrNode
#from variable import Variable
#from label import Label
from logicexpressionnodes import *
from linkedlistnode import LinkedList, LinkedListNode

class StructureNodeList(LinkedList):
    def linearize(self, csl:List[str]) -> None:
        """Crée la vesion linéaire de l'ensemble de la structure

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        """
        haltNode = SimpleNode("halt")
        self.append(haltNode)
        self._linearizeRecursive(csl)
        # une fois ceci fait, on supprime les jump qui pointeraient vers le noeud suivant et les dummies
        self._deleteJumpNextLine()
        self._deleteDummies()
        # enfin il faut assigner tous les labels
        self._assignLabels()

    def _linearizeRecursive(self, csl:List[str]) -> None:
        """Propage le calcul de la version linéaire aux enfants

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        """

        for node in self.toList():
            if isinstance(node, IfNode):
                nodeLinear = node._getLinearStructureList(csl)
                self.replace(node, nodeLinear)

    def _deleteJumpNextLine(self):
        """Recherche un jump pointant vers la ligne suivante et le supprime
        """
        jumpsToScan:List['JumpNode'] = [node for node in self.toList() if isinstance(node, JumpNode)]
        jumpsLeft:List['JumpNode'] = []
        jumpsDeleted = 1
        while jumpsDeleted > 0:
            # certains jump ont été retirés
            jumpsDeleted = 0
            for node in jumpsToScan:
                if node.cible == node._next:
                    self.delete(node)
                    jumpsDeleted += 1
                else:
                    jumpsLeft.append(node)
            jumpsToScan = jumpsLeft
            jumpsLeft:List['JumpNode'] = []

    def _deleteDummies(self):
        """Recherche les dummy
        """
        dummiesList:List['StructureNode'] = [node for node in self.toList() if isinstance(node, SimpleNode) and node.snType == "dummy"]
        for node in dummiesList:
            self.delete(node)

    def _assignLabels(self):
        """Recherche les jump et assigne un label à leur cible
        """
        jumpsList:List['JumpNode'] = [node for node in self.toList() if isinstance(node, JumpNode)]
        for j in jumpsList:
            j.cible.assignLabel()


    def __str__(self):
        """Transtypage -> str
        :return: version texte
        :rtype: str
        """
        childrenList = self.toList()
        childrenStrList = [ str(node) for node in childrenList ]
        return "\n".join(childrenStrList)

    def tabulatedStr(self):
        """Transtypage
        :return: chaîne de caractères avec une tabulation à chaque ligne
        :rtype: str
        """
        strList = str(self).split('\n')
        return '\t' + '\n\t'.join([line for line in strList])

    def delete(self, nodeToDel:"LinkedListNode") -> bool:
        """supprime l'élément node

        :param nodeToDel: élément à supprimer
        :type nodeToDel: LinkedListNode
        :return: suppression effectuée
        :rtype: bool
        """
        jumpsToMod = [node for node in self.toList() if node != nodeToDel and isinstance(node, JumpNode) and node.cible == nodeToDel]
        if nodeToDel._next == self._head and len(jumpsToMod) > 0:
            # nodeToDel en dernier et jumps à brancher sur lui
            # -> insertion d'un node dummy
            dummy = SimpleNode("dummy")
            self.append(dummy)
        newCibleJumps = cast(StructureNode, nodeToDel._next) # qui existe toujours
        for j in jumpsToMod:
            j.setCible(newCibleJumps)
        return super().delete(nodeToDel)

class StructureNode(LinkedListNode):
    _lineNumber = 0 # type : int
    _label:Optional["Label"] = None

    def __str__(self) -> str:
        """Transtypage -> str

        :return: chaîne par défaut, 'noeud de structure'
        :rtype: str
        """
        return "noeud de structure"

    @property
    def label(self) -> Optional[Label]:
        """Accesseur

        :return: label de l'item
        :rtype: Optional[Label]
        """
        return self._label

    def assignLabel(self) -> Label:
        """Assigne un label au noeud s'il n'en a pas déjà un
        :return: label de l'item
        :rtype: Label
        """
        if self._label is None:
            self._label = Label()
        return self._label

    def labelToStr(self) -> str:
        """
        :return: label en str, "" si pas de label
        :rtype: str
        """
        if self._label is None:
            return ""
        return str(self._label)

    @property
    def lineNumber(self) -> int:
        """Accesseur pour le numéro de ligne d'origine de cet élément

        :return: numéro de ligne d'origine
        :rtype: int
        """
        return self._lineNumber

class SimpleNode(StructureNode):
    _snType:str = "nop"
    def __init__(self, snType:str=""):
        super().__init__()
        if snType in ("halt", "dummy"):
            self._snType = snType

    @property
    def snType(self) -> str:
      """Accesseur

      :return: snType
      :rtype: str
      """
      return self._snType

    def __str__(self):
        """Transtypage -> str

        :return: chaîne par défaut, 'noeud de structure'
        :rtype: str
        """
        return "{}\t{}".format(self.labelToStr(), self._snType)

class IfNode(StructureNode):
    _children: "StructureNodeList"
    _condition: Union[LogicExpressionNode, ComparaisonExpressionNode]
    def __init__(self, lineNumber:int, condition:Union[LogicExpressionNode, ComparaisonExpressionNode], children:List[StructureNode]):
        """Constructeur d'un noeud If

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param condition: expression logique du test de ce if.
        :type condition: Union[LogicExpressionNode, ComparaisonExpressionNode]
        :param children: liste des objets enfants
        :type children: List[StructureNode]
        """
        super().__init__()
        self._condition = condition
        self._children = StructureNodeList(cast(List[LinkedListNode],children))
        self._lineNumber = lineNumber

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce noeud et de ses enfants
        :rtype: str
        """
        childrenStr = self._children.tabulatedStr()
        return "{}\tif {} {{\n{}\n\t}}".format(self.labelToStr(), self._condition, childrenStr)

    def _decomposeCondition(self, csl:List[str], cibleOUI:'StructureNode', cibleNON:'StructureNode') -> 'StructureNodeList':
        """Décompose un condition complexe, contenant des and, not, or,
        en un ensemble de branchement conditionnels, les opérations logiques
        étant assurées par l'organisation des branchements

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :param cibleOUI: cible dans le cas d'un test Vrai
        :type cibleOUI: StructureNode
        :param cibleNON: cible dans le cas d'un test Faux
        :type cibleNON: StructureNode
        :return: version linéaire de la condition, faite de branchements
        :rtype: StructureNodeList
        """

        # La condition va entraîner un branchement conditionnel. C'est le cas NON qui provoque le branchement.
        conditionInverse = self._condition.logicNegateClone()
        return self._recursiveDecomposeComplexeCondition(csl, conditionInverse, cibleOUI, cibleNON)

    def _recursiveDecomposeComplexeCondition(self, csl:List[str], conditionSaut:Union[LogicExpressionNode, ComparaisonExpressionNode], cibleDirecte:'StructureNode', cibleSautCond:'StructureNode') -> 'StructureNodeList':
        """Fonction auxiliaire et récursive pour la décoposition d'une condition complexe
        en un ensemble de branchement et de condition élémentaire

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :param conditionSaut: condition du saut conditionnel
        :type conditionSaut: Union[LogicExpressionNode, ComparaisonExpressionNode]
        :param cibleDirecte: cible en déroulement normal, càd condition fausse => pas de saut
        :type cibleDirecte: StructureNode
        :param cibleSautCond: cible du saut conditionnel, si la condition est vraie
        :type cibleSautCond: StructureNode
        :return: version linéaire de la condition, faite de branchements
        :rtype: StructureNodeList
        """
        if isinstance(conditionSaut, ComparaisonExpressionNode):
            conditionSaut = conditionSaut.adjustConditionClone(csl)
        if isinstance(conditionSaut, ComparaisonExpressionNode):
            # c'est un test élémentaire
            if conditionSaut.inversed:
                notInversedCond = conditionSaut.logicNegateClone()
                sautConditionnel = JumpNode(self._lineNumber, cibleDirecte, notInversedCond)
                sautOui = JumpNode(self._lineNumber, cibleSautCond)
            else:
                sautConditionnel = JumpNode(self._lineNumber, cibleSautCond, conditionSaut)
                sautOui = JumpNode(self._lineNumber, cibleDirecte)
            return StructureNodeList([sautConditionnel, sautOui])
        # sinon il faut décomposer la condition en conditions élémentaires
        if isinstance(conditionSaut, NotNode):
            conditionEnfant = conditionSaut.operand
            return self._recursiveDecomposeComplexeCondition(csl, conditionEnfant, cibleSautCond, cibleDirecte)

        if isinstance(conditionSaut, AndNode):
            conditionEnfant1, conditionEnfant2 = conditionSaut.operands
            enfant2 = self._recursiveDecomposeComplexeCondition(csl, conditionEnfant2, cibleDirecte, cibleSautCond)
            if enfant2.head is None :
                return self._recursiveDecomposeComplexeCondition(csl, conditionEnfant1, cibleDirecte, cibleSautCond)
            enfant1 = self._recursiveDecomposeComplexeCondition(csl, conditionEnfant1, cibleDirecte, cast(StructureNode,enfant2.head))
            enfant1.append(enfant2)
            return enfant1
        if isinstance(conditionSaut, OrNode):
            conditionEnfant1, conditionEnfant2 = conditionSaut.operands
            enfant2 = self._recursiveDecomposeComplexeCondition(csl, conditionEnfant2, cibleDirecte, cibleSautCond)
            if enfant2.head is None:
                return self._recursiveDecomposeComplexeCondition(csl, conditionEnfant1, cibleDirecte, cibleSautCond)
            enfant1 = self._recursiveDecomposeComplexeCondition(csl, conditionEnfant1, cast(StructureNode, enfant2.head), cibleSautCond)
            enfant1.append(enfant2)
            return enfant1
        raise AttributeError("Noeud de condition {} pas pris en charge.".format(conditionSaut), {"lineNumber": self._lineNumber})

    def _getLinearStructureList(self, csl:List[str]) -> 'StructureNodeList':
        """Production de la version linéaire pour l'ensemble du noeud If.
        Cela comprend :
        * les labels identifiant les différents blocs pour les sauts,
        * la condition décomposée en conditions simples assurées par des branchements conditionnels,
        * le bloc enfant

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: version linéaire du noeud if
        :rtype: StructureNodeList
        """

        # Ce noeud est enfant d'une liste L
        # il pourrait être le dernier et alors self._next
        # pointerait sur L._head au lieu d'un véritable _next
        # on ajoute donc un élément dummy à la suite pour prévenir
        # cette situation (gênante pour le saut)
        dummy = SimpleNode("dummy")
        self.insertRight(dummy)

        self._children._linearizeRecursive(csl)
        cibleIf = self._children.head
        if cibleIf is None:
            cibleIf = self._next
        listForCondition = self._decomposeCondition(
            csl,
            cast(StructureNode, cibleIf),
            cast(StructureNode, self._next)
        )
        listForCondition.append(self._children)
        return listForCondition

class IfElseNode(IfNode):
    _elseChildren:'StructureNodeList'
    _condition:Union[LogicExpressionNode, ComparaisonExpressionNode]
    def __init__(self, ifLineNumber:int, condition:Union[LogicExpressionNode, ComparaisonExpressionNode], ifChildren:List[StructureNode], elseLineNumber:int, elseChildren:List[StructureNode]):
        """Constructeur d'un noeud IfElse

        :param ifLineNumber: numéro de ligne dans le programme d'origine
        :type ifLineNumber: int
        :param elseLineNumber: numéro de ligne dans le programme d'origine pour le Else
        :type elseLineNumber: int
        :param condition: expression logique du test de ce if.
        :type condition: Union[LogicExpressionNode, ComparaisonExpressionNode]
        :param ifChildren: liste des objets enfants pour le bloc If
        :type ifChildren: List[StructureNode]
        :param elseChildren: liste des objets enfants pour le bloc Else
        :type elseChildren: List[StructureNode]
        """

        super().__init__(ifLineNumber, condition, ifChildren)
        self._elseChildren = StructureNodeList(cast(List[LinkedListNode],elseChildren))
        self._elseLineNumber = elseLineNumber

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce noeud et de ses enfants
        :rtype: str
        """
        childrenStr = self._children.tabulatedStr()
        elseChildrenStr = self._elseChildren.tabulatedStr()
        return "{}\tif {} {{\n{}\n\t}} else {{\n{}\n\t}}".format(self.labelToStr(), self._condition, childrenStr, elseChildrenStr)

    def _getLinearStructureList(self, csl:List[str]) -> 'StructureNodeList':
        """Production de la version linéaire pour l'ensemble du noeud If Else.
        Cela comprend :
        * les labels identifiant les différents blocs pour les sauts,
        * la condition décomposée en conditions simples assurées par des branchements conditionnels,
        * les blocs enfants, If et Else

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: version linéaire du noeud
        :rtype: StructureNodeList
        """

        # Ce noeud est enfant d'une liste L
        # il pourrait être le dernier et alors self._next
        # pointerait sur L._head au lieu d'un véritable _next
        # on ajoute donc un élément dummy à la suite pour prévenir
        # cette situation (gênante pour le saut)
        dummy = SimpleNode("dummy")
        self.insertRight(dummy)

        self._children._linearizeRecursive(csl)
        self._elseChildren._linearizeRecursive(csl)
        cibleIf = self._children.head
        cibleElse = self._elseChildren.head
        if cibleElse is None:
            cibleElse = self._next
        if cibleIf is None:
            cibleIf = cibleElse


        sautFin = JumpNode(
            self._lineNumber,
            cast(StructureNode, self._next)
        )
        listForCondition = self._decomposeCondition(
            csl,
            cast(StructureNode, cibleIf),
            cast(StructureNode, cibleElse)
        )

        output = listForCondition
        output.append(self._children)
        output.append(sautFin)
        output.append(self._elseChildren)

        return output

class WhileNode(IfNode):
    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce noeud et de ses enfants
        :rtype: str
        """
        childrenStr = self._children.tabulatedStr()
        return "{}\twhile {} {{\n{}\n\t}}".format(self.labelToStr(), self._condition, childrenStr)

    def _getLinearStructureList(self, csl:List[str]) -> 'StructureNodeList':
        """Production de la version linéaire pour l'ensemble du noeud While.
        Cela comprend :
        * les labels identifiant les différents blocs pour les sauts,
        * la condition décomposée en conditions simples assurées par des branchements conditionnels,
        * Le saut final assurant la boucle
        * le bloc enfant

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: version linéaire du noeud
        :rtype: StructureNodeList
        """

        # Ce noeud est enfant d'une liste L
        # il pourrait être le dernier et alors self._next
        # pointerait sur L._head au lieu d'un véritable _next
        # on ajoute donc un élément dummy à la suite pour prévenir
        # cette situation (gênante pour le saut)
        self.insertRight(SimpleNode("dummy"))

        self._children._linearizeRecursive(csl)
        cibleWhile = self._children.head
        dummy:Optional[SimpleNode] = None
        # il est indispensable que la liste children soit non vide
        if cibleWhile is None:
            dummy = SimpleNode("dummy")
            self._children.append(dummy)
            cibleWhile = dummy

        listForCondition = self._decomposeCondition(
            csl,
            cast(StructureNode, cibleWhile),
            cast(StructureNode, self._next)
        )
        cibleCondition = listForCondition.head
        if cibleCondition is None:
            # la boucle ne peut pas être exécutée
            return StructureNodeList([])

        sautRetour = JumpNode(
            self._lineNumber,
            cast(StructureNode, cibleCondition)
        )

        output = listForCondition
        output.append(self._children)
        output.append(sautRetour)
        if isinstance(dummy, SimpleNode):
            output.delete(dummy)

        return output

class AffectationNode(StructureNode):
    _expression: ArithmeticExpressionNode
    def __init__(self, lineNumber:int, variableCible:Variable, expression:ArithmeticExpressionNode):
        """Noeud représentant une affectation de forme variable <- expression

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param variableCible: variable qui sera affectée
        :type variableCible: Variable
        :param expression: expression arithmétique dont le résultat est affecté à la variable
        :type expression: ArithmeticExpressionNode
        """
        super().__init__()
        self._lineNumber = lineNumber
        self._cible = variableCible
        self._expression = expression

    @property
    def expression(self) -> ArithmeticExpressionNode:
        """Accesseur : retourne l'expression dont le résultat doit être affecté à la variable cible.

        :return: expression arithmétique dont le résultat doit être affecté à la variable cible.
        :rtype: ArithmeticExpressionNode
        """

        return self._expression

    @property
    def cible(self) -> Variable:
        """Accesseur : retourne la variable cible de l'affectation.

        :return: variable cible.
        :rtype: Variable
        """
        return self._cible

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud en chaîne de caractères
        :rtype: str
        """
        return '{}\t{} {} {}'.format(self.labelToStr(), self._cible, chr(0x2190), self._expression)

class InputNode(StructureNode):
    _cible: Variable
    def __init__(self, lineNumber:int, variableCible:Variable):
        """Noeud input précisant une variable devant stocké le résultat du input

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param variableCible: variable qui sera affectée
        :type variableCible: Variable
        """
        super().__init__()
        self._lineNumber = lineNumber
        self._cible = variableCible

    @property
    def cible(self) -> Variable:
        """Accesseur : retourne la variable cible du input.

        :return: variable cible.
        :rtype: Variable
        """
        return self._cible

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud en chaîne de caractères
        :rtype: str
        """
        return "{}\t{} {} Input".format(self.labelToStr(), self._cible, chr(0x2190))

class PrintNode(StructureNode):
    _expression:ArithmeticExpressionNode
    def __init__(self, lineNumber:int, expression:ArithmeticExpressionNode):
        """Noeud représentant un print, permettant d'afficher le résultat d'une expression arithmétique

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param expression: expression arithmétique dont le résultat est affecté à la variable
        :type expression: ArithmeticExpressionNode
        """
        super().__init__()
        self._lineNumber = lineNumber
        self._expression = expression

    @property
    def expression(self) -> ArithmeticExpressionNode:
        """Accesseur : retourne l'expression dont le résultat doit être affiché.

        :return: expression arithmétique dont le résultat doit être affiché.
        :rtype: ArithmeticExpressionNode
        """
        return self._expression

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud en chaîne de caractères
        :rtype: str
        """
        return "{}\t{} {} Affichage".format(self.labelToStr(), self._expression, chr(0x2192))

class JumpNode(StructureNode):
    _cible: 'StructureNode'
    _condition: Optional[ComparaisonExpressionNode]
    def __init__(self, lineNumber:int, cible:'StructureNode', condition:Optional[ComparaisonExpressionNode] = None):
        """Noeud représentant un saut conditionnel ou inconditionnel.

        :param lineNumber: numéro de ligne dans le programme d'origine,
        :type lineNumber: int
        :param cible: cible du saut,
        :type cible: StructureNode
        :param condition: expression booléenne exprimant à quelle condition le saut est effectué. None si le saut est inconditionnel.
        :type expression: Optional[ComparaisonExpressionNode]
        """
        super().__init__()
        self._condition = condition
        self._lineNumber = lineNumber
        self._cible = cible

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères du noeud
        :rtype: str
        """

        if self._condition == None:
            return "{}\tSaut {}".format(self.labelToStr(), self._cible.assignLabel())
        return "{}\tSaut {} si {}".format(self.labelToStr(), self._cible.assignLabel(), self._condition)

    @property
    def cible(self) -> 'StructureNode':
        """Accesseur

        :return: cible du saut
        :rtype: StructureNode
        """

        return self._cible

    def setCible(self, cible:'StructureNode') -> None:
        """Assigne une nouvelle cible

        :param cible: nouvelle cible
        :type cible: StructureNode
        """
        self._cible = cible

    def getCondition(self) -> Optional[ComparaisonExpressionNode]:
        """Accesseur

        :return: condition du saut
        :rtype: Optional[ComparaisonExpressionNode]
        """

        return self._condition

if __name__=="__main__":
    from expressionparser import ExpressionParser as EP

    varX = Variable('x')
    varY = Variable('y')

    initialisationX = AffectationNode(
        1,
        varX,
        cast(ArithmeticExpressionNode, EP.buildExpression('0'))
    )

    initialisationY = AffectationNode(
        2,
        varY,
        cast(ArithmeticExpressionNode, EP.buildExpression('0'))
    )

    affectationX = AffectationNode(
        4,
        varX,
        cast(ArithmeticExpressionNode, EP.buildExpression('x+1'))
    )

    affectationY = AffectationNode(
        5,
        varY,
        cast(ArithmeticExpressionNode, EP.buildExpression('y+x'))
    )

    whileItem = WhileNode(
        3,
        cast(LogicExpressionNode, EP.buildExpression('x < 10 or y < 100')),
        [affectationX, affectationY]
    )

    affichageFinal = PrintNode(
        6,
        cast(ArithmeticExpressionNode, EP.buildExpression('y'))
    )

#     print("Avant linéarisation...")
#     print()
#     structureList = StructureNodeList([initialisationX, initialisationY, whileItem, affichageFinal])
#     print(structureList)
#     print()
#     print("Après linéarisation avec (< et == étant les tests pris en charge)...")
#     print()
#     structureList.linearize(["<","=="])
#     print(structureList)


    print()

    from codeparser import CodeParser
    code = CodeParser.parse(filename = "example2.code")
    structureList = StructureNodeList(cast(List[LinkedListNode], code))
    print("Avant linéarisation...")
    print(structureList)
    structureList.linearize([">","<","=="])
    print("Après linéarisation avec  (>, < et == étant les tests pris en charge)...")
    print()
    print(structureList)
