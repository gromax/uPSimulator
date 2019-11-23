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

class TokenUnaryOperator(Token):
    regex = "~|not"

class TokenNumber(Token):
    regex = "(-\s*)?[0-9]+"

    def __init__(self,expression):
        self.value = int(expression.strip())

    def __str__(self):
        return str(self.value)

class TokenParenthesis(Token):
    regex = "\(|\)"

class ExpressionParser:
    TokensList = [ TokenVariable, TokenNumber, TokenBinaryOperator, TokenUnaryOperator, TokenParenthesis]

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
        for tok in self.tokens:
            print(tok)
