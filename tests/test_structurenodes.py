"""
.. module:: tests.test_structurenodes
:synopsis: Test de modules.structuresnodes
"""

from modules.structuresnodes import StructureNode, TransfertNode, WhileNode, StructureNodeList
from modules.parser.expression import ExpressionParser as EP
from modules.primitives.variable import Variable
from modules.primitives.operators import Operators

import unittest

class SingleItem(unittest.TestCase):
    def test1(self):
        varX = Variable('x')
        initialisationX = TransfertNode(
            1,
            varX,
            EP.buildExpression('0')
        )
        self.assertEqual(str(initialisationX), "	@x ← #0")

    def test2(self):
        varY = Variable('y')
        initialisationY = TransfertNode(
            2,
            varY,
            EP.buildExpression('0')
        )
        self.assertEqual(str(initialisationY), "	@y ← #0")

    def test3(self):
        varX = Variable('x')
        affectationX = TransfertNode(
            4,
            varX,
            EP.buildExpression('x+1')
        )
        self.assertEqual(str(affectationX), "	@x ← (@x + #1)")

    def test4(self):
        varY = Variable('y')
        affectationY = TransfertNode(
            5,
            varY,
            EP.buildExpression('y+x')
        )
        self.assertEqual(str(affectationY), "	@y ← (@y + @x)")

    def test5(self):
        varX = Variable('x')
        varY = Variable('y')
        affectationX = TransfertNode(
            4,
            varX,
            EP.buildExpression('x+1')
        )
        affectationY = TransfertNode(
            5,
            varY,
            EP.buildExpression('y+x')
        )
        whileItem = WhileNode(
            3,
            EP.buildExpression('x < 10 or y < 100'),
            [affectationX, affectationY]
        )
        good = "\n".join([
            "	while ((@x < #10) or (@y < #100)) {",
            "		@x ← (@x + #1)",
            "		@y ← (@y + @x)",
            "	}"
        ])
        self.assertEqual(str(whileItem), good)
    
    def test6(self):
        affichageFinal = TransfertNode(
            6,
            None,
            EP.buildExpression('y')
        )
        self.assertEqual(str(affichageFinal), "	@y → Affichage")

        
class LinearizationTest(unittest.TestCase):
    def test1(self):
        varX = Variable('x')
        varY = Variable('y')
        initialisationX = TransfertNode(
            1,
            varX,
            EP.buildExpression('0')
        )
        initialisationY = TransfertNode(
            2,
            varY,
            EP.buildExpression('0')
        )
        affectationX = TransfertNode(
            4,
            varX,
            EP.buildExpression('x+1')
        )
        affectationY = TransfertNode(
            5,
            varY,
            EP.buildExpression('y+x')
        )
        whileItem = WhileNode(
            3,
            EP.buildExpression('x < 10 or y < 100'),
            [affectationX, affectationY]
        )
        affichageFinal = TransfertNode(
            6,
            None,
            EP.buildExpression('y')
        )
        structureList = StructureNodeList([initialisationX, initialisationY, whileItem, affichageFinal])
        good = "\n".join([
            "	@x ← #0",
            "	@y ← #0",
            "	while ((@x < #10) or (@y < #100)) {",
            "		@x ← (@x + #1)",
            "		@y ← (@y + @x)",
            "	}",
            "	@y → Affichage"
        ])
        self.assertEqual(str(structureList), good)
    def test2(self):
        varX = Variable('x')
        varY = Variable('y')
        initialisationX = TransfertNode(
            1,
            varX,
            EP.buildExpression('0')
        )
        initialisationY = TransfertNode(
            2,
            varY,
            EP.buildExpression('0')
        )
        affectationX = TransfertNode(
            4,
            varX,
            EP.buildExpression('x+1')
        )
        affectationY = TransfertNode(
            5,
            varY,
            EP.buildExpression('y+x')
        )
        whileItem = WhileNode(
            3,
            EP.buildExpression('x < 10 or y < 100'),
            [affectationX, affectationY]
        )
        affichageFinal = TransfertNode(
            6,
            None,
            EP.buildExpression('y')
        )
        structureList = StructureNodeList([initialisationX, initialisationY, whileItem, affichageFinal])
        structureList.linearize([Operators.INF, Operators.EQ])
        good = "\n".join([
            "	@x ← #0",
            "	@y ← #0",
            "Lab1	Saut Lab2 si (@x < #10)",
            "	Saut Lab2 si (@y < #100)",
            "	Saut Lab3",
            "Lab2	@x ← (@x + #1)",
            "	@y ← (@y + @x)",
            "	Saut Lab1",
            "Lab3	@y → Affichage",
            "	halt"
        ])

        self.assertEqual(str(structureList), good)

