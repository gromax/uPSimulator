from errors import *
from expressionnodes import *
from compileexpressionmanager import *

class Expression:
    def __init__(self, rootNode):
        '''
        Entrée : Arbre représentant l'expression
        Chaque noeud est un noeud dont le type UnaryNode, BinaryNode, LitteralNode ou VariableNode
        '''
        self.__rootNode = rootNode

    def isComplexeCondition(self):
        return self.__rootNode.isComplexeCondition()

    def boolDecompose(self):
        '''
        Sortie : Tuple avec type d'opération, et expression enfants
        si c'est une opération de type not, and, or
        None sinon
        '''
        if isinstance(self.__rootNode,UnaryNode):
            operator, node = self.__rootNode.boolDecompose()
            return operator, Expression(node)
        if isinstance(self.__rootNode,BinaryNode):
            decomp = self.__rootNode.boolDecompose()
            if decomp != None:
                operator, node1, node2 = decomp
                return operator, Expression(node1), Expression(node2)
        return None

    def getType(self):
        '''
        Sortie :
        - 'int' si le résultat est de type 'int',
        - 'bool' si le résultat est de type 'booléen',
        - None en cas d'erreur
        Parcours récursif de l'arbre
        '''
        return self.__rootNode.getType()

    def comparaisonSwap(self):
        '''
        miroir de la comparaison
        '''
        assert self.getType() == 'bool' and not self.__rootNode.isComplexeCondition()
        self.__rootNode.comparaisonSwap()

    def comparaisonNegate(self):
        '''
        retourne une copie négative du symbole de comparaison
        '''
        assert self.getType() == 'bool' and not self.__rootNode.isComplexeCondition()
        return Expression(self.__rootNode.comparaisonNegate())

    def conditionNegate(self):
        '''
        retourne une copie négative de la condition
        '''
        assert self.getType() == 'bool'
        return Expression(self.__rootNode.conditionNegate())

    def getComparaisonSymbol(self):
        '''
        retourne le symbole de comparaison d'une comparaison élémentaire
        '''
        assert self.__rootNode.getType() == 'bool' and not self.__rootNode.isComplexeCondition()
        comparator = self.__rootNode.getComparaisonSymbol()
        assert comparator != None
        return comparator

    def __str__(self):
        '''
        Fonction de conversion de Expression en string
        '''
        return str(self.__rootNode)

    def getRegisterCost(self):
        '''
        Calcul du cout de calcul d'une expression:
        Entrée: Arbre représentant l'expression
        Sortie: Entier
        '''
        return self.__rootNode.getRegisterCost()

    def calcCompile(self, **options):
        if self.getType() != 'int' and self.__rootNode.isComplexeCondition():
            raise CompilationError(f"{str(self)} n'est pas une expression arithmétique ou une comparaison simple.")
        if "cem" in options:
          cem = options["cem"]
        else:
          cem = CompileExpressionManager(**options)
        # Le - unaire pourrait ne pas exister dans les commandes
        if not cem.engine.hasNEG():
            self.__rootNode.negTosub()
        self.__rootNode.calcCompile(cem)
        if "debug" in options and options["debug"] == True:
            print(cem)
        return cem


if __name__=="__main__":
    from variablemanager import *
    print("Test pour l'expression 3*17+9-(4+1)*(2+3)")
    n1 = ValueNode(Litteral(1))
    n2 = ValueNode(Litteral(2))
    n3 = ValueNode(Litteral(3))
    n4 = ValueNode(Litteral(4))
    n9 = ValueNode(Litteral(9))
    n17 = ValueNode(Litteral(17))
    mult3_17 = BinaryNode("*",n3,n17)
    add4_1 = BinaryNode("+", n4, n1)
    add2_3 = BinaryNode("+", n2, n3)
    mult_4p1x2p3 = BinaryNode("*", add4_1, add2_3)
    add_3x17p9 = BinaryNode("+", mult3_17, n9)
    nFinal = BinaryNode("-", add_3x17p9 ,mult_4p1x2p3)

    monExpression = Expression(nFinal)
    cem = CompileExpressionManager()
    monExpression.calcCompile(cem = cem)
    print(cem)

    print()
    print("nouvel essai, même expression avec autorisation d'avoir des littéraux dans les commandes")
    monExpression.calcCompile(litteralInCommand = True, debug = True)

