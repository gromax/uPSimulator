"""
.. module:: structuresnodes
   :synopsis: définition des noeuds constituant le programme dans sa version structurée : Instructions simples, conditions, boucles. Contribue à la transformation d'une version où les conditions et boucles sont assurés par des sauts inconditionnels / conditionnels. Cette version est qualifiée de version linéaire.

   .. note::

    Les noeuds ne sont jamais modifiés. toute modification entraîne la création de clones.
"""

from typing import List, Optional, Tuple, Sequence, Union

from errors import *
from litteral import Litteral
from variable import Variable
from processorengine import ProcessorEngine
from compileexpressionmanager import CompileExpressionManager

class ExpressionNode:
    """Noeud parent garantissant l'existence de certaines fonctions pour tous les noeuds.
    """
    def compile(self, CEMObject:CompileExpressionManager) -> None:
        """Exécute la compilation
        :param CEMObject:Gestionnaire de compilation pour une expression
        :type CEMObject:CompileExpressionManager
        :return:None
        """
        if self.getType() != 'int' and self.isComplexeCondition():
            raise CompilationError(f"{str(self)} n'est pas une expression arithmétique ou une comparaison simple.")
        self.calcCompile(CEMObject)

    def isLitteral(self) -> bool:
        """Le noeud est-il un littéral ?
        :return:Vrai si le noeud est un simple littéral
        :rtype:bool
        """
        return False

    def needUAL(self) -> bool:
        """L'évaluation de ce noeud nécessitera-t-elle l'utilisation de l'UAL ?
        :return:Vrai si l'UAL est nécessaire.
        :rtype:bool
        """
        return False

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcul le nombre de registre nécessaire pour l'évaluation d'un noeud
        :return:nombre de registres
        :rtype:int
        """
        return 1

    def calcCompile(self, CEMObject:CompileExpressionManager) -> None:
        """Exécute la compilation
        :param CEMObject:Gestionnaire de compilation pour une expression
        :type CEMObject:CompileExpressionManager
        :return:None
        """
        engine = CEMObject.getEngine()
        myCost = self.getRegisterCost(engine)
        needUAL =self.needUAL()
        CEMObject.getNeededRegisterSpace(myCost, needUAL)

    def isSimpleCondition(self) -> bool:
        """
        :return:Vrai si l'expression est de type 'bool' et sans opérateur and, or, not
        :rtype:bool
        """
        return self.getType() == 'bool' and not self.isComplexeCondition()

    def getType(self) -> str:
        """Renvoie le type. 'int' par défaut
        :return: type de l'expression, 'bool' pour booléen et 'int' pour arithmétique
        :rtype:str
        """

        return 'int'

    def isComplexeCondition(self) -> bool:
        """S'agit-il d'une condition composée de and, or, not ?
        :return:Vrai si c'est une condition logique contenant des and, or, not
        :rtype:bool
        """

        return False

    def getComparaisonSymbol(self) -> Optional[str]:
        """Symbole de comparaisons utilisé dans une comparaison simple
        :return:None dans le cas général
        :rtype:None

        .. note::

        Ne sert que pour BinaryNode, dans le cas d'une expression logique
        """

        return None

    def adjustConditionClone(self, csl:List[str]) -> 'ExpressionNode':
        """Dans le cas d'une expression contenant des symboles de comparaisons,
        adapte l'expression pour qu'elle ne contienne qu'une liste de symboles autorisés.
        Crée un clone pour accueillir la modification si nécessaire.

        :param csl:Liste des symboles de comparaison autorisés
        :type csl:List[str]
        :return:Noeud original ou clone avec les modifications faites
        :rtype:ExpressionNode

        .. note::

        Sert pour BinaryNode, dans le cas d'une expression logique avec symboles de comparaison

        Si pas de modification, le noeud original est conservé.
        """

        return self

    def negToSubClone(self) -> 'ExpressionNode':
        """Adapte l'expression pour l'éventualité de l'absence d'une commande NEG, c'est à dire un - unaire.
        Si une modification est nécessaire, un clone est créé.

        :return:Noeud original ou clone avec les modifications faites
        :rtype:ExpressionNode

        .. note::

        Sert pour UnaryNode, dans le cas d'une opération -
        """

        return self

    def logicNegateClone(self) -> 'ExpressionNode':
        """Calcul la négation logique de l'expression.
        Si nécessaire un clone est créé.
        Dans le cas d'une opération arithmétique, on se contente de retourner le noeud sans modification.

        :return:Noeud original ou clone avec les modifications faites
        :rtype:ExpressionNode
        """

        return self

    def boolDecompose(self) -> Tuple[str,Sequence['ExpressionNode']]:
        """Décompose une condition complexe pour construire les sauts conditionnels qui réaliseront cette condition.

        :return:Par défaut ('',())
        :rtype:tuple(str,empty tuple)
        """
        return ('',())

    def clone(self) -> 'ExpressionNode':
        """Fonction par défaut
        :return:l'objet lui-même
        :rtype:ExpressionNode
        """
        return self

    def getValue(self) -> Union[None,Variable,Litteral]:
        """Fonction par défaut. Utilisée dans ValueNode
        :return:None par défaut
        :rtype:None
        """
        return None

class UnaryNode(ExpressionNode):
    __knownOperators:Sequence[str] = ('not', '~', '-')
    def __init__(self, operator:str, operand:ExpressionNode):
        """Constructeur
        :param operator:Opérateur parmi not, ~ et - (unaire)
        :type operator:str
        :param operand:Opérande
        :type operand:ExpressionNode
        """

        assert operator in self.__knownOperators
        assert isinstance(operand,ExpressionNode)
        self.__operator = operator
        self.__operand = operand

    def isComplexeCondition(self) -> bool:
        """S'agit-il d'une condition composée de not ?
        :return:Vrai si c'est un opérateur not
        :rtype:bool

        .. note::

        Inutile de vérifier les enfants car si ce n'est pas not,
        les enfants sont forcément de type arithmétique.
        """

        return self.__operator == "not"

    def boolDecompose(self) -> Tuple[str,Sequence[ExpressionNode]]:
        """Renvoie les éléments structurant une condition complexe
        afin de traitement pour orgniser les sauts conditionnels qui feront exécuteront cette condition.

        :return:tuple ("not",(noeud enfant)) ou ('',())
        :rtype:tuple(str,tuple(ExpressionNode))
        """

        if self.__operator != "not":
            return ('',())
        return "not", (self.__operand,)

    def logicNegateClone(self) -> ExpressionNode:
        """Calcul la négation logique de l'expression.
        Dans le cas not, consiste à enlever le not.

        Si pas un not, alors c'est un noeud arithmétique qui n'est pas modifié.
        :return:clone pour obtenir une négation logique
        :rtype:ExpressionNode

        .. note::

        Un clone est systèmatiquement créé
        """

        if self.__operator == "not":
            return self.__operand.clone()
        return self.clone()

    def adjustConditionClone(self, csl:List[str]) -> ExpressionNode:
        """Ajuste les symboles de comparaison des enfants pour les adapter aux symboles autorisés
        Crée un clone pour accueillir la modification si nécessaire.

        :param csl:Liste des symboles de comparaison autorisés
        :type csl:List[str]
        :return:clone avec les modifications faites
        :rtype:ExpressionNode

        .. note::

        Si le noeud est un not, les enfants contiendront des symboles de comparaison.
        On propage alors au noeud enfant.

        La modification du noeud enfant peut emboîter un not supplémentaire (!= transformé en not ==)
        Cela est sans importance : les not sont exécutés par un jeu de branchement de sauts.
        L'enchainement de deux not conduit seulement à inverser deux fois de suites les cibles d'un branchement
        ce qui ne crée aucune complication.

        Si le noeud n'est pas un not, l'enfant est forcément arithmétique et donc il est inutile d'aller plus loin.
        """

        if self.__operator != "not":
            return self
        newOp = self.__operand.adjustConditionClone(csl)
        return UnaryNode("not", newOp)

    def getType(self) -> str:
        """Type d'expression

        :return:'bool' ou 'int' ou '' en cas d'erreur
        :rtype:str

        .. note::

        Les variables et littéraux sont arithmétiques ainsi que tous les calculs exécutés sur eux.

        Les comparaisons telles que ==, <... produisent des quantités booléennes.

        Les opérateur not, and, or ne peuvent s'appliquer qu'à des opérandes de type booléens.

        Les opérateurs &, |... sont bitwises et à ce titre sont considérés comme arithmétiques.
        """

        operandType = self.__operand.getType()
        if operandType == None or (self.__operator == '~' and operandType=='bool'):
            return ''
        elif self.__operator == "not":
            return 'bool'
        return 'int'

    def negToSubClone(self) -> ExpressionNode:
        """Adapte l'expression pour l'éventualité de l'absence d'une commande NEG, c'est à dire un - unaire.

        Ainsi, si l'opérateur est -, le noeud est transformé en l'opération 0 - ... de façon à remplacer le - unaire - binaire

        :return:Noeud original ou clone avec les modifications faites
        :rtype:ExpressionNode

        .. note::

        La demande de modification est propagée au noeud enfant.
        """


        newOperand = self.__operand.negToSubClone()
        if not self.__operator == "-":
            return UnaryNode(self.__operator, newOperand)
        zero = ValueNode(Litteral(0))
        return BinaryNode("-", zero, newOperand)

    def __str__(self) -> str:
        """Transtypage -> str
        :return:Représentation du noeud sous forme d'une chaîne de caractères
        :rtype:str

        .. note::

        L'expression est entièrement parenthèsée.
        """
        strOperand = str(self.__operand)
        return self.__operator+"("+strOperand+")"

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        """Calcul le nombre de registre nécessaire pour l'évaluation d'un noeud
        :return:nombre de registres
        :rtype:int

        .. note::

        L'opérande étant placée dans un registre, on peut envisager de placer le résultat au même endroit.
        L'opération ne nécessite alors pas de registres supplémentaire.
        """

        return self.__operand.getRegisterCost(engine)

    def needUAL(self) -> bool:
        """L'évaluation de ce noeud nécessitera l'ual.

        :return:Vrai
        :rtype:bool
        """

        return True

    def calcCompile(self, CEMObject:CompileExpressionManager) -> None:
        """Exécute la compilation
        :param CEMObject:Gestionnaire de compilation pour une expression
        :type CEMObject:CompileExpressionManager
        :return:None
        """

        if self.__operator == "not":
            raise ExpressionError("opérateur not ne peut être compilé en calcul.")
        super(UnaryNode,self).calcCompile(CEMObject)
        engine = CEMObject.getEngine()
        if self.__operand.isLitteral() and engine.litteralOperatorAvailable(self.__operator, self.__operand.getValue()):
            litteral = self.__operand.getValue()
            CEMObject.pushUnaryOperatorWithLitteral(self.__operator, litteral)
        else:
            self.__operand.calcCompile(CEMObject)
            CEMObject.pushUnaryOperator(self.__operator)

    def clone(self) -> 'UnaryNode':
        """Crée un noeud clone
        :return:clone
        :rtype:UnaryNode

        .. note::

        l'aborescence enfant est également clonée.
        """
        cloneOperand = self.__operand.clone()
        operator = self.__operator
        return UnaryNode(operator, cloneOperand)

class BinaryNode(ExpressionNode):
    __knownOperators:Sequence[str] = ('+', '-', '*', '/', '%', 'and', 'or', '&', '|', '^', '<', '>', '<=', '>=', '==', '!=')
    __symetricOperators:Sequence[str] = ('+', '*', '&', '|', '^')
    __logicalOperators:Sequence[str] = ("and", "or")
    __comparaisonOperators:Sequence[str] = ("<=", "<", ">=", ">", "==", "!=")
    def __init__(self, operator:str, operand1:ExpressionNode, operand2:ExpressionNode):
        '''
        operator : dans +, -, *, /, %, and, or, &, |
        operand1 et operand2 : objet de type ExpressionNode
        '''
        assert operator in self.__knownOperators
        assert isinstance(operand1,ExpressionNode)
        assert isinstance(operand2,ExpressionNode)
        self.__operator = operator
        self.__operands = operand1, operand2

    def isComplexeCondition(self) -> bool:
        return self.__operator == "or" or self.__operator == "and"

    def boolDecompose(self) -> Tuple[str,Sequence[ExpressionNode]]:
        '''
        Sortie : si and, or, tuple avec le nom "and" ou "or", et les deux enfants.
        None sinon
        '''
        if self.__operator != "or" and self.__operator != "and":
            return ('',())
        return self.__operator, (self.__operands[0], self.__operands[1])

    def logicNegateClone(self) -> 'BinaryNode':
        '''
        retourne une copie en négation logique s'il y a lieu
        '''
        comparaisonNegation = { "<":">=", ">":"<=", "<=":">", ">=":"<", "==":"!=", "!=":"==" }
        if self.__operator in comparaisonNegation:
            newOperator = comparaisonNegation[self.__operator]
            op1, op2 = self.__operands
            cloneOp1 = op1.clone()
            cloneOp2 = op2.clone()
            return BinaryNode(newOperator, cloneOp1, cloneOp2)
        operatorNegation = { "and":"or", "or":"and" }
        if self.__operator in operatorNegation:
            newOperator = operatorNegation[self.__operator]
            op1, op2 = self.__operands
            negCloneOp1 = op1.logicNegateClone()
            negCloneOp2 = op2.logicNegateClone()
            return BinaryNode(newOperator, negCloneOp1, negCloneOp2)
        # Sinon, pas de modification -> pas besoin de cloner
        return self

    def adjustConditionClone(self,csl:List[str]) -> Union['BinaryNode',UnaryNode]:
        '''
        csl = liste de string : symboles de comparaisons disponibles
        '''
        if self.__operator in self.__logicalOperators:
            op1, op2 = self.__operands
            newOp1 = op1.adjustConditionClone(csl)
            newOp2 = op2.adjustConditionClone(csl)
            return BinaryNode(self.__operator, newOp1, newOp2)
        if self.__operator in self.__comparaisonOperators and not self.__operator in csl:
            miroir = { "<":">", ">":"<", "<=":">=", ">=":"<=", "!=":"!=", "==":"==" }
            inverse = { "<":">=", ">":"<=", "<=":">", ">=":"<", "==":"!=", "!=":"==" }
            inverseMiroir = { "<":"<=", ">":">=", "<=":"<", ">=":">", "==":"!=", "!=":"==" }
            op1, op2 = self.__operands
            if miroir[self.__operator] in csl:
                return BinaryNode(miroir[self.__operator], op2, op1)
            if inverse[self.__operator] in csl:
                inverseNode = BinaryNode(inverse[self.__operator], op1, op2)
                return UnaryNode("not", inverseNode)
            if inverseMiroir[self.__operator] in csl:
                inverseNode = BinaryNode(inverseMiroir[self.__operator], op2, op1)
                return UnaryNode("not", inverseNode)
            raise AttributeError(f"Aucun opérateur pour {self.__operator} dans le modèle de processeur.")
        return self

    def getType(self) -> str:
        '''
        Sortie =
          'bool' si opération de type booléen
          'int' si opération de type entier
          '' si construction invalide
        '''
        operand1Type = self.__operands[0].getType()
        operand2Type = self.__operands[1].getType()
        if operand1Type != operand2Type or operand1Type == '' or operand2Type == '':
            return ''
        elif operand1Type == 'bool' and self.__operator in "+-*/%&|":
            # cas opérateur entier agissant sur opérandes logiques
            return ''
        elif operand1Type == 'bool' and self.__operator in "and;or":
            # cas opérateur logique agissant sur opérandes logiques
            return 'bool'
        elif operand1Type == 'bool':
            # cas ==, <=...
            return ''
        elif self.__operator in "and;or":
            # cas opérateur logique agissant sur entiers
            return ''
        elif self.__operator in "+-*/%&|":
            # cas opérateur entier agissant sur entier
            return 'int'
        else:
            # cas == <=... agissant sur entier
            return 'bool'

    def negToSubClone(self) -> 'BinaryNode':
        '''
        modifie les - unaires de l'arborescence en - binaire
        '''
        op1, op2 = self.__operands
        newOp1 = op1.negToSubClone()
        newOp2 = op2.negToSubClone()
        return BinaryNode(self.__operator, newOp1, newOp2)

    def __str__(self) -> str:
        strOperand1 = str(self.__operands[0])
        strOperand2 = str(self.__operands[1])
        return "(" + strOperand1 + " " + self.__operator + " " + strOperand2 + ")"

    def getRegisterCost(self, engine:ProcessorEngine) -> int:
        op1, op2 = self.__operands
        if op2.isLitteral() and engine.litteralOperatorAvailable(self.__operator, op2.getValue()):
            return op1.getRegisterCost(engine)
        if self.isSymetric() and op1.isLitteral() and engine.litteralOperatorAvailable(self.__operator, op1.getValue()):
            return op2.getRegisterCost(engine)
        costOperand1 = op1.getRegisterCost(engine)
        costOperand2 = op2.getRegisterCost(engine)
        return min(max(costOperand1, costOperand2+1), max(costOperand1+1, costOperand2))

    def isSymetric(self) -> bool:
        return self.__operator in self.__symetricOperators

    def needUAL(self) -> bool:
        return True

    def getComparaisonSymbol(self) -> Optional[str]:
        if self.__operator in self.__comparaisonOperators:
            return self.__operator
        return None

    def calcCompile(self, CEMObject:CompileExpressionManager) -> None:
        '''
        CEMObject = objet CompileExpressionManager
        '''
        isComparaison = self.getComparaisonSymbol() != None
        if isComparaison:
            operator = "cmp"
        else:
            operator = self.__operator
        super(BinaryNode,self).calcCompile(CEMObject)
        op1, op2 = self.__operands
        engine = CEMObject.getEngine()
        if (not isComparaison) and self.isSymetric() and not op2.isLitteral() and op1.isLitteral() and engine.litteralOperatorAvailable(operator, op1.getValue()):
            op1, op2 = op2, op1
        if (not isComparaison) and op2.isLitteral() and engine.litteralOperatorAvailable(operator, op2.getValue()):
            firstToCalc = op1
            secondToCalc = op2
        elif op1.getRegisterCost(engine) >= op2.getRegisterCost(engine):
            firstToCalc = op1
            secondToCalc = op2
        else:
            firstToCalc = op2
            secondToCalc = op1
        firstToCalc.calcCompile(CEMObject)
        if (not isComparaison) and op2.isLitteral() and engine.litteralOperatorAvailable(operator, op2.getValue()):
            CEMObject.pushBinaryOperatorWithLitteral(operator, op2.getValue())
        else:
            secondToCalc.calcCompile(CEMObject)
            CEMObject.pushBinaryOperator(operator, firstToCalc == op1)

    def clone(self) -> 'BinaryNode':
        '''
        Retourne un clone de l'objet et de son arborescence
        '''
        op1, op2 = self.__operands
        cloneOp1 = op1.clone()
        cloneOp2 = op2.clone()
        operator = self.__operator
        return BinaryNode(operator, cloneOp1, cloneOp2)

class ValueNode(ExpressionNode):
    def __init__(self,value):
        '''
        value de type Litteral ou Variable
        '''
        self.__value = value

    def __str__(self) -> str:
        return str(self.__value)

    def isLitteral(self) -> bool:
        return isinstance(self.__value, Litteral)

    def getValue(self) -> Union[Variable,Litteral]:
        """Accesseur
        :return:valeur
        :rtype:Litteral ou Variable
        """
        return self.__value

    def calcCompile(self, CEMObject:CompileExpressionManager) -> None:
        '''
        CEMObject = objet CompileExpressionManager
        '''
        super(ValueNode,self).calcCompile(CEMObject)
        CEMObject.pushValue(self.__value)

    def clone(self) -> 'ValueNode':
        '''
        Retourne un clone de l'objet et de son arborescence
        '''
        return ValueNode(self.__value)

if __name__=="__main__":
    from variable import Variable

    #Vérification de base
    l_1 = ValueNode(Litteral(1))
    l_10 = ValueNode(Litteral(10))
    v_x = ValueNode(Variable("x"))
    v_y = ValueNode(Variable("y"))

    l_m1 = UnaryNode("-", l_1)
    add_x_1 = BinaryNode("+", v_x, l_1)
    sub_y_10 = BinaryNode("-", v_y, l_10)
    m = BinaryNode("*", add_x_1, sub_y_10)
    m2 = BinaryNode("*", l_m1, m)
    tst = BinaryNode("<=", m2, l_10)
    ntst = UnaryNode("not", tst)

    print(ntst)

    # vérification de l'ajustement des test
    ntst_adj = ntst.adjustConditionClone(["==", "<"])
    print(ntst_adj)

    # vérication négation logique
    neg_ntst = ntst.logicNegateClone()
    print(neg_ntst)

    # vérification de la suppression du neg
    neg_replace_tst = ntst.negToSubClone()
    print(neg_replace_tst)
