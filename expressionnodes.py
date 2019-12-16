from errors import *
from compileexpressionmanager import *

class Node:
    def isLitteral(self):
        return False

    def needUAL(self):
        return True

    def getRegisterCost(self, litteralInCommand):
        return 1

    def calcCompile(self, CompileExpressionManagerObject):
        litteralInCommand = CompileExpressionManagerObject.litteralInCommand
        myCost = self.getRegisterCost(litteralInCommand)
        needUAL =self.needUAL()
        CompileExpressionManagerObject.getNeededRegisterSpace(myCost, needUAL)

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

    def boolDecompose(self):
        '''
        Sortie : tuple avec "not" et operand si c'est not
        None sinon
        '''
        if self.__operator != "not":
            return None
        return "not", self.__operand

    def getType(self):
        operandType = self.__operand.getType()
        if operandType == None or (self.__operator == '~' and operandType=='bool'):
            return None
        elif self.__operator == "not":
            return 'bool'
        return 'int'

    def __str__(self):
        strOperand = str(self.__operand)
        return self.__operator+"("+strOperand+")"

    def getRegisterCost(self, litteralInCommand):
        return self.__operand.getRegisterCost(litteralInCommand)

    def needUAL(self):
        return True

    def calcCompile(self, CompileExpressionManagerObject):
        if self.__operator == "not":
            raise ExpressionError("opérateur not ne peut être compilé en calcul.")
        super(UnaryNode,self).calcCompile(CompileExpressionManagerObject)
        litteralInCommand = CompileExpressionManagerObject.litteralInCommand
        if litteralInCommand and self.__operand.isLitteral():
            litteral =
            CompileExpressionManagerObject.pushUnaryOperatorWithLitteral(self.__operator, self.__operand.getValue())
        else:
            self.__operand.calcCompile(CompileExpressionManagerObject)
            CompileExpressionManagerObject.pushUnaryOperator(self.__operator)

class BinaryNode(Node):
    __knownOperators = ('+', '-', '*', '/', '%', 'and', 'or', '&', '|')
    __symetricOperators = ('+', '*', '&', '|')
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

    def boolDecompose(self):
        '''
        Sortie : si and, or, tuple avec le nom "and" ou "or", et les deux enfants.
        None sinon
        '''
        if self.__operator != "or" and self.__operator != "and":
            return None
        return self.__operator, self.__operands[0], self.__operands[1]

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

    def __str__(self):
        strOperand1 = str(self.__operands[0])
        strOperand2 = str(self.__operands[1])
        return "(" + strOperand1 + " " + self.__operator + " " + strOperand2 + ")"

    def getRegisterCost(self, litteralInCommand):
        op1, op2 = self.__operands
        if litteralInCommand and op2.isLitteral():
            return op1.getRegisterCost(litteralInCommand)
        if litteralInCommand and self.isSymetric() and op1.isLitteral():
            return op2.getRegisterCost(litteralInCommand)
        costOperand1 = op1.getRegisterCost(litteralInCommand)
        costOperand2 = op2.getRegisterCost(litteralInCommand)
        return min(max(costOperand1, costOperand2+1), max(costOperand1+1, costOperand2))

    def isSymetric(self):
        return self.__operator in self.__symetricOperators

    def needUAL(self):
        return True

    def calcCompile(self, CompileExpressionManagerObject):
        super(BinaryNode,self).calcCompile(CompileExpressionManagerObject)
        litteralInCommand = CompileExpressionManagerObject.litteralInCommand
        op1, op2 = self.__operands
        if litteralInCommand and self.isSymetric() and not op2.isLitteral() and op1.isLitteral():
            op1, op2 = op2, op1
        if litteralInCommand and op2.isLitteral():
            firstToCalc = op1
            secondToCalc = op2
        elif op1.getRegisterCost(litteralInCommand) >= op2.getRegisterCost(litteralInCommand):
            firstToCalc = op1
            secondToCalc = op2
        else:
            firstToCalc = op2
            secondToCalc = op1
        firstToCalc.calcCompile(CompileExpressionManagerObject)
        if litteralInCommand and op2.isLitteral():
            CompileExpressionManagerObject.pushBinaryOperatorWithLitteral(self.__operator, op2.getValue())
        else:
            secondToCalc.calcCompile(CompileExpressionManagerObject)
            CompileExpressionManagerObject.pushBinaryOperator(self.__operator, firstToCalc == op1)

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

    def calcCompile(self, CompileExpressionManagerObject):
        super(ValueNode,self).calcCompile(CompileExpressionManagerObject)
        CompileExpressionManagerObject.pushValue(self.__value)

if __name__=="__main__":
    from variablemanager import *
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
