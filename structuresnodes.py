"""
.. module:: structuresnodes
   :synopsis: définition des noeuds constituant le programme dans sa version structurée : Instructions simples, conditions, boucles. Contribue à la transformation d'une version où les conditions et boucles sont assurés par des sauts inconditionnels / conditionnels. Cette version est qualifiée de version linéaire.
"""
from typing import List

from expression import Expression
from variable import Variable

class StructureNode:
    _lineNumber = 0 # type : int
    def __str__(self) -> str:
        """Transtypage -> str
        :return : chaîne par défaut, 'noeud de structure'
        :rtype: str
        """
        return "noeud de structure"

    def getLinearStructureList(self, csl:List['str']) -> List['StructureNode']:
        """Fonction récursive produisant la version linéaire
        :param csl:Liste des comparaisons permises par le processeur utilisé
        :type csl:List[str]
        :return : Liste des noeuds de la version linéaire
        :rtype: List[StructureNode]
        """

        return [ self ]

    def getLineNumber(self) -> int:
        """Accesseur pour le numéro de ligne d'origine de cet élément
        :return : numéro de ligne d'origine
        :rtype: int
        """
        return self._lineNumber

class IfNode(StructureNode):
    @classmethod
    def _recursiveLinearStructureListOnChildren(cls, csl:List[str], childrenList:List['StructureNode']) -> List['StructureNode']:
        """Propage le calcul de la version linéaire aux enfants
        :param csl:Liste des comparaisons permises par le processeur utilisé
        :type csl:List[str]
        :param childrenList:Liste des noeuds enfants à considérer
        :type childrenList:List[StructureNode]
        :return : Liste enfant en version linéaire
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
        :param childrenList:Liste des noeuds enfants à considérer
        :type childrenList:List[StructureNode]
        :return : Liste enfant transtypée en chaîne de caractères
        :rtype: str
        """

        childrenStrList = [ str(node) for node in childrenList ]
        return "\n".join(childrenStrList)

    def __init__(self, lineNumber:int, condition:Expression, children:List[StructureNode]):
        """Constructeur d'un noeud If
        :param lineNumber:Numéro de ligne dans le programme d'origine
        :type lineNumber:int
        :param condition:Expression logique du test de ce if.
        :type condition:Expression
        :param children:Liste des objets enfants
        :type children:List[StructureNode]
        """

        assert isinstance(condition, Expression)
        self._condition = condition
        assert condition.getType() == 'bool'
        for node in children:
            assert isinstance(node,StructureNode)
        self._children = children
        self._lineNumber = lineNumber

    def __str__(self) -> str:
        """Transtypage -> str
        :return:Version chaîne de caractères de ce noeud et de ses enfants
        :rtype:str
        """
        childrenStr = self._childrenStr(self._children)
        return "if "+str(self._condition)+" {\n"+childrenStr+"\n}"

    def _decomposeCondition(self, csl:List[str], cibleOUI:'LabelNode', cibleNON:'LabelNode') -> List['StructureNode']:
        '''
        csl = liste de string : symboles de comparaisons disponibles
        cibleOUI, cibleNON : cible LabelNode en cas de OUI et en cas de NON
        Sortie : liste de TestNode et de LabelNode
        '''
        # La condition va entraîner un branchement conditionnel. C'est le cas NON qui provoque le branchement.
        conditionInverse = self._condition.logicNegateClone()
        # mais il faut s'assurer que les opérateurs de comparaisons sont bien connus
        conditionInverse = conditionInverse.adjustConditionClone(csl)
        return self._recursiveDecomposeComplexeCondition(conditionInverse, cibleOUI, cibleNON)

    def _recursiveDecomposeComplexeCondition(self, conditionSaut, cibleDirecte, cibleSautCond):
        '''
        conditionSaut = Expression booléenne, condition du saut conditionnel
        cibleSautCond = LabelNode, cible du saut conditionnel
        cibleDirecte = LabelNode, cible du saut si condition fausse
        '''
        if not conditionSaut.isComplexeCondition():
            # c'est un test élémentaire
            sautConditionnel = JumpNode(self._lineNumber, cibleSautCond, conditionSaut)
            sautOui = JumpNode(self._lineNumber, cibleDirecte)
            return [sautConditionnel, sautOui]
        # sinon il faut décomposer la condition en conditions élémentaires
        decomposition = conditionSaut.boolDecompose()
        if decomposition[0] == "not":
            # c'est un not, il faudra inverser OUI et NON et traiter la condition enfant
            conditionEnfant = decomposition[1]
            return self._recursiveDecomposeComplexeCondition(conditionEnfant, cibleSautCond, cibleDirecte)
        # c'est un OR ou AND
        cibleInter = LabelNode()
        operator, conditionEnfant1, conditionEnfant2 = decomposition
        if operator == "and":
            enfant1 = self._recursiveDecomposeComplexeCondition(conditionEnfant1, cibleDirecte, cibleInter)
            enfant2 = self._recursiveDecomposeComplexeCondition(conditionEnfant2, cibleDirecte, cibleSautCond)
        else:
            enfant1 = self._recursiveDecomposeComplexeCondition(conditionEnfant1, cibleInter, cibleSautCond)
            enfant2 = self._recursiveDecomposeComplexeCondition(conditionEnfant2, cibleDirecte, cibleSautCond)
        return enfant1 + [cibleInter] + enfant2

    def getLinearStructureList(self, csl):
        '''
        csl = liste de string : symboles de comparaisons disponibles
        '''
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
    def __init__(self, ifLineNumber, condition, ifChildren, elseLineNumber, elseChildren):
        '''
        Entrées :
          ifLineNumber = int, numéro ligne d'origine
          elseLineNumber = int, numéro ligne d'origine
          condition est un objet Expression
          ifChildren = éléments enfants
          elseChildren = éléments enfants
        '''
        super().__init__(ifLineNumber, condition, ifChildren)
        #super(IfNode, self).__init__(ifLineNumber, condition, ifChildren)
        for node in elseChildren:
            assert isinstance(node,StructureNode)
        self._elseChildren = elseChildren
        self._elseLineNumber = elseLineNumber

    def __str__(self):
        ifChildrenStr = self._childrenStr(self._children)
        elseChildrenStr = self._childrenStr(self._elseChildren)
        return "if "+str(self._condition)+" {\n"+ifChildrenStr+"\n}\nelse {\n"+elseChildrenStr+"\n}"

    def getLinearStructureList(self,csl):
        '''
        csl = liste de string : symboles de comparaisons disponibles
        '''
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
    def __str__(self):
        childrenStr = self._childrenStr(self._children)
        return "while "+str(self._condition)+" {\n"+childrenStr+"\n}"

    def getLinearStructureList(self,csl):
        '''
        csl = liste de string : symboles de comparaisons disponibles
        '''
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
    __currentIndex = 0
    @classmethod
    def getNextFreeIndex(cls):
        cls.__currentIndex += 1
        return cls.__currentIndex

    def __init__(self):
        self.__index = self.getNextFreeIndex()

    def __str__(self):
        return "l"+str(self.__index)

class AffectationNode(StructureNode):
    def __init__(self, lineNumber, variableCible, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          variableCible = objet Variable, variable cible
          expression = objet Expression
        '''
        assert isinstance(expression, Expression)
        assert expression.getType() == 'int'
        assert isinstance(variableCible, Variable)
        self._lineNumber = lineNumber
        self._cible = variableCible
        self._expression = expression

    def getExpression(self):
        return self._expression

    def getCible(self):
        return self._cible

    def __str__(self):
        return str(self._cible)+" "+chr(0x2190)+" "+str(self._expression)

class InputNode(StructureNode):
    def __init__(self, lineNumber, variableCible):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          nomCible = string nom de la variable cible
        '''
        assert isinstance(variableCible, Variable)
        self._lineNumber = lineNumber
        self._cible = variableCible

    def getCible(self):
        return self._cible

    def __str__(self):
        return str(self._cible)+" "+chr(0x2190)+" Input"

class PrintNode(StructureNode):
    def __init__(self, lineNumber, expression):
        '''
        Entrées :
          lineNumber = int numéro de ligne d'origine de l'affectation
          expression est un objet Expression
        '''
        assert isinstance(expression, Expression)
        assert expression.getType() == 'int'
        self._lineNumber = lineNumber
        self._expression = expression

    def getExpression(self):
        return self._expression

    def __str__(self):
        return str(self._expression)+" "+chr(0x2192)+" Affichage"

class JumpNode(StructureNode):
    def __init__(self, lineNumber, cible, condition=None):
        assert isinstance(cible, LabelNode)
        assert condition == None or isinstance(condition,Expression) and condition.isSimpleCondition()
        self._condition = condition
        self._lineNumber = lineNumber
        self._cible = cible

    def __str__(self):
        if self._condition == None:
            return "Saut "+str(self._cible)
        return "Saut "+str(self._cible)+" si "+str(self._condition)

    def getCible(self):
        return self._cible

    def getCondition(self):
        return self._condition

    def assignNewCibleClone(self,newCible):
        '''
        newCible = LabelNode
        '''
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


