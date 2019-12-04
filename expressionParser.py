'''
Module d'analyse des expressions arithmétiques et logiques
'''
from errors import *
from expression import *
from variableManager import *
import re

class Token:
    @classmethod
    def test(cls, expression):
        return re.match("^"+cls.regex+"$", expression.strip()) != None

    def __init__(self,expression):
        self.expression = expression.strip()

    def isOperand(self):
        return isinstance(self,TokenVariable) or isinstance(self,TokenNumber)

    def isOperator(self):
        return isinstance(self,TokenBinaryOperator) or isinstance(self,TokenUnaryOperator)


class TokenBinaryOperator(Token):
    regex = "<=|==|>=|!=|[<>+\-*\/%&|]|and|or"

    def __init__(self,expression):
        self.__operator = expression.strip()

    def getOperator(self):
        return self.__operator

    def getPriority(self):
        if self.__operator == "and":
            return 3
        elif self.__operator in "<==>":
            return 4
        elif self.__operator in "+-":
            return 5
        elif self.__operator in "*/&|":
            return 6
        elif self.__operator == "%":
            return 7
        else:
            # cas du or
            return 1

    def toNode(self, operandsList):
        '''
        operandsList : liste des opérandes.
        '''
        if len(operandsList) <2:
            raise ExpressionError(f"Pas assez d'opérandes pour : {self.__operator}")
        operand2 = operandsList.pop()
        operand1 = operandsList.pop()
        return BinaryNode(self.__operator, operand1, operand2)

class TokenUnaryOperator(Token):
    regex = "~|not"

    def __init__(self,expression):
        self.__operator = expression.strip()

    def getOperator(self):
        return self.__operator

    def getPriority(self):
        if self.__operator == "not":
            return 2
        return 6

    def toNode(self, operandsList):
        '''
        operandsList : liste des opérandes.
        '''
        if len(operandsList) == 0:
            raise ExpressionError(f"Plus d'opérande pour : {self.__operator}")
        operand = operandsList.pop()
        return UnaryNode(self.__operator, operand)

class TokenVariable(Token):
    regex = "[a-zA-Z_][a-zA-Z_0-9]*"

    @classmethod
    def test(cls, expression):
        # les mots and, not or vont matcher avec Variable. Il faut rejeter ces cas
        expression_stripped = expression.strip()
        if expression_stripped in "and;or;not":
            return False
        return super().test(expression_stripped)

    def getValue(self):
        return self.expression

    def toNode(self, variableManagerObject):
        '''
        variableManagerObject : gestionnaire des variables et des littéraux
        '''
        nomVariable = self.expression
        variableObject = variableManagerObject.addVariableByName(nomVariable)
        return ValueNode(variableObject)

class TokenNumber(Token):
    regex = "[0-9]+"

    def __init__(self,expression):
        self.value = int(expression.strip())

    def negate(self):
        self.value *= -1
        return self

    def getValue(self):
        return self.value

    def toNode(self, variableManagerObject):
        '''
        variableManagerObject : gestionnaire des variables et des littéraux
        '''
        variableManagerObject.addLitteralByValue(self.value)
        return ValueNode(self.value)


class TokenParenthesis(Token):
    regex = "\(|\)"

    def isOpening(self):
        return self.expression == "("

class ExpressionParser:
    TokensList =  [TokenVariable, TokenNumber, TokenBinaryOperator, TokenUnaryOperator, TokenParenthesis]

    @staticmethod
    def testBrackets(expression):
        '''
        Entrée : expression = chaîne de caractères représentant une expression
        Sortie : True si les parenthèses sont équilibrées
        '''
        nbParentheses = 0
        for caractere in expression :
            if caractere == '(':
                nbParentheses += 1
            elif caractere == ')': nbParentheses -= 1
            if nbParentheses < 0 : return False
        if nbParentheses > 0 : return False
        return True

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
    def __buildReversePolishNotation(tokensList):
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
                raise ExpressionError(f"Token inconnu : {str(token)}")
        # arrivé à la fin des tokens, on vide la pile d'attente
        while len(waitingStack)>0:
            token = waitingStack.pop()
            if token.isOperator():
                polishStack.append(token)
        return polishStack

    @staticmethod
    def __buildTree(polishTokensList, variableManagerObject):
        '''
        Entrées :
           polishTokensList : list de Tokens construite en utilisant la notation polonaise inversée
           variableManagerObject : objet de gestion des variables
        Sortie : Noeud racine de l'expression
        '''
        operandsList = []
        for token in polishTokensList:
            if token.isOperand():
                node = token.toNode(variableManagerObject)
            else:
                node = token.toNode(operandsList)
            operandsList.append(node)
        # à la fin, normalement, il n'y a qu'un opérande
        if len(operandsList) != 1:
            raise ExpressionError(f"Pas assez d'opérateurs !'")
        return operandsList.pop()

    @classmethod
    def __tokensListIsLegal(cls, tokensList):
        '''
        Entrée : liste de tokens
        Sortie : True si la succession est valable, c'est à dire s'il n'y a pas de succession telle que (* ou +*
        '''
        if len(tokensList) == 0:
            return True
        tokenPrecedent = None
        for tokenCourant in tokensList:
            if not cls.isLegal(tokenPrecedent, tokenCourant):
                return False
            tokenPrecedent = tokenCourant
        # Le dernier Token est il valable en tant que dernier token ?
        if not cls.isLegal(tokenPrecedent, None):
            return False
        return True

    @classmethod
    def regex(cls):
        regexList = [ "("+Token.regex+")" for Token in cls.TokensList ]
        return "("+"|".join(regexList)+")"

    @classmethod
    def strIsVariableName(cls,nomVariable):
        '''
        Entrée : nomVariable = chaine de caractère à tester
        Sortie : True si c'est un nom de variable valable
        '''
        regex = TokenVariable
        return re.match(f"^(\s*{regex})+\s*$", nomVariable) != None

    @classmethod
    def strIsExpression(cls,expression):
        '''
        Entrée : expression = chaîne de caractère
        Sortie : True la chaîne de caractère contient une expression arithmétique ou logique
        '''
        regex = cls.regex()
        return re.match(f"^(\s*{regex})+\s*$", expression) != None

    @classmethod
    def __buildTokensList(cls, expression):
        regex = cls.regex()
        matchsList = [it[0] for it in re.findall(regex, expression)]
        tokensList = []
        for item in matchsList:
            for TokenType in cls.TokensList:
                if TokenType.test(item):
                    newToken = TokenType(item)
                    tokensList.append(newToken)
                    break;
        return cls.__consolidAddSub(tokensList)

    @classmethod
    def __consolidAddSub(cls,tokensList):
        # Certains + et - peuvent recevoir différentes interprétations
        # un + et un donnés après ( ou après début
        indice = 0
        while indice < len(tokensList):
            token = tokensList[indice]
            if indice <= 0:
                tokenPrecedent = None
            else:
                tokenPrecedent = tokensList[indice-1]
            if indice >= len(tokensList)-1:
                tokenSuivant = None
            else:
                tokenSuivant = tokensList[indice+1]


            if isinstance(token,TokenBinaryOperator) and token.getOperator() in "+-" and not ExpressionParser.isLegal(tokenPrecedent, token):
                # Ce + ou - doit être rectifié car il ne devrait pas se trouver à la suite de ce qui précède
                if token.getOperator() == "+":
                    # Dans le cas d'un +, il suffit de le supprimer
                    del tokensList[indice]
                    # inutile de passer au suivant
                elif isinstance(tokenSuivant,TokenNumber):
                    # l'opérateur est - et le suivant est un nombre
                    tokenSuivant.negate()
                    del tokensList[indice]
                    # inutile de passer au suivant
                elif tokenPrecedent==None or isinstance(tokenPrecedent,TokenParenthesis) and tokenPrecedent.isOpening():
                    # l'opérateur est - mais il ne peut être intégré au suivant.
                    # on l'interprète comme -1 x
                    tokenMinusOne = TokenNumber("-1")
                    tokenMultiply = TokenBinaryOperator("*")
                    del tokensList[indice]
                    tokensList.insert(indice,tokenMultiply)
                    tokensList.insert(indice,tokenMinusOne)
                    # inutile de passer au suivant
                else:
                    # tout autre cas est une faute et est laissé en l'état
                    # passage au suivant
                    indice += 1
            else:
                # passage au suivant
                indice += 1
        return tokensList

    def __init__(self, variableManagerObject=None):
        if variableManagerObject == None:
            self.__variableManager = VariableManager()
        else:
            assert isinstance(variableManagerObject, VariableManager)
            self.__variableManager = variableManagerObject
    def buildExpression(self, originalExpression):
        '''
        Entrée : chaine de caractères expression
        Sortie : Objet expression
        '''
        expression = originalExpression.strip()
        if not self.strIsExpression(expression):
            raise ExpressionError(f"{originalExpression} : Expression incorrecte.")
        if not self.testBrackets(expression):
            raise ExpressionError(f"{originalExpression} : Les parenthèses ne sont pas équilibrées.")
        tokensList = ExpressionParser.__buildTokensList(expression)
        if not self.__tokensListIsLegal(tokensList):
            raise ExpressionError(f"{originalExpression} : Erreur. Vérifiez.")
        reversePolishTokensList = self.__buildReversePolishNotation(tokensList)
        rootNodeTree = ExpressionParser.__buildTree(reversePolishTokensList, self.__variableManager)

        return Expression(rootNodeTree)

