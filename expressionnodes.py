from errors import *
from compileexpressionmanager import *
from variablemanager import *
from litteral import Litteral

'''
Les noeuds ne sont jamais modifiés. Les modifications sont faites sur des clones
'''

class Node:
    def isLitteral(self):
        return False

    def needUAL(self):
        return True

    def getRegisterCost(self, engine):
        return 1

    def calcCompile(self, CEMObject):
        '''
        CEMObject = objet CompileExpressionManager
        '''
        engine = CEMObject.getEngine()
        myCost = self.getRegisterCost(engine)
        needUAL =self.needUAL()
        CEMObject.getNeededRegisterSpace(myCost, needUAL)

    def isComplexeCondition(self):
        return False

    def getComparaisonSymbol(self):
        '''
        Utile seulement pour BinaryNode avec opérateur <, <=, ==, =>, >, !=
        '''
        return None

    def adjustConditionClone(self,csl):
        '''
        csl = liste de string : symboles de comparaisons disponibles
        modification seulement pour condition élémentaire
        '''
        return self

    def negToSubClone(self):
        '''
        vm = VariableManager, nécessaire pour ajouter le littéral 0 au besoin
        modifie les - unaires de l'arborescence en - binaire
        Seuls les UnaryNode et BinaryNode, qui peuvent être affectés
        par une telle modification, sont clonés
        '''
        return self

    def logicNegateClone(self):
        '''
        retourne un clone avec négation logique s'il y a lieu
        '''
        return self

    def clone(self):
        '''
        Seuls les Unary et Binary sont clonés. Les feuilles terminales ne sont pas modifiées
        '''
        return self


class UnaryNode(Node):
    __knownOperators = ('not', '~', '-')
    def __init__(self,operator,operand):
        '''
        operator = not, ~, - (moins autant qu'opérateur unaire)
        operand : Node
        '''
        assert operator in self.__knownOperators
        assert isinstance(operand,Node)
        self.__operator = operator
        self.__operand = operand

    def isComplexeCondition(self):
        return self.__operator == "not"

    def boolDecompose(self):
        '''
        Sortie : tuple avec "not" et operand si c'est not
        None sinon
        '''
        if self.__operator != "not":
            return None
        return "not", self.__operand

    def logicNegateClone(self):
        '''
        retourne un clone avec négation logique s'il y a lieu
        '''
        if self.__operator == "not":
            return self.__operand.clone()
        return self.clone()

    def adjustConditionClone(self,csl):
        '''
        csl = liste de string : symboles de comparaisons disponibles
        '''
        if self.__operator != "not":
            return self
        newOp = self.__operand.adjustConditionClone(csl)
        return UnaryNode("not", newOp)

    def getType(self):
        operandType = self.__operand.getType()
        if operandType == None or (self.__operator == '~' and operandType=='bool'):
            return None
        elif self.__operator == "not":
            return 'bool'
        return 'int'

    def negToSubClone(self, vm):
        '''
        vm = VariableManager, nécessaire pour ajouter le littéral 0 au besoin
        Si -, c'est un - unaire remplacé par une soustraction (binaire)
        retourne un clone avec les modifications s'il y a lieu
        '''
        newOperand = self.__operand.negToSubClone()
        if not self.__operator == "-":
            return UnaryNode(self.__operator, newOperand)
        zero = Litteral(0)
        return BinaryNode("-", zero, newOperand)

    def __str__(self):
        strOperand = str(self.__operand)
        return self.__operator+"("+strOperand+")"

    def getRegisterCost(self, engine):
        return self.__operand.getRegisterCost(engine)

    def needUAL(self):
        return True

    def calcCompile(self, CEMObject):
        '''
        CEMObject = objet CompileExpressionManager
        '''
        if self.__operator == "not":
            raise ExpressionError("opérateur not ne peut être compilé en calcul.")
        super(UnaryNode,self).calcCompile(CEMObject)
        engine = CEMObject.getEngine()
        if engine.litteralOperatorAvailable(self.__operator) and self.__operand.isLitteral():
            litteral = self.__operand.getValue()
            CEMObject.pushUnaryOperatorWithLitteral(self.__operator, litteral)
        else:
            self.__operand.calcCompile(CEMObject)
            CEMObject.pushUnaryOperator(self.__operator)
    def clone(self):
        cloneOperand = self.__operand.clone()
        operator = self.__operator
        return UnaryNode(operator, cloneOperand)

class BinaryNode(Node):
    __knownOperators = ('+', '-', '*', '/', '%', 'and', 'or', '&', '|', '<', '>', '<=', '>=', '==')
    __symetricOperators = ('+', '*', '&', '|')
    __logicalOperators = ("and", "or")
    __comparaisonOperators = ("<=", "<", ">=", ">", "==", "!=")
    def __init__(self,operator,operand1, operand2):
        '''
        operator : dans +, -, *, /, %, and, or, &, |
        operand1 et operand2 : objet de type Node
        '''
        assert operator in self.__knownOperators
        assert isinstance(operand1,Node)
        assert isinstance(operand2,Node)
        self.__operator = operator
        self.__operands = operand1, operand2

    def isComplexeCondition(self):
        return self.__operator == "or" or self.__operator == "and"

    def boolDecompose(self):
        '''
        Sortie : si and, or, tuple avec le nom "and" ou "or", et les deux enfants.
        None sinon
        '''
        if self.__operator != "or" and self.__operator != "and":
            return None
        return self.__operator, self.__operands[0], self.__operands[1]

    def logicNegateClone(self):
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

    def adjustConditionClone(self,csl):
        '''
        csl = liste de string : symboles de comparaisons disponibles
        '''
        if self.__operator in self.__logicalOperators:
            op1, op2 = self.__operands
            newOp1 = op1.adjustConditionClone(csl)
            newOp2 = op2.adjustConditionClone(csl)
            return BinaryNode(self.__operator, newOp1, newOp2)
        if self.__operator in self.__comparaisonOperators and not self.__operator in csl:
            miroir = { "<":">", ">":"<", "<=":"=>", ">=":"<=" }
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

    def comparaisonMirrorClone(self):
        if self.getComparaisonSymbol() != None:
            op1, op2 = self.__operands
            miroir = { "<":">", ">":"<", "<=":"=>", ">=":"<=" }
            if self.__operator in miroir:
                newOperator = miroir[self.__operator]
            else:
                newOperator = self.__operator
            return BinaryNode(newOperator, op2, op1)
        # pas de modification, sans objet
        return self

    def getType(self):
        '''
        Sortie =
          'bool' si opération de type booléen
          'int' si opération de type entier
          None si construction invalide
        '''
        operand1Type = self.__operands[0].getType()
        operand2Type = self.__operands[1].getType()
        if operand1Type != operand2Type or operand1Type == None or operand2Type == None:
            return None
        elif operand1Type == 'bool' and self.__operator in "+-*/%&|":
            # cas opérateur entier agissant sur opérandes logiques
            return None
        elif operand1Type == 'bool' and self.__operator in "and;or":
            # cas opérateur logique agissant sur opérandes logiques
            return 'bool'
        elif operand1Type == 'bool':
            # cas ==, <=...
            return None
        elif self.__operator in "and;or":
            # cas opérateur logique agissant sur entiers
            return None
        elif self.__operator in "+-*/%&|":
            # cas opérateur entier agissant sur entier
            return 'int'
        else:
            # cas == <=... agissant sur entier
            return 'bool'

    def negToSubClone(self, vm):
        '''
        vm = VariableManager, nécessaire pour ajouter le littéral 0 au besoin
        modifie les - unaires de l'arborescence en - binaire
        '''
        op1, op2 = self.__operands
        newOp1 = op1.negToSubClone(vm)
        newOp2 = op2.negToSubClone(vm)
        return BinaryNode(self.__operator, newOp1, newOp2)

    def __str__(self):
        strOperand1 = str(self.__operands[0])
        strOperand2 = str(self.__operands[1])
        return "(" + strOperand1 + " " + self.__operator + " " + strOperand2 + ")"

    def getRegisterCost(self, engine):
        op1, op2 = self.__operands
        if engine.litteralOperatorAvailable(self.__operator) and op2.isLitteral():
            return op1.getRegisterCost(engine)
        if engine.litteralOperatorAvailable(self.__operator) and self.isSymetric() and op1.isLitteral():
            return op2.getRegisterCost(engine)
        costOperand1 = op1.getRegisterCost(engine)
        costOperand2 = op2.getRegisterCost(engine)
        return min(max(costOperand1, costOperand2+1), max(costOperand1+1, costOperand2))

    def isSymetric(self):
        return self.__operator in self.__symetricOperators

    def needUAL(self):
        return True

    def calcCompile(self, CEMObject):
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
        litteralAvailable = (not isComparaison) and engine.litteralOperatorAvailable(operator)
        if litteralAvailable and self.isSymetric() and not op2.isLitteral() and op1.isLitteral():
            op1, op2 = op2, op1
        if litteralAvailable and op2.isLitteral():
            firstToCalc = op1
            secondToCalc = op2
        elif op1.getRegisterCost(engine) >= op2.getRegisterCost(engine):
            firstToCalc = op1
            secondToCalc = op2
        else:
            firstToCalc = op2
            secondToCalc = op1
        firstToCalc.calcCompile(CEMObject)
        if litteralAvailable and op2.isLitteral():
            CEMObject.pushBinaryOperatorWithLitteral(operator, op2.getValue())
        else:
            secondToCalc.calcCompile(CEMObject)
            CEMObject.pushBinaryOperator(operator, firstToCalc == op1)

    def clone(self):
        op1, op2 = self.__operands
        cloneOp1 = op1.clone()
        cloneOp2 = op2.clone()
        operator = self.__operator
        return Binary(operator, cloneOp1, cloneOp2)

class ValueNode(Node):
    def __init__(self,value):
        '''
        value de type int ou Variable
        '''
        self.__value = value

    def getType(self):
        return 'int'

    def __str__(self):
        return str(self.__value)

    def isLitteral(self):
        return self.__value.isLitteral()

    def getValue(self):
        return self.__value

    def calcCompile(self, CEMObject):
        '''
        CEMObject = objet CompileExpressionManager
        '''
        super(ValueNode,self).calcCompile(CEMObject)
        CEMObject.pushValue(self.__value)

if __name__=="__main__":
    from litteral import Litteral
    print("Test sur littéral")
    cem = CompileExpressionManager()
    node = ValueNode(Litteral(4))
    node.calcCompile(cem)
    print(cem)

    print("Test sur opération unaire")
    cem = CompileExpressionManager()
    nodeL = ValueNode(Litteral(4))
    nodeOp = UnaryNode("-", nodeL)
    nodeOp.calcCompile(cem)
    print(cem)

    print("Test sur opération binaire")
    cem = CompileExpressionManager()
    nodeChild1 = ValueNode(Litteral(4))
    nodeChild2 = ValueNode(Litteral(3))
    nodeOp = BinaryNode("-", nodeChild1, nodeChild2)
    nodeOp.calcCompile(cem)
    print(cem)
