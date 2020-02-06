"""
.. module:: expressionparser
   :synopsis: gestion du parse des expressions arithmétiques et logiques

"""

from typing import List, Union


from errors import *
from litteral import Litteral
from variable import Variable
from expressionnodes import ExpressionNode, ValueNode, UnaryNode, BinaryNode
import re

class Token:
    regex:str
    @classmethod
    def test(cls, expression:str) -> bool:
        """Chaque type de noeud est associé à une expression régulière

        :param expression: expression à tester
        :type expression: str
        :return: vrai si l'expression valide l'expression régulière
        :rtype: bool
        """
        return re.match("^"+cls.regex+"$", expression.strip()) != None

    def __init__(self,expression):
        """Constructeur

        :param expression: expression
        :type expression: str
        """
        self.expression = expression.strip()

    def isOperand(self) -> bool:
        """Le token est-il une opérande ?

        :return: vrai le token est un nombre ou une variable
        :rtype: bool
        """
        return isinstance(self,TokenVariable) or isinstance(self,TokenNumber)

    def isOperator(self) -> bool:
        """Le token est-il une opérateur de calcul ?

        :return: vrai le token est un opérateur, binaire ou unaire
        :rtype: bool
        """
        return isinstance(self,TokenBinaryOperator) or isinstance(self,TokenUnaryOperator)

    def getPriority(self) -> int:
        """Fonction par défaut

        :return: priorité de l'opérateur
        :rtype: int
        """
        return 0

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str
        """
        return "Token ?"


class TokenBinaryOperator(Token):
    regex:str = "<=|==|>=|!=|[\^<>+\-*\/%&|]|and|or"

    def __init__(self,operator:str):
        """Constructeur

        :param operator: operateur
        :type operator: str
        """
        self.__operator = operator.strip()

    def getOperator(self) -> str:
        """Accesseur

        :return: opérateur
        :rtype: str
        """
        return self.__operator

    def getPriority(self) -> int:
        """
        :return: priorité de l'opérateur
        :rtype: int
        """
        if self.__operator == "and":
            return 3
        elif self.__operator in "<==>":
            return 4
        elif self.__operator in "+-":
            return 5
        elif self.__operator == "|":
            return 6
        elif self.__operator in "*/&^":
            return 7
        elif self.__operator == "%":
            return 8
        else:
            # cas du or
            return 1

    def toNode(self, operandsList:List[ExpressionNode]) -> BinaryNode:
        """Conversion en objet ExpressionNode

        :param operandsList: opérandes enfants
        :type operandsList: list(ExpressionNode)
        :return: noeud binaire expression correspondant
        :rtype: BinaryNode
        :raises: ExpressionError si pas assez d'opérandes pour l'opérateur demandé
        """
        if len(operandsList) <2:
            raise ExpressionError(f"Pas assez d'opérandes pour : {self.__operator}")
        operand2 = operandsList.pop()
        operand1 = operandsList.pop()
        return BinaryNode(self.__operator, operand1, operand2)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str
        """
        return str(self.__operator)

class TokenUnaryOperator(Token):
    regex:str = "~|not"

    def __init__(self,operator:str):
        """Constructeur

        :param operator: operateur
        :type operator: str
        """
        self.__operator = operator.strip()

    def getOperator(self) -> str:
        """Accesseur

        :return: opérateur
        :rtype: str
        """
        return self.__operator

    def getPriority(self) -> int:
        """
        :return: priorité de l'opérateur
        :rtype: int
        """
        if self.__operator == "not":
            return 2
        return 6

    def toNode(self, operandsList:List[ExpressionNode]) -> Union[ValueNode,UnaryNode]:
        """Conversion en objet ExpressionNode

        :param operandsList: opérandes enfants
        :type operandsList: list(ExpressionNode,ExpressionNode)
        :return: noeud unaire ou valeur correspondant
        :rtype: UnaryNode / ValueNode
        :raises: ExpressionError s'il n'y a plus d'opérande à dépiler dans la pile des opérandes

        .. note:

        un - unaire sur un littéral est aussitôt convertit en l'opposé de ce littéral
        """
        if len(operandsList) == 0:
            raise ExpressionError(f"Plus d'opérande pour : {self.__operator}")
        operand = operandsList.pop()
        # Le cas NEG sur litteral devrait se contenter de preondre l'opposé du littéral
        opTryValue = operand.getValue()
        if self.__operator == "-" and isinstance(opTryValue,Litteral):
            negLitt = opTryValue.negClone()
            return ValueNode(negLitt)
        return UnaryNode(self.__operator, operand)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str
        """
        return str(self.__operator)


class TokenVariable(Token):
    regex:str = "[a-zA-Z][a-zA-Z_0-9]*"

    @classmethod
    def test(cls, expression:str) -> bool:
        """Teste si l'expression correspond à nom de variable valide

        :param expression: expression à tester
        :type expression: str
        :return: vrai si l'expression valide l'expression régulière
        :rtype: bool

        .. note: Les mots and, not, or vont valider l'expression régulière mais doivent être rejetés
        """

        expression_stripped = expression.strip()
        if expression_stripped in "and;or;not":
            return False
        return super().test(expression_stripped)

    def getValue(self) -> str:
        """Accesseur

        :return: expression
        :rtype: str
        """
        return self.expression

    def toNode(self):
        """Conversion en objet ExpressionNode

        .. note:: Crée un objet Variable correspondant

        :return: noeud valeur correspondant
        :rtype: ValueNode
        """
        nomVariable = self.expression
        variableObject = Variable(nomVariable)
        return ValueNode(variableObject)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str
        """
        return str(self.expression)

class TokenNumber(Token):
    regex:str = "[0-9]+"
    __value:int

    def __init__(self,expression):
        """Constructeur

        :param expression: chaîne de texte représentannt le nombre
        :type operator: str
        """
        self.__value = int(expression.strip())

    def getValue(self) -> int:
        """Accesseur

        :return: valeur
        :rtype: int
        """
        return self.__value

    def toNode(self):
        """Conversion en objet ExpressionNode

        .. note:: Crée un objet Litteral correspondant

        :return: noeud valeur correspondant
        :rtype: ValueNode
        """
        litteralObject = Litteral(self.__value)
        return ValueNode(litteralObject)

    def __str__(self) -> str:
        """Transtypage -> str

        :return: version chaîne de caractères de ce token
        :rtype: str
        """
        return str(self.__value)


class TokenParenthesis(Token):
    regex:str = "\(|\)"

    def isOpening(self) -> bool:
        """

        :return: vrai si la parenthèse est ouvrante
        :rtype: bool
        """
        return self.expression == "("

class ExpressionParser:
    TokensList =  [TokenVariable, TokenNumber, TokenBinaryOperator, TokenUnaryOperator, TokenParenthesis]

    @staticmethod
    def testBrackets(expression) -> bool:
        """Test l'équilibre des parenthèses

        :return: vrai si les parenthèses sont équilibrées
        :rtype: bool

        :Example:
          >>> ExpressionParser.testBrackets('4*x - ((3 + 2) + 4)')
          True
          >>> ExpressionParser.testBrackets('( ( ( ) ) ')
          False
          >>> ExpressionParser.testBrackets('( ( ) ) ) ')
          False
          >>> ExpressionParser.testBrackets('( ) ) (')
          False
        """

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
        """Test si l'enchaînement de deux Token est possible. Par exemple '*' ne peut pas suivre '('

        - un opérateur binaire ne peut être en première ou dernière place
        - ')' ne peut être en premier ni '(' à la fin
        - deux opérateurs binaires ne peuvent pas se suivre
        - un opérateur binaire ne peut pas suivre '(' ou précéder ')'
        - une opérande (nombre/variable) ne peut précéder un opérateur unaire
        - deux opérandes ne peuvent se suivre
        - deux parenthèses différentes ne peuvent se suivre : '()' et ')(' interdits

        :return: vrai si l'enchaînement est possible
        :rtype: bool

        :Exemple:
          >>> ExpressionParser.isLegal(TokenParenthesis('('), TokenBinaryOperator('+'))
          False
          >>> ExpressionParser.isLegal(TokenParenthesis(')'), TokenBinaryOperator('+'))
          True
          >>> ExpressionParser.isLegal(TokenParenthesis('('), TokenUnaryOperator('-'))
          True
          >>> ExpressionParser.isLegal(TokenParenthesis('('), TokenBinaryOperator('-'))
          False
        """

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
    def __buildReversePolishNotation(tokensList:List[Token]) -> List[Token]:
        """Construit l'expression dans une notation polonaise inversée

        :param tokensList: liste brute des tokens
        :type tokensList: list(Token)
        :return: liste des tokens en notation représentant l'expression en notation polonaise inversée
        :rtype: list(Token)

        :Exemple:
        >>> tokensList = ExpressionParser._ExpressionParser__buildTokensList('(3 + 4) * 5 - 7 / 8')

        >>> polishList = ExpressionParser._ExpressionParser__buildReversePolishNotation(tokensList)

        >>> " ".join([str(token) for token in polishList])
        '3 4 + 5 * 7 8 / -'

        .. note::

        L'effet de cette notation est de supprimer les parenthèses

        """

        polishStack:List[Token] = []
        waitingStack:List[Token] = []
        for token in tokensList:
            if token.isOperand():
                polishStack.append(token)
            elif isinstance(token, TokenParenthesis) and not token.isOpening():
                while len(waitingStack)>0 and not isinstance(waitingStack[-1], TokenParenthesis):
                    # forcément une parenthèse fermante
                    polishStack.append(waitingStack.pop())
            elif isinstance(token, TokenParenthesis):
                # donc un parenthèse ouvrante
                waitingStack.append(token)
            elif token.isOperator():
                # on dépile la pile d'attente si elle contient des opérateurs de priorité plus haute
                while len(waitingStack)>0 and waitingStack[-1].isOperator() and waitingStack[-1].getPriority() >= token.getPriority():
                    polishStack.append(waitingStack.pop())
                waitingStack.append(token)
        # arrivé à la fin des tokens, on vide la pile d'attente
        while len(waitingStack)>0:
            token = waitingStack.pop()
            if token.isOperator():
                polishStack.append(token)
        return polishStack

    @staticmethod
    def __buildTree(polishTokensList:List[Token]) -> ExpressionNode:
        """Construit l'arbre représentant l'expression

        :param polishTokensList: liste des tokens dans la version polonaise inversée
        :type polishTokensList: list(Token)
        :return: noeud racine de l'arbre représentant l'expression
        :rtype: ExpressionNode
        :raises: ExpressionError s'il reste plus d'un opérande en fin de traitement.
        Arrive si pas assez d'opérateurs pour combiner les opérandes.
        """

        operandsList:List[ExpressionNode] = []
        for token in polishTokensList:
            if isinstance(token,TokenVariable) or isinstance(token,TokenNumber):
                node = token.toNode()
                operandsList.append(node)
            elif isinstance(token,TokenUnaryOperator) or isinstance(token,TokenBinaryOperator):
                node = token.toNode(operandsList)
                operandsList.append(node)
        # à la fin, normalement, il n'y a qu'un opérande
        if len(operandsList) != 1:
            raise ExpressionError(f"Pas assez d'opérateurs !'")
        return operandsList.pop()

    @classmethod
    def __tokensListIsLegal(cls, tokensList:List[Token]) -> bool:
        """Teste si la liste de tokens un enchaînement de paire autorisées

        :param tokensList: liste brute des tokens
        :type tokensList: list[Token]
        :return: Vrai si l'enchaînement de token est autorisé
        :rtype: bool
        """

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
    def variableRegex(cls) -> str:
        """Donne accès à l'expression régulière d'une variable

        :return: expression régulière d'une variable
        :rtype: str
        """
        return TokenVariable.regex

    @classmethod
    def expressionRegex(cls) -> str:
        """Donne accès à l'expression régulière d'une expression

        :return: expression régulière d'une expression
        :rtype: str
        """
        return f"(\s*{cls.regex()})+"

    @classmethod
    def regex(cls) -> str:
        """Concatène les expressions régulière pour les différents constituants d'une expression

        :return: expression régulière d'un item d'expression
        :rtype: str
        """
        regexList = [ "("+Token.regex+")" for Token in cls.TokensList ]
        return "("+"|".join(regexList)+")"

    @classmethod
    def strIsVariableName(cls, nomVariable:str) -> bool:
        """Teste si une chaîne de caractères est un nom de variable possible.

        Exclut les mots-clefs du langage

        :param expression: expression à tester
        :type exression: str
        :return: vrai si le nom est valable
        :rtype: bool
        """
        regex = TokenVariable.regex
        nomVariable = nomVariable.strip()
        if nomVariable in ("if", "else", "elif", "else", "while", "print", "input", "and", "or", "not"):
            return False
        return re.match(f"^(\s*{regex})+\s*$", nomVariable) != None

    @classmethod
    def strIsExpression(cls, expression:str) -> bool:
        """Teste si une chaîne de caractères est une expression possible.

        :param expression: expression à tester
        :type exression: str
        :return: vrai si l'expression est valable
        :rtype: bool

        :Example:
          >>> ExpressionParser.strIsExpression("45x-3zdf = dz")
          False
          >>> ExpressionParser.strIsExpression("45*x-3+zdf - dz")
          True
        """

        regex = cls.regex()
        return re.match(f"^(\s*{regex})+\s*$", expression) != None

    @classmethod
    def __buildTokensList(cls, expression:str) -> List[Token]:
        """Transforme une expression en une liste de tokens représentant chacun un item de l'expression.

        :param expression: expression à tester
        :type exression: str
        :return: La liste des tokens tels que donnés dans l'expression
        :rtype: list(Token)

        .. note:: Les symboles + et - est ambigu car ils peuvent être compris comme des symboles unaires ou binaires. On réalise un traitement pour lever l'ambiguité.
        """

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
    def __consolidAddSub(cls, tokensList:List[Token]) -> List[Token]:
        """Cherche les + et les - pour lever l'ambiguité sur leur arité : un - ou un + peut être unaire ou binaire.

        - À la détection, tous les - et + sont compris comme binaires par défaut,
        - Un + compris comme unaire peut être supprimé,
        - Un - compris comme unaire doit recevoir un token unaire en remplacement de son token binaire

        Dans ces l'opérateur est modifié :
        - le token suit '('
        - le token est en début d'expression
        - le token suit un opérateur

        :param tokensList: liste brute des tokens représentant l'expression
        :type tokensList: list[Token]
        :return: La liste des tokens avec les - et + corrigés le cas échéant
        :rtype: list[Token]
        """

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
                else:
                    # l'opérateur est - et c'est un cas d'opération unaire
                    # on l'interprète comme neg
                    tokenNeg = TokenUnaryOperator("-")
                    del tokensList[indice]
                    tokensList.insert(indice,tokenNeg)
                    # inutile de passer au suivant
            else:
                # passage au suivant
                indice += 1
        return tokensList

    def __init__(self):
        """Constructeur"""
        pass

    def buildExpression(self, originalExpression:str) -> ExpressionNode:
        """À partir d'une expression sous forme d'une chaîne de texte, produit l'arbre représentant cette expression et retourne la racine de cet arbre.

        :param originalExpression: expression à analyser
        :type originalExpression: str
        :return: racine de l'arbre
        :rtype: ExpressionNode
        :raises: ExpressionError si l'expression ne match pas l'expression régulière ou si les parenthèses ne sont pas convenablement équilibrées, ou si l'expression contient un enchaînement non valable, comme +).
        """

        expression = originalExpression.strip()
        if not self.strIsExpression(expression):
            raise ExpressionError(f"{originalExpression} : Expression incorrecte.")
        if not self.testBrackets(expression):
            raise ExpressionError(f"{originalExpression} : Les parenthèses ne sont pas équilibrées.")
        tokensList = ExpressionParser.__buildTokensList(expression)
        if not self.__tokensListIsLegal(tokensList):
            raise ExpressionError(f"{originalExpression} : Erreur. Vérifiez.")
        reversePolishTokensList = self.__buildReversePolishNotation(tokensList)
        rootNodeTree = ExpressionParser.__buildTree(reversePolishTokensList)

        return rootNodeTree

if __name__=="__main__":
    EP = ExpressionParser()
    for strExpression in [
      "-2 + x",
      "(x < 10 or y < 100)",
      "3*x+ 5 -y",
      "+ 6 -4*x / 3",
      "x<4 and y>3*x",
      "(2 < 4) * (3+x)",
      "(2+x) and (x-1)",
      "45^x",
      "x"
    ]:
        print("Test de :",strExpression)
        oExpression = EP.buildExpression(strExpression)
        print(oExpression) # Utilise la conversion to string de ExpressionNode
        print(oExpression.getType()) # affichage du type, 'bool' 'int' ou None
