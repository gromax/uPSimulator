from expressionParser import *
from errors import *

class Expression:
    @staticmethod
    def getExpressionRegex():
        return ExpressionParser.regex()

    @staticmethod
    def strIsExpression(str):
        '''
        Entrée : chaine de caractères str
        Sortie: True si cela correspond à une expression
        '''
        return ExpressionParser.test(str)

    def __init__(self, expression):
        '''
        Entrée : chaine de caractères expression
        '''
        if not self.test(expression):
            raise ExpressionError(f"{expression} : Expression incorrecte.")
        self.expression = expression.strip()
        if not self.parenthesesEquilibrees():
            raise ExpressionError(f"{expression} : Les parenthèses ne sont pas équilibrées.")
        tokensList = ExpressionParser.buildTokensList(expr)
        if not ExpressionParser(tokensList):
            raise ExpressionError(f"{expression} : Erreur. Vérifiez.")
        reversePolishTokensList = ExpressionParser.buildReversePolishNotation(tokensList)
        self.tree = ExpressionParser.buildTree(reversePolishTokensList)
        self.type = ExpressionParser.nodeType(self.tree)
        if self.type == None:
            raise ExpressionError(f"{expression} : Erreur de type. Attention au type des opérateur.")

    def parenthesesEquilibrees(self):
        nbParentheses = 0
        for caractere in self.expression :
            if caractere == '('
                nbParentheses += 1
            elif caractere == ')': nbParentheses -= 1
            if nbParentheses < 0 : return False
        if nbParentheses > 0 : return False
        return True

txt1 = Expression("(3-2)+4)")
txt2 = Expression("-(-(-34-45)*5-(-3<9))")
print(txt1.expressionValide())
print(txt2.expressionValide())