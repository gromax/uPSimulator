"""
.. module:: expressionparser
   :synopsis: gestion du parse des expressions arithmétiques et logiques

"""

from typing import List, Union
import re

from modules.primitives.operators import Operators
from modules.errors import ExpressionError

from modules.expressionnodes.arithmeticexpressionnodes import ArithmeticExpressionNode
from modules.expressionnodes.comparaisonexpressionnodes import ComparaisonExpressionNode
from modules.expressionnodes.logicexpressionnodes import LogicExpressionNode
from modules.parser.parsertokens import Token, TokenVariable, TokenNumber, TokenBinaryOperator, TokenUnaryOperator, TokenParenthesis

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
                return precedent.isOpening() == suivant.isOpening()
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
                openingFound = False
                while len(waitingStack)>0 and not openingFound:
                    unstackedToken = waitingStack.pop()
                    if isinstance(unstackedToken, TokenParenthesis):
                        # forcément une parenthèse ouvrante
                        openingFound = True
                    else:
                        polishStack.append(unstackedToken)
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
    def __buildTree(polishTokensList:List[Token]) -> Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]:
        """Construit l'arbre représentant l'expression

        :param polishTokensList: liste des tokens dans la version polonaise inversée
        :type polishTokensList: list(Token)
        :return: noeud racine de l'arbre représentant l'expression. None en cas d'erreur
        :rtype: Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode, None]
        """

        operandsList:List[Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode]] = []
        for token in polishTokensList:
            if isinstance(token,TokenVariable) or isinstance(token,TokenNumber):
                node = token.toNode()
                if node is None:
                    return None
                operandsList.append(node)
            elif isinstance(token,TokenUnaryOperator) or isinstance(token,TokenBinaryOperator):
                node = token.toNode(operandsList)
                if node is None:
                    return None
                operandsList.append(node)
        # à la fin, normalement, il n'y a qu'un opérande
        if len(operandsList) != 1:
            return None
        return operandsList.pop()

    @classmethod
    def __tokensListIsLegal(cls, tokensList:List[Token]) -> bool:
        """Teste si la liste de tokens un enchaînement de paire autorisées

        :param tokensList: liste brute des tokens
        :type tokensList: list[Token]
        :return: Vrai si l'enchaînement de token est autorisé
        :rtype: bool

        :Exemple:
          >>> ExpressionParser._ExpressionParser__tokensListIsLegal([])
          True
          >>> pOuvrante = TokenParenthesis('(')
          >>> pFermante = TokenParenthesis(')')
          >>> un = TokenNumber('1')
          >>> deux = TokenNumber('2')
          >>> fois = TokenBinaryOperator('*')
          >>> ExpressionParser._ExpressionParser__tokensListIsLegal([un, fois, deux])
          True
          >>> ExpressionParser._ExpressionParser__tokensListIsLegal([un, fois])
          False
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
        return TokenVariable.regex()

    @classmethod
    def expressionRegex(cls) -> str:
        """Donne accès à l'expression régulière d'une expression

        :return: expression régulière d'une expression
        :rtype: str
        """
        return r"(\s*{})+".format(cls.regex())

    @classmethod
    def regex(cls) -> str:
        """Concatène les expressions régulière pour les différents constituants d'une expression

        :return: expression régulière d'un item d'expression
        :rtype: str
        """
        regexList = [ "({})".format(Token.regex()) for Token in cls.TokensList ]
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
        regex = TokenVariable.regex()
        nomVariable = nomVariable.strip()
        if nomVariable in ("if", "else", "elif", "else", "while", "print", "input", "and", "or", "not"):
            return False
        return re.match(r"^(\s*{})+\s*$".format(regex), nomVariable) != None

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
        return re.match(r"^(\s*{})+\s*$".format(regex), expression) != None

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
                    break
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
        pmOperators = (Operators.ADD, Operators.MINUS)
        indice = 0
        while indice < len(tokensList):
            token = tokensList[indice]
            if indice <= 0:
                tokenPrecedent = None
            else:
                tokenPrecedent = tokensList[indice-1]

            if isinstance(token,TokenBinaryOperator) and token.operator in pmOperators and not ExpressionParser.isLegal(tokenPrecedent, token):
                # Ce + ou - doit être rectifié car il ne devrait pas se trouver à la suite de ce qui précède
                if token.operator == Operators.ADD:
                    # Dans le cas d'un +, il suffit de le supprimer
                    del tokensList[indice]
                    # inutile de passer au suivant
                else:
                    # l'opérateur est - et c'est un cas d'opération unaire
                    # on l'interprète comme neg
                    tokenNeg = TokenUnaryOperator.makeFromOperator(Operators.NEG)
                    del tokensList[indice]
                    tokensList.insert(indice,tokenNeg)
                    # inutile de passer au suivant
            else:
                # passage au suivant
                indice += 1
        return tokensList

    @classmethod
    def buildExpression(cls, originalExpression:str) -> Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode]:
        """À partir d'une expression sous forme d'une chaîne de texte, produit l'arbre représentant cette expression et retourne la racine de cet arbre.

        :param originalExpression: expression à analyser
        :type originalExpression: str
        :return: racine de l'arbre
        :rtype: Union[ArithmeticExpressionNode, ComparaisonExpressionNode, LogicExpressionNode]
        :raises: ExpressionError si l'expression ne match pas l'expression régulière ou si les parenthèses ne sont pas convenablement équilibrées, ou si l'expression contient un enchaînement non valable, comme +).
        """

        expression = originalExpression.strip()
        if not cls.strIsExpression(expression):
            raise ExpressionError("{} : Expression incorrecte.".format(originalExpression))
        if not cls.testBrackets(expression):
            raise ExpressionError(f"{originalExpression} : Les parenthèses ne sont pas équilibrées.")
        tokensList = cls.__buildTokensList(expression)
        if not cls.__tokensListIsLegal(tokensList):
            raise ExpressionError(f"{originalExpression} : Erreur. Vérifiez.")
        reversePolishTokensList = cls.__buildReversePolishNotation(tokensList)
        rootNodeTree = cls.__buildTree(reversePolishTokensList)
        if rootNodeTree is None:
            raise ExpressionError(f"{originalExpression} : Erreur. Vérifiez.")
        return rootNodeTree

if __name__=="__main__":
    for strExpression in [
      "-2 + x",
      "(x < 10 or y < 100)",
      "((3*x)+ (5 +-y))",
      "+ 6 -4*x / 3",
      "x<4 and y>3*x",
      "(2 < 4) * (3+x)",
      "(2+x) and (x-1)",
      "45^x",
      "x"
    ]:
        print("Test de :",strExpression)
        try:
            oExpression = ExpressionParser.buildExpression(strExpression)
        except Exception as e:
            print(e)
        else:
            print(oExpression)
