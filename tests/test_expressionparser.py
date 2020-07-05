"""
.. module:: tests.test_expressionparser
:synopsis: Test de modules.parser.expression
"""


import unittest

from modules.parser.expression import ExpressionParser as EP
from modules.errors import ExpressionError

class MyTest(unittest.TestCase):
    def test1(self):
        strExpression = "-2 + x"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "(#-2 + @x)")

    def test2(self):
        strExpression = "(x < 10 or y < 100)"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "((@x < #10) or (@y < #100))")

    def test3(self):
        strExpression = "((3*x)+ (5 +-y))"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "((@x * #3) + ( - (@y) + #5))")

    def test4(self):
        strExpression = "+ 6 -4*x / 3"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "(#6 - ((@x * #4) / #3))")

    def test5(self):
        strExpression = "x<4 and y>3*x"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "((@x < #4) and (@y > (@x * #3)))")

    def test6(self):
        # mult on logic terms
        strExpression = "(2 < 4) * (3+x)"
        with self.assertRaises(ExpressionError) as context:
            EP.buildExpression(strExpression)
        self.assertTrue("Erreur. Vérifiez." in str(context.exception))

    def test7(self):
        # and on arithmetics terms
        strExpression = "(2+x) and (x-1)"
        with self.assertRaises(ExpressionError) as context:
            EP.buildExpression(strExpression)
        self.assertTrue("Erreur. Vérifiez." in str(context.exception))

    def test8(self):
        strExpression = "45^x"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "(@x ^ #45)")

    def test9(self):
        strExpression = "x"
        objExpression = EP.buildExpression(strExpression)
        self.assertEqual(str(objExpression), "@x")

