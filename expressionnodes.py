from errors import *
from compileexpressionmanager import *

class UnaryNode:
    def __init__(self,operator,operand):
        '''
        operator = not, ~, - (moins autant qu'opérateur unaire)
        operand : Node
        '''
        assert operator in "not,-,~"
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

    def getRegisterCost(self):
        return self.__operand._getRegisterCost()

    def nodeNeedUAL(self):
        return True

    def calcCompile(self, CompileExpressionManagerObject):
        self.__operand.calcCompile(CompileExpressionManagerObject)
        if self.__operator == "not":
            raise ExpressionError("opérateur not ne peut être compilé en calcul.")
        registreOperand = CompileExpressionManagerObject.freeRegister()
        registreDestination = CompileExpressionManagerObject.getAvailableRegister()
        if self.__operator == "-":
            operationDecription = "neg"
        else:
            operationDecription = "bitwise not"
        operation = (operationDecription, registreDestination, registreOperand)
        CompileExpressionManagerObject.addNewOperation(operation)

class BinaryNode:
    def __init__(self,operator,operand1, operand2):
        '''
        operator : dans +, -, *, /, %, and, or, &, |
        operand1 et operand2 : objet de type ValueNode, BinaryNode ou UnaryNode
        '''
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

    def getRegisterCost(self):
        costOperand1 = self.__operands[0].getRegisterCost()
        costOperand2 = self.__operands[1].getRegisterCost()
        return min(max(costOperand1, costOperand2+1), max(costOperand1+1, costOperand2))

    def nodeNeedUAL(self):
        return True

    def calcCompile(self, CompileExpressionManagerObject):
        if self.__operands[0].getRegisterCost() >= self.__operands[1].getRegisterCost():
            operand1 = self.__operands[0]
            operand2 = self.__operands[1]
            tokenDirectCalc = True
        else:
            operand2 = self.__operands[0]
            operand1 = self.__operands[1]
            tokenDirectCalc = False
        operand1.calcCompile(CompileExpressionManagerObject)
        memoryUse = CompileExpressionManagerObject.storeToMemory(operand2.getRegisterCost())
        operand2.calcCompile(CompileExpressionManagerObject)
        if memoryUse:
            CompileExpressionManagerObject.loadFromMemory()
        r1 = CompileExpressionManagerObject.freeRegister()
        r2 = CompileExpressionManagerObject.freeRegister()
        registreDestination = CompileExpressionManagerObject.getAvailableRegister()
        if tokenDirectCalc:
            operation = (self.__operator, registreDestination, r1, r2)
        else:
            operation = (self.__operator, registreDestination, r2, r1)
        CompileExpressionManagerObject.addNewOperation(operation)

class ValueNode:
    def __init__(self,value):
        '''
        value de type int ou Variable
        '''
        self.__value = value

    def getType(self):
        return 'int'

    def __str__(self):
        return str(self.__value)

    def getRegisterCost(self):
        return 1

    def nodeNeedUAL(self):
        return False

    def isLitteral(self):
        return isinstance(self.__value, int)

    def calcCompile(self, CompileExpressionManagerObject):
        if self.isLitteral():
            operationDescription = "litteral -> registre"
        else:
            operationDescription = "variable -> registre"
        registreDestination = CompileExpressionManagerObject.getAvailableRegister()
        operation = (operationDescription, self.__value, registreDestination)
        CompileExpressionManagerObject.addNewOperation(operation)

if __name__=="__main__":
    print("Test sur littéral")
    cem = CompileExpressionManager()
    node = ValueNode(4)
    node.calcCompile(cem)
    print(cem)

    print("Test sur opération unaire")
    cem = CompileExpressionManager()
    nodeL = ValueNode(4)
    nodeOp = UnaryNode("-", nodeL)
    nodeOp.calcCompile(cem)
    print(cem)

    print("Test sur opération binaire")
    cem = CompileExpressionManager()
    nodeChild1 = ValueNode(4)
    nodeChild2 = ValueNode(3)
    nodeOp = BinaryNode("-", nodeChild1, nodeChild2)
    nodeOp.calcCompile(cem)
    print(cem)
