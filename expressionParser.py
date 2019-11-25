'''
Module d'analyse des expressions arithmétiques et logiques
'''
from errors import *
import re

class Token:
    @classmethod
    def test(cls, expression):
        return re.match("^"+cls.regex+"$", expression.strip()) != None

    def __init__(self,expression):
        self.expression = expression.strip()

    def __str__(self):
        return self.expression

    def isOperand(self):
        return isinstance(self,TokenVariable) or isinstance(self,TokenNumber)

    def isOperator(self):
        return isinstance(self,TokenBinaryOperator) or isinstance(self,TokenUnaryOperator)


class TokenVariable(Token):
    regex = "[a-zA-Z_][a-zA-Z_0-9]*"

    @classmethod
    def test(cls, expression):
        # les mots and, not or vont matcher avec Variable. Il faut rejeter ces cas
        expression_stripped = expression.strip()
        if expression_stripped in "and;or;not":
            return False
        return super().test(expression_stripped)

class TokenBinaryOperator(Token):
    regex = "<=|==|>=|[<>+\-*\/%&|]|and|or"
    child1 = None
    child2 = None

    def __init__(self,expression):
        self.operator = expression.strip()

    def getOperator(self):
        return self.operator

    def __str__(self):
        if self.child1 == None:
            childStr1 = "?"
        else:
            childStr1 = str(self.child1)
        if self.child2 == None:
            childStr2 = "?"
        else:
            childStr2 = str(self.child2)

        return "( "+childStr1+" "+self.operator+" "+childStr2+" )"

    def getPriority(self):
        if self.operator == "and":
            return 3
        elif self.operator in "<==>":
            return 4
        elif self.operator in "+-":
            return 5
        elif self.operator in "*/&|":
            return 6
        elif self.operator == "%":
            return 7
        else:
            # cas du or
            return 1

    def setChilds(self, child1, child2):
        self.child1 = child1
        self.child2 = child2

class TokenUnaryOperator(Token):
    regex = "~|not"
    child = None

    def __init__(self,expression):
        self.operator = expression.strip()

    def getOperator(self):
        return self.operator

    def __str__(self):
        if self.child == None:
            childStr = "?"
        else:
            childStr = str(self.child)
        return "("+self.operator+" "+childStr+")"

    def getPriority(self):
        if self.operator == "not":
            return 2
        return 6

    def setChild(self, token):
        self.child = token

class TokenNumber(Token):
    regex = "[0-9]+"

    def __init__(self,expression):
        self.value = int(expression.strip())

    def __str__(self):
        return str(self.value)

    def negate(self):
        self.value *= -1
        return self

class TokenParenthesis(Token):
    regex = "\(|\)"

    def isOpening(self):
        return self.expression == "("

class ExpressionParser:
    TokensList =  [TokenVariable, TokenNumber, TokenBinaryOperator, TokenUnaryOperator, TokenParenthesis]

    @staticmethod
    def isLegal(precedent, suivant):
        '''
        précédent, suivant : 2 tokens successifs dont on veut savoir si l'enchaînement est valable
        None si pas de token
        Sortie True si oui
        '''
        if precedent == None:
            if suivant == None:
                return True
            elif isinstance(suivant, TokenBinaryOperator):
                return False
            elif isinstance(suivant, TokenUnaryOperator):
                return True
            elif suivant.isOperand():
                return True
            elif isinstance(suivant, TokenParenthesis):
                return suivant.isOpening()
        elif precedent.isOperator():
            if suivant == None:
                return False
            elif isinstance(suivant, TokenBinaryOperator):
                return False
            elif isinstance(suivant, TokenUnaryOperator):
                return True
            elif suivant.isOperand():
                return True
            elif isinstance(suivant, TokenParenthesis):
                return suivant.isOpening()
        elif precedent.isOperand():
            if suivant == None:
                return True
            elif isinstance(suivant, TokenBinaryOperator):
                return True
            elif isinstance(suivant, TokenUnaryOperator):
                return False
            elif suivant.isOperand():
                return False
            elif isinstance(suivant, TokenParenthesis):
                return not suivant.isOpening()
            else:
                return False
        elif isinstance(precedent, TokenParenthesis):
            if suivant == None:
                return not precedent.isOpening()
            elif isinstance(suivant, TokenBinaryOperator):
                return not precedent.isOpening()
            elif isinstance(suivant, TokenUnaryOperator):
                return precedent.isOpening()
            elif suivant.isOperand():
                return precedent.isOpening()
            elif isinstance(suivant, TokenParenthesis):
                return precedent.isOpening() != suivant.isOpening()
        # par défaut on retourne faux
        return False

    @staticmethod
    def buildReversePolishNotation(tokensList):
        polishStack = []
        waitingStack = []
        for token in tokensList:
            if token.isOperand():
                polishStack.append(token)
            elif isinstance(token, TokenParenthesis) and not token.isOpening():
                while len(waitingStack)>0 and not isinstance(waitingStack[-1], TokenParenthesis):
                    # forcément une parenthèse ouvrante
                    polishStack.append(waitingStack.pop())
            elif isinstance(token, TokenParenthesis):
                # donc un parenthèse ouvrante
                waitingStack.append(token)
            elif token.isOperator():
                # on dépile la pile d'attente si elle contient des opérateurs de priorité plus haute
                while len(waitingStack)>0 and waitingStack[-1].isOperator() and waitingStack[-1].getPriority() >= token.getPriority():
                    polishStack.append(waitingStack.pop())
                waitingStack.append(token)
            else:
                raise ExpressionError(f"Token inconnu : {str(token)}.'")
        # arrivé à la fin des tokens, on vide la pile d'attente
        while len(waitingStack)>0:
            token = waitingStack.pop()
            if token.isOperator():
                polishStack.append(token)
        return polishStack

    @staticmethod
    def buildTree(polishTokensList):
        operandsList = []
        for token in polishTokensList:
            if token.isOperand():
                operandsList.append(token)
            elif isinstance(token,TokenUnaryOperator):
                if len(operandsList) == 0:
                    raise ExpressionError(f"Plus d'opérande pour : {str(token)}.'")
                operand = operandsList.pop()
                token.setChild(operand)
                operandsList.append(token)
            else:
                # opérateur binaire
                if len(operandsList) <2:
                    raise ExpressionError(f"Pas assez d'opérandes pour : {str(token)}.'")
                operand2 = operandsList.pop()
                operand1 = operandsList.pop()
                token.setChilds(operand1, operand2)
                operandsList.append(token)
        # à la fin, normalement, il n'y a qu'un opérande
        if len(operandsList) != 1:
            raise ExpressionError(f"Pas assez d'opérateurs !'")
        return operandsList.pop()

    @classmethod
    def regex(cls):
        regexList = [ "("+Token.regex+")" for Token in cls.TokensList ]
        return "("+"|".join(regexList)+")"

    @classmethod
    def test(cls,expression):
        regex = cls.regex()
        return re.match(f"^(\s*{regex})+\s*$", expression) != None

    def __init__(self, expression):
        self.expression = expression
        if not self.test(expression):
            raise ExpressionError(f"[{self.expression}] => L'expression contient une erreur.'")
        regex = self.regex()
        matchsList = [it[0] for it in re.findall(regex, expression)]
        self.tokens = []
        for item in matchsList:
            for TokenType in self.TokensList:
                if TokenType.test(item):
                    newToken = TokenType(item)
                    self.tokens.append(newToken)
                    break;
        self.consolidAddSub()
        print([str(it) for it in self.tokens])

    def getTokenByIndice(self, indice):
        if indice <0 or indice>=len(self.tokens):
            return None
        return self.tokens[indice]

    def consolidAddSub(self):
        # Certains + et - peuvent recevoir différentes interprétations
        # un + et un donnés après ( ou après début
        indice = 0
        while indice < len(self.tokens):
            token = self.tokens[indice]
            tokenPrecedent = self.getTokenByIndice(indice-1)
            if isinstance(token,TokenBinaryOperator) and token.getOperator() in "+-" and not ExpressionParser.isLegal(tokenPrecedent, token):
                # Ce + ou - doit être rectifié car il ne devrait pas se trouver à la suite de ce qui précède
                if token.getOperator() == "+":
                    # Dans le cas d'un +, il suffit de le supprimer
                    del self.tokens[indice]
                    # inutile de passer au suivant
                elif isinstance(self.getTokenByIndice(indice+1),TokenNumber):
                    # l'opérateur est - et le suivant est un nombre
                    self.getTokenByIndice(indice+1).negate()
                    del self.tokens[indice]
                    # inutile de passer au suivant
                elif tokenPrecedent==None or isinstance(tokenPrecedent,TokenParenthesis) and tokenPrecedent.isOpening():
                    # l'opérateur est - mais il ne peut être intégré au suivant.
                    # on l'interprète comme -1 x
                    tokenMinusOne = TokenNumber("-1")
                    tokenMultiply = TokenBinaryOperator("*")
                    del self.tokens[indice]
                    self.tokens.insert(indice,tokenMultiply)
                    self.tokens.insert(indice,tokenMinusOne)
                    # inutile de passer au suivant
                else:
                    # tout autre cas est une faute et est laissé en l'état
                    # passage au suivant
                    indice += 1
            else:
                # passage au suivant
                indice += 1
