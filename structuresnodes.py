"""
.. module:: structuresnodes
   :synopsis: définition des noeuds constituant le programme dans sa version structurée : Instructions simples, conditions, boucles. Contribue à la transformation d'une version où les conditions et boucles sont assurés par des sauts inconditionnels / conditionnels. Cette version est qualifiée de version linéaire.
"""
from typing import List, Optional

from expressionnodes import ExpressionNode
from variable import Variable

class StructureNode:
    _lineNumber = 0 # type : int
    def __str__(self) -> str:
        """Transtypage -> str

        :return: chaîne par défaut, 'noeud de structure'
        :rtype: str
        """
        return "noeud de structure"

    def getLinearStructureList(self, csl:List['str']) -> List['StructureNode']:
        """Fonction récursive produisant la version linéaire

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: liste des noeuds de la version linéaire
        :rtype: List[StructureNode]
        """

        return [ self ]

    @property
    def lineNumber(self) -> int:
        """Accesseur pour le numéro de ligne d'origine de cet élément

        :return: numéro de ligne d'origine
        :rtype: int
        """
        return self._lineNumber

class IfNode(StructureNode):
    @classmethod
    def _recursiveLinearStructureListOnChildren(cls, csl:List[str], childrenList:List['StructureNode']) -> List['StructureNode']:
        """Propage le calcul de la version linéaire aux enfants

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :param childrenList: liste des noeuds enfants à considérer
        :type childrenList: List[StructureNode]
        :return: liste enfant en version linéaire
        :rtype: List[StructureNode]
        """

        outList = []
        for node in childrenList:
            nodeLinear = node.getLinearStructureList(csl)
            outList.extend(nodeLinear)
        return outList

    @classmethod
    def _childrenStr(cls, childrenList:List['StructureNode']) -> str:
        """Propage le transtypage -> str aux enfants

        :param childrenList: liste des noeuds enfants à considérer
        :type childrenList: List[StructureNode]
        :return: liste enfant transtypée en chaîne de caractères
        :rtype: str
        """

        childrenStrList = [ str(node) for node in childrenList ]
        return "\n".join(childrenStrList)

    def __init__(self, lineNumber:int, condition:ExpressionNode, children:List[StructureNode]):
        """Constructeur d'un noeud If

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param condition: expression logique du test de ce if.
        :type condition: ExpressionNode
        :param children: liste des objets enfants
        :type children: List[StructureNode]
        """

        assert isinstance(condition, ExpressionNode)
        self._condition = condition
        assert condition.getType() == 'bool'
        for node in children:
            assert isinstance(node,StructureNode)
        self._children = children
        self._lineNumber = lineNumber

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce noeud et de ses enfants
        :rtype: str
        """
        childrenStr = self._childrenStr(self._children)
        return "if "+str(self._condition)+" {\n"+childrenStr+"\n}"

    def _decomposeCondition(self, csl:List[str], cibleOUI:'LabelNode', cibleNON:'LabelNode') -> List['StructureNode']:
        """Décompose un condition complexe, contenant des and, not, or,
        en un ensemble de branchement conditionnels, les opérations logiques
        étant assurées par l'organisation des branchements

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :param cibleOUI: cible dans le cas d'un test Vrai
        :type cibleOUI: LabelNode
        :param cibleNON: cible dans le cas d'un test Faux
        :type cibleNON: LabelNode
        :return: version linéaire de la condition, faite de branchements
        :rtype: List[StructureNode]
        """

        # La condition va entraîner un branchement conditionnel. C'est le cas NON qui provoque le branchement.
        conditionInverse = self._condition.logicNegateClone()
        # mais il faut s'assurer que les opérateurs de comparaisons sont bien connus
        conditionInverse = conditionInverse.adjustConditionClone(csl)
        return self._recursiveDecomposeComplexeCondition(conditionInverse, cibleOUI, cibleNON)

    def _recursiveDecomposeComplexeCondition(self, conditionSaut:ExpressionNode, cibleDirecte:'LabelNode', cibleSautCond:'LabelNode') -> List['StructureNode']:
        """Fonction auxiliaire et récursive pour la décoposition d'une condition complexe
        en un ensemble de branchement et de condition élémentaire

        :param conditionSaut: condition du saut conditionnel
        :type conditionSaut: ExpressionNode
        :param cibleDirecte: cible en déroulement normal, càd condition fausse => pas de saut
        :type cibleDirecte: LabelNode
        :param cibleSautCond: cible du saut conditionnel, si la condition est vraie
        :type cibleSautCond: LabelNode
        :return: version linéaire de la condition, faite de branchements
        :rtype: List[StructureNode]
        """
        if not conditionSaut.isComplexeCondition():
            # c'est un test élémentaire
            sautConditionnel = JumpNode(self._lineNumber, cibleSautCond, conditionSaut)
            sautOui = JumpNode(self._lineNumber, cibleDirecte)
            return [sautConditionnel, sautOui]
        # sinon il faut décomposer la condition en conditions élémentaires
        operator, conditionsEnfants = conditionSaut.boolDecompose()
        if operator == "not":
            # c'est un not, il faudra inverser OUI et NON et traiter la condition enfant
            conditionEnfant = conditionsEnfants[0]
            return self._recursiveDecomposeComplexeCondition(conditionEnfant, cibleSautCond, cibleDirecte)
        # c'est un OR ou AND
        cibleInter = LabelNode()
        conditionEnfant1, conditionEnfant2 = conditionsEnfants
        if operator == "and":
            enfant1 = self._recursiveDecomposeComplexeCondition(conditionEnfant1, cibleDirecte, cibleInter)
            enfant2 = self._recursiveDecomposeComplexeCondition(conditionEnfant2, cibleDirecte, cibleSautCond)
        else:
            enfant1 = self._recursiveDecomposeComplexeCondition(conditionEnfant1, cibleInter, cibleSautCond)
            enfant2 = self._recursiveDecomposeComplexeCondition(conditionEnfant2, cibleDirecte, cibleSautCond)
        return enfant1 + [cibleInter] + enfant2

    def getLinearStructureList(self, csl:List[str]) -> List['StructureNode']:
        """Production de la version linéaire pour l'ensemble du noeud If.
        Cela comprend :
        * les labels identifiant les différents blocs pour les sauts,
        * la condition décomposée en conditions simples assurées par des branchements conditionnels,
        * le bloc enfant

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: version linéaire du noeud if
        :rtype: List[StructureNode]
        """

        labelIf = LabelNode()
        labelFin = LabelNode()
        listForCondition = self._decomposeCondition(csl, labelIf, labelFin)
        listForChildren = self._recursiveLinearStructureListOnChildren(csl, self._children)
        outputList = listForCondition
        outputList.append(labelIf)
        outputList.extend(listForChildren)
        outputList.append(labelFin)
        return outputList

class IfElseNode(IfNode):
    def __init__(self, ifLineNumber:int, condition:ExpressionNode, ifChildren:List[StructureNode], elseLineNumber:int, elseChildren:List[StructureNode]):
        """Constructeur d'un noeud IfElse

        :param ifLineNumber: numéro de ligne dans le programme d'origine
        :type ifLineNumber: int
        :param elseLineNumber: numéro de ligne dans le programme d'origine pour le Else
        :type elseLineNumber: int
        :param condition: expression logique du test de ce if.
        :type condition: ExpressionNode
        :param ifChildren: liste des objets enfants pour le bloc If
        :type ifChildren: List[StructureNode]
        :param elseChildren: liste des objets enfants pour le bloc Else
        :type elseChildren: List[StructureNode]
        """

        super().__init__(ifLineNumber, condition, ifChildren)
        #super(IfNode, self).__init__(ifLineNumber, condition, ifChildren)
        for node in elseChildren:
            assert isinstance(node,StructureNode)
        self._elseChildren = elseChildren
        self._elseLineNumber = elseLineNumber

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce noeud et de ses enfants
        :rtype: str
        """
        ifChildrenStr = self._childrenStr(self._children)
        elseChildrenStr = self._childrenStr(self._elseChildren)
        return "if "+str(self._condition)+" {\n"+ifChildrenStr+"\n}\nelse {\n"+elseChildrenStr+"\n}"

    def getLinearStructureList(self, csl:List[str]) -> List['StructureNode']:
        """Production de la version linéaire pour l'ensemble du noeud If Else.
        Cela comprend :
        * les labels identifiant les différents blocs pour les sauts,
        * la condition décomposée en conditions simples assurées par des branchements conditionnels,
        * les blocs enfants, If et Else

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: version linéaire du noeud
        :rtype: List[StructureNode]
        """

        labelIf = LabelNode()
        labelElse = LabelNode()
        labelFin = LabelNode()
        sautFin = JumpNode(self._lineNumber, labelFin)
        listForCondition = self._decomposeCondition(csl, labelIf, labelElse)
        listForIfChildren = self._recursiveLinearStructureListOnChildren(csl, self._children)
        listForElseChildren = self._recursiveLinearStructureListOnChildren(csl, self._elseChildren)
        outputList = listForCondition
        outputList.append(labelIf)
        outputList.extend(listForIfChildren)
        outputList.append(sautFin)
        outputList.append(labelElse)
        outputList.extend(listForElseChildren)
        outputList.append(labelFin)
        return outputList

class WhileNode(IfNode):
    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce noeud et de ses enfants
        :rtype: str
        """

        childrenStr = self._childrenStr(self._children)
        return "while "+str(self._condition)+" {\n"+childrenStr+"\n}"

    def getLinearStructureList(self,csl):
        """Production de la version linéaire pour l'ensemble du noeud While.
        Cela comprend :
        * les labels identifiant les différents blocs pour les sauts,
        * la condition décomposée en conditions simples assurées par des branchements conditionnels,
        * Le saut final assurant la boucle
        * le bloc enfant

        :param csl: liste des comparaisons permises par le processeur utilisé
        :type csl: List[str]
        :return: version linéaire du noeud
        :rtype: List[StructureNode]
        """

        labelWhile = LabelNode()
        labelDebut = LabelNode()
        labelFin = LabelNode()
        sautRetour = JumpNode(self._lineNumber, labelWhile)
        listForCondition = self._decomposeCondition(csl, labelDebut, labelFin)
        listForChildren = self._recursiveLinearStructureListOnChildren(csl, self._children)
        outputList = [ labelWhile ]
        outputList.extend(listForCondition)
        outputList.append(labelDebut)
        outputList.extend(listForChildren)
        outputList.append(sautRetour)
        outputList.append(labelFin)
        return outputList

class LabelNode(StructureNode):
    __currentIndex = 0 # type: int
    @classmethod
    def getNextFreeIndex(cls) -> int:
        """génère un nouvel index de numéro de label. Assure l'unicité des numéros.

        :return: index pour in nouveau label
        :rtype: int
        """
        cls.__currentIndex += 1
        return cls.__currentIndex

    def __init__(self):
        """Constructeur. Attribue comme index, le prochain index libre
        """
        self.__index = self.getNextFreeIndex() # type:int

    def __str__(self) -> str:
        """Transtypage -> str

        :return: index du label préfixé par 'l'
        :rtype: str
        """
        return "Lab"+str(self.__index)

class AffectationNode(StructureNode):
    def __init__(self, lineNumber:int, variableCible:Variable, expression:ExpressionNode):
        """Noeud représentant une affectation de forme variable <- expression

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param variableCible: variable qui sera affectée
        :type variableCible: Variable
        :param expression: expression arithmétique dont le résultat est affecté à la variable
        :type expression: ExpressionNode
        """
        assert isinstance(expression, ExpressionNode)
        assert expression.getType() == 'int'
        assert isinstance(variableCible, Variable)
        self._lineNumber = lineNumber
        self._cible = variableCible
        self._expression = expression

    @property
    def expression(self) -> ExpressionNode:
        """Accesseur : retourne l'expression dont le résultat doit être affecté à la variable cible.

        :return: expression arithmétique dont le résultat doit être affecté à la variable cible.
        :rtype: ExpressionNode
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
        return str(self._cible)+" "+chr(0x2190)+" "+str(self._expression)

class InputNode(StructureNode):
    def __init__(self, lineNumber:int, variableCible:Variable):
        """Noeud input précisant une variable devant stocké le résultat du input

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param variableCible: variable qui sera affectée
        :type variableCible: Variable
        """

        assert isinstance(variableCible, Variable)
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
        return str(self._cible)+" "+chr(0x2190)+" Input"

class PrintNode(StructureNode):
    def __init__(self, lineNumber:int, expression:ExpressionNode):
        """Noeud représentant un print, permettant d'afficher le résultat d'une expression arithmétique

        :param lineNumber: numéro de ligne dans le programme d'origine
        :type lineNumber: int
        :param expression: expression arithmétique dont le résultat est affecté à la variable
        :type expression: ExpressionNode
        """

        assert isinstance(expression, ExpressionNode)
        assert expression.getType() == 'int'
        self._lineNumber = lineNumber
        self._expression = expression

    @property
    def expression(self) -> ExpressionNode:
        """Accesseur : retourne l'expression dont le résultat doit être affiché.

        :return: expression arithmétique dont le résultat doit être affiché.
        :rtype: ExpressionNode
        """
        return self._expression

    def __str__(self) -> str:
        """Transtypage -> str

        :return: noeud en chaîne de caractères
        :rtype: str
        """

        return str(self._expression)+" "+chr(0x2192)+" Affichage"

class JumpNode(StructureNode):
    def __init__(self, lineNumber:int, cible:LabelNode, condition:Optional[ExpressionNode] = None):
        """Noeud représentant un saut conditionnel ou inconditionnel.

        :param lineNumber: numéro de ligne dans le programme d'origine,
        :type lineNumber: int
        :param cible: cible du saut,
        :type cible: LabelNode
        :param condition: expression booléenne exprimant à quelle condition le saut est effectué. None si le saut est inconditionnel.
        :type expression: Optional[ExpressionNode]
        """

        assert isinstance(cible, LabelNode)
        assert condition == None or isinstance(condition,ExpressionNode) and condition.isSimpleCondition()
        self._condition = condition
        self._lineNumber = lineNumber
        self._cible = cible

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères du noeud
        :rtype: str
        """

        if self._condition == None:
            return "Saut "+str(self._cible)
        return "Saut "+str(self._cible)+" si "+str(self._condition)

    @property
    def cible(self) -> LabelNode:
        """Accesseur

        :return: cible du saut
        :rtype: LabelNode
        """

        return self._cible

    def getCondition(self) -> Optional[ExpressionNode]:
        """Accesseur

        :return: condition du saut
        :rtype: Optional[ExpressionNode]
        """

        return self._condition

    def assignNewCibleClone(self, newCible:LabelNode) -> 'JumpNode':
        """Crée un clone avec une nouvelle cible.

        :return: clone du noeud avec une nouvelle cible
        :rtype: JumpNode
        """

        return JumpNode(self._lineNumber, newCible, self._condition)



if __name__=="__main__":
    from expressionparser import *
    # VM = VariableManager()
    # EP = ExpressionParser(VM)
    EP = ExpressionParser()

    # varX = VM.addVariableByName('x')
    # varY = VM.addVariableByName('y')
    varX = Variable('x')
    varY = Variable('y')
    expr = EP.buildExpression('3*x+2')

    initialisationX = AffectationNode(1, varX, EP.buildExpression('0'))
    initialisationY = AffectationNode(2, varY, EP.buildExpression('0'))
    AffectationX = AffectationNode(4, varX, EP.buildExpression('x+1'))
    AffectationY = AffectationNode(5, varY, EP.buildExpression('y+x'))
    whileItem = WhileNode(3, EP.buildExpression('x < 10 or y < 100'), [AffectationX, AffectationY])
    affichageFinal = PrintNode(6, EP.buildExpression('y'))
    print(initialisationX)
    print(initialisationY)
    print(whileItem)
    print(affichageFinal)
    print("Décomposition du while :")
    decomposition = whileItem.getLinearStructureList(["<","=="])
    for node in decomposition:
        print(node)


