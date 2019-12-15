from errors import *
from expressionconvert import *

class UnaryNode:
    def __init__(self,operator,operand):
        '''
        operator = not, ~, - (moins autant qu'opérateur unaire)
        operand : Node
        '''
        assert self.operator in "not,-,~"
        self.__operator = operator
        self.__operand = operand

    def boolDecompose(self):
        '''
        Sortie : tuple avec "not" et operand si c'est not
        None sinon
        '''
        if self.__operator != "not":
            return None
        expressionEnfant = Expression(self.__operand)
        return ("not", expressionEnfant)

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
        self.__operands.calcCompile(CompileExpressionManagerObject)
        if self.__operator == "not":
            raise ExpressionError("opérateur not ne peut être compilé en calcul.")
        if self.__operator == "-":
            operation = ('neg', 0)
        else:
            operation = ('bitwise not', 0)
        CompileExpressionManagerObject.addNewOperation(operation)

class BinaryNode:
    def __init__(self,operator,operand1, operand2):
        self.__operator = operator
        self.__operands = operand1, operand2

    def boolDecompose(self):
        '''
        Sortie : si and, or, tuple avec le nom "and" ou "or", et les deux enfants.
        None sinon
        '''
        if self.__operator != "or" and self.__operator != "and":
            return None
        expressionEnfant1 = Expression(self.__operands[0])
        expressionEnfant2 = Expression(self.__operands[1])
        return (self.__operator, expressionEnfant1, expressionEnfant2)

    def getType(self):
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
        if self.__operands[0].getRegisterCost()>=self.__operands[1].getRegisterCost():
            operand1 = self.__operands[0]
            operand2 = self.__operands[1]
            TokenDirectCalc = True
        else:
            operand2 = self.__operands[0]
            operand1 = self.__operands[1]
            TokenDirectCalc = False
        operand1.calcCompile(CompileExpressionManagerObject)
        memoryUse = CompileExpressionManagerObject.storeToMemory(operand2.getRegisterCost())
        operand2.calcCompile(CompileExpressionManagerObject)
        if memoryUse:
            CompileExpressionManagerObject.loadFromMemory()
        r1 = CompileExpressionManagerObject.freeRegister()
        r2 = CompileExpressionManagerObject.freeRegister()
        if TokenDirectCalc:
            operation = (self.__operator, CompileExpressionManagerObject.getAvailableRegister(), r1, r2 )
        else:
            operation = (self.__operator, CompileExpressionManagerObject.getAvailableRegister(), r2, r1)
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

    def calcCompile(self, CompileExpressionManagerObject):
        operation = ('litteral ou variable -> registre', self.__value, CompileExpressionManagerObject.getAvailableRegister()) ## Il conviendra de gérer l'adresse mémoire
        CompileExpressionManagerObject.addNewOperation(operation)

class Expression:
    def __init__(self, rootNode):
        '''
        Entrée : Arbre représentant l'expression
        Chaque noeud est un noeud dont le type UnaryNode, BinaryNode, LitteralNode ou VariableNode
        '''
        self.__rootNode = rootNode

    def boolDecompose(self):
        '''
        Sortie : Tuple avec type d'opération, et expression enfants
        si c'est une opération de type not, and, or
        None sinon
        '''
        if not (isinstance(self.__rootNode,UnaryNode) or isinstance(self.__rootNode,BinaryNode)):
            return None
        return self.__rootNode.boolDecompose()

    def getType(self):
        '''
        Sortie :
        - 'int' si le résultat est de type 'int',
        - 'bool' si le résultat est de type 'booléen',
        - None en cas d'erreur
        Parcours récursif de l'arbre
        '''
        return self.__rootNode.getType()

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

    def calcCompile(self, CompileExpressionManagerObject):
        if self.getType() != 'int':
            raise ExpressionError(f"Cette expression n'appelle pas de calcul'")
        return self.__rootNode.calcCompile(CompileExpressionManagerObject)
