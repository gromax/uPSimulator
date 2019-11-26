from expressionParser import *

class Expression:
    def __init__(self, expr):
        self.expr = ExpressionParser.buildTokensList(expr)

    def parenthesesEquilibrees(self):
        nbParentheses = 0
        for element in self.expr :
            if isinstance(element, TokenParenthesis):
                if element.isOpening() : nbParentheses += 1
                else : nbParentheses -= 1
            if nbParentheses < 0 : return False
        if nbParentheses > 0 : return False
        else : return True

    def expressionValide(self):
        """Vérifie qu'une expression est correcte."""
        if self.parenthesesEquilibrees() :
            return True
        else : return False

txt1 = Expression("(3-2)+4)")
txt2 = Expression("-(-(-34-45)*5-(-3<9))")
print(txt1.expressionValide())
print(txt2.expressionValide())